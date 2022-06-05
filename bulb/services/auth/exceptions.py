from fastapi import HTTPException


class NotAuthenticated(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=401,
            detail={
                "error_summary": "Not authenticated",
            }
        )
