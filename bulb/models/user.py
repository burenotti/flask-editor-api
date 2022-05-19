from pydantic import BaseModel


class User(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
