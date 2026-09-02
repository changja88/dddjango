# 미니 설계 명세 — orders BC 레인 마커 (midlane 픽스처 — E 계열 재발화 판형)

Phase 2 진입 후 명세 개정 재실행(`--base <G1 기준선 SHA>`)의 실행기 계약을 고정한다 — 러너가
합성 저장소 상태를 바꿔 가며 같은 명세로 네 번 돌린다:
E1 계획 add 가 기준선 «이후 커밋»에 실존 → `--base` 명시 → exit 0 · 스텁 판정 · 기실현 0 /
E2 계획 add 가 미커밋 WIP 로 실존 → `--base` 명시 → 기실현 1 · 스텁 대체 판정(실물 판정 혼입 0) /
E3 E2 상태에서 `--base` 미지정 → 형식 red(exit 3) 유지 / E4 계획 add 가 기준선 트리에 실존 →
`--base` 명시해도 형식 red(exit 3) 유지.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/domain_layer/shared_value_object/lane_marker.py	# 값 객체
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/domain_layer/shared_value_object/lane_marker.py::LaneMarker {value: str}
```
