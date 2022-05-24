from fastapi import APIRouter

from ..services.permissions import github_oauth

router = APIRouter()

router.include_router(github_oauth.router, prefix="/github")
