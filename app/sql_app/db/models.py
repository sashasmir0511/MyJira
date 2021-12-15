import enum

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.sql_app.db.database import Base


class State(enum.Enum):
    created = 1
    assigned = 2
    worked = 3
    reviewed = 4
    finished = 5


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column("email", String, primary_key=True, unique=True)
    hash_password = Column(String(64), nullable=False)
    is_active = Column(Boolean, nullable=False)

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Release(Base):
    __tablename__ = "release"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    release_date = Column(TIMESTAMP, nullable=False)

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Requirement(Base):
    __tablename__ = "requirement"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    link = Column(String(500), nullable=False)

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    creator_id = Column(ForeignKey("user.id"), nullable=False)
    release_id = Column(ForeignKey("release.id"), nullable=False)

    creator = relationship("User")
    release = relationship("Release")

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class TeamMember(Base):
    __tablename__ = "team_member"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    is_manager = Column(Boolean, nullable=False)
    project_id = Column(ForeignKey("project.id"), nullable=False)
    is_active = Column(Boolean, nullable=False)
    user_id = Column(ForeignKey("user.id"), nullable=False)
    role_id = Column(ForeignKey("role.id"), nullable=False)

    user = relationship("User")
    project = relationship("Project")
    role = relationship("Role")

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    manager_id = Column(ForeignKey("team_member.id"), nullable=False)
    assignee_id = Column(ForeignKey("team_member.id"))
    state_id = Column(Enum(State), nullable=False)
    requirement_id = Column(ForeignKey("requirement.id"))
    project_id = Column(ForeignKey("project.id"))
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    finished_at = Column(TIMESTAMP)

    assignee = relationship(
        "TeamMember", primaryjoin="Task.assignee_id == TeamMember.id"
    )
    manager = relationship("TeamMember", primaryjoin="Task.manager_id == TeamMember.id")
    project = relationship("Project")
    requirement = relationship("Requirement")

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    message = Column(Text, nullable=False)
    task_id = Column(ForeignKey("task.id"), nullable=False)
    creator_id = Column(ForeignKey("team_member.id"), nullable=False)
    prev_state_id = Column(Enum(State), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    creator = relationship("TeamMember")
    task = relationship("Task")

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    path = Column(String(500), nullable=False)
    type = Column(String(5), nullable=False)
    task_id = Column(ForeignKey("task.id"), nullable=False)

    task = relationship("Task")
