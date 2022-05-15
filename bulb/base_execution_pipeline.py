from __future__ import annotations

from contextlib import suppress
from typing import Any, Iterator

from runbox import DockerExecutor, SandboxBuilder

from bulb.cfg import LanguageProfile
from bulb.proto import BuildStage


class BaseExecutionPipeline:

    def __init__(self, executor: DockerExecutor):
        self.executor = executor
        self.builder = SandboxBuilder()
        self.stages: list[BuildStage] = []
        self.shared_state: dict[str, Any] = {}

    def then(self, stage: BuildStage) -> BaseExecutionPipeline:
        self.stages.append(stage)
        return self

    async def execute(self, profile: LanguageProfile, code: str):
        async def _exec(stage_iter: Iterator[BuildStage]):
            with suppress(StopIteration):
                stage = next(stage_iter)
                async with stage(self, profile, code):
                    await _exec(stage_iter)

        await _exec(iter(self.stages))
