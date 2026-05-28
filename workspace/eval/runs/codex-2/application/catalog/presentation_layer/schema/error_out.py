from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProblemDetails:
    type: str
    title: str
    status: int
    detail: str
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }
        body.update(self.extensions)
        return body

