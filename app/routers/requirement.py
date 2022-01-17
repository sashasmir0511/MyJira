from typing import List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from starlette import status

from app.sql_app.db.database import SessionLocal

from ..sql_app.crud import requirement as crud
from ..sql_app.schemas.requirement import ReturnRequirement
from .depends import get_current_user, is_manager


router = APIRouter(tags=["requirement"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/requirement/{requirement_id}", response_model=ReturnRequirement)
async def get_requirement_by_id(
    requirement_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnRequirement = Depends(get_current_user),
    ):
    db_requirement = crud.get_requirement_by_id(db, requirement_id=requirement_id)
    if not db_requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found"
        )
    return db_requirement
