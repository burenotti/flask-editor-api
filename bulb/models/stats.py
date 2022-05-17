from pydantic import BaseModel

__all__ = [
    'Language',
    'Stats'
]


class Language(BaseModel):
    language: str
    versions: list[str]


class Stats(BaseModel):
    available_languages: list[Language]
