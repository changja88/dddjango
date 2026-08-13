# codex 쌍둥이 대기 정책 수정 (2026-08-13 — 라운드 2′ 레인 B 정지 수확)

**상태**: 사용자 승인(「진행해줘」) → 구현 → v2.4.1 릴리즈. 규모가 작아 적대 리뷰 생략(사용자 확인).

## 진단 (rollout 로그 실측 — 세션 3개 대조)

레인 B(2′·codex) 38ea0b6a `stopped — 설계 역할 결과 미수신`(11:24→11:59·35분)의 진범은
서브에이전트가 아니라 **코디네이터의 대기 정책 공백**이다:

- 11:38 `spawn_agent`(architect) → `wait_agent` 10~60s 폴링 전부 `{"timed_out":true}` —
  **`list_agents` 는 내내 `running`** 인데 «미수신» 으로 분류.
- 11:50·11:53 `interrupt_agent` ×2 — interrupt 는 진행 중 턴을 파괴한다. fork 1 은 15분간
  정상 조사 후 **「추가 탐색 중단·design-spec.md 를 닫는 중」 발화 직후** 두 번째 interrupt
  로 소멸. retry fork 는 5분 만에 같은 패턴 → 포기 → 정지.
- 정지 처리 자체는 규약 준수(«STOP 아님» 분류 정확·fallback 금지 준수·G0 산출물 정상·
  앵커 동결 준수) — **정지는 유효**, 결함은 매뉴얼(플러그인 codex 쌍둥이) 소속.
- 근원: 쌍둥이 SKILL 이 `spawn_agent`/`wait_agent` **사용**은 지시하나 **대기 정책**
  (타임아웃≠실패·죽음 판정 자·interrupt 금지)을 미규정 — 공백을 엣지 규율
  «미수신/타임아웃=blocked»(죽은 에이전트용)로 메움. claude 판은 Task 도구가 완료까지
  블로킹이라 이 문제가 구조적으로 없음 — **쌍둥이 치환이 낳은 codex 고유 결함**.

## 수정 3곳 (문서 전용 — 검사기·eval 무접촉)

1. `codex-dddjango/skills/dddjango/SKILL.md` :22 — **대기 정책 불릿 신설**:
   timeout=«아직 일하는 중»·`running` 이면 `wait_agent` 반복(상한 없음·수십 분 정상)·
   `interrupt_agent` 재촉 금지(30분+ 무진행 실측 시 마지막 수단)·«미수신»=터미널 상태
   또는 무진행 실측일 때만(running 을 미수신으로 분류 금지).
2. 같은 파일 :186(엣지 규율) — «미수신/타임아웃» 문구를 대기 정책의 자로 재정의
   (timeout 자체는 미수신 아님).
3. `codex-dddjango/skills/dddjango-design-architect/SKILL.md` :30 — **산출물-우선 쓰기**:
   조사 종료 즉시 design-spec.md 생성·절 단위 이어 쓰기(파일 성장=진행 신호·중단 내성).

## 쌍둥이 대응표

| claude 판 | codex 판 | 사유 |
|---|---|---|
| (해당 절 없음) | 대기 정책 불릿·엣지 규율 자 | Task 는 완료까지 블로킹 — wait/interrupt 축 자체가 codex 전용(치환 토큰 Bash↔셸 계열과 같은 «의도된 비대칭») |
| architect 산출물 일괄 작성 | 산출물-우선 쓰기 | claude 는 파일-성장 신호가 불필요(블로킹 수신) — codex 만 진행 관측 채널 필요 |

## 부수 관측 (이번 수정 스코프 밖 — ⑦ 재상정 재료)

- update_plan 자발 2회(지시 삭제 후에도 호출 — 네이티브 도구·무해·지난 판 «지시 있고 0회» 와 역설).
- 한 줄 상태 `[k/n]` 발화 0 — H5′ 미작동 재현(2회째).
- 클린룸 `git log -5 --oneline` 1회(제목만·실질 오염 0·정직 신고 — 재발 2회째·방어 후보: 레인 훅).

## 재기동 조건 (재료 무변 — 새 앵커 불요)

같은 앵커 `67dba2c1`·같은 요청문·`.dddjango/20260813-1136-billing-checkout/` 재사용
(stopped.md 재개 조건 그대로). codex 설치본 v2.4.1 확인 후:
`cd ~/Desktop/broccoli-rebuild-codex && codex "$(cat docs/rebuild/billing/request.md)"`
