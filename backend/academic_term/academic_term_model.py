import datetime
from sqlalchemy import String, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base

from backend.school.school_model import School
from backend.exam.exam_model import Exam
from backend.attendance.attendance_models import Attendance


class AcademicTerm(Base):
    __tablename__ = "academic_terms"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    start_date: Mapped[datetime.datetime] = mapped_column()
    end_date: Mapped[datetime.datetime] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="academic_terms")

    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="academic_term")
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="academic_term"
    )

    def __init__(
        self,
        name: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        school_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.school_id = school_id
