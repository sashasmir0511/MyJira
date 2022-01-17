from datetime import datetime

from pydantic import BaseModel


class Release(BaseModel):
    name: str
    description: str
    release_date: datetime


class ReturnRelease(Release):
    id: int
    name: str
    description: str
    release_date: datetime
