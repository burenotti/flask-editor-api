from fastapi import APIRouter

from . import execution

router = APIRouter()

router.include_router(execution.router)
