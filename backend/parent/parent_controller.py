from pydantic import BaseModel

from fastapi import APIRouter

router= APIRouter()
class GetParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    student_id: str

class CreateParent(BaseModel):
    first_name: str
    last_name: str
    phone: str
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
