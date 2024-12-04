import datetime
from sqlalchemy import String, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import enum


from backend.teacher.teacher_model import Teacher
from backend.classroom.classroom_model import Classroom
from backend.academic_term.academic_term_model import AcademicTerm
from backend.module.module_model import Module
from backend.school.school_model import School


class DayOfWeek(enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    start_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    day_of_week: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    timetable_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("timetables.id"))
    timetable: Mapped["Timetable"] = relationship(
        "Timetable", back_populates="time_slots"
    )

    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship("Module")

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("teachers.id"))
    teacher: Mapped["Teacher"] = relationship("Teacher")

    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    classroom: Mapped["Classroom"] = relationship("Classroom")

    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        day_of_week: DayOfWeek,
        timetable_id: uuid.UUID,
        module_id: uuid.UUID,
        teacher_id: uuid.UUID,
        classroom_id: uuid.UUID,
    ):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.day_of_week = day_of_week.value
        self.timetable_id = timetable_id
        self.module_id = module_id
        self.teacher_id = teacher_id
        self.classroom_id = classroom_id


class Timetable(Base):
    __tablename__ = "timetables"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    academic_year: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    academic_term_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("academic_terms.id")
    )
    grade_level: Mapped[int] = mapped_column()

    school: Mapped["School"] = relationship("School")
    academic_term: Mapped["AcademicTerm"] = relationship("AcademicTerm")
    time_slots: Mapped[list["TimeSlot"]] = relationship(
        "TimeSlot", back_populates="timetable", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        name: str,
        academic_year: str,
        school_id: uuid.UUID,
        academic_term_id: uuid.UUID,
        grade_level: int,
    ):
        super().__init__()
        self.name = name
        self.academic_year = academic_year
        self.school_id = school_id
        self.academic_term_id = academic_term_id
        self.grade_level = grade_level
