from pydantic import BaseModel
from fastapi import APIRouter

router=APIRouter()
class GetFile(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    file_size: str


class CreateFile(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    file_size: str

class UpdateFile(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    file_size: str

class DeleteFile(BaseModel):
    file_id: str

@router.get("/file/{user_id}/list")
def get_file():
    pass

@router.post("/file/{user_id}/create")
def create_file():
    pass

@router.put("/file/{file_id}/update")
def update_file():
    pass

@router.delete("/file/{file_id}/delete")
def delete_file():
    pass