from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.database.database_constants import DATABASE_URL


SQLAlchemyEngine = create_engine(DATABASE_URL)
SQLAlchemySessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=SQLAlchemyEngine
)


def get_db():
    return SQLAlchemySessionLocal()


def get_db_from_generator():
    db = SQLAlchemySessionLocal()
    try:
        yield db
    finally:
        db.close()


DatabaseDependency = Annotated[Session, Depends(get_db_from_generator)]