from typing import Type
from backend.database.base import Base
from backend.user.user_models import (
    UserPermission,
    User,
    UserPermissionAssociation,
    UserRoleAssociation,
    UserSession,
    Role,
    RolePermissionAssociation,
)
from backend.school.school_model import (
    School,
    SchoolParent,
    SchoolParentAssociation,
    SchoolStudentAssociation,
)
from backend.parent.parent_model import ParentStudentAssociation
from backend.file.file_model import File
from backend.student.student_model import Student
from backend.parent.parent_model import ParentStudentAssociation
from backend.inventory.inventory_model import Inventory
from backend.teacher.teacher_model import (
    Teacher,
    TeacherModuleAssociation,
    ClassTeacherAssociation,
)
from backend.payment.payment_model import Payment
from backend.attendance.attendance_models import Attendance
from backend.classroom.classroom_model import Classroom
from backend.academic_term.academic_term_model import AcademicTerm
from backend.module.module_model import Module, ModuleEnrollment
from backend.exam.exam_model import Exam
from backend.exam.exam_results.exam_result_model import ExamResult
from backend.calendar_events.calendar_events_model import CalendarEvent
from backend.timetable.timetable_model import TimeSlot, Timetable


def get_all_models() -> list[Type[Base]]:
    return [
        School,
        Student,
        SchoolParent,
        ParentStudentAssociation,
        Teacher,
        Classroom,
        Module,
        ModuleEnrollment,
        Attendance,
        AcademicTerm,
        Exam,
        ExamResult,
        SchoolParentAssociation,
        SchoolStudentAssociation,
        Inventory,
        File,
        Payment,
        TeacherModuleAssociation,
        ClassTeacherAssociation,
        UserPermission,
        UserPermissionAssociation,
        RolePermissionAssociation,
        User,
        UserSession,
        UserRoleAssociation,
        Role,
        TimeSlot,
        Timetable,
        CalendarEvent,
    ]
