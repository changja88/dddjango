# 미니 설계 명세 — orders BC 죽은 값 객체 제거 (remove 대상 부재 픽스처 · 차단 모드 E4)

비후행 `remove` 한 행이 기준선에 없는 경로를 가리킨다 — «형식 red — remove 대상 부재» exit 3 이 기대값이다
(고정 기준선에서 기실현 remove 는 실존이므로, 이미 지워진 경로의 remove 행은 거두어야 한다 · 예외 없음).

## 파일 계획

<!-- machine: file-plan -->
```paths
remove	application/orders/domain_layer/shared_value_object/nothing.py	# 기준선에 없는 경로
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (없음) | — | — | — | retain | — |
