import datetime
import decimal
import enum
from sqlalchemy import String, DateTime, Numeric, ForeignKey, UUID, func, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from dateutil.relativedelta import relativedelta
from backend.database.base import Base
import typing
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum
from backend.permissions.permissions_schemas import  PERMISSIONS

class RoleType(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

#
class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[typing.Optional[str]] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    school_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        onupdate=func.now(), nullable=True
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
    files: Mapped[list["File"]] = relationship("File", back_populates="school")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="school")
    users: Mapped[list["User"]] = relationship("User", back_populates="school")
    teachers: Mapped[list["Teacher"]] = relationship("Teacher", back_populates="school")
    classrooms: Mapped[list["Classroom"]] = relationship(
        "Classroom", back_populates="school"
    )
    academic_terms: Mapped[list["AcademicTerm"]] = relationship(
        "AcademicTerm", back_populates="school"
    )
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="school")

    def __init__(
        self,
        name: str,
        school_number: str,
        country: str,
        address: typing.Optional[str] = None,
    ):
        super().__init__()
        self.name = name
        self.school_number = school_number
        self.country = country
        self.address = address


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    date_of_birth: Mapped[datetime.datetime] = mapped_column()
    gender: Mapped[str] = mapped_column(String)
    grade_level: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="students"
    )

    school_students_associations: Mapped[list["SchoolStudentAssociation"]] = (
        relationship("SchoolStudentAssociation", back_populates="student")
    )

    schools: Mapped[list["School"]] = relationship(
        "School", secondary="school_student_associations", viewonly=True
    )
    files: Mapped[list["File"]] = relationship("File", back_populates="student")

    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="student"
    )
    exam_results: Mapped[list["ExamResult"]] = relationship(
        "ExamResult", back_populates="student"
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="student_user", uselist=False
    )

    parent_student_associations: Mapped[list["ParentStudentAssociation"]] = (
        relationship("ParentStudentAssociation", back_populates="student")
    )
    parents: Mapped[list["SchoolParent"]] = relationship(
        "SchoolParent", secondary="parent_student_associations", viewonly=True
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: datetime.datetime,
        gender: str,
        grade_level: int,
        classroom_id: uuid.UUID,
    ):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.grade_level = grade_level
        self.classroom_id = classroom_id


class SchoolParent(Base):
    __tablename__ = "school_parents"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    gender: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    street_and_building: Mapped[typing.Optional[str]] = mapped_column(String)
    zip_code: Mapped[typing.Optional[str]] = mapped_column(String)
    city: Mapped[typing.Optional[str]] = mapped_column(String)
    passport_number: Mapped[typing.Optional[str]] = mapped_column(String)
    national_id_number: Mapped[str] = mapped_column(String)
    notes: Mapped[typing.Optional[str]] = mapped_column(String)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

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
    files: Mapped[list["File"]] = relationship("File", back_populates="parent")
    user: Mapped["User"] = relationship(
        "User", back_populates="parent_user", uselist=False
    )

    def __init__(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        email: str,
        national_id_number: str,
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


class ParentStudentAssociation(Base):
    __tablename__ = "parent_student_associations"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("school_parents.id"), primary_key=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("students.id"), primary_key=True
    )

    parent: Mapped["SchoolParent"] = relationship(
        "SchoolParent", back_populates="parent_student_associations"
    )
    student: Mapped["Student"] = relationship(
        "Student", back_populates="parent_student_associations"
    )


