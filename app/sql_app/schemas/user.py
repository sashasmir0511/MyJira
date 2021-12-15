from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator


class ReturnUser(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    name: str

    is_active: bool


class UserIn(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[constr(min_length=4)] = None
    password2: Optional[str] = None
    is_active: Optional[bool] = None

    @validator("password2")
    def password_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("password don't match")
        return v
