from fastapi import Depends
from runbox import DockerExecutor

from .pipeline_factory import PipelineFactory
from bulb.utils import once_init


@once_init
def get_executor():
    return DockerExecutor()


@once_init
def get_factory() -> PipelineFactory:
    from bulb.loader import factory
    return factory


class RunboxService:

    def __init__(
        self,
        executor: DockerExecutor = Depends(get_executor),
        pipeline_factory: PipelineFactory = Depends(get_factory)
    ):
        self.pipeline_factory = pipeline_factory
        self.executor = executor

    async def run_code(
        self,
        langauge: str,
        version: str | None,
        code: str,
    ):
        await self.pipeline_factory \
            .create_pipeline(langauge, version) \
            .execute(self.executor, code)
