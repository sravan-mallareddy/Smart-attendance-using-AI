import logging
from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from services.face_service import (
    check_liveness,
    decode_base64_image,
    extract_embedding,
    find_best_match,
    reset_liveness_session,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recognize", response_model=schemas.RecognitionResult)
async def recognize_and_mark(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Accepts a base64-encoded webcam frame, runs anti-spoofing liveness
    checks, extracts the Facenet embedding, matches against registered
    employees, and marks attendance if confidence >= 60 %.
    """
    image_data = payload.get("image")
    if not image_data:
        raise HTTPException(status_code=400, detail="No image data provided")

    # session_key lets us track frame variation per browser tab / device
    session_key = payload.get("session_key", "default")

    # ── Decode ──────────────────────────────────────────────────────────────
    try:
        img = decode_base64_image(image_data)
    except Exception as exc:
        raise HTTPException(status_code=422,
                            detail=f"Image decode error: {exc}")

    # ── Liveness / anti-spoofing ─────────────────────────────────────────────
    is_live, liveness_msg = check_liveness(img, session_key)
    if not is_live:
        logger.info("Liveness check failed [%s]: %s", session_key, liveness_msg)
        return schemas.RecognitionResult(
            recognized=False,
            attendance_marked=False,
            message=liveness_msg,
        )

    # ── Face embedding ───────────────────────────────────────────────────────
    try:
        query_embedding = extract_embedding(img)
    except ValueError as exc:
        return schemas.RecognitionResult(
            recognized=False,
            attendance_marked=False,
            message=f"No face detected: {exc}",
        )

    # ── Load registered employees ────────────────────────────────────────────
    employees = (
        db.query(models.Employee)
        .filter(models.Employee.face_embedding.isnot(None))
        .all()
    )
    if not employees:
        return schemas.RecognitionResult(
            recognized=False,
            attendance_marked=False,
            message="No registered employees found. Please register employees first.",
        )

    # ── Match ────────────────────────────────────────────────────────────────
    matched_emp, confidence = find_best_match(query_embedding, employees)

    if matched_emp is None:
        if confidence > 0:
            # Near-miss — confidence present but below threshold
            return schemas.RecognitionResult(
                recognized=False,
                attendance_marked=False,
                message=(
                    f"Face detected but confidence too low ({confidence:.1f}%). "
                    "Please position your face clearly in the centre "
                    "and scan again."
                ),
            )
        return schemas.RecognitionResult(
            recognized=False,
            attendance_marked=False,
            message=(
                "Face not recognized. "
                "If you are registered, try better lighting or remove glasses."
            ),
        )

    # ── Already marked today? ────────────────────────────────────────────────
    today    = date.today()
    existing = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.employee_db_id == matched_emp.id,
            models.Attendance.date == today,
        )
        .first()
    )
    if existing:
        return schemas.RecognitionResult(
            recognized=True,
            employee_name=matched_emp.name,
            employee_id=matched_emp.employee_id,
            employee_db_id=matched_emp.id,
            confidence=confidence,
            attendance_marked=False,
            already_marked=True,
            message=f"Attendance already marked for {matched_emp.name} today",
        )

    # ── Mark attendance ──────────────────────────────────────────────────────
    now    = datetime.now()
    record = models.Attendance(
        employee_db_id=matched_emp.id,
        employee_name=matched_emp.name,
        employee_id=matched_emp.employee_id,
        date=today,
        time=now.strftime("%H:%M:%S"),
        status="present",
        confidence=confidence,
    )
    db.add(record)
    db.commit()

    reset_liveness_session(session_key)
    logger.info(
        "Attendance marked: %s (%s) conf=%.1f%%",
        matched_emp.name, matched_emp.employee_id, confidence,
    )

    return schemas.RecognitionResult(
        recognized=True,
        employee_name=matched_emp.name,
        employee_id=matched_emp.employee_id,
        employee_db_id=matched_emp.id,
        confidence=confidence,
        attendance_marked=True,
        already_marked=False,
        message=(
            f"✓ Attendance marked for {matched_emp.name} "
            f"at {now.strftime('%H:%M:%S')}"
        ),
    )
