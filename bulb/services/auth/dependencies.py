from fastapi import Depends

from bulb.cfg import config
from bulb.models.user import User
from .github_oauth import GithubOAuth
from bulb.services.auth.exceptions import NotAuthenticated

github_oauth = GithubOAuth(
    config.github,
    authorization_url='/oauth/github/authorize',
    token_url='/oauth/github/token',
    tags=['Github Authentication']
)


async def get_current_user(
    user: User | None = Depends(github_oauth),
) -> User | None:
    return user


async def get_authenticated_user(
    user: User | None = Depends(get_current_user),
) -> User | None:
    if user is None:
        raise NotAuthenticated()

    return user
