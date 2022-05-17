from typing import Literal

from pydantic import BaseModel
from runbox.models import SandboxState

__all__ = [
    'WebsocketMessage',
    'OutputMessage',
    'ErrorMessage',
    'MissingProfileMessage',
    'BuildFailedMessage',
    'FinishMessage',
    'InputMessage',
    'TerminateMessage',
]


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


class InputMessage(WebsocketMessage):
    message_type: str = "input_message"
    data: str


class TerminateMessage(WebsocketMessage):
    message_type: str = "terminate_message"
