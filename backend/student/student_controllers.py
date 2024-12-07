import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query
from backend.raise_exception import raise_exception
from backend.teacher.teacher_model import ClassTeacherAssociation
from backend.user.user_models import RoleType, User
from backend.student.student_model import Student
from backend.classroom.classroom_model import Classroom
from backend.school.school_model import SchoolParent, SchoolStudentAssociation
from backend.parent.parent_model import ParentStudentAssociation
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from sqlalchemy import func
from backend.payment.payment_model import Payment

router = APIRouter()


class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    parent_id: uuid.UUID
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    classroom_id: uuid.UUID


@router.post("/students/create")
async def create_student(
    db: DatabaseDependency,
    body: CreateStudent,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    parent = db.query(SchoolParent).filter(SchoolParent.id == body.parent_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Parent  not found")

    class_room = db.query(Classroom).filter(Classroom.id == body.classroom_id).first()

    if not class_room:
        raise HTTPException(status_code=404, detail="Classroom not found")
    # --

    if not any(
        permission.permissions.student_permissions.can_add_students is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    # ---
    student_user = User(
        email=body.first_name + body.last_name + "@student.com",
        username=body.first_name + body.last_name,
        password_hash="student",
    )
    db.add(student_user)
    student = Student(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        grade_level=body.grade_level,
        classroom_id=class_room.id,
        user_id=student_user.id,
    )

    db.add(student)
    db.flush()
    # ---
    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id, student_id=student.id
    )
    db.add(parent_student_association)
    db.flush()
    db.commit()

    return {}


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
        "students": students,
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


@router.get("/students/{student_id}")
async def get_student(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    return student


@router.get("/students/{student_id}/parents")
async def get_student_parents(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students
        and permission.permissions.parent_permissions.can_view_parents is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    parents = (
        db.query(SchoolParent)
        .join(ParentStudentAssociation)
        .filter(ParentStudentAssociation.student_id == student_id)
        .all()
    )

    return parents


@router.get("/students/{student_id}/classroom")
async def get_student_classroom(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="permission-denied")

    classroom = db.query(Classroom).filter(Classroom.id == student.classroom_id).first()

    return classroom


@router.get("/students/{class_room_id}")
async def get_students_in_classroom(
    db: DatabaseDependency,
    class_room_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    class_room = db.query(Classroom).filter(Classroom.id == class_room_id).first()

    if not class_room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    students = db.query(Student).filter(Student.classroom_id == class_room_id).all()

    return students
