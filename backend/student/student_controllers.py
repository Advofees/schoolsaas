from pydantic import BaseModel

class GetStudent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    admission_number: str
    parent_id:str
    class_id: str
    payments_id: str

class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    phone: str
    admission_number: str
    parent_id:str
    class_id: str
    payments_id: str

class UpdateStudent(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str
    admission_number: str
    parent_id:str
    class_id: str

class DeleteStudent(BaseModel):
    student_id: str

