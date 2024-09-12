from typing import Type
from backend.database.base import Base
from backend.models import (Student,School,SchoolStaff,SchoolParent,Inventory,File,
                            Payment,SchoolStaffPermissions,StaffUser,Grade,Teacher,
                            ExamResult,Exam,Classroom,Module,Attendance,
                            AcademicTerm,SchoolParentAssociation,
                            SchoolStudentAssociation,TeacherModuleAssociation)

def get_all_models() -> list[Type[Base]]: return [
    Student,
    School,
    SchoolStaff,
    SchoolParent,
    Inventory,
    File,
    Payment,
    SchoolStaffPermissions,
    StaffUser,
    Grade,
    Teacher,
    ExamResult,
    Exam,
    Classroom,
    Module,
    Attendance,
    AcademicTerm,
    SchoolParentAssociation,
    SchoolStudentAssociation,
    TeacherModuleAssociation
]