import pathlib
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from runbox import SandboxBuilder, DockerSandbox
from runbox.docker.utils import write_files
from runbox.models import File

from bulb.cfg import config
from .base_execution_pipeline import PipelineState
from .proto import InputStream, OutputStream, ExecutionPipeline
from .sandbox_observer import SandboxObserver
from .solution_builder import SolutionBuilder

__all__ = ['BuildAndMountAt', 'CreateSandbox',
           'Run', 'WriteSourceCode', 'Observe']


class BuildAndMountAt:

    def __init__(self, at: pathlib.Path | str):
        self.mount_at = pathlib.Path(at)

    @asynccontextmanager
    async def __call__(
        self,
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        builder = SolutionBuilder(
            profile=context.profile.build_profile,
            executor=state.executor,
        )
        source_file = File(content=state.code, name='main.cpp')
        async with builder.build([source_file]) as build_volume:
            context.builder = context.builder.mount(build_volume, self.mount_at)
            yield


class CreateSandbox:

    def __init__(self, sandbox_key: str = "sandbox"):
        self.sandbox_key = sandbox_key

    @asynccontextmanager
    async def __call__(
        self,
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        sandbox = await SandboxBuilder() \
            .with_profile(context.profile.profile) \
            .with_limits(config.limits) \
            .create(state.executor)

        async with sandbox:
            state.shared[self.sandbox_key] = sandbox
            yield


class Run:

    def __init__(self, sandbox_key: str):
        self.sandbox_key = sandbox_key

    @asynccontextmanager
    async def __call__(
        self,
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        sandbox: DockerSandbox = state.shared[self.sandbox_key]
        await sandbox.run()
        yield


class WriteSourceCode:

    def __init__(self, at: pathlib.Path | str, sandbox_key: str = "sandbox"):
        self.sandbox_key = sandbox_key
        self.path = pathlib.Path(at)

    @asynccontextmanager
    async def __call__(
        self,
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        sandbox: DockerSandbox = state.shared[self.sandbox_key]
        directory = self.path.parent
        filename = self.path.name
        file = File(name=filename, content=state.code)
        await write_files(sandbox._container, directory, [file])
        yield


class Observe:

    def __init__(
        self,
        sandbox_key: str,
        input_stream_key: str = "sandbox_input_stream",
        output_stream_key: str = "sandbox_output_stream",
    ):
        self.input_stream_key = input_stream_key
        self.output_stream_key = output_stream_key
        self.sandbox_key = sandbox_key

    @asynccontextmanager
    async def __call__(
        self,
        context: ExecutionPipeline,
        state: PipelineState,
    ) -> AsyncContextManager[None]:
        sandbox: DockerSandbox = state.shared[self.sandbox_key]
        input_stream: InputStream = state.shared[self.input_stream_key]
        output_stream: OutputStream = state.shared[self.output_stream_key]
        observer = SandboxObserver(sandbox, input_stream, output_stream)
        await observer.wait()
        yield
