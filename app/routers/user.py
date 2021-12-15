from typing import List

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..sql_app.crud import team_member as team_member_crud
from ..sql_app.crud import user as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.user import ReturnUser, UserIn
from .depends import get_current_user, is_manager

router = APIRouter(tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users", response_model=List[ReturnUser])
async def get_all_users(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_users(db, limit=limit, skip=skip)


@router.get("/user/{user_id}", response_model=ReturnUser)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    result = crud.get_user_by_id(db, user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.get("/user", response_model=ReturnUser)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    result = crud.get_by_email(db, email)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.delete("/user/{user_id}", response_model=ReturnUser)
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    result = crud.delete_user_by_id(db, user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.delete("/user", response_model=ReturnUser)
async def delete_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    result = crud.delete_by_email(db, email)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.patch("/user/{user_id}", response_model=ReturnUser)
async def update_user(
    user_id: int,
    user: UserIn,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    error = HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    old_user = crud.get_user_by_id(db, user_id=user_id)
    if old_user is None:
        raise error

    team_member = team_member_crud.get_team_member_by_user_name(db, current_user.name)
    if team_member is None or (
        not team_member.is_manager and old_user.email != current_user.email
    ):
        raise error

    result = crud.update_user(db, user_id=user_id, new_user=user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.post("/user", response_model=ReturnUser)
async def create_user(
    user: UserIn,
    db: Session = Depends(get_db),
):
    result = crud.create_user(db, user)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result
