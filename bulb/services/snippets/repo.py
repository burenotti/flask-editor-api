from typing import overload

from fastapi import Depends
from sqlalchemy import delete, select, update

from bulb.database import get_session, AsyncSession
from bulb.models.snippets import Snippet, SnippetIdentity, SnippetInfo
from bulb.services.snippets.exceptions import SnippetAlreadyExists


def _identity_raw(creator_username: str, name: str):
    return ((Snippet.creator_username == creator_username) &
            (Snippet.name == name))


def _identity_snippet(snippet: SnippetIdentity):
    return _identity_raw(
        snippet.creator_username,
        snippet.name
    )


@overload
def identity(creator_username: str, name: str):
    ...


@overload
def identity(snippet: SnippetIdentity):
    ...


def identity(*args):
    match args:
        case [snippet] if isinstance(snippet, SnippetIdentity):
            return _identity_snippet(snippet)
        case [str(username), str(name)]:
            return _identity_raw(username, name)


class SnippetsRepo:

    def __init__(self, session: AsyncSession = Depends(get_session, use_cache=False)):
        self.session = session

    async def add(self, snippet: Snippet) -> None:
        async with self.session:
            self.session.add(snippet)
            await self.session.commit()

    async def get(
        self,
        creator_username: str,
        name: str
    ) -> Snippet | None:
        query = select(Snippet).where(identity(creator_username, name))

        return (await self.session.scalars(query)).one_or_none()

    async def list(
        self,
        creator_username: str,
        public_only: bool = True,
    ) -> list[Snippet]:
        query = select(Snippet).where(
            Snippet.creator_username == creator_username
        )

        if public_only:
            query = query.where(Snippet.public)

        items = await self.session.scalars(query)
        return items.all()

    async def remove(
        self, snippet: SnippetIdentity,
    ) -> None:
        async with self.session.begin():
            await self.session.execute(
                delete(Snippet).where(
                    identity(snippet.creator_username, snippet.name)
                )
            )
            await self.session.commit()

    async def put(self, snippet: SnippetIdentity, new_snippet: Snippet) -> Snippet:
        query = update(Snippet) \
            .where(identity(snippet)) \
            .values(new_snippet.dict()) \
            .returning(Snippet)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().one()

    async def fork(
        self,
        snippet_source: SnippetIdentity,
        snippet_dest: SnippetInfo,
    ) -> None:
        async with self.session:
            code = await self.session.scalar(
                select(Snippet.code).where(identity(snippet_source))
            )

            dest_exists = await self.session.scalar(
                select(True).where(identity(snippet_dest))
            )

            if dest_exists:
                raise SnippetAlreadyExists(snippet_dest.creator_username, snippet_dest.name)

            snippet = Snippet(
                creator_username=snippet_dest.creator_username,
                name=snippet_dest.name,
                code=code,
                public=snippet_dest.public,
            )
            self.session.add(snippet)
            await self.session.commit()
