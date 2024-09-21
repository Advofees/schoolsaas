import decimal
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.database import DatabaseDependency
from backend.models import Exam, ExamResult, ModuleEnrollment,  User
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


@router.get("/school/exam_results/student/{student_id}/list")
def get_exam_results(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    student_id: str,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    exams = db.query(ExamResult).filter(ExamResult.exam_id == student_id).all()
    return exams


@router.get("/school/exam_results/{exam_id}/list")
def get_exam_results_by_student_id(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    exam_id: str,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    exams = db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
    return exams


@router.get(
    "school/exam_results/classromm/{classromm_id}/exam/{exam_id}/academic_term/{academic_term_id}/list"
)
def get_exam_results_for_classroom(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    exam_id: str,
    academic_term_id: str,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    result = (
        db.query(ExamResult)
        .join(Exam)
        .filter(Exam.academic_term_id == academic_term_id, Exam.id == exam_id)
        .all()
    )

    """'
    GET exams results for students in a particular classroom for all modules for a specific term and exam

    | Student | Module 1 | Module 2 | Module 3 | Module 4 | Module 5 | Total | Average | Grade | Position 
    |---------|----------|----------|----------|----------|----------|-------|---------|-------|---------
    | 1       | 50       | 60       | 70       | 80       | 90       | 350   | 70      | A     | 1
    | 2       | 60       | 70       | 80       | 90       | 100      | 400   | 80      | A     | 2
    """


class CreateModuleExamResult(BaseModel):
    student_id: uuid.UUID
    exam_id: uuid.UUID
    class_room_id: uuid.UUID
    module_id: uuid.UUID
    marks_obtained: decimal.Decimal


@router.post("/school/exam_results/create")
def create_exam_results(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    body: CreateModuleExamResult,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_add_exam_results
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    module_enrollment = (
        db.query(ModuleEnrollment)
        .filter(
            ModuleEnrollment.student_id == body.student_id,
            ModuleEnrollment.module_id == body.module_id,
        )
        .first()
    )

    if not module_enrollment:
        raise HTTPException(
            status_code=400, detail="Student is not enrolled in this module")
    
    exam_result = (
        db.query(ExamResult)
        .filter(
            ExamResult.exam_id == body.exam_id,
            ExamResult.class_room_id == body.class_room_id,
            ExamResult.module_id == body.module_id,
        )
        .first()
    )

    if exam_result:
        raise HTTPException(
            status_code=400, detail="Exam result already exists, update instead"
        )

    
    new_exam_result = ExamResult(
        student_id=body.student_id,
        exam_id=body.exam_id,
        module_id=body.module_id,
        class_room_id=body.class_room_id,
        marks_obtained=body.marks_obtained,
    )
    db.add(new_exam_result)
    db.commit()
    return {"detail": "Exam result added successfully"}


class UpdateModuleExamResult(BaseModel):
    exam_id: uuid.UUID
    class_room_id: uuid.UUID
    module_id: uuid.UUID
    marks_obtained: decimal.Decimal


@router.put("/school/exam_results/update")
def update_exam_results(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    body: UpdateModuleExamResult,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_edit_exam_results
        for role in user.roles
        if role.user_permissions
        for permission in role.user_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    exam_result = (
        db.query(ExamResult)
        .filter(
            ExamResult.exam_id == body.exam_id,
            ExamResult.class_room_id == body.class_room_id,
            ExamResult.module_id == body.module_id,
        )
        .first()
    )

    if not exam_result:
        raise HTTPException(
            status_code=400, detail="Exam result does not exist, create instead"
        )

    exam_result.marks_obtained = body.marks_obtained
    db.commit()
    return {"detail": "Exam result updated successfully"}
