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
    for table in reversed(metadata.sorted_tables):
        if table.name == "alembic_version":
            continue
        connection.execute(table.delete())

engine.dispose()
alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")


with get_db() as db:
    # School Admin Permissions
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

    # Create School Admin Role
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

    school_admin_user = User(
        username="school@app.com",
        email="school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(school_admin_user)
    db.flush()

    school_user_permission_association = UserPermissionAssociation(
        user_id=school_admin_user.id, user_permission_id=school_management_permission.id
    )
    db.add(school_user_permission_association)
    db.flush()

    sunrise_academy = School(
        name="Sunrise Academy",
        address="123 Education Lane, Learning District",
        country="United States",
        school_number=str(faker.random_number(digits=6, fix_len=True)),
        user_id=school_admin_user.id,
    )
    db.add(sunrise_academy)
    db.flush()

    school_user_role_association = UserRoleAssociation(
        user_id=school_admin_user.id, role_id=school_admin_role.id
    )
    db.add(school_user_role_association)
    db.flush()

    grade_1_mathematics_classroom = Classroom(
        name="Grade 1 Mathematics Focus",
        grade_level=1,
        school_id=sunrise_academy.id,
    )
    db.add(grade_1_mathematics_classroom)
    db.flush()

    grade_2_science_classroom = Classroom(
        name="Grade 2 Science Focus",
        grade_level=2,
        school_id=sunrise_academy.id,
    )
    db.add(grade_2_science_classroom)
    db.flush()

    # Create Academic Terms
    first_academic_term_2024 = AcademicTerm(
        name="Term 1 2024",
        start_date=datetime.datetime(2024, 1, 1),
        end_date=datetime.datetime(2024, 4, 30),
        school_id=sunrise_academy.id,
    )
    second_academic_term_2024 = AcademicTerm(
        name="Term 2 2024",
        start_date=datetime.datetime(2024, 5, 1),
        end_date=datetime.datetime(2024, 8, 31),
        school_id=sunrise_academy.id,
    )
    third_academic_term_2024 = AcademicTerm(
        name="Term 3 2024",
        start_date=datetime.datetime(2024, 9, 1),
        end_date=datetime.datetime(2024, 12, 31),
        school_id=sunrise_academy.id,
    )
    db.add_all(
        [first_academic_term_2024, second_academic_term_2024, third_academic_term_2024]
    )
    db.flush()

    mathematics_module = Module(
        name="Mathematics",
        description="Comprehensive mathematics curriculum including algebra and geometry",
    )
    db.add(mathematics_module)
    db.flush()

    additional_modules = [
        Module(
            name="Science",
            description="Foundational physics concepts including mechanics and energy",
        ),
        Module(
            name="CRE",
            description="Introduction to chemical principles and reactions",
        ),
        Module(
            name="Kiswahili",
            description="Study of living organisms and natural systems",
        ),
        Module(
            name="English Literature",
            description="Analysis of literary works and composition",
        ),
        Module(
            name="History",
            description="World history and historical analysis",
        ),
    ]
    db.add_all(additional_modules)
    db.flush()

    math_teacher_user = User(
        username="james.thompson",
        email="teacher.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(math_teacher_user)
    db.flush()

    teacher_role = Role(
        name="TeacherRole", type=RoleType.CLASS_TEACHER, description="Teacher Role"
    )
    db.add(teacher_role)
    db.flush()

    math_teacher_role_assoc = UserRoleAssociation(
        user_id=math_teacher_user.id, role_id=teacher_role.id
    )
    db.add(math_teacher_role_assoc)
    db.flush()

    math_teacher = Teacher(
        first_name="James",
        last_name="Thompson",
        email="teacher.school@app.com",
        school_id=sunrise_academy.id,
        user_id=math_teacher_user.id,
    )
    db.add(math_teacher)
    db.flush()

    math_teacher_classroom_assoc = ClassTeacherAssociation(
        teacher_id=math_teacher.id,
        classroom_id=grade_1_mathematics_classroom.id,
        is_primary=True,
    )
    db.add(math_teacher_classroom_assoc)
    db.flush()

    # Create Second Teacher (Science)
    science_teacher_user = User(
        username="sarah.schmidt",
        email="teacher.sarah.schmidt@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(science_teacher_user)
    db.flush()

    science_teacher_role_assoc = UserRoleAssociation(
        user_id=science_teacher_user.id, role_id=teacher_role.id
    )
    db.add(science_teacher_role_assoc)
    db.flush()

    science_teacher = Teacher(
        first_name="Sarah",
        last_name="Schmidt",
        email="teacher.sarah.schmidt@school.app",
        school_id=sunrise_academy.id,
        user_id=science_teacher_user.id,
    )
    db.add(science_teacher)
    db.flush()

    science_teacher_classroom_assoc = ClassTeacherAssociation(
        teacher_id=science_teacher.id,
        classroom_id=grade_2_science_classroom.id,
        is_primary=True,
    )
    db.add(science_teacher_classroom_assoc)
    db.flush()

    # Create Student Role
    student_role = Role(
        name="StudentRole", type=RoleType.STUDENT, description="Student Role"
    )
    db.add(student_role)
    db.flush()

    # Grade 1 Students
    # Student 1: John Davis
    student1_user = User(
        username="john.davis",
        email="student.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(student1_user)
    db.flush()

    student1_role_assoc = UserRoleAssociation(
        user_id=student1_user.id, role_id=student_role.id
    )
    db.add(student1_role_assoc)
    db.flush()

    student1 = Student(
        first_name="John",
        last_name="Davis",
        date_of_birth=datetime.datetime(2017, 3, 15),
        gender="M",
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student1_user.id,
    )
    db.add(student1)
    db.flush()

    student1_school_assoc = SchoolStudentAssociation(
        student_id=student1.id, school_id=sunrise_academy.id
    )
    db.add(student1_school_assoc)
    db.flush()

    # Student 2: Michael Chang
    student2_user = User(
        username="michael.chang",
        email="student.michael.chang@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student2_user)
    db.flush()

    student2_role_assoc = UserRoleAssociation(
        user_id=student2_user.id, role_id=student_role.id
    )
    db.add(student2_role_assoc)
    db.flush()

    student2 = Student(
        first_name="Michael",
        last_name="Chang",
        date_of_birth=datetime.datetime(2017, 5, 20),
        gender="M",
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student2_user.id,
    )
    db.add(student2)
    db.flush()

    student2_school_assoc = SchoolStudentAssociation(
        student_id=student2.id, school_id=sunrise_academy.id
    )
    db.add(student2_school_assoc)
    db.flush()

    # Student 3: Sofia Patel
    student3_user = User(
        username="sofia.patel",
        email="student.sofia.patel@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student3_user)
    db.flush()

    student3_role_assoc = UserRoleAssociation(
        user_id=student3_user.id, role_id=student_role.id
    )
    db.add(student3_role_assoc)
    db.flush()

    student3 = Student(
        first_name="Sofia",
        last_name="Patel",
        date_of_birth=datetime.datetime(2017, 7, 10),
        gender="F",
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student3_user.id,
    )
    db.add(student3)
    db.flush()

    student3_school_assoc = SchoolStudentAssociation(
        student_id=student3.id, school_id=sunrise_academy.id
    )
    db.add(student3_school_assoc)
    db.flush()

    # Grade 2 Students
    # Student 4: David Kim
    student4_user = User(
        username="david.kim",
        email="student.david.kim@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student4_user)
    db.flush()

    student4_role_assoc = UserRoleAssociation(
        user_id=student4_user.id, role_id=student_role.id
    )
    db.add(student4_role_assoc)
    db.flush()

    student4 = Student(
        first_name="David",
        last_name="Kim",
        date_of_birth=datetime.datetime(2016, 4, 25),
        gender="M",
        grade_level=2,
        classroom_id=grade_2_science_classroom.id,
        user_id=student4_user.id,
    )
    db.add(student4)
    db.flush()

    student4_school_assoc = SchoolStudentAssociation(
        student_id=student4.id, school_id=sunrise_academy.id
    )
    db.add(student4_school_assoc)
    db.flush()

    # Student 5: Emily Wong
    student5_user = User(
        username="emily.wong",
        email="student.emily.wong@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student5_user)
    db.flush()

    student5_role_assoc = UserRoleAssociation(
        user_id=student5_user.id, role_id=student_role.id
    )
    db.add(student5_role_assoc)
    db.flush()

    # Student 6: Alexander Martinez
    student6_user = User(
        username="alexander.martinez",
        email="student.alex.martinez@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student6_user)
    db.flush()

    student6_role_assoc = UserRoleAssociation(
        user_id=student6_user.id, role_id=student_role.id
    )
    db.add(student6_role_assoc)
    db.flush()

    student6 = Student(
        first_name="Alexander",
        last_name="Martinez",
        date_of_birth=datetime.datetime(2016, 8, 30),
        gender="M",
        grade_level=2,
        classroom_id=grade_2_science_classroom.id,
        user_id=student6_user.id,
    )
    db.add(student6)
    db.flush()

    student6_school_assoc = SchoolStudentAssociation(
        student_id=student6.id, school_id=sunrise_academy.id
    )
    db.add(student6_school_assoc)
    db.flush()

    # Create module enrollments for all students in all modules
    all_students = [student1, student2, student3, student4, student6]
    all_modules = [mathematics_module] + additional_modules

    for student in all_students:
        for module in all_modules:
            module_enrollment = ModuleEnrollment(
                student_id=student.id,
                module_id=module.id,
            )
            db.add(module_enrollment)
    db.flush()

    # Create exams for each module
    for module in all_modules:
        term_exams = [
            Exam(
                name=f"{module.name} Term 1 Assessment",
                date=datetime.datetime(2024, 4, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=first_academic_term_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 2 Assessment",
                date=datetime.datetime(2024, 8, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=second_academic_term_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 3 Assessment",
                date=datetime.datetime(2024, 12, 1),
                total_marks=100,
                module_id=module.id,
                academic_term_id=third_academic_term_2024.id,
            ),
        ]
        db.add_all(term_exams)
        db.flush()

        # Create exam results for each student
        for student in all_students:
            for exam in term_exams:
                # Assign different grade ranges based on student's strengths
                base_score = 75  # Base score for average performance

                # Adjust scores based on student and subject
                if module.name == "Advanced Mathematics" and student in [
                    student2,
                    student3,
                ]:  # Michael and Sofia excel in math
                    base_score += 15
                elif module.name in ["Physics", "Chemistry"] and student in [
                    student4,
                ]:  # David and Emily excel in sciences
                    base_score += 15
                elif module.name == "English Literature" and student in [
                    student3,
                    student6,
                ]:  # Sofia and Alexander excel in literature
                    base_score += 15

                final_score = min(100, max(65, base_score + random.randint(-8, 8)))

                exam_result = ExamResult(
                    marks_obtained=decimal.Decimal(str(final_score)),
                    exam_id=exam.id,
                    student_id=student.id,
                    class_room_id=student.classroom_id,
                    module_id=module.id,
                )
                db.add(exam_result)
        db.flush()

    db.commit()
