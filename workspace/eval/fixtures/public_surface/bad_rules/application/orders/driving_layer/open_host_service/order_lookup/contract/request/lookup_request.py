from dataclasses import dataclass

from ..exception.malformed_lookup_payload_error import MalformedLookupPayloadError


@dataclass(frozen=True)
class LookupRequest:
    order_id: str

    def __post_init__(self) -> None:
        if not self.order_id:
            raise MalformedLookupPayloadError("EMPTY_ID")
