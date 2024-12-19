import datetime
import typing
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, StringConstraints, EmailStr

from backend.school.school_model import (
    SchoolParent,
    SchoolParentAssociation,
    SchoolStudentAssociation,
)
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.student.student_model import Student
from backend.classroom.classroom_model import Classroom
from backend.parent.parent_model import ParentRelationshipType, ParentStudentAssociation
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.passwords import hash_password

router = APIRouter()


@router.get("/students/{student_id}")
async def get_student(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    student = (
        db.query(Student)
        .join(SchoolStudentAssociation)
        .filter(
            Student.id == student_id,
            SchoolStudentAssociation.school_id == user.school_id,
            SchoolStudentAssociation.is_active == True,
        )
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return {
        "id": student.id,
        "nemis_number": student.nemis_number,
        "email": student.user.email,
        "user_id": student.user_id,
    }


@router.get("/students/{classroom_id}")
async def get_students_in_classroom(
    db: DatabaseDependency,
    classroom_id: uuid.UUID,
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
    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    classroom = (
        db.query(Classroom)
        .filter(Classroom.id == classroom_id, Classroom.school_id == user.school_id)
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    students = (
        db.query(Student)
        .filter(Student.classroom_id == classroom.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return students


@router.get("/students/list")
async def get_all_students_for_a_particular_school(
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
    if not user.has_role_type(RoleType.SCHOOL_ADMIN) or user.has_role_type(
        RoleType.SCHOOL_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    students = (
        db.query(Student)
        .join(SchoolStudentAssociation)
        .filter(SchoolStudentAssociation.school_id == user.school_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return students


class createStudent(BaseModel):
    first_name: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    last_name: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    password: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    username: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    classroom_id: uuid.UUID
    parent_id: uuid.UUID
    parent_relationship_type: ParentRelationshipType


@router.post("/students/create")
async def create_student(
    db: DatabaseDependency,
    body: createStudent,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    parent = (
        db.query(SchoolParent)
        .join(SchoolParentAssociation)
        .filter(
            SchoolParent.id == body.parent_id,
            SchoolParentAssociation.school_id == user.school_id,
            SchoolParentAssociation.is_active == True,
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=404,
            detail="Parent not found or not associated with this school",
        )

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == body.classroom_id, Classroom.school_id == user.school_id
        )
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    new_student_user = User(
        email=body.email,
        username=body.username,
        password_hash=hash_password(body.password),
    )
    db.add(new_student_user)
    db.flush()

    student = Student(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        grade_level=body.grade_level,
        classroom_id=classroom.id,
        user_id=new_student_user.id,
    )
    db.add(student)
    db.flush()

    student_school_association = SchoolStudentAssociation(
        student_id=student.id, school_id=classroom.school_id
    )
    db.add(student_school_association)
    db.flush()

    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id,
        student_id=student.id,
        relationship_type=body.parent_relationship_type.value,
    )
    db.add(parent_student_association)
    db.flush()

    student_role = (
        db.query(Role)
        .filter(Role.type == RoleType.STUDENT, Role.school_id == classroom.school_id)
        .first()
    )

    if not student_role:
        student_role = Role(
            name=RoleType.STUDENT.name,
            type=RoleType.STUDENT,
            description=RoleType.STUDENT.value,
            school_id=classroom.school_id,
        )
        db.add(student_role)
        db.flush()

    student_role_association = UserRoleAssociation(
        user_id=new_student_user.id,
        role_id=student_role.id,
        school_id=classroom.school_id,
    )
    db.add(student_role_association)
    db.flush()

    db.commit()

    return {"message": "student-registered-successfully"}
