from sqlalchemy import String, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
import datetime
from backend.database.base import Base
import typing

if typing.TYPE_CHECKING:
    from backend.models import School
    from backend.models import SchoolParent
    from backend.models import Student
    from backend.models import Teacher




class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column()
    file_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    # ---
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="files")

    # ---
    parent_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("school_parents.id")
    )
    parent: Mapped[typing.Optional["SchoolParent"]] = relationship(
        "SchoolParent", back_populates="files"
    )

    # ---
    student_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("students.id")
    )
    student: Mapped[typing.Optional["Student"]] = relationship(
        "Student", back_populates="files"
    )
    teacher_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("teachers.id")
    )
    teacher: Mapped[typing.Optional["Teacher"]] = relationship(
        Teacher, back_populates="files"
    )

    def __init__(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        file_path: str,
        school_id: uuid.UUID,
        parent_id: typing.Optional[uuid.UUID] = None,
        student_id: typing.Optional[uuid.UUID] = None,
    ):
        super().__init__()
        self.filename = filename
        self.file_type = file_type
        self.file_size = file_size
        self.file_path = file_path
        self.school_id = school_id
        self.parent_id = parent_id
        self.student_id = student_id
