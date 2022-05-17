from contextlib import asynccontextmanager

from aiodocker.volumes import DockerVolume
from runbox import Mount, DockerExecutor, SandboxBuilder, DockerSandbox
from runbox.models import DockerProfile, File

from bulb.cfg import config
from .exceptions import BuildFailedError


class SolutionBuilder:

    def __init__(self, profile: DockerProfile, executor: DockerExecutor):
        self.profile = profile
        self.executor = executor

    @asynccontextmanager
    async def build(self, files: list[File]) -> DockerVolume:
        async with self.executor.workdir() as workdir:
            workdir: DockerVolume
            mount = Mount(volume=workdir, bind=self.profile.workdir)
            sandbox = await self._create_sandbox(files, mount)
            async with sandbox:
                await self._execute_build(sandbox)
            yield workdir

    async def _create_sandbox(self, files: list[File], workdir: Mount) -> DockerSandbox:
        sandbox = await SandboxBuilder() \
            .with_profile(self.profile) \
            .with_limits(config.limits) \
            .mount(**workdir.dict()) \
            .add_files(*files) \
            .create(self.executor)

        return sandbox

    @classmethod
    async def _execute_build(cls, sandbox: DockerSandbox) -> None:
        await sandbox.run()
        await sandbox.wait()

        state = await sandbox.state()

        if state.exit_code != 0:
            logs = await sandbox.log(stdout=True, stderr=True)
            raise BuildFailedError(logs)
