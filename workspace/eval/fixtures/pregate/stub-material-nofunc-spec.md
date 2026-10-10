# 미니 설계 명세 — orders BC 재료 파일 · 함수 symbol 없음(스텁 픽스처 P1-nofunc — 스텁 글 대조)

재료 파일을 새로 만들되 재료 함수 symbol 이 없다(값 객체 import 만). 정형 본문이 없으므로 settings 보충도 없다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/composition_root/wiring_material.py	# 재료 파일(새로 · 함수 없음)
empty	application/orders/composition_root/dependency_wiring.py	# 고정 파일(#488)
empty	application/orders/composition_root/event_wiring.py	# 고정 파일(#488)
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/composition_root/wiring_material.py	from application.orders.domain_layer.shared_value_object.language_code import LanguageCode
```
