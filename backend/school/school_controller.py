import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Query

from backend.database.database import DatabaseDependency
from backend.models import (
    RoleType,
    School,
    User,
)
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


    
class UpdateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str


@router.get("/school/list", status_code=status.HTTP_200_OK)
def get_school(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    if not user.has_role_type(RoleType.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not any(
        permission.permissions.school_permissions.can_view_school
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
   
        
    total_schools = db.query(School).count()

    schools = db.query(School).offset(offset).limit(limit).all()
    next_offset = offset + limit
    has_next = next_offset < total_schools

    return {
        "total": total_schools,
        "limit": limit,
        "offset": offset,
        "next": (
            f"/school/list?limit={limit}&offset={next_offset}" if has_next else None
        ),
        "schools": schools,
    }


@router.put("/school/{school_id}/update", status_code=status.HTTP_204_NO_CONTENT)
def update_school(
    db: DatabaseDependency,
    body: UpdateSchool,
    auth_context: UserAuthenticationContextDependency,
    school_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    school.name = body.name

    db.commit()
    return {}

@router.get("/school/{school_id}/delete", status_code=status.HTTP_200_OK)
def get_school_by_id(
    db: DatabaseDependency,
    school_id: int,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.school_permissions.can_view_school
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    return school