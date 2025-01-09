import uuid
from fastapi import APIRouter

from backend.database.database import DatabaseDependency


from backend.user.user_authentication import UserAuthenticationContextDependency

router = APIRouter()


@router.get("/academic-terms/by-school-id/list")
def get_school_academic_terms(
    db: DatabaseDependency, auth_context: UserAuthenticationContextDependency
):
    pass


@router.get("/academic-terms/by-academic-term-id/{academic_term_id}")
def get_school_academic_term_id(
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
    academic_term_id: uuid.UUID,
):
    pass
