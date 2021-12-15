from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.team_member import ReturnTeamMember, TeamMember
from .utils import to_dict


def get_all_team_members(
    db: Session, limit: int = 10, skip: int = 0
) -> List[ReturnTeamMember]:
    result = db.query(models.TeamMember).offset(skip).limit(limit).all()
    return [ReturnTeamMember.parse_obj(to_dict(obj)) for obj in result]


def get_team_member_by_id(
    db: Session, team_member_id: int
) -> Optional[ReturnTeamMember]:
    result = (
        db.query(models.TeamMember)
        .filter(models.TeamMember.id == team_member_id)
        .one_or_none()
    )
    return None if result is None else ReturnTeamMember.parse_obj(to_dict(result))


def get_team_member_by_user_name(db: Session, name: str) -> Optional[ReturnTeamMember]:
    result = (
        db.query(models.TeamMember)
        .join(models.User, models.User.id == models.TeamMember.user_id, isouter=True)
        .filter(models.User.name == name)
        .one_or_none()
    )
    return None if result is None else ReturnTeamMember.parse_obj(to_dict(result))


def delete_team_member_by_id(
    db: Session, team_member_id: int
) -> Optional[ReturnTeamMember]:
    result = (
        db.query(models.TeamMember)
        .filter(models.TeamMember.id == team_member_id)
        .one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        return ReturnTeamMember.parse_obj(to_dict(result))


def delete_team_member_by_user_name(
    db: Session, name: str
) -> Optional[ReturnTeamMember]:
    result = (
        db.query(models.TeamMember)
        .join(models.User, models.User.id == models.TeamMember.user_id, isouter=True)
        .filter(models.User.name == name)
        .one_or_none()
    )
    if result:
        db.delete(result)
        db.commit()
        return ReturnTeamMember.parse_obj(to_dict(result))


def create(db: Session, new_team_member: TeamMember) -> ReturnTeamMember:
    db_team_member = models.TeamMember(**new_team_member.dict())
    db.add(db_team_member)
    db.commit()
    db.refresh(db_team_member)
    return ReturnTeamMember.parse_obj(to_dict(db_team_member))


def update(
    db: Session, team_member_id: int, new_team_member: TeamMember
) -> Optional[ReturnTeamMember]:
    result = (
        db.query(models.TeamMember)
        .filter(models.TeamMember.id == team_member_id)
        .one_or_none()
    )
    if result is None:
        return None

    result.is_manager = new_team_member.is_manager
    result.is_active = new_team_member.is_active
    result.project_id = new_team_member.project_id
    result.user_id = new_team_member.user_id
    result.role_id = new_team_member.role_id
    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnTeamMember.parse_obj(to_dict(result))
