from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..sql_app.crud import project as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.project import ProjectCreate, ProjectEdit, ReturnProject
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager

router = APIRouter(tags=["projects"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/project/{project_id}", response_model=ReturnProject)
async def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    db_project = crud.get_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.get("/project", response_model=ReturnProject)
async def get_project_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    db_project = crud.get_project_by_name(db, name=name)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.delete("/project/{project_id}", response_model=ReturnProject)
async def delete_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_project = crud.delete_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.delete("/project", response_model=ReturnProject)
async def delete_project_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_project = crud.delete_project_by_name(db, name=name)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.get("/projects", response_model=List[ReturnProject])
async def task_projects(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_projects(db, skip=skip, limit=limit)


@router.post("/project", response_model=ReturnProject)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    return crud.create_project(db=db, new_project=project, creator_id=current_user.id)


@router.patch("/project/{project_id}", response_model=ReturnProject)
async def edit_project(
    project_id: int,
    project: ProjectEdit,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    db_project = crud.edit_project(db, project_id=project_id, new_project=project)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return db_project
