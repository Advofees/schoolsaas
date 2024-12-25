from backend.teacher.teacher_model import Teacher


def to_teacher_dto(teacher: Teacher) -> dict:
    return {
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "email": teacher.email,
        "phone_number": teacher.phone_number,
        "user_id": teacher.user_id,
        "created_at": teacher.created_at,
        "updated_at": teacher.updated_at,
    }
