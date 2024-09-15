from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()
class GetPayment(BaseModel):
    amount: str
    student_id: str
    payment_date: str
    payment_method: str
    payment_status: str
    
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
def get_payments():
    pass

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

