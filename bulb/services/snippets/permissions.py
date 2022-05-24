from fastapi import Depends
from fastapi.params import Path

from bulb.models.user import User
from .exceptions import CreatorAccessRequired
from ..permissions import get_current_user


async def get_snippet_creator(
    user: User = Depends(get_current_user),
    creator_username: str = Path(...),
) -> User:
    if user.username != creator_username:
        raise CreatorAccessRequired()

    return user


async def has_creator_permission(
    user: User = Depends(get_current_user),
    creator_username: str = Path(...),
) -> bool:
    return user.username == creator_username
