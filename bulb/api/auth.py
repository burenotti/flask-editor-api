from fastapi import APIRouter

from ..cfg import config

router = APIRouter()

github_oauth = GithubOAuth(config.github, tags=['Github Authentication'])
router.include_router(github_oauth.router, prefix="/github")
