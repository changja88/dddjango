# 미니 설계 명세 — 재료 파일과 이름만 같은 다른 자리(스텁 픽스처 P1-elsewhere — 스텁 글 대조 짝)

`wiring_material.py` 이름의 파일 둘을 재료 파일 자리(`application/<bc>/composition_root/wiring_material.py`) 밖에 둔다 —
`composition_root/` 한 단 아래와 다른 층. 둘 다 정형 본문 · settings 보충 대상이 아니다(`raise NotImplementedError` 그대로).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/composition_root/legacy/wiring_material.py	# composition_root 한 단 아래
add	application/orders/domain_layer/wiring_material.py	# 다른 층
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/composition_root/legacy/wiring_material.py::default_language() -> str
application/orders/domain_layer/wiring_material.py::default_language() -> str
```
