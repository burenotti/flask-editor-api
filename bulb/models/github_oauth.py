from pydantic import BaseModel, Field, validator


class GithubUserMapper(BaseModel):
    email: str
    username: str = Field(alias="login")
    first_name: str = Field(alias="name")
    last_name: str = Field(alias="name")
    avatar_url: str

    @validator('first_name')
    def split_first_name(cls, full_name: str):
        return full_name.split(' ')[0]

    @validator('last_name')
    def split_last_name(cls, full_name: str):
        tokens = full_name.split(' ')
        return tokens[-1] if len(tokens) > 1 else ""
