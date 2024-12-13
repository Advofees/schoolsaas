from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.school.school_model import School
from backend.teacher.teacher_model import Teacher
from backend.user.user_models import Role, RoleType, User, UserRoleAssociation
from backend.user.passwords import hash_password
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


@router.get("/school/teachers/list")
async def get_teachers_in_a_particular_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user-not-found"
        )

    school = db.query(School).filter(School.id == user.school_user.id).first()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School not found"
        )
    return school.teachers


@router.get("/school/teachers/{teacher_id}")
async def get_teacher_in_particular_school_by_id(
    teacher_id: int,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )

    return teacher


class TeacherModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str


@router.post("/school/teachers/create")
async def create_teacher_in_particular_school(
    body: TeacherModel,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user-not-found"
        )

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user-be-in-a-school"
        )

    user_with_email = db.query(User).filter(User.email == body.email).first()

    if user_with_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user-with-this-email-already-exists",
        )

    new_teacher_user = User(
        email=body.email,
        password_hash=hash_password(password=body.password),
        username=body.email,
    )
    db.add(new_teacher_user)

    teacher_role = db.query(Role).filter(Role.name == RoleType.TEACHER.name).first()

    if not teacher_role:
        teacher_role = Role(
            name=RoleType.TEACHER.name,
            type=RoleType.TEACHER,
            description=RoleType.TEACHER.value,
        )
        db.add(teacher_role)
        db.flush()
    else:
        teacher_role_association = UserRoleAssociation(
            user_id=new_teacher_user.id, role_id=teacher_role.id
        )
        db.add(teacher_role_association)
        db.flush()

    teacher_with_email = (
        db.query(Teacher)
        .filter(Teacher.email == body.email, Teacher.school_id == user.school_id)
        .first()
    )
    if teacher_with_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="teacher-with-this-email-already-exists",
        )

    new_teacher = Teacher(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        school_id=user.school_id,
        user_id=new_teacher_user.id,
    )
    db.add(new_teacher)
    db.commit()

    return {"message": "teacher-created-successfully"}
