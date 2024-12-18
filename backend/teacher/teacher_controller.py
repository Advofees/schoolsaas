import typing
import uuid
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, StringConstraints, EmailStr
from backend.classroom.classroom_model import Classroom
from backend.database.database import DatabaseDependency
from backend.school.school_model import School
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.user.passwords import hash_password
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


def to_teacher_dto(teacher: Teacher) -> dict:
    return {
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "email": teacher.email,
        "phone_number": teacher.phone_number,
        "user_id": teacher.user_id,
        "created_at": teacher.created_at,
        "updated_at": teacher.updated_at,
    }


@router.get("/teachers/list")
async def get_teachers_in_a_particular_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    school = db.query(School).filter(School.id == user.school_user.id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
        )

    skip = (page - 1) * limit
    teachers = (
        db.query(Teacher)
        .filter(Teacher.school_id == school.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [to_teacher_dto(teacher) for teacher in teachers]


@router.get("/teachers/{teacher_id}")
async def get_teacher_in_particular_school_by_teacher_id(
    teacher_id: int,
    db: DatabaseDependency,
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
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )

    return teacher


@router.get("/teachers/classrooms/{classroom_id}")
async def get_teacher_in_particular_school_classroom_by_classroom_id(
    classroom_id: uuid.UUID,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()

    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    skip = (page - 1) * limit
    teachers = (
        db.query(Teacher)
        .join(ClassTeacherAssociation)
        .filter(ClassTeacherAssociation.classroom_id == classroom.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return teachers


class TeacherModel(BaseModel):
    first_name: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    last_name: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    phone: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    password: str


@router.post("/teachers/create")
async def create_teacher_in_particular_school(
    body: TeacherModel,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user-be-in-a-school"
        )

    user_with_email = db.query(User).filter(User.email == body.email).first()

    if user_with_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user-with-this-email-already-exists",
        )

    new_teacher_user = User(
        email=body.email,
        password_hash=hash_password(password=body.password),
        username=body.email,
    )
    db.add(new_teacher_user)

    teacher_role = db.query(Role).filter(Role.name == RoleType.TEACHER.name).first()

    if not teacher_role:
        teacher_role = Role(
            name=RoleType.TEACHER.name,
            type=RoleType.TEACHER,
            description=RoleType.TEACHER.value,
        )
        db.add(teacher_role)
        db.flush()

    teacher_role_association = UserRoleAssociation(
        user_id=new_teacher_user.id, role_id=teacher_role.id
    )
    db.add(teacher_role_association)
    db.flush()

    teacher_with_email = (
        db.query(Teacher)
        .filter(Teacher.email == body.email, Teacher.school_id == user.school_id)
        .first()
    )
    if teacher_with_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="teacher-with-this-email-already-exists",
        )

    new_teacher = Teacher(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        school_id=user.school_id,
        user_id=new_teacher_user.id,
    )
    db.add(new_teacher)
    db.commit()

    return {"message": "teacher-created-successfully"}
