# 미니 설계 명세 — orders BC 문서 정리 슬라이스 (블록 공허 픽스처 · 차단 모드 exit 3)

machine 마커와 펜스는 있으나 file-plan 행이 0(주석뿐)인 명세다. 관찰 모드에서는 «실체화 0 · 결손 0» skip(exit 4)
으로 통과했고, 차단 모드에서 «블록 의무»를 빈 펜스로 충족하는 도피 경로가 된다 — «형식 red(블록 공허)» exit 3 이
기대값이다(변경 파일이 없는 명세는 pre-gate 대상이 아니라 산문이다 · update 대상이라도 적는다).

## 파일 계획

<!-- machine: file-plan -->
```paths
# 이번 슬라이스는 파일을 만들지도 고치지도 않는다(문서 정리) — 행 0
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| (없음) | — | — | — | retain | — |
