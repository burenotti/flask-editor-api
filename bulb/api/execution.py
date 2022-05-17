import itertools

from fastapi import APIRouter, WebSocket, Depends

from bulb.cfg import config
from bulb.models import Stats, Language
from bulb.services import RunboxService

router = APIRouter(prefix='/code')


@router.get('/stats', response_model=Stats)
async def get_stats() -> Stats:
    langs = itertools.groupby(config.languages, lambda lang: lang.language)

    return Stats(available_languages=[
        Language(
            language=name,
            versions=[lang.version for lang in group],
        ) for name, group in langs
    ])


@router.websocket('/run')
async def run_code(
    ws: WebSocket,
    language: str,
    code: str,
    version: str | None = None,
    service: RunboxService = Depends(),
):
    await ws.accept()
    await service.run_code(language, version, code, ws)
