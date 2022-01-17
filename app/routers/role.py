from typing import List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..sql_app.crud import role as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.role import ReturnRole, Role
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager

router = APIRouter(tags=["roles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/roles", response_model=List[ReturnRole])
async def get_all_roles(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_roles(db, limit=limit, skip=skip)


@router.get("/role/{role_id}", response_model=ReturnRole)
async def get_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    role = crud.get_role_by_id(db, role_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.get("/role", response_model=ReturnRole)
async def get_role_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    role = crud.get_role_by_name(db, name=name)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.delete("/role/{role_id}", response_model=ReturnRole)
async def delete_role_by_id(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    role = crud.delete_role_by_id(db, role_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.delete("/role", response_model=ReturnRole)
async def delete_role_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    role = crud.delete_role_by_name(db, name=name)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.post("/role", response_model=ReturnRole)
async def create_role(
    new_role: Role,
    db: Session = Depends(get_db),
#    current_user: ReturnUser = Depends(is_manager),
):
    return crud.create(db, new_role=new_role)


@router.patch("/role/{role_id}", response_model=ReturnRole)
async def update_role(
    role_id: int,
    new_role: Role,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    role = crud.update(db, new_role=new_role, role_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role
