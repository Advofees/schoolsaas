from sqlalchemy import ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
import datetime
from backend.database.base import Base

import typing

if typing.TYPE_CHECKING:
    from backend.user.user_models import User


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column()
    path: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="files")

    def __init__(
        self,
        name: str,
        file_type: str,
        size: int,
        path: str,
        user_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.type = file_type
        self.size = size
        self.path = path
        self.user_id = user_id


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("files.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    file: Mapped["File"] = relationship("File")
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __init__(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        super().__init__()
        self.file_id = file_id
        self.user_id = user_id
