from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.role import ReturnRole, Role
from .utils import to_dict


def get_all_roles(db: Session, limit: int = 10, skip: int = 0) -> List[ReturnRole]:
    result = db.query(models.Role).offset(skip).limit(limit).all()
    return [ReturnRole.parse_obj(to_dict(obj)) for obj in result]


def get_role_by_id(db: Session, role_id: int) -> Optional[ReturnRole]:
    result = db.query(models.Role).filter(models.Role.id == role_id).one_or_none()
    return None if result is None else ReturnRole.parse_obj(to_dict(result))


def get_role_by_name(db: Session, name: str) -> Optional[ReturnRole]:
    result = db.query(models.Role).filter(models.Role.name == name).one_or_none()
    return None if result is None else ReturnRole.parse_obj(to_dict(result))


def delete_role_by_id(db: Session, role_id: int) -> Optional[ReturnRole]:
    result = db.query(models.Role).filter(models.Role.id == role_id).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnRole.parse_obj(to_dict(result))


def delete_role_by_name(db: Session, name: str) -> Optional[ReturnRole]:
    result = db.query(models.Role).filter(models.Role.name == name).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnRole.parse_obj(to_dict(result))


def create(db: Session, new_role: Role) -> ReturnRole:
    db_role = models.Role(**new_role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return ReturnRole.parse_obj(to_dict(db_role))


def update(db: Session, role_id: int, new_role: Role) -> Optional[ReturnRole]:
    result = db.query(models.Role).filter(models.Role.id == role_id).one_or_none()
    if result is None:
        return None

    result.name = new_role.name
    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnRole.parse_obj(to_dict(result))
