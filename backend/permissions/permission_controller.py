import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.database import DatabaseDependency
from backend.user.user_models import RoleType, User, UserPermission

from backend.permissions.permissions_schemas import PERMISSIONS, TeacherPermissions
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


class TeacherPermissionModel(BaseModel):
    permissions: TeacherPermissions


@router.put("/school/teachers/permission/{teacher_user_id}/{teacher_id}")
async def update_user_permissions(
    body: TeacherPermissionModel,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    teacher_user_id: uuid.UUID,
    teacher_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_update = db.query(User).filter(User.id == teacher_user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Permission denied")

    role = next(
        (role for role in user_to_update.roles if role.type == RoleType.TEACHER),
        None,
    )
    if not role:
        raise HTTPException(status_code=403, detail="Permission denied")

    teacher_permission_definition = PERMISSIONS(teacher_permissions=body.permissions)

    teacher_permission_permission = UserPermission(
        permission_description=teacher_permission_definition
    )
    role.user_permissions.append(teacher_permission_permission)
    db.commit()
    return {"detail": "Permissions updated successfully"}


class RemoveAllUserPermissions(BaseModel):
    user_id: uuid.UUID


@router.put("/school/teachers/permission/{user_id}")
def remove_all_user_permissions(
    body: RemoveAllUserPermissions,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_to_update = db.query(User).filter(User.id == body.user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Permission denied")

    if any(
        permission.permissions.school_permissions.can_delete_school
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    role = next(
        (role for role in user_to_update.roles if role.type == RoleType.SCHOOL_ADMIN),
        None,
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.user_permissions = []
    db.commit()
    return {"detail": "Permissions removed successfully"}
