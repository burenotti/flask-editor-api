import asyncio
from contextlib import asynccontextmanager
from typing import Callable, Awaitable, AsyncIterable

from runbox import DockerExecutor, SandboxBuilder, DockerSandbox
from runbox.docker.exceptions import SandboxError
from runbox.models import File, SandboxState
from runbox.proto import SandboxIO
from starlette.websockets import WebSocket

from bulb.cfg import config, LanguageProfile
from bulb.exceptions import MissingProfileError
from bulb.models import OutputMessage

StreamType = str
Output = str
Callback = Callable[[Output, StreamType], Awaitable]

executor = DockerExecutor()


async def run_code(
        language: str,
        code: str,
        get_input: AsyncIterable[str],
        on_output: Callback,
        version: str | None = None,
) -> SandboxState:
    async with create_sandbox(language, code, version) as sandbox:
        sandbox: DockerSandbox
        io = await sandbox.run()

        input_task = asyncio.create_task(send_input(get_input, io))
        output_task = asyncio.create_task(read_output(io, on_output))

        await sandbox.wait()
        state = await sandbox.state()

        if not input_task.done():
            input_task.cancel()

        await output_task

        return state


async def read_output(
        io: SandboxIO,
        on_output: Callback,
):
    while message := await io.read_out():
        stream_type = {1: 'stdout', 2: 'stderr'}
        await on_output(message.data.decode('utf-8'), stream_type.get(message.stream))


async def send_input(
        stream: AsyncIterable[str],
        io: SandboxIO,
):
    async for data in stream:
        await io.write_in(data.encode('utf-8'))


async def get_input_ws(ws: WebSocket):
    while data := await ws.receive_text():
        yield data


def send_output_ws(ws: WebSocket):
    async def send(data: Output, stream: StreamType):
        await ws.send_text(OutputMessage(
            data=data,
            stream=stream,
        ).json())

    return send


def get_profile(language: str, version: str | None = None) -> LanguageProfile:
    suitable = [
        lang for lang in config.languages
        if lang.language == language and
           (lang.version == version or version is None)
    ]

    if suitable:
        return suitable[0]
    else:
        raise MissingProfileError(language, version)


@asynccontextmanager
async def create_sandbox(language: str, code: str, version: str | None = None):
    file = File(name='code', content=code)

    profile = get_profile(language, version)
    async with executor.workdir() as workdir:
        builder = SandboxBuilder() \
            .with_limits(config.limits) \
            .add_files(file) \
            .mount(workdir, '/sandbox')

        if profile.build_required:
            builder_sandbox = await builder \
                .with_profile(profile.build_profile) \
                .create(executor)

            async with builder_sandbox:
                await builder_sandbox.run()
                await builder_sandbox.wait()
                state = await builder_sandbox.state()
                if state.exit_code != 0:
                    logs = await builder_sandbox.log(stdout=True, stderr=True)
                    raise SandboxError("Build failed", logs)

        sandbox = await builder \
            .with_profile(profile.profile) \
            .create(executor)

        async with sandbox:

            yield sandbox

# async def create_result_response(state: SandboxState):
