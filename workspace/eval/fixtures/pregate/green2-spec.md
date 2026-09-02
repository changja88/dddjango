# 미니 설계 명세 — billing BC 스텁 충실도 4계열 (green2 픽스처)

수리 배치(2026-09-02)의 4계열을 고정한다: ⑴ 수신자 표기 메서드(중복 self 소멸)
⑵ ABC 선언형 렌더(@abstractmethod+`...` — #212/#283) ⑶ apps.py 정형 필드 보충(#329/#332)
⑷ 모델 Meta.db_table 합성(연속 대문자 snake — #630). 예보 0(green)이 기대값이다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/application_layer/port/invoice_render/invoice_render_port.py	# ABC 포트
add	application/billing/driven_layer/adapter/invoice_render/pdf_adapter.py	# 구현 짝
add	application/billing/driven_layer/django_billing/apps.py	# 정형 보충 대상(필드 결손)
add	application/billing/driven_layer/django_billing/models/http_log_model.py	# 연속 대문자 모델
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/billing/application_layer/port/invoice_render/invoice_render_port.py::InvoiceRenderPort(ABC) {}
application/billing/application_layer/port/invoice_render/invoice_render_port.py::InvoiceRenderPort.render(self, *, number: str) -> bytes
application/billing/driven_layer/adapter/invoice_render/pdf_adapter.py::PdfInvoiceRenderAdapter(InvoiceRenderPort) {}
application/billing/driven_layer/adapter/invoice_render/pdf_adapter.py::PdfInvoiceRenderAdapter.render(*, number: str) -> bytes
application/billing/driven_layer/django_billing/apps.py::BillingConfig(AppConfig) {}
application/billing/driven_layer/django_billing/models/http_log_model.py::HTTPLogModel(Model) {}
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/billing/driven_layer/adapter/invoice_render/pdf_adapter.py	from application.billing.application_layer.port.invoice_render.invoice_render_port import InvoiceRenderPort
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (이번 슬라이스 없음) | — | — | — | — | — |

## 예외 번역표

<!-- machine: exception-map -->
```exceptions
```
