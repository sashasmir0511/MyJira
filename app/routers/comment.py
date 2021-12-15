from typing import List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..sql_app.crud import comment as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.comment import Comment, EditComment, ReturnComment
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_team_member

router = APIRouter(tags=["comments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/comment/{task_id}", response_model=List[ReturnComment])
async def get_comment_by_task_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
):
    comment = crud.get_comment_by_task_id(db, task_id=task_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found"
        )
    return comment


@router.delete("/comment/{comment_id}", response_model=ReturnComment)
async def delete_comment_by_id(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
):
    error = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )
    curr_comment = crud.get_comment_by_id(db, comment_id)
    if curr_comment is None:
        raise error

    if curr_comment.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    comment = crud.delete_comment_by_id(db, comment_id=comment_id)
    if comment is None:
        raise error
    return comment


@router.post("/comment", response_model=ReturnComment)
async def create_comment(
    new_comment: Comment,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
):
    return crud.create(db, new_comment=new_comment, creator=current_user.id)


@router.patch("/comment/{comment_id}", response_model=ReturnComment)
async def update_comment(
    comment_id: int,
    new_comment: EditComment,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
):
    error = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )
    curr_comment = crud.get_comment_by_id(db, comment_id)
    if curr_comment is None:
        raise error

    if curr_comment.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    comment = crud.update(db, new_comment=new_comment, comment_id=comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return comment
