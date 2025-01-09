from fastapi import APIRouter

from backend.database.database import DatabaseDependency


from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()
