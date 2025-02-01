import decimal
import typing
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_, asc, desc
from sqlalchemy.orm import Query as SQLQUERY
import datetime
from backend.database.database import DatabaseDependency
from backend.teacher.teacher_model import Teacher
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.payment.payment_model import (
    Payment,
    PaymentCategory,
    PaymentDirection,
    PaymentMethod,
    PaymentStatus,
    PaymentUserAssociation,
    PaymentUserType,
)
from backend.user.user_models import RoleType, User
from backend.student.student_model import Student

router = APIRouter()


def get_user_type(user: User) -> str:
    if user.student_user:
        return "student"
    elif user.teacher_user:
        return "teacher"
    elif user.school_parent_user:
        return "parent"
    elif user.school_user:
        return "school"
    else:
        raise Exception()


def apply_sort(query: SQLQUERY, sort_by: str, sort_order: str) -> SQLQUERY:
    sort_mapping = {
        "date": Payment.date,
        "amount": Payment.amount,
        "status": Payment.status,
        "method": Payment.method,
        "created_at": Payment.created_at,
    }

    sort_column = sort_mapping.get(sort_by)
    if not sort_column:
        return query

    return query.order_by(
        desc(sort_column) if sort_order == "desc" else asc(sort_column)
    )


def to_user_dto(user: User) -> dict:
    return {"name": user.name, "email": user.email, "id": user.id}


@router.get("/payment/search")
def search_payments(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    offset: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="payments per page"),
    sort_by: typing.Literal[
        "date", "amount", "status", "method", "created_at"
    ] = "date",
    sort_order: typing.Literal["asc", "desc"] = "desc",
    search: typing.Optional[str] = Query(
        None,
        min_length=1,
        description="Search term for reference number, description, or user name",
    ),
    start_date: typing.Optional[datetime.datetime] = Query(
        None, description="Filter by start date"
    ),
    end_date: typing.Optional[datetime.datetime] = Query(
        None, description="Filter by end date"
    ),
    min_amount: typing.Optional[decimal.Decimal] = Query(
        None, ge=0, description="Minimum amount"
    ),
    max_amount: typing.Optional[decimal.Decimal] = Query(
        None, ge=0, description="Maximum amount"
    ),
    payment_method: typing.Optional[PaymentMethod] = Query(
        None, description="Filter by payment method"
    ),
    payment_status: typing.Optional[PaymentStatus] = Query(
        None, description="Filter by payment status"
    ),
    payment_category: typing.Optional[PaymentCategory] = Query(
        None, description="Filter by payment category"
    ),
    payment_direction: typing.Optional[PaymentDirection] = Query(
        None, description="Filter by payment direction"
    ),
    payee_user_id: typing.Optional[uuid.UUID] = Query(
        None, description="Filter by related user ID"
    ),
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user or not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view payments",
        )

    query = (
        db.query(Payment)
        .join(PaymentUserAssociation)
        .join(User)
        .outerjoin(Student)
        .outerjoin(Teacher)
        .filter(Payment.school_id == user.school_id)
        .options(
            joinedload(Payment.users)
            .joinedload(PaymentUserAssociation.user)
            .joinedload(User.student_user),
            joinedload(Payment.users)
            .joinedload(PaymentUserAssociation.user)
            .joinedload(User.teacher_user),
        )
    )

    if search:
        search_filter = or_(
            Payment.reference_number.ilike(f"%{search}%"),
            Payment.description.ilike(f"%{search}%"),
            Student.first_name.ilike(f"%{search}%"),
            Student.last_name.ilike(f"%{search}%"),
            Teacher.first_name.ilike(f"%{search}%"),
            Teacher.last_name.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    if start_date:
        query = query.filter(Payment.date >= start_date)
    if end_date:
        query = query.filter(Payment.date <= end_date)
    if min_amount is not None:
        query = query.filter(Payment.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Payment.amount <= max_amount)
    if payment_method:
        query = query.filter(Payment.method == payment_method.value)
    if payment_status:
        query = query.filter(Payment.status == payment_status.value)
    if payment_category:
        query = query.filter(Payment.category == payment_category.value)
    if payment_direction:
        query = query.filter(Payment.direction == payment_direction.value)

    if payee_user_id:
        query = query.filter(
            and_(
                PaymentUserAssociation.user_id == payee_user_id,
                PaymentUserAssociation.type == PaymentUserType.RELATED.value,
            )
        )

    # total = query.count()

    query = apply_sort(query, sort_by, sort_order)

    offset = (offset - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    payments = query.all()

    def transform_payment(payment: Payment) -> dict:
        return {
            "id": payment.id,
            "amount": payment.amount,
            "date": payment.date,
            "method": payment.method,
            "direction": payment.direction,
            "category": payment.category,
            "description": payment.description,
            "payee": (to_user_dto(payment.payee) if payment.payee else None),
            "payment_recorder": (
                to_user_dto(payment.recorded_by) if payment.recorded_by else None
            ),
        }

    # total_pages = (total + limit - 1) // limit

    return (transform_payment(payment) for payment in payments)


class createPayment(BaseModel):
    amount: str
    student_id: uuid.UUID
    payment_date: str
    payment_method: PaymentMethod
    payment_status: PaymentStatus


@router.post("/payment/create")
def create_payment(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    body: createPayment,
):
    pass


class UpdatePayment(BaseModel):
    amount: str
    student_id: str
    payment_date: str
    payment_method: PaymentMethod
    payment_status: PaymentStatus


@router.put("/payment/update")
def update_payment():
    pass


@router.delete("/payment/delete/{payment_id}")
def delete_payment(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    payment_id: uuid.UUID,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user or not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete payments",
        )

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.school_id == user.school_id)
        .first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted successfully"}
