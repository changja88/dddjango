from .contract.exception.invalid_card_selection_published_error import (
    InvalidCardSelectionPublishedError,
)
from .contract.request.read_cards_request import ReadCardsRequest
from .contract.response.read_cards_response import ReadCardsResponse


def read_cards_query(request: ReadCardsRequest) -> ReadCardsResponse:
    if request.selection == "unknown":
        raise InvalidCardSelectionPublishedError("UNKNOWN_CARD")
    return ReadCardsResponse(code="OK", reading=request.selection)
