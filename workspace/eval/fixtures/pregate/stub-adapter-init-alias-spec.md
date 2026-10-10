# 미니 설계 명세 — orders BC 시계 어댑터 패키지 · `__init__.py` 에 별칭만(스텁 픽스처 P4′ — 진짜 위반)

P3 과 같고 `__init__.py` 에 모듈 별칭 한 줄만 더한다(symbols 의 `alias` 행 — 클래스 · 함수 symbol 없음).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	# 재수출 + 별칭
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
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py::alias DefaultClock = SystemClockAdapter
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	from .adapter.system_clock_adapter import SystemClockAdapter as SystemClockAdapter
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	from application.orders.application_layer.port.clock.clock_port import ClockPort
```
