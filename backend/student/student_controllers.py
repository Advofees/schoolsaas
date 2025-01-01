import typing
import uuid
from sqlalchemy import desc, asc
from fastapi import APIRouter, HTTPException, status, Query

from backend.school.school_model import (
    School,
    SchoolParent,
    SchoolParentAssociation,
    SchoolStudentAssociation,
)
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.student.student_model import HealthItem, Student
from backend.classroom.classroom_model import Classroom
from backend.student.parent.parent_model import ParentStudentAssociation
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.passwords import hash_password
from backend.paginated_response import PaginatedResponse
from backend.student.student_schemas import (
    to_student_dto,
    StudentResponse,
    OrderBy,
    StudentSortableFields,
    createStudentFullInfo,
)
from backend.student.student_model import StudentHealthRecord

router = APIRouter()


@router.get("/students/by-student-id/{student_id}")
async def get_student(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    student = (
        db.query(Student)
        .join(SchoolStudentAssociation)
        .filter(
            Student.id == student_id,
            SchoolStudentAssociation.school_id == user.school_id,
            SchoolStudentAssociation.is_active == True,
        )
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return StudentResponse(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.user.email,
        grade_level=student.grade_level,
        date_of_birth=student.date_of_birth,
        nemis_number=student.nemis_number,
        gender=student.gender,
        classroom_id=student.classroom_id,
        user_id=student.user_id,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


@router.get("/students/by-classroom-id/{classroom_id}")
async def get_students_in_classroom(
    db: DatabaseDependency,
    classroom_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    order_field: typing.Optional[StudentSortableFields] = None,
    order_direction: typing.Optional[OrderBy] = None,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    classroom = (
        db.query(Classroom)
        .filter(Classroom.id == classroom_id, Classroom.school_id == user.school_id)
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    query = db.query(Student).filter(Student.classroom_id == classroom.id)

    total_count = query.count()

    if order_field and order_direction:
        sort_column = getattr(Student, order_field.value)
        if order_direction == OrderBy.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

    offset = (page - 1) * limit
    students = query.offset(offset).limit(limit).all()

    return PaginatedResponse[StudentResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[to_student_dto(student) for student in students],
    )


@router.get("/students/by-school-id/list")
async def get_all_students_for_a_particular_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    order_field: typing.Optional[StudentSortableFields] = None,
    order_direction: typing.Optional[OrderBy] = None,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )
    query = (
        db.query(Student)
        .join(SchoolStudentAssociation)
        .join(User)
        .filter(
            SchoolStudentAssociation.school_id == user.school_id,
            SchoolStudentAssociation.is_active == True,
        )
    )

    total_count = query.count()

    if order_field and order_direction:
        sort_column = getattr(Student, order_field.value)
        if order_direction == OrderBy.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

    offset = (page - 1) * limit
    students = query.offset(offset).limit(limit).all()

    return PaginatedResponse[StudentResponse](
        total=total_count,
        page=page,
        limit=limit,
        data=[to_student_dto(student) for student in students],
    )


@router.post("/students/create")
async def create_student(
    db: DatabaseDependency,
    body: createStudentFullInfo,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )
    #
    # --- create parent
    #
    school_parent = (
        db.query(SchoolParent)
        .filter(
            SchoolParent.email == body.student_parent_info.email,
            SchoolParent.national_id_number
            == body.student_parent_info.national_id_number,
        )
        .first()
    )

    if school_parent:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="School Parent already exists"
        )
    school = db.query(School).filter(School.user_id == user.id).first()

    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    student_parent = SchoolParent(
        first_name=body.student_parent_info.first_name,
        last_name=body.student_parent_info.last_name,
        phone_number=body.student_parent_info.phone_number,
        email=body.student_parent_info.email,
        gender=body.student_parent_info.gender,
        national_id_number=body.student_parent_info.national_id_number,
        user_id=user.id,
    )

    db.add(student_parent)
    db.flush()

    school_parent_associtiaon = SchoolParentAssociation(
        school_id=school.id, parent_id=student_parent.id
    )
    db.add(school_parent_associtiaon)

    existing_parent_user = (
        db.query(User).filter(User.email == body.student_parent_info.email).first()
    )
    if existing_parent_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Parent email already exists"
        )

    parent_user = User(
        email=body.student_parent_info.email,
        username=body.student_parent_info.username,
        password_hash=hash_password(body.student_info.password),
    )
    db.add(parent_user)
    db.flush()

    parent_role = (
        db.query(Role)
        .filter(Role.type == RoleType.PARENT.value, Role.school_id == school.id)
        .first()
    )

    if not parent_role:
        parent_role = Role(
            name=RoleType.STUDENT.name,
            type=RoleType.STUDENT,
            description=RoleType.STUDENT.value,
            school_id=school.id,
        )
        db.add(parent_role)
        db.flush()

    parent_role_association = UserRoleAssociation(
        user_id=parent_user.id,
        role_id=parent_role.id,
        school_id=school.id,
    )
    db.add(parent_role_association)
    db.flush()

    #
    # ---
    #

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == body.student_info.classroom_id,
            Classroom.school_id == user.school_id,
        )
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    #
    # --- create student
    #
    existing_student_user = (
        db.query(User).filter(User.email == body.student_info.email).first()
    )
    if existing_student_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Student email already exists"
        )

    new_student_user = User(
        email=body.student_info.email,
        username=body.student_info.username,
        password_hash=hash_password(body.student_info.password),
    )
    db.add(new_student_user)
    db.flush()

    student = Student(
        first_name=body.student_info.first_name,
        last_name=body.student_info.last_name,
        date_of_birth=body.student_info.date_of_birth,
        gender=body.student_info.gender,
        grade_level=body.student_info.grade_level,
        classroom_id=classroom.id,
        user_id=new_student_user.id,
        nemis_number=body.student_info.nemis_number,
    )
    db.add(student)
    db.flush()

    student_school_association = SchoolStudentAssociation(
        student_id=student.id, school_id=classroom.school_id
    )
    db.add(student_school_association)
    db.flush()

    parent_student_association = ParentStudentAssociation(
        parent_id=student_parent.id,
        student_id=student.id,
        relationship_type=body.student_info.parent_relationship_type.value,
    )
    db.add(parent_student_association)
    db.flush()

    student_role = (
        db.query(Role)
        .filter(
            Role.type == RoleType.STUDENT.value, Role.school_id == classroom.school_id
        )
        .first()
    )

    if not student_role:
        student_role = Role(
            name=RoleType.STUDENT.name,
            type=RoleType.STUDENT,
            description=RoleType.STUDENT.value,
            school_id=classroom.school_id,
        )
        db.add(student_role)
        db.flush()

    student_role_association = UserRoleAssociation(
        user_id=new_student_user.id,
        role_id=student_role.id,
        school_id=classroom.school_id,
    )
    db.add(student_role_association)
    db.flush()

    #
    # ---create student health details
    #

    new_student_health = StudentHealthRecord(
        student_id=student.id,
        blood_type=body.student_health_info.blood_type,
        insurance_provider=body.student_health_info.insurance_provider,
        insurance_policy_number=body.student_health_info.insurance_policy_number,
        primary_doctor=body.student_health_info.primary_doctor,
        doctor_phone=body.student_health_info.doctor_phone,
    )
    db.add(new_student_health)
    db.flush()

    if body.student_health_info.health_items:
        for item in body.student_health_info.health_items:
            health_item = HealthItem(
                name=item.name,
                type=item.type.value,
                severity=item.severity.value,
                notes=item.notes,
                student_health_record_id=new_student_health.id,
            )
            db.add(health_item)
        db.flush()
    #
    # ---
    #

    #
    # --- create student upload files
    #

    db.commit()

    return {"message": "student-registered-successfully"}
