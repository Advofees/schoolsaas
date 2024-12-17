import uuid
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.user.user_models import RoleType, User
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.classroom.classroom_model import Classroom

router = APIRouter()


@router.get("/classrooms/list")
def school_classrooms(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(status_code=403, detail="permission-denied")

    classrooms = (
        db.query(Classroom)
        .filter(Classroom.school_id == user.school_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return classrooms


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
