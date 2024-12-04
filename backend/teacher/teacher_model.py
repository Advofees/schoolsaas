import datetime
from sqlalchemy import String, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing


if typing.TYPE_CHECKING:
    from backend.user.user_models import User
    from backend.school.school_model import School
    from backend.module.module_model import Module
    from backend.payment.payment_model import Payment


class TeacherModuleAssociation(Base):

    __tablename__ = "teacher_module_association"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("teachers.id"), primary_key=True
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("modules.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __init__(self, teacher_id: uuid.UUID, module_id: uuid.UUID):
        super().__init__()
        self.teacher_id = teacher_id
        self.module_id = module_id


class Teacher(Base):

    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # ---
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="teachers")

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="teacher_user", uselist=False
    )

    # ---

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="teacher"
    )

    modules: Mapped[list["Module"]] = relationship(
        "Module", secondary="teacher_module_association", back_populates="teachers"
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        school_id: uuid.UUID,
        user_id: uuid.UUID,
        phone_number: typing.Optional[str] = None,
    ):
        super().__init__()

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user_id = user_id
        self.school_id = school_id
        self.phone_number = phone_number
