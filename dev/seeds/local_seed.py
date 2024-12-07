from dotenv import load_dotenv

load_dotenv()

import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.database.all_models import get_all_models

get_all_models()

import random
import decimal
from faker import Faker

import backend.database.all_models  # pyright: ignore [reportUnusedImport]
from backend.user.permissions.permissions_schemas import (
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
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
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
    #
    # ---school default permissions
    #
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

    school_management_permission = UserPermission(
        permission_description=school_management_permission_definition.model_dump()
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

    #
    # ---school registration(school_admin registration)
    #
    school_user = User(
        username="school",
        email="school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(school_user)
    db.flush()

    #
    # --- link school(school_admin) to their permissions
    #
    school_user_permission_association = UserPermissionAssociation(
        user_id=school_user.id, user_permission_id=school_management_permission.id
    )
    db.add(school_user_permission_association)
    db.flush()

    school = School(
        name=faker.name(),
        address=faker.address(),
        country=faker.country(),
        school_number=str(faker.random_number(digits=6, fix_len=True)),
        user_id=school_user.id,
    )
    db.add(school)
    db.flush()

    #
    # --
    #
    school_user_role_association = UserRoleAssociation(
        user_id=school_user.id, role_id=school_admin_role.id
    )
    db.add(school_user_role_association)
    db.flush()

    #
    # ---
    #
    grade_1_green_classroom = Classroom(
        name=f"Classroom 1 ",
        grade_level=1,
        school_id=school.id,
    )
    db.add(grade_1_green_classroom)
    db.flush()

    #
    # ---
    #
    first_academic_term_2024 = AcademicTerm(
        name=f"Term 1",
        start_date=datetime.datetime(2023, 1, 1),
        end_date=datetime.datetime(2023, 12, 31),
        school_id=school.id,
    )
    second_academic_term_2024 = AcademicTerm(
        name=f"Term 2",
        start_date=datetime.datetime(2023, 1, 1),
        end_date=datetime.datetime(2023, 12, 31),
        school_id=school.id,
    )
    third_academic_term_2024 = AcademicTerm(
        name=f"Term 3",
        start_date=datetime.datetime(2023, 1, 1),
        end_date=datetime.datetime(2023, 12, 31),
        school_id=school.id,
    )

    db.add_all(
        [first_academic_term_2024, second_academic_term_2024, third_academic_term_2024]
    )
    db.flush()

    #
    # --- subjects/modules
    #
    possible_modules = [
        "Mathematics",
        "Science",
        "English",
        "History",
        "Geography",
        "Computer studies",
        "Kiswahili",
    ]

    module = Module(
        name=possible_modules[0],
        description=possible_modules[0],
    )

    db.add(module)
    db.flush()

    #
    # ---
    #
    first_term_2024_exam = Exam(
        name=module.name,
        date=datetime.datetime(2023, 6, 1),
        total_marks=80,
        module_id=module.id,
        academic_term_id=third_academic_term_2024.id,
    )
    second_term_2024_exam = Exam(
        name=module.name,
        date=datetime.datetime(2023, 6, 1),
        total_marks=40,
        module_id=module.id,
        academic_term_id=third_academic_term_2024.id,
    )
    third_term_2024_exam = Exam(
        name=module.name,
        date=datetime.datetime(2023, 6, 1),
        total_marks=60,
        module_id=module.id,
        academic_term_id=third_academic_term_2024.id,
    )
    db.add_all([first_term_2024_exam, second_term_2024_exam, third_term_2024_exam])
    db.flush()

    #
    # ---
    #

    grade_1_green_teacher_user = User(
        username=faker.user_name(),
        email="teacher.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(grade_1_green_teacher_user)
    db.flush()

    # Create teacher role and permissions if needed
    teacher_role = Role(
        name=f"TeacherRole", type=RoleType.TEACHER, description="Teacher Role"
    )
    db.add(teacher_role)
    db.flush()

    # Associate teacher user with role
    teacher_role_assoc = UserRoleAssociation(
        user_id=grade_1_green_teacher_user.id, role_id=teacher_role.id
    )
    db.add(teacher_role_assoc)
    db.flush()

    grade_1_green_teacher = Teacher(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        school_id=school.id,
        user_id=grade_1_green_teacher_user.id,
    )
    db.add(grade_1_green_teacher)
    db.flush()
    #
    # --- class teacher assignment
    #

    assign_grade_1_green_classroom_a_class_teacher = ClassTeacherAssociation(
        teacher_id=grade_1_green_teacher.id,
        classroom_id=grade_1_green_classroom.id,
    )

    db.add(assign_grade_1_green_classroom_a_class_teacher)
    db.flush()

    #
    #
    #

    student_user = User(
        username=faker.user_name(),
        email="student.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(student_user)
    db.flush()

    # Create student role and permissions
    student_role = Role(
        name=f"StudentRole", type=RoleType.STUDENT, description="Student Role"
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
        classroom_id=grade_1_green_classroom.id,
        user_id=student_user.id,
    )
    db.add(student)
    db.flush()

    school_student_association = SchoolStudentAssociation(
        student_id=student.id, school_id=school.id
    )
    db.add(school_student_association)
    db.flush()

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
        exam_id=third_term_2024_exam.id,
        student_id=student.id,
        class_room_id=grade_1_green_classroom.id,
        module_id=module.id,
    )

    db.add(exam_result)
    db.flush()

    db.commit()
