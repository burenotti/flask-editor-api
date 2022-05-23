from enum import Enum

from pydantic import BaseModel, AnyHttpUrl


class UserOrigin(Enum):
    github = "github"


class User(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    avatar_url: AnyHttpUrl
    origin: UserOrigin


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
