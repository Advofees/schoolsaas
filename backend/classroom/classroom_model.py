import datetime
from sqlalchemy import String, DateTime, ForeignKey, UUID, func, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing

if typing.TYPE_CHECKING:

    from backend.school.school_model import School
    from backend.student.student_model import Student
    from backend.attendance.attendance_models import Attendance
    from backend.teacher.teacher_model import Teacher, ClassTeacherAssociation


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    grade_level: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="classrooms")

    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="classroom"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="classroom"
    )

    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher", secondary="class_teacher_associations", back_populates="classrooms"
    )

    teacher_associations: Mapped[list["ClassTeacherAssociation"]] = relationship(
        "ClassTeacherAssociation", back_populates="classroom"
    )

    @property
    def primary_teacher(self) -> typing.Optional["Teacher"]:
        for assoc in self.teacher_associations:
            if assoc.is_primary:
                return assoc.teacher
        return None

    def __init__(
        self,
        name: str,
        grade_level: int,
        school_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.grade_level = grade_level
        self.school_id = school_id
