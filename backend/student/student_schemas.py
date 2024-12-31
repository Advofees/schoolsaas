import uuid
import datetime
import typing
import enum
from pydantic import BaseModel, StringConstraints, EmailStr
from backend.student.parent.parent_model import ParentRelationshipType
from backend.student.student_model import Student
from backend.student.parent.parent_controller import createParent


class createStudent(BaseModel):
    first_name: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    last_name: typing.Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    password: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    email: typing.Annotated[
        EmailStr, StringConstraints(strip_whitespace=True, to_lower=True)
    ]
    username: typing.Annotated[str, StringConstraints(strip_whitespace=True)]
    classroom_id: uuid.UUID
    parent_id: uuid.UUID
    nemis_number: typing.Optional[str]
    parent_relationship_type: ParentRelationshipType


class StudentResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    nemis_number: typing.Optional[str]
    email: str
    classroom_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class StudentSortableFields(enum.Enum):
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    GRADE_LEVEL = "grade_level"
    EMAIL = "email"
    DATE_OF_BIRTH = "date_of_birth"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class OrderBy(enum.Enum):
    ASC = "asc"
    DESC = "desc"


def to_student_dto(student: Student) -> StudentResponse:
    return StudentResponse(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.user.email,
        grade_level=student.grade_level,
        date_of_birth=student.date_of_birth,
        nemis_number=student.nemis_number,
        gender=student.gender,
        classroom_id=student.classroom_id,
        user_id=student.user_id,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


class createstudentHealthInfo(BaseModel):
    pass


class createStudentDocumentUploads(BaseModel):
    pass


class createStudentFullInfo(BaseModel):
    student_info: createStudent
    student_parent_info: createParent
    student_health_info: createstudentHealthInfo
    student_documents_upload: createStudentDocumentUploads
