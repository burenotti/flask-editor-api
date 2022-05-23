import ssl
from abc import abstractmethod, ABC
from typing import Sequence, Any

import certifi
from aiohttp import ClientSession, TCPConnector
from fastapi import APIRouter, Query, Depends, Request, Form
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import AnyHttpUrl
from pydantic.main import ModelMetaclass
from starlette.responses import RedirectResponse
from yarl import URL

from bulb.cfg import ExternalOAuthConfig
from bulb.utils import once_init_async

__all__ = ['AbstractExternalOAuth', 'aiohttp_session']


@once_init_async
async def aiohttp_session():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = TCPConnector(ssl_context=ssl_context)
    return ClientSession(connector=connector)


class AbstractExternalOAuth(OAuth2AuthorizationCodeBearer, ABC):
    token_model: ModelMetaclass

    def __init__(
        self,
        config: ExternalOAuthConfig,
        authorization_url: AnyHttpUrl = None,
        token_url: AnyHttpUrl = None,
        name: str = None,
        tags: Sequence[str] = ("Auth",),
    ):
        OAuth2AuthorizationCodeBearer.__init__(
            self,
            authorizationUrl=authorization_url,
            tokenUrl=token_url,
        )

        self._config = config
        self.name = name

        self._router = APIRouter(tags=list(tags))

        self._router.add_api_route(
            '/authorize', self.redirect, methods=["GET"],
            summary=f"Get authorization code from {self.name}")
        self._router.add_api_route(
            '/token', self.get_token, methods=["POST"],
            summary=f"Exchange {self.name} authorization code with token",
            response_model=self.token_model)

    @property
    def router(self):
        return self._router

    async def redirect(
        self, redirect_uri: AnyHttpUrl = Query(...)
    ):
        url = URL(self._config.authorize_url).with_query({
            "redirect_uri": redirect_uri,
            "client_id": self._config.client_id,
            "scope": "read:user,user:email",
        })
        return RedirectResponse(str(url))

    async def get_token(
        self,
        code: str = Form(...),
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

    async def __call__(self, request: Request) -> Any:
        token: str = await super().__call__(request)
        return await self.get_current_user(token)

    @abstractmethod
    async def get_current_user(self, token: str) -> Any:
        pass

    @abstractmethod
    async def handle_access_token(self, access_token: dict[str, str]) -> Any:
        pass

    @abstractmethod
    async def get_user(self, access_token: dict[str, str]) -> Any:
        pass
