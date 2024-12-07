import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import func

from backend.classroom.classroom_model import Classroom
from backend.database.database import DatabaseDependency
from backend.payment.payment_model import Payment
from backend.raise_exception import raise_exception
from backend.school.school_model import School, SchoolStudentAssociation
from backend.student.student_model import Student
from backend.teacher.teacher_model import ClassTeacherAssociation
from backend.user.user_models import User, RoleType
from backend.user.user_authentication import UserAuthenticationContextDependency
import datetime

router = APIRouter()


class PaymentMethodStats(BaseModel):
    amount: float
    count: int


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


def dashboard_resources_dto(
    students: list[Student],
    total_students_managed: int,
    total_current_year_students_enrollment: int,
    page: int,
    total_pages: int,
    payments: PaymentStats,
    current_year: int,
) -> dict:

    return {
        "total_students_managed": total_students_managed,
        "total_current_year_students_enrollment": total_current_year_students_enrollment,
        "page": page,
        "total_pages": total_pages,
        "current_year": current_year,
        "payments": payments,
        "students": [student_dto(student) for student in students],
    }


@router.get("/school/students/dashboard-resources")
async def get_all_students(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="students per page"),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)
    school_id = user.school_id or raise_exception()

    skip = (page - 1) * page_size

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
            .offset(skip)
            .limit(page_size)
            .all()
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
            .offset(skip)
            .limit(page_size)
            .all()
        )

    else:
        raise HTTPException(403)

    total_pages = total_students_managed // page_size + (
        1 if total_students_managed % page_size else 0
    )
    return dashboard_resources_dto(
        students=students,
        total_students_managed=total_students_managed,
        total_current_year_students_enrollment=overall_school_students_created_this_year,
        page=page,
        total_pages=total_pages,
        current_year=current_year,
        payments=payment_summary,
    )


class UpdateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str


@router.get("/school/list", status_code=status.HTTP_200_OK)
def get_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.has_role_type(RoleType.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="Permission denied")

    total_schools = db.query(School).count()

    schools = db.query(School).offset(offset).limit(limit).all()
    next_offset = offset + limit
    has_next = next_offset < total_schools

    return {
        "total": total_schools,
        "limit": limit,
        "offset": offset,
        "next": (
            f"/school/list?limit={limit}&offset={next_offset}" if has_next else None
        ),
        "schools": schools,
    }


@router.put("/school/{school_id}/update", status_code=status.HTTP_204_NO_CONTENT)
def update_school(
    db: DatabaseDependency,
    body: UpdateSchool,
    auth_context: UserAuthenticationContextDependency,
    school_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

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
        raise HTTPException(status_code=404, detail="User not found")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    return school
