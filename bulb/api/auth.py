from fastapi import APIRouter

from ..cfg import config
from ..services import GithubOAuth

router = APIRouter()

github_oauth = GithubOAuth(
    config.github,
    authorization_url='/oauth/github/authorize',
    token_url='/oauth/github/token',
    tags=['Github Authentication']
)
router.include_router(github_oauth.router, prefix="/github")
