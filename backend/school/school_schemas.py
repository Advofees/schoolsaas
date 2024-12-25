import datetime
import uuid
import typing
from pydantic import BaseModel, StringConstraints, EmailStr
from backend.school.school_model import School


class SchoolResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    country: str
    school_number: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UpdateSchool(BaseModel):
    name: typing.Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    location: str
    phone_number: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    website: str
    logo: str


def to_school_dto(school: School) -> SchoolResponse:
    return SchoolResponse(
        id=school.id,
        name=school.name,
        country=school.country,
        user_id=school.user_id,
        school_number=school.school_number,
        created_at=school.created_at,
        updated_at=school.updated_at,
    )
