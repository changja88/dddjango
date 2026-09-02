# 미니 설계 명세 — billing BC 사설 보조 타입·대입식 필드·마이그레이션 정형 (green3 픽스처)

수리 배치 2 Part 1(2026-09-03)의 ④′·⑤ 계열을 고정한다: ⑴ 사설 보조 타입 `_InvoiceTotalPart {…}` +
메서드 행 `_InvoiceTotalPart.value(self) -> int`(파서가 클래스로 분류 — 검사기의 사설 면제 경로를 스텁이
그대로 탄다) ⑵ Django 필드 대입식 `name = <식>` 모델 필드 ⑶ `migrations/__init__.py` 빈 파일 +
`migrations/0001_initial.py` 정형 보충(symbols 결손 — Migration 클래스 1·`initial = True`).
예보 0(green)이 기대값이다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/domain_layer/shared_value_object/invoice_total.py	# 값 객체 + 사설 보조 타입
add	application/billing/driven_layer/django_billing/models/invoice_model.py	# 대입식 필드 모델
add	application/billing/driven_layer/django_billing/migrations/__init__.py	# 빈 파일 정형
add	application/billing/driven_layer/django_billing/migrations/0001_initial.py	# 정형 보충(symbols 결손)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/billing/domain_layer/shared_value_object/invoice_total.py::InvoiceTotal {amount: int, currency: str}
application/billing/domain_layer/shared_value_object/invoice_total.py::_InvoiceTotalPart {amount: int}
application/billing/domain_layer/shared_value_object/invoice_total.py::_InvoiceTotalPart.value(self) -> int
application/billing/driven_layer/django_billing/models/invoice_model.py::InvoiceModel(Model) {number = models.CharField(max_length=32), total = models.IntegerField()}
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (이번 슬라이스 없음) | — | — | — | — | — |

## 예외 번역표

<!-- machine: exception-map -->
```exceptions
```
