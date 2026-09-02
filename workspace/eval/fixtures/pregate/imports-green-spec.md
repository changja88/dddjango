# 미니 설계 명세 — billing BC 인보이스 번호 슬라이스 (계약 실존 green 픽스처)

green-spec 형상 + boundary-imports 4종(실존 확인 `FrozenClock` · 자기 add 해소 · 서브모듈 형 · 서드파티)이
계약 실존 결손 0 · exit 0 임을 고정한다. 서드파티 행은 **update 소비자**(스텁 미반영 — 실존 판정에는 포함)에 둔다.
합성 저장소 = `mini_repo` + `imports_overlay/`(`framework/test/frozen_clock.py` · 0B `placeholder_helper.py`).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/domain_layer/shared_value_object/invoice_number.py	# 값 객체
add	application/billing/test/unit/test_invoice_number.py	# 단위 테스트 자리
add	application/billing/test/e2e/test_invoice_flow.py	# e2e 자리
update	config/settings/base.py	# 설정 배선(시뮬레이션 밖 — 실존 판정 소비자)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/billing/domain_layer/shared_value_object/invoice_number.py::InvoiceNumber {value: str}
application/billing/test/unit/test_invoice_number.py::test_rejects_blank_value
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/billing/test/unit/test_invoice_number.py	from application.billing.domain_layer.shared_value_object.invoice_number import InvoiceNumber
application/billing/test/unit/test_invoice_number.py	from framework.test.frozen_clock import FrozenClock
application/billing/test/unit/test_invoice_number.py	from framework.test import frozen_clock
config/settings/base.py	from ninja import NinjaAPI
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| InvoiceNumber 검증 | 값 객체 생성 시점 검증 계약 | 빈 번호 유입 | 없음 | add | `application/billing/test/unit/test_invoice_number.py` |
| 인보이스 흐름 e2e | 입구-출구 한 흐름 | 입구 차단 회귀 | 없음 | add | `application/billing/test/e2e/test_invoice_flow.py` [client: yes] |

## 예외 번역표

<!-- machine: exception-map -->
```exceptions
InvoiceNumberInvalid	application/billing/domain_layer/shared_value_object/invoice_number.py
```
