# T2-1 출력 계약 설계 — 공용 포매터 재저작 (선행 리뷰 대상)

> 지위: 개정 5 기각(레인 T·MEDIATION 부록)의 실행 설계. 귀속 매핑표(`2026-08-19-ontology-t2-1-attribution-map.md`)와 **한 묶음으로 선행 리뷰**를 받은 뒤 적용한다. 목표는 E8 원 처방의 회복 — **rule 보유 발견의 라인 문면은 공용 모듈이 소유한다**(T12 채택 정의: 구조화 입력 → 단일 포매터 → 라인+레코드 동시 산출).

## 저자 판단 요약

1. «공용 포매터»는 새 장치가 아니라 **기존 `Findings`/`Candidates`의 add**다 — 이 두 표면은 이미 라인을 자기 문법(`[{rule}] {where}: {msg}` / `[ⓓ{rule}] {where}: {msg} — 물음: {q}`)으로 소유한다. 재저작 = rule 보유 발견의 모든 출력 지점을 이 두 표면으로 이행.
2. `SliceFindings`(호출자 소유 라인+rule 레코드)는 **이행 완료 후 제거** — E8 «어댑터» 판정의 대상이었다.
3. `ContractFindings`(rule=null·라인 호출자 소유)는 **존치** — 선행 계약 검사기는 E8 문면상 «출력 규약 밖»이고 이 설계는 T0 B2 심의를 통과한 것이다. 단 라인 앞에 통일 표지를 붙이지 않는다(계약 레인의 기존 소비자·overlap-review 문면 보존).
4. stdout 문면 변경은 이제 **의도된 산출**이다(원계획 «접두 신설이 그 목적» 복원) — 비용은 레인 T가 실측으로 확정: 기준선 EXPECTED 갱신(사유 동반)·backstop 0/679·앵커 대칭 무영향.

## 자인 약점 (리뷰 집중 요청)

- ⓓ#511(`— 물음:` 무msg 특수 문면)과 B형 locator(`{rel}:{lineno}` 무콜론)의 정형화가 의미를 바꾸지 않는지.
- 계약 레인 존치(3번)가 «부분 통일»로 남는 것이 E8 재위반인지 — 저자 판단은 «규약 밖» 문면이 근거지만 반론 가능.
- backstop fragment 보존은 «category·shown 문자열이 msg 안에 잔존»에 의존 — 매핑표의 msg 구성이 이를 깨는 행이 있는지.

## 이행 표 (레인별)

| 레인 | 현행 | 이행 후 | 문면 영향 |
|---|---|---|---|
| tree-slice A형(`  [#N] {where}: {msg}`) | SliceFindings(line=…) | `Findings.add(rule, where, msg)` + `print(" ", x)` | **byte 동일**(1단 판형) |
| tree-slice B형(`  [#N] {rel}:{lineno} {msg}`) | SliceFindings(line=…) | `Findings.add(rule, f"{rel}:{lineno}", msg)` | 콜론 1개 추가(정형화 — 의도) |
| tree-slice ⓓ(`  [ⓓ#N] …`) | SliceFindings(severity=info) | `Candidates.add(rule, where, msg, question)` | ⓓ#511은 msg·question 분해 신규(매핑표 부속) |
| dataclass code-profile — **rule 귀속 사이트**(매핑표) | ContractFindings 또는 SliceFindings(render 보존) | `Findings.add(rule, f"{path}:{lineno}", msg)` — msg 구성은 매핑표 열 | `  - path:12  category: shown` → `  [#N] path:12: msg`(변경 — 목적) |
| openapi #63 code·repo_scan | SliceFindings(line=…) | `Findings.add("#63", where, msg)` | 변경(정형화) |
| **계약 레인**(rule=null — 자유 출력 5종·response-schema·common-container·매핑표가 계약 유지로 판정한 code category) | ContractFindings | **존치**(라인 호출자 소유) | 무변 |
| #74 대상-0 가드 21종 | 직접 print+return 2(레코드 0) | 공용 `guard_zero_targets()` — 라인 무변+`rule="대상0"` 센티널 레코드(rule=null+sentinel 격리) | 라인 무변·레코드 신규 |
| 헤더·근거 블록·clean 라인 | 각 검사기 소유 | **무변**(계약 범위 = 위반 라인만) | 무변 |

## findings.py 변경

- `SliceFindings` 클래스 제거(이행 완료 커밋에서 — 과도기 중 공존 허용).
- `guard_zero_targets(checker_out, target, msg)` 헬퍼 신설(21종 공용 — 라인 print는 호출자, 레코드만 공용. 라인까지 통일하면 21종 문면이 바뀌므로 v1은 레코드만).
- 스키마 `findings/0` 무변(생산자 정리일 뿐).

## 검증 계획 (적용 후)

1. `checker_baseline_matrix` — parsed 증가분을 검사기별 사유(«code 레인 #N 라인 신규 N건»)와 함께 EXPECTED 갱신. synthetic 군 축소 예상(rule 귀속 검사기).
2. `findings_count_matrix` — rule 분포 이동(contract→#N)을 매핑표와 1:1 대조하는 갱신. **stdout↔record 대응 단언 추가**(하네스 보강 항목과 합류).
3. `api_error_backstop_matrix` — 679 green + **fragment 14종이 신 문면에 잔존하는지 정적 표로 선확인**(레인 T#8 처방).
4. `findings_smoke` — DM/CC byte 골든 무변 확인 + D11 byte 골든 8종은 **이행 후 문면으로 신규 채취**.
5. `make verify` 전체 + 혼성 패널 재검(codex+신선 Claude — 규약 R1′).
