from typing import List
import aiohttp

from fastapi import HTTPException, WebSocket
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app.routers.role import get_role_by_name

from ..sql_app.crud import team_member as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.team_member import ReturnTeamMember, TeamMember
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager

router = APIRouter(tags=["team_members"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.websocket("/create_TeamMember/{project_id}/ws")
async def websocket_create_TeamMembers(
    websocket: WebSocket,
    project_id: int,
    ):
    await websocket.accept()
    data = await websocket.receive_json()
    data["project_id"] = project_id
    data["is_manager"] = False
    data["is_active"] = True
    role_name = data["role_name"]
    user_name = data["user_name"]
    del data["user_name"]
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://0.0.0.0:5000/role_name/{role_name}') as response:
            if response.status == 200:
                token = await response.json()
                data["role_id"] = token['id']
                del data['role_name']
                print(data)
                async with session.post(f'http://0.0.0.0:5000/create_team_member/{user_name}', json=data) as response:
                    if response.status == 200:
                        await websocket.send_text("OK")
                    else:
                        await websocket.send_text("Fail create team_member")
            else:
                await websocket.send_text("Fail not role")


@router.websocket("/remove_TeamMember/ws")
async def websocket_remove_TeamMembers(websocket: WebSocket,):
    await websocket.accept()
    data = await websocket.receive_json()
    team_member_id = data["TeamMembers_id"]
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'http://0.0.0.0:5000/team_member/{team_member_id}') as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail remove team_member")


@router.get("/team_members", response_model=List[ReturnTeamMember])
async def get_all_team_members(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_all_team_members(db, limit=limit, skip=skip)


@router.get("/team_members", response_model=List[ReturnTeamMember])
async def get_team_members_by_project_id(
    project_id: int,
    db: Session = Depends(get_db),
#    current_user: ReturnUser = Depends(get_current_user),
):
    return crud.get_team_members_by_project_id(db, project_id=project_id)

@router.get("/team_member/{team_member_id}", response_model=ReturnTeamMember)
async def get_team_member_by_id(
    team_member_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
):
    team_member = crud.get_team_member_by_id(db, team_member_id=team_member_id)
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TeamMember not found"
        )
    return team_member


@router.get("/team_member", response_model=ReturnTeamMember)
async def get_team_member_by_user_name(
    name: str,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
):
    team_member = crud.get_team_member_by_user_name(db, name=name)
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TeamMember not found"
        )
    return team_member


@router.delete("/team_member/{team_member_id}", response_model=ReturnTeamMember)
async def delete_team_member_by_id(
    team_member_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
):
    team_member = crud.delete_team_member_by_id(db, team_member_id=team_member_id)
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TeamMember not found"
        )
    return team_member


@router.delete("/team_member", response_model=ReturnTeamMember)
async def delete_team_member_by_user_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
):
    team_member = crud.delete_team_member_by_user_name(db, name=name)
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TeamMember not found"
        )
    return team_member


@router.post("/create_team_member/{user_name}", response_model=ReturnTeamMember)
async def create_team_member(
    user_name: str,
    new_team_member: TeamMember,
    db: Session = Depends(get_db),
#    current_user: ReturnUser = Depends(is_manager),
):
    db_user = await get_team_member_by_user_name(db=db, name=user_name)
    new_team_member.user_id = db_user.user_id
    print(new_team_member)
    return crud.create(db, new_team_member=new_team_member)


@router.patch("/team_member/{team_member_id}", response_model=ReturnTeamMember)
async def update_team_member(
    team_member_id: int,
    new_team_member: TeamMember,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
):
    team_member = crud.update(
        db, new_team_member=new_team_member, team_member_id=team_member_id
    )
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TeamMember not found"
        )
    return team_member
