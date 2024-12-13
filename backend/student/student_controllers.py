import datetime
import typing
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, StringConstraints, EmailStr

from backend.school.school_model import SchoolParent, SchoolStudentAssociation
from backend.teacher.teacher_model import ClassTeacherAssociation
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.student.student_model import Student
from backend.classroom.classroom_model import Classroom
from backend.parent.parent_model import ParentStudentAssociation
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.passwords import hash_password

router = APIRouter()


class CreateStudent(BaseModel):
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    parent = db.query(SchoolParent).filter(SchoolParent.id == body.parent_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Parent  not found")

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == body.classroom_id, Classroom.school_id == user.school_id
        )
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="classroom-not-found")

    # ---
    new_student_user = User(
        email=body.email,
        username=body.first_name + body.last_name,
        password_hash=hash_password(body.password),
    )
    db.add(new_student_user)

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
    # ---
    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id, student_id=student.id
    )
    db.add(parent_student_association)
    db.flush()

    student_role = db.query(Role).filter(Role.name == RoleType.TEACHER.name).first()

    if not student_role:
        student_role = Role(
            name=RoleType.STUDENT.name,
            type=RoleType.STUDENT,
            description=RoleType.STUDENT.value,
        )
        db.add(student_role)
        db.flush()

    student_role_association = UserRoleAssociation(
        user_id=new_student_user.id, role_id=student_role.id
    )
    db.add(student_role_association)
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.get("/students/{student_id}/parents")
async def get_student_parents(
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

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    parents = (
        db.query(SchoolParent)
        .join(ParentStudentAssociation)
        .filter(ParentStudentAssociation.student_id == student_id)
        .all()
    )

    return parents


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
    if user.has_role_type(RoleType.SCHOOL_ADMIN):
        students = (
            db.query(Student)
            .join(SchoolStudentAssociation)
            .filter(SchoolStudentAssociation.school_id == user.school_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
    elif user.has_role_type(RoleType.CLASS_TEACHER):
        teacher_id = user.teacher_user.id
        if not user.teacher_user.id:
            raise Exception()

        teacher_id = user.teacher_user.id
        students = (
            db.query(Student)
            .join(Student.classroom)
            .join(Classroom.teacher_associations)
            .filter(
                ClassTeacherAssociation.teacher_id == teacher_id,
                ClassTeacherAssociation.is_primary == True,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    return students
