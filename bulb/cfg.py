from datetime import timedelta
from pathlib import Path

from pydantic import BaseSettings, BaseModel
from runbox.models import Limits, DockerProfile


class LanguageProfile(BaseModel):
    language: str
    version: str

    profile: DockerProfile
    build_profile: DockerProfile | None = None

    @property
    def build_required(self) -> bool:
        return self.build_profile is not None


cpp17_profile = LanguageProfile(
    language='C++',
    version='C++17',
    build_profile=DockerProfile(
        image='gcc10',
        workdir=Path('/build'),
        cmd_template=['g++', 'main.cpp', '--std=c++17', '/sandbox/build'],
        user='builder'
    ),
    profile=DockerProfile(
        image='gcc10',
        workdir=Path('/sandbox'),
        cmd_template=['/sandbox/build'],
        user='sandbox',
    ),
)

cpp11_profile = cpp17_profile.copy(update={
    'version': 'C++11',
    'build_profile': {
        'cmd_template': ['g++', 'main.cpp', '--std=c++11', '/sandbox/build']
    }
})

python3_10_profile = LanguageProfile(
    language='python',
    version='3.10',
    profile=DockerProfile(
        image='python3.10-sandbox',
        workdir=Path('/sandbox'),
        cmd_template=['python', 'main.py'],
        user='sandbox',
    ),
)

python2_7_profile = LanguageProfile(
    language='python',
    version='2.7',
    profile=DockerProfile(
        image='python2.7-sandbox',
        workdir=Path('/sandbox'),
        cmd_template=['python', 'main.py'],
        user='sandbox',
    )
)


class LimitsConfig(Limits):
    class Config:
        env_prefix = 'LIMITS__'


class Config(BaseSettings):
    debug: bool = True
    limits: LimitsConfig = Limits(
        time=timedelta(minutes=2),
        disk_space_mb=128,
        memory_mb=128,
        cpu_count=1,
    )

    languages: list[LanguageProfile] = [
        python3_10_profile,
        python2_7_profile,
        cpp17_profile,
        cpp11_profile,
    ]

    class Config:
        env_nested_delimiter = '__'


config = Config(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
