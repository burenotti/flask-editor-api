import datetime
from datetime import timedelta

from pydantic import BaseSettings, BaseModel, Field, HttpUrl, AnyHttpUrl, validator
from runbox.models import Limits

from bulb.models.language_profile import LanguageProfile
from . import profiles


class LimitsConfig(Limits):
    class Config:
        env_prefix = 'LIMITS__'


class ExternalOAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_url: HttpUrl
    token_swap_url: HttpUrl
    origin: AnyHttpUrl


class JWTConfig(BaseModel):

    secret: str
    algorithm: str = "HS256"
    token_lifetime: timedelta = timedelta(weeks=2)

    class Config:
        env_prefix = "JWT__"


class Config(BaseSettings):
    debug: bool = True
    limits: LimitsConfig = Limits(
        time=timedelta(minutes=2),
        disk_space_mb=128,
        memory_mb=128,
        cpu_count=1,
    )

    languages: list[LanguageProfile] = [
        profiles.python3_10_profile,
        profiles.python2_7_profile,
        profiles.cpp17_profile,
        profiles.cpp11_profile,
    ]

    github: ExternalOAuthConfig | None = Field(None, env="github")

    jwt: JWTConfig

    class Config:
        env_nested_delimiter = '__'


config = Config(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
