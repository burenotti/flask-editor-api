import pathlib
from typing import AsyncContextManager

from runbox import SandboxBuilder, DockerSandbox
from runbox.docker.utils import write_files
from runbox.models import File

from bulb.base_execution_pipeline import BaseExecutionPipeline
from bulb.cfg import LanguageProfile, config
from bulb.solution_builder import SolutionBuilder

__all__ = ['BuildAndMountAt', 'CreateSandbox', 'Run', 'WriteSourceCode']


class BuildAndMountAt:

    def __init__(self, at: pathlib.Path | str):
        self.mount_at = pathlib.Path(at)

    async def __call__(
        self,
        context: BaseExecutionPipeline,
        profile: LanguageProfile,
        code: str
    ) -> AsyncContextManager[None]:
        builder = SolutionBuilder(
            profile=profile.build_profile,
            executor=context.executor
        )
        source_file = File(content=code, name='source')
        async with builder.build([source_file]) as build_volume:
            context.builder = context.builder.mount(build_volume, self.mount_at)
            yield


class CreateSandbox:

    def __init__(self, sandbox_key: str = "sandbox"):
        self.sandbox_key = sandbox_key

    async def __call__(
        self,
        context: BaseExecutionPipeline,
        profile: LanguageProfile,
        code: str
    ) -> AsyncContextManager[None]:
        sandbox = await SandboxBuilder() \
            .with_profile(profile.profile) \
            .with_limits(config.limits) \
            .create(context.executor)

        async with sandbox:
            context.shared_state[self.sandbox_key] = sandbox
            yield


class Run:

    def __init__(self, sandbox_key: str):
        self.sandbox_key = sandbox_key

    async def __call__(
        self,
        context: BaseExecutionPipeline,
        profile: LanguageProfile,
        code: str
    ) -> AsyncContextManager[None]:
        sandbox: DockerSandbox = context.shared_state[self.sandbox_key]
        await sandbox.run()
        yield


class WriteSourceCode:

    def __init__(self, at: pathlib.Path | str, sandbox_key: str = "sandbox"):
        self.sandbox_key = sandbox_key
        self.path = pathlib.Path(at)

    async def __call__(
        self,
        context: BaseExecutionPipeline,
        profile: LanguageProfile,
        code: str
    ) -> AsyncContextManager[None]:
        sandbox: DockerSandbox = context.shared_state[self.sandbox_key]
        directory = self.path.parent
        filename = self.path.name
        file = File(name=filename, content=code)
        await write_files(sandbox._container, self.path.parent, [file])
        yield
