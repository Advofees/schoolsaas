from dotenv import load_dotenv


load_dotenv()

import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.database.all_models import get_all_models

get_all_models()
import datetime

import mimetypes
import os
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
from backend.file.file_model import Profile, File
from backend.s3.aws_s3_service import init_s3_client
from backend.s3.s3_constants import BUCKET_NAME
from backend.module.module_model import Module, ModuleEnrollment
from backend.school.school_model import School, SchoolParent, SchoolParentAssociation
from backend.student.parent.parent_model import ParentStudentAssociation
from backend.student.student_model import Student, Gender
from backend.teacher.teacher_model import ClassTeacherAssociation, Teacher
from backend.classroom.classroom_model import Classroom
from backend.academic_term.academic_term_model import AcademicTerm
from backend.school.school_model import School, SchoolStudentAssociation
from backend.exam.exam_model import Exam
from backend.exam.exam_results.exam_result_model import ExamResult
from backend.attendance.attendance_models import Attendance, AttendanceStatus
from backend.user.passwords import hash_password

from backend.payment.payment_model import (
    PaymentUserAssociation,
    Payment,
    PaymentCategory,
    PaymentDirection,
    PaymentMethod,
    PaymentStatus,
    PaymentUserType,
)

faker = Faker()


def create_simple_profile(file_path: str, user_id: uuid.UUID, db: Session):
    s3 = init_s3_client()

    # Make sure user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Check if bucket exists, create if it doesn't
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except:
        s3.create_bucket(Bucket=BUCKET_NAME)

    # Read file and get its details
    with open(file_path, "rb") as file:
        file_content = file.read()
        file_size = len(file_content)
        file_name = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0]

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    if file_path.lower().endswith(".png"):
        content_type = "image/png"
    elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
        content_type = "image/jpeg"
    elif file_path.lower().endswith(".svg"):
        content_type = "image/svg+xml"

    # Clean filename and create S3 key
    clean_filename = file_name.replace(" ", "_")
    file_key = f"profiles/{user_id}/{uuid.uuid4()}-{clean_filename}"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=file_content,
        ContentType=content_type,
        ACL="private",
    )

    existing_profiles = (
        db.query(Profile)
        .filter(Profile.user_id == user_id, Profile.is_active == True)
        .all()
    )

    for profile in existing_profiles:
        profile.is_active = False

    new_file = File(
        name=file_name,
        file_type=content_type,
        size=file_size,
        path=file_key,
        user_id=user_id,
    )
    db.add(new_file)
    db.flush()

    profile = Profile(file_id=new_file.id, user_id=user_id)
    db.add(profile)
    db.commit()

    return profile


