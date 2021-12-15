from pydantic import BaseModel


class Role(BaseModel):
    name: str


class ReturnRole(Role):
    id: int
