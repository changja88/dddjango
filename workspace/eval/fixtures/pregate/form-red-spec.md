# 미니 설계 명세 — 중복 인자 계획 (form-red 픽스처)

compile 격상(symtable 검증)의 자기검증: 수신자 정규화 뒤에도 남는 중복 인자
(`x: int, x: int`)는 형식 red(exit 3)여야 한다 — ast.parse 는 이를 못 잡는다.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/billing/application_layer/port/invoice_render/broken_port.py	# 중복 인자 계획
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/billing/application_layer/port/invoice_render/broken_port.py::BrokenPort(ABC) {}
application/billing/application_layer/port/invoice_render/broken_port.py::BrokenPort.render(self, x: int, x: int) -> bytes
```
