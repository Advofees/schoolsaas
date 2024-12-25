import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from backend.paginated_response import PaginatedResponse
from backend.attendance.attendance_models import AttendanceStatus
from backend.database.database import DatabaseDependency


from backend.school.school_model import School
from backend.user.user_models import (
    RoleType,
    User,
)

from backend.student.student_model import Student

from backend.attendance.attendance_models import Attendance

from backend.user.user_authentication import UserAuthenticationContextDependency
import datetime
import typing

router = APIRouter()


class AttendanceResponse(BaseModel):
    id: uuid.UUID
    date: datetime.datetime
    status: str
    remarks: typing.Optional[str]
    student_id: uuid.UUID
    school_id: uuid.UUID
    classroom_id: uuid.UUID
    academic_term_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: typing.Optional[datetime.datetime]


def attendance_to_dto(attendance: Attendance) -> AttendanceResponse:
    return AttendanceResponse(
        id=attendance.id,
        date=attendance.date,
        status=attendance.status,
        remarks=attendance.remarks,
        student_id=attendance.student_id,
        school_id=attendance.school_id,
        classroom_id=attendance.classroom_id,
        academic_term_id=attendance.academic_term_id,
        created_at=attendance.created_at,
        updated_at=attendance.updated_at,
    )


@router.get("/attendance/list")
def get_all_attendance_for_a_specific_classroom_in_a_date_range(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    attendance_status: typing.Optional[AttendanceStatus] = None,
    classroom_id: typing.Optional[uuid.UUID] = None,
    academic_term_id: typing.Optional[uuid.UUID] = None,
    start_date: typing.Optional[datetime.datetime] = None,
    end_date: typing.Optional[datetime.datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized"
        )

    query = db.query(Attendance).filter(Attendance.school_id == user.school_id)

    if attendance_status:
        query = query.filter(Attendance.status == attendance_status.value)

    if classroom_id is not None:
        query = query.filter(
            Attendance.classroom_id == classroom_id,
        )

    if start_date is not None and end_date is not None:
        query = query.filter(Attendance.date.between(start_date, end_date))

    if academic_term_id is not None:
        query = query.filter(
            Attendance.academic_term_id == academic_term_id,
        )

    total_count = query.count()

    offset = (page - 1) * limit
    attendance_records = query.offset(offset).limit(limit).all()

    return PaginatedResponse[AttendanceResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[
            attendance_to_dto(attendance=attendance)
            for attendance in attendance_records
        ],
    )


class SchoolAttendanceDTO(BaseModel):
    student_id: uuid.UUID
    classroom_id: uuid.UUID
    academic_term_id: uuid.UUID
    remarks: str
    status: AttendanceStatus
    date: datetime.datetime


@router.post("/attendance/create")
def create_student_class_attendance(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    body: SchoolAttendanceDTO,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized"
        )

    if not (
        user.teacher_user
        or user.has_role_type(RoleType.TEACHER)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized"
        )

    student = (
        db.query(Student)
        .filter(
            Student.id == body.student_id, Student.classroom_id == body.classroom_id
        )
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="student-not-found"
        )

    attendance = (
        db.query(Attendance)
        .filter(Attendance.student_id == student.id, Attendance.date == body.date)
        .first()
    )
    if attendance:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="student-attendance-already-recorded",
        )

    school = db.query(School).filter(School.id == user.school_id).first()

    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    attendance = Attendance(
        student_id=body.student_id,
        status=body.status,
        date=body.date,
        school_id=school.id,
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


@router.patch("/attendance/by-attendance-id/{attendance_id}")
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

    db.flush()
    db.commit()

    return {}


@router.delete("/attendance/{attendance_id}")
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
