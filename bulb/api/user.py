from fastapi import APIRouter, Depends

from bulb.api.auth import github_oauth
from bulb.models.user import User

router = APIRouter()


@router.get(
    '/me',
    response_model=User,
)
async def get_current_user(user: User = Depends(github_oauth)) -> User:
    return user
