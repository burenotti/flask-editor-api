from typing import AsyncIterable

from fastapi import WebSocket

from bulb.models import TerminateMessage, InputMessage, WebsocketMessage


class WebsocketInputStream:

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.router = {
            'terminate_message': TerminateMessage,
            'input_message': InputMessage,
        }

    async def __aiter__(self) -> AsyncIterable[WebsocketMessage]:
        while json := await self.websocket.receive_json():
            msg_type = self.router.get(json['message_type'])
            yield msg_type.parse_obj(json)


class WebsocketOutputStream:

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def write(self, message: WebsocketMessage) -> None:
        await self.websocket.send_text(message.json())
