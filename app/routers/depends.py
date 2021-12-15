from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from ..sql_app.core.security import JWTBearer, decode_access_token
from ..sql_app.crud import team_member, user
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.user import ReturnUser


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(JWTBearer())
) -> ReturnUser:
    cred_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are not valid"
    )
    payload = decode_access_token(token)
    if payload is None:
        raise cred_exception
    email: str = payload.get("sub")
    if email is None:
        raise cred_exception
    curr_user = user.get_by_email(db, email=email)
    if curr_user is None or not curr_user.is_active:
        raise cred_exception
    return curr_user


def is_team_member(
    db: Session = Depends(get_db), token: str = Depends(JWTBearer())
) -> ReturnUser:
    curr_user = get_current_user(db, token)
    user_member = team_member.get_team_member_by_user_name(db, curr_user.name)
    if not user_member or not user_member.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not member"
        )
    return curr_user


def is_manager(
    db: Session = Depends(get_db), token: str = Depends(JWTBearer())
) -> ReturnUser:
    curr_user = get_current_user(db, token)
    user_member = team_member.get_team_member_by_user_name(db, curr_user.name)
    if not user_member or not user_member.is_active or not user_member.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not manager"
        )
    return curr_user
