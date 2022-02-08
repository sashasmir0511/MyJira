from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from app.routers.comment import get_comment_by_task_id
import json
import requests
import aiohttp
import asyncio

from app.routers.user import get_user_by_id
from app.routers.requirement import get_requirement_by_id
from app.routers.team_member import get_team_member_by_id, get_team_member_by_user_name
from app.sql_app.db.models import State
#from app.routers.attachment import get_attachments_by_task_id
from ..sql_app.schemas.project import ReturnProject
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from fastapi.templating import Jinja2Templates

from app.sql_app.db.database import SessionLocal

from ..sql_app.crud import task as crud
from ..sql_app.crud import project as crud_project
from ..sql_app.schemas.task import ReturnTask, TaskCreate, TaskEdit
from ..sql_app.schemas.user import ReturnUser
from ..sql_app.schemas.requirement import ReturnRequirement
from .depends import get_current_user, is_manager

router = APIRouter(tags=["tasks"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.websocket("/update_task/{task_id}/ws")
async def websocket_update_task(
    websocket: WebSocket,
    task_id: int
    ):
    await websocket.accept()
    data = await websocket.receive_json()
    for s in State:
        if 'State.' + s.name == data["state_id"]:
            data["state_id"] = s.value
    async with aiohttp.ClientSession() as session:
        async with session.patch(f'http://0.0.0.0:5000/update_task/{task_id}', json=data) as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail")


@router.patch("/update_task/{task_id}", response_model=ReturnTask)
async def edit_task(
    task_id: int,
    task: TaskEdit,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    db_team_member = await get_team_member_by_user_name(db=db, name=task.assignee_name)
    task.assignee_id = db_team_member.id
    db_task = crud.edit_task(db=db, new_task=task, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.websocket("/update_task_description/{task_id}/ws")
async def websocket_update_task_description(
    websocket: WebSocket,
    task_id: int
    ):
    await websocket.accept()
    data = await websocket.receive_json()
    description = data["description"]
    async with aiohttp.ClientSession() as session:
        async with session.patch(f'http://0.0.0.0:5000/update_task_description/{task_id}/{description}') as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail")


@router.websocket("/remove_task/ws")
async def websocket_create_task(websocket: WebSocket,):
    await websocket.accept()
    data = await websocket.receive_json()
    task_id = data['task_id']
    print(data)
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'http://0.0.0.0:5000/remove_task/{task_id}') as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text("Fail")

                
@router.websocket("/create_task/{project_id}/ws")
async def websocket_create_task(
    websocket: WebSocket,
    project_id: int
    ):
    await websocket.accept()
    data = await websocket.receive_json()
    data["state_id"] = 1
    data["project_id"] = project_id
    async with aiohttp.ClientSession() as session:
        async with session.post('http://0.0.0.0:5000/tasks', json=data) as response:
            if response.status == 200:
                await websocket.send_text("OK")
            else:
                await websocket.send_text(f"Fail")


@router.get("/create_task/{project_id}", response_class=HTMLResponse)
async def create_task(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db)):
    db_project = await get_project_by_id(project_id, db=db)
    dict_Response = {"request": request,"project_id": project_id, 'project_name': db_project.name}
    return templates.TemplateResponse("create_task.html", dict_Response)


@router.get("/task/{project_id}/{task_id}", response_class=HTMLResponse)
async def read_task(
    request: Request,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    ):
    dict_Response = {"request": request,
                     "project_id": project_id, "task_id": task_id}
    db_task = await get_task_by_id(task_id, db=db)
    dict_Response['task_name'] = db_task.name
    dict_Response['state_id'] = db_task.state_id.value
    dict_Response['state_name'] = db_task.state_id
    dict_Response['description'] = db_task.description
    dict_Response['created_at'] = db_task.created_at
    dict_Response['updated_at'] = db_task.updated_at
    
    db_user_manager = await get_user_by_id(db_task.manager_id, db=db)
    dict_Response['manager'] = db_user_manager.name

    db_team_member = await get_team_member_by_id(db_task.assignee_id, db=db)
    db_user = await get_user_by_id(db_team_member.user_id, db=db)
    dict_Response['assignee_name'] = db_user.name

    db_project = await get_project_by_id(project_id, db=db)
    dict_Response['project_name'] = db_project.name

    db_requirement = await get_requirement_by_id(db_task.requirement_id, db=db)
    dict_Response['requirement_link'] = db_requirement.link

    # db_attachments = await get_attachments_by_task_id(task_id, db=db)
    # dict_Response['attachments_id'] = [db_attachments[i].id for i in range(len(db_attachments))]
    #dict_Response['attachments_name'] = [db_attachments[i].name for i in range(len(db_attachments))]

    db_comments = await get_comment_by_task_id(task_id, db=db)
    dict_Response['comments_id'] = [db_comments[i].id for i in range(len(db_comments))]
    dict_Response['comments_message'] = [db_comments[i].message for i in range(len(db_comments))]
    dict_Response['comments_created_at'] = [db_comments[i].created_at for i in range(len(db_comments))]
    return templates.TemplateResponse("task.html", dict_Response)


#ТОDO: если импортировать происходит ошибка
#@router.get("/task/project/{project_id}", response_model=ReturnProject)
async def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    db_project = crud_project.get_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project


@router.get("/task/{task_id}", response_model=ReturnTask)
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
    ):
    db_task = crud.get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.get("/task", response_model=ReturnTask)
async def get_task_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    db_task = crud.get_task_by_name(db, name=name)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.get("/tasks", response_model=List[ReturnTask])
async def task_gets(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    return crud.get_all_tasks(db, skip=skip, limit=limit)


@router.get("/tasks", response_model=List[ReturnTask])
async def get_tasks_by_project_id(
    project_id: int,
    db: Session = Depends(get_db),
    #    current_user: ReturnUser = Depends(get_current_user),
    ):
    db_tasks = crud.get_tasks_by_project_id(db, project_id=project_id)
    return db_tasks


@router.delete("/remove_task/{task_id}", response_model=ReturnTask)
async def delete_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    db_task = crud.delete_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.delete("/task", response_model=ReturnTask)
async def delete_task_by_name(
    name: str,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    db_task = crud.delete_task_by_name(db, name=name)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.post("/tasks", response_model=ReturnTask)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    return crud.create_task(db=db, new_task=task
    # , manager_id=current_user.id)
    )


@router.patch("/update_task_description/{task_id}/{description}", response_model=ReturnTask)
async def edit_task_description(
    task_id: int,
    description: str,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(is_manager),
    ):
    db_task = crud.edit_task_description(db=db, description=description, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task



