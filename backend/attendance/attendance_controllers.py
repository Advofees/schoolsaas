import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.attendance.attendance_models import AttendanceStatus
from backend.database.database import DatabaseDependency


from backend.user.user_models import (
    User,
)

from backend.student.student_model import Student

from backend.attendance.attendance_models import Attendance

from backend.user.user_authentication import UserAuthenticationContextDependency
import datetime
import typing

router = APIRouter()


@router.get(
    "/attendance/school/{school_id}/{classroom_id}/{start_date}/{end_date}/list"
)
def get_all_attendance_for_a_specific_classroom_in_a_date_range(
    db: DatabaseDependency,
    classroom_id: uuid.UUID,
    school_id: uuid.UUID,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
):
    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.classroom_id == classroom_id,
            Attendance.school_id == school_id,
            Attendance.date.between(start_date, end_date),
        )
        .all()
    )
    return attendance


@router.get("/attendance/school/{school_id}/{academic_term_id}/list")
def get_attendance_statistics_for_a_school_in_an_academic_term(
    db: DatabaseDependency,
    academic_term_id: uuid.UUID,
    school_id: uuid.UUID,
):
    school_term_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.school_id == school_id,
            Attendance.academic_term_id == academic_term_id,
        )
        .all()
    )
    return school_term_attendance


class SchoolAttendanceDTO(BaseModel):
    student_id: uuid.UUID
    classroom_id: uuid.UUID
    school_id: uuid.UUID
    academic_term_id: uuid.UUID
    remarks: str
    status: AttendanceStatus
    date: datetime.datetime


@router.post("/attendance/school/create")
def create_student_class_attendance(
    db: DatabaseDependency,
    authentication_context: UserAuthenticationContextDependency,
    body: SchoolAttendanceDTO,
):
    user = db.query(User).filter(User.id == authentication_context.user_id).first()

    if not user:
        raise HTTPException(404, detail="not-found")
    if not user.teacher_user:
        raise HTTPException(403, detail="needs-to-teacher")

    student = (
        db.query(Student)
        .filter(
            Student.id == body.student_id, Student.classroom_id == body.classroom_id
        )
        .first()
    )
    if not student:
        raise HTTPException(404, detail="student-not-found")

    attendance = (
        db.query(Attendance)
        .filter(Attendance.student_id == student.id, Attendance.date == body.date)
        .first()
    )
    if attendance:
        raise HTTPException(403, detail="student-attendance-already-recorded")

    attendance = Attendance(
        student_id=body.student_id,
        status=body.status.value,
        date=body.date,
        school_id=body.school_id,
        classroom_id=body.classroom_id,
        academic_term_id=body.academic_term_id,
        remarks=body.remarks,
    )
    db.add(attendance)
    db.flush()
    db.commit()
    return {"message": "attendance-for-the-day-added-successfully"}


class AttendanceUpdateDTO(BaseModel):
    status: typing.Optional[AttendanceStatus]
    remarks: typing.Optional[str]
    date: typing.Optional[datetime.datetime]


@router.patch("/attendance/school/{attendance_id}")
def partial_update_student_attendance(
    attendance_id: uuid.UUID,
    body: AttendanceUpdateDTO,
    db: DatabaseDependency,
    authentication_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == authentication_context.user_id).first()
    if not user:
        raise HTTPException(404, detail="user-not-found")
    if not user.teacher_user:
        raise HTTPException(403, detail="needs-to-be-teacher")

    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(404, detail="attendance-record-not-found")

    if body.date and body.date != attendance.date:
        existing_attendance = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == attendance.student_id,
                Attendance.date == body.date,
                Attendance.id != attendance_id,
            )
            .first()
        )
        if existing_attendance:
            raise HTTPException(
                403, detail="student-attendance-already-exists-for-this-date"
            )

    if body.status:
        attendance.status = body.status.value
    if body.remarks:
        attendance.remarks = body.remarks
    if body.date:
        attendance.date = body.date

    db.commit()
    db.refresh(attendance)

    return {}


@router.delete("/attendance/school/{attendance_id}")
def delete_student_attendance(
    attendance_id: uuid.UUID,
    db: DatabaseDependency,
    authentication_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == authentication_context.user_id).first()
    if not user:
        raise HTTPException(404, detail="user-not-found")
    if not user.teacher_user:
        raise HTTPException(403, detail="needs-to-be-teacher")

    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(404, detail="attendance-record-not-found")

    db.delete(attendance)
    db.commit()

    return {"message": "attendance-record-deleted-successfully"}
