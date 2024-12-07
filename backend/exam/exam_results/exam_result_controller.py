import datetime
import decimal
import typing
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.database import DatabaseDependency

from backend.exam.exam_results.exam_result_model import ExamResult
from backend.user.user_models import User
from backend.module.module_model import ModuleEnrollment

from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


class ExamResultResponseModel(BaseModel):
    id: uuid.UUID
    marks_obtained: decimal.Decimal
    comments: typing.Optional[str]
    created_at: datetime.datetime
    updated_at: typing.Optional[datetime.datetime]
    exam_id: uuid.UUID
    student_id: uuid.UUID
    class_room_id: uuid.UUID
    module_id: uuid.UUID
    percentage: float
    grade_obtained: str


def exam_result_response(exam_result: ExamResult) -> dict:
    return {
        "id": exam_result.id,
        "marks_obtained": exam_result.marks_obtained,
        "comments": exam_result.comments,
        "created_at": exam_result.created_at,
        "updated_at": exam_result.updated_at,
        "exam_id": exam_result.exam_id,
        "student_id": exam_result.student_id,
        "class_room_id": exam_result.class_room_id,
        "module_id": exam_result.module_id,
        "module_name": exam_result.get_module_name,
        "percentage": exam_result.percentage,
        "grade_obtained": exam_result.grade_obtained,
    }


@router.get("/school/student/classroom/{classroom_id}/{exam_id}")
def get_module_exam_result_for_classroom(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    classroom_id: uuid.UUID,
    exam_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    exam_results = (
        db.query(ExamResult)
        .filter(ExamResult.class_room_id == classroom_id, ExamResult.exam_id == exam_id)
        .all()
    )
    results = [exam_result_response(result) for result in exam_results]

    return results


@router.get("/school/student/classroom/{classroom_id}/{exam_id}/{student_id}")
def get_module_exam_result_for_student_in_a_classroom(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    classroom_id: uuid.UUID,
    exam_id: uuid.UUID,
    student_id: uuid.UUID,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    exam_results = (
        db.query(ExamResult)
        .filter(
            ExamResult.class_room_id == classroom_id,
            ExamResult.exam_id == exam_id,
            ExamResult.student_id == student_id,
        )
        .all()
    )
    results = [exam_result_response(result) for result in exam_results]

    return results


@router.get("/school/student/module/exam_result/{student_id}/{exam_id}/{module_id}")
def get_specific_module_exam_results_for_student(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    student_id: uuid.UUID,
    exam_id: uuid.UUID,
    module_id: uuid.UUID,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    exam_result = (
        db.query(ExamResult)
        .filter(
            ExamResult.exam_id == exam_id,
            ExamResult.module_id == module_id,
            ExamResult.student_id == student_id,
        )
        .all()
    )
    return exam_result


@router.get("/school/exam/{exam_id}/exam_results")
def get_exam_results_by_student_id(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    exam_id: str,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(
        permission.permissions.exam_result_permissions.can_view_exam_results is True
        for permission in user.all_permissions
    ):
        raise HTTPException(status_code=403, detail="Permission denied")

    exams = db.query(ExamResult).filter(ExamResult.exam_id == exam_id).all()
    return exams


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
        permission.permissions.exam_result_permissions.can_add_exam_results is True
        for permission in user.all_permissions
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
            status_code=400, detail="Student is not enrolled in this module"
        )

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
    return {"message": "Exam result added successfully"}


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
        permission.permissions.exam_result_permissions.can_edit_exam_results is True
        for permission in user.all_permissions
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
    return {"message": "Exam result updated successfully"}
