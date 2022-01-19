import json
from app.routers.task import get_tasks_by_project_id
from app.routers.role import get_role_by_id
from app.routers.release import get_release_by_id
from app.routers.user import get_user_by_id
from app.routers.team_member import get_team_members_by_project_id
from typing import List
import aiohttp

from fastapi import APIRouter, Depends, HTTPException, WebSocket, Request
from sqlalchemy.orm import Session
from starlette import status
from fastapi.responses import HTMLResponse

from ..sql_app.crud import project as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.project import ProjectCreate, ProjectEdit, ReturnProject
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_manager
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["projects"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.websocket("/remove_project/ws")
async def websocket_remove_project(websocket: WebSocket,):
    await websocket.accept()
    data = await websocket.receive_json()
    project_id = data["project_id"]
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'http://0.0.0.0:5000/delete_project/{project_id}') as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail Project")


@router.websocket("/create_project/ws")
async def websocket_create_project(websocket: WebSocket,):
    await websocket.accept()
    data = await websocket.receive_json()
    project_data = {"name": data["project_name"]
                    , "description": data["description"]
                    , "release_id": data["release_id"]}
    # release_data = {"name": data["release_name"]
    #                 ,"description": data["release_description"]
    #                 ,"release_date": data["release_data"]}
    async with aiohttp.ClientSession() as session:
        # async with session.post(f'http://0.0.0.0:5000/release', json=release_data) as response:
        #     if response.status == 200:
        #         project_data["release_id"] = response.json()["release_id"]
        async with session.post(f'http://0.0.0.0:5000/project', json=project_data) as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail Project")


@router.get("/projects", response_model=List[ReturnProject])
async def get_all_projects(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    #current_user: ReturnUser = Depends(get_current_user),
    ):
    return crud.get_all_projects(db, limit=limit, skip=skip)


@router.get("/project_list", response_class=HTMLResponse)
async def read_project_list(
    request: Request,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user)
    ):
    db_projects = await get_all_projects(db=db, limit=100)
    dict_Response = {"request": request}
    dict_Response["project_id"] = [project.id for project in db_projects]
    dict_Response["project_name"] = [project.name for project in db_projects]
    return templates.TemplateResponse("project_list.html", dict_Response)


@router.get("/project/html/n_{project_name}", response_class=HTMLResponse)
async def read_project(
    request: Request,
    project_name: str,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
    ):

    db_project = await get_project_by_name(name=project_name, db=db)
    dict_Response = {"request": request, "project_name": project_name, "project_id": db_project.id}
    dict_Response['project_discription'] = db_project.description

    db_user = await get_user_by_id(user_id=db_project.creator_id, db=db)
    dict_Response["creator_name"] = db_user.name
    
    db_release = await get_release_by_id(release_id=db_project.release_id, db=db)
    dict_Response["release_discription"] = db_release.description
    dict_Response["release_name"] = db_release.name
    dict_Response["release_date"] = db_release.release_date
    
    db_tasks = await get_tasks_by_project_id(db_project.id, db=db)
    dict_Response['tasks_id'] = [db_tasks[i].id for i in range(len(db_tasks))]
    dict_Response['tasks_name'] = [db_tasks[i].name for i in range(len(db_tasks))]
    dict_Response['tasks_description'] = [db_tasks[i].description for i in range(len(db_tasks))]

    db_team_member = await get_team_members_by_project_id(db_project.id, db=db)
    db_team_member_name = [ await get_user_by_id(i.user_id, db=db) for i in db_team_member]
    db_role = [ await get_role_by_id(i.role_id, db=db) for i in db_team_member]
    dict_Response['team_member_id'] = [i.id for i in db_team_member]
    dict_Response['team_member_is_manager'] = [i.is_manager for i in db_team_member]
    dict_Response['team_member_is_active'] = [i.is_active for i in db_team_member]
    dict_Response['team_member_name'] = [i.name for i in db_team_member_name]
    dict_Response['team_member_role'] = [i.name for i in db_role]
    return templates.TemplateResponse("project.html", dict_Response)


@router.get("/project", response_model=ReturnProject)
async def get_project_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    db_project = crud.get_project_by_name(db, name=name)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.get("/project/{project_id}", response_model=ReturnProject)
async def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
    ):
    db_project = crud.get_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.delete("/delete_project/{project_id}", response_model=ReturnProject)
async def delete_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    db_project = crud.delete_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.delete("/project", response_model=ReturnProject)
async def delete_project_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
    ):
    db_project = crud.delete_project_by_name(db, name=name)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.get("/projects", response_model=List[ReturnProject])
async def task_projects(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    return crud.get_all_projects(db, skip=skip, limit=limit)


@router.post("/project", response_model=ReturnProject)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    return crud.create_project(db=db, new_project=project
    # , creator_id=current_user.id
    )


@router.patch("/project/{project_id}", response_model=ReturnProject)
async def edit_project(
    project_id: int,
    project: ProjectEdit,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_manager),
    ):
    db_project = crud.edit_project(
        db, project_id=project_id, new_project=project)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return db_project
