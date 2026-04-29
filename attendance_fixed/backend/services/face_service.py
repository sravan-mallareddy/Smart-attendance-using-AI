import cv2
import numpy as np
import json
import os
import base64
import logging
from typing import List, Optional, Tuple
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)

FACE_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "face_db")
os.makedirs(FACE_DB_DIR, exist_ok=True)

MODEL_NAME        = "Facenet"
DETECTOR_BACKEND  = "opencv"
FALLBACK_DETECTOR = "mtcnn"
SKIP_DETECTOR     = "skip"

# ── Thresholds ─────────────────────────────────────────────────────────────
# Mobile phone photos have slightly different embedding distributions than
# webcam captures due to different compression, focal length, and lighting.
# Cosine distance of 0.40 → ~60% confidence (on the edge).
# Raised to 0.45 to be more forgiving for mobile/varied lighting while
# still rejecting clearly different faces (which score > 0.55 typically).
COSINE_THRESHOLD         = 0.45   # raised from 0.40 — better mobile photo matching
MIN_CONFIDENCE_PCT       = 55.0   # lowered from 60 — accept good-enough matches
DUPLICATE_FACE_THRESHOLD = 0.40   # keep strict for registration deduplication

# ── Liveness state ──────────────────────────────────────────────────────────
_liveness_history: dict = {}   # session_key -> list[float]
_LIVENESS_FRAMES_REQUIRED = 3  # need at least N frames before motion check

_deepface_loaded = False


def _ensure_deepface() -> None:
    global _deepface_loaded
    if not _deepface_loaded:
        from deepface import DeepFace  # noqa: F401
        _deepface_loaded = True


# ── Image decode helpers ────────────────────────────────────────────────────

def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image — check file format (JPG/PNG/WEBP)")
    return img


def decode_base64_image(b64_string: str) -> np.ndarray:
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    img_bytes = base64.b64decode(b64_string)
    return decode_image_bytes(img_bytes)


# ── Preprocessing ───────────────────────────────────────────────────────────

def preprocess_image(img: np.ndarray) -> np.ndarray:
    """Upscale tiny frames, downscale huge images, apply CLAHE contrast."""
    h, w = img.shape[:2]

    if max(h, w) < 400:
        scale = 400 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_CUBIC)
        h, w = img.shape[:2]

    if max(h, w) > 1280:
        scale = 1280 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    # CLAHE contrast enhancement for dark/dim frames
    try:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_ch = clahe.apply(l_ch)
        img = cv2.cvtColor(cv2.merge((l_ch, a_ch, b_ch)), cv2.COLOR_LAB2BGR)
    except Exception:
        pass

    return img


# ── Liveness / Anti-Spoofing ────────────────────────────────────────────────

def _compute_frame_hash(img: np.ndarray) -> float:
    """Perceptual brightness hash for detecting static images."""
    small = cv2.resize(img, (16, 16))
    gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return float(gray.mean())


