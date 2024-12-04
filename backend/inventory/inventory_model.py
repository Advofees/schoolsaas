import datetime
from sqlalchemy import DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid

from backend.database.base import Base
from backend.school.school_model import School


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    item_name: Mapped[str] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school: Mapped["School"] = relationship("School", back_populates="inventories")

    def __init__(self, item_name: str, quantity: int, school_id: uuid.UUID):
        super().__init__()
        self.item_name = item_name
        self.quantity = quantity
        self.school_id = school_id
