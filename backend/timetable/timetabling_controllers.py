from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import datetime
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.user_models import User, RoleType

from backend.user.user_models import User


from backend.exam.exam_model import Exam

from backend.calendar_events.calendar_events_model import CalendarEvent
from backend.timetable.timetable_model import DayOfWeek, TimeSlot, Timetable


class TimeSlotCreate(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    day_of_week: DayOfWeek
    module_id: uuid.UUID
    teacher_id: uuid.UUID
    classroom_id: uuid.UUID


class TimetableCreate(BaseModel):
    name: str
    academic_year: str
    grade_level: int
    academic_term_id: uuid.UUID


class CalendarEventCreate(BaseModel):
    title: str
    description: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    is_recurring: bool
    recurrence_rule: str
    module_id: uuid.UUID
    classroom_id: uuid.UUID


class TimeSlotResponse(BaseModel):
    id: uuid.UUID
    start_time: datetime.datetime
    end_time: datetime.datetime
    day_of_week: str
    module_name: str
    teacher_name: str
    classroom_name: str


class TimetableResponse(BaseModel):
    id: uuid.UUID
    name: str
    academic_year: str
    grade_level: int
    time_slots: list[TimeSlotResponse]


router = APIRouter()


@router.post("/schools/{school_id}/timetables")
async def create_school_timetable(
    school_id: uuid.UUID,
    timetable_data: TimetableCreate,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    """Create a new timetable for a school."""
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Not authorized")

    timetable = Timetable(
        school_id=school_id,
        academic_term_id=timetable_data.academic_term_id,
        grade_level=timetable_data.grade_level,
        name=timetable_data.name,
        academic_year=timetable_data.academic_year,
    )
    db.add(timetable)
    db.commit()
    return timetable


@router.get("/schools/{school_id}/timetables")
async def get_school_timetables(
    school_id: uuid.UUID,
    grade_level: int,
    academic_term_id: uuid.UUID,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)
    query = db.query(Timetable).filter(Timetable.school_id == school_id)

    if grade_level is not None:
        query = query.filter(Timetable.grade_level == grade_level)
    if academic_term_id:
        query = query.filter(Timetable.academic_term_id == academic_term_id)

    return query.all()


@router.post("/timetables/{timetable_id}/slots", response_model=TimeSlotResponse)
async def add_timetable_slot(
    timetable_id: uuid.UUID,
    body: TimeSlotCreate,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_slots = (
        db.query(TimeSlot)
        .filter(
            TimeSlot.day_of_week == body.day_of_week,
            TimeSlot.timetable_id == timetable_id,
            TimeSlot.end_time > body.start_time,
            TimeSlot.start_time < body.end_time,
        )
        .filter(
            (TimeSlot.classroom_id == body.classroom_id)
            | (TimeSlot.teacher_id == body.teacher_id)
        )
        .count()
    )
    if existing_slots > 0:
        raise HTTPException(
            status_code=400, detail="Time slot conflicts with existing schedule"
        )
    time_slot = TimeSlot(
        start_time=body.start_time,
        end_time=body.end_time,
        day_of_week=body.day_of_week,
        timetable_id=timetable_id,
        module_id=body.module_id,
        teacher_id=body.teacher_id,
        classroom_id=body.classroom_id,
    )
    db.add(time_slot)
    db.commit()


@router.get("/teachers/{teacher_id}/schedule")
async def get_teacher_timetable(
    teacher_id: uuid.UUID,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(404)

    time_slots = db.query(TimeSlot).filter(TimeSlot.teacher_id == teacher_id).all()

    schedule = []
    current_date = start_date
    while current_date <= end_date:
        day_of_week = DayOfWeek(current_date.strftime("%A").lower())
        day_slots = [slot for slot in time_slots if slot.day_of_week == day_of_week]

        for slot in day_slots:
            schedule.append(
                {
                    "date": current_date.date(),
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                    "module": slot.module.name,
                    "classroom": slot.classroom.name,
                }
            )

        current_date += datetime.timedelta(days=1)


# Calendar endpoints
@router.post("/schools/{school_id}/calendar-events")
async def create_calendar_event(
    school_id: uuid.UUID,
    event_data: CalendarEventCreate,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)
    event = CalendarEvent(
        title=event_data.title,
        description=event_data.description,
        start_datetime=event_data.start_datetime,
        end_datetime=event_data.end_datetime,
        is_recurring=event_data.is_recurring,
        recurrence_rule=event_data.recurrence_rule,
        school_id=school_id,
        creator_id=user.id,
        module_id=event_data.module_id,
        classroom_id=event_data.classroom_id,
    )
    db.add(event)
    db.commit()
    return event


@router.get("/schools/{school_id}/calendar-events")
async def get_school_events(
    school_id: uuid.UUID,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    classroom_id: uuid.UUID,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(404)

    school_events = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.school_id == school_id,
            CalendarEvent.start_datetime >= start_date,
            CalendarEvent.end_datetime <= end_date,
        )
        .filter(CalendarEvent.classroom_id == classroom_id)
        .all()
    )
    return school_events


class TimetableEventGeneration(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime


@router.post("/timetables/{timetable_id}/generate-events")
async def generate_timetable_events(
    timetable_id: uuid.UUID,
    event_params: TimetableEventGeneration,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)

    if not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(status_code=403, detail="Not authorized")

    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")

    # events = []
    # time_slots = timetable.time_slots

    # for slot in time_slots:

    #     event = CalendarEvent(
    #         title=f"{slot.module.name} - {slot.classroom.name}",
    #         description=f"Teacher: {slot.teacher.first_name} {slot.teacher.last_name}",
    #         start_datetime=datetime.datetime.combine(
    #             event_params.start_date.date(), slot.start_time
    #         ),
    #         end_datetime=datetime.datetime.combine(
    #             event_params.start_date.date(), slot.end_time
    #         ),
    #         is_recurring=True,
    #         recurrence_rule=f"FREQ=WEEKLY;BYDAY={slot.day_of_week.value[:2].upper()};UNTIL={event_params.end_date.strftime('%Y%m%d')}",
    #         school_id=timetable.school_id,
    #         creator_id=slot.teacher.user_id,
    #         module_id=slot.module_id,
    #         classroom_id=slot.classroom_id,
    #     )
    #     db.add(event)
    #     events.append(event)

    # db.commit()
    # return events


@router.post("/exams/{exam_id}/schedule")
async def schedule_exam(
    exam_id: uuid.UUID,
    school_id: uuid.UUID,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404)

    if not user.has_role_type(RoleType.TEACHER):
        raise HTTPException(status_code=403, detail="Not authorized")

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    event = CalendarEvent(
        title=f"Exam: {exam.name} - {exam.module.name}",
        description=f"Total Marks: {exam.total_marks}",
        start_datetime=exam.date,
        end_datetime=exam.date + datetime.timedelta(hours=2),
        school_id=school_id,
        creator_id=user.id,
        module_id=exam.module_id,
    )
    db.add(event)
    db.commit()
    return event
