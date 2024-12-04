from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from backend.database.database import DatabaseDependency
from backend.user.user_models import User
from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


class CreatePayment(BaseModel):
    amount: str
    student_id: str
    payment_date: str
    payment_method: str
    payment_status: str


class UpdatePayment(BaseModel):
    amount: str
    student_id: str
    payment_date: str
    payment_method: str
    payment_status: str


@router.get("/payment/list")
def get_payments(
    db: DatabaseDependency, auth_context: UserAuthenticationContextDependency
):

    user = db.query(User).filter(User.id == auth_context.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/payment/create")
def create_payment():
    pass


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
