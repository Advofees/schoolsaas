from sqlalchemy import ForeignKey, String, UUID ,  DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import Optional, List
from backend.database.base import Base

# Student-School Association Model
class StudentSchoolAssociation(Base):
    __tablename__ = "student_schools"

    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"), primary_key=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    
    # Additional columns
    enrollment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    scholarship_amount: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    extra_notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="student_schools")
    school: Mapped["School"] = relationship("School", back_populates="student_schools")

    def __repr__(self):
        return (f"<StudentSchoolAssociation(student_id={self.student_id}, "
                f"school_id={self.school_id}, enrollment_date={self.enrollment_date}, "
                f"status={self.status}, scholarship_amount={self.scholarship_amount}, "
                f"extra_notes={self.extra_notes})>")


# Student Model
class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_parents.id"))

    # Relationships
    parent: Mapped["SchoolParent"] = relationship("SchoolParent", back_populates="students")
    student_schools: Mapped[List["StudentSchoolAssociation"]] = relationship("StudentSchoolAssociation", back_populates="student")
    files: Mapped[List["File"]] = relationship("File", back_populates="student")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name})>"


# School Model
class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String)
    country: Mapped[Optional[str]] = mapped_column(String)
    school_number: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)

    # Relationships
    student_schools: Mapped[List["StudentSchoolAssociation"]] = relationship("StudentSchoolAssociation", back_populates="school")
    school_staffs: Mapped[List["SchoolStaff"]] = relationship("SchoolStaff", back_populates="school")
    school_parents: Mapped[List["SchoolParent"]] = relationship("SchoolParent", back_populates="school")
    inventories: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="school")
    files: Mapped[List["File"]] = relationship("File", back_populates="school")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="school")
    newsletters: Mapped[List["Newsletter"]] = relationship("Newsletter", back_populates="school")
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="school")

    def __repr__(self):
        return f"<School(id={self.id}, name={self.name})>"

# SchoolStaff Model
class SchoolStaff(Base):
    __tablename__ = "school_staffs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="school_staff")
    school: Mapped["School"] = relationship("School", back_populates="school_staffs")

    def __repr__(self):
        return f"<SchoolStaff(id={self.id}, name={self.name})>"

# SchoolParent Model
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
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="school_parents")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="parent")
    files: Mapped[List["File"]] = relationship("File", back_populates="parent")

    def __repr__(self):
        return f"<SchoolParent(id={self.id}, name={self.name})>"

# Inventory Model
class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="inventories")
    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(id={self.id}, name={self.name})>"

# InventoryItem Model
class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("inventories.id"))

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="items")

    def __repr__(self):
        return f"<InventoryItem(id={self.id}, name={self.name})>"

# File Model

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

    def __repr__(self):
        return f"<File(id={self.id}, file_path={self.file_path})>"


# Payment Model
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[Numeric] = mapped_column(Numeric)
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount})>"

# Newsletter Model
class Newsletter(Base):
    __tablename__ = "newsletters"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="newsletters")

    def __repr__(self):
        return f"<Newsletter(id={self.id}, title={self.title})>"

# Email Model
class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject})>"

# User Model
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True)

    # Relationships
    school_staff: Mapped[Optional["SchoolStaff"]] = relationship("SchoolStaff", back_populates="user", uselist=False)
    files: Mapped[List["File"]] = relationship("File", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
