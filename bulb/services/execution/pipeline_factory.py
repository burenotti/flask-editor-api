from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bulb.models import LanguageProfile
from .exceptions import MissingProfileError
from .proto import ExecutionPipeline

PipelineOrCallable = ExecutionPipeline | Callable[[LanguageProfile], ExecutionPipeline]


@dataclass
class Route:
    lang: LanguageProfile
    raw_pipeline: PipelineOrCallable

    @property
    def pipeline(self) -> ExecutionPipeline:
        if callable(self.raw_pipeline):
            return self.raw_pipeline(self.lang)
        else:
            return self.raw_pipeline


class PipelineFactory:

    def __init__(self):
        self.routes: list[Route] = []

    def register(self, lang: LanguageProfile, pipeline: PipelineOrCallable) -> PipelineFactory:
        self.routes.append(Route(lang, pipeline))
        return self

    def _get_route(self, lang: str, lang_ver: str) -> Route:
        filtered = [
            route for route in self.routes
            if route.lang.language == lang and
               (lang_ver is None or lang_ver == route.lang.version)
        ]

        if not filtered:
            raise MissingProfileError(lang, lang_ver)

        return filtered[0]

    def create_pipeline(self, lang: str, lang_ver: str) -> ExecutionPipeline:
        route = self._get_route(lang, lang_ver)
        return route.pipeline
