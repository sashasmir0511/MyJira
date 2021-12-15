from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.release import Release, ReturnRelease
from .utils import to_dict


def get_all_releases(
    db: Session, limit: int = 10, skip: int = 0
) -> List[ReturnRelease]:
    result = db.query(models.Release).offset(skip).limit(limit).all()
    return [ReturnRelease.parse_obj(to_dict(obj)) for obj in result]


def get_release_by_id(db: Session, release_id: int) -> Optional[ReturnRelease]:
    result = (
        db.query(models.Release).filter(models.Release.id == release_id).one_or_none()
    )
    return None if result is None else ReturnRelease.parse_obj(to_dict(result))


def get_release_by_name(db: Session, name: str) -> Optional[ReturnRelease]:
    result = db.query(models.Release).filter(models.Release.name == name).one_or_none()
    return None if result is None else ReturnRelease.parse_obj(to_dict(result))


def delete_release_by_id(db: Session, release_id: int) -> Optional[ReturnRelease]:
    result = (
        db.query(models.Release).filter(models.Release.id == release_id).one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        return ReturnRelease.parse_obj(to_dict(result))


def delete_release_by_name(db: Session, name: str) -> Optional[ReturnRelease]:
    result = db.query(models.Release).filter(models.Release.name == name).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnRelease.parse_obj(to_dict(result))


def create(db: Session, new_release: Release) -> ReturnRelease:
    db_release = models.Release(**new_release.dict())
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    return ReturnRelease.parse_obj(to_dict(db_release))


def update(
    db: Session, release_id: int, new_release: Release
) -> Optional[ReturnRelease]:
    result = (
        db.query(models.Release).filter(models.Release.id == release_id).one_or_none()
    )
    if result is None:
        return None

    result.name = new_release.name
    result.description = new_release.description
    result.release_date = new_release.release_date
    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnRelease.parse_obj(to_dict(result))
