from pydantic import BaseModel


class ReturnRequirement(BaseModel):
    id: int
    link: str
