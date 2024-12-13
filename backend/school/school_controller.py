from dataclasses import dataclass
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import func
from backend.classroom.classroom_model import Classroom
from backend.database.database import DatabaseDependency
from backend.payment.payment_model import Payment
from backend.raise_exception import raise_exception
from backend.school.school_model import School, SchoolStudentAssociation
from backend.student.student_model import Student, Gender
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.attendance.attendance_models import Attendance, AttendanceStatus
from backend.user.user_models import User, RoleType
from backend.user.user_authentication import UserAuthenticationContextDependency
import datetime
import typing
from pydantic import BaseModel, StringConstraints, EmailStr

router = APIRouter()


class PaymentMethodStats(BaseModel):
    amount: float
    count: int


class AttendanceMetrics(BaseModel):
    total_absent: typing.Optional[int]
    total_present: typing.Optional[int]
    start_date: datetime.datetime
    total_present_male: int
    total_absent_male: int
    total_present_female: int
    total_absent_female: int
    end_date: typing.Optional[datetime.datetime]
    filter_type: str  # 'day', 'week', 'month', 'year'


@dataclass
class DateRangeResult:
    start_date: datetime.datetime
    end_date: datetime.datetime


def calculate_date_range(
    filter_type: str,
    filter_date: typing.Optional[datetime.datetime] = None,
) -> DateRangeResult:
    """
    Calculate start and end dates based on filter type and date.
    Returns (start_date, end_date) tuple.
    """
    if not filter_date:
        filter_date = datetime.datetime.now()

    # Normalize the time component
    start_date = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if filter_type == "day":
        end_date = start_date + datetime.timedelta(days=1)

    elif filter_type == "week":
        # Adjust to start of week (Monday)
        start_date = start_date - datetime.timedelta(days=start_date.weekday())
        end_date = start_date + datetime.timedelta(days=7)

    elif filter_type == "month":
        # Start from first day of the month
        start_date = start_date.replace(day=1)
        # Move to first day of next month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

    elif filter_type == "year":
        # Start from first day of the year
        start_date = start_date.replace(month=1, day=1)
        # End on first day of next year
        end_date = start_date.replace(year=start_date.year + 1)

    else:
        raise ValueError(f"Invalid filter_type: {filter_type}")

    return DateRangeResult(start_date=start_date, end_date=end_date)


@dataclass
class MetricsCounter:
    total_present: int = 0
    total_absent: int = 0
    total_present_male: int = 0
    total_present_female: int = 0
    total_absent_male: int = 0
    total_absent_female: int = 0


def get_classroom_attendance_metrics(
    db: DatabaseDependency,
    school_id: uuid.UUID,
    classroom_id: uuid.UUID,
    filter_type: str = "day",
    filter_date: typing.Optional[datetime.datetime] = None,
) -> AttendanceMetrics:
    """Get attendance metrics for a specific classroom."""

    date_range_result = calculate_date_range(filter_type, filter_date)

    query = db.query(Attendance).filter(
        Attendance.school_id == school_id,
        Attendance.classroom_id == classroom_id,
        Attendance.date >= date_range_result.start_date,
        Attendance.date < date_range_result.end_date,
    )

    attendances = query.all()

    metrics = MetricsCounter()

    # Single pass through the data
    for attendance in attendances:
        if attendance.status == AttendanceStatus.PRESENT.value:
            metrics.total_present += 1
            if attendance.student.gender == Gender.MALE.value:
                metrics.total_present_male += 1
            elif attendance.student.gender == Gender.FEMALE.value:
                metrics.total_present_female += 1
        elif attendance.status == AttendanceStatus.ABSENT.value:
            metrics.total_absent += 1
            if attendance.student.gender == Gender.MALE.value:
                metrics.total_absent_male += 1
            elif attendance.student.gender == Gender.FEMALE.value:
                metrics.total_absent_female += 1
        else:
            raise Exception()

    return AttendanceMetrics(
        total_present=metrics.total_present,
        total_absent=metrics.total_absent,
        total_present_male=metrics.total_present_male,
        total_present_female=metrics.total_present_female,
        total_absent_male=metrics.total_absent_male,
        total_absent_female=metrics.total_absent_female,
        start_date=date_range_result.start_date,
        end_date=date_range_result.end_date,
        filter_type=filter_type,
    )


