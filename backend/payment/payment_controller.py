import decimal
import typing
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Query as SQLQUERY
from sqlalchemy import asc, desc
import datetime
from backend.database.database import DatabaseDependency
from backend.user.user_models import RoleType, User
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.payment.payment_model import Payment, PaymentMethod, PaymentStatus

router = APIRouter()


@router.get("/payment/list")
def get_payments(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    sort_by: typing.Literal["date", "amount", "status", "method", "created_at"],
    sort_order: typing.Literal["asc", "desc"],
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
    min_amount: decimal.Decimal | None = None,
    max_amount: decimal.Decimal | None = None,
    payment_method: PaymentMethod | None = None,
    payment_status: PaymentStatus | None = None,
    teacher_id: uuid.UUID | None = None,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user or not user.has_role_type(RoleType.SCHOOL_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    query = db.query(Payment).filter(Payment.school_id == user.school_id)

    if start_date:
        query = query.filter(Payment.date >= start_date)
    if end_date:
        query = query.filter(Payment.date <= end_date)
    if min_amount is not None:
        query = query.filter(Payment.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Payment.amount <= max_amount)
    if payment_method:
        query = query.filter(Payment.method == payment_method)
    if payment_status:
        query = query.filter(Payment.status == payment_status)
    if teacher_id:
        query = query.filter(Payment.teacher_id == teacher_id)

    if sort_by:
        query = apply_sort(query, sort_by, sort_order)

    payments: list[Payment] = query.offset(offset).limit(limit).all()

    return payments


def apply_sort(
    query: SQLQUERY[Payment], sort_by: str, sort_order: str
) -> SQLQUERY[Payment]:
    valid_sort_fields = {
        "date": Payment.date,
        "amount": Payment.amount,
        "status": Payment.status,
        "method": Payment.method,
        "created_at": Payment.created_at,
    }

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field. Valid options are: {', '.join(valid_sort_fields.keys())}",
        )

    sort_field = valid_sort_fields[sort_by]
    return query.order_by(desc(sort_field) if sort_order == "desc" else asc(sort_field))


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
def delete_payment():
    pass


@router.get("/payment/payment-id/{payment_id}")
def get_payment_by_id():
    pass


@router.get("/payment/student-id/{student_id}")
def get_payment_by_student_id():
    pass
