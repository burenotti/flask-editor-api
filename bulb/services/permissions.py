from fastapi import Depends

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
