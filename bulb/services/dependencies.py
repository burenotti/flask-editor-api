from functools import partial

from fastapi import Body, Depends, Path

from bulb.cfg import config
from bulb.models.snippets import SnippetCreate, Snippet, SnippetIdentity
from bulb.models.user import User
from bulb.services import SnippetsRepo
from bulb.services.auth.dependencies import get_current_user_or_none
from bulb.services.snippets.exceptions import UnsupportedLanguage, SnippetPrivateOrNotExists
from bulb.services.snippets.permissions import has_creator_permission


def is_owner(user: User, snippet: SnippetIdentity):
    return user.username == snippet.creator_username


def can_read_snippet(user, snippet: Snippet):
    return snippet.public or is_owner(user, snippet)


def check_language(snippet: SnippetCreate = Body(...)):
    is_language_supported = bool([lang for lang in config.languages if
                                  lang.language == snippet.language and
                                  lang.version == snippet.language_version])

    if not is_language_supported:
        raise UnsupportedLanguage(snippet.language, snippet.language_version)

    return snippet


def snippet_identity_from_path(
    creator_username: str = Path(...),
    name: str = Path(...),
) -> SnippetIdentity:
    return SnippetIdentity(
        creator_username=creator_username,
        name=name,
    )


async def get_snippet(
    repo: SnippetsRepo = Depends(),
    snippet_identity: SnippetIdentity = Depends(snippet_identity_from_path)
) -> Snippet | None:
    snippet = await repo.get(**snippet_identity.dict())
    return snippet


async def get_snippet_if_allowed(
    user: User = Depends(get_current_user_or_none),
    snippet: Snippet | None = Depends(get_snippet),
) -> Snippet:
    if not snippet or not can_read_snippet(user, snippet):
        raise SnippetPrivateOrNotExists()

    return snippet


async def get_snippets(
    repo: SnippetsRepo = Depends(),
    creator_username: str = Path(...),
    public_only: bool = Depends(has_creator_permission),
) -> list[Snippet]:
    return await repo.list(creator_username, public_only=public_only)


get_all_snippets = partial(get_snippets, public_only=False)
get_public_snippets = partial(get_snippets, public_only=True)