def get_entire_school_attendance_metrics(
    db: DatabaseDependency,
    school_id: uuid.UUID,
    filter_type: str = "day",
    filter_date: typing.Optional[datetime.datetime] = None,
) -> AttendanceMetrics:

    date_range_result = calculate_date_range(filter_type, filter_date)

    query = db.query(Attendance).filter(
        Attendance.school_id == school_id,
        Attendance.date >= date_range_result.start_date,
        Attendance.date < date_range_result.end_date,
    )

    attendances = query.all()

    metrics = MetricsCounter()

    for attendance in attendances:

        if attendance.status == AttendanceStatus.PRESENT.value:
            metrics.total_present += 1
            if attendance.student.gender == Gender.MALE.value:
                metrics.total_present_male += 1
            elif attendance.student.gender == Gender.FEMALE.value:
                metrics.total_present_female += 1
        elif attendance.status == AttendanceStatus.ABSENT.value:
            metrics.total_absent += 1
            if attendance.student.gender == Gender.MALE.value:
                metrics.total_absent_male += 1
            elif attendance.student.gender == Gender.FEMALE.value:
                metrics.total_absent_female += 1
        else:
            raise Exception()

    return AttendanceMetrics(
        total_present=metrics.total_present,
        total_absent=metrics.total_absent,
        total_present_male=metrics.total_present_male,
        total_present_female=metrics.total_present_female,
        total_absent_male=metrics.total_absent_male,
        total_absent_female=metrics.total_absent_female,
        start_date=date_range_result.start_date,
        end_date=date_range_result.end_date,
        filter_type=filter_type,
    )


class PaymentStats(BaseModel):
    total_received_amount: float
    by_method: dict[str, PaymentMethodStats]
    year: int

    @classmethod
    def from_payments(cls, payments: list[Payment], year: int) -> "PaymentStats":
        method_stats: dict[str, PaymentMethodStats] = {}
        total_received_amount = 0

        # Group payments by method and calculate stats
        for payment in payments:
            if payment.method not in method_stats:
                method_stats[payment.method] = PaymentMethodStats(amount=0, count=0)

            method_stats[payment.method].amount += payment.amount
            method_stats[payment.method].count += 1
            total_received_amount += payment.amount

        return cls(
            total_received_amount=total_received_amount,
            by_method=method_stats,
            year=year,
        )


def student_dto(student: Student) -> dict:
    return {
        "grade_level": student.grade_level,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "classroom_id": student.classroom_id,
        "user_id": student.user_id,
        "id": student.id,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
    }


def teacher_dto(teacher: Teacher) -> dict:
    return {
        "school_id": teacher.school_id,
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "phone_number": teacher.phone_number,
        "email": teacher.email,
        "created_at": teacher.created_at,
        "updated_at": teacher.updated_at,
    }


def dashboard_resources_dto(
    students: list[Student],
    teachers: list[Teacher],
    total_students_managed: int,
    total_current_year_students_enrollment: int,
    total_teachers_managed: int,
    payments: PaymentStats,
    current_year: int,
    attendance_metrics: AttendanceMetrics,
) -> dict:

    return {
        "current_year": current_year,
        "students_total": total_students_managed,
        "current_year_students_enrollment_total": total_current_year_students_enrollment,
        "teachers_total": total_teachers_managed,
        "attendance": attendance_metrics,
        "teachers" "payments": payments,
        "teachers": [teacher_dto(teacher) for teacher in teachers],
        "students": [student_dto(student) for student in students],
    }


