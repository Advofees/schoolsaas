import datetime
from sqlalchemy import ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing
import enum
from backend.school.school_model import School
from backend.teacher.teacher_model import Teacher


class PaymentMethod(enum.Enum):
    MPESA = "mpesa"
    BANK = "bank"
    CASH = "cash"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[datetime.datetime] = mapped_column()
    method: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(onupdate=func.now())

    # --
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship(School, back_populates="payments")

    teacher_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("teachers.id")
    )
    teacher: Mapped[typing.Optional["Teacher"]] = relationship(
        Teacher, back_populates="payments"
    )

    def __init__(
        self,
        amount: float,
        date: datetime.datetime,
        method: PaymentMethod,
        school_id: uuid.UUID,
    ):
        super().__init__()
        self.amount = amount
        self.date = date
        self.method = method.value
        self.school_id = school_id
