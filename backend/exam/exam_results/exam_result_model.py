import datetime
from sqlalchemy import ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing
import decimal

if typing.TYPE_CHECKING:
    from backend.exam.exam_model import Exam
    from backend.student.student_model import Student
    from backend.module.module_model import Module


class ExamResult(Base):
    __tablename__ = "exam_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    marks_obtained: Mapped[decimal.Decimal] = mapped_column(nullable=False)
    comments: Mapped[typing.Optional[str]] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("exams.id"))
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_results")

    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"))
    student: Mapped["Student"] = relationship("Student", back_populates="exam_results")

    class_room_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship("Module")

    @property
    def percentage(self):
        return (self.marks_obtained / 100) * 100

    @property
    def grade_obtained(self):
        if self.percentage >= 90:
            return "A+"
        elif self.percentage >= 80:
            return "A"
        elif self.percentage >= 70:
            return "B"
        elif self.percentage >= 60:
            return "C"
        elif self.percentage >= 50:
            return "D"
        else:
            return "F"

    @property
    def get_module_name(self):
        return self.module.name

    def __init__(
        self,
        marks_obtained: decimal.Decimal,
        exam_id: uuid.UUID,
        student_id: uuid.UUID,
        class_room_id: uuid.UUID,
        module_id: uuid.UUID,
    ):
        super().__init__()
        self.marks_obtained = marks_obtained
        self.exam_id = exam_id
        self.student_id = student_id
        self.class_room_id = class_room_id
        self.module_id = module_id
