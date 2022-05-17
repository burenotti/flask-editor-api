from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Iterator

from runbox import DockerExecutor, SandboxBuilder

from bulb.cfg import LanguageProfile
from .proto import BuildStage


@dataclass(slots=True, frozen=True)
class PipelineState:
    executor: DockerExecutor
    code: str
    shared: dict[str, Any] = field(default_factory=dict)


class BaseExecutionPipeline:

    def __init__(self):
        self.profile: LanguageProfile | None = None
        self.builder = SandboxBuilder()
        self.stages: list[BuildStage] = []

    def with_profile(self, profile: LanguageProfile) -> BaseExecutionPipeline:
        copy = self.copy()
        copy.profile = profile
        return copy

    def then(self, stage: BuildStage) -> BaseExecutionPipeline:
        self.stages.append(stage)
        return self

    async def execute(
        self,
        executor: DockerExecutor,
        code: str,
        initial_shared_state: dict[str, Any] = None
    ):
        state = PipelineState(executor, code, initial_shared_state or {})

        async def _exec(stage_iter: Iterator[BuildStage]):
            with suppress(StopIteration):
                stage = next(stage_iter)
                async with stage(self, state):
                    await _exec(stage_iter)

        await _exec(iter(self.stages))

    def copy(self) -> BaseExecutionPipeline:
        copy = BaseExecutionPipeline()
        copy.profile = self.profile
        copy.stages = self.stages.copy()
        return copy
