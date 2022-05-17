import asyncio

from runbox import DockerSandbox

from bulb.models import InputMessage, TerminateMessage, FinishMessage, \
    OutputMessage
from .proto import InputStream, OutputStream


class SandboxObserver:

    def __init__(
        self,
        sandbox: DockerSandbox,
        input_stream: InputStream,
        output_stream: OutputStream,
    ):
        self.sandbox = sandbox
        self.input_stream = input_stream
        self.output_stream = output_stream

    async def handle_input(self):
        io = self.sandbox._stream
        async for message in self.input_stream:
            if isinstance(message, InputMessage):
                await io.write_in(message.data.encode('utf-8'))
            elif isinstance(message, TerminateMessage):
                await self.sandbox.kill()

    async def handle_output(self):
        while message := await self.sandbox._stream.read_out():
            stream_types = {1: 'stdout', 2: 'stderr'}
            stream_type = stream_types.get(message.stream)
            message_data = message.data.decode('utf-8')

            message = OutputMessage(data=message_data, stream=stream_type)
            await self.output_stream.write(message)

    async def handle_sandbox_finish(self):
        state = await self.sandbox.state()
        message = FinishMessage(**state.dict(by_alias=True))
        await self.output_stream.write(message)

    async def wait(self) -> None:

        input_task = asyncio.create_task(self.handle_input())
        output_task = asyncio.create_task(self.handle_output())

        await self.sandbox.wait()

        if not input_task.done():
            input_task.cancel()

        await output_task

        await self.handle_sandbox_finish()
