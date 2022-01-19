from typing import List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..sql_app.crud import release as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.release import Release, ReturnRelease
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager

router = APIRouter(tags=["releases"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/releases", response_model=List[ReturnRelease])
async def get_all_releases(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    #current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_releases(db, limit=limit, skip=skip)


@router.get("/release", response_model=ReturnRelease)
async def get_release_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    release = crud.get_release_by_name(db, name=name)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release


@router.get("/release/{release_id}", response_model=ReturnRelease)
async def get_release_by_id(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    release = crud.get_release_by_id(db, release_id=release_id)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release


@router.delete("/release}", response_model=ReturnRelease)
async def delete_release_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    release = crud.delete_release_by_name(db, name=name)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release


@router.delete("/release/{release_id}", response_model=ReturnRelease)
async def delete_release_by_id(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    release = crud.delete_release_by_id(db, release_id=release_id)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release


@router.post("/release", response_model=ReturnRelease)
async def create_release(
    new_release: Release,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
):
    return crud.create(db, new_release=new_release)


@router.patch("/release/{release_id}", response_model=ReturnRelease)
async def update_release(
    release_id: int,
    new_release: Release,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    release = crud.update(db, new_release=new_release, release_id=release_id)
    if release is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Release not found"
        )
    return release
