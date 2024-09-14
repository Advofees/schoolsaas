import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException,status
from backend.database.database import DatabaseDependency
from backend.models import RolePermissionAssociation, SchoolParent,  UserPermission, UserRoleAssociation
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
    role_id: str
    national_id_number: str


class UpdateParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    student_id: uuid.UUID
    role_id: uuid.UUID


class DeleteParent(BaseModel):
    parent_id: str


@router.post("/parent/create",status_code=status.HTTP_201_CREATED)
async def create_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    body: CreateParent,

):
    
    role= db.query(RolePermissionAssociation).filter(UserRoleAssociation.user_id==auth_context.user_id).first()
    if not role:
        raise HTTPException(status_code=403, detail="User does not have a role")
    # ---
    required_associated_permissions= db.query(RolePermissionAssociation).filter(RolePermissionAssociation.role_id == body.role_id).first()

    if not required_associated_permissions:
        raise HTTPException(status_code=404)

    user_permissions= db.query(UserPermission).filter(UserPermission.id == required_associated_permissions.user_permission_id).first()

    if not user_permissions:
        raise HTTPException(status_code=404, detail="User permission not found")
    
    if not user_permissions.permissions.parent_permissions.can_add_parents:
        raise HTTPException(status_code=403)
    
    school_parent= db.query(SchoolParent).filter(SchoolParent.email == body.email,SchoolParent.national_id_number==body.national_id_number).first()

    if school_parent:
        raise HTTPException(status_code=409, detail="School Parent already exists")
    
    new_school_parent= SchoolParent(
        first_name=body.first_name,
        last_name=body.last_name,
        phone_number=body.phone_number,
        email=body.email,
        gender=body.gender,
        national_id_number=body.national_id_number,
    )

    db.add(new_school_parent)
    db.flush()
    db.commit()
    return {
        "message": "School Parent created successfully",
      }

from fastapi import Query

@router.get("/parent/list",status_code=status.HTTP_200_OK)
async def get_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    limit: int = Query(10, ge=1),  
    offset: int = Query(0, ge=0)   
):
 
    role = db.query(RolePermissionAssociation).filter(
        UserRoleAssociation.user_id == auth_context.user_id
    ).first()

    if not role:
        raise HTTPException(status_code=403, detail="User does not have a role")
    

    required_associated_permissions = db.query(RolePermissionAssociation).filter(
        RolePermissionAssociation.role_id == role.role_id
    ).first()
    if not required_associated_permissions:
        raise HTTPException(status_code=404)


    user_permissions = db.query(UserPermission).filter(
        UserPermission.id == required_associated_permissions.user_permission_id
    ).first()

    if not user_permissions:
        raise HTTPException(status_code=404, detail="User permission not found")


    if not user_permissions.permissions.parent_permissions.can_view_parents:
        raise HTTPException(status_code=403)


    total_parents = db.query(SchoolParent).count()

    parents = db.query(SchoolParent).offset(offset).limit(limit).all()
    next_offset = offset + limit
    has_next = next_offset < total_parents

    return {
        "total": total_parents,
        "limit": limit,
        "offset": offset,
        "next": f"/parent/list?limit={limit}&offset={next_offset}" if has_next else None,
        "parents": parents,
    }
