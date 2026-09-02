# 미니 설계 명세 — billing BC 인보이스 번호 슬라이스 (계약 실존 red 픽스처)

imports-green-spec 형상 + 결손 3종(⑴ 모듈 부재 `framework.test.nope` · ⑵ 자리표시자 0B `placeholder_helper` ·
⑶ 심볼 미정의 `frozen_clock import Missing`)이 «정확히 그 단계 각 1건»으로 나오고 registry 귀속 0 이라
**exit 5**(권고·비차단)임을 고정한다. ⑴ 은 add 소비자(스텁 전사 — compile 만 · import 는 하지 않는다),
⑵⑶ 은 update 소비자(스텁 미반영 — 실존 판정에는 포함)에 둔다.

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
application/billing/test/unit/test_invoice_number.py	from framework.test.nope import Nope
config/settings/base.py	from framework.test.placeholder_helper import Helper
config/settings/base.py	from framework.test.frozen_clock import Missing
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
