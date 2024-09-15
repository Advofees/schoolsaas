import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.database.database import DatabaseDependency
from backend.models import Classroom, ParentStudentAssociation, SchoolParent, Student, User
from backend.user.user_authentication import UserAuthenticationContextDependency
router = APIRouter()


class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    parent_id:str
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    classroom_id:uuid.UUID



@router.post("/students/create")
async def create_student(db:DatabaseDependency,body: CreateStudent,auth_context: UserAuthenticationContextDependency):
    
    user= db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)
    
    parent = db.query(SchoolParent).filter(SchoolParent.id == body.parent_id).first()

    if not parent :
        raise HTTPException(status_code=404, detail="Parent  not found")
    
    class_room=db.query(Classroom).filter(Classroom.id == body.classroom_id).first()

    if not class_room:
        raise HTTPException(status_code=404, detail="Classroom not found")
    #--
    if not any(
        permission.permissions.student_permissions.can_add_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    student = Student(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        grade_level=body.grade_level,
        classroom_id=class_room.id

    )

    db.add(student)
    db.flush()
    # ---
    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id,
        student_id=student.id
    )
    db.add(parent_student_association)
    db.flush()
    db.commit()

    return {}

