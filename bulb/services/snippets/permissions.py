from fastapi import Depends
from fastapi.params import Path

from bulb.models.user import User
from .exceptions import CreatorAccessRequired
from bulb.services.auth.dependencies import get_current_user, get_current_user_or_none


async def get_snippet_creator(
    user: User = Depends(get_current_user),
    creator_username: str = Path(...),
) -> User:
    if user.username != creator_username:
        raise CreatorAccessRequired()

    return user


async def has_creator_permission(
    user: User = Depends(get_current_user_or_none),
    creator_username: str = Path(...),
) -> bool:
    return user and user.username == creator_username
