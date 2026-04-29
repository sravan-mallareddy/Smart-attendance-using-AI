from sqlalchemy import (
    Column, Integer, String, Float, Date,
    DateTime, Text, UniqueConstraint
)
from sqlalchemy.sql import func
from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    # Serialized face embedding (JSON list of floats)
    face_embedding = Column(Text, nullable=True)
    face_image_path = Column(String(255), nullable=True)
    laptop_serial = Column(String(100), nullable=True)   # company-issued device serial
    created_at = Column(DateTime, server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("employee_db_id", "date", name="uq_attendance_per_day"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_db_id = Column(Integer, nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    employee_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    time = Column(String(20), nullable=True)
    status = Column(String(20), default="present")
    confidence = Column(Float, nullable=True)
    marked_at = Column(DateTime, server_default=func.now())
