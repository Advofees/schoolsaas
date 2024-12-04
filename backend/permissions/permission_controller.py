import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.database.database import DatabaseDependency
from backend.user.user_models import (
    User,
    UserPermission,
    UserPermissionAssociation,
)

from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.permissions.permissions_schemas import PERMISSIONS

router = APIRouter()


class createUserPermissionDTO(BaseModel):
    user_id: uuid.UUID
    permission_description: dict

    @classmethod
    def validate_permissions(cls, permission_dict: dict) -> PERMISSIONS:
        base_permissions = PERMISSIONS()
        for category, perms in permission_dict.items():
            if hasattr(base_permissions, category):
                category_model = getattr(base_permissions, category)
                for perm_name, perm_value in perms.items():
                    if hasattr(category_model, perm_name):
                        setattr(category_model, perm_name, perm_value)

        return PERMISSIONS.model_validate(base_permissions.model_dump())


@router.post("/permissions/create")
def create_permission(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    body: createUserPermissionDTO,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(403, detail="not-authorized")

    valid_permission_description = createUserPermissionDTO.validate_permissions(
        body.permission_description
    )
    new_permission = UserPermission(permission_description=valid_permission_description)
    db.add(new_permission)
    db.flush()
    associated_user = db.query(User).filter(User.id == body.user_id).first()
    if not associated_user:
        raise HTTPException(404)

    association = UserPermissionAssociation(
        user_id=associated_user.id, user_permission_id=new_permission.id
    )
    db.add(association)
    db.flush()


@router.delete("/permissions/{user_permission_id}/delete")
def remove_permission(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    user_permission_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(403, detail="not-authorized")

    user_permission_association = (
        db.query(UserPermissionAssociation)
        .filter(
            UserPermissionAssociation.user_id == user.id,
            UserPermissionAssociation.user_permission_id == user_permission_id,
        )
        .first()
    )
    if not user_permission_association:
        raise HTTPException(404)

    db.delete(user_permission_association)
    permission = (
        db.query(UserPermission).filter(UserPermission.id == user_permission_id).first()
    )
    if not permission:
        raise HTTPException(404)
    db.delete(permission)
    db.flush()
