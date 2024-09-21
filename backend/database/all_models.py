from typing import Type
from backend.database.base import Base
from backend.models import (
    Student,
    School,
    SchoolParent,
    Inventory,
    File,
    Payment,
    UserPermission,
    User,
    Teacher,
    ExamResult,
    Exam,
    Classroom,
    Module,
    Attendance,
    AcademicTerm,
    SchoolParentAssociation,
    SchoolStudentAssociation,
    TeacherModuleAssociation,
    Role,
    RolePermissionAssociation,
    UserRoleAssociation,
    ModuleEnrollment
)


def get_all_models() -> list[Type[Base]]:
    return [
        Student,
        School,
        SchoolParent,
        Inventory,
        File,
        Payment,
        UserPermission,
        User,
        Teacher,
        ExamResult,
        Exam,
        Classroom,
        Module,
        Attendance,
        AcademicTerm,
        SchoolParentAssociation,
        SchoolStudentAssociation,
        TeacherModuleAssociation,
        Role,
        RolePermissionAssociation,
        UserRoleAssociation,
        ModuleEnrollment
    ]
