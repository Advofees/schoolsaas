import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.school.school_model import SchoolParent, SchoolStudentAssociation
from backend.user.user_models import User
from backend.student.student_model import Student
from backend.classroom.classroom_model import Classroom
from backend.parent.parent_model import ParentStudentAssociation
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.passwords import hash_password

router = APIRouter()


class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    password: str
    email: str
    classroom_id: uuid.UUID
    parent_id: uuid.UUID


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

    classroom = db.query(Classroom).filter(Classroom.id == body.classroom_id).first()

    if not classroom:
        raise HTTPException(status_code=404, detail="classroom-not-found")

    # ---
    student_user = User(
        email=body.email,
        username=body.first_name + body.last_name,
        password_hash=hash_password(body.password),
    )
    db.add(student_user)

    student = Student(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        grade_level=body.grade_level,
        classroom_id=classroom.id,
        user_id=student_user.id,
    )

    db.add(student)
    db.flush()

    student_school_association = SchoolStudentAssociation(
        student_id=student.id, school_id=classroom.school_id
    )
    db.add(student_school_association)
    db.flush()
    # ---
    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id, student_id=student.id
    )
    db.add(parent_student_association)
    db.flush()
    db.commit()

    return {"message": "student-registered-successfully"}


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
