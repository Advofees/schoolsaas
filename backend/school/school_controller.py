from pydantic import BaseModel
from fastapi import APIRouter,status

from backend.database.database import DatabaseDependency

router=APIRouter()




class UpdateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str
    

@router.post("/school/create",status_code=status.HTTP_201_CREATED)
def create_school():
    pass

@router.get("/school/list")
def get_school(db:DatabaseDependency, ):
    pass

@router.put("/school/update",status_code=status.HTTP_204_NO_CONTENT)
def update_school():
    pass

@router.get("/school/school-id/{school_id}",status_code=status.HTTP_200_OK)
def get_school_by_id():
    pass

@router.delete("/school/delete/{school_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_school():
    pass