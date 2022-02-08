from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.sql_app.db.models import State


class TaskBase(BaseModel):
    name: str
    state_id: State
    assignee_id: int
    requirement_link: str
    project_id: int
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskEdit(BaseModel):
    state_id: Optional[State]
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None


class ReturnTask(BaseModel):
    id: int
    manager_id: int
    assignee_id: int
    project_id: int
    name: str
    requirement_id: int
    state_id: State
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime] = None
    description: Optional[str] = None
