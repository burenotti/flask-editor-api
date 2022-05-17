from __future__ import annotations

from contextlib import asynccontextmanager
from typing import (
    AsyncIterable, Protocol, AsyncContextManager,
    TYPE_CHECKING, Any
)

from runbox import DockerExecutor, SandboxBuilder

from bulb.cfg import LanguageProfile
from bulb.models import WebsocketMessage

if TYPE_CHECKING:
    from .base_execution_pipeline import PipelineState


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
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        ...


class ExecutionPipeline(Protocol):

    builder: SandboxBuilder
    profile: LanguageProfile

    def with_profile(self, profile: LanguageProfile) -> ExecutionPipeline:
        ...

    def then(self, stage: BuildStage) -> ExecutionPipeline:
        ...

    async def execute(
        self,
        executor: DockerExecutor,
        code: str,
        initial_shared_state: dict[str, Any] = None
    ):
        ...

    def copy(self) -> ExecutionPipeline:
        ...
