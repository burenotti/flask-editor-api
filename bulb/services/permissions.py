from fastapi import Depends, Request, HTTPException

from bulb.cfg import config
from bulb.models.user import User
from bulb.services import GithubOAuth

github_oauth = GithubOAuth(
    config.github,
    authorization_url='/oauth/github/authorize',
    token_url='/oauth/github/token',
    tags=['Github Authentication']
)


async def get_current_user(
    user: User = Depends(github_oauth),
):
    return user


async def get_current_user_or_none(
    request: Request
) -> User | None:
    try:
        return await get_current_user(await github_oauth(request))
    except HTTPException:
        return None
