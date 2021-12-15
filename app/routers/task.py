from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.sql_app.db.database import SessionLocal

from ..sql_app.crud import task as crud
from ..sql_app.schemas.task import ReturnTask, TaskCreate, TaskEdit
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager

router = APIRouter(tags=["tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/task/{task_id}", response_model=ReturnTask)
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    db_task = crud.get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.get("/task", response_model=ReturnTask)
async def get_task_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    db_task = crud.get_task_by_name(db, name=name)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.get("/tasks", response_model=List[ReturnTask])
async def task_gets(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_tasks(db, skip=skip, limit=limit)


@router.delete("/task/{task_id}", response_model=ReturnTask)
async def delete_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_task = crud.delete_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.delete("/task", response_model=ReturnTask)
async def delete_task_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_task = crud.delete_task_by_name(db, name=name)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.post("/tasks", response_model=ReturnTask)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    return crud.create_task(db=db, new_task=task, manager_id=current_user.id)


@router.patch("/tasks/{task_id}", response_model=ReturnTask)
async def edit_task(
    task_id: int,
    task: TaskEdit,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_task = crud.edit_task(db=db, new_task=task, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task
