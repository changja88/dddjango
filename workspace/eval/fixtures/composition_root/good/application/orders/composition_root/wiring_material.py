"""orders 결선 재료 — 교체 대상이 아닌 공유 생성 지식."""
from __future__ import annotations

from django.conf import settings

from application.orders.domain_layer.order.value_object.order_thresholds import OrderThresholds
from application.orders.domain_layer.shared_value_object.language_code import LanguageCode


def operating_language() -> str:
    """프로젝트 운영 언어 설정 값을 읽는다."""
    return settings.LANGUAGE_CODE


def default_language() -> LanguageCode:
    """프로젝트 기본 번역 언어를 orders 언어 코드로 만든다."""
    return LanguageCode(settings.PARLER_DEFAULT_LANGUAGE_CODE)


def order_thresholds() -> OrderThresholds:
    """주문 경고 금액과 차단 금액의 조합을 만든다."""
    return OrderThresholds.create(warning=settings.ORDERS_WARNING_AMOUNT, block=1000000)
