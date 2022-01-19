from fastapi import status, Request, WebSocket
from fastapi import Depends
from fastapi.routing import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import json
import requests
import aiohttp
import asyncio
from fastapi.encoders import jsonable_encoder

from ..sql_app.core.security import create_access_token, verify_password
from ..sql_app.crud import user
from ..sql_app.crud import auth as crud
from ..sql_app.db import models
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.token import Login, Token

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/auth", response_model=Token)
async def login(
    login_data: Login,
    db: Session = Depends(get_db)
    ) -> Token:

    curr_user = crud.get_curr_user(db=db, login_data=login_data)
    if curr_user is None \
        or not verify_password(login_data.password, curr_user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = Token(access_token=create_access_token({"sub": curr_user.email}), token_type="Bearer")
    return token


@router.websocket("/auth/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        data = json.loads(data)
        
        async with aiohttp.ClientSession() as session:
            async with session.post('http://0.0.0.0:5000/auth', json={"email": data['L'], "password": data['P']}) as response:
                if response.status == 200:
                    token = await response.json()
                    # await websocket.send_text("Done")
                    await websocket.send_json(token)
                    return token
                else:
                    await websocket.send_text(f"Incorrect username or password")
    