class Teacher(Base):

    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school: Mapped["School"] = relationship("School", back_populates="teachers")
    classrooms: Mapped[list["Classroom"]] = relationship(
        "Classroom", back_populates="teacher"
    )
    modules: Mapped[list["Module"]] = relationship(
        "Module", secondary="teacher_module_association", back_populates="teachers"
    )
    files: Mapped[list["File"]] = relationship("File", back_populates="teacher")
    user: Mapped["User"] = relationship(
        "User", back_populates="teacher_user", uselist=False
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="teacher"
    )

    def __init__(
        self,
        name: str,
        email: str,
        school_id: uuid.UUID,
        phone_number: typing.Optional[str] = None,
    ):
        super().__init__()
        self.name = name
        self.email = email
        self.school_id = school_id
        self.phone_number = phone_number


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    grade_level: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="classrooms")

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("teachers.id"))
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="classrooms")

    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="classroom"
    )

    def __init__(
        self, name: str, grade_level: int, school_id: uuid.UUID, teacher_id: uuid.UUID
    ):
        super().__init__()
        self.name = name
        self.grade_level = grade_level
        self.school_id = school_id
        self.teacher_id = teacher_id


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[typing.Optional[str]] = mapped_column(String)

    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher", secondary="teacher_module_association", back_populates="modules"
    )
    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="module")

    def __init__(self, name: str, description: typing.Optional[str] = None):
        super().__init__()
        self.name = name
        self.description = description


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime.datetime] = mapped_column()
    status: Mapped[str] = mapped_column(String)  # Present, Absent, Late, etc.
    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    student: Mapped["Student"] = relationship("Student", back_populates="attendances")

    def __init__(self, date: datetime.datetime, status: str, student_id: uuid.UUID):
        super().__init__()
        self.date = date
        self.status = status
        self.student_id = student_id


class AcademicTerm(Base):
    __tablename__ = "academic_terms"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    start_date: Mapped[datetime.datetime] = mapped_column()
    end_date: Mapped[datetime.datetime] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="academic_terms")

    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="academic_term")

    def __init__(
        self,
        name: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        school_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.school_id = school_id


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g., 'A', 'B', 'C', 'D', 'F'
    min_score: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False)
    max_score: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False)
    gpa_point: Mapped[decimal.Decimal] = mapped_column(nullable=False
    )  # e.g., 4.0, 3.0, 2.0, 1.0, 0.0
    description: Mapped[typing.Optional[str]] = mapped_column(String)


    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="grades")

    def __init__(
        self,
        name: str,
        min_score: decimal.Decimal,
        max_score: decimal.Decimal,
        gpa_point: decimal.Decimal,
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


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    date: Mapped[datetime.datetime] = mapped_column()
    total_marks: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship("Module", back_populates="exams")

    academic_term_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("academic_terms.id")
    )
    academic_term: Mapped["AcademicTerm"] = relationship(
        "AcademicTerm", back_populates="exams"
    )

    exam_results: Mapped[list["ExamResult"]] = relationship(
        "ExamResult", back_populates="exam"
    )

    def __init__(
        self,
        name: str,
        date: datetime.datetime,
        total_marks: float,
        module_id: uuid.UUID,
        academic_term_id: uuid.UUID,
    ):
        super().__init__()
        self.name = name
        self.date = date
        self.total_marks = total_marks
        self.module_id = module_id
        self.academic_term_id = academic_term_id


class ExamResult(Base):
    __tablename__ = "exam_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    marks_obtained: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("exams.id"))
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_results")

    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"))
    student: Mapped["Student"] = relationship("Student", back_populates="exam_results")

    def __init__(
        self, marks_obtained: float, exam_id: uuid.UUID, student_id: uuid.UUID
    ):
        super().__init__()
        self.marks_obtained = marks_obtained
        self.exam_id = exam_id
        self.student_id = student_id


class SchoolParentAssociation(Base):
    __tablename__ = "school_parent_associations"

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("schools.id"), primary_key=True
    )

    school: Mapped["School"] = relationship(
        "School", back_populates="school_parent_associations"
    )

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("school_parents.id"), primary_key=True
    )
    parent: Mapped["SchoolParent"] = relationship(
        "SchoolParent", back_populates="school_parent_associations"
    )


