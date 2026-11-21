# 설계 v2 — dddjango 2.44.0 후보: 리팩토링 도구 한계 둘(F4-199 · F4-200) + 동작 보존 장치의 지금 판 구멍

작성 2026-11-21 · 운영자. v1(10:36) → v2: 설계 독립 검토 T(도구 적대 · 차단 1 · 중요 3 · 사소 2) · P(글 · 그래프 · 차단 0 · 중요 6 · 사소 6) 모두 받음(`op-rev-DISPOSITION.md` · 보고 `rev-t/REPORT.md` · `rev-p/REPORT.md`) + 사용자 «나.»(범위 넓힘). 기준 배포판 2.43.0(`3293b498` · 사본 `rel-2.43.0/`). 본문 절: **§A = `design-a.md` v2(F4-199)** · **§B = `design-b.md` v2(F4-200 + D8) + `design-b-v3.md`(D9 · 바뀐 절만) + `design-b-v4.md`(재확인 첫째 반영 · 바뀐 절만 · 규칙 글 최종 문안)** · §A 에 patch-d(red 글 꼬리) · v1 은 `design-v1.md` · `design-a-v1.md` · `design-b-v1.md`. 경로:줄은 rel-2.43.0.

## 0. 결정

| 번호 | 결정 | 출처 |
|---|---|---|
| D1 | 범위 = F4-199 · F4-200. F4-201 · web 은 범위 밖 | 사용자 «그럼 다음 수정대상도 리팩토링 실행 도중 걸린 도구 한계부터 수정하자. … web은 제외.» |
| D2 | F4-200: 시험에 실제 영향 없는 고쳐 쓰기 ① 값 → 이름 상수 ② 식 → 이름 상수 ③ 기대값 → 시험 안 지역 이름 ④ 순서 없는 묶음 차례 + 그 이름 바꾸기는 «기대 그대로» · 조건 «한 번만 정하고 고쳐 쓰지 않음» · 코드를 읽어야 아는 꼴은 멈춤 · 덧감사 안 함 | 사용자 «그렇게 진행하자.» |
| D3 | F4-199: 닫힌 변경 창에서 V 여럿이 적은 원소도 그 창이 소비했으면 그 창 기준선에 결속 — 도구를 R-3633 문면에 맞춤 · 슬라이스가 갈리면 가장 앞 슬라이스 V 만 · plus 는 그 V 들 덧값 합을 다 채울 때만 · 규칙 글 무변 | 운영자 처리(사용자에게 09:47 알림 · 검토 T3 · P 사소 1 반영) |
| D4 | 다른 파일에서 import 한 상수 · 열거형 멤버 상수는 이번 판 밖(«바뀜» 그대로) | 운영자 처리 — 계획 요약에 한 줄 |
| D5 | 길 C(G2 배너 «항목 밖 관찰 k» · 요청 가이드 한 줄) 안 넣음 | 운영자 처리 — 남는 레인 할 일은 사용자 «할 일» 로 |
| D6 | 닫힌 창 open 기록 `--baseline` 우회에 가드 · 글 한 구 안 넣음 | 운영자 처리 |
| D7 | 판 번호 2.44.0(minor) — 새 규범 하나 · 동작 보존 장치 판정 넓힘 · dddjango-web 무변(두 자리 모두 web 에 같은 장치 없음) | 운영자 처리 |
| D8 | 지금 판 장치 구멍 둘도 이번 판: mock 단언 키워드 이름을 기대로 · unittest · Django 단언 메서드를 D 원소로(§B §2) | 사용자 «나.»(11-21 12:05 앞) |
| D9 | D8 과 같은 결의 assert 문 구멍 셋(왼쪽이 기대인 `in` · 좌우 거꾸로 `200 == r` · `pytest.raises(E, f)` 부르는 꼴)도 이번 판 — 비교의 «글자 값 쪽» 이 기대(§B v3 §2.3 · §2.4) · 둘 다 이름인 `x in y` 는 두 쪽 · 대칭 연산 좌우 같음 · unittest 거꾸로 쪽 가름은 안 넣음 | 운영자 처리(이미 정한 결정 «나.» 의 같은 결 · 질문 생략 · 이의 시 뒤집음) |
| D10 | 새 규범 자리는 Coordinator «바뀌는 것 목록» 문단(b13 — 설계자 · Phase 1 리뷰어 파견 입력에 실림) · LEDGER 재기준선 · pre-gate 재예보 안내 | 검토 P 중요 1 · 5 · 6 |

## 1. 고칠 것 한눈에

| 보고 | 지금(2.43.0) | 고친 뒤 | 바뀌는 파일 |
|---|---|---|---|
| F4-199 | 닫힌 창에서 V 둘 이상이 같은 옛 원소를 적으면 «모호» 로 결속 안 함 → G1′ `changes` 가 지금 시험에서 옛 원문을 찾아 red(현장 5) · 결속 빠져 «집행 원소 보존» 대조도 꺼짐 | 소비된 원소는 가장 앞 슬라이스 V 들이 그 창 기준선 · 뒤 슬라이스 V 의 낡은 인용은 G1′ 에서 red 로 드러나 고침 · plus 는 합 다 참일 때만 · 보존 대조 살아남 | `refactor_audit.py`(+31 −14) · Codex byte 미러 · 러너 사례 16 · 변이 6 |
| F4-200 | 단언 속 `T * 5` → `T * SLACK`(SLACK = 5)도 D 확정 → G2 에서 찾은 같은 꼴 자리를 같은 실행에서 못 고침 | ①~④ 는 «변화 없음» → 0T · 0F 개별 감사 · 값이 바뀌거나 V 가 인용한 원소면 지금처럼 red | `behavior_guard.py` · Codex byte 미러 · 그래프(새 규범 1 · 개정 넷) · Codex SKILL 넷 · 러너 `norm_checks` |
| D8 · D9 | mock 키워드 이름 · unittest 단언 · `in` 왼쪽 · 좌우 거꾸로 · `pytest.raises` 부르는 꼴의 기대 변화를 못 봄(거짓 녹색) | 기대로 봄(멈춤) · mock 키워드 차례만 바꾼 것은 같은 뜻 | 위와 같은 파일 |

