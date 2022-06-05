from pydantic import BaseModel
from sqlalchemy import Text, Column
from sqlmodel import SQLModel, Field


class SnippetIdentity(SQLModel):
    creator_username: str = Field(primary_key=True)
    name: str = Field(primary_key=True, min_length=3)


class SnippetInfo(SnippetIdentity):
    public: bool = True


class Snippet(SnippetInfo, table=True):
    language: str = Field(min_length=1)
    language_version: str = Field(min_length=1)
    code: str = Field(..., sa_column=Column('code', Text(), nullable=False))


class SnippetCreate(BaseModel):
    name: str = Field(min_length=3)
    code: str = Field(min_length=3)
    language: str = Field(min_length=1)
    language_version: str = Field(min_length=1)
    public: bool = True


class SnippetPatch(BaseModel):
    name: str | None = Field(min_length=3)
    code: str | None = Field(min_length=3)
    language: str | None = Field(min_length=1)
    language_version: str | None = Field(min_length=1)
    public: bool | None = True


class SnippetForkInfo(BaseModel):
    name: str
    public: bool = True
