from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payload_id: str
    body: str