규모(v4 측정): `behavior_guard.py` 배포판 대비 +484 −13 · 러너 +약 300(사례 ①~④ · D8 46 · D9 38 · 창 사례 · 변이 28 · 기존 사례 둘 고침) · `refactor_audit.py` +41 −15 · 러너 +약 116 · 규칙 글 새 1 · 개정 4 · LEDGER 4 · Codex SKILL 4 · byte 미러 2.

## 2. 둘에 걸친 것

### 2.1 진행 중 실행(2.43.0 으로 연 실행이 2.44.0 으로 이어질 때)

- F4-199(§A §4): red → green(같은 슬라이스 다중 owner 소비 원소 · 현장 red 5 → 0) · 뒤 슬라이스 owner 의 낡은 인용은 red(G1′ 에서 고침) · green → 보존 red(2.43.0 아래에서 이미 G1′ 이 가장 앞 슬라이스 owner 의 소비된 원소를 지금 글로 다시 쓴 실행) · 결속 원소가 다중 owner 뿐이던 창은 그 창 기준선을 읽음(head 못 읽으면 실행 불능 — 기존 규칙).
- F4-200(§B §8): red → 개별 감사(①~④) · green → red 는 C2 하나(V 승인 케이스 편집이 ①~④ 뿐 · 2.44.0 으로 close · 재close 한 창에만 — verify 는 저장된 close 기록을 읽음 · 검토 P 사소 5) · 현장 실행 다시 매김에서 C2 로 새로 붉는 것 0(검토 T).
- D8 · D9: 지금 판이 보지 못하던 기대 변화가 새로 멈춤(진행 중 레인 하나 mock 키워드 든 단언 12줄 · unittest 단언 현장 0) · D9 로 현장 비교 원소 25,696 중 2,055(8.0%)의 열쇠 쪽이 바뀜 — 글자 왼쪽 `in` 1,571 은 주어 이름 바꾸기가 풀리고(지금 판 거짓 red) 글자 편집이 멈춤(지금 판 거짓 녹색) · 둘 다 이름인 `in` 404 는 왼쪽만 바꿔도 새로 멈춤(한계) · 이어진 비교 58 · 왼쪽 글자 22 · 문장 자리 raises 부르는 꼴 0.
- pre-gate: 판정 무관 · 실행 트리 digest(scripts `*.py` · `*.json`)가 바뀌어 도는 실행은 다음 G1′ · G2 전에 재예보(검토 P 중요 6) — 노트 «도는 실행» · 보고에 진행 레인.
- 옛 창 기록(open · close · 후보) 꼴 무변.

### 2.2 요청 가이드 · 문서

- 요청 가이드: 바뀔 것 없음(사용자 칸 · 플러그인이 하거나 묻는 일 그대로 — 검토 P 확인).
- README `:321` 한 구(검토 P 사소 4 · §B §5 문안) · `work_flow.spec.json` 2.44.0 줄 · `master.html` 기준 판.
- 사용자 할 일: 현장 레인의 다음 정리 요청에 H11 자리(이름 없는 배수)를 적게 발주자에게 전함(§B v1 §7 ④).

### 2.3 검사

`make verify` 전체 + `make verify-mutation`(refactor_audit · behavior_guard 변이 표 둘 다 바뀜) · 봉인 두 번 · 그래프 → render `--apply` → ISSUED · LEDGER · target-counts · `make rulepack` · q4 골든 · 미러 sync · `runtime_parity_check`(Coordinator Codex 글자 대조) · mkrev2 → file_tree.html(트리 무변이면 대조만).

### 2.4 구현 단위(겹치지 않게 · 계획에서 확정)

- A(F4-199): `refactor_audit.py` · `refactor_audit_fixture_run.py` `closed_window_shared_cases` · 변이 6 · Codex byte 미러.
- B(F4-200 + D8 · D9 장치): `behavior_guard.py` · `behavior_guard_fixture_run.py` `norm_checks` · 변이 · Codex byte 미러.
- G(글): 그래프 `command-dddjango.ttl`(R-3791 새 · R-3633 rev4) · `agent-coder.ttl`(R-3649 rev3) · `agent-design-architect.ttl`(R-3644 rev3) · `agent-discipline-reviewer.ttl`(R-3647 rev2) · Codex SKILL 넷 · README · `work_flow.spec.json`.
- 운영자: ISSUED · render · LEDGER · target-counts · rulepack · 골든 · 봉인 · 파생 문서.

## 3. 받아들일 한계(노트 «받아들인 한계» 와 같은 목록)

§A §5 일곱 + §B §7 «받아들일 한계» + D4 · D5(점검표 밖 관찰은 다음 실행 몫 — 기대를 정말 바꾸는 새 자리) · D6.

## 4. 좁은 재확인에 맡길 물음

- 검토 T: T1 ~ T4 · G4 가 §A v2 · §B v2(· v3) 수리판에서 닫혔나 · 새 넓힘(D8 · D9)이 거짓 녹색 · 지금 판 판정 바뀜(넓힘 몫 밖)을 만드나 · unittest 자리 역할 표의 틀린 칸.
- 검토 P: 중요 1 ~ 6 · 사소가 §B v2 §5 규칙 글 · 그래프 절차에 맞게 반영됐나 · R-3633 rev4 · R-3647 rev2 문안 · LEDGER 네 행 · target-counts.
