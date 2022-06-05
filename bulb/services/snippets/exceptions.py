from fastapi import HTTPException


class SnippetAlreadyExists(HTTPException):

    def __init__(self, creator_username: str, name: str):
        self.name = name
        self.creator_username = creator_username
        super().__init__(
            status_code=400,
            detail={
                "error_summary": "Snippet with this name already exists",
                "name": self.name,
                "creator_username": self.creator_username,
            }
        )


class SnippetPrivateOrNotExists(HTTPException):

    def __init__(self):
        super(SnippetPrivateOrNotExists, self).__init__(
            status_code=400,
            detail={
                "error_summary": "Snippet does not exist or private",
            }
        )


class CreatorAccessRequired(HTTPException):

    def __init__(self, ):
        super(CreatorAccessRequired, self).__init__(
            status_code=403,
            detail={
                "error_summary": "You need to be an owner of a snippet to do this",
            }
        )


class UnsupportedLanguage(HTTPException):

    def __init__(self, language: str, version: str):
        super().__init__(
            status_code=422,
            detail={
                "error_summary": "Language of this version is not supported",
                "language": language,
                "version": version,
            }
        )
