import os
import jwt
import uuid
import datetime
from typing import Union
import hashlib

from pydantic import BaseModel
from backend.email_service.mail_service import EmailServiceDependency, SendEmailParams
from backend.raise_exception import raise_exception
from backend.user.user_models import User, UserSession
from backend.school.school_model import School
from fastapi import APIRouter, HTTPException, Response, status
from backend.database.database import DatabaseDependency
from backend.user.passwords import hash_password, verify_password
from backend.user.user_authentication import OptionalUserAuthenticationContextDependency
from pyotp import TOTP

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


router = APIRouter()


class RegisterRequestBody(BaseModel):
    email: str
    password: str
    username: str
    name: str
    school_number: str
    country: str


@router.post("/auth/user/register", status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequestBody,
    db: DatabaseDependency,
):
    school_user = (
        db.query(User)
        .filter((User.email == body.email) | (User.username == body.username))
        .first()
    )

    if school_user:
        raise HTTPException(
            status_code=409, detail="School with that email already exists"
        )

    school = db.query(School).filter(School.school_number == body.school_number).first()
    if school:
        raise HTTPException(
            status_code=409, detail="School with that number already exists"
        )

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        username=body.username,
    )

    db.add(user)
    db.flush()

    new_school = School(
        name=body.name,
        school_number=body.school_number,
        country=body.country,
        user_id=user.id,
    )
    db.add(new_school)
    db.flush()
    db.commit()

    return {"message": "School registered successfully"}


class LoginRequestBody(BaseModel):
    identity: str
    password: str


@router.post("/auth/user/login", status_code=status.HTTP_200_OK)
def login(
    body: LoginRequestBody,
    response: Response,
    db: DatabaseDependency,
):
    user = (
        db.query(User)
        .filter((User.email == body.identity) | (User.username == body.identity))
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    school_id = user.school_id or raise_exception()

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=404, detail="Invalid password or username")

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
            "permissions": user.all_permissions,
        },
        "name": user.name,
        "school_id": school_id,
    }


@router.post("/auth/user/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
):
    response.delete_cookie(
        key="user_access_token",
    )
    return {"message": "logout-successfully"}


@router.get("/auth/user/session", status_code=status.HTTP_200_OK)
def get_user_session(
    db: DatabaseDependency,
    auth_context: OptionalUserAuthenticationContextDependency,
):
    if not auth_context:
        raise HTTPException(status_code=404)

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.roles:
        raise HTTPException(status_code=403, detail="You don't have permission")
    # school details
    # user info
    # ---
    school_id = user.school_id or raise_exception()
    school = db.query(School).filter(School.id == school_id).first()

    if not school:
        raise HTTPException(404)

    return {
        "user_id": auth_context.user_id,
        "roles": user.roles,
        "permissions": user.all_permissions,
        "name": user.name,
        "email": user.email,
        "school": {
            "id": school_id,
            "name": school.name,
            "number": school.school_number,
            "address": school.address,
        },
    }


class TriggerSetPasswordWithEmailRequestBody(BaseModel):
    identity: str


class TriggerSetPasswordWithIDRequestBody(BaseModel):
    id: uuid.UUID


@router.post("/auth/user/trigger_set_password")
def trigger_set_password(
    db: DatabaseDependency,
    email_service: EmailServiceDependency,
    body: Union[
        TriggerSetPasswordWithEmailRequestBody, TriggerSetPasswordWithIDRequestBody
    ],
):
    user = db.query(User)

    if isinstance(body, TriggerSetPasswordWithEmailRequestBody):
        user = user.filter(
            (User.email == body.identity) | (User.username == body.identity)
        )
    elif isinstance(body, TriggerSetPasswordWithIDRequestBody):
        user = user.filter(User.id == body.id)
    else:
        raise Exception()

    user = user.first()

    if not user:
        raise HTTPException(status_code=404)

    otp = TOTP(
        user.secret_key,
        digest=hashlib.sha256,
        digits=6,
        interval=300,
    ).now()

    email_params = SendEmailParams(
        email=user.email,
        subject="Set Password",
        message=f"Your password reset code is {otp}",
    )
    email_service.send(email_params)


class SetPasswordRequestBody(BaseModel):
    identity: str
    password: str
    otp: str


class SetPasswordTokenData(BaseModel):
    user_id: uuid.UUID


@router.post("/auth/user/set_password", status_code=status.HTTP_201_CREATED)
def set_password(
    db: DatabaseDependency,
    body: SetPasswordRequestBody,
):

    user = (
        db.query(User)
        .filter((User.email == body.identity) | (User.username == body.identity))
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not TOTP(
        user.secret_key,
        digest=hashlib.sha256,
        digits=6,
        interval=300,
    ).verify(body.otp):
        raise HTTPException(status_code=404, detail="invalid-totp-code")

    user.password_hash = hash_password(body.password)
    db.commit()

    return {"message": "password-reset-successfully"}
