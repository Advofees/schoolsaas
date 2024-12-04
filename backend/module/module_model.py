from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing

if typing.TYPE_CHECKING:

    from backend.student.student_model import Student
    from backend.teacher.teacher_model import Teacher
    from exam.exam_model import Exam


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[typing.Optional[str]] = mapped_column(String)

    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher", secondary="teacher_module_association", back_populates="modules"
    )
    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="module")

    module_enrollments: Mapped[list["ModuleEnrollment"]] = relationship(
        "ModuleEnrollment", back_populates="module"
    )

    students: Mapped[list["Student"]] = relationship(
        "Student",
        secondary="module_enrollments",
        back_populates="modules",
        viewonly=True,
    )

    def __init__(self, name: str, description: typing.Optional[str] = None):
        super().__init__()
        self.name = name
        self.description = description


class ModuleEnrollment(Base):
    __tablename__ = "module_enrollments"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), primary_key=True
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id"), primary_key=True
    )

    student: Mapped["Student"] = relationship(
        "Student", back_populates="module_enrollments"
    )
    module: Mapped["Module"] = relationship(
        "Module", back_populates="module_enrollments"
    )

    def __init__(self, student_id: uuid.UUID, module_id: uuid.UUID):
        super().__init__()
        self.student_id = student_id
        self.module_id = module_id
