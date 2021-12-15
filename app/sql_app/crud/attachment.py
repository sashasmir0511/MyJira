import os
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from ..core.config import DOC_PATH
from ..db import models
from ..schemas.attachment import Attachment, ReturnAttachment
from .utils import to_dict


def get_attachment_by_id(db: Session, attachment_id: int) -> Optional[ReturnAttachment]:
    result = (
        db.query(models.Attachment)
        .filter(models.Attachment.id == attachment_id)
        .one_or_none()
    )
    return None if result is None else ReturnAttachment.parse_obj(to_dict(result))


def get_attachment_by_name(db: Session, name: str) -> Optional[ReturnAttachment]:
    result = (
        db.query(models.Attachment).filter(models.Attachment.name == name).one_or_none()
    )
    return None if result is None else ReturnAttachment.parse_obj(to_dict(result))


def delete_attachment_by_id(
    db: Session, attachment_id: int
) -> Optional[ReturnAttachment]:
    result = (
        db.query(models.Attachment)
        .filter(models.Attachment.id == attachment_id)
        .one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        os.remove(os.path.join(DOC_PATH, result.path, result.name))
        return ReturnAttachment.parse_obj(to_dict(result))


def delete_attachment_by_name(db: Session, name: str) -> Optional[ReturnAttachment]:
    result = (
        db.query(models.Attachment).filter(models.Attachment.name == name).one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        os.remove(os.path.join(DOC_PATH, result.path, result.name))
        return ReturnAttachment.parse_obj(to_dict(result))


def create(db: Session, new_attachment: Attachment) -> ReturnAttachment:
    path = os.path.join(DOC_PATH, new_attachment.path)
    Path(path).mkdir(parents=True, exist_ok=True)

    with open(os.path.join(path, new_attachment.name), "wb") as f:
        f.write(new_attachment.file_body)

    db_attachment = models.Attachment(
        name=new_attachment.name,
        type=new_attachment.type,
        path=new_attachment.path,
        task_id=new_attachment.task_id,
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return ReturnAttachment.parse_obj(to_dict(db_attachment))


def update(
    db: Session, attachment_id: int, new_attachment: Attachment
) -> Optional[ReturnAttachment]:
    result = (
        db.query(models.Attachment)
        .filter(models.Attachment.id == attachment_id)
        .one_or_none()
    )
    if result is None:
        return None

    old_path = os.path.join(DOC_PATH, result.path, result.name)
    new_path = os.path.join(DOC_PATH, new_attachment.path, new_attachment.name)
    os.rename(old_path, new_path)

    result.name = new_attachment.name
    result.type = new_attachment.type
    result.path = new_attachment.path
    result.task_id = new_attachment.task_id

    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnAttachment.parse_obj(to_dict(result))
