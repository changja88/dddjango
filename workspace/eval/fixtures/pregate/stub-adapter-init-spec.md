# 미니 설계 명세 — orders BC 시계 어댑터 패키지(스텁 거짓 red 픽스처 P3)

어댑터 패키지 `driven_layer/adapter/clock/system_adapter/` 를 새로 만들고 `__init__.py` 에 재수출 한 줄만 둔다
(규칙에 맞는 실물 계획). 스텁 머리의 `from __future__ import annotations` 가 #640 «재수출 전용»에 걸리는지 본다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	# 재수출 한 줄
add	application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	# 구현
empty	application/orders/driven_layer/adapter/clock/system_adapter/adapter/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/command/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/constant/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/contract/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/schema/__init__.py
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py::SystemClockAdapter(ClockPort)
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	from .adapter.system_clock_adapter import SystemClockAdapter as SystemClockAdapter
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	from application.orders.application_layer.port.clock.clock_port import ClockPort
```
