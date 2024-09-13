from pydantic import BaseModel


class StudentPermissions(BaseModel):
    can_add_students: bool = False
    can_edit_students: bool = False
    can_view_students: bool = False
    can_delete_students: bool = False
    
class ParentPermissions(BaseModel):
    can_add_parents: bool = False
    can_edit_parents: bool = False
    can_view_parents: bool = False
    can_delete_parents: bool = False
    
class ClassPermissions(BaseModel):
    can_manage_classes: bool = False
    can_view_classes: bool = False
    can_add_classes: bool = False
    can_edit_classes: bool = False
    can_delete_classes: bool = False
    
class TeacherPermissions(BaseModel):
    can_add_teachers: bool = False
    can_edit_teachers: bool = False
    can_view_teachers: bool = False
    can_delete_teachers: bool = False
    
class GradePermissions(BaseModel):
    can_add_grades: bool = False
    can_edit_grades: bool = False
    can_view_grades: bool = False
    can_delete_grades: bool = False
    
class AttendancePermissions(BaseModel):
    can_view_attendance: bool = False
    can_manage_attendance: bool = False
    
class ReportPermissions(BaseModel):
    can_view_reports: bool = False
    can_generate_reports: bool = False
    
class FeeManagementPermissions(BaseModel):
    can_manage_fees: bool = False
    can_view_fees: bool = False
    
class LibraryPermissions(BaseModel):
    can_manage_library: bool = False
    can_borrow_books: bool = False
    can_view_library: bool = False
    
class TimetablePermissions(BaseModel):
    can_manage_timetable: bool = False
    can_view_timetable: bool = False
    
class SchoolEventPermissions(BaseModel):
    can_manage_school_events: bool = False
    can_view_school_events: bool = False
    

class ALL_KNOWN_PERMISSIONS(BaseModel):
    student_permissions: StudentPermissions = StudentPermissions()
    parent_permissions: ParentPermissions = ParentPermissions()
    class_permissions: ClassPermissions = ClassPermissions()
    teacher_permissions: TeacherPermissions = TeacherPermissions()
    grade_permissions: GradePermissions = GradePermissions()
    attendance_permissions: AttendancePermissions = AttendancePermissions()
    report_permissions: ReportPermissions = ReportPermissions()
    fee_management_permissions: FeeManagementPermissions = FeeManagementPermissions()
    library_permissions: LibraryPermissions = LibraryPermissions()
    timetable_permissions: TimetablePermissions = TimetablePermissions()
    school_event_permissions: SchoolEventPermissions = SchoolEventPermissions()
    
    @classmethod
    def validate_permissions(cls, permissions: dict):
        return cls(**permissions)