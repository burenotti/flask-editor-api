from pydantic import BaseModel
from runbox.models import DockerProfile


class LanguageProfile(BaseModel):
    language: str
    version: str

    profile: DockerProfile
    build_profile: DockerProfile | None = None

    @property
    def build_required(self) -> bool:
        return self.build_profile is not None
