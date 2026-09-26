# 미니 명세 — 승인 머지 유입(F4-21 · 로드맵 3 S-1)

기준선 이후 발주자 승인 머지가 main 에서 추가 1(`config/inflow_settings.py`) · 수정 1(`config/api.py` 에
`INFLOW_ROUTE`) · 삭제 1(`config/celery.py`)을 들여온 레인의 재발화 판형이다. `--approved-merge-file` 이 없으면
update 대상이 «기준선 이후 실존» 형식 red 이고, 있으면 유입이 사본에 실려 green · 실존 결손 0(수정 유입의 새 이름)이다.

## 파일 계획

<!-- machine: file-plan -->
```paths
update	config/inflow_settings.py	# 승인 머지로 들어온 파일
update	config/settings/base.py	# 수정 유입의 새 이름을 소비
add	application/billing/domain_layer/shared_value_object/invoice_number.py	# 값 객체
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/billing/domain_layer/shared_value_object/invoice_number.py::InvoiceNumber {value: str}
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
config/settings/base.py	from config.api import INFLOW_ROUTE
```