def check_liveness(img: np.ndarray, session_key: str) -> Tuple[bool, str]:
    """
    Two-method anti-spoofing check calibrated for real webcam and mobile camera use.

    Method 1 — Laplacian texture analysis:
      Phone screens displaying a face photo produce very low Laplacian variance.
      Real webcam/mobile camera faces have organic skin texture.
      Threshold tuned conservatively so mobile cameras (slightly compressed) pass.

    Method 2 — Frame-variation tracking:
      A static photo produces near-zero brightness variation across frames.
      A live person breathing / micro-moving produces measurable variation.
      Only enforced after enough frames have accumulated (avoids false reject on first scan).

    Returns:
        (True, "ok") if live face detected
        (False, reason_message) if spoofing detected
    """
    # Method 1: texture — reject only extremely smooth images (screen/printed photo)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Lowered minimum threshold: mobile cameras compress JPEG aggressively,
    # reducing sharpness. Real faces still score >>30 even on compressed frames.
    TEXTURE_MIN = 30.0    # was 100 — too strict for mobile camera streams
    TEXTURE_MAX = 6000.0  # raised: some mobile cameras produce high-sharpness frames

    if lap_var < TEXTURE_MIN:
        return False, (
            f"Liveness failed: image too smooth (score {lap_var:.0f}). "
            "Do not hold a phone photo or printed photo to the camera — "
            "please use a live camera feed."
        )
    if lap_var > TEXTURE_MAX:
        return False, (
            f"Liveness failed: image appears to be a printed photo "
            f"(score {lap_var:.0f})."
        )

    # Method 2: frame variation — only applied after enough frames collected
    fval    = _compute_frame_hash(img)
    history = _liveness_history.setdefault(session_key, [])
    history.append(fval)
    if len(history) > 10:
        history.pop(0)

    if len(history) >= _LIVENESS_FRAMES_REQUIRED:
        variation = float(np.std(history))
        # Lowered threshold: mobile cameras auto-adjust exposure causing natural
        # brightness drift; 0.3 catches truly static images while accepting live feeds
        if variation < 0.3:  # was 0.8 — too strict, rejects stabilised mobile cameras
            return False, (
                "Liveness failed: no natural movement detected. "
                "Please use a live camera — holding a photo to the camera is not accepted."
            )

    return True, "ok"


def reset_liveness_session(session_key: str) -> None:
    """Clear liveness history after a successful attendance mark."""
    _liveness_history.pop(session_key, None)


# ── DeepFace helpers ────────────────────────────────────────────────────────

def _represent(img: np.ndarray, detector: str,
               enforce: bool = True) -> list:
    """Call DeepFace.represent with numpy-array or file-path fallback."""
    from deepface import DeepFace
    import inspect

    kwargs = dict(
        model_name=MODEL_NAME,
        detector_backend=detector,
        enforce_detection=enforce,
        align=True,
    )

    try:
        sig = inspect.signature(DeepFace.represent)
        img_param = "img" if "img" in sig.parameters else "img_path"
    except Exception:
        img_param = "img_path"

    # Try 1: numpy array
    try:
        results = DeepFace.represent(**{img_param: img}, **kwargs)
        if results:
            return results
    except Exception as e1:
        logger.debug("numpy path failed (%s): %s", detector, e1)

    # Try 2: temp file (most compatible fallback)
    tmp = os.path.join(os.path.dirname(__file__), "..", "_tmp_face.jpg")
    try:
        cv2.imwrite(tmp, img)
        results = DeepFace.represent(**{img_param: tmp}, **kwargs)
        if results:
            return results
    except Exception as e2:
        logger.debug("file path failed (%s): %s", detector, e2)
        raise
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    raise ValueError("DeepFace returned empty results")


def extract_embedding(img: np.ndarray) -> list:
    """
    Extract a Facenet embedding using multiple detector strategies:
    1. opencv  enforce=True
    2. mtcnn   enforce=True
    3. opencv  enforce=False
    4. mtcnn   enforce=False
    5. skip    enforce=False  (whole-frame fallback)
    """
    _ensure_deepface()
    img = preprocess_image(img)
    last_error = None

    for detector in [DETECTOR_BACKEND, FALLBACK_DETECTOR]:
        try:
            results   = _represent(img, detector, enforce=True)
            embedding = results[0]["embedding"]
            logger.info("Embedding via %s (enforce) %d-d", detector, len(embedding))
            return embedding
        except Exception as exc:
            last_error = exc
            logger.warning("Detector '%s' enforce=True failed: %s", detector, exc)

    for detector in [DETECTOR_BACKEND, FALLBACK_DETECTOR, SKIP_DETECTOR]:
        try:
            results = _represent(img, detector, enforce=False)
            if results:
                embedding = results[0]["embedding"]
                logger.info("Embedding via %s (no-enforce) %d-d",
                            detector, len(embedding))
                return embedding
        except Exception as exc:
            last_error = exc
            logger.warning("Detector '%s' enforce=False failed: %s", detector, exc)

    raise ValueError(
        "No face detected. Ensure good lighting, face clearly visible, "
        f"look directly at the camera. (Last error: {last_error})"
    )


# ── Face image storage ──────────────────────────────────────────────────────

