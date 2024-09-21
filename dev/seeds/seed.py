import decimal
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
import random

import backend.database.all_models  # pyright: ignore [reportUnusedImport]
from backend.permissions.permissions_schemas import (
    PERMISSIONS,
    ClassPermissions,
    ExamResultPermissions,
    ParentPermissions,
    SchoolPermissions,
    StudentPermissions,
    TeacherPermissions,
)
from backend.models import (
    Role,
    RoleType,
    User,
    School,
    UserPermission,
    Teacher,
    Module,
    Student,
    Exam,
    ExamResult,
    Classroom,
    AcademicTerm,
    UserRoleAssociation,
)
from backend.user.passwords import hash_password
from sqlalchemy.orm import Session
from backend.database.database import get_db
import datetime

faker = Faker()


def seed_user(db: Session):

    parent_management_permission_definition = PERMISSIONS(
        class_permissions=ClassPermissions(
            can_add_classes=True,
            can_edit_classes=True,
            can_view_classes=True,
            can_delete_classes=True,
        ),
        teacher_permissions=TeacherPermissions(
            can_add_teachers=True,
            can_edit_teachers=True,
            can_view_teachers=True,
            can_delete_teachers=True,
        ),
        exam_result_permissions=ExamResultPermissions(
            can_add_exam_results=True,
            can_edit_exam_results=True,
            can_view_exam_results=True,
            can_delete_exam_results=True,
        ),
        parent_permissions=ParentPermissions(
            can_add_parents=True,
            can_edit_parents=True,
            can_view_parents=True,
            can_delete_parents=True,
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
            can_manage_permissions=True,
            can_delete_permissions=True,
            can_add_permissions=True,
            can_edit_permissions=True,
            can_view_permissions=True,
        ),
    )

    parent_management_permission_user_permission = UserPermission(
        permission_description=parent_management_permission_definition
    )

    db.add(parent_management_permission_user_permission)
    db.flush()

    role = Role(name="SchoolRole", type=RoleType.SCHOOL_ADMIN)
    role.user_permissions.append(parent_management_permission_user_permission)

    db.add(role)
    db.flush()

    user = User(
        username="school",
        email="school@app.com",
        password_hash=hash_password("password123"),
    )
    db.add(user)
    db.flush()
    school = School(
        name=faker.name(),
        address=faker.address(),
        country=faker.country(),
        school_number=str(faker.random_number(digits=6, fix_len=True)),
        user_id=user.id,
    )
    db.add(school)
    db.flush()
    user_role_association = UserRoleAssociation(user_id=user.id, role_id=role.id)
    db.add(user_role_association)
    db.flush()

    classroom = Classroom(
        name=f"Classroom 1 ",
        grade_level=1,
        school_id=school.id,
    )
    db.add(classroom)
    db.flush()

    academic_term = AcademicTerm(
        name=f"Term 1",
        start_date=datetime.datetime(2023, 1, 1),
        end_date=datetime.datetime(2023, 12, 31),
        school_id=school.id,
    )
    db.add(academic_term)
    db.flush()
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

    exam = Exam(
        name=f"Exam Module name",
        date=datetime.datetime(2023, 6, 1),
        total_marks=100,
        module_id=modules[0].id,
        academic_term_id=academic_term.id,
    )
    db.add(exam)
    db.flush()

    # --create school teachers
    teachers:list[Teacher] = []
    for i in range(len(possible_modules)):
        teacher_user = User(
            username=faker.user_name(),
            email=faker.email(),
            password_hash=hash_password("password123"),
        )
        db.add(teacher_user)
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


    # --- create school students
    students:list[Student] = []
    
    for j in range(5):
        student_user = User(
            username=faker.user_name(),
            email=faker.email(),
            password_hash=hash_password("password123"),
        )
        db.add(student_user)
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
        students.append(student)

    db.add_all(students)
    db.flush()

    # --- create exam results
    exam_results:list[ExamResult] = []
    for student in students:
        for module in modules:
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



if __name__ == "__main__":
    db = get_db()
    seed_user(db)
    db.commit()
