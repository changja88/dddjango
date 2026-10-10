# 미니 설계 명세 — orders BC 재료 함수(스텁 거짓 red 픽스처 P1)

`composition_root/wiring_material.py` 를 새로 만들며 재료 함수 하나를 선언한다. 실물 계획은 규칙에 맞는
`return LanguageCode(settings.LANGUAGE_CODE)` 한 문장이지만 symbols 문법에는 본문 자리가 없다 — 스텁 본문이
#652 «본문 꼴»에 걸리는지 본다. 값 객체 모듈은 합성 저장소(`stub_overlay/`)에 있다.

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
application/orders/composition_root/wiring_material.py::default_language() -> LanguageCode
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/composition_root/wiring_material.py	from django.conf import settings
application/orders/composition_root/wiring_material.py	from application.orders.domain_layer.shared_value_object.language_code import LanguageCode
```
