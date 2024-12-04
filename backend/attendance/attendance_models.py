import datetime
from sqlalchemy import String, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing
import enum


if typing.TYPE_CHECKING:
    from backend.school.school_model import School
    from backend.student.student_model import Student
    from backend.classroom.classroom_model import Classroom
    from backend.academic_term.academic_term_model import AcademicTerm


class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime.datetime] = mapped_column()
    status: Mapped[str] = mapped_column(String)  # Present, Absent, Late, etc.
    remarks: Mapped[typing.Optional[str]] = mapped_column(String)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"))
    student: Mapped["Student"] = relationship("Student", back_populates="attendances")

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="attendances")

    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="attendances"
    )

    academic_term_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("academic_terms.id")
    )
    academic_term: Mapped["AcademicTerm"] = relationship(
        "AcademicTerm", back_populates="attendances"
    )

    def __init__(
        self,
        date: datetime.datetime,
        status: str,
        student_id: uuid.UUID,
        school_id: uuid.UUID,
        classroom_id: uuid.UUID,
        academic_term_id: uuid.UUID,
        remarks: typing.Optional[str] = None,
    ):
        super().__init__()
        self.date = date
        self.status = status
        self.student_id = student_id
        self.school_id = school_id
        self.classroom_id = classroom_id
        self.academic_term_id = academic_term_id
        self.remarks = remarks