@router.get("/school/dashboard-resources")
async def get_all_students(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    filter_type: str = Query("day", enum=["day", "week", "month", "year"]),
    filter_date: typing.Optional[datetime.datetime] = Query(
        None, description="Filter date, defaults to today"
    ),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    school_id = user.school_id or raise_exception()

    current_year = datetime.datetime.now().year
    year_start = datetime.datetime(current_year, 1, 1)
    year_end = datetime.datetime(current_year + 1, 1, 1)

    all_payments_for_this_year = (
        db.query(Payment)
        .filter(
            Payment.school_id == school_id,
            Payment.date >= year_start,
            Payment.date < year_end,
        )
        .all()
    )

    payment_summary = PaymentStats.from_payments(
        all_payments_for_this_year, current_year
    )

    if user.has_role_type(RoleType.SCHOOL_ADMIN):
        total_students_managed = (
            db.query(func.count(Student.id))
            .join(SchoolStudentAssociation)
            .filter(SchoolStudentAssociation.school_id == school_id)
            .scalar()
        )
        total_teachers_managed = (
            db.query(func.count(Teacher.id))
            .filter(Teacher.school_id == school_id)
            .scalar()
        )
        overall_school_students_created_this_year = (
            db.query(func.count(Student.id))
            .join(SchoolStudentAssociation)
            .filter(
                SchoolStudentAssociation.school_id == school_id,
                Student.created_at >= year_start,
                Student.created_at < year_end,
            )
            .scalar()
        )

        students = (
            db.query(Student)
            .join(SchoolStudentAssociation)
            .filter(SchoolStudentAssociation.school_id == school_id)
            .limit(6)
            .all()
        )

        teachers = (
            db.query(Teacher).filter(Teacher.school_id == school_id).limit(6).all()
        )
        #
        #
        #
        attendance_metrics = get_entire_school_attendance_metrics(
            db,
            school_id=school_id,
            filter_type=filter_type,
            filter_date=filter_date,
        )

    elif user.has_role_type(RoleType.CLASS_TEACHER):
        teacher_id = user.teacher_user.id or raise_exception()

        total_students_managed = (
            db.query(func.count(Student.id))
            .join(Student.classroom)
            .join(Classroom.teacher_associations)
            .filter(
                ClassTeacherAssociation.teacher_id == teacher_id,
                ClassTeacherAssociation.is_primary == True,
            )
            .scalar()
        )

        overall_school_students_created_this_year = (
            db.query(func.count(Student.id))
            .join(Student.classroom)
            .join(Classroom.teacher_associations)
            .filter(
                ClassTeacherAssociation.teacher_id == teacher_id,
                ClassTeacherAssociation.is_primary == True,
                Student.created_at >= year_start,
                Student.created_at < year_end,
            )
            .scalar()
        )

        students = (
            db.query(Student)
            .join(Student.classroom)
            .join(Classroom.teacher_associations)
            .filter(
                ClassTeacherAssociation.teacher_id == teacher_id,
                ClassTeacherAssociation.is_primary == True,
            )
            .limit(6)
            .all()
        )
        #
        # ---
        #
        classroom = (
            db.query(Classroom)
            .join(ClassTeacherAssociation)
            .filter(
                ClassTeacherAssociation.teacher_id == teacher_id,
                ClassTeacherAssociation.is_primary == True,
            )
            .first()
        )
        if not classroom:
            raise Exception()

        total_teachers_managed = (
            db.query(func.count(Teacher.id))
            .join(ClassTeacherAssociation)
            .filter(ClassTeacherAssociation.classroom_id == classroom.id)
            .scalar()
        )
        teachers = (
            db.query(Teacher)
            .join(ClassTeacherAssociation)
            .filter(ClassTeacherAssociation.classroom_id == classroom.id)
            .limit(6)
            .all()
        )

        attendance_metrics = get_classroom_attendance_metrics(
            db,
            school_id=school_id,
            classroom_id=classroom.id,
            filter_type=filter_type,
            filter_date=filter_date,
        )

    else:
        raise HTTPException(403)

    return dashboard_resources_dto(
        students=students,
        total_students_managed=total_students_managed,
        total_current_year_students_enrollment=overall_school_students_created_this_year,
        current_year=current_year,
        payments=payment_summary,
        attendance_metrics=attendance_metrics,
        teachers=teachers,
        total_teachers_managed=total_teachers_managed,
    )


@router.get("/school/list", status_code=status.HTTP_200_OK)
def get_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not user.has_role_type(RoleType.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="permission-denied")

    schools = db.query(School).offset(offset).limit(limit).all()

    return schools


class UpdateSchool(BaseModel):
    name: typing.Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    location: str
    phone_number: str
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    website: str
    logo: str


@router.put("/school/{school_id}/update", status_code=status.HTTP_204_NO_CONTENT)
def update_school(
    db: DatabaseDependency,
    body: UpdateSchool,
    auth_context: UserAuthenticationContextDependency,
    school_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="school-not-found")

    school.name = body.name

    db.commit()
    return {}


@router.get("/school/{school_id}/delete", status_code=status.HTTP_200_OK)
def get_school_by_id(
    db: DatabaseDependency,
    school_id: int,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="school-not-found")

    return school
