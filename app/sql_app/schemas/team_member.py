from typing import Optional
from pydantic import BaseModel


class TeamMember(BaseModel):
    is_manager: bool
    project_id: int
    is_active: bool
    user_id: Optional[int] = None
    role_id: int


class ReturnTeamMember(TeamMember):
    id: int
    user_id: int
    project_id: int