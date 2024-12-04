import jwt
import os
import uuid
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.user.user_models import UserSession
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from dataclasses import dataclass

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


class JWTPayload(BaseModel):
    session_id: uuid.UUID


@dataclass
class UserAuthenticationContext:
    user_id: uuid.UUID


def get_user_authentication_context(
    user_access_token: Annotated[str, Cookie(include_in_schema=False)],
    db: DatabaseDependency,
):
    try:
        raw_payload = jwt.decode(
            user_access_token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, headers={"X-Authentication-Type": "user"})

    payload = JWTPayload.model_validate(raw_payload)

    session = db.query(UserSession).filter(UserSession.id == payload.session_id).first()

    if not session:
        raise HTTPException(status_code=401, headers={"X-Authentication-Type": "user"})

    return UserAuthenticationContext(user_id=session.user_id)


UserAuthenticationContextDependency = Annotated[
    UserAuthenticationContext,
    Depends(get_user_authentication_context),
]


def get_optional_user_authentication_context(
    db: DatabaseDependency,
    user_access_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
):
    if user_access_token:
        return get_user_authentication_context(user_access_token, db)
    else:
        return None


OptionalUserAuthenticationContextDependency = Annotated[
    UserAuthenticationContext | None,
    Depends(get_optional_user_authentication_context),
]
