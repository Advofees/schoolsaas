from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.database.database import DatabaseDependency
from backend.models import RolePermissionAssociation,  User, UserPermission
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


class GetParent(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    student_id: str


class CreateParent(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    gender: str
    email: str
    student_id: str
    role_id: str


class UpdateParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    student_id: str
    role_id: str


class DeleteParent(BaseModel):
    parent_id: str


@router.post("/parent/create")
async def create_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    body: CreateParent,
):
  
    user=db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404)
    # ---
    associated_permissions= db.query(RolePermissionAssociation).filter(RolePermissionAssociation.role_id == body.role_id).first()

    if not associated_permissions:
        raise HTTPException(status_code=404)

    user_permissions= db.query(UserPermission).filter(UserPermission.id == associated_permissions.user_permission_id).first()

    if not user_permissions:
        raise HTTPException(status_code=404)
    
    if not user_permissions.permissions.parent_permissions.can_add_parents:
        raise HTTPException(status_code=403)

    # school_parent= SchoolParent(
    #     first_name=body.first_name,
    #     last_name=body.last_name,
    #     phone_number=body.phone_number,
    #     email=body.email,
    #     gender=body.gender,
    # )

    # parent_user_account= User(
    #     email=body.email,
    #     school_id=user.school_id,
    #     username=body.email,
    #     password_hash="",
    # )

    # db.add(school_parent)
    # db.flush()
    # db.commit()
    return {}
