from typing import List, Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter()


# ── Today stats (used by dashboard + attendance page) ──────────────────────

@router.get("/today", response_model=schemas.TodayStats)
def get_today_attendance(db: Session = Depends(get_db)):
    today = date.today()
    records = (
        db.query(models.Attendance)
        .filter(models.Attendance.date == today)
        .order_by(models.Attendance.marked_at.desc())
        .all()
    )
    total   = db.query(models.Employee).count()
    present = len(records)
    return schemas.TodayStats(
        date=str(today),
        total_employees=total,
        present=present,
        absent=max(0, total - present),
        # model_validate is the Pydantic v2 replacement for from_orm
        records=[schemas.AttendanceResponse.model_validate(r) for r in records],
    )


# ── Dashboard stats ─────────────────────────────────────────────────────────

@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    today    = date.today()
    week_ago = today - timedelta(days=7)
    today_present = (
        db.query(models.Attendance)
        .filter(models.Attendance.date == today)
        .count()
    )
    week_total = (
        db.query(models.Attendance)
        .filter(models.Attendance.date >= week_ago)
        .count()
    )
    total_employees = db.query(models.Employee).count()
    return schemas.DashboardStats(
        today_present=today_present,
        week_total=week_total,
        total_employees=total_employees,
        today_absent=max(0, total_employees - today_present),
    )


# ── List records (reports page) ─────────────────────────────────────────────

@router.get("/", response_model=List[schemas.AttendanceResponse])
def list_attendance(
    date_filter: Optional[str] = Query(None, alias="date"),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Attendance)
    if date_filter:
        try:
            parsed = date.fromisoformat(date_filter)
            query  = query.filter(models.Attendance.date == parsed)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD.",
            )
    if employee_id:
        query = query.filter(models.Attendance.employee_id == employee_id)
    return (
        query.order_by(models.Attendance.marked_at.desc())
        .limit(500)
        .all()
    )


# ── Delete single record ────────────────────────────────────────────────────

@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == attendance_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(record)
    db.commit()
    return {"message": "Attendance record deleted successfully"}
