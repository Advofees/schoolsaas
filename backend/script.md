```python
from sqlalchemy.orm import Session

def get_overall_results(session: Session, classroom_name: str):
    results = (
        db.query(
            Classroom.name,
            Student.name,
            Exam.name,
            ExamResult.marks_obtained,
            Exam.total_marks,
            (ExamResult.marks_obtained / Exam.total_marks) * 100
        )
        .join(Student.classroom)
        .join(ExamResult.student)
        .join(ExamResult.exam)
        .join(Exam.module)
        .filter(Classroom.name == classroom_name)
        .all()
    )
    
    return results

    ```