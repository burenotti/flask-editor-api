class BuildFailedError(Exception):

    def __init__(self, logs: list[str]):
        super().__init__(logs)
        self.logs = logs


class MissingProfileError(Exception):

    def __init__(self, language: str, version: str):
        super().__init__("Missing profile:", language, version)
        self.language = language
        self.version = version
