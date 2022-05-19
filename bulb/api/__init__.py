from fastapi import APIRouter

from . import execution
from . import auth

router = APIRouter()

router.include_router(execution.router)
router.include_router(auth.router, prefix="/oauth")
