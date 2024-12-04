from dotenv import load_dotenv

load_dotenv()

import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.database.all_models import get_all_models

get_all_models()

import random
import decimal
from faker import Faker

import backend.database.all_models  # pyright: ignore [reportUnusedImport]
from backend.permissions.permissions_schemas import (
    PERMISSIONS,
    SchoolPermissions,
    StudentPermissions,
    TeacherPermissions,
)
from backend.user.user_models import (
    User,
    Role,
    RoleType,
    UserPermission,
    RolePermissionAssociation,
    UserPermissionAssociation,
    UserRoleAssociation,
)
from backend.module.module_model import Module, ModuleEnrollment
from backend.school.school_model import School
from backend.student.student_model import Student
from backend.teacher.teacher_model import Teacher
from backend.classroom.classroom_model import Classroom
from backend.academic_term.academic_term_model import AcademicTerm
from backend.school.school_model import School, SchoolStudentAssociation
from backend.exam.exam_model import Exam
from backend.exam.exam_results.exam_result_model import ExamResult

from backend.user.passwords import hash_password
from backend.database.database import get_db
import datetime

from sqlalchemy import MetaData, create_engine

from backend.database.database import DATABASE_URL, get_db

from alembic import command
from alembic.config import Config

engine = create_engine(DATABASE_URL)

metadata = MetaData()
metadata.reflect(engine)
faker = Faker()
with engine.begin() as connection:
    # the use of reversed(metadata.sorted_tables) is to ensure that foreign key constraints are not violated
    for table in reversed(metadata.sorted_tables):
        if table.name == "alembic_version":
            continue

        connection.execute(table.delete())

engine.dispose()

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")


with get_db() as db:

    school_management_permission_definition = PERMISSIONS(
        teacher_permissions=TeacherPermissions(
            can_add_teachers=True,
            can_edit_teachers=True,
            can_view_teachers=True,
            can_delete_teachers=True,
        ),
        student_permissions=StudentPermissions(
            can_add_students=True,
            can_edit_students=True,
            can_view_students=True,
            can_delete_students=True,
        ),
        school_permissions=SchoolPermissions(
            can_manage_school=True,
            can_view_school=True,
            can_add_school=True,
            can_edit_school=True,
            can_delete_school=True,
        ),
    )

    # Create UserPermission instance
    school_management_permission = UserPermission(
        permission_description=school_management_permission_definition
    )
    db.add(school_management_permission)
    db.flush()

    school_admin_role = Role(
        name="SchoolRole",
        type=RoleType.SCHOOL_ADMIN,
        description="School Administrator Role",
    )
    db.add(school_admin_role)
    db.flush()

    school_role_permission_assoc = RolePermissionAssociation(
        role_id=school_admin_role.id, user_permission_id=school_management_permission.id
    )
    db.add(school_role_permission_assoc)
    db.flush()

    # Create User
    user = User(
        username="school",
        email="school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(user)
    db.flush()

    # Create UserPermissionAssociation
    user_permission_assoc = UserPermissionAssociation(
        user_id=user.id, user_permission_id=school_management_permission.id
    )
    db.add(user_permission_assoc)
    db.flush()

    # Create School
    school = School(
        name=faker.name(),
        address=faker.address(),
        country=faker.country(),
        school_number=str(faker.random_number(digits=6, fix_len=True)),
        user_id=user.id,
    )
    db.add(school)
    db.flush()

    # Create UserRoleAssociation
    user_role_association = UserRoleAssociation(
        user_id=user.id, role_id=school_admin_role.id
    )
    db.add(user_role_association)
    db.flush()

    # Create Classroom
    classroom = Classroom(
        name=f"Classroom 1 ",
        grade_level=1,
        school_id=school.id,
    )
    db.add(classroom)
    db.flush()

    # Create AcademicTerm
    academic_term = AcademicTerm(
        name=f"Term 1",
        start_date=datetime.datetime(2023, 1, 1),
        end_date=datetime.datetime(2023, 12, 31),
        school_id=school.id,
    )
    db.add(academic_term)
    db.flush()

    # Create Modules
    possible_modules = [
        "Mathematics",
        "Science",
        "English",
        "History",
        "Geography",
        "Computer studies",
        "Kiswahili",
    ]
    modules: list[Module] = []
    for module in possible_modules:
        new_module = Module(
            name=f"{module} Module",
            description=faker.text(),
        )
        modules.append(new_module)
    db.add_all(modules)
    db.flush()

    # Create Exam
    exam = Exam(
        name=f"Exam Module name",
        date=datetime.datetime(2023, 6, 1),
        total_marks=100,
        module_id=modules[0].id,
        academic_term_id=academic_term.id,
    )
    db.add(exam)
    db.flush()

    # Create Teachers
    teachers: list[Teacher] = []
    for i in range(len(possible_modules)):
        # Create teacher user with permissions
        teacher_user = User(
            username=faker.user_name(),
            email=faker.email(),
            password_hash=hash_password("password123"),
        )
        db.add(teacher_user)
        db.flush()

        # Create teacher role and permissions if needed
        teacher_role = Role(
            name=f"TeacherRole_{i}", type=RoleType.TEACHER, description="Teacher Role"
        )
        db.add(teacher_role)
        db.flush()

        # Associate teacher user with role
        teacher_role_assoc = UserRoleAssociation(
            user_id=teacher_user.id, role_id=teacher_role.id
        )
        db.add(teacher_role_assoc)
        db.flush()

        teacher = Teacher(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            school_id=school.id,
            user_id=teacher_user.id,
        )
        teachers.append(teacher)
    db.add_all(teachers)
    db.flush()

    # Create Students
    students: list[Student] = []
    for j in range(5):
        # Create student user with permissions
        student_user = User(
            username=faker.user_name(),
            email=faker.email(),
            password_hash=hash_password("password123"),
        )
        db.add(student_user)
        db.flush()

        # Create student role and permissions
        student_role = Role(
            name=f"StudentRole_{j}", type=RoleType.STUDENT, description="Student Role"
        )
        db.add(student_role)
        db.flush()

        # Associate student user with role
        student_role_assoc = UserRoleAssociation(
            user_id=student_user.id, role_id=student_role.id
        )
        db.add(student_role_assoc)
        db.flush()

        student = Student(
            first_name=faker.name(),
            last_name=faker.last_name(),
            date_of_birth=datetime.datetime(2005, 1, 1),
            gender=faker.random_element(elements=("M", "F")),
            grade_level=1,
            classroom_id=classroom.id,
            user_id=student_user.id,
        )
        db.add(student)
        students.append(student)
        db.flush()

        school_student_association = SchoolStudentAssociation(
            student_id=student.id, school_id=school.id
        )
        db.add(school_student_association)
        db.flush()

    db.add_all(students)
    db.flush()

    # Create ExamResults and ModuleEnrollments
    exam_results: list[ExamResult] = []
    for student in students:
        for module in modules:
            # Create module enrollment
            module_enrollment = ModuleEnrollment(
                student_id=student.id,
                module_id=module.id,
            )
            db.add(module_enrollment)
            db.flush()

            # Create exam results
            exam_result = ExamResult(
                marks_obtained=decimal.Decimal(random.randint(40, 100)),
                exam_id=exam.id,
                student_id=student.id,
                class_room_id=classroom.id,
                module_id=module.id,
            )
            exam_results.append(exam_result)
    db.add_all(exam_results)
    db.flush()

    db.commit()
