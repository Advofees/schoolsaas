import os
import jwt
import uuid
import datetime
from typing import Union
from pydantic import BaseModel
from backend.models import School, User, UserSession
from fastapi import APIRouter, HTTPException, Response, status
from backend.database.database import DatabaseDependency
from backend.user.passwords import hash_password, verify_password
from backend.user.user_authentication import OptionalUserAuthenticationContextDependency

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


router = APIRouter()


class LoginRequestBody(BaseModel):
    email: str
    password: str


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
    school_user = db.query(User).filter(User.email == body.email).first()

    if school_user:
        raise HTTPException(
            status_code=409, detail="School with that email already exists"
        )

    school = db.query(School).filter(School.school_number == body.school_number).first()
    if school:
        raise HTTPException(
            status_code=409, detail="School with that number already exists"
        )

    new_school = School(
        name=body.name,
        school_number=body.school_number,
        country=body.country,
    )
    db.add(new_school)
    db.flush()
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        username=body.username,
        school_id=new_school.id,
        student_id=None,
        parent_id=None,
    )

    db.add(user)
    db.flush()
    db.commit()

    return {"message": "School registered successfully"}


@router.post("/auth/user/login",status_code=status.HTTP_200_OK)
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


@router.post("/auth/user/logout",status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
):
    response.delete_cookie(
        key="user_access_token",
    )
    return {}


@router.get("/auth/user/session",status_code=status.HTTP_200_OK)
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


@router.post("/auth/user/set_password",status_code=status.HTTP_201_CREATED)
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
    return {}
