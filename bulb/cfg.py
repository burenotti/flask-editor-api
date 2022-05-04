from datetime import timedelta
from pathlib import Path

from pydantic import BaseSettings, BaseModel
from runbox.models import Limits, DockerProfile


class LimitsConfig(Limits):
    class Config:
        env_prefix = 'LIMITS__'


class LanguageProfile(BaseModel):
    language: str
    version: str

    profile: DockerProfile
    build_profile: DockerProfile | None = None

    @property
    def build_required(self) -> bool:
        return self.build_profile is not None


class Config(BaseSettings):
    debug: bool = True
    limits: LimitsConfig = Limits(
        time=timedelta(minutes=2),
        disk_space_mb=128,
        memory_mb=128,
        cpu_count=1,
    )

    # There are default languages profile because
    # RunBox DockerProfile is unserializable type.
    # I'll fix RunBox and remove default values.
    languages: list[LanguageProfile] = [
        LanguageProfile(
            language='python',
            version='3.10',
            profile=DockerProfile(
                image='python-sandbox',
                user='sandbox',
                workdir=Path('/sandbox'),
                cmd_template=['python', ...],
            )
        ),
        LanguageProfile(
            language='C++',
            version='C++17',
            build_profile=DockerProfile(
                image='gcc10-sandbox:latest',
                user='sandbox',
                workdir=Path('/sandbox'),
                cmd_template=['g++', ..., '--std=c++17', '-o', '/sandbox/build']
            ),
            profile=DockerProfile(
                image='gcc10-sandbox:latest',
                user='sandbox',
                workdir=Path('/sandbox'),
                cmd_template=['/sandbox/build']
            ),
        )
    ]

    class Config:
        env_nested_delimiter = '__'


config = Config(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
