import json
import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from services.face_service import (
    check_duplicate_face,
    decode_image_bytes,
    decode_base64_image,
    extract_embedding,
    save_face_image,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── List / Get ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).order_by(models.Employee.name).all()


@router.get("/stats")
def employee_stats(db: Session = Depends(get_db)):
    return {"total_employees": db.query(models.Employee).count()}


@router.get("/{employee_db_id}", response_model=schemas.EmployeeResponse)
def get_employee(employee_db_id: int, db: Session = Depends(get_db)):
    emp = (db.query(models.Employee)
           .filter(models.Employee.id == employee_db_id)
           .first())
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


# ── Register ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=schemas.EmployeeResponse)
async def register_employee(
    name:         str            = Form(...),
    employee_id:  str            = Form(...),
    email:        Optional[str]  = Form(None),
    department:   Optional[str]  = Form(None),
    designation:  Optional[str]  = Form(None),
    laptop_serial: Optional[str] = Form(None),
    image:        UploadFile     = File(...),
    # JSON array of base64 strings — extra webcam samples for multi-shot accuracy
    extra_images: Optional[str]  = Form(None),
    db: Session = Depends(get_db),
):
    # ── 1. Duplicate Employee ID check ──────────────────────────────────────
    if (db.query(models.Employee)
            .filter(models.Employee.employee_id == employee_id)
            .first()):
        raise HTTPException(
            status_code=400,
            detail=f"Employee ID '{employee_id}' is already registered.",
        )

    # ── 2. Decode image ─────────────────────────────────────────────────────
    img_bytes = await image.read()
    try:
        img = decode_image_bytes(img_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # ── 3. Extract primary embedding ────────────────────────────────────────
    try:
        primary_embedding = extract_embedding(img)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Face detection failed: {exc}. "
                "Tips: use good lighting, face camera directly, "
                "avoid sunglasses or face coverings."
            ),
        )

    # ── 4. Duplicate face check ─────────────────────────────────────────────
    existing = (
        db.query(models.Employee)
        .filter(models.Employee.face_embedding.isnot(None))
        .all()
    )
    is_dup, dup_emp, _dist = check_duplicate_face(primary_embedding, existing)
    if is_dup:
        raise HTTPException(
            status_code=400,
            detail=(
                f"This face is already registered under employee "
                f"'{dup_emp.name}' (ID: {dup_emp.employee_id}). "
                "Each person can only be registered once. "
                "If this is a genuinely different person, please use a "
                "clearer, well-lit, front-facing photo."
            ),
        )

    # ── 5. Collect all embeddings (multi-sample for better accuracy) ────────
    all_embeddings = [primary_embedding]

    if extra_images:
        try:
            extra_list = json.loads(extra_images)
            for b64_str in extra_list[:4]:  # cap at 4 extra samples
                try:
                    extra_img = decode_base64_image(b64_str)
                    emb = extract_embedding(extra_img)
                    all_embeddings.append(emb)
                except Exception as exc:
                    logger.warning("Extra sample skipped: %s", exc)
        except Exception as exc:
            logger.warning("Could not parse extra_images JSON: %s", exc)

    # ── 6. Persist ──────────────────────────────────────────────────────────
    face_path      = save_face_image(img, employee_id)
    embedding_json = (
        json.dumps(all_embeddings)
        if len(all_embeddings) > 1
        else json.dumps(all_embeddings[0])
    )

    emp = models.Employee(
        name=name,
        employee_id=employee_id,
        email=email or None,
        department=department or None,
        designation=designation or None,
        face_embedding=embedding_json,
        face_image_path=face_path,
        laptop_serial=laptop_serial.strip().upper() if laptop_serial else None,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


# ── Delete ──────────────────────────────────────────────────────────────────

@router.delete("/{employee_db_id}")
def delete_employee(employee_db_id: int, db: Session = Depends(get_db)):
    emp = (db.query(models.Employee)
           .filter(models.Employee.id == employee_db_id)
           .first())
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Remove face image from disk (handle both absolute path and relative filename)
    if emp.face_image_path:
        # Try as-is first (absolute path from old versions)
        candidate = emp.face_image_path
        if not os.path.isabs(candidate):
            # Relative filename — resolve against face_db directory
            from services.face_service import FACE_DB_DIR
            candidate = os.path.join(FACE_DB_DIR, candidate)
        if os.path.exists(candidate):
            try:
                os.remove(candidate)
            except Exception as exc:
                logger.warning("Could not delete face image: %s", exc)

    db.delete(emp)
    db.commit()
    return {"message": f"Employee '{emp.name}' deleted successfully"}


# ── Device Verification ─────────────────────────────────────────────────────

@router.get("/verify-device/{serial_number}")
def verify_device(serial_number: str, db: Session = Depends(get_db)):
    """
    Check whether a laptop serial number belongs to a registered company employee.
    Returns employee info if found, or a 'not found' message if the device is unknown.
    """
    normalized = serial_number.strip().upper()
    emp = (
        db.query(models.Employee)
        .filter(models.Employee.laptop_serial == normalized)
        .first()
    )
    if emp:
        return {
            "verified": True,
            "message": f"Device belongs to {emp.name} ({emp.employee_id})",
            "employee_name": emp.name,
            "employee_id": emp.employee_id,
            "department": emp.department,
            "designation": emp.designation,
            "laptop_serial": emp.laptop_serial,
        }
    return {
        "verified": False,
        "message": f"Serial '{normalized}' not found in company records. Device may be personal or unregistered.",
        "laptop_serial": normalized,
    }
