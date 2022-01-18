from typing import List, Optional

from sqlalchemy.orm import Session
from ..db import models
from ..schemas.user import ReturnUser
from ..schemas.token import Login
from ..db.database import database
from .utils import to_dict


def get_curr_user(db: Session, login_data: Login)-> Optional[ReturnUser]:
    curr_user = db.query(models.User).filter(models.User.email == login_data.email).one_or_none()
    return None if curr_user is None else ReturnUser.parse_obj(to_dict(curr_user))
