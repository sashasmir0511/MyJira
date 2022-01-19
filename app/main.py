import uvicorn
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


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

# @app.get("/logout")
# async def route_logout_and_remove_cookie():
#     response = RedirectResponse(url="/")
#     response.delete_cookie("Authorization", domain="localtest.me")
#     return response

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, host="0.0.0.0", reload=True)
