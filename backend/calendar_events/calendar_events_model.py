import datetime

from sqlalchemy import String, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing

from backend.school.school_model import School
from backend.module.module_model import Module
from backend.classroom.classroom_model import Classroom

if typing.TYPE_CHECKING:
    from backend.user.user_models import User


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[typing.Optional[str]] = mapped_column(String)
    start_datetime: Mapped[datetime.datetime] = mapped_column(nullable=False)
    end_datetime: Mapped[datetime.datetime] = mapped_column(nullable=False)
    is_recurring: Mapped[bool] = mapped_column(default=False)
    recurrence_rule: Mapped[typing.Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[typing.Optional[datetime.datetime]] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    module_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        ForeignKey("modules.id"), nullable=True
    )
    classroom_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        ForeignKey("classrooms.id"), nullable=True
    )

    school: Mapped["School"] = relationship("School")
    creator: Mapped["User"] = relationship("User")
    module: Mapped[typing.Optional["Module"]] = relationship("Module")
    classroom: Mapped[typing.Optional["Classroom"]] = relationship("Classroom")

    def __init__(
        self,
        title: str,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        school_id: uuid.UUID,
        creator_id: uuid.UUID,
        description: typing.Optional[str] = None,
        is_recurring: bool = False,
        recurrence_rule: typing.Optional[str] = None,
        module_id: typing.Optional[uuid.UUID] = None,
        classroom_id: typing.Optional[uuid.UUID] = None,
    ):
        super().__init__()
        self.title = title
        self.description = description
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.is_recurring = is_recurring
        self.recurrence_rule = recurrence_rule
        self.school_id = school_id
        self.creator_id = creator_id
        self.module_id = module_id
        self.classroom_id = classroom_id
