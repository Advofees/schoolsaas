import datetime
from sqlalchemy import String, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from backend.database.base import Base
import typing

if typing.TYPE_CHECKING:
    from backend.user.user_models import (
        User,
        Role,
        UserRoleAssociation,
        UserPermissionAssociation,
    )
    from backend.student.student_model import Student
    from backend.student.parent.parent_model import ParentStudentAssociation
    from backend.inventory.inventory_model import Inventory
    from backend.teacher.teacher_model import Teacher
    from backend.payment.payment_model import Payment
    from backend.attendance.attendance_models import Attendance
    from backend.classroom.classroom_model import Classroom
    from backend.academic_term.academic_term_model import AcademicTerm


class SchoolParent(Base):
    __tablename__ = "school_parents"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    gender: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    street_and_building: Mapped[typing.Optional[str]] = mapped_column()
    zip_code: Mapped[typing.Optional[str]] = mapped_column()
    city: Mapped[typing.Optional[str]] = mapped_column()
    passport_number: Mapped[typing.Optional[str]] = mapped_column()
    national_id_number: Mapped[str] = mapped_column()
    notes: Mapped[typing.Optional[str]] = mapped_column()
    phone_number: Mapped[typing.Optional[str]] = mapped_column()

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    # ---
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="school_parent_user", uselist=False
    )

    # ---
    school_parent_associations: Mapped[list["SchoolParentAssociation"]] = relationship(
        "SchoolParentAssociation", back_populates="parent"
    )
    schools: Mapped[list["School"]] = relationship(
        "School", secondary="school_parent_associations", viewonly=True
    )
    parent_student_associations: Mapped[list["ParentStudentAssociation"]] = (
        relationship("ParentStudentAssociation", back_populates="parent")
    )
    students: Mapped[list["Student"]] = relationship(
        "Student", secondary="parent_student_associations", viewonly=True
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        email: str,
        national_id_number: str,
        user_id: uuid.UUID,
        phone_number: typing.Optional[str] = None,
        street_and_building: typing.Optional[str] = None,
        zip_code: typing.Optional[str] = None,
        city: typing.Optional[str] = None,
        passport_number: typing.Optional[str] = None,
        notes: typing.Optional[str] = None,
    ):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.phone_number = phone_number
        self.street_and_building = street_and_building
        self.zip_code = zip_code
        self.city = city
        self.passport_number = passport_number
        self.national_id_number = national_id_number
        self.notes = notes
        self.user_id = user_id


class SchoolParentAssociation(Base):
    __tablename__ = "school_parent_associations"

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )

    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("schools.id"), primary_key=True
    )

    school: Mapped["School"] = relationship(
        "School", back_populates="school_parent_associations"
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("school_parents.id"), primary_key=True
    )
    parent: Mapped["SchoolParent"] = relationship(
        "SchoolParent", back_populates="school_parent_associations"
    )

    def __init__(self, school_id: uuid.UUID, parent_id: uuid.UUID):
        super().__init__()
        self.school_id = school_id
        self.parent_id = parent_id


class SchoolStudentAssociation(Base):
    __tablename__ = "school_student_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("schools.id"), primary_key=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("students.id"), primary_key=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    school: Mapped["School"] = relationship(
        "School", back_populates="school_students_associations"
    )
    student: Mapped["Student"] = relationship(
        "Student", back_populates="school_students_associations"
    )

    def __init__(self, school_id: uuid.UUID, student_id: uuid.UUID):
        super().__init__()
        self.school_id = school_id
        self.student_id = student_id


class School(Base):

    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[typing.Optional[str]] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    school_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", back_populates="school_user", uselist=False
    )

    school_students_associations: Mapped[list["SchoolStudentAssociation"]] = (
        relationship("SchoolStudentAssociation", back_populates="school")
    )

    students: Mapped[list["Student"]] = relationship(
        "Student", secondary="school_student_associations", viewonly=True
    )

    school_parent_associations: Mapped[list["SchoolParentAssociation"]] = relationship(
        "SchoolParentAssociation", back_populates="school"
    )
    school_parents: Mapped[list["SchoolParent"]] = relationship(
        "SchoolParent", secondary="school_parent_associations", viewonly=True
    )

    inventories: Mapped[list["Inventory"]] = relationship(
        "Inventory", back_populates="school"
    )
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="school")

    teachers: Mapped[list["Teacher"]] = relationship("Teacher", back_populates="school")
    classrooms: Mapped[list["Classroom"]] = relationship(
        "Classroom", back_populates="school"
    )
    academic_terms: Mapped[list["AcademicTerm"]] = relationship(
        "AcademicTerm", back_populates="school"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="school"
    )

    roles: Mapped[list["Role"]] = relationship("Role", back_populates="school")
    user_role_associations: Mapped[list["UserRoleAssociation"]] = relationship(
        "UserRoleAssociation", back_populates="school"
    )
    user_permission_associations: Mapped[list["UserPermissionAssociation"]] = (
        relationship("UserPermissionAssociation", back_populates="school")
    )

    def __init__(
        self,
        name: str,
        school_number: str,
        country: str,
        user_id: uuid.UUID,
        address: typing.Optional[str] = None,
    ):
        super().__init__()
        self.name = name
        self.school_number = school_number
        self.country = country
        self.address = address
        self.user_id = user_id
