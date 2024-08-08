from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#---
from backend.authentication.authentication_controller import router as authentication_router
from backend.school.school_controller import router as school_router
from backend.teacher.teacher_controller import router as teacher_router
from backend.parent.parent_controller import router as parent_router
from backend.student.student_controllers import router as student_router
from backend.payment.payment_controller import router as payment_router
from backend.file.file_controller import router as file_router
from backend.lesson_plan.lesson_plan_controller import router as lesson_plan_router



#---
app = FastAPI(docs_url="/")

origins = [os.environ["FRONTEND_URL"]]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Authentication-Type"],
)

#---
app.include_router(authentication_router,tags=["Authentication"])
#---
app.include_router(school_router,tags=["School"])
app.include_router(teacher_router,tags=["Teacher"])
app.include_router(parent_router,tags=["Parent"])
app.include_router(student_router,tags=["Student"])
app.include_router(payment_router,tags=["Payment"])
app.include_router(file_router,tags=["File"])
app.include_router(lesson_plan_router,tags=["Lesson Plans"])


@app.get("/health")
def health():

    return {"version": os.environ.get("GIT_COMMIT_SHA")}
