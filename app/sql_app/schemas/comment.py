from datetime import datetime

from pydantic import BaseModel

from app.sql_app.db.models import State


class Comment(BaseModel):
    message: str
    task_id: int
    prev_state_id: State


class EditComment(BaseModel):
    message: str


class ReturnComment(Comment):
    id: int
    creator_id: int
    created_at: datetime
