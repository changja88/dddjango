# 소급 A/B 대조 — 구 실행기(v2.17.16 설치본과 byte 동일) × 신 실행기(차단 승격) · 동일 입력 (2026-09-03)

절차: `git clone` + `checkout --detach <G1 기준선>`(라이브 저장소 무변경) → 두 실행기를 같은 spec·같은 `--base`·같은 클론으로 실행 → 비교 키 = (exit, 안정 ID 집합, e-ID 집합) · 텍스트(모드 문면·요약 행) 제외. 원본 stdout: 이 폴더 `<좌표>-<old|new>.out`.

| 좌표 | 기준선 | 구(2.17.16) exit·ID·e-ID | 신(승격) exit·ID·e-ID | A/B | 신 실행기 요약 |
|---|---|---|---|---|---|
| L1 media-library 최종 명세 | `138359f7cf6f` | 2 · 6 · 0 | 2 · 6 · 0 | **동일** | 요약: 귀속 6건 · 실존 결손 0건 · 기준선 138359f7cf6f · 모드 차단 |
| L2 notification-bc 최종 명세 | `1eb8507424c7` | 2 · 1 · 0 | 2 · 1 · 0 | **동일** | 요약: 귀속 1건 · 실존 결손 0건 · 기준선 1eb8507424c7 · 모드 차단 |
| L3 notification-email-template 최종 명세 | `9ca3dd4929b7` | 0 · 0 · 0 | 0 · 0 · 0 | **동일** | 요약: 귀속 0건 · 실존 결손 0건 · 기준선 9ca3dd4929b7 · 모드 차단 |
| L4 fortune-catalog 최종 명세(워킹트리) | `e1294f59c35c` | 2 · 3 · 0 | 2 · 3 · 0 | **동일** | 요약: 귀속 3건 · 실존 결손 0건 · 기준선 e1294f59c35c · 모드 차단 |
| R reading 최종본(19b27df) | `80431d9480f7` | 4 · 0 · 0 | 3 · 0 · 0 | 상이(의도) | 요약: 형식 red 7건(remove 대상 부재 7) · 기준선 80431d9480f7 · 모드 차단 |
| Rp reading 재라벨 판형(78e616a · run 37) | `61b56ef4b69e` | 5 · 0 · 2 | 3 · 0 · 0 | 상이(의도) | 요약: 형식 red 26건(remove 대상 부재 2 · update 대상 부재 24) · 기준선 61b56ef4b69e · 모드 차단 |

- **무손실**: L1~L4(형식 규범 이후 4레인 · update/remove 전건 기준선 실존) 전부 exit·귀속 ID·e-ID 동일 → 판정 표면 불변.
- **R(reading 최종본 × 마지막 기준선)**: 신 실행기 형식 red «remove 대상 부재 7» — 기준선을 15회 옮긴 관행 아래 이미 실현된 삭제 행(고정 기준선 프로토콜에서는 실존 → red 0). update 부재 0(승격 부품 `prepare_fortune_evidence_use_case.py` 는 유효 승격 형태 예외로 통과 — 계획 Δ4 기대와 일치 · `R-new.out` 에는 비관측: 형식 red 경로는 materialize 전 반환 · rv5-A 가 스크래치 직접 호출로 promoted 1(`__init__` ∧ 본체 실존) 실측 · ⑤ 반영 뒤 실행기는 형식 red 블록에 «승격 형태 예외 통과 N건» 행을 인쇄한다).
- **R′(재라벨 판형 78e616a × run 37 기준선)**: 신 실행기 형식 red «update 대상 부재 24 · remove 대상 부재 2» — ledger:144 «기실현 add 24경로를 update 로 재라벨(구판 형식 red 회피)» 의 기계 재현. 구 실행기는 exit 5(실체화 0·결손 2)로 통과시켰다 = 차단 모드가 봉쇄하는 도피 경로의 실측.
- **카탈로그 `--check-report`(현 리포트 × 워킹트리 명세)**: exit 3 stale — `cb95a1bddb32 ≠ 6cf8e2ffdfc3` — 발견 ⑩(Phase 2 개정 3회 · 재실행 0)의 기계 재현.

```
# design_pregate --check-report · 모드 차단(enforce) · 실행기: design_pregate.py · dddjango v2.17.16 · 블록 해시 cb95a1bddb32
  불비: stale — 명세 블록 해시 cb95a1bddb32 ≠ 마지막 예보 6cf8e2ffdfc3 · 재발화

요약: check-report 불비 1건 · 블록 해시 cb95a1bddb32=6cf8e2ffdfc3 · 마지막 판정 green · 귀속 0건 · 실존 결손 0건 · 기준선 e1294f59c35c
```

- **kkebi-server 구형 명세 1건(20260823-0623-image-bc)**: exit 3 «블록 부재» — 차단 모드에서 구형 명세 레인이 받는 첫 메시지 실물(`--report` 는 스크래치 — kkebi 런 폴더 무변경).

```
형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 update · 부재 경로만 add)

요약: 형식 red 1건(블록 부재) · 기준선 6608fb0d955c · 모드 차단
```
