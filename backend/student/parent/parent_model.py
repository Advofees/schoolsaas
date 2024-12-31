from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing

if typing.TYPE_CHECKING:
    from backend.school.school_model import SchoolParent
    from backend.student.student_model import Student

import enum


class ParentRelationshipType(enum.Enum):
    FATHER = "father"
    MOTHER = "mother"
    GUARDIAN = "guardian"
    OTHER = "other"


class ParentStudentAssociation(Base):
    __tablename__ = "parent_student_associations"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("school_parents.id"), primary_key=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("students.id"), primary_key=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    parent: Mapped["SchoolParent"] = relationship(
        "SchoolParent", back_populates="parent_student_associations"
    )
    student: Mapped["Student"] = relationship(
        "Student", back_populates="parent_student_associations"
    )
    relationship_type: Mapped[str] = mapped_column()

    def __init__(
        self,
        parent_id: uuid.UUID,
        student_id: uuid.UUID,
        relationship_type: str,
        is_active: bool = True,
    ):
        super().__init__()
        self.parent_id = parent_id
        self.student_id = student_id
        self.relationship_type = relationship_type
        self.is_active = is_active
