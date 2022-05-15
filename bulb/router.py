from bulb.cfg import config, LanguageProfile
from bulb.exceptions import MissingProfileError


class DirectProfileRouter:

    def __call__(self, language: str, version: str) -> LanguageProfile:
        suitable = [
            lang for lang in config.languages
            if lang.language == language and
               (lang.version == version or version is None)
        ]

        if suitable:
            return suitable[0]
        else:
            raise MissingProfileError(language, version)
