import datetime
from sqlalchemy import String, DateTime, Boolean, Numeric, ForeignKey, UUID, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, Optional
import uuid
from dateutil.relativedelta import relativedelta

from backend.database.base import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String)
    country: Mapped[Optional[str]] = mapped_column(String)
    school_number: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)

    # Relationships
    school_parent_associations: Mapped[List["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="school")
    school_parents: Mapped[List["SchoolParent"]] = relationship("SchoolParent", secondary="school_parent_associations", viewonly=True)
    school_students_associations: Mapped[List["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="school")
    students: Mapped[List["Student"]] = relationship("Student", secondary="school_student_associations", viewonly=True)
    inventories: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="school")
    files: Mapped[List["File"]] = relationship("File", back_populates="school")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="school")
    newsletters: Mapped[List["Newsletter"]] = relationship("Newsletter", back_populates="school")
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="school")
    school_staffs: Mapped[List["SchoolStaff"]] = relationship("SchoolStaff", back_populates="school")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))

    # Relationships
    parent: Mapped[Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="students")
    school_students_associations: Mapped[List["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="student")
    schools: Mapped[List["School"]] = relationship("School", secondary="school_student_associations", viewonly=True)
    files: Mapped[List["File"]] = relationship("File", back_populates="student")

class SchoolStudentAssociation(Base):
    __tablename__ = "school_student_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"), primary_key=True)

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="school_students_associations")
    student: Mapped["Student"] = relationship("Student", back_populates="school_students_associations")

class SchoolStaff(Base):
    __tablename__ = "school_staffs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    permissions_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_staff_permissions.id"), unique=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="school_staff", uselist=False)
    school: Mapped["School"] = relationship("School", back_populates="school_staffs")
    school_staff_permission: Mapped["SchoolStaffPermissions"] = relationship("SchoolStaffPermissions", back_populates="school_staff", uselist=False)

class SchoolStaffPermissions(Base):
    __tablename__ = "school_staff_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    can_add_students: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_add_parents: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_manage_classes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_view_reports: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    school_staff: Mapped["SchoolStaff"] = relationship("SchoolStaff", back_populates="school_staff_permission", uselist=False)

class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="inventories")
    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="inventory")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("inventories.id"))

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="items")

class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String)
    school_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("schools.id"))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("users.id"))
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("students.id"))

    # Relationships
    school: Mapped[Optional["School"]] = relationship("School", back_populates="files")
    parent: Mapped[Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="files")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="files")
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="files")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[Numeric] = mapped_column(Numeric)
    payment_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="payments")

class Newsletter(Base):
    __tablename__ = "newsletters"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="newsletters")

class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="emails")

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    school_staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_staffs.id"))

    # Relationships
    school_staff: Mapped["SchoolStaff"] = relationship("SchoolStaff", back_populates="user", uselist=False)
    files: Mapped[List["File"]] = relationship("File", back_populates="user")
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"),nullable=False)
    expire_at: Mapped[datetime.datetime] = mapped_column(DateTime,nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    def __init__(self, user_id: uuid.UUID):
        super().__init__()

        self.user_id = user_id
        self.expire_at = datetime.datetime.utcnow() + relativedelta(months=6)

class SchoolParent(Base):
    __tablename__ = "school_parents"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    street_and_building: Mapped[Optional[str]] = mapped_column(String)
    zip_code: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)
    passport_number: Mapped[Optional[str]] = mapped_column(String)
    national_id_number: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)
    phone_number: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    school_parent_associations: Mapped[List["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="parent")
    schools: Mapped[List["School"]] = relationship("School", secondary="school_parent_associations", viewonly=True)
    students: Mapped[List["Student"]] = relationship("Student", back_populates="parent")
    files: Mapped[List["File"]] = relationship("File", back_populates="parent")

class SchoolParentAssociation(Base):
    __tablename__ = "school_parent_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_parents.id"), primary_key=True)

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="school_parent_associations")
    parent: Mapped["SchoolParent"] = relationship("SchoolParent", back_populates="school_parent_associations")