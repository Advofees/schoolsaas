import typing
from pydantic import BaseModel, StringConstraints, EmailStr


class createParent(BaseModel):
    first_name: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    last_name: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    phone_number: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    gender: str
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    national_id_number: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    password: str
    username: str
