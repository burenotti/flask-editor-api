from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class SnippetIdentity(SQLModel):
    creator_username: str = Field(primary_key=True)
    name: str = Field(primary_key=True, min_length=3)


class SnippetInfo(SnippetIdentity):
    public: bool = True


class Snippet(SnippetInfo, table=True):
    code: str


class SnippetCreate(BaseModel):
    name: str = Field(min_length=3)
    code: str = Field(min_length=3)
    public: str = True