def save_face_image(img: np.ndarray, employee_id: str) -> str:
    """Save face image to face_db directory. Returns the relative filename for portable storage."""
    safe_id  = employee_id.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"{safe_id}.jpg"
    abs_path = os.path.abspath(os.path.join(FACE_DB_DIR, filename))
    cv2.imwrite(abs_path, img)
    # Return relative filename so it's portable across machines / path moves.
    # The backend serves it at /face_images/<filename> via StaticFiles mount.
    return filename


def _get_stored_array(emp) -> Optional[np.ndarray]:
    """Parse stored JSON embedding into an averaged ndarray, or None on error."""
    if not emp.face_embedding:
        return None
    try:
        data = json.loads(emp.face_embedding)
        if data and isinstance(data[0], list):
            # Multi-sample: average all samples for robust matching
            return np.mean(
                [np.array(e, dtype=np.float32) for e in data], axis=0
            )
        return np.array(data, dtype=np.float32)
    except Exception as exc:
        logger.warning("Could not parse embedding for %s: %s",
                       getattr(emp, "employee_id", "?"), exc)
        return None


# ── Duplicate face check (registration guard) ───────────────────────────────

def check_duplicate_face(
    new_embedding: list,
    existing_employees: list,
) -> Tuple[bool, object, float]:
    """
    Compare a new embedding against every registered employee.

    Returns:
        (True,  matched_employee, distance) if a duplicate is found
        (False, None,             distance) if no duplicate
    """
    q_arr         = np.array(new_embedding, dtype=np.float32)
    best_distance = 1.0
    best_emp      = None

    for emp in existing_employees:
        stored = _get_stored_array(emp)
        if stored is None:
            continue
        try:
            dist = float(cosine(q_arr, stored))
            logger.debug("Dup-check %s: %.4f", emp.employee_id, dist)
            if dist < best_distance:
                best_distance = dist
                best_emp      = emp
        except Exception as exc:
            logger.warning("Dup-check skip %s: %s", emp.employee_id, exc)

    if best_distance < DUPLICATE_FACE_THRESHOLD and best_emp is not None:
        logger.info(
            "Duplicate face detected — new face matches %s (dist=%.4f)",
            best_emp.employee_id, best_distance,
        )
        return True, best_emp, best_distance

    return False, None, best_distance


# ── Recognition matching ────────────────────────────────────────────────────

def find_best_match(
    query_embedding: list,
    employees: list,
) -> Tuple[object, float]:
    """
    Find the best-matching employee for attendance recognition.

    Returns:
        (employee, confidence_pct)    — accepted match  (conf >= MIN_CONFIDENCE_PCT)
        (None,     confidence_pct)    — near-miss        (0 < conf < MIN, scan again)
        (None,     0.0)               — no match at all
    """
    best_employee = None
    best_distance = 1.0
    q_arr = np.array(query_embedding, dtype=np.float32)

    for emp in employees:
        stored = _get_stored_array(emp)
        if stored is None:
            continue
        try:
            dist = float(cosine(q_arr, stored))
            logger.debug("Recog dist %s: %.4f", emp.employee_id, dist)
            if dist < best_distance:
                best_distance = dist
                best_employee = emp
        except Exception as exc:
            logger.warning("Recog skip %s: %s", emp.employee_id, exc)

    if best_distance < COSINE_THRESHOLD and best_employee is not None:
        confidence = round((1.0 - best_distance) * 100, 2)

        if confidence < MIN_CONFIDENCE_PCT:
            logger.info(
                "Low-confidence: %s conf=%.1f%% < %.0f%% — scan-again",
                best_employee.employee_id, confidence, MIN_CONFIDENCE_PCT,
            )
            return None, confidence  # signal "try again"

        logger.info(
            "Matched %s dist=%.4f conf=%.1f%%",
            best_employee.employee_id, best_distance, confidence,
        )
        return best_employee, confidence

    logger.info("No match. Best dist=%.4f (threshold=%.2f)",
                best_distance, COSINE_THRESHOLD)
    return None, 0.0
