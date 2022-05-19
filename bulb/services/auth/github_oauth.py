from abc import ABC
from typing import Sequence

import aiohttp

from .abstract_oauth import AbstractExternalOAuth, RedirectOnSuccess

__all__ = ['AbstractGithubOAuth']

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
        self.session = session or aiohttp.ClientSession()

    async def get_user(self, access_token: dict[str, str]) -> User:
        request = self.session.get(
            url='https://api.github.com/user',
            headers={
                "Authorization", f"{access_token['token_type']} {access_token['access_token']}"
            },
        )
        async with request as response:
            raw_user = await response.json()
            mapper = GithubUserMapper.parse_obj(raw_user)
            return User(**mapper.dict())


class RedirectGithubOAuth(RedirectOnSuccess, AbstractGithubOAuth):
    redirect_address = "localhost:8000/"
