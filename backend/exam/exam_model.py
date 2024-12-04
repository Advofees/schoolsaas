import datetime
import typing
from sqlalchemy import String, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base

if typing.TYPE_CHECKING:

    from backend.module.module_model import Module
    from backend.academic_term.academic_term_model import AcademicTerm
    from backend.exam.exam_results.exam_result_model import ExamResult


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    date: Mapped[datetime.datetime] = mapped_column()
    total_marks: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship("Module", back_populates="exams")

    academic_term_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("academic_terms.id")
    )
    academic_term: Mapped["AcademicTerm"] = relationship(
        "AcademicTerm", back_populates="exams"
    )

    exam_results: Mapped[list["ExamResult"]] = relationship(
        "ExamResult", back_populates="exam"
    )

    def __init__(
        self,
        name: str,
        date: datetime.datetime,
        total_marks: float,
        module_id: uuid.UUID,
        academic_term_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.date = date
        self.total_marks = total_marks
        self.module_id = module_id
        self.academic_term_id = academic_term_id
