from dotenv import load_dotenv

load_dotenv()

from backend.database.all_models import get_all_models

get_all_models()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---
from backend.user.user_controller import router as authentication_router
from backend.user.permissions.permission_controller import router as permissions_router
from backend.school.school_controller import router as school_router
from backend.teacher.teacher_controller import router as teacher_router
from backend.parent.parent_controller import router as parent_router
from backend.student.student_controllers import router as student_router
from backend.payment.payment_controller import router as payment_router
from backend.lesson_plan.lesson_plan_controller import router as lesson_plan_router
from backend.exam.exam_results.exam_result_controller import (
    router as exam_result_router,
)

# from backend.file.file_controller import router as file_router
from backend.classroom.classroom_controller import router as classroom_router
from backend.attendance.attendance_controllers import router as attendance_router

# ---
app = FastAPI(docs_url="/")

origins = [os.environ["FRONTEND_URL"], os.environ["SECURE_FRONTEND_URL"]]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Authentication-Type"],
)

# ---
app.include_router(authentication_router, tags=["authentication"])
app.include_router(permissions_router, tags=["permissions"])
# ---
app.include_router(school_router, tags=["school"])
app.include_router(teacher_router, tags=["teacher"])
app.include_router(attendance_router, tags=["attendance"])

app.include_router(classroom_router, tags=["classroom"])
app.include_router(exam_result_router, tags=["exam-results"])

app.include_router(parent_router, tags=["parent"])
app.include_router(student_router, tags=["student"])
app.include_router(payment_router, tags=["payment"])
app.include_router(lesson_plan_router, tags=["lesson-plans"])
# app.include_router(file_router)


@app.get("/health", tags=["health"])
def health():
    return {"version": os.environ.get("GIT_COMMIT_SHA")}
