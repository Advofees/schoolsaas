import datetime
from sqlalchemy import ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
import enum
import decimal
import typing
from backend.database.base import Base
from backend.school.school_model import School

if typing.TYPE_CHECKING:
    from backend.user.user_models import User


class PaymentUserType(enum.Enum):
    RELATED = "related"
    RECORDER = "recorder"


class PaymentMethod(enum.Enum):
    MPESA = "mpesa"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    MOBILE_PAYMENT = "mobile_payment"
    CRYPTOCURRENCY = "cryptocurrency"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    PROCESSING = "processing"


class PaymentCategory(enum.Enum):
    TUITION = "tuition"
    EXAM_FEE = "exam_fee"
    TRANSPORT = "transport"
    BOARDING = "boarding"
    UNIFORM = "uniform"
    BOOKS = "books"
    ACTIVITY = "activity"
    OTHER = "other"


class PaymentDirection(enum.Enum):
    INBOUND = "inbound"  # School receives money
    OUTBOUND = "outbound"  # School pays money


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[decimal.Decimal] = mapped_column(nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(nullable=False)
    reference_number: Mapped[str] = mapped_column(unique=True)
    direction: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    updated_at: Mapped[datetime.datetime] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship(School, back_populates="payments")

    users: Mapped[list["PaymentUserAssociation"]] = relationship(
        "PaymentUserAssociation",
        back_populates="payment",
    )

    @property
    def payee(self):
        association = next(
            (
                assoc
                for assoc in self.users
                if assoc.type == PaymentUserType.RELATED.value
            ),
            None,
        )
        return association.user if association else None

    @property
    def recorded_by(self):
        association = next(
            (
                assoc
                for assoc in self.users
                if assoc.type == PaymentUserType.RECORDER.value
            ),
            None,
        )
        return association.user if association else None

    def __init__(
        self,
        amount: decimal.Decimal,
        date: datetime.datetime,
        method: PaymentMethod,
        category: PaymentCategory,
        status: PaymentStatus,
        direction: PaymentDirection,
        school_id: uuid.UUID,
        recorded_by_id: uuid.UUID,
        reference_number: str,
        description: str,
        payee: uuid.UUID,
    ):
        super().__init__()
        self.amount = amount
        self.date = date
        self.method = method.value
        self.category = category.value
        self.status = status.value
        self.direction = direction.value
        self.school_id = school_id
        self.recorded_by_id = recorded_by_id
        self.reference_number = reference_number
        self.description = description
        self.payment_is_for_or_from_user_id = payee


class PaymentUserAssociation(Base):
    __tablename__ = "payment_user_associations"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("payments.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), primary_key=True
    )
    type: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    # Define both sides of the relationship
    payment: Mapped["Payment"] = relationship("Payment", back_populates="users")
    user: Mapped["User"] = relationship("User", back_populates="payment_associations")

    def __init__(
        self, payment_id: uuid.UUID, user_id: uuid.UUID, type: PaymentUserType
    ):
        super().__init__()
        self.payment_id = payment_id
        self.user_id = user_id
        self.type = type.value
