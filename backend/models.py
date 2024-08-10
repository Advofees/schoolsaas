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
    name: Mapped[str] = mapped_column(String,nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    school_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school_parent_associations: Mapped[List["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="school")
    school_students_associations: Mapped[List["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="school")
    
    school_parents: Mapped[List["SchoolParent"]] = relationship("SchoolParent", secondary="school_parent_associations", viewonly=True)
   
    students: Mapped[List["Student"]] = relationship("Student", secondary="school_student_associations", viewonly=True)
    inventories: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="school")
    files: Mapped[List["File"]] = relationship("File", back_populates="school")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="school")
    newsletters: Mapped[List["Newsletter"]] = relationship("Newsletter", back_populates="school")
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="school")
    school_staffs: Mapped[List["SchoolStaff"]] = relationship("SchoolStaff", back_populates="school")

    def __init__(self, 
                 name: str, 
                 school_number: str,
                 country: str, 
                 address: Optional[str], 
                 ):
        super().__init__()
        self.name = name
        self.school_number = school_number
        self.country = country
        self.address = address
      


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    parent: Mapped[Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="students")
    school_students_associations: Mapped[List["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="student")
    schools: Mapped[List["School"]] = relationship("School", secondary="school_student_associations", viewonly=True)
    files: Mapped[List["File"]] = relationship("File", back_populates="student")

    def __init__(self, name: str, parent_id: Optional[uuid.UUID] = None):
        super().__init__()
        self.name = name
        self.parent_id = parent_id

class SchoolStudentAssociation(Base):
    __tablename__ = "school_student_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="school_students_associations")
    student: Mapped["Student"] = relationship("Student", back_populates="school_students_associations")
    def __init__(self, school_id: uuid.UUID, student_id: uuid.UUID):
        super().__init__()
        self.school_id = school_id
        self.student_id = student_id

class SchoolStaff(Base):
    __tablename__ = "school_staffs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    permissions_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_staff_permissions.id"), unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    staff_user: Mapped["StaffUser"] = relationship("StaffUser", back_populates="school_staff", uselist=False)
    school: Mapped["School"] = relationship("School", back_populates="school_staffs")
    school_staff_permission: Mapped["SchoolStaffPermissions"] = relationship("SchoolStaffPermissions", back_populates="school_staff", uselist=False)
    
    def __init__(self, 
                 name: Optional[str], 
                 school_id: uuid.UUID, 
                 permissions_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.school_id = school_id
        self.permissions_id = permissions_id
class SchoolStaffPermissions(Base):
    __tablename__ = "school_staff_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    can_add_students: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_add_parents: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_manage_classes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_view_reports: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school_staff: Mapped["SchoolStaff"] = relationship("SchoolStaff", back_populates="school_staff_permission", uselist=False)
    def __init__(self, 
                 can_add_students: bool, 
                 can_add_parents: bool, 
                 can_manage_classes: bool, 
                 can_view_reports: bool):
        super().__init__()
        self.can_add_students = can_add_students
        self.can_add_parents = can_add_parents
        self.can_manage_classes = can_manage_classes
        self.can_view_reports = can_view_reports
class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="inventories")
    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="inventory")
    def __init__(self, 
                 name: str, 
                 school_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.school_id = school_id

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("inventories.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="items")
    def __init__(self, 
                 name: str, 
                 inventory_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.inventory_id = inventory_id

class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String)
    school_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("schools.id"))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))
    staff_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("staff_users.id"))
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("students.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school: Mapped[Optional["School"]] = relationship("School", back_populates="files")
    parent: Mapped[Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="files")
    staff_user: Mapped[Optional["StaffUser"]] = relationship("StaffUser", back_populates="files")
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="files")
    def __init__(self, 
                 file_path: str, 
                 school_id: Optional[uuid.UUID] = None, 
                 parent_id: Optional[uuid.UUID] = None, 
                 staff_user_id: Optional[uuid.UUID] = None, 
                 student_id: Optional[uuid.UUID] = None):
        super().__init__()
        self.file_path = file_path
        self.school_id = school_id
        self.parent_id = parent_id
        self.staff_user_id = staff_user_id
        self.student_id = student_id

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[Numeric] = mapped_column(Numeric)
    payment_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="payments")
    def __init__(self, 
                 amount: Numeric, 
                 school_id: uuid.UUID, 
                 payment_date: Optional[DateTime] = None):
        super().__init__()
        self.amount = amount
        self.school_id = school_id
        self.payment_date = payment_date

class Newsletter(Base):
    __tablename__ = "newsletters"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="newsletters")
    def __init__(self, 
                 title: str, 
                 content: str, 
                 school_id: uuid.UUID, 
                 sent_date: Optional[DateTime] = None):
        super().__init__()
        self.title = title
        self.content = content
        self.school_id = school_id
        self.sent_date = sent_date

class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    sent_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="emails")
    def __init__(self, 
                 subject: str, 
                 body: str, 
                 school_id: uuid.UUID, 
                 sent_date: Optional[DateTime] = None):
        super().__init__()
        self.subject = subject
        self.body = body
        self.school_id = school_id
        self.sent_date = sent_date
class StaffUser(Base):
    __tablename__ = "staff_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String)
    school_staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_staffs.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school_staff: Mapped["SchoolStaff"] = relationship("SchoolStaff", back_populates="staff_user", uselist=False)
    files: Mapped[List["File"]] = relationship("File", back_populates="staff_user")
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="staff_user")

    def __init__(self, 
                 username: str, 
                 email: str, 
                 password_hash: str, 
                 school_staff_id: Optional[uuid.UUID] = None):
        super().__init__()
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.school_staff_id = school_staff_id
class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    staff_user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("staff_users.id"),nullable=False)
    expire_at: Mapped[datetime.datetime] = mapped_column(DateTime,nullable=False)
    
    # Relationships
    staff_user: Mapped["StaffUser"] = relationship("StaffUser", back_populates="sessions")
    def __init__(self, staff_user_id: uuid.UUID):
        super().__init__()

        self.staff_user_id = staff_user_id
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
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
    school_parent_associations: Mapped[List["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="parent")
    schools: Mapped[List["School"]] = relationship("School", secondary="school_parent_associations", viewonly=True)
    students: Mapped[List["Student"]] = relationship("Student", back_populates="parent")
    files: Mapped[List["File"]] = relationship("File", back_populates="parent")

    def __init__(self, 
                 name: str, 
                 street_and_building: Optional[str] = None, 
                 zip_code: Optional[str] = None, 
                 city: Optional[str] = None, 
                 passport_number: Optional[str] = None, 
                 national_id_number: Optional[str] = None, 
                 notes: Optional[str] = None, 
                 phone_number: Optional[str] = None):
        super().__init__()
        self.name = name
        self.street_and_building = street_and_building
        self.zip_code = zip_code
        self.city = city
        self.passport_number = passport_number
        self.national_id_number = national_id_number
        self.notes = notes
        self.phone_number = phone_number

class SchoolParentAssociation(Base):
    __tablename__ = "school_parent_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_parents.id"), primary_key=True)

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="school_parent_associations")
    parent: Mapped["SchoolParent"] = relationship("SchoolParent", back_populates="school_parent_associations")
    def __init__(self, school_id: uuid.UUID, parent_id: uuid.UUID):
        super().__init__()
        self.school_id = school_id
        self.parent_id = parent_id