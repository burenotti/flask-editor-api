from typing import Literal

from pydantic import BaseModel
from runbox.models import SandboxState


class Language(BaseModel):
    language: str
    versions: list[str]


class Stats(BaseModel):
    available_languages: list[Language]


class WebsocketMessage(BaseModel):
    message_type: str


class OutputMessage(WebsocketMessage):
    message_type: str = "output_message"
    data: str
    stream: Literal["stdout", "stderr"]


class ErrorMessage(WebsocketMessage):
    message_type: str = "error"
    error_type: str


class MissingProfileMessage(ErrorMessage):
    error_type: str = "missing_profile"


class BuildFailedMessage(ErrorMessage):
    error_type: str = "build_failed"
    logs: list[str]


class FinishMessage(WebsocketMessage, SandboxState):
    message_type: str = "finish"
