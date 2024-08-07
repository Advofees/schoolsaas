from pydantic import BaseModel

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