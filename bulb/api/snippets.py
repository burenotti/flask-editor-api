import sqlalchemy.exc
from fastapi import APIRouter, Depends, Path, Body, Response, Query
from starlette.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
)

from bulb.models.snippets import SnippetCreate, Snippet, SnippetIdentity, SnippetPatch, SnippetInfo
from bulb.models.user import User
from ..services import SnippetsRepo
from ..services.dependencies import check_language, get_snippet_if_allowed, \
    snippet_identity_from_path
from ..services.permissions import get_current_user
from ..services.snippets.exceptions import (
    SnippetAlreadyExists
)
from ..services.snippets.permissions import has_creator_permission, get_snippet_creator

router = APIRouter(tags=['Snippets'])


def is_owner(user: User, snippet: SnippetIdentity):
    return user.username == snippet.creator_username


def can_read_snippet(user, snippet: Snippet):
    return snippet.public or is_owner(user, snippet)


def get_snippet_info(
    user: User = Depends(get_current_user),
    fork_name: str = Query(...),
    public: bool = Query(True),
) -> SnippetInfo:
    return SnippetInfo(
        creator_username=user.username,
        name=fork_name,
        public=public,
    )


@router.post(
    '/',
    status_code=HTTP_201_CREATED,
    summary="Creates code snippet",
    dependencies=[Depends(check_language)]
)
async def create(
    repo: SnippetsRepo = Depends(),
    creator: User = Depends(get_current_user),
    snippet: SnippetCreate = Body(...),
) -> None:
    try:
        await repo.add(Snippet(
            creator_username=creator.username,
            name=snippet.name,
            code=snippet.code,
            public=snippet.public,
            language=snippet.language,
            language_version=snippet.language_version,
        ))
    except sqlalchemy.exc.IntegrityError:
        raise SnippetAlreadyExists(creator.username, snippet.name)


@router.get(
    '/{creator_username:str}/name/{name:str}',
    status_code=HTTP_200_OK,
    response_model=Snippet,
    summary="Get code snippet",
)
async def get(
    snippet: Snippet = Depends(get_snippet_if_allowed),
) -> Snippet | None:
    return snippet


@router.get(
    '/{creator_username:str}/list',
    status_code=HTTP_200_OK,
    response_model=list[Snippet],
    summary="Get a list of the user's code snippets",
    description="Returns a list of users code snippets. "
                "Returns all snippets if authorized as same user "
                "else only public will be returned."
)
async def list_snippets(
    repo: SnippetsRepo = Depends(),
    creator_username: str = Path(...),
    public_only: bool = Depends(has_creator_permission),
) -> list[Snippet]:
    return await repo.list(creator_username, public_only)


@router.delete(
    '/{creator_username:str}/name/{name:str}',
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_snippet_creator)],
    summary="Deletes user snippet",
    description="Delete user snippet. "
                "Only creator can delete snippets."
)
async def remove(
    repo: SnippetsRepo = Depends(),
    snippet: SnippetIdentity = Depends(snippet_identity_from_path)
) -> Response:
    await repo.remove(snippet)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.patch(
    '/{creator_username:str}/name/{name:str}',
    dependencies=[Depends(get_snippet_creator)],
    summary="Partially update snippet",
    description="Partially updates snippet. "
                "Only creator of a snippet is allowed to delete it.",
)
async def patch(
    repo: SnippetsRepo = Depends(),
    snippet: Snippet = Depends(get_snippet_if_allowed),
    updated_fields: SnippetPatch = Body(...),
) -> None:
    new_snippet = snippet.copy(update=updated_fields.dict(exclude_unset=True))
    return await repo.put(snippet, new_snippet)


@router.post(
    '/{creator_username:str}/name/{name:str}/fork',
    summary="Forks user snippet",
    description="Copies user snippet. "
                "User is allowed to fork all them snippets "
                "and public snippets of other users.",
    dependencies=[]
)
async def fork(
    snippet: Snippet = Depends(get_snippet_if_allowed),
    dest: SnippetInfo = Depends(get_snippet_info),
    repo: SnippetsRepo = Depends(),

) -> Response:
    await repo.fork(snippet, dest)

    return Response(status_code=HTTP_204_NO_CONTENT)