class SchoolStudentAssociation(Base):
    __tablename__ = "school_student_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("schools.id"), primary_key=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("students.id"), primary_key=True
    )

    school: Mapped["School"] = relationship(
        "School", back_populates="school_students_associations"
    )
    student: Mapped["Student"] = relationship(
        "Student", back_populates="school_students_associations"
    )

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


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    file_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # ---
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="files")

    # ---
    parent_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("school_parents.id")
    )
    parent: Mapped[typing.Optional["SchoolParent"]] = relationship(
        "SchoolParent", back_populates="files"
    )

    # ---
    student_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("students.id")
    )
    student: Mapped[typing.Optional["Student"]] = relationship(
        "Student", back_populates="files"
    )
    teacher_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("teachers.id")
    )
    teacher: Mapped[typing.Optional["Teacher"]] = relationship(
        Teacher, back_populates="files"
    )

    def __init__(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        file_path: str,
        school_id: uuid.UUID,
        parent_id: typing.Optional[uuid.UUID] = None,
        student_id: typing.Optional[uuid.UUID] = None,
    ):
        super().__init__()
        self.filename = filename
        self.file_type = file_type
        self.file_size = file_size
        self.file_path = file_path
        self.school_id = school_id
        self.parent_id = parent_id
        self.student_id = student_id


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[float] = mapped_column(nullable=False)
    payment_date: Mapped[datetime.datetime] = mapped_column()
    payment_method: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(onupdate=func.now())

    # --
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="payments")

    teacher_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("teachers.id")
    )
    teacher: Mapped[typing.Optional["Teacher"]] = relationship(
        "Teacher", back_populates="payments"
    )

    def __init__(
        self,
        amount: float,
        payment_date: datetime.datetime,
        payment_method: str,
        school_id: uuid.UUID,
    ):
        super().__init__()
        self.amount = amount
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.school_id = school_id


class TeacherModuleAssociation(Base):

    __tablename__ = "teacher_module_association"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("teachers.id"), primary_key=True
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("modules.id"), primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # ---
    student_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("students.id")
    )

    student_user: Mapped[typing.Optional["Student"]] = relationship(
        "Student", back_populates="user", uselist=False
    )

    # ---
    parent_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("school_parents.id")
    )
    parent_user: Mapped["SchoolParent"] = relationship(
        "SchoolParent", back_populates="user", uselist=False
    )

    # ---
    teacher_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("teachers.id")
    )
    teacher_user: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="user", uselist=False
    )
    # ---

    school_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(
        UUID, ForeignKey("schools.id")
    )
    school: Mapped["School"] = relationship("School", back_populates="users")

    # ---

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary='user_role_associations', back_populates="users"
    )
    # ---

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )

    def __init__(
        self,
        email: str,
        username: str,
        password_hash: str,
        school_id: typing.Optional[uuid.UUID] = None,
        student_id: typing.Optional[uuid.UUID] = None,
        parent_id: typing.Optional[uuid.UUID] = None,
        teacher_id: typing.Optional[uuid.UUID] = None,
    ):
        super().__init__()
        ids = [student_id, parent_id, teacher_id]
        if sum(x is not None for x in ids) > 1:
            raise ValueError(
                "A user can only be either a student, teacher, or parent, but not all at the same time."
            )

        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.school_id = school_id


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    expire_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    # ---
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __init__(self, user_id: uuid.UUID):
        super().__init__()

        self.user_id = user_id
        self.expire_at = datetime.datetime.utcnow() + relativedelta(months=6)


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    permission_description: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary='role_permission_associations', back_populates="user_permissions"
    )
    @property
    def permissions(self):
        return PERMISSIONS.model_validate(self.permission_description)

    def __init__(self, permission_description: PERMISSIONS):
        super().__init__()
        self.permission_description = PERMISSIONS.model_validate(permission_description).dict(exclude_unset=True)
        

class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission_associations'

    role_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('roles.id'), primary_key=True)
    user_permission_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('user_permissions.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

class UserRoleAssociation(Base):
    __tablename__ = 'user_role_associations'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('users.id'), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('roles.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False)
    description: Mapped[typing.Optional[str]] = mapped_column(String)
    
    user_permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission", secondary='role_permission_associations', back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(
        "User", secondary='user_role_associations', back_populates="roles"
    )
    def __init__(self, name: str,type: RoleType, description: typing.Optional[str] = None):
        super().__init__()
        self.name = name
        self.description = description
        self.type = type