from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class EmployeeCreate(BaseModel):
    name: str
    employee_id: str
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    laptop_serial: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    employee_id: str
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    face_image_path: Optional[str] = None
    laptop_serial: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    id: int
    employee_name: str
    employee_id: str
    date: date
    time: Optional[str] = None
    status: str
    confidence: Optional[float] = None
    marked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecognitionResult(BaseModel):
    recognized: bool
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    employee_db_id: Optional[int] = None
    confidence: Optional[float] = None
    attendance_marked: bool
    already_marked: bool = False
    message: str


class TodayStats(BaseModel):
    date: str
    total_employees: int
    present: int
    absent: int
    records: List[AttendanceResponse]


class DashboardStats(BaseModel):
    today_present: int
    week_total: int
    total_employees: int
    today_absent: int
