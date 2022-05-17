from fastapi import Depends, WebSocket

from bulb.loader import executor
from bulb.utils import once_init
from .pipeline_factory import PipelineFactory
from .stream import WebsocketInputStream, WebsocketOutputStream


@once_init
def get_factory() -> PipelineFactory:
    from bulb.loader import factory
    return factory


class RunboxService:

    def __init__(
        self,
        pipeline_factory: PipelineFactory = Depends(get_factory)
    ):
        self.pipeline_factory = pipeline_factory
        self.executor = executor

    async def run_code(
        self,
        langauge: str,
        version: str | None,
        code: str,
        ws: WebSocket,
    ):
        state = {
            "sandbox_input_stream": WebsocketInputStream(ws),
            "sandbox_output_stream": WebsocketOutputStream(ws),
        }
        await self.pipeline_factory \
            .create_pipeline(langauge, version) \
            .execute(self.executor, code, state)
