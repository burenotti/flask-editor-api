from fastapi import APIRouter

from bulb.services.auth.dependencies import github_oauth

router = APIRouter()

router.include_router(github_oauth.router, prefix="/github")
