from typing import AsyncIterable, Protocol

from bulb.cfg import LanguageProfile
from bulb.models import WebsocketMessage


class ProfileRouter:

    def __call__(self, language: str, version: str) -> LanguageProfile:
        ...


InputStream = AsyncIterable[WebsocketMessage]


class OutputStream(Protocol):

    async def write(self, message: WebsocketMessage) -> None:
        ...
