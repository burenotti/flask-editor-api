from contextlib import asynccontextmanager
from typing import AsyncIterable, Protocol, TYPE_CHECKING, AsyncGenerator, ContextManager, \
    AsyncContextManager

from bulb.cfg import LanguageProfile
from bulb.models import WebsocketMessage

if TYPE_CHECKING:
    from .base_execution_pipeline import BaseExecutionPipeline


class ProfileRouter:

    def __call__(self, language: str, version: str) -> LanguageProfile:
        ...


InputStream = AsyncIterable[WebsocketMessage]


class OutputStream(Protocol):

    async def write(self, message: WebsocketMessage) -> None:
        ...


class BuildStage(Protocol):

    @asynccontextmanager
    def __call__(
        self,
        context: BaseExecutionPipeline,
        profile: LanguageProfile,
        code: str
    ) -> AsyncContextManager[None]:
        ...
