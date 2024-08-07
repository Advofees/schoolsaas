from pydantic import BaseModel

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

class DeletePayment(BaseModel):
    payment_id: str

