from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_204_NO_CONTENT, HTTP_200_OK
)

from .auth import github_oauth
from ..models.snippets import Snippet, SnippetCreate
from ..models.user import User
from ..services import SnippetsRepo, snippets

router = APIRouter(tags=['Snippets'])


@router.post(
    '/',
    status_code=HTTP_204_NO_CONTENT,
    response_model=None,
)
async def create_snippet(
    snippet: SnippetCreate,
    user: User = Depends(github_oauth),
    service: SnippetsRepo = Depends(),
) -> None:
    await service.add(
        Snippet(
            **snippet.dict(),
            creator_username=user.username,
        )
    )


@router.get(
    '/{creator_username:str}/{name:str}',
    status_code=HTTP_200_OK,
    response_model=Snippet,
)
async def get_snippet(
    snippet: Snippet = Depends(snippets.get_snippet),
) -> Snippet:
    return snippet


@router.get(
    '/{creator_username:str}/list',
    status_code=HTTP_200_OK,
    response_model=list[Snippet],
)
async def list_snippets(
    user: User = Depends(github_oauth),
) -> list[Snippet]:
    pass


@router.delete('/')
async def remove_snippet():
    pass
