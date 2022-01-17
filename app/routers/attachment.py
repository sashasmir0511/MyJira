import os
from typing import List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from starlette import status

from ..sql_app.core.config import DOC_PATH
from ..sql_app.crud import attachment as crud
from ..sql_app.db.database import SessionLocal
from ..sql_app.schemas.attachment import Attachment, ReturnAttachment
from ..sql_app.schemas.user import ReturnUser
from .depends import get_current_user, is_team_member

router = APIRouter(tags=["attachments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/attachment/{attachment_id}", response_class=FileResponse)
async def get_attachment_by_id(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    attachment = crud.get_attachment_by_id(db, attachment_id=attachment_id)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    return FileResponse(
        path=os.path.join(DOC_PATH, attachment.path, attachment.name),
        filename=attachment.name,
        media_type=attachment.type,
    )


@router.get("/attachment/{task_id}", response_class=List[ReturnAttachment])
async def get_attachments_by_task_id(
    task_id: int,
    db: Session = Depends(get_db),
    #current_user: ReturnUser = Depends(get_current_user),
    ):
    db_attachments = crud.get_attachments_by_task_id(db, task_id=task_id)
    return db_attachments


@router.get("/attachment", response_class=FileResponse)
async def get_attachment_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    attachment = crud.get_attachment_by_name(db, name=name)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    return FileResponse(
        path=os.path.join(DOC_PATH, attachment.path, attachment.name),
        filename=attachment.name,
        media_type=attachment.type,
    )


@router.delete("/attachment/{attachment_id}", response_model=ReturnAttachment)
async def delete_attachment_by_id(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(get_current_user),
    ):
    attachment = crud.delete_attachment_by_id(db, attachment_id=attachment_id)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    return attachment


@router.delete("/attachment", response_model=ReturnAttachment)
async def delete_attachment_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
    ):
    attachment = crud.delete_attachment_by_name(db, name=name)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    return attachment


@router.post("/attachment", response_model=ReturnAttachment)
async def create_attachment(
    new_attachment: Attachment,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
    ):
    return crud.create(db, new_attachment=new_attachment)


@router.patch("/attachment/{attachment_id}", response_model=ReturnAttachment)
async def update_attachment(
    attachment_id: int,
    new_attachment: Attachment,
    db: Session = Depends(get_db),
    current_user: ReturnUser = Depends(is_team_member),
    ):
    attachment = crud.update(
        db, new_attachment=new_attachment, attachment_id=attachment_id
    )
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    return attachment
