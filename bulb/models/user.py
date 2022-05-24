from pydantic import BaseModel, AnyHttpUrl


class User(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    avatar_url: AnyHttpUrl


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
