from pydantic import BaseModel, validator
from sqlmodel import SQLModel, Field

from bulb.models.user import UserOrigin


class SnippetInfo(SQLModel):
    creator_origin: str = Field(primary_key=True)
    creator_username: str = Field(primary_key=True)
    name: str = Field(primary_key=True, min_length=3)
    public: bool = True,


class Snippet(SnippetInfo, table=True):
    code: str
    public: bool = True

    @validator('creator_origin')
    def validate_origin(cls, origin: str) -> str:
        if origin not in list(UserOrigin):
            raise ValueError(
                f"creator_origin must be in [{', '.join(UserOrigin)}], got {origin}"
            )

        return origin


class SnippetCreate(BaseModel):
    name: str = Field(min_length=3)
    code: str = Field(min_length=3)
    public: str = True
