# 미니 설계 명세 — orders BC 재료 함수 · settings import 괄호 꼴(스텁 픽스처 P1″a)

P1 과 같고 settings import 를 `from django.conf import (settings)` 로 적는다(구문으로는 같은 결속).

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
application/orders/composition_root/wiring_material.py	from django.conf import (settings)
application/orders/composition_root/wiring_material.py	from application.orders.domain_layer.shared_value_object.language_code import LanguageCode
```
