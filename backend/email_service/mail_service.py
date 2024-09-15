import resend
from pydantic import BaseModel
import os
from typing import Annotated
from fastapi import Depends


resend.api_key = os.environ.get("EMAIL_SERVICE_API_KEY")
EMAIL_DOMAIN = os.environ.get("EMAIL_DOMAIN")



class SendEmailParams(BaseModel):
    email: str
    subject: str
    message: str

def send_mail(body: SendEmailParams) -> resend.Email:
    params = {
        "from": f"donotreply@{EMAIL_DOMAIN}",
        "to": [f"{body.email}"],
        "subject": f"{body.subject}",
        "html": f"<strong>{body.message}</strong>",
    }
    email = resend.Emails.send(params)
    return email


class EmailService:
    def send(self, body: SendEmailParams) -> resend.Email:
        return send_mail(body)


def get_email_service() -> EmailService:
    return EmailService()


EmailServiceDependency = Annotated[EmailService, Depends(get_email_service)]
