# 판정 — native Coordinator vs 대조군 (Task 11 Step 3)

판정 5종은 배차 노트 «확정된 사실»의 것이다. 기계 판정은 `judge.py`(평가자 스크립트 · `/tmp/dddjango-web-interaction-evidence-20260913/native/judge.py`)가 scratch build·스냅샷·stream-json에서 계산했고 결과는 `judgement.json`(native)·`control/judgement.json`이다. 정답 대조는 드라이런 `summarize.py` + `prior/oracle/oracle.json`(후보에게 비공개)으로 했다 — `oracle-summary.json`·`control/oracle-summary.json`.

| # | 판정 | native | control(구 command/agents + 신 scripts/references/검사기) |
|---|---|---|---|
| ① | 드라이버 실행 사실 — `interactions.json` 존재 · `collector.driver_sha256`/`snippet_sha256` = 스냅샷 파일 sha · 포인터 sha 일치 | **○** 2문서(관계인·설정) 전부 일치 | **○** 2문서 전부 일치 |
| ② | 잔여 0 ∧ 검사기 `--phase inputs` exit 0 | **△** 잔여 0(관계인 슬라이스 3 · 설정 슬라이스 1) · exit **2** — defect 1 = `coverage_review: independent review-result: pass required`(기계 결함 0) | **×** 잔여 0(슬라이스 2) · exit **2** — defect 20(새 표면 미연결 16 · v1 잔존 2 · coverage 2) |
| ③ | 예외 `interaction_exclusions` 0 또는 사용자 원문 있음 | **○** 0행(승인 원문이 없어 대신 만들지 않음 — 반환) | **○** 6행 — 기존 scope 원문 «설정 나머지 무변…» 인용(검사기 통과 · 리뷰어 «해석 타당·확인 필요») |
| ④ | 표면 연결 — case `reached_by` ≠ ∅ ∧ reference_capture sha = 그 step 캡처 sha | **○** 30/30 | **×** 12/14(2건 v1 · reached_by 없음) + 미연결 새 표면 16 |
| ⑤ | 독립 G0 리뷰 Agent 호출 흔적(`Agent` 도구 · `dddjango-web:design-review-web`) | **○** 2회(1차 fail 반영 → 2차) | **○** 1회 |

## 정답 미제공 조건의 도달(oracle · 후보에게 비공개)

| 항목 | 기대(드라이런 10차) | native | control |
|---|---|---|---|
| 관계 8 / 시 12 / 시·도 17 / 시·군 153 | 8/12/17/153 | 8/12/17/153 | 8/12/17/153 |
| 스크림·바깥 click / Esc | ≥1 / ≥1 | 1 / 2 | 1 / 7 |
| 토글 2상태(윤달·몰라요·못려요·목록 행 handler) | 7 | 7 | 7 |
| 실행 단위 / 대상 | 251 / 223 | 251 / 223 | 251 / 223 |
| 도달까지 슬라이스 | 3(잔여 0) · 6(게이트 정지) | 3(잔여 0) · 4(정지) | 2(잔여 0) · 11(예산 소진) |
| 드롭다운 열림을 case로 승격 | — | ○ 관계·시·시·도·시·군 9 메뉴 case 신설(`reached_by` 결속) | × 표면 12를 «예외 승인 D-C»로 반환 |
| 체크박스(윤달·몰라요·못려요) | 값 상태(checked)는 표면 키 밖 — 캡처·case 불요 | value-only 육안 항목으로 결정 ②에 묶어 반환 | 언급 없음(드라이버 executed에는 포함) |
| 빈 목록 | 드라이런도 미도달(K2 한계 · 정적 case) | 미도달 → `related/empty` 제외 승인 요청(반환) | 미도달 → D-A로 반환(v1 잔존) |

## 해석(제약 준수)

1. **«검사기가 막았다»로 좁힌다.** 대조군(구 Coordinator 규범)도 검사기 exit 2 메시지와 신 references(design-acquisition §3)를 읽고 드라이버를 스스로 실행해 잔여 0·리뷰어 호출까지 갔다 — 따라서 «드라이버를 실행하게 만든 것»의 공은 Coordinator md 개정이 아니라 **검사기 exit 2 + references**다(«기존 지침도 통과하면 개선 주장 금지»). Coordinator md 개정의 관찰 가능한 차이는 ⓐ «partial ∧ 잔여 0 = 통과» 읽기(4슬라이스 vs 11슬라이스 · 32분 vs 88분) ⓑ «선언 → case 추가 → 예외» 순서로 새 표면 16개를 case로 이어 기계 결함 0에 도달한 것 ⓒ 예외 행을 승인 원문 없이 만들지 않은 것 — 이 셋뿐이다.
2. **어느 쪽도 «완료(exit 0)»가 아니다.** 남은 것은 사람 결정(`related/empty`·`related/form-error`의 제외 승인 원문)이고, 검사기는 리뷰어 fail을 exit 2로 유지했다. «검사기 exit 0 없이는 ready가 되지 않는다»는 것이 두 run에서 동일하게 실측됐다(build-state `design_status: blocked`).
3. **native 1회 성공을 전체 성공으로 확대하지 않는다.** 같은 프롬프트·같은 스냅샷 1회 실행이며, 병행 실행(CPU 공유)·permissionMode auto·사전 승인 문구 조건에서의 결과다. 판정 ②가 △인 이유(리뷰어 fail)는 평가 계정이 비대화형이라 승인 원문을 줄 수 없는 조건에서 생긴 것이므로, «승인 원문을 주면 exit 0이 된다»는 추정은 실측하지 않았다(control이 «가상 승인을 적용한 staging 사본에 prepare exit 0»을 진단으로 돌렸으나 실제 입력이 아니므로 인용하지 않는다).
4. 정답 미제공 조건에서 두 run 모두 oracle 전 항목(관계 8·시 12·시·도 17·시·군 153·스크림·Esc·토글 7)에 도달했다 — 도달은 드라이버의 성질이며 Coordinator의 성질이 아니다(같은 드라이버 바이트).
