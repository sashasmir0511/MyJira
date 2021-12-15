from typing import List, Optional

from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..db import models
from ..schemas.user import ReturnUser, UserIn
from .utils import to_dict


def get_all_users(db: Session, limit: int = 10, skip: int = 0) -> List[ReturnUser]:
    result = db.query(models.User).offset(skip).limit(limit).all()
    return [ReturnUser.parse_obj(to_dict(obj)) for obj in result]


def get_user_by_id(db: Session, user_id: int) -> Optional[ReturnUser]:
    result = db.query(models.User).filter(models.User.id == user_id).one_or_none()
    return None if result is None else ReturnUser.parse_obj(to_dict(result))


def get_by_email(db: Session, email: str) -> Optional[ReturnUser]:
    result = db.query(models.User).filter(models.User.email == email).one_or_none()
    return None if result is None else ReturnUser.parse_obj(to_dict(result))


def delete_user_by_id(db: Session, user_id: int) -> Optional[ReturnUser]:
    result = db.query(models.User).filter(models.User.id == user_id).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnUser.parse_obj(to_dict(result))


def delete_by_email(db: Session, email: str) -> Optional[ReturnUser]:
    result = db.query(models.User).filter(models.User.email == email).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnUser.parse_obj(to_dict(result))


def create_user(db: Session, new_user: UserIn) -> ReturnUser:
    db_user = models.User(
        name=new_user.name,
        email=new_user.email,
        hash_password=hash_password(new_user.password),
        is_active=new_user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return ReturnUser.parse_obj(to_dict(db_user))


def update_user(db: Session, user_id: int, new_user: UserIn) -> Optional[ReturnUser]:
    result = db.query(models.User).filter(models.User.id == user_id).one_or_none()
    if result is None:
        return None
    result.name = new_user.name
    result.email = new_user.email
    result.hash_password = hash_password(new_user.password)
    result.is_active = new_user.is_active

    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnUser.parse_obj(to_dict(result))
