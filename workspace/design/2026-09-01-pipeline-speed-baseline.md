# 파이프라인 속도 베이스라인 — 전 레인 실측 (절차 ① 산출물)

- 날짜: 2026-09-01
- 지위: 속도 리비전(pre-gate) 8단계 절차의 **① 원인 일반화 검증** 산출물. ⓪(분석 적대 검증 3레인)의 정정판을 입력으로 한다.
- 확정 결정(2026-09-01 사용자 승인): 배치 범위 = pre-gate 단독 · 배포 = 관찰 모드 우선(보고 전용 → 실측 후 차단 승격).

## 0. 발단과 ⓪ 정정판 요약

spring_dream_server `feat-fortune-reading` 레인(08-31 23:14 ~ 09-01 14:0x, 벽시계 890분+)의 전수 프로파일에서 출발했다. ⓪ 적대 검증(독립 서브에이전트 3레인)으로 확정된 결산:

- 원가 ~700분 — **재설계·재리뷰는 발견을 앞당겨도 이동할 뿐 소멸하지 않는다**(초기 «145분 절감» 주장은 이 오류로 기각).
- 이미 해소(v2.17.13) 35~45분(#396 계열).
- pre-gate 절감 가능 **65~85분/레인**(STOP 절차 오버헤드 + 오형상 구현 재작업분, acceptance 재사용률 74% 실측 반영).
- STOP 10건 확정 분류: ①선행 3 / ②검사기 결함 1(#396) / ③설계·기계검출가능 2 / ④난제 2 / ⑤운영·해석 2.

## 1. 방법·자료

- **Codex 레인**: `~/.codex/sessions/**` 롤아웃 1,266개 중 spring_dream_server cwd 524세션 → dddjango 레인 12개 귀속(멀티 6 + 코디네이터 단일 스레드 6). 스크립트 `scratchpad/baseline_codex/01~04_*.py`.
- **Claude 레인**: `~/.claude/projects/…worktrees…` 27디렉터리·28세션 → dddjango 19 + dddjango-web 6 + 비파이프라인 2. 스크립트 `scratchpad/baseline_claude/{analyze,report,aggregate}.py`.
- **STOP·반송 전수**: STOP 60종·REPORT 13종·git 549커밋 대조 → dddjango 레인 18개(비-dddjango 발주 03 등 제외), 반송·정지 이벤트 47건. 정규 게이트 승인 기록(G0/G1/G2.md 22종)은 이벤트로 세지 않음.
- 방법론(⓪에서 검증·확정): 역할 라벨 = session_meta `agent_path` / 토큰 = 누적 카운터 리셋 감지 후 delta 재구성 / exec = custom_tool_call↔output call_id 짝(30초 yield 상한) / 활성 = 5분 컷(2~10분에 강건).

## 2. 실측 A — 시간 구조 (두 런타임)

**일반 패턴(전 레인 성립) — «모델 시간 지배»**: Claude 27/27 레인에서 모델 생성 시간이 도구 실행의 ≈11배(레인별 6~18배). Codex도 동일 방향(exec 1.6~30%, 대부분 한 자리 %). 도구 실행(테스트·검사기)·발주자 대기·유휴는 어느 레인에서도 지배 항이 아니다(예외: 08-27 밤샘 대기 레인 2개의 유휴 >50%).

**특이 패턴(기준 레인 고유) — «architect 지배»**: fortune-reading의 architect 활성 51~53%는 재현되지 않는다.

| 구분 | architect 비중(벽시계) | 최대 역할 |
|---|---|---|
| fortune-reading (기준) | **51.2%** | architect (설계 개정 세션 10개) |
| 타 Codex 멀티 레인 4개 | 13~28% | coder/코디네이터 |
| Claude dddjango 19레인 합 | — | **coder 3,524분 > architect 1,452분** (구현이 설계의 2배) |

규모 참고: Claude dddjango 레인 평균 활성 399분(중앙값 359) · dddjango-web 평균 98분(≈1/4 규모) · Codex 레인 중앙값 활성 204분.

**부수 관찰**: Codex 레인 6개(08-30~31 오전: fortune-character-1·fortune-record·product·wallet·fortune-intent·query-translation)는 서브에이전트 spawn 없이 **코디네이터 단일 스레드**로 실행됐다(multi_agent 미가동 추정). 파이프라인 규율(sequential fallback 금지) 관점의 별도 관찰 후보.

## 3. 실측 B — STOP·반송 전수 (18레인·47건)

분류 합계: **① 선행·제품 결정 12 / ② 검사기·규범 결함 5 / ③ 결정적 사전 검출 가능 설계 결함 13 / ④ 설계 난제·기계 검출 불가 11 / ⑤ 운영·해석 5 / UNCLEAR 1**. (애매 건은 ④·UNCLEAR로 보수 분류 — ③ 13건은 하한.)

### ③형(pre-gate 표적)의 일반성 — 핵심 판정

- 출현 레인 **8/18(44%)** — llm-access·accounts·service-policy·fortune-record·wallet·fortune-intent·fortune-calculation·fortune-reading. STOP 있는 레인 기준 8/13(62%). **특정 레인 현상이 아니라 신규 BC 레인의 일반 패턴.**
- 비용: 실측 7건 합 329분(건당 평균 47분, 대역 35~85분). 레인당 평균 ≈**34분**(③ 발생 레인만 ≈56분). fortune-reading의 ③ 비용(64·84분)은 **이상치가 아니라 대표치** — 그 레인의 돌출은 ③이 아니라 총 STOP 밀도(11건, ①·⑤ 중첩).
- **발견 시점이 비용을 결정**: G1 설계 시점에 잡힌 ③은 ≈0분(accounts A3 — architect가 G2 red를 사전 예측·정지), G1 이후(슬라이스·G2)에서 터진 ③은 40~90분. **13건 중 11건이 G1 이후 발화**했고 패턴은 동일 — «승인된 설계 명세가 registry 결정 계약과 조인되지 않은 채 동결».
- 감소 추세 존재(검사기 수리 누적 + 운영 학습 — 최후발 fortune-character-2는 ③ 0 완주)하나, 같은 날 fortune-reading이 ③ 2건을 냈으므로 복잡한 신규 BC에서는 여전히 재발.

### pre-gate 표적 규칙 5군 (47건 실측 귀납)

파일 배치(#160/#484/#267/#310) · 명명(#41/#43/#632) · published-language(#453/#454/#455/#473) · 테스트 물리 분류(#389/#392/#388) · 계층 의존(#8/#92/#574/#93/#554).

## 4. ROI 판정

- 기대 절감: **레인당 평균 ≈34분, ③ 발생 레인 40~90분/건** — 발견을 G1 시점으로 앞당기면 실측상 ≈0분 대역으로 떨어진 선례(accounts A3)가 있다. 극적이지 않지만 신규 BC 레인마다 반복 발생하는 실손실이며, 시간 외 편익으로 «G1 승인 명세의 신뢰성»(반송 없는 동결)이 있다.
- ⓪·①의 전제(«③형은 일반 패턴이고 결정적으로 앞당길 수 있다»)는 **유지** — 절차 계속(② 설계 명세)이 정당하다.
- 시간 구조의 최대 항(모델 시간·coder 시간)은 pre-gate 표적이 아니다 — 이번 배치의 목표를 «반송 루프 제거»로 한정하고, 총 시간의 극적 단축을 약속하지 않는다.

## 5. ② 설계 명세에 넘기는 제약 (⓪·①에서 확정)

1. pre-gate 입력은 §6 파일 계획만으론 위반의 ~10%만 커버 — **§3 계약표 + §6 트리 + §8 입장표의 전 명세 조인** 필요 → 명세 기계가독 형식 규범 동반 개정.
2. 게이트는 G1 1회성이 아니라 **명세 개정 승인마다 재실행**(#216은 반송 후 재설계가 «도입»한 2차 결함 — 1회성 게이트로는 원리적 불가).
3. 커버리지 한계 명시: 코더 슬립·표기류·명세 내부 의미 모순(④)은 잡지 못한다. ③ 13/47(28%)이 표적의 상한이 아니라 하한이되, ④ 11건은 표적이 아니다.
4. 시뮬레이터 노선: 팬텀 트리 실체화(기존 검사기 재사용·이중 정본 회피) 권고 — ② 게이트 결정 사항.
5. 오탐은 절대 불가 — ④ 백테스트 게이트(역사 정답지: fortune-reading b5392f0에서 24건 재현·e152e57 및 타 레인 승인본 오탐 0)와 ⑦ 관찰 모드가 방벽.

## 6. 부수 발견 — 이번 배치 밖 후보

- **② 잔존 1순위: registry_gate 병렬 레인 귀속 사각** — 앵커 차분이 발주자 사전 승인 `merge main` 유입분을 레인 산출물과 구별 못해 타 레인 오귀속 재발(accounts 804건·service-policy 818건·fortune-record 818건·chat-relay 90건·fortune-intent 77건). `registry_gate.py`에 레인 경로 필터 옵션 부재 실독 확인. 현재 소비측 수동 규칙(«경로별 분리 보고»)으로 연명 중. **별도 검사기 수리 배치 후보(권고: pre-gate와 분리).**
- #493 «imported stdlib base는 소유 심볼 계산 제외» 해석 명문화(규범 문서화 후보 — 검사기는 정상 판정 확정).
- `.dddjango/violations/*.jsonl` sidecar 정리 책임 명문화(소소).
- Codex single-mode 실행 6레인 관찰(sequential fallback 규율 관점).

## 7. 재현 경로

- ⓪ 스크립트: 세션 scratchpad `profile_rollouts.py`·`deep_profile.py`·`burst_exec.py`·`union_idle.py` 및 적대 검증 레인 산출물.
- ① 스크립트: scratchpad `baseline_codex/`·`baseline_claude/`.
- 1차 자료: `~/.codex/sessions/2026/{08,09}/**`, `~/.claude/projects/-Users-hyun--herdr-worktrees-*`, `~/.herdr/worktrees/spring_dream_server/*/docs/superpowers/orders/lane/`, 각 워크트리 `.dddjango/`.
