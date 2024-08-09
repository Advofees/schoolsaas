
import jwt
import os
import uuid
from pydantic import BaseModel
from backend.database.database import DatabaseDependency
from dataclasses import dataclass

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

@dataclass
class AccountantUserAuthenticationContext:
    school_admin_user_id: uuid.UUID #points to id in session
    school_admin_id: uuid.UUID # points to the id the school table


class JWTPayload(BaseModel):
    session_id: str
