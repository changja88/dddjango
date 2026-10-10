"""shipping 결선 재료 반례 — `from django.conf import settings` 가 없는 재료 파일(이름째 들이기 반례의 짝이기도 하다)."""
from application.shipping.domain_layer.shipment.value_object.parcel_weight import ParcelWeight


def default_language() -> str:  # 기대: #652 M-lead-b-unbound-settings — (가) 의 settings 가 F2 import 로 묶이지 않음(결속) ⟪한 줄로 정확히 한 번 묶이지 않았다(F2 · 결속)⟫
    """프로젝트 기본 번역 언어 설정 값을 읽는다."""
    return settings.PARLER_DEFAULT_LANGUAGE_CODE


def settings() -> ParcelWeight:  # 기대: #652 M-lead-a-settings-name — 재료 함수 이름 = settings(F3 결속) ⟪재료 이름 `settings` 이 settings · str · int · bool · float 와 같다(F3 결속)⟫
    return ParcelWeight(10)
