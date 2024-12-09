from dotenv import load_dotenv

load_dotenv()

import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.database.all_models import get_all_models

get_all_models()

import random
import decimal
from faker import Faker
import uuid
from sqlalchemy.orm import Session
import backend.database.all_models  # pyright: ignore [reportUnusedImport]
from backend.user.permissions.permissions_schemas import (
    PERMISSIONS,
    SchoolPermissions,
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
from backend.student.student_model import Student, Gender
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.classroom.classroom_model import Classroom
from backend.academic_term.academic_term_model import AcademicTerm
from backend.school.school_model import School, SchoolStudentAssociation
from backend.exam.exam_model import Exam
from backend.exam.exam_results.exam_result_model import ExamResult
from backend.attendance.attendance_models import Attendance, AttendanceStatus
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
        country="Kenya",
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

    teacher_role = Role(
        name="TeacherRole", type=RoleType.CLASS_TEACHER, description="Teacher Role"
    )
    db.add(teacher_role)
    db.flush()
    #
    # ---
    #
    math_teacher_user = User(
        username="james.thompson",
        email="teacher.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(math_teacher_user)
    db.flush()

    math_teacher_role_assoc = UserRoleAssociation(
        user_id=math_teacher_user.id, role_id=teacher_role.id
    )
    db.add(math_teacher_role_assoc)
    db.flush()

    math_teacher = Teacher(
        first_name="James",
        last_name="Thompson",
        email="james.thompson@app.com",
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
        email="teacher.school@school.app",
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
        email="sarah.schmidt@school.app",
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
    student_john_davis_user = User(
        username="john.davis",
        email="student.school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(student_john_davis_user)
    db.flush()

    student_john_davis_role_assoc = UserRoleAssociation(
        user_id=student_john_davis_user.id, role_id=student_role.id
    )
    db.add(student_john_davis_role_assoc)
    db.flush()

    student_john_davis = Student(
        first_name="John",
        last_name="Davis",
        date_of_birth=datetime.datetime(2017, 3, 15),
        gender=Gender.MALE.value,
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student_john_davis_user.id,
    )
    db.add(student_john_davis)
    db.flush()

    student_john_davis_school_assoc = SchoolStudentAssociation(
        student_id=student_john_davis.id, school_id=sunrise_academy.id
    )
    db.add(student_john_davis_school_assoc)
    db.flush()

    # Student 2: Michael Chang
    student_micheal_chang = User(
        username="michael.chang",
        email="student.michael.chang@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student_micheal_chang)
    db.flush()

    student_micheal_chang_role_assoc = UserRoleAssociation(
        user_id=student_micheal_chang.id, role_id=student_role.id
    )
    db.add(student_micheal_chang_role_assoc)
    db.flush()

    student_micheal_chang = Student(
        first_name="Michael",
        last_name="Chang",
        date_of_birth=datetime.datetime(2017, 5, 20),
        gender=Gender.MALE.value,
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student_micheal_chang.id,
    )
    db.add(student_micheal_chang)
    db.flush()

    student_micheal_chang_school_assoc = SchoolStudentAssociation(
        student_id=student_micheal_chang.id, school_id=sunrise_academy.id
    )
    db.add(student_micheal_chang_school_assoc)
    db.flush()

    # Student 3: Sofia Patel
    student_sofia_patel_user = User(
        username="sofia.patel",
        email="student.sofia.patel@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student_sofia_patel_user)
    db.flush()

    student_sofia_patel_role_assoc = UserRoleAssociation(
        user_id=student_sofia_patel_user.id, role_id=student_role.id
    )
    db.add(student_sofia_patel_role_assoc)
    db.flush()

    student_sofia_patel = Student(
        first_name="Sofia",
        last_name="Patel",
        date_of_birth=datetime.datetime(2017, 7, 10),
        gender=Gender.FEMALE.value,
        grade_level=1,
        classroom_id=grade_1_mathematics_classroom.id,
        user_id=student_sofia_patel_user.id,
    )
    db.add(student_sofia_patel)
    db.flush()

    student_sofia_patel_school_assoc = SchoolStudentAssociation(
        student_id=student_sofia_patel.id, school_id=sunrise_academy.id
    )
    db.add(student_sofia_patel_school_assoc)
    db.flush()

    # Grade 2 Students
    # Student 4: David Kim
    student_david_kim_user = User(
        username="david.kim",
        email="student.david.kim@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student_david_kim_user)
    db.flush()

    student_david_kim_role_assoc = UserRoleAssociation(
        user_id=student_david_kim_user.id, role_id=student_role.id
    )
    db.add(student_david_kim_role_assoc)
    db.flush()

    student_david_kim = Student(
        first_name="David",
        last_name="Kim",
        date_of_birth=datetime.datetime(2016, 4, 25),
        gender=Gender.MALE.value,
        grade_level=2,
        classroom_id=grade_2_science_classroom.id,
        user_id=student_david_kim_user.id,
    )
    db.add(student_david_kim)
    db.flush()

    student_david_kim_school_assoc = SchoolStudentAssociation(
        student_id=student_david_kim.id, school_id=sunrise_academy.id
    )
    db.add(student_david_kim_school_assoc)
    db.flush()

    # Student 5: Emily Wong
    student_emily_wong_user = User(
        username="emily.wong",
        email="student.emily.wong@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student_emily_wong_user)
    db.flush()

    student_emily_wong_role_assoc = UserRoleAssociation(
        user_id=student_emily_wong_user.id, role_id=student_role.id
    )
    db.add(student_emily_wong_role_assoc)
    db.flush()

    # Student 6: Alexander Martinez
    student_alexander_martinez_user = User(
        username="alexander.martinez",
        email="student.alex.martinez@school.app",
        password_hash=hash_password("password123"),
    )
    db.add(student_alexander_martinez_user)
    db.flush()

    student_alexander_martinez_role_assoc = UserRoleAssociation(
        user_id=student_alexander_martinez_user.id, role_id=student_role.id
    )
    db.add(student_alexander_martinez_role_assoc)
    db.flush()

    student_alexander_martinez = Student(
        first_name="Alexander",
        last_name="Martinez",
        date_of_birth=datetime.datetime(2016, 8, 30),
        gender=Gender.MALE.value,
        grade_level=2,
        classroom_id=grade_2_science_classroom.id,
        user_id=student_alexander_martinez_user.id,
    )
    db.add(student_alexander_martinez)
    db.flush()

    student_alexander_martinez_school_assoc = SchoolStudentAssociation(
        student_id=student_alexander_martinez.id, school_id=sunrise_academy.id
    )
    db.add(student_alexander_martinez_school_assoc)
    db.flush()

    #
    # ---
    #

    all_students: list[Student] = [
        student_john_davis,
        student_micheal_chang,
        student_sofia_patel,
        student_david_kim,
        student_alexander_martinez,
    ]
    attendance_months = {
        1: (first_academic_term_2024, [8, 15, 22, 29]),  # January
        2: (first_academic_term_2024, [5, 12, 19, 26]),  # February
        3: (first_academic_term_2024, [4, 11, 18, 25]),  # March
        5: (second_academic_term_2024, [6, 13, 20, 27]),  # May
        6: (second_academic_term_2024, [3, 10, 17, 24]),  # June
        7: (second_academic_term_2024, [1, 8, 15, 22]),  # July
        10: (third_academic_term_2024, [7, 14, 21, 28]),  # October
        11: (third_academic_term_2024, [4, 11, 18, 25]),  # November
        12: (third_academic_term_2024, [2, 9, 16, 23]),  # December
    }

    def create_attendance_records(
        db: Session,
        students: list[Student],
        start_date: datetime.datetime,
        school_id: uuid.UUID,
        academic_term_id: uuid.UUID,
        num_days: int = 5,
    ):
        for student in students:
            current_date = start_date

            for day in range(num_days):
                # 90% chance of being present
                is_present = random.random() < 0.9

                attendance = Attendance(
                    date=current_date,
                    status=(
                        AttendanceStatus.PRESENT
                        if is_present
                        else AttendanceStatus.ABSENT
                    ),
                    student_id=student.id,
                    school_id=school_id,
                    classroom_id=student.classroom_id,
                    academic_term_id=academic_term_id,
                    remarks="Regular attendance" if is_present else "Absent",
                )
                db.add(attendance)

                current_date = current_date + datetime.timedelta(days=1)

        db.flush()

    for month, (academic_term, mondays) in attendance_months.items():
        for day in mondays:
            start_date = datetime.datetime(2024, month, day)
            create_attendance_records(
                db,
                students=all_students,
                start_date=start_date,
                school_id=sunrise_academy.id,
                academic_term_id=academic_term.id,
            )

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
                date=datetime.datetime(2024, 3, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=first_academic_term_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 2 Assessment",
                date=datetime.datetime(2024, 7, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=second_academic_term_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 3 Assessment",
                date=datetime.datetime(2024, 10, 1),
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
                    student_micheal_chang,
                    student_sofia_patel,
                ]:  # Michael and Sofia excel in math
                    base_score += 15
                elif module.name in ["Physics", "Chemistry"] and student in [
                    student_david_kim,
                ]:  # David and Emily excel in sciences
                    base_score += 15
                elif module.name == "English Literature" and student in [
                    student_sofia_patel,
                    student_alexander_martinez,
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
