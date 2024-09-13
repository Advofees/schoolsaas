from sqlalchemy import String, Numeric, ForeignKey, UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing
if typing.TYPE_CHECKING:
    from backend.models import School


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g., 'A', 'B', 'C', 'D', 'F'
    min_score: Mapped[float] = mapped_column(Numeric, nullable=False)
    max_score: Mapped[float] = mapped_column(Numeric, nullable=False)
    gpa_point: Mapped[float] = mapped_column(
        Numeric, nullable=False
    )  # e.g., 4.0, 3.0, 2.0, 1.0, 0.0
    description: Mapped[typing.Optional[str]] = mapped_column(String)

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="grades")

    def __init__(
        self,
        name: str,
        min_score: float,
        max_score: float,
        gpa_point: float,
        school_id: uuid.UUID,
        description: typing.Optional[str] = None,
    ):

        super().__init__()
        self.name = name
        self.min_score = min_score
        self.max_score = max_score
        self.gpa_point = gpa_point
        self.school_id = school_id
        self.description = description
