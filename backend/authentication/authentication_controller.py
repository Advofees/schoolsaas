import enum
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()
class Roles(enum.Enum):
    ADMIN = 'admin'
    PARENT= 'parent'
    TEACHER = 'teacher'
    STUDENT = 'student'
    SCHOOL = 'school'
    USER= 'user'

class Actions(enum.Enum):
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'

class UserSignIn(BaseModel):
    email: str
    password: str

class SchoolSignUp(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    address: str

# school signs up
# school adds one teacher as the school admin
# school admin adds students
# school admin adds parents
# school admin adds teachers
# teachers can create lesson plans
# teachers can create assignments
# teachers can create quizzes
# teachers can create exams
# teachers can create resources

@router.post('/authentication/sign-in')
def sign_in(user: UserSignIn):
    pass

@router.post('/authentication/sign-up/school')
def sign_up_school(school: SchoolSignUp):
    pass