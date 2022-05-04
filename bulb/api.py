import itertools

from fastapi import APIRouter, WebSocket

from . import services
from .cfg import config
from .exceptions import MissingProfileError, BuildFailedError
from .models import Stats, Language, MissingProfileMessage, BuildFailedMessage, FinishMessage
from .services import send_output_ws, get_input_ws

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
):
    await ws.accept()
    try:
        state = await services.run_code(
            language, code,
            version=version,
            get_input=get_input_ws(ws),
            on_output=send_output_ws(ws),
        )

        await ws.send_text(FinishMessage(**state.dict(by_alias=True)).json())

    except BuildFailedError as why:
        await ws.send_text(BuildFailedMessage(logs=why.logs).json())
    except MissingProfileError:
        await ws.send_text(MissingProfileMessage().json())
