import datetime
import uuid
import enum
import typing
from sqlalchemy import desc, asc
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.user.user_models import RoleType, User
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.classroom.classroom_model import Classroom
from backend.teacher.teacher_schemas import TeacherResponse, to_teacher_dto
from backend.paginated_response import PaginatedResponse

router = APIRouter()


class classRoomResponse(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    name: str
    grade_level: int
    class_teacher: TeacherResponse | None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class OrderBy(enum.Enum):
    ASC = "asc"
    DESC = "desc"


class ClassroomSortableFields(enum.Enum):
    NAME = "name"
    GRADE_LEVEL = "grade_level"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ClassroomFilterParams(BaseModel):
    grade_level: typing.Optional[int] = None
    name: typing.Optional[str] = None
    has_primary_teacher: typing.Optional[bool] = None
    created_after: typing.Optional[datetime.datetime] = None
    created_before: typing.Optional[datetime.datetime] = None


def classroom_to_dto(classroom: Classroom) -> classRoomResponse:
    return classRoomResponse(
        id=classroom.id,
        name=classroom.name,
        grade_level=classroom.grade_level,
        school_id=classroom.school_id,
        class_teacher=(
            to_teacher_dto(classroom.primary_teacher)
            if classroom.primary_teacher
            else None
        ),
        created_at=classroom.created_at,
        updated_at=classroom.updated_at,
    )


@router.get("/classrooms/by-school-id/list")
def school_classrooms(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    order_field: typing.Optional[ClassroomSortableFields] = None,
    order_direction: typing.Optional[OrderBy] = None,
    filters: ClassroomFilterParams = Depends(),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if not (
        user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):
        raise HTTPException(status_code=403, detail="permission-denied")

    query = db.query(Classroom).filter(Classroom.school_id == user.school_id)

    if filters.grade_level is not None:
        query = query.filter(Classroom.grade_level == filters.grade_level)

    if filters.name:
        query = query.filter(Classroom.name.ilike(f"%{filters.name}%"))

    if filters.has_primary_teacher is not None:
        if filters.has_primary_teacher:
            query = query.join(ClassTeacherAssociation).filter(
                ClassTeacherAssociation.is_primary == True
            )
        else:
            query = query.outerjoin(ClassTeacherAssociation).filter(
                ClassTeacherAssociation.is_primary.is_(None)
            )

    if filters.created_after:
        query = query.filter(Classroom.created_at >= filters.created_after)

    if filters.created_before:
        query = query.filter(Classroom.created_at <= filters.created_before)

    total_count = query.count()

    if order_field and order_direction:
        sort_column = getattr(Classroom, order_field.value)
        if order_direction == OrderBy.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(asc(Classroom.name))

    offset = (page - 1) * limit
    classrooms = query.offset(offset).limit(limit).all()

    return PaginatedResponse[classRoomResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[classroom_to_dto(classroom) for classroom in classrooms],
    )


class classTeacherAssociation(BaseModel):
    is_primary: bool


@router.post("/classroom/{classrom_id}/teachers/{teacher_id}/add")
def assign_teacher_to_classroom(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    teacher_id: uuid.UUID,
    classroom_id: uuid.UUID,
    body: classTeacherAssociation,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    association = ClassTeacherAssociation(
        teacher_id=teacher.id, classroom_id=classroom.id, is_primary=body.is_primary
    )
    db.add(association)
    db.commit()
