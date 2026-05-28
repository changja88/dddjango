"""요청 본문 파서 — application/json만 허용하는 콘텐츠 협상 (설계 명세 section 2.3, 2.5).

요청 본문 미디어 타입이 application/json이 아니면 파싱을 시도하지 않고
UnsupportedMediaTypeError를 발생시켜 어댑터에서 415 problem+json으로 변환한다.
정확성(파싱 성공 여부)이 아니라 Content-Type 자체로 협상한다.
"""

from __future__ import annotations

from django.http import HttpRequest
from ninja.parser import Parser
from ninja.types import DictStrAny

from catalog.api.errors import UnsupportedMediaTypeError

_JSON_MEDIA_TYPE = "application/json"


class JsonOnlyParser(Parser):
    """본문 Content-Type이 application/json일 때만 파싱한다."""

    def parse_body(self, request: HttpRequest) -> DictStrAny:
        if request.content_type != _JSON_MEDIA_TYPE:
            raise UnsupportedMediaTypeError()
        return super().parse_body(request)
