from abc import ABC
from typing import Sequence

import aiohttp

from .abstract_oauth import (
    AbstractExternalOAuth, RedirectOnSuccess, WrapToken, aiohttp_session
)

__all__ = ['AbstractGithubOAuth', 'RedirectGithubOAuth']

from bulb.cfg import ExternalOAuthConfig
from bulb.models.user import User
from bulb.models.github_oauth import GithubUserMapper


class AbstractGithubOAuth(AbstractExternalOAuth, ABC):

    def __init__(
        self,
        config: ExternalOAuthConfig,
        session: aiohttp.ClientSession = None,
        tags: Sequence[str] = None,
    ):
        super().__init__(config, tags=tags)
        self.session = session

    async def _init(self):
        self.session = self.session or await aiohttp_session()

    async def get_email(self, access_token: dict[str, str]) -> str:
        await self._init()
        token_header = f"{access_token['token_type']} {access_token['access_token']}"
        request = self.session.get(
            url='https://api.github.com/user/public_emails',
            headers={
                "Accept": "application/json",
                "Authorization": token_header,
            },
        )
        async with request as response:
            response = await response.json()

        primary_emails = [email for email in response if email["primary"]]

        email = primary_emails[0] if primary_emails else response[0]
        return email['email']

    async def get_user(self, access_token: dict[str, str]) -> User:
        await self._init()
        request = self.session.get(
            url='https://api.github.com/user',
            headers={
                "Authorization": f"{access_token['token_type']} {access_token['access_token']}"
            },
        )
        async with request as response:
            raw_user = await response.json()
            if not raw_user.get('email'):
                email = await self.get_email(access_token)
                raw_user["email"] = email
            mapper = GithubUserMapper.parse_obj(raw_user)
            return User(**mapper.dict())


class RedirectGithubOAuth(WrapToken, RedirectOnSuccess, AbstractGithubOAuth):
    mapper = User.parse_obj
    redirect_address = "localhost:8000/"
