from pydantic import BaseModel


class Attachment(BaseModel):
    name: str
    path: str
    type: str
    task_id: int
    file_body: bytes


class ReturnAttachment(BaseModel):
    id: int
    name: str
    path: str
    type: str
    task_id: int
