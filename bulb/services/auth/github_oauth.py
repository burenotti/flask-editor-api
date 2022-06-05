from typing import Sequence

import aiohttp

from . import jwt
from .abstract_oauth import (
    AbstractExternalOAuth, aiohttp_session
)

__all__ = ['GithubOAuth']

from bulb.cfg import ExternalOAuthConfig
from bulb.models.user import User, Token
from bulb.models.github_oauth import GithubUserMapper


class GithubOAuth(AbstractExternalOAuth):
    token_model = Token

    def __init__(
        self,
        config: ExternalOAuthConfig,
        token_url: str = None,
        authorization_url: str = None,
        session: aiohttp.ClientSession = None,
        tags: Sequence[str] = None,
    ):
        AbstractExternalOAuth.__init__(
            self,
            config=config,
            name="GitHub",
            token_url=token_url,
            authorization_url=authorization_url,
            tags=tags
        )
        self.session = session

    async def _init(self):
        self.session = self.session or await aiohttp_session()

    async def get_email(self, token: Token) -> str:
        await self._init()
        token_header = f"{token.token_type} {token.access_token}"
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

    async def get_user(self, token: Token) -> User:
        await self._init()
        token = Token.parse_obj(token)
        request = self.session.get(
            url='https://api.github.com/user',
            headers={
                "Authorization": f"{token.token_type} {token.access_token}"
            },
        )
        async with request as response:
            raw_user = await response.json()
            if not raw_user.get('email'):
                email = await self.get_email(token)
                raw_user["email"] = email
            mapper = GithubUserMapper.parse_obj(raw_user)
            return User(**mapper.dict())

    async def handle_access_token(self, token: Token) -> Token:
        user = await self.get_user(token)
        token = jwt.create_token(user)
        return token

    @classmethod
    async def get_current_user(cls, token: str) -> User:
        return jwt.decode_user(token)
