import os
import jwt
import uuid
import datetime
from typing import Union
from pydantic import BaseModel
from backend.models import User,  UserSession
from fastapi import APIRouter, HTTPException, Response
from backend.database.database import DatabaseDependency
from backend.user.passwords import hash_password, verify_password
from backend.user.user_authentication import OptionalUserAuthenticationContextDependency

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


router = APIRouter()


class LoginRequestBody(BaseModel):
    email: str
    password: str


@router.post("/auth/user/login")
def login(
    body: LoginRequestBody,
    response: Response,
    db: DatabaseDependency,
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=404)

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=404)

    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.expire_at < datetime.datetime.now(),
    ).delete()

    db.flush()

    session = UserSession(user_id=user.id)
    db.add(session)
    db.flush()

    # ---

    access_token = jwt.encode(
        {
            "session_id": str(session.id),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    db.commit()

    response.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=True,
        expires=60 * 60 * 24 * 365,
        samesite="strict",
    )

    return {
        "access_token": access_token,
        "session": {
            "user_id": session.user_id,
            "roles": user.roles,
        },
    }


@router.post("/auth/user/logout")
def logout(
    response: Response,
):
    response.delete_cookie(
        key="user_access_token",
    )
    return {}


@router.get("/auth/user/session")
def get_user_session(
    db: DatabaseDependency,
    auth_context: OptionalUserAuthenticationContextDependency,
):
    if not auth_context:
        raise HTTPException(status_code=404)

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise Exception()

    if not user.roles:
        raise Exception()
    


    return {
        "user_id": auth_context.user_id,
        "roles": user.roles,

    }


class TriggerSetPasswordWithEmailRequestBody(BaseModel):
    email: str


class TriggerSetPasswordWithIDRequestBody(BaseModel):
    id: uuid.UUID


@router.post("/auth/user/trigger_set_password")
def trigger_set_password(
    db: DatabaseDependency,
    # email_service: EmailServiceDependency,
    body: Union[
        TriggerSetPasswordWithEmailRequestBody, TriggerSetPasswordWithIDRequestBody
    ],
):
    user = db.query(User)

    if isinstance(body, TriggerSetPasswordWithEmailRequestBody):
        user = user.filter(User.email == body.email)
    elif isinstance(body, TriggerSetPasswordWithIDRequestBody):
        user = user.filter(User.id == body.id)
    else:
        raise Exception()

    user = user.first()

    if not user:
        raise HTTPException(status_code=404)

    token = jwt.encode(
        {
            "ext": str(datetime.datetime.now() + datetime.timedelta(hours=1)),
            "user_id": str(user.id),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    # email_service.send_email(
    #     address=user.email,
    #     subject="Set Password",
    #     text=f"Your password reset link: {dashboard_url}/user/set-password?token={token}",
    # )


class SetPasswordRequestBody(BaseModel):
    password: str
    token: str


class SetPasswordTokenData(BaseModel):
    user_id: uuid.UUID


@router.post("/auth/user/set_password")
def set_password(
    db: DatabaseDependency,
    body: SetPasswordRequestBody,
):
    try:
        raw_payload = jwt.decode(
            body.token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=409, detail="expired-token")

    token_data = SetPasswordTokenData.model_validate(raw_payload)

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if not user:
        raise HTTPException(status_code=404)

    user.password_hash = hash_password(body.password)

    db.commit()
