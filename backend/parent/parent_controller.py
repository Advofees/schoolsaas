from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.database.database import DatabaseDependency
from backend.models import SchoolParent, User
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


class UpdateParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    student_id: str


class DeleteParent(BaseModel):
    parent_id: str


@router.get("/parent/create")
async def create_parent(
    auth_context: UserAuthenticationContextDependency,
    db: DatabaseDependency,
    parent: CreateParent,
):
  
    user=db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404)
    # ---
    if not user.school_id:
        raise HTTPException(status_code=403)
    
    school_parent= SchoolParent(
        first_name=parent.first_name,
        last_name=parent.last_name,
        phone_number=parent.phone_number,
        email=parent.email,
        gender=parent.gender,
    )

    parent_user_account= User(
        email=parent.email,
        school_id=user.school_id,
        username=parent.email,
        password_hash="",
    )

    db.add(school_parent)
    db.flush()
    db.commit()
    return {}
