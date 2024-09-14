from pydantic import BaseModel
from fastapi import APIRouter

from backend.database.database import DatabaseDependency

router=APIRouter()
class GetSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str

class CreateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str

class UpdateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str
    
class DeleteSchool(BaseModel):
    school_id: str

@router.get("/school/list")
def get_school(db:DatabaseDependency, ):
    pass

@router.post("/school/create")
def create_school():
    pass

@router.put("/school/update")
def update_school():
    pass

@router.delete("/school/delete/{school_id}")
def delete_school():
    pass

@router.get("/school/school-id/{school_id}")
def get_school_by_id():
    pass