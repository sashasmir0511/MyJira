from fastapi import status
from fastapi.params import Depends
from fastapi.routing import APIRouter, HTTPException
from sqlalchemy.orm import Session

from ..sql_app.core.security import create_access_token, verify_password
from ..sql_app.crud import user
from ..sql_app.db import models
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.token import Login, Token

router = APIRouter(tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/auth", response_model=Token)
async def login(login_data: Login, db: Session = Depends(get_db)) -> Token:
    curr_user = (
        db.query(models.User)
        .filter(models.User.email == login_data.email)
        .one_or_none()
    )
    if curr_user is None or not verify_password(
        login_data.password, curr_user.hash_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return Token(
        access_token=create_access_token({"sub": curr_user.email}), token_type="Bearer"
    )
