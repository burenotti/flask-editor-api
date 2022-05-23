from pydantic import BaseModel, Field, validator

from bulb.models.user import UserOrigin


class GithubUserMapper(BaseModel):
    email: str
    username: str = Field(alias="login")
    first_name: str = Field(alias="name")
    last_name: str = Field(alias="name")
    avatar_url: str
    origin: UserOrigin = Field(UserOrigin.github, allow_mutation=False)

    @validator('first_name')
    def split_first_name(cls, full_name: str):
        return full_name.split(' ')[0]

    @validator('last_name')
    def split_last_name(cls, full_name: str):
        tokens = full_name.split(' ')
        return tokens[-1] if len(tokens) > 1 else ""