def create_tumaini_school(db: Session):

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

    school_admin_user = User(
        username="principal.makena",
        email="principal.makena@tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(school_admin_user)
    db.flush()

    tumaini_academy = School(
        name="Tumaini Academy",
        address="Thika Road, Juja",
        country="Kenya",
        school_number=str(faker.random_number(digits=6, fix_len=True)),
        user_id=school_admin_user.id,
    )
    db.add(tumaini_academy)
    db.flush()
    # Create School Admin Role
    school_admin_role = Role(
        name="SchoolRole",
        type=RoleType.SCHOOL_ADMIN,
        description="School Administrator Role",
        school_id=tumaini_academy.id,
    )
    db.add(school_admin_role)
    db.flush()

    school_role_permission_assoc = RolePermissionAssociation(
        role_id=school_admin_role.id, user_permission_id=school_management_permission.id
    )
    db.add(school_role_permission_assoc)
    db.flush()

    school_profile = create_simple_profile(
        file_path="dev/profiles/school.png", user_id=school_admin_user.id, db=db
    )

    school_user_permission_association = UserPermissionAssociation(
        user_id=school_admin_user.id,
        user_permission_id=school_management_permission.id,
        school_id=tumaini_academy.id,
    )
    db.add(school_user_permission_association)
    db.flush()

    school_user_role_association = UserRoleAssociation(
        user_id=school_admin_user.id,
        role_id=school_admin_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(school_user_role_association)
    db.flush()

    grade_1_classroom = Classroom(
        name="Grade 1 Simba",  # Simba means Lion in Swahili
        grade_level=1,
        school_id=tumaini_academy.id,
    )
    db.add(grade_1_classroom)
    db.flush()

    grade_2_classroom = Classroom(
        name="Grade 2 Chui",  # Chui means Leopard in Swahili
        grade_level=2,
        school_id=tumaini_academy.id,
    )
    db.add(grade_2_classroom)
    db.flush()

    # Create Academic Terms
    term_1_2024 = AcademicTerm(
        name="Term 1 2024",
        start_date=datetime.datetime(2024, 1, 1),
        end_date=datetime.datetime(2024, 4, 30),
        school_id=tumaini_academy.id,
    )
    term_2_2024 = AcademicTerm(
        name="Term 2 2024",
        start_date=datetime.datetime(2024, 5, 1),
        end_date=datetime.datetime(2024, 8, 31),
        school_id=tumaini_academy.id,
    )
    term_3_2024 = AcademicTerm(
        name="Term 3 2024",
        start_date=datetime.datetime(2024, 9, 1),
        end_date=datetime.datetime(2024, 12, 31),
        school_id=tumaini_academy.id,
    )
    db.add_all([term_1_2024, term_2_2024, term_3_2024])
    db.flush()

    # Create Modules
    mathematics_module = Module(
        name="Mathematics",
        description="Comprehensive mathematics curriculum including algebra and geometry",
    )
    db.add(mathematics_module)
    db.flush()

    additional_modules = [
        Module(
            name="Science",
            description="Foundational science concepts including physics and biology",
        ),
        Module(
            name="Kiswahili",
            description="Kiswahili language and literature studies",
        ),
        Module(
            name="English",
            description="English language and composition",
        ),
        Module(
            name="Social Studies",
            description="History, geography and civic education",
        ),
        Module(
            name="CRE",
            description="Christian Religious Education",
        ),
    ]
    db.add_all(additional_modules)
    db.flush()

    teacher_role = Role(
        name="TeacherRole",
        type=RoleType.CLASS_TEACHER,
        description="Teacher Role",
        school_id=tumaini_academy.id,
    )
    db.add(teacher_role)
    db.flush()

    # Create Mathematics Teacher
    math_teacher_user = User(
        username="teacher.wanjiku",
        email="grace.wanjiku@tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(math_teacher_user)
    db.flush()

    math_teacher_profile = create_simple_profile(
        file_path="dev/profiles/teacher.png", user_id=math_teacher_user.id, db=db
    )
    math_teacher_role_assoc = UserRoleAssociation(
        user_id=math_teacher_user.id,
        role_id=teacher_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(math_teacher_role_assoc)
    db.flush()

    math_teacher = Teacher(
        first_name="Grace",
        last_name="Wanjiku",
        email="grace.wanjiku@tumaini.edu.ke",
        school_id=tumaini_academy.id,
        user_id=math_teacher_user.id,
    )
    db.add(math_teacher)
    db.flush()

    math_teacher_classroom_assoc = ClassTeacherAssociation(
        teacher_id=math_teacher.id,
        classroom_id=grade_1_classroom.id,
        is_primary=True,
    )
    db.add(math_teacher_classroom_assoc)
    db.flush()

    # Create Science Teacher
    science_teacher_user = User(
        username="teacher.ochieng",
        email="peter.ochieng@tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(science_teacher_user)
    db.flush()

    science_teacher_role_assoc = UserRoleAssociation(
        user_id=science_teacher_user.id,
        role_id=teacher_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(science_teacher_role_assoc)
    db.flush()

    science_teacher = Teacher(
        first_name="Peter",
        last_name="Ochieng",
        email="peter.ochieng@tumaini.edu.ke",
        school_id=tumaini_academy.id,
        user_id=science_teacher_user.id,
    )
    db.add(science_teacher)
    db.flush()

    science_teacher_classroom_assoc = ClassTeacherAssociation(
        teacher_id=science_teacher.id,
        classroom_id=grade_2_classroom.id,
        is_primary=True,
    )
    db.add(science_teacher_classroom_assoc)
    db.flush()

    # Create Student Role
    student_role = Role(
        name="StudentRole",
        type=RoleType.STUDENT,
        description="Student Role",
        school_id=tumaini_academy.id,
    )
    db.add(student_role)
    db.flush()

    # Grade 1 Students
    # Student 1: David Kamau
    student_kamau_user = User(
        username="david.kamau",
        email="david.kamau@student.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(student_kamau_user)
    db.flush()

    student_kamau_profile = create_simple_profile(
        file_path="dev/profiles/girl.png", user_id=student_kamau_user.id, db=db
    )

    student_kamau_role_assoc = UserRoleAssociation(
        user_id=student_kamau_user.id,
        role_id=student_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(student_kamau_role_assoc)
    db.flush()

    student_kamau = Student(
        first_name="David",
        last_name="Kamau",
        date_of_birth=datetime.datetime(2017, 3, 15),
        gender=Gender.MALE.value,
        grade_level=1,
        classroom_id=grade_1_classroom.id,
        user_id=student_kamau_user.id,
    )
    db.add(student_kamau)
    db.flush()

    student_kamau_school_assoc = SchoolStudentAssociation(
        student_id=student_kamau.id, school_id=tumaini_academy.id
    )
    db.add(student_kamau_school_assoc)
    db.flush()

    # Student 2: Faith Muthoni
    student_muthoni_user = User(
        username="faith.muthoni",
        email="faith.muthoni@student.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(student_muthoni_user)
    db.flush()

    student_muthoni_role_assoc = UserRoleAssociation(
        user_id=student_muthoni_user.id,
        role_id=student_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(student_muthoni_role_assoc)
    db.flush()

    student_muthoni = Student(
        first_name="Faith",
        last_name="Muthoni",
        date_of_birth=datetime.datetime(2017, 5, 20),
        gender=Gender.FEMALE.value,
        grade_level=1,
        classroom_id=grade_1_classroom.id,
        user_id=student_muthoni_user.id,
    )
    db.add(student_muthoni)
    db.flush()

    student_muthoni_school_assoc = SchoolStudentAssociation(
        student_id=student_muthoni.id, school_id=tumaini_academy.id
    )
    db.add(student_muthoni_school_assoc)
    db.flush()

    # Student 3: James Kiprop
    student_kiprop_user = User(
        username="james.kiprop",
        email="james.kiprop@student.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(student_kiprop_user)
    db.flush()

    student_kiprop_role_assoc = UserRoleAssociation(
        user_id=student_kiprop_user.id,
        role_id=student_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(student_kiprop_role_assoc)
    db.flush()

    student_kiprop = Student(
        first_name="James",
        last_name="Kiprop",
        date_of_birth=datetime.datetime(2017, 7, 10),
        gender=Gender.MALE.value,
        grade_level=1,
        classroom_id=grade_1_classroom.id,
        user_id=student_kiprop_user.id,
    )
    db.add(student_kiprop)
    db.flush()

    student_kiprop_school_assoc = SchoolStudentAssociation(
        student_id=student_kiprop.id, school_id=tumaini_academy.id
    )
    db.add(student_kiprop_school_assoc)
    db.flush()

    # Grade 2 Students
    # Student 4: Sarah Akinyi
    student_akinyi_user = User(
        username="sarah.akinyi",
        email="sarah.akinyi@student.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(student_akinyi_user)
    db.flush()

    student_akinyi_role_assoc = UserRoleAssociation(
        user_id=student_akinyi_user.id,
        role_id=student_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(student_akinyi_role_assoc)
    db.flush()

    student_akinyi = Student(
        first_name="Sarah",
        last_name="Akinyi",
        date_of_birth=datetime.datetime(2016, 4, 25),
        gender=Gender.FEMALE.value,
        grade_level=2,
        classroom_id=grade_2_classroom.id,
        user_id=student_akinyi_user.id,
    )
    db.add(student_akinyi)
    db.flush()

    student_akinyi_school_assoc = SchoolStudentAssociation(
        student_id=student_akinyi.id, school_id=tumaini_academy.id
    )
    db.add(student_akinyi_school_assoc)
    db.flush()

    # Student 5: Daniel Njoroge
    student_njoroge_user = User(
        username="daniel.njoroge",
        email="daniel.njoroge@student.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(student_njoroge_user)
    db.flush()

    student_njoroge_role_assoc = UserRoleAssociation(
        user_id=student_njoroge_user.id,
        role_id=student_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(student_njoroge_role_assoc)
    db.flush()

    student_njoroge = Student(
        first_name="Daniel",
        last_name="Njoroge",
        date_of_birth=datetime.datetime(2016, 6, 15),
        gender=Gender.MALE.value,
        grade_level=2,
        classroom_id=grade_2_classroom.id,
        user_id=student_njoroge_user.id,
    )
    db.add(student_njoroge)
    db.flush()

    student_njoroge_school_assoc = SchoolStudentAssociation(
        student_id=student_njoroge.id, school_id=tumaini_academy.id
    )
    db.add(student_njoroge_school_assoc)
    db.flush()

    # Create parent role
    parent_role = Role(
        name=RoleType.PARENT.name,
        type=RoleType.PARENT,
        description=RoleType.PARENT.value,
        school_id=tumaini_academy.id,
    )
    db.add(parent_role)
    db.flush()

    # Create parent users and associations
    # Parent for David Kamau
    kamau_parent_user = User(
        username="parent.kamau",
        email="john.kamau@parent.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(kamau_parent_user)
    db.flush()

    parent_kamau_role_assoc = UserRoleAssociation(
        user_id=kamau_parent_user.id,
        role_id=parent_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(parent_kamau_role_assoc)
    db.flush()

    kamau_parent = SchoolParent(
        first_name="John",
        last_name="Kamau",
        gender="male",
        email="john.kamau@parent.tumaini.edu.ke",
        phone_number="254700123456",
        national_id_number="12345678",
        user_id=kamau_parent_user.id,
    )
    db.add(kamau_parent)
    db.flush()

    kamau_school_association = SchoolParentAssociation(
        school_id=tumaini_academy.id, parent_id=kamau_parent.id
    )
    db.add(kamau_school_association)
    db.flush()

    kamau_student_association = ParentStudentAssociation(
        parent_id=kamau_parent.id,
        student_id=student_kamau.id,
        relationship_type="father",
    )
    db.add(kamau_student_association)
    db.flush()

    # Parent for Faith Muthoni
    muthoni_parent_user = User(
        username="parent.muthoni",
        email="alice.muthoni@parent.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(muthoni_parent_user)
    db.flush()

    parent_muthoni_role_assoc = UserRoleAssociation(
        user_id=muthoni_parent_user.id,
        role_id=parent_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(parent_muthoni_role_assoc)
    db.flush()

    muthoni_parent = SchoolParent(
        first_name="Alice",
        last_name="Muthoni",
        gender="female",
        email="alice.muthoni@parent.tumaini.edu.ke",
        phone_number="254711987654",
        national_id_number="87654321",
        user_id=muthoni_parent_user.id,
    )
    db.add(muthoni_parent)
    db.flush()

    muthoni_school_association = SchoolParentAssociation(
        school_id=tumaini_academy.id, parent_id=muthoni_parent.id
    )
    db.add(muthoni_school_association)
    db.flush()

    muthoni_student_association = ParentStudentAssociation(
        parent_id=muthoni_parent.id,
        student_id=student_muthoni.id,
        relationship_type="mother",
    )
    db.add(muthoni_student_association)
    db.flush()

    # Parent for James Kiprop
    kiprop_parent_user = User(
        username="parent.kiprop",
        email="william.kiprop@parent.tumaini.edu.ke",
        password_hash=hash_password("password123"),
    )
    db.add(kiprop_parent_user)
    db.flush()

    parent_kiprop_role_assoc = UserRoleAssociation(
        user_id=kiprop_parent_user.id,
        role_id=parent_role.id,
        school_id=tumaini_academy.id,
    )
    db.add(parent_kiprop_role_assoc)
    db.flush()

    kiprop_parent = SchoolParent(
        first_name="William",
        last_name="Kiprop",
        gender="male",
        email="william.kiprop@parent.tumaini.edu.ke",
        phone_number="254722345678",
        national_id_number="23456789",
        user_id=kiprop_parent_user.id,
    )
    db.add(kiprop_parent)
    db.flush()

    kiprop_school_association = SchoolParentAssociation(
        school_id=tumaini_academy.id, parent_id=kiprop_parent.id
    )
    db.add(kiprop_school_association)
    db.flush()

    kiprop_student_association = ParentStudentAssociation(
        parent_id=kiprop_parent.id,
        student_id=student_kiprop.id,
        relationship_type="father",
    )
    db.add(kiprop_student_association)
    db.flush()

    # Collect all students for attendance and payments
    all_students = [
        student_kamau,
        student_muthoni,
        student_kiprop,
        student_akinyi,
        student_njoroge,
    ]

    # Create attendance records
    attendance_months = {
        1: (term_1_2024, [8, 15, 22, 29]),  # January
        2: (term_1_2024, [5, 12, 19, 26]),  # February
        3: (term_1_2024, [4, 11, 18, 25]),  # March
        5: (term_2_2024, [6, 13, 20, 27]),  # May
        6: (term_2_2024, [3, 10, 17, 24]),  # June
        7: (term_2_2024, [1, 8, 15, 22]),  # July
        10: (term_3_2024, [7, 14, 21, 28]),  # October
        11: (term_3_2024, [4, 11, 18, 25]),  # November
        12: (term_3_2024, [2, 9, 16, 23]),  # December
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

    # Create attendance records for each month
    for month, (academic_term, mondays) in attendance_months.items():
        for day in mondays:
            start_date = datetime.datetime(2024, month, day)
            create_attendance_records(
                db,
                students=all_students,
                start_date=start_date,
                school_id=tumaini_academy.id,
                academic_term_id=academic_term.id,
            )

    # Create module enrollments
    all_modules = [mathematics_module] + additional_modules
    for student in all_students:
        for module in all_modules:
            module_enrollment = ModuleEnrollment(
                student_id=student.id,
                module_id=module.id,
            )
            db.add(module_enrollment)
    db.flush()

    # Create exams and results
    for module in all_modules:
        term_exams = [
            Exam(
                name=f"{module.name} Term 1 Assessment",
                date=datetime.datetime(2024, 3, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=term_1_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 2 Assessment",
                date=datetime.datetime(2024, 7, 15),
                total_marks=100,
                module_id=module.id,
                academic_term_id=term_2_2024.id,
            ),
            Exam(
                name=f"{module.name} Term 3 Assessment",
                date=datetime.datetime(2024, 10, 1),
                total_marks=100,
                module_id=module.id,
                academic_term_id=term_3_2024.id,
            ),
        ]
        db.add_all(term_exams)
        db.flush()

        # Create exam results
        for student in all_students:
            for exam in term_exams:
                base_score = 75

                # Adjust scores based on student strengths
                if module.name == "Mathematics" and student in [
                    student_muthoni,
                    student_akinyi,
                ]:
                    base_score += 15
                elif module.name == "Science" and student in [
                    student_kiprop,
                    student_njoroge,
                ]:
                    base_score += 15
                elif module.name == "English" and student in [
                    student_kamau,
                    student_muthoni,
                ]:
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

    # Create payments
    # Student fee payments
    for student in all_students:
        term1_payment = Payment(
            amount=decimal.Decimal("15000.00"),
            date=datetime.datetime(2024, 1, 5),
            method=PaymentMethod.BANK_TRANSFER,
            category=PaymentCategory.TUITION,
            status=PaymentStatus.COMPLETED,
            direction=PaymentDirection.INBOUND,
            school_id=tumaini_academy.id,
            recorded_by_id=school_admin_user.id,
            reference_number=f"T1FEE-{uuid.uuid4().hex[:6]}",
            description=f"Term 1 2024 Tuition Fee - {student.first_name} {student.last_name}",
            payee=student.user_id,
        )
        db.add(term1_payment)
        db.flush()

        student_payment_assoc = PaymentUserAssociation(
            payment_id=term1_payment.id,
            user_id=student.user_id,
            type=PaymentUserType.RELATED,
        )
        recorder_payment_assoc = PaymentUserAssociation(
            payment_id=term1_payment.id,
            user_id=school_admin_user.id,
            type=PaymentUserType.RECORDER,
        )
        db.add_all([student_payment_assoc, recorder_payment_assoc])
        db.flush()

        term2_payment = Payment(
            amount=decimal.Decimal("15000.00"),
            date=datetime.datetime(2024, 5, 3),
            method=PaymentMethod.MPESA,
            category=PaymentCategory.TUITION,
            status=PaymentStatus.COMPLETED,
            direction=PaymentDirection.INBOUND,
            school_id=tumaini_academy.id,
            recorded_by_id=school_admin_user.id,
            reference_number=f"T2FEE-{uuid.uuid4().hex[:6]}",
            description=f"Term 2 2024 Tuition Fee - {student.first_name} {student.last_name}",
            payee=student.user_id,
        )
        db.add(term2_payment)
        db.flush()

        student_payment_assoc2 = PaymentUserAssociation(
            payment_id=term2_payment.id,
            user_id=student.user_id,
            type=PaymentUserType.RELATED,
        )
        recorder_payment_assoc2 = PaymentUserAssociation(
            payment_id=term2_payment.id,
            user_id=school_admin_user.id,
            type=PaymentUserType.RECORDER,
        )
        db.add_all([student_payment_assoc2, recorder_payment_assoc2])
        db.flush()

    # Teacher salary payments
    teachers = [math_teacher, science_teacher]
    for teacher in teachers:
        jan_salary = Payment(
            amount=decimal.Decimal("45000.00"),
            date=datetime.datetime(2024, 1, 31),
            method=PaymentMethod.BANK_TRANSFER,
            category=PaymentCategory.OTHER,
            status=PaymentStatus.COMPLETED,
            direction=PaymentDirection.OUTBOUND,
            school_id=tumaini_academy.id,
            recorded_by_id=school_admin_user.id,
            reference_number=f"SAL-JAN-{uuid.uuid4().hex[:6]}",
            description=f"January 2024 Salary - {teacher.first_name} {teacher.last_name}",
            payee=teacher.user_id,
        )
        db.add(jan_salary)
        db.flush()

        teacher_payment_assoc = PaymentUserAssociation(
            payment_id=jan_salary.id,
            user_id=teacher.user_id,
            type=PaymentUserType.RELATED,
        )

        recorder_payment_assoc = PaymentUserAssociation(
            payment_id=jan_salary.id,
            user_id=school_admin_user.id,
            type=PaymentUserType.RECORDER,
        )
        db.add_all([teacher_payment_assoc, recorder_payment_assoc])
        db.flush()

        feb_salary = Payment(
            amount=decimal.Decimal("45000.00"),
            date=datetime.datetime(2024, 2, 28),
            method=PaymentMethod.BANK_TRANSFER,
            category=PaymentCategory.OTHER,
            status=PaymentStatus.COMPLETED,
            direction=PaymentDirection.OUTBOUND,
            school_id=tumaini_academy.id,
            recorded_by_id=school_admin_user.id,
            reference_number=f"SAL-FEB-{uuid.uuid4().hex[:6]}",
            description=f"February 2024 Salary - {teacher.first_name} {teacher.last_name}",
            payee=teacher.user_id,
        )
        db.add(feb_salary)
        db.flush()

        teacher_payment_assoc_feb = PaymentUserAssociation(
            payment_id=feb_salary.id,
            user_id=teacher.user_id,
            type=PaymentUserType.RELATED,
        )
        recorder_payment_assoc_feb = PaymentUserAssociation(
            payment_id=feb_salary.id,
            user_id=school_admin_user.id,
            type=PaymentUserType.RECORDER,
        )
        db.add_all([teacher_payment_assoc_feb, recorder_payment_assoc_feb])
        db.flush()

    db.commit()
