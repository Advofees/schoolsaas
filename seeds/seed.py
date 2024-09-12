from dotenv import load_dotenv
from faker import Faker
load_dotenv()
import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.models import StaffUser, SchoolStaff, School, SchoolStaffPermissions, Teacher, Module, Student, Exam, ExamResult, Classroom, AcademicTerm
from backend.authentication.passwords import hash_password
from sqlalchemy.orm import Session
from backend.database.database import get_db
import datetime

faker = Faker()

def seed_user(db: Session):
    # Create a school
    school = School(
        name=faker.name(),
        address=faker.address(),
        country=faker.country(),
        school_number=str(faker.random_number(digits=6, fix_len=True)),
    )
    db.add(school)
    db.flush()

    # Create permissions
    permissions_1 = SchoolStaffPermissions(
        can_add_students=True,
        can_manage_classes=True,
        can_view_reports=False,
        can_add_parents=True
    )
    permission_2 = SchoolStaffPermissions(
        can_add_students=True,
        can_manage_classes=True,
        can_view_reports=True,
        can_add_parents=True
    )
    db.add_all([permissions_1, permission_2])
    db.flush()

    # Create staff users
    school_staff = SchoolStaff(
        name=faker.name(),
        school_id=school.id,
        permissions_id=permissions_1.id,
    )
    school_staff_1 = SchoolStaff(
        name=faker.name(),
        school_id=school.id,
        permissions_id=permission_2.id,
    )
    db.add_all([school_staff, school_staff_1])
    db.flush()

    user = StaffUser(
        username=faker.user_name(),
        email="user@app.com",
        password_hash=hash_password("password123"),
        school_staff_id=school_staff.id
    )
    user_1 = StaffUser(
        username=faker.user_name(),
        email=faker.email(),
        password_hash=hash_password("password123"),
        school_staff_id=school_staff.id
    )
    db.add_all([user, user_1])
    db.flush()

    # Create teachers and their modules
    teachers = []
    for i in range(7):
        teacher = Teacher(name=faker.name(), email=faker.email(), school_id=school.id)
        db.add(teacher)
        db.flush()
        module = Module(name=f"Module {i+1}", description=faker.text())
        db.add(module)
        db.flush()
        teacher.modules.append(module)
        db.flush()
        teachers.append(teacher)

    # Create students and their exam results
    for i in range(5):
        classroom = Classroom(name=f"Classroom {i+1}", grade_level=i+1, school_id=school.id, teacher_id=teachers[i].id)
        db.add(classroom)
        db.flush()

        academic_term = AcademicTerm(name=f"Term {i+1}", start_date=datetime.datetime(2023, 1, 1), end_date=datetime.datetime(2023, 12, 31), school_id=school.id)
        db.add(academic_term)
        db.flush()

        for j in range(5):  # Ensure at least 5 students per classroom
            student = Student(name=faker.name(), date_of_birth=datetime.datetime(2005, 1, 1), gender=faker.random_element(elements=("M","F")), grade_level=i+1, classroom_id=classroom.id)
            db.add(student)
            db.flush()

            for teacher in teachers:
                for module in teacher.modules:
                    exam = Exam(name=f"Exam {module.name}", date=datetime.datetime(2023, 6, 1), total_marks=100, module_id=module.id, academic_term_id=academic_term.id)
                    db.add(exam)
                    db.flush()

                    exam_result = ExamResult(marks_obtained=random.randint(40, 100), exam_id=exam.id, student_id=student.id)
                    db.add(exam_result)
                    db.flush()

    db.commit()

if __name__ == "__main__":
    db = get_db()
    seed_user(db)