import datetime
import typing
import uuid
import enum
from sqlalchemy import desc, asc
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel, StringConstraints, EmailStr
from backend.classroom.classroom_model import Classroom
from backend.database.database import DatabaseDependency
from backend.school.school_model import School
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.user.passwords import hash_password
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.teacher.teacher_schemas import to_teacher_dto, TeacherResponse
from backend.paginated_response import PaginatedResponse

router = APIRouter()


class OrderBy(enum.Enum):
    ASC = "asc"
    DESC = "desc"


class TeacherSortableFields(enum.Enum):
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    EMAIL = "email"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TeacherFilterParams(BaseModel):
    first_name: typing.Optional[str] = None
    last_name: typing.Optional[str] = None
    email: typing.Optional[str] = None
    has_primary_classroom: typing.Optional[bool] = None
    created_after: typing.Optional[datetime.datetime] = None
    created_before: typing.Optional[datetime.datetime] = None


@router.get("/teachers/by-school-id/list")
async def get_teachers_in_a_particular_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    order_field: typing.Optional[TeacherSortableFields] = None,
    order_direction: typing.Optional[OrderBy] = None,
    filters: TeacherFilterParams = Depends(),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    school = db.query(School).filter(School.id == user.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
        )

    query = db.query(Teacher).filter(Teacher.school_id == school.id)

    if filters.first_name:
        query = query.filter(Teacher.first_name.ilike(f"%{filters.first_name}%"))

    if filters.last_name:
        query = query.filter(Teacher.last_name.ilike(f"%{filters.last_name}%"))

    if filters.email:
        query = query.filter(Teacher.email.ilike(f"%{filters.email}%"))

    if filters.has_primary_classroom is not None:
        if filters.has_primary_classroom:
            query = query.join(ClassTeacherAssociation).filter(
                ClassTeacherAssociation.is_primary == True
            )
        else:
            query = query.outerjoin(ClassTeacherAssociation).filter(
                ClassTeacherAssociation.is_primary.is_(None)
            )

    if filters.created_after:
        query = query.filter(Teacher.created_at >= filters.created_after)

    if filters.created_before:
        query = query.filter(Teacher.created_at <= filters.created_before)

    total_count = query.count()

    if order_field and order_direction:
        sort_column = getattr(Teacher, order_field.value)
        if order_direction == OrderBy.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(asc(Teacher.last_name), asc(Teacher.first_name))

    offset = (page - 1) * limit
    teachers = query.offset(offset).limit(limit).all()

    return PaginatedResponse[TeacherResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[to_teacher_dto(teacher) for teacher in teachers],
    )


@router.get("/teachers/by-teacher-id/{teacher_id}")
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

    return to_teacher_dto(teacher=teacher)


class TeacherClassroomFilterParams(BaseModel):
    first_name: typing.Optional[str] = None
    last_name: typing.Optional[str] = None
    email: typing.Optional[str] = None
    is_primary: typing.Optional[bool] = None
    created_after: typing.Optional[datetime.datetime] = None
    created_before: typing.Optional[datetime.datetime] = None


@router.get("/teachers/by-classroom-id/{classroom_id}")
async def get_teacher_in_particular_school_classroom_by_classroom_id(
    classroom_id: uuid.UUID,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    order_field: typing.Optional[TeacherSortableFields] = None,
    order_direction: typing.Optional[OrderBy] = None,
    filters: TeacherClassroomFilterParams = Depends(),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    query = (
        db.query(Teacher)
        .join(ClassTeacherAssociation)
        .filter(ClassTeacherAssociation.classroom_id == classroom.id)
    )

    if filters.first_name:
        query = query.filter(Teacher.first_name.ilike(f"%{filters.first_name}%"))

    if filters.last_name:
        query = query.filter(Teacher.last_name.ilike(f"%{filters.last_name}%"))

    if filters.email:
        query = query.filter(Teacher.email.ilike(f"%{filters.email}%"))

    if filters.is_primary is not None:
        query = query.filter(ClassTeacherAssociation.is_primary == filters.is_primary)

    if filters.created_after:
        query = query.filter(Teacher.created_at >= filters.created_after)

    if filters.created_before:
        query = query.filter(Teacher.created_at <= filters.created_before)

    total_count = query.count()

    if order_field and order_direction:
        sort_column = getattr(Teacher, order_field.value)
        if order_direction == OrderBy.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:

        query = query.order_by(asc(Teacher.last_name), asc(Teacher.first_name))

    offset = (page - 1) * limit
    teachers = query.offset(offset).limit(limit).all()

    return PaginatedResponse[TeacherResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[to_teacher_dto(teacher) for teacher in teachers],
    )


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

    if not (
        user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
        or user.has_role_type(RoleType.SUPER_ADMIN)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user-must-be-in-a-school"
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
            school_id=user.school_id,
        )
        db.add(teacher_role)
        db.flush()

    teacher_role_association = UserRoleAssociation(
        user_id=new_teacher_user.id,
        role_id=teacher_role.id,
        school_id=user.school_id,
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
