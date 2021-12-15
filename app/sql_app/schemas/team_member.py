from pydantic import BaseModel


class TeamMember(BaseModel):
    is_manager: bool
    project_id: int
    is_active: bool
    user_id: int
    role_id: int


class ReturnTeamMember(TeamMember):
    id: int
