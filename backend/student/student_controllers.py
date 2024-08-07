from pydantic import BaseModel
from fastapi import APIRouter,status, HTTPException
import typing
router = APIRouter()
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

students = [
        GetStudent(first_name="John", last_name="Doe", phone="1234567890", admission_number="1234", parent_id="5678", class_id="9A", payments_id="abcd1234"),
        GetStudent(first_name="John", last_name="Doe", phone="1234567890", admission_number="1235", parent_id="5678", class_id="9A", payments_id="abcd1234"),
        GetStudent(first_name="John", last_name="Doe", phone="1234567890", admission_number="1236", parent_id="5678", class_id="9A", payments_id="abcd1234"),
        GetStudent(first_name="John", last_name="Doe", phone="1234567890", admission_number="1237", parent_id="5678", class_id="9A", payments_id="abcd1234"),
        GetStudent(first_name="John", last_name="Doe", phone="1234567890", admission_number="1238", parent_id="5678", class_id="9A", payments_id="abcd1234")
    ]




@router.get("/students/all", response_model=typing.List[GetStudent], status_code=status.HTTP_200_OK)
async def all_students():
    return students

@router.post("/students/create", status_code=status.HTTP_201_CREATED)
async def create_student(student: CreateStudent):
    return {"message": "Student created"}

@router.patch("/students/update", status_code=status.HTTP_200_OK)
async def update_student(student: UpdateStudent):
    return {"message": "Student updated"}

@router.get("/students/{student_id}", status_code=status.HTTP_200_OK)
async def get_student_by_id(student_id: str):
    student = next((student for student in students if student.admission_number == student_id), None)
    if student:
        return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
