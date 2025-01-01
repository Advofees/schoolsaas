import uuid

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query
from backend.database.database import DatabaseDependency
from backend.student.parent.parent_model import ParentStudentAssociation
from backend.student.student_model import Student
from backend.user.user_models import RoleType, User
from backend.school.school_model import School, SchoolParent, SchoolParentAssociation
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


@router.get("/parents/list", status_code=status.HTTP_200_OK)
async def get_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    query = db.query(SchoolParent)

    if not user.has_role_type(RoleType.SUPER_ADMIN):
        school = db.query(School).filter(School.user_id == user.id).first()
        if not school:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        query = query.join(SchoolParentAssociation).filter(
            SchoolParentAssociation.school_id == school.id,
            SchoolParentAssociation.is_active == True,
        )

    parents = query.offset(offset).limit(limit).all()
    return parents


@router.get("/parents/{student_id}")
async def get_student_parents(
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
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
        or user.has_role_type(RoleType.CLASS_TEACHER)
        or user.has_role_type(RoleType.TEACHER)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    parents = (
        db.query(SchoolParent)
        .join(ParentStudentAssociation)
        .join(SchoolParentAssociation)
        .filter(
            ParentStudentAssociation.student_id == student_id,
            SchoolParentAssociation.school_id == user.school_id,  #
        )
        .all()
    )

    return parents


class updateParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    student_id: uuid.UUID
    role_id: uuid.UUID


@router.put("/parent/update", status_code=status.HTTP_200_OK)
async def update_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    body: updateParent,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    school = db.query(School).filter(School.user_id == user.id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    school_parent = (
        db.query(SchoolParent).filter(SchoolParent.id == body.student_id).first()
    )

    if not school_parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School Parent not found"
        )
    parent_association = (
        db.query(SchoolParentAssociation)
        .filter(
            SchoolParentAssociation.school_id == school.id,
            SchoolParentAssociation.parent_id == school_parent.id,
            SchoolParentAssociation.is_active == True,
        )
        .first()
    )

    if not parent_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found in this school",
        )

    school_parent.first_name = body.first_name
    school_parent.last_name = body.last_name
    school_parent.phone_number = body.phone
    school_parent.email = body.email

    db.flush()
    db.commit()

    return {"message": "School Parent updated successfully"}


@router.delete(
    "/parent/delete/{school_parent_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    school_parent_id: uuid.UUID,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    if not (
        user.has_role_type(RoleType.SUPER_ADMIN)
        or user.has_role_type(RoleType.SCHOOL_ADMIN)
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="permission-denied"
        )

    school = db.query(School).filter(School.user_id == user.id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    school_parent = (
        db.query(SchoolParent).filter(SchoolParent.id == school_parent_id).first()
    )

    if not school_parent:
        raise HTTPException(status_code=404, detail="School Parent not found")

    parent_association = (
        db.query(SchoolParentAssociation)
        .filter(
            SchoolParentAssociation.school_id == school.id,
            SchoolParentAssociation.parent_id == school_parent.id,
            SchoolParentAssociation.is_active == True,
        )
        .first()
    )

    if not parent_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found in this school",
        )
    parent_association.is_active = False

    db.query(ParentStudentAssociation).filter(
        ParentStudentAssociation.parent_id == school_parent.id
    ).delete()

    db.query(SchoolParentAssociation).filter(
        SchoolParentAssociation.parent_id == school_parent.id
    ).delete()

    db.delete(school_parent)
    db.flush()
    db.commit()

    return {"message": "School Parent deleted successfully"}
