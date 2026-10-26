"""void_not_found 예외."""


class VoidNotFound(Exception):
    def __init__(self, branch: str) -> None:
        if not branch:
            raise ValueError("branch")
        super().__init__(branch)
