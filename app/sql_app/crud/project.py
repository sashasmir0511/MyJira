from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.project import ProjectCreate, ProjectEdit, ReturnProject
from .utils import to_dict


def get_project_by_id(db: Session, project_id: int) -> Optional[ReturnProject]:
    result = (
        db.query(models.Project).filter(models.Project.id == project_id).one_or_none()
    )
    return None if result is None else ReturnProject.parse_obj(to_dict(result))


def get_project_by_name(db: Session, name: str) -> Optional[ReturnProject]:
    result = db.query(models.Project).filter(models.Project.name == name).one_or_none()
    return None if result is None else ReturnProject.parse_obj(to_dict(result))


def delete_project_by_id(db: Session, project_id: int) -> Optional[ReturnProject]:
    result = (
        db.query(models.Project).filter(models.Project.id == project_id).one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        return ReturnProject.parse_obj(to_dict(result))


def delete_project_by_name(db: Session, name: str) -> Optional[ReturnProject]:
    result = db.query(models.Project).filter(models.Project.name == name).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnProject.parse_obj(to_dict(result))


def get_all_projects(
    db: Session, skip: int = 0, limit: int = 100
) -> List[ReturnProject]:
    result = db.query(models.Project).offset(skip).limit(limit).all()
    return [ReturnProject.parse_obj(to_dict(obj)) for obj in result]


def create_project(
    db: Session, new_project: ProjectCreate, creator_id: int
) -> ReturnProject:
    db_project = models.Project(**new_project.dict(), creator_id=creator_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return ReturnProject.parse_obj(to_dict(db_project))


def edit_project(
    db: Session, project_id: int, new_project: ProjectEdit
) -> Optional[ReturnProject]:
    result = (
        db.query(models.Project).filter(models.Project.id == project_id).one_or_none()
    )
    if result is None:
        return None

    result.name = new_project.name
    result.description = new_project.description
    result.release_id = new_project.release_id

    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnProject.parse_obj(to_dict(result))
