import datetime
from sqlalchemy import String, DateTime,  Numeric, ForeignKey, UUID, func, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid
from dateutil.relativedelta import relativedelta
from backend.database.base import Base
import typing

class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[typing.Optional[str]] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    school_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(onupdate=func.now(),nullable=True)


    school_parent_associations: Mapped[list["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="school")
    school_students_associations: Mapped[list["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="school")
    school_parents: Mapped[list["SchoolParent"]] = relationship("SchoolParent", secondary="school_parent_associations", viewonly=True)
    students: Mapped[list["Student"]] = relationship("Student", secondary="school_student_associations", viewonly=True)
    inventories: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="school")
    files: Mapped[list["File"]] = relationship("File", back_populates="school")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="school")
    school_staffs: Mapped[list["SchoolStaff"]] = relationship("SchoolStaff", back_populates="school")
    teachers: Mapped[list["Teacher"]] = relationship("Teacher", back_populates="school")
    classrooms: Mapped[list["Classroom"]] = relationship("Classroom", back_populates="school")
    academic_terms: Mapped[list["AcademicTerm"]] = relationship("AcademicTerm", back_populates="school")
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="school")

    def __init__(self, name: str, school_number: str, country: str, address: typing.Optional[str] = None):
        super().__init__()
        self.name = name
        self.school_number = school_number
        self.country = country
        self.address = address

class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    date_of_birth: Mapped[datetime.datetime] = mapped_column()
    gender: Mapped[str] = mapped_column(String)
    grade_level: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))
    classroom_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("classrooms.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


    parent: Mapped[typing.Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="students")
    school_students_associations: Mapped[list["SchoolStudentAssociation"]] = relationship("SchoolStudentAssociation", back_populates="student")
    schools: Mapped[list["School"]] = relationship("School", secondary="school_student_associations", viewonly=True)
    files: Mapped[list["File"]] = relationship("File", back_populates="student")
    classroom: Mapped["Classroom"] = relationship("Classroom", back_populates="students")
    attendances: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="student")
    exam_results: Mapped[list["ExamResult"]] = relationship("ExamResult", back_populates="student")

    def __init__(self, name: str, date_of_birth: datetime.datetime, gender: str, grade_level: int, classroom_id: uuid.UUID, parent_id: typing.Optional[uuid.UUID] = None):
        super().__init__()
        self.name = name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.grade_level = grade_level
        self.classroom_id = classroom_id
        self.parent_id = parent_id


class SchoolParent(Base):
    __tablename__ = "school_parents"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    street_and_building: Mapped[typing.Optional[str]] = mapped_column(String)
    zip_code: Mapped[typing.Optional[str]] = mapped_column(String)
    city: Mapped[typing.Optional[str]] = mapped_column(String)
    passport_number: Mapped[typing.Optional[str]] = mapped_column(String)
    national_id_number: Mapped[typing.Optional[str]] = mapped_column(String)
    notes: Mapped[typing.Optional[str]] = mapped_column(String)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


    school_parent_associations: Mapped[list["SchoolParentAssociation"]] = relationship("SchoolParentAssociation", back_populates="parent")
    schools: Mapped[list["School"]] = relationship("School", secondary="school_parent_associations", viewonly=True)
    students: Mapped[list["Student"]] = relationship("Student", back_populates="parent")
    files: Mapped[list["File"]] = relationship("File", back_populates="parent")

    def __init__(self, name: str, gender: str, email: str, phone_number: typing.Optional[str] = None, street_and_building: typing.Optional[str] = None, 
                 zip_code: typing.Optional[str] = None, city: typing.Optional[str] = None, passport_number: typing.Optional[str] = None, 
                 national_id_number: typing.Optional[str] = None, notes: typing.Optional[str] = None):
        super().__init__()
        self.name = name
        self.gender = gender
        self.email = email
        self.phone_number = phone_number
        self.street_and_building = street_and_building
        self.zip_code = zip_code
        self.city = city
        self.passport_number = passport_number
        self.national_id_number = national_id_number
        self.notes = notes

class Teacher(Base):

    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


    school: Mapped["School"] = relationship("School", back_populates="teachers")
    classrooms: Mapped[list["Classroom"]] = relationship("Classroom", back_populates="teacher")
    modules: Mapped[list["Module"]] = relationship("Module", secondary="teacher_module_association", back_populates="teachers")

    def __init__(self, name: str, email: str, school_id: uuid.UUID, phone_number: typing.Optional[str] = None):
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
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="classrooms")

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("teachers.id"))
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="classrooms")

    students: Mapped[list["Student"]] = relationship("Student", back_populates="classroom")

    def __init__(self, name: str, grade_level: int, school_id: uuid.UUID, teacher_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.grade_level = grade_level
        self.school_id = school_id
        self.teacher_id = teacher_id

class Module(Base):
    __tablename__ = 'modules'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[typing.Optional[str]] = mapped_column(String)

 
    teachers: Mapped[list["Teacher"]] = relationship("Teacher", secondary="teacher_module_association", back_populates="modules")
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
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
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
    created_at: Mapped[datetime.datetime] = mapped_column( default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="academic_terms")

    exams: Mapped[list["Exam"]] = relationship("Exam", back_populates="academic_term")

    def __init__(self, name: str, start_date: datetime.datetime, end_date: datetime.datetime, school_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.school_id = school_id

class Grade(Base):
    __tablename__ = 'grades'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'A', 'B', 'C', 'D', 'F'
    min_score: Mapped[float] = mapped_column(Numeric, nullable=False)
    max_score: Mapped[float] = mapped_column(Numeric, nullable=False)
    gpa_point: Mapped[float] = mapped_column(Numeric, nullable=False)  # e.g., 4.0, 3.0, 2.0, 1.0, 0.0
    description: Mapped[typing.Optional[str]] = mapped_column(String)

    # Relationships
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="grades")

    def __init__(self, name: str, min_score: float, max_score: float, gpa_point: float, school_id: uuid.UUID, description: typing.Optional[str] = None):
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
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship("Module", back_populates="exams")

    academic_term_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("academic_terms.id"))
    academic_term: Mapped["AcademicTerm"] = relationship("AcademicTerm", back_populates="exams")

    exam_results: Mapped[list["ExamResult"]] = relationship("ExamResult", back_populates="exam")

    def __init__(self, name: str, date: datetime.datetime, total_marks: float, module_id: uuid.UUID, academic_term_id: uuid.UUID):
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
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("exams.id"))
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_results")

    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"))
    student: Mapped["Student"] = relationship("Student", back_populates="exam_results")

    def __init__(self, marks_obtained: float, exam_id: uuid.UUID, student_id: uuid.UUID):
        super().__init__()
        self.marks_obtained = marks_obtained
        self.exam_id = exam_id
        self.student_id = student_id

