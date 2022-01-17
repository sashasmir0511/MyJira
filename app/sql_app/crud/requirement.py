from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.requirement import ReturnRequirement
from .utils import to_dict


def get_all_requirement(db: Session, limit: int = 10, skip: int = 0) -> List[ReturnRequirement]:
    result = db.query(models.Requirement).offset(skip).limit(limit).all()
    return [ReturnRequirement.parse_obj(to_dict(obj)) for obj in result]


def get_requirement_by_id(db: Session, requirement_id: int) -> Optional[ReturnRequirement]:
    result = db.query(models.Requirement).filter(models.Requirement.id == requirement_id).one_or_none()
    return None if result is None else ReturnRequirement.parse_obj(to_dict(result))