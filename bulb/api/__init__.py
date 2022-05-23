from fastapi import APIRouter

from . import (
    execution,
    auth,
    user,
    snippets,
)

router = APIRouter()

router.include_router(execution.router)
router.include_router(user.router, prefix='/user')
router.include_router(auth.router, prefix="/oauth")
router.include_router(snippets.router, prefix='/snippet')
