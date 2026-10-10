# 미니 설계 명세 — orders BC 재료 함수 · 반환 타입 허용 밖(스텁 픽스처 P2 — D17 소유 · #652 진짜 위반)

P1(`stub-material-spec.md`)과 같고 재료 함수의 반환 주석이 `dict`(F3 허용 밖 — F2 클래스 · str · int · bool · float 아님)다.
정형 본문(`return settings.PREGATE_STUB`)이 본문 꼴을 지나므로 다음 탈락인 «반환 주석» #652 가 예보돼야 한다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/composition_root/wiring_material.py	# 재료 파일(새로)
empty	application/orders/composition_root/dependency_wiring.py	# 고정 파일(#488)
empty	application/orders/composition_root/event_wiring.py	# 고정 파일(#488)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/composition_root/wiring_material.py::default_language() -> dict
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/composition_root/wiring_material.py	from django.conf import settings
application/orders/composition_root/wiring_material.py	from application.orders.domain_layer.shared_value_object.language_code import LanguageCode
```