class SchoolParentAssociation(Base):
    __tablename__ = "school_parent_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_parents.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

  
    school: Mapped["School"] = relationship("School", back_populates="school_parent_associations")
    parent: Mapped["SchoolParent"] = relationship("SchoolParent", back_populates="school_parent_associations")

class SchoolStudentAssociation(Base):
    __tablename__ = "school_student_associations"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"), primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("students.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)


    school: Mapped["School"] = relationship("School", back_populates="school_students_associations")
    student: Mapped["Student"] = relationship("Student", back_populates="school_students_associations")

class SchoolStaff(Base):
    __tablename__ = "school_staffs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)

   
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    staff_user: Mapped["StaffUser"] = relationship("StaffUser", back_populates="school_staff", uselist=False)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="school_staffs")
    
    permissions_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("school_staff_permissions.id"), unique=True)
    school_staff_permission: Mapped["SchoolStaffPermissions"] = relationship("SchoolStaffPermissions", back_populates="school_staff", uselist=False)
    
    files: Mapped[list["File"]] = relationship("File", back_populates="school_staff")


    def __init__(self, name: str, permissions_id:uuid.UUID, school_id: uuid.UUID):
        super().__init__()
        self.name = name
        self.permissions_id=permissions_id
        self.school_id = school_id
   

class StaffUser(Base):
    __tablename__ = "staff_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    school_staff_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_staffs.id"))
    school_staff: Mapped["SchoolStaff"] = relationship("SchoolStaff", back_populates="staff_user", uselist=False)

    files: Mapped[list["File"]] = relationship("File", back_populates="staff_user")
    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="staff_user")

    def __init__(self, 
                 username: str, 
                 email: str, 
                 password_hash: str, 
                 school_staff_id: typing.Optional[uuid.UUID] = None):
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
    expire_at: Mapped[datetime.datetime] = mapped_column(DateTime,nullable=False)
    

    staff_user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("staff_users.id"),nullable=False)
    staff_user: Mapped["StaffUser"] = relationship("StaffUser", back_populates="sessions")

    def __init__(self, staff_user_id: uuid.UUID):
        super().__init__()

        self.staff_user_id = staff_user_id
        self.expire_at = datetime.datetime.utcnow() + relativedelta(months=6)

class SchoolStaffPermissions(Base):
    __tablename__ = "school_staff_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    can_add_students: Mapped[bool] = mapped_column( nullable=False)
    can_add_parents: Mapped[bool] = mapped_column(nullable=False)
    can_manage_classes: Mapped[bool] = mapped_column( nullable=False)
    can_view_reports: Mapped[bool] = mapped_column( nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


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
    item_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    # Relationships
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

    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="files")

    parent_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_parents.id"))
    parent: Mapped[typing.Optional["SchoolParent"]] = relationship("SchoolParent", back_populates="files")

    student_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("students.id"))
    student: Mapped[typing.Optional["Student"]] = relationship("Student", back_populates="files")

    staff_user_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("staff_users.id"))
    staff_user: Mapped[typing.Optional["StaffUser"]] = relationship("StaffUser", back_populates="files")

    school_staff_id: Mapped[typing.Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("school_staffs.id"))
    school_staff: Mapped[typing.Optional["SchoolStaff"]] = relationship("SchoolStaff", back_populates="files")

    def __init__(self, filename: str, file_type: str, file_size: int, file_path: str, school_id: uuid.UUID, 
                 parent_id: typing.Optional[uuid.UUID] = None, student_id: typing.Optional[uuid.UUID] = None, 
                 staff_user_id: typing.Optional[uuid.UUID] = None, school_staff_id: typing.Optional[uuid.UUID] = None):
        super().__init__()
        self.filename = filename
        self.file_type = file_type
        self.file_size = file_size
        self.file_path = file_path
        self.school_id = school_id
        self.parent_id = parent_id
        self.student_id = student_id
        self.staff_user_id = staff_user_id
        self.school_staff_id = school_staff_id

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    amount: Mapped[float] = mapped_column(nullable=False)
    payment_date: Mapped[datetime.datetime] = mapped_column()
    payment_method: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(onupdate=func.now())

    #--
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("schools.id"))
    school: Mapped["School"] = relationship("School", back_populates="payments")

    def __init__(self, amount: float, payment_date: datetime.datetime, payment_method: str, school_id: uuid.UUID):
        super().__init__()
        self.amount = amount
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.school_id = school_id

class TeacherModuleAssociation(Base):

    __tablename__ = "teacher_module_association"

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("teachers.id"), primary_key=True)
    module_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("modules.id"), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=False)