import os
import jwt
import uuid
import datetime
from sqlalchemy.orm import Session
import typing

# from pyotp import TOTP
# import hashlib
from pydantic import BaseModel
from backend.email_service.mail_service import EmailServiceDependency, SendEmailParams
from backend.raise_exception import raise_exception
from backend.user.user_models import (
    Role,
    RoleType,
    User,
    UserRoleAssociation,
    UserSession,
    Profile,
)
from pydantic import BaseModel, StringConstraints, EmailStr
from backend.school.school_model import School
from fastapi import APIRouter, HTTPException, Response, status
from backend.database.database import DatabaseDependency
from backend.user.passwords import hash_password, verify_password
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.file.file_model import File

from backend.s3.aws_s3_service import init_s3_client
from backend.s3.s3_constants import BUCKET_NAME, PRESIGNED_URL_EXPIRATION

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
FRONTEND_URL = os.environ["FRONTEND_URL"]

router = APIRouter()


def get_profile_url(
    profile_id: uuid.UUID,
    db: Session,
) -> typing.Optional[str]:
    s3 = init_s3_client()
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        return None

    file = db.query(File).filter(File.id == profile.file_id).first()
    if not file:
        return None

    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": file.path},
        ExpiresIn=PRESIGNED_URL_EXPIRATION,
    )

    return presigned_url


class RegisterRequestBody(BaseModel):
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    password: str
    username: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    name: typing.Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
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
            status_code=status.HTTP_409_CONFLICT,
            detail="school-with-email-or-username-already-exists",
        )

    school = db.query(School).filter(School.school_number == body.school_number).first()
    if school:
        raise HTTPException(status_code=409, detail="school-code-already-exists")

    school_admin_user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        username=body.username,
    )

    db.add(school_admin_user)
    db.flush()

    new_school = School(
        name=body.name,
        school_number=body.school_number,
        country=body.country,
        user_id=school_admin_user.id,
    )
    db.add(new_school)
    db.flush()

    school_admin_role = (
        db.query(Role).filter(Role.name == RoleType.SCHOOL_ADMIN.name).first()
    )
    if not school_admin_role:
        school_admin_role = Role(
            name=RoleType.SCHOOL_ADMIN.name,
            type=RoleType.SCHOOL_ADMIN,
            description=RoleType.SCHOOL_ADMIN.value,
        )

        db.add(school_admin_role)
        db.flush()

    school_user_role_association = UserRoleAssociation(
        user_id=school_admin_user.id, role_id=school_admin_role.id
    )
    db.add(school_user_role_association)
    db.flush()

    db.commit()

    return {"message": "school-registered-successfully"}


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid-credentials",
        )
    school_id = user.school_id or raise_exception()

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid-credentials",
        )

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
    return {"message": "logged-out-successfully"}


def logout_all(
    db: DatabaseDependency,
    user_id: uuid.UUID,
):
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
    ).delete()


@router.get("/auth/user/session", status_code=status.HTTP_200_OK)
def get_user_session(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unauthorized"
        )

    school_id = user.school_id or raise_exception()

    school = db.query(School).filter(School.id == school_id).first()

    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    profile_url = None
    if user.profile and user.profile.id:
        profile_url = get_profile_url(db=db, profile_id=user.profile.id)

    return {
        "user_id": auth_context.user_id,
        "name": user.name,
        "email": user.email,
        "profile_url": profile_url if profile_url else None,
        "school": {
            "id": school.id,
            "name": school.name,
            "number": school.school_number,
            "address": school.address,
        },
        "roles": user.roles,
        "permissions": user.all_permissions,
    }


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="expired-token"
        )

    token_data = SetPasswordTokenData.model_validate(raw_payload)

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user.password_hash = hash_password(body.password)

    db.commit()


class TriggerResetPasswordWithEmailRequestBody(BaseModel):
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]


@router.post("/auth/user/forgot-password")
def generate_link_to_reset_password_and_send_to_users_email(
    db: DatabaseDependency,
    body: TriggerResetPasswordWithEmailRequestBody,
    email_service: EmailServiceDependency,
):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    token = jwt.encode(
        {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=1),
            "user_id": str(user.id),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    email_params = SendEmailParams(
        email=user.email,
        subject="Set Password",
        message=f"Your password reset link: {reset_link}",
    )

    email_service.send(email_params)

    return {}


@router.post("/auth/user/request-password-change")
def generate_link_to_reset_password_and_send_to_authenticated_users_email(
    db: DatabaseDependency,
    email_service: EmailServiceDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    token = jwt.encode(
        {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=1),
            "user_id": str(user.id),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    email_params = SendEmailParams(
        email=user.email,
        subject="Set Password",
        message=f"Your password reset link: {reset_link}",
    )

    email_service.send(email_params)

    return {"message": "reset-link-sent-to-your-email"}


class ResetPasswordRequestBody(BaseModel):
    new_password: str
    token: str


class ResetPasswordTokenData(BaseModel):
    user_id: uuid.UUID


@router.post("/auth/user/reset-password")
def reset_password(
    db: DatabaseDependency,
    body: ResetPasswordRequestBody,
):
    try:
        raw_payload = jwt.decode(
            body.token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="expired-token"
        )

    token_data = ResetPasswordTokenData.model_validate(raw_payload)

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="invalid-token")

    user.password_hash = hash_password(body.new_password)

    db.flush()

    logout_all(db, user.id)

    db.flush()
    db.commit()
    return {"message": "password-reset-successfully"}


#
# LETS ONLY ADD OTP WHEN WE HAVE MONEY TO COVER EMAIL COSTS AND HAVE RATE LIMITER IN PLACE
#
# class GenerateAccountantUserTOTPRequestBody(BaseModel):
#     identity: str
#     password: str


# @router.post("/auth/user/generate_totp")
# def generate_totp_code_and_send_to_user_email(
#     body: GenerateAccountantUserTOTPRequestBody,
#     db: DatabaseDependency,
#     email_service: EmailServiceDependency,
# ):
#     user = db.query(User).filter(User.email == body.identity).first()

#     if not user:
#         raise HTTPException(status_code=404)

#     if not verify_password(body.password, user.password_hash):
#         raise HTTPException(status_code=404)

#     time_based_one_time_password_code = TOTP(
#         user.secret_key,
#         digest=hashlib.sha256,
#         digits=6,
#         interval=300,
#     ).now()

#     # ---

#     email_params = SendEmailParams(
#         email=user.email,
#         subject="VERIFICATION CODE",
#         message=f"Your CODE: {time_based_one_time_password_code}",
#     )
#     email_service.send(email_params)

#     return {"message": "login-verification-code-sent"}

# ---
