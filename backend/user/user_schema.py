import uuid
from pydantic import BaseModel
from backend.user.user_models import User


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str


def to_user_dto(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email)
