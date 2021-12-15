import uvicorn
from fastapi import FastAPI

from app.routers import (
    attachment,
    auth,
    comment,
    project,
    release,
    role,
    task,
    team_member,
    user,
)
from app.sql_app.db.database import Base, database, engine

app = FastAPI(title="Jira")

app.include_router(auth.router)
app.include_router(attachment.router)
app.include_router(comment.router)
app.include_router(role.router)
app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(release.router)
app.include_router(team_member.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello this is jira"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
