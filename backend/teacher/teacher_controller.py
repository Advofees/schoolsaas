from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.email_service.mail_service import EmailServiceDependency, SendEmailParams
from backend.school.school_model import School
from backend.teacher.teacher_model import Teacher
from backend.user.user_models import RoleType, User
from backend.user.passwords import generate_temp_password, hash_password
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


@router.get("/school/teachers/list")
async def get_teachers_in_a_particular_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.teacher_permissions.can_view_teachers
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    school = db.query(School).filter(School.id == user.school_user.id).first()

    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school.teachers


@router.get("/school/teachers/{teacher_id}")
async def get_teacher_in_particular_school_by_id(
    teacher_id: int,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.teacher_permissions.can_view_teachers
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return teacher


class TeacherModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str


@router.post("/school/teachers/create")
async def create_teacher_in_particular_school(
    email_service: EmailServiceDependency,
    body: TeacherModel,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not any(
        permission.permissions.teacher_permissions.can_add_teachers
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    school = db.query(School).filter(School.id == user.school_user.id).first()

    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    user_with_email = db.query(User).filter(User.email == body.email).first()
    if user_with_email:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    temporary_password = generate_temp_password(8)

    email_params = SendEmailParams(
        email=user.email,
        subject="Welcome to {school.name}",
        message=f"You have been added as a teacher in our school : here is temporary password{temporary_password}, change it after login",
    )

    email_service.send(email_params)
    new_teacher_user = User(
        email=body.email,
        password_hash=hash_password(password=body.password),
        username=body.email,
    )
    db.add(new_teacher_user)

    teacher_with_email = (
        db.query(Teacher)
        .filter(Teacher.email == body.email, Teacher.school_id == school.id)
        .first()
    )
    if teacher_with_email:
        raise HTTPException(
            status_code=400, detail="Teacher with this email already exists"
        )

    new_teacher = Teacher(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        school_id=school.id,
        user_id=new_teacher_user.id,
    )
    db.add(new_teacher)
    db.commit()

    return {"detail": "Teacher created successfully"}
