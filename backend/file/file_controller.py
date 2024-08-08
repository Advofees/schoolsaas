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

@router.get("/file/list")
def get_file():
    pass

@router.post("/file/create")
def create_file():
    pass

@router.put("/file/update/{file_id}")
def update_file(file_id: str):
    pass

@router.delete("/file/delete/{file_id}")
def delete_file(file_id: str):
    pass