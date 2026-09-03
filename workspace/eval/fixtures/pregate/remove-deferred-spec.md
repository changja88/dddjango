# 미니 설계 명세 — orders BC 후행 제거 (remove@Ln 픽스처 · E4 판정 밖)

후행 `remove@L1` 한 행이 기준선에 없는 경로를 가리킨다 — 후행 remove 는 G1 승인 시점 상태를 유지하는
격리 조치라 E4 판정 밖이다(현행 «미시뮬레이션» 유지) · 실체화 0 · 결손 0 → skip exit 4 가 기대값이다
(`remove-target-spec.md` 의 짝 — 비후행만 형식 red).

## 파일 계획

<!-- machine: file-plan -->
```paths
remove@L1	application/orders/domain_layer/shared_value_object/nothing.py	# 후행 제거(슬라이스 1 뒤)
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (없음) | — | — | — | retain | — |
