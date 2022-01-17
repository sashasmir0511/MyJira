from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str
    release_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectEdit(ProjectBase):
    pass


class ReturnProject(ProjectBase):
    id: int
    name: str
    creator_id: int
    release_id: int
    description: str
