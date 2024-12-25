import datetime
from sqlalchemy import String, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Index


from backend.parent.parent_model import ParentStudentAssociation
from backend.attendance.attendance_models import Attendance
from backend.classroom.classroom_model import Classroom
from backend.school.school_model import School, SchoolParent, SchoolStudentAssociation
from backend.exam.exam_results.exam_result_model import ExamResult
import enum

if typing.TYPE_CHECKING:
    from backend.user.user_models import User
    from backend.module.module_model import Module, ModuleEnrollment


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    date_of_birth: Mapped[datetime.datetime] = mapped_column()
    gender: Mapped[str] = mapped_column(String)
    grade_level: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    # National Education Management Information System
    # --- nemis number is issued by the govt of kenya from the time the child starts the kenyan education system
    #
    nemis_number: Mapped[typing.Optional[str]] = mapped_column(nullable=True)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="students"
    )

    school_students_associations: Mapped[list["SchoolStudentAssociation"]] = (
        relationship("SchoolStudentAssociation", back_populates="student")
    )

    schools: Mapped[list["School"]] = relationship(
        "School", secondary="school_student_associations", viewonly=True
    )

    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="student"
    )
    exam_results: Mapped[list["ExamResult"]] = relationship(
        "ExamResult", back_populates="student"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="student_user", uselist=False
    )

    parent_student_associations: Mapped[list["ParentStudentAssociation"]] = (
        relationship("ParentStudentAssociation", back_populates="student")
    )
    parents: Mapped[list["SchoolParent"]] = relationship(
        "SchoolParent", secondary="parent_student_associations", viewonly=True
    )

    module_enrollments: Mapped[list["ModuleEnrollment"]] = relationship(
        "ModuleEnrollment", back_populates="student", cascade="all, delete-orphan"
    )
    modules: Mapped[list["Module"]] = relationship(
        "Module",
        secondary="module_enrollments",
        back_populates="students",
        viewonly=True,
    )

    search_vector: Mapped[typing.Optional[str]] = mapped_column(TSVECTOR, nullable=True)
    __table_args__ = (
        Index("ix_students_search_vector", "search_vector", postgresql_using="gin"),
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: datetime.datetime,
        gender: str,
        grade_level: int,
        classroom_id: uuid.UUID,
        user_id: uuid.UUID,
        nemis_number: typing.Optional[str] = None,
    ):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.grade_level = grade_level
        self.classroom_id = classroom_id
        self.user_id = user_id
        self.nemis_number = nemis_number
