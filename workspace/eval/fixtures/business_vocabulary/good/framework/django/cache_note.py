from __future__ import annotations

from django.core.cache import cache


def note_hits(key: str) -> object:
    # orders 화면이 이 캐시를 같이 쓰지만, 여기는 기술 헬퍼라 그 사정을 모른다.
    """산문 설명 — promotion 같은 일반 낱말이 문서에 나와도 결합이 아니다."""
    return cache.get(key)
