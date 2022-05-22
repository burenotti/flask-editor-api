import ssl
from abc import abstractmethod, ABC
from typing import Sequence, Any, Callable

import certifi
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, Query, Depends, Request
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from yarl import URL

from bulb.cfg import ExternalOAuthConfig
from bulb.models.user import User, Token
from bulb.services.auth import jwt
from bulb.utils import once_init_async

__all__ = ['AbstractExternalOAuth', 'RedirectOnSuccess']


@once_init_async
async def aiohttp_session():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = TCPConnector(ssl_context=ssl_context)
    return ClientSession(connector=connector)


class AbstractExternalOAuth(ABC):
    user_model: BaseModel

    def __init__(
        self,
        config: ExternalOAuthConfig,
        tags: Sequence[str] = ("Auth",),
    ):
        self._config = config
        self._router = APIRouter(tags=list(tags))

        self._router.add_api_route(
            '/redirect', self.redirect, methods=["GET"])
        self._router.add_api_route(
            '/swap_token', self.swap_token, methods=["GET"], name="swap_token",
        )

    @property
    def router(self):
        return self._router

    async def redirect(self, request: Request):
        redirect_uri = request.url_for("swap_token")
        url = URL(self._config.authorize_url).with_query({
            "redirect_uri": redirect_uri,
            "client_id": self._config.client_id,
            "scope": "read:user,user:email",
        })
        return RedirectResponse(str(url))

    async def swap_token(
        self,
        code: str = Query(...),
        session: ClientSession = Depends(aiohttp_session)
    ):
        params = {
            "code": code,
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        headers = {
            "Accept": "application/json"
        }
        request = session.post(self._config.token_url, params=params, headers=headers)
        async with request as response:
            access_token = await response.json()

        return await self.handle_access_token(access_token)

    @abstractmethod
    async def handle_access_token(self, access_token: dict[str, str]) -> Any:
        pass

    @abstractmethod
    async def get_user(self, access_token: dict[str, str]) -> Any:
        pass


class RedirectOnSuccess:
    redirect_address: str
    access_token_param: str = "access_token"
    token_type_param: str = "token_type"

    async def handle_access_token(self, access_token: dict[str, str]) -> RedirectResponse:
        url = URL(self.redirect_address).update_query({
            self.access_token_param: access_token["access_token"],
            self.token_type_param: access_token["token_type"],
        })

        return RedirectResponse(url)


class WrapToken(AbstractExternalOAuth, ABC):

    mapper: Callable[[dict[str, Any]], User]

    async def handle_access_token(self, access_token: dict[str, str]) -> Any:
        user = await self.get_user(access_token)
        user = self.mapper(user)
        token = jwt.create_token(user)
        return await super().handle_access_token(token.dict())
