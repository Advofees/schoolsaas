from fastapi import APIRouter

router= APIRouter()


# class
# subject
# age range of the students
# specific learning objectives
# general learning objectives
# materials needed
# activities
# assessment
# evaluation
# homework
# notes
# date
# time
# topics
@router.get("/lesson_plan/create")
def create_lesson_plan():
    return {"lesson_plan": "Lesson Plan"}

@router.put("/lesson_plan/update/{lesson_plan_id}")
def update_lesson_plan():
    return {"lesson_plan": "Lesson Plan"}

@router.delete("/lesson_plan/delete/{lesson_plan_id}")
def delete_lesson_plan():
    return {"lesson_plan": "Lesson Plan"}

@router.get("/lesson_plan/generate/")
def generate_lesson_plan():
    return {"lesson_plan": "Lesson Plan"}