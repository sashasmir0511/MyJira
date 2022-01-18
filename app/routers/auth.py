from fastapi import status, Request, WebSocket
from fastapi import Depends
from fastapi.routing import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import json


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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        data = json.loads(data)
        
        await websocket.send_text(f"Token: {data}")
        try:
            token = login(Login(email = data['L'], password = data['P']))
            await websocket.send_text(f"Вход выполнен {token['access_token']}")
        except:
            await websocket.send_text(f"Incorrect username or password")
        


@router.post("/auth", response_model=Token)
def login(
    login_data: Login,
    db: Session = Depends(get_db)
    ) -> Token:
    print(type(db))
    curr_user = crud.get_curr_user(db=db, login_data=login_data)
    if curr_user is None \
        or not verify_password(login_data.password, curr_user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = Token(access_token=create_access_token({"sub": curr_user.email}), token_type="Bearer")
    return token
