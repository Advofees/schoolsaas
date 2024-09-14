from dotenv import load_dotenv
from faker import Faker
load_dotenv()
import random

import backend.database.all_models  # pyright: ignore [reportUnusedImport]
from backend.permissions.permissions_schemas import PERMISSIONS, ParentPermissions, StudentPermissions
from backend.models import Role, RoleType, User, School, UserPermission, Teacher, Module, Student, Exam, ExamResult, Classroom, AcademicTerm, UserRoleAssociation
from backend.user.passwords import hash_password
from sqlalchemy.orm import Session
from backend.database.database import get_db
import datetime

faker = Faker()

def seed_user(db: Session):

    school = School(
        name=faker.name(),
        address=faker.address(),
        country=faker.country(),
        school_number=str(faker.random_number(digits=6, fix_len=True)),
    )
    db.add(school)
    db.flush()

    parent_management_permission_definition = PERMISSIONS(
        parent_permissions=ParentPermissions(can_add_parents=True, can_edit_parents=True, can_view_parents=True, can_delete_parents=True),
        student_permissions=StudentPermissions(can_add_students=True, can_edit_students=True, can_view_students=True, can_delete_students=True,),
        
    )

    parent_management_permission_user_permission = UserPermission(permission_description=parent_management_permission_definition)
    
    db.add(parent_management_permission_user_permission)   
    db.flush()

    role = Role(name="SchoolRole", type=RoleType.SCHOOL_ADMIN)
    role.user_permissions.append(parent_management_permission_user_permission)

    db.add(role)
    db.flush()

    user = User(
        username=faker.user_name(),
        email="phantomschool@app.com",
        password_hash=hash_password("password123"),
        school_id=school.id
    )
    db.add(user)
    db.flush()
    
    user_role_association = UserRoleAssociation(user_id=user.id, role_id=role.id)
    db.add(user_role_association)
    db.flush()


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
            student = Student(first_name=faker.name(),last_name=faker.last_name(), date_of_birth=datetime.datetime(2005, 1, 1), gender=faker.random_element(elements=("M","F")), grade_level=i+1, classroom_id=classroom.id)
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