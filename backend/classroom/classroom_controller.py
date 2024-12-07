import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.user.user_models import User
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.classroom.classroom_model import Classroom

router = APIRouter()


class classTeacherAssociation(BaseModel):
    is_primary: bool


@router.post("/classroom/{classrom_id}/teachers/{teacher_id}/associate")
def assign_teacher_to_classroom(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    teacher_id: uuid.UUID,
    classroom_id: uuid.UUID,
    body: classTeacherAssociation,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)

    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(404)

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(404)

    association = ClassTeacherAssociation(
        teacher_id=teacher.id, classroom_id=classroom.id, is_primary=body.is_primary
    )
    db.add(association)
    db.commit()
