import datetime
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_

from backend.database.database import DatabaseDependency
from backend.models import (
    Classroom,
    ParentStudentAssociation,
    School,
    SchoolParent,
    Student,
    User,
)
from backend.user.user_authentication import UserAuthenticationContextDependency
from sqlalchemy import select, func, and_

from typing import Optional
from fastapi import Query


router = APIRouter()


class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    parent_id: uuid.UUID
    date_of_birth: datetime.datetime
    gender: str
    grade_level: int
    classroom_id: uuid.UUID


@router.post("/students/create")
async def create_student(
    db: DatabaseDependency,
    body: CreateStudent,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    parent = db.query(SchoolParent).filter(SchoolParent.id == body.parent_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Parent  not found")

    class_room = db.query(Classroom).filter(Classroom.id == body.classroom_id).first()

    if not class_room:
        raise HTTPException(status_code=404, detail="Classroom not found")
    # --
    if not any(
        permission.permissions.student_permissions.can_add_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    # ---
    student_user = User(
        email=body.first_name + body.last_name + "@student.com",
        username=body.first_name + body.last_name,
        password_hash="student",
    )
    db.add(student_user)
    student = Student(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        grade_level=body.grade_level,
        classroom_id=class_room.id,
        user_id=student_user.id,
    )

    db.add(student)
    db.flush()
    # ---
    parent_student_association = ParentStudentAssociation(
        parent_id=body.parent_id, student_id=student.id
    )
    db.add(parent_student_association)
    db.flush()
    db.commit()

    return {}


@router.get("/students/{student_id}")
async def get_student(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    return student


@router.get("/students/{student_id}/parents")
async def get_student_parents(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    if not any(
        permission.permissions.parent_permissions.can_view_parents
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    parents = (
        db.query(SchoolParent)
        .join(ParentStudentAssociation)
        .filter(ParentStudentAssociation.student_id == student_id)
        .all()
    )

    return parents


@router.get("/students/{student_id}/classroom")
async def get_student_classroom(
    db: DatabaseDependency,
    student_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if not any(
        permission.permissions.student_permissions.can_view_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    classroom = db.query(Classroom).filter(Classroom.id == student.classroom_id).first()

    return classroom


@router.get("/students/{class_room_id}")
async def get_students_in_classroom(
    db: DatabaseDependency,
    class_room_id: uuid.UUID,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=403)

    class_room = db.query(Classroom).filter(Classroom.id == class_room_id).first()

    if not class_room:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if not any(
        permission.permissions.student_permissions.can_view_students
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    students = db.query(Student).filter(Student.classroom_id == class_room_id).all()

    return students


class StudentSearchParams(BaseModel):
    search_term: Optional[str] = None
    student_id: Optional[uuid.UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    grade_level_min: Optional[int] = None
    grade_level_max: Optional[int] = None
    date_of_birth_start: Optional[datetime.date] = None
    date_of_birth_end: Optional[datetime.date] = None


@router.get("/school/search/advanced-search")
async def advanced_search_students_feat(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    search_term: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    grade_level_min: Optional[int] = Query(None),
    grade_level_max: Optional[int] = Query(None),
    date_of_birth_start: Optional[datetime.date] = Query(None),
    date_of_birth_end: Optional[datetime.date] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
):
    params = StudentSearchParams(
        search_term=search_term,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        grade_level_min=grade_level_min,
        grade_level_max=grade_level_max,
        date_of_birth_start=date_of_birth_start,
        date_of_birth_end=date_of_birth_end,
    )

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(status_code=403)
    user_school_ids = [assoc.school_id for assoc in user.school_user.school_parent_associations]

    conditions = []
    if params.search_term:
        conditions.append(
            or_(
                Student.first_name.ilike(f"%{params.search_term}%"),
                Student.last_name.ilike(f"%{params.search_term}%"),
                func.similarity(Student.first_name, params.search_term) > 0.1,
                func.similarity(Student.last_name, params.search_term) > 0.1,
            )
        )
    if params.student_id:
        conditions.append(Student.id == params.student_id)
    if params.first_name:
        conditions.append(Student.first_name.ilike(f"%{params.first_name}%"))
    if params.last_name:
        conditions.append(Student.last_name.ilike(f"%{params.last_name}%"))
    if params.gender:
        conditions.append(Student.gender == params.gender)
    if params.grade_level_min is not None:
        conditions.append(Student.grade_level >= params.grade_level_min)
    if params.grade_level_max is not None:
        conditions.append(Student.grade_level <= params.grade_level_max)
    if params.date_of_birth_start:
        conditions.append(Student.date_of_birth >= params.date_of_birth_start)
    if params.date_of_birth_end:
        conditions.append(Student.date_of_birth <= params.date_of_birth_end)

    query = select(Student)
    if conditions:
        query = query.filter(
            and_(*conditions),
             Student.schools.any(School.id.in_(user_school_ids)),
        )

    query = query.order_by(Student.last_name, Student.first_name)
    query = query.offset(offset).limit(limit)

    result = db.execute(query)
    students = result.scalars().all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found")

    return students
