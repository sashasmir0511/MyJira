from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.comment import Comment, EditComment, ReturnComment
from .utils import to_dict


def get_comment_by_task_id(db: Session, task_id: int) -> List[ReturnComment]:
    result = db.query(models.Comment).filter(models.Comment.task_id == task_id).all()
    return [ReturnComment.parse_obj(to_dict(obj)) for obj in result]


def get_comment_by_id(db: Session, comment_id: int) -> Optional[ReturnComment]:
    result = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).one_or_none()
    )
    return None if result is None else ReturnComment.parse_obj(to_dict(result))


def delete_comment_by_id(db: Session, comment_id: int) -> Optional[ReturnComment]:
    result = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        return ReturnComment.parse_obj(to_dict(result))


def create(db: Session, new_comment: Comment, creator: int = 1) -> ReturnComment:
    db_comment = models.Comment(
        **new_comment.dict(),
        creator_id=creator,
        created_at=datetime.now(),
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return ReturnComment.parse_obj(to_dict(db_comment))


def update(
    db: Session, comment_id: int, new_comment: EditComment
) -> Optional[ReturnComment]:
    result = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).one_or_none()
    )
    if result is None:
        return None

    result.message = new_comment.message
    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnComment.parse_obj(to_dict(result))
