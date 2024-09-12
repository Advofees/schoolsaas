from typing import Type,List
from backend.database.base import Base
from backend.models import (Student,School,SchoolStaff,SchoolParent,Inventory,File,
                            Payment,SchoolStaffPermissions,StaffUser,Grade,Teacher,
                            ExamResult,Exam,Classroom,Module,Attendance,
                            AcademicTerm,SchoolParentAssociation,
                            SchoolStudentAssociation,TeacherModuleAssociation)

ALL_MODELS: List[Type[Base]] = [
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