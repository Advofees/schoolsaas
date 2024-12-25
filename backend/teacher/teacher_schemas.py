import datetime
import uuid
from backend.teacher.teacher_model import Teacher
from pydantic import BaseModel


class TeacherResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


def to_teacher_dto(teacher: Teacher) -> TeacherResponse:
    return TeacherResponse(
        id=teacher.id,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        email=teacher.email,
        phone_number=teacher.phone_number,
        user_id=teacher.user_id,
        created_at=teacher.created_at,
        updated_at=teacher.updated_at,
    )
