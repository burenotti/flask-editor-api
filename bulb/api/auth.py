from fastapi import APIRouter

from ..cfg import config
from ..services import RedirectGithubOAuth

router = APIRouter()

github_oauth = RedirectGithubOAuth(config.github, tags=['Github Authentication'])
router.include_router(github_oauth.router, prefix="/github")
