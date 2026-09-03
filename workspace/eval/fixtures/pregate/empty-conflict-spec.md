# 미니 설계 명세 — config 설정 자리 (empty 충돌 픽스처 · 차단 모드 E4)

`empty` 한 행이 기준선에 이미 있는 파일을 가리킨다 — «형식 red — empty 충돌(실존)» exit 3 이 기대값이다.
`empty` 는 add 와 같은 «새 파일» 태그이므로 기준선 실존을 already-built 로 통과시키면 기실현 add 를 empty 로
재라벨해 실체화 0 으로 도피하는 경로가 남는다(6단계 감사 MAJOR-1 — update 재라벨과 동형).

## 파일 계획

<!-- machine: file-plan -->
```paths
empty	config/settings/base.py	# 기준선에 실존하는 파일을 «새 빈 파일»로 재라벨
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (없음) | — | — | — | retain | — |
