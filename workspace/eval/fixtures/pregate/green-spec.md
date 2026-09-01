# 미니 설계 명세 — billing BC 인보이스 번호 슬라이스 (green 픽스처)

pre-gate 기계 블록 5종([신규 1]~[신규 5])을 모두 갖춘 최소 명세. 신규 BC `billing` 을
열고 값 객체 하나 + 단위/e2e 테스트 자리를 계획한다 — 예보 0(green)이 기대값이다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/domain_layer/shared_value_object/invoice_number.py	# 값 객체
add	application/billing/test/unit/test_invoice_number.py	# 단위 테스트 자리
add	application/billing/test/e2e/test_invoice_flow.py	# e2e 자리
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
