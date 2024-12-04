import uuid
from fastapi import APIRouter, HTTPException
from backend.database.database import DatabaseDependency
from backend.user.user_models import (
    User,
    UserPermission,
    UserPermissionAssociation,
)

from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


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
