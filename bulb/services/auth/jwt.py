from datetime import timedelta, datetime
from typing import Any

from jose import jwt

from bulb.cfg import config
from bulb.models.user import User, Token

__all__ = ['create_token']


def create_token(
    user: User,
    algorithm: str = config.jwt.algorithm,
    secret: str = config.jwt.secret,
    lifetime: timedelta = config.jwt.token_lifetime,
) -> Token:
    now = datetime.utcnow()
    claims = {
        "iat": now,
        "exp": now + lifetime,
        **user.dict(),
    }
    token = jwt.encode(
        claims=claims,
        key=secret,
        algorithm=algorithm,
    )
    return Token(access_token=token)


def decode(
    token: str,
    algorithms: list[str] = None,
    secret: str = config.jwt.secret,
) -> dict[str, Any]:
    algorithms = algorithms or [config.jwt.algorithm]
    return jwt.decode(
        token=token,
        key=secret,
        algorithms=algorithms,
    )


def decode_user(
    token: str,
    algorithms: list[str] = None,
    secret: str = config.jwt.secret,
):
    return User.parse_obj(decode(token, algorithms, secret))
