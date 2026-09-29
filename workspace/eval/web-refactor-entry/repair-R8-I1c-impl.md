# 구현 기록 I1c — ㉯ 상시 답의 dddjango-web 확장 (2026-09-29)

- 설계: 원본 체크아웃 `workspace/plan/2026-09-26-refactor-path-repair/design-R8-I1c-standing-answer-web.md`(§11 «리뷰 처분»이 §0~§10 의 해당 문장을 대체한다).
- 리뷰: scratch `review-I1c/review-I1c-design.md` — «수정 후 승인»(blocker 0 · major 1 · minor 9 · nit 8 · core 조율 3). 전건 수용하고 최소화 권고 1~6 을 채택했다.
- 사용자 결정: 09-29 04시 ③ «㉮+㉯ (권장)» · 05시 «web도 적용 (권장)».
- 작업 위치: 이 워크트리(`agent-acd60c09333360921`). I3·I4 미커밋 변경 위에 더했다. 시작할 때 작업 트리 = `scratchpad/i3/I3I4-final.patch` 였다(`git apply --check -R` 통과). 커밋·push 는 하지 않았다.
- 원본 체크아웃·core 워크트리는 고치지 않았다. 설계 문서(원본 체크아웃의 미추적 파일)만 예외로 §11 을 덧붙였다.
- Serena·Graphify 는 쓰지 않았다(지시).

## 1. 바뀐 파일 (㉯ web 만 — I3I4 스냅샷 대비)

| 파일 | +/− | 몫 |
|---|---|---|
| `dddjango-web/commands/dddjango-web.md` | +3 −1 | `:304` **Phase 1~2** 두 구(MJ1 · m1) · `:306` 새 문단 **상시 답** |
| `codex-dddjango-web/skills/dddjango-web/SKILL.md` | +3 −1 | 같음(`:329` · `:331`). 플랫폼 토큰은 `${SKILL_DIR}`·«네이티브 셸로» |
| `dddjango-web/scripts/refactor_audit.py` · Codex byte 미러 | +272 −1 | 새 하위 명령 `standing [<폴더> --gate]` · core 공유 블록 · self-test 상시 답 문면 결속 · 머리 사용법 |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` · Codex byte 미러 | +99 −1 | 블록 «M: standing» 12묶음 30단언 |
| `Makefile` | +3 −1 | `verify-web`: 블록 cmp 1줄 · 문단 cmp 1줄(`**Phase 1~2**`·`**상시 답**` 루프) · 안내 echo 1줄 고침 |

- 무접촉: 에이전트 md 전부(Codex 역할 SKILL 포함) · `src/debt.py` · backstop · `commands/refactor.md` · Codex `dddjango-web-refactor/` · core 전 파일.
- I3·I4 변경 6파일 · 기록 2개: 바이트 그대로다(㉯ 만의 diff 에 나오지 않음).

## 2. 문면 (양 런타임)

**`:304` Phase 1~2 — 늘 적용(파일 유무와 무관)**
- design-architect-web 파견 입력(MJ1): 뺀 항목을 완료 보고마다 전부 다시 적고, 항목마다 막는 것의 범주(닫힌 6어 `외부 관찰 동작`·`테스트 본문 동반`·`테스트 새 판정`·`API 계약`·`경계 교차`·`web/ 밖` 가운데 하나 이상)와 막는 `파일:행`(위치마다 `파일:행[-행]` 을 ` · ` 로 잇는다)을 붙인다.
  - 범주는 처방을 그대로 따를 때 막는 것만이다. 동작을 지키려는 우회와 재사용 선택은 범주가 아니다.
  - 여섯 범주의 web 뜻 풀이도 이 구에 둔다. n4: `테스트 본문 동반` 은 «치환 밖»만이고 «web/ 밖» 한정은 뺐다.
- design-review-web·discipline-reviewer-web 파견 입력(m1): «(있으면) 이번 설계가 동작 불변 불가로 슬라이스 0 에서 뺀 `M<n>`(architect 사유) — 처분은 재상정 기록 몫».

**`:306` 상시 답 — 조건부(m7)**
- `standing` 은 «파일이 있고 G1 승인 전에 불가 항목이 드러나면» 돈다. `--gate` 는 «상시 답 줄이 있으면» 돈다. 파일 없는 흐름에서는 명령이 0 이다.
- 적용 범위는 G1 승인 전에 드러난 항목에만이다(m2).
- Coordinator 는 architect 범주를 해석하지 않고 옮긴다. 셋 밖 낱말이 하나라도 있거나, 범주·위치가 없거나, «미룰 수 없음»·`C<n>` 이면 묻는다(MJ1).
- 배너는 `상시 답: 적용 예정 k건(M<n> <범주> …)` 1행과 안내 1줄이다(n2: «묻는 재상정 u건» 삭제).
- 결정 기록
  - G1 승인 입력 때, architect 마지막 완료 보고 기준으로 적는다(m1 흡수).
  - 이유를 R-3589 성격으로 문면에 적었다: «그 전에 적으면 Phase 1 서브에이전트가 읽는 `refactor-scope.md` 에 상시 답이 드러난다».
  - 절 첫 줄 `- 상시 답 적용 k건`, 항목마다 한 줄, `재상정 키: -` · `의미 재상정 키:`.
- `--gate` 때: «Phase 2 진입 준비 ⑤ 커밋 뒤 첫 coder-web 파견 전(설계 반송 재진입 뒤 첫 파견 전 포함)»(m4). 호출 접두는 `${CLAUDE_PLUGIN_ROOT}/scripts/`(n5).
- red 처리(m5 · K3 와 같은 뜻)
  - «묻는다» red: 재상정 STOP.
  - 그 밖 red: 같은 키의 고친 줄을 새 절에 적는다.
  - 뒤 절의 같은 키 사용자 답 줄이나 고친 상시 답 줄이 앞 줄을 대체한다.
- 예외 두 문장: 결정 출처 일반 방침 금지(`:153`)와 경계 절 재상정 물음 정지(`:276`)에 대한 리팩토링 모드 예외 · 파일 쓰기 금지 · 파견 입력에 싣기 금지. «사용자 결정» 구는 삭제했다(n1 · 최소화 6).
- 길이: 상시 답 문단 1,920자(설계 v1 2,081자) + `:304` +633자.

## 3. 도구 — `refactor_audit.py standing`

**공유 블록(m6)**: core 워크트리 `agent-a60e383dcbc6966fb` `dddjango/scripts/refactor_audit.py` 의 `# ── 상시 답 인식 블록 시작 …` ~ `# ── 상시 답 인식 블록 끝 ──`(표지 주석 포함 35행)을 통째로 복사했다.
- 마지막 복사: 2026-09-29 15:18:22 · core HEAD `fcf051fd`(단계 B 미커밋 판).
- **블록 sha256 `2a9ae2e43d62ce903c9694f2516d267301f740fa40591b2fd568e5faea8fd1e3`**. 처음 추출(14:5x)과 같다.
- 블록 안: `STANDING_FILE`·`STANDING_SENTENCE`·`STANDING_CATEGORIES`·`STANDING_MARK`·`STANDING_SECTION`·`STANDING_EXPECT` · `_standing_rows` · `_standing_verdict`.

**블록 밖**

| 부분 | 내용 |
|---|---|
| `_git_try` · `_standing` · `_standing_source_ok` · `_STANDING_SRC` · `_USER_SRC` | core 착륙본과 같은 코드(블록 밖이라 byte 대조 대상은 아님 — 조율 ②) |
| `_scope_decisions` | 마지막 `## G0` 절부터(m3). 절 = 종류·표지(첫 비빈 줄 `- 상시 답 적용 k건`)·키 행. 결정 줄 = `· 결정 =` 칸이 있는 줄, 또는 `출처 = 상시 답` 을 담은 줄(모양이 틀려도 검사 대상 — 조용히 빠지지 않음). 칸 값은 다음 칸 이름 앞까지다(m5). 머리 `결정 줄:` 은 떼고, 병합 괄호 `(+M<k>)` 안은 키가 아니다 |
| `_standing_gate` | ① 출처 커밋·행 ② `결정 = 별도 요청` ③ 키 `M<n>` 하나 · 마지막 G0 의미 ⓐ 안 · 사유 `동작 불변 불가(<범주>… — <파일:행>…)` · 범주 ⊆ 3 · 위치 `파일:행[-행]` 만(fullmatch) · **git_snapshot 판** 줄 수 안(m4) ④ 표지 있는 재상정 절 안 · 상시 답 절에 다른 결정 줄 없음 · 같은 키의 앞선 재상정 절 사용자 답 줄보다 뒤가 아님(G0 절 줄은 세지 않음) ⑤ 절 안 상시 답 줄 전부의 키 = `의미 재상정 키` · `재상정 키: -`(n3) · 대체(뒤 재상정 절 같은 키 사용자 답·상시 답 줄). k 계수 검사는 뺐다(core 에 없음 · 리뷰 §6) |
| red 꼬리 | `— 묻는다(재상정 STOP)`(범주 셋 밖·범주 없음·`C<n>`) / `— 고친 줄을 새 `ⓐ 재상정` 절에 적는다`(그 밖) |
| `cmd_standing` | 폴더 없이: `상시 답: 없음` / `인식 — …` + `상시 답 출처: …` / `인식 안 함(<사유>) — 적용 0` + `기대 문장: …` · exit 0. `--gate`: red 행 + `요약: standing gate · 상시 답 줄 n · 대체 s · red r` · exit 0/2 · 1 = 실행 불능(`git_snapshot` 없음 등) |
| `--self-test` | «상시 답이 덮는 범주»~«셋뿐» 백틱 = 상수 · 문장·파일 상수가 Coordinator 에 실재(두 런타임) |

**규모(m9 — 실제)**: +272행.
- 블록 35
- core 와 같은 도우미 38
- 파서 47
- gate 95
- 출력·CLI 31
- self-test 11
- 상수·머리 15

리뷰 추정(약 +130~180)보다 크다. 줄일 수 있는 곳은 core 가 `_standing`·`_standing_source_ok`·`_STANDING_SRC` 를 블록 안으로 옮기는 것(조율 ②)뿐이다. 그래도 web 파일 줄 수는 같고 중복만 사라진다.

## 4. 픽스처 — 블록 «M: standing»(12묶음 30단언)

| 묶음 | 닫는 것 |
|---|---|
| M1 파일 없음 | 회귀 0 |
| M2 미추적 · 커밋본 인식(출처 값) · 커밋되지 않은 수정 | git 조건(W3′ 는 블록 byte 동일이라 core S3′ 와 중복 — 뺐다) |
| M3 사용자 출처만(상시 답 줄 0) · 정상(`결정 줄:` 머리 · web 상대 위치 · G0 사용자 판단 줄 뒤 M7) | 파일 무관 흐름 · K1 · m5 머리 |
| M4 범주 단독·혼합 · `C<n>` · G0 ⓐ 밖 M | MJ1 규칙 · 묻는다/고친 줄 꼬리 |
| M5 출처 행 · 커밋 비조상 · 처분 ⓑ · 칸 모양 틀린 상시 답 줄 | ①·② · fail-open 봉쇄 |
| M6 표지 없는 절 · G0 절 안 상시 답 줄 · 상시 답 절 안 사용자 줄 | ④ |
| M7 앞선 재상정 사용자 답 뒤 상시 답 줄 | 사용자 답 우선 |
| M8 뒤 절 사용자 답 · 고친 상시 답 줄의 대체 | K3 · m5 |
| M9 맨 `:행` · `2·3` · 판 줄 수 밖 · 슬라이스 0 뒤 드리프트 통과 · 위치 꼬리 글 | m4 · m5 위치 |
| M10 `의미 재상정 키` ≠ 줄 키 · `재상정 키` ≠ `-` | ⑤ |
| M11 재사용 폴더(앞 실행 줄) | m3 |
| M12 적용 커밋 뒤 파일 수정·삭제 · 삭제 뒤 `standing` 없음 | 커밋 기준 · «다음 BC부터» |

## 5. 검증

| 확인 | 결과 |
|---|---|
| `bash dddjango-web/scripts/test/fixtures_refactor_audit.sh` | PASS=107 FAIL=0(기존 77 + M 30) |
| `make verify-web STANDING_CORE=<core 워크트리 refactor_audit.py>` | **exit 0**. `run_fixtures` 16파일 실패 0. self-test claude·codex red 0. 블록 cmp·문단 cmp 통과. byte 미러·references·REQUEST_GUIDE·요청 가이드 계약 통과. 로그 scratch `i1c/verify-web.log` |
| `make verify-web`(이 워크트리의 `dddjango/` — core ㉯ 미착륙 `fcf051fd`) | 블록 cmp 줄에서 red(예상 — core 블록 없음). core ㉯ 가 main 에 착륙하면 인자 없이 green 이어야 한다. 그 전 대조는 `STANDING_CORE=` |
| `claude plugin validate dddjango-web --strict` | exit 0(✔ Validation passed) |
| self-test 음성(임시 플러그인 사본에서 문면 범주 하나 뺌 · 문장 바꿈) | red 1 · red 2(exit 2) |
| 문단 cmp 음성(임시 Codex 사본 두 구 변경) | `**Phase 1~2**`·`**상시 답**` 둘 다 DIFF |
| 변이(임시 scripts 사본에서 검사 하나씩 제거 · scratch `i1c/mutate.py`) | **9/9 잡힘**: 범주 부분집합 · 사용자 답 우선 · 키 행 결속 · 커밋 조상 · 대체 · 마지막 G0 뒤만 · git_snapshot 판 · C 키 묻기 · 위치 fullmatch. 위치 fullmatch 는 첫 회 생존 → M9e(꼬리 글) 추가 뒤 잡힘 |
| Codex byte 미러 | `diff -rq dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts` 차이 0 |

- `make verify`(core 전체)는 돌리지 않았다. 이번 변경은 core 파일과 core 타깃을 건드리지 않는다. Makefile 변경은 `verify-web` 레시피 안뿐이다.

## 6. R8-WR 재생 (scratch 원 사본은 읽기만)

`8-rehearsal/sds-R8-WR` 를 scratch `i1c/replay` 로 `git clone` 하고 산출물 폴더를 rsync 했다. 원 사본 `git status` 는 무변이다. `git_snapshot` `b67f636e` 는 clone 에 있다.

| # | 입력 | 결과 |
|---|---|---|
| ① | 원본 `refactor-scope.md`(사용자 출처 재상정만) · `standing --gate` | `상시 답 줄 0 · 대체 0 · red 0` exit 0 — 파일 없는 흐름 무변 |
| ② | 파일 없음 · `standing` | `상시 답: 없음` exit 0 |
| ③ | 인식 파일(«…» 로 감싼 문장 1줄) 커밋 · `standing` | `인식` · `상시 답 출처: 상시 답 .dddjango/standing-answer.md:1@5a150c19327e` |
| ④ 변형 A | architect 가 M3 에 `외부 관찰 동작 · 경계 교차` 를 적은 경우: M3 는 사용자 출처로 묻고, M5(`테스트 본문 동반` — `test_home_employee_gate.py:70·82·96` · `test_navigation_icons.py:36` 을 위치마다 전체 경로로)와 M7(`외부 관찰 동작 · 테스트 새 판정 · 테스트 본문 동반` — `home_view.py:16-19` · `test_home_conversation.py:131-135`)은 상시 답 절 | `standing --gate` **exit 0** · `상시 답 줄 2` |
| ⑤ 변형 B | architect 가 M3 를 `외부 관찰 동작` 만 적은 경우: M3(+M12)·M5·M7 모두 상시 답 절 | **exit 0** · `상시 답 줄 3`. M3 위치 `home_view_model.py:67` 은 git_snapshot 판(68줄)으로 통과한다. 슬라이스 0 커밋 `f68c1b755` 판은 57줄이라 작업 트리 기준이었다면 red(m4 실물) |
| ⑥ | 원본·A·B 각각 `backstop --debt-residual` · `refactor_audit residual` · `residual_m_sets` | 세 판 모두 같다: `ⓐ 잔존 0 · 재상정 제외 0` · `M_m=3(결정적 잔존 3)` · 의미 재상정 {M3 M5 M7} · 대상 {M17 M18 M19}. clone 작업 트리에는 슬라이스 0 이 없어 결정적 잔존이 3 이다(판끼리 같음이 요점). 표지 줄·계기 줄은 러너가 무시한다 |
| ⑦ 음성 | «동작 변경·테스트 수정이 …»(리뷰 초안 문장) 커밋 | `인식 안 함(문장 없음) — 적용 0` + `기대 문장:` |

→ 기대(설계 §11 정정)대로다: M5·M7 은 덮인다. M3 는 architect 표기에 따라 덮이거나 묻는다.

## 7. diff 통계

`git diff --stat`(HEAD 대비 · I3I4 포함):

```
 Makefile                                           |   4 +-
 .../dddjango-web-design-architect-web/SKILL.md     |   6 +-
 .../skills/dddjango-web-design-review-web/SKILL.md |   8 +-
 codex-dddjango-web/skills/dddjango-web/SKILL.md    |  74 +++---
 .../skills/dddjango-web/scripts/refactor_audit.py  | 273 ++++++++++++++++++++-
 .../scripts/test/fixtures_refactor_audit.sh        | 100 +++++++-
 .../references/design-acquisition.md               |  14 --
 dddjango-web/commands/dddjango-web.md              |  72 +++---
 dddjango-web/scripts/refactor_audit.py             | 273 ++++++++++++++++++++-
 .../scripts/test/fixtures_refactor_audit.sh        | 100 +++++++-
 .../references/design-acquisition.md               |  14 --
 11 files changed, 823 insertions(+), 115 deletions(-)
```

㉯ web 만(임시 인덱스 = HEAD + `I3I4-final.patch` 대비 · 패치 scratch `i1c/I1c-only.patch`):

```
 Makefile                                           |   4 +-
 codex-dddjango-web/skills/dddjango-web/SKILL.md    |   4 +-
 .../skills/dddjango-web/scripts/refactor_audit.py  | 273 ++++++++++++++++++++-
 .../scripts/test/fixtures_refactor_audit.sh        | 100 +++++++-
 dddjango-web/commands/dddjango-web.md              |   4 +-
 dddjango-web/scripts/refactor_audit.py             | 273 ++++++++++++++++++++-
 .../scripts/test/fixtures_refactor_audit.sh        | 100 +++++++-
 7 files changed, 751 insertions(+), 7 deletions(-)
```

새 미추적 파일: 이 기록(`workspace/eval/web-refactor-entry/repair-R8-I1c-impl.md`).

## 8. 남은 위험 · 조율

1. **착륙 순서**
   - `make verify-web`(인자 없음)은 core ㉯ 블록이 같은 트리에 있어야 green 이다. 이 워크트리만 main 에 먼저 들어가면 core 착륙 전까지 red 다.
   - core 가 먼저 착륙한 뒤 core 블록이 다시 바뀌면, 이 기록의 sha 와 대조해 web 블록을 다시 통째로 복사한다.
2. **양방향 대조(m6 후반) — core 파일 몫**
   - `verify-web` 은 자동 경로(`make verify`) 밖이다. 그래서 core 블록을 고친 커밋에서는 대조가 돌지 않는다.
   - 처방은 core 쪽 1건이다: core 러너(`refactor_audit_fixture_run.py`)에 블록 cmp 1사례를 두거나, core 블록 머리 주석에 «고치면 `make verify-web`»을 더한다. 운영 세션이 core 에 전달해야 한다.
3. **옮겨 적기 신뢰**
   - 범주는 architect 가 쓰고 Coordinator 는 옮기기만 한다. 도구는 낱말 ⊆ 3 과 위치 실재만 본다.
   - architect 반환과 결정 줄의 대조는 없다(완료 보고가 파일이 아니다).
   - 행동 시험에서 옮겨 적기가 어긋나면 리뷰 MJ1 처방 4(명세 `## 동작 불변 불가 항목` 표 + 도구 대조)로 간다. 이때 제목은 `## 슬라이스 0 …` 로 시작하면 안 된다(`_SPEC_HEAD_RE`).
4. **architect 반환 형식**
   - `:304` 한 구는 파견 입력 지시다. architect md 는 그대로라, 반환에 범주가 없으면 문면대로 «범주 없음 → 묻는다»로 간다(안전 쪽).
   - 행동 시험에서 반환 누락이 잦으면 architect md `:56` 에 한 구를 넣는다. 이때는 파일 존재를 알리지 않는 문장으로 쓴다.
5. **재개 공백(n7)**: 적용 예정 목록은 G1 승인 전 대화에만 있다. 잃으면 G2 `residual` 이 잔존으로 센다(fail-closed). 문면에는 적지 않았다.
6. **레인 도중 파일 변경**: 파일이 `git_snapshot..HEAD` 에 들면 끝 green ④ `--subst-check` 가 exit 2 다. 막는 것은 캠페인 절차(첫 레인 전 커밋 · 끝에 삭제 · 도중 무변)다.
7. **봉인·배포**: `manifest_seal --write`·`make release-web` 은 하지 않았다. `manifest_seal.py --check --draft`(읽기만) 드리프트 목록: ✗ protocol «봉인 후 변경 — Makefile» · ✗ protocol «tree_sha256 드리프트» — ㉯ 가 Makefile 을 바꿔 생긴 예상 드리프트다(구현 리뷰 n10). 운영 세션이 재발행할 때 정렬한다.
8. **행동 시험(운영 세션 몫)**
   - R8-WR2 형 레인에 파일을 커밋해 돌린다.
   - 기대: architect 완료 보고에 6어 범주와 위치가 붙는다 · 덮는 항목 STOP 0 · 리뷰어가 뺀 항목을 «계획 없음»으로 내지 않는다 · G1 배너 1행 · 승인 뒤 절 · `--gate` exit 0.
   - 음성 대조: 한 글자 다른 파일이면 종전대로 STOP 이어야 한다.

## 9. 구현 리뷰 처분 (review-I1c-impl · **승인** · blocker 0 · major 0 · minor 5 · nit 10)

- 리뷰: scratch `review-I1c/review-I1c-impl.md`(탐침·변이 `impl/`). 운영 세션 지시로 minor·nit 를 이 워크트리에서 수리했다. 커밋·push 는 하지 않았다.
- core 공유 블록은 바꾸지 않았다. sha256 `2a9ae2e4…d1e3` 가 core 워크트리 현재 판과 같다(수리 뒤 재확인).

| # | 리뷰 | 처분 | 구현 |
|---|---|---|---|
| m1 | 배너 괄호 조건이 빠져 파일 없는 실행에 `인식 안 함` 이 나올 여지 | 반영 | `:306`·Codex `:331` «(**파일이 있는데** 인식하지 못하면 …)» — core `:251` 과 같다 |
| m2 | 다중 키 상시 답 줄을 뒤 절이 일부 키만 대체하면 fail-open | 반영 | 대체를 키별 `live` 로 바꿨다(core 와 같은 뜻 · 뒤 재상정 절 한정은 그대로). 전 키가 대체될 때만 `대체`이고, ③ 항목 검사는 `live` 키만 본다. 줄 단위 검사(①·②·사유·범주·위치)는 살아 있는 키가 하나라도 있으면 그대로 돈다. 픽스처 M15 |
| m3 | 범주를 백틱째·쉼표로 옮기면 «묻는다» | 반영(최소) | `re.split(r"[·,]", …)` + `.strip("`")`. 셋 밖 낱말은 여전히 전부 «묻는다»다. 모르는 낱말을 «고친 줄»로 돌리는 선택지는 쓰지 않았다(Coordinator 가 범주 낱말을 고치면 해석이 된다 — MJ1). 픽스처 M16 |
| m4 | 착륙 순서 | 운영 세션 몫 | core 를 먼저 작업 트리에 적용한다(지시) |
| m5 | `--gate` 시점 «⑤ 커밋 뒤» · 도구 문구 | 반영 | 문면 «Phase 2 진입 준비 ⑥(`git_snapshot` 기록) 뒤 첫 coder-web 파견 전»(양 런타임) · 도구 ToolError «… ⑥(`git_snapshot` 기록) 뒤에 돈다» |
| n1 | 디렉터리 위치 통과 | 반영 | `git cat-file blob <snap>:<경로>` — 트리는 실패해 red. 픽스처 M17b |
| n2 | 비UTF-8 위치 exit 1 | 반영 | `UnicodeDecodeError` → 0행(기존 `_lines_of` 와 같다) → red. 픽스처 M17a |
| n3 | 역순·0행·절대 경로 문구 | 반영 | «`파일:행[-행]`(저장소 상대 · 1 ≤ 시작 ≤ 끝) 정형이 아니다»로 따로 낸다. 판 밖은 «git_snapshot 판(…)의 파일·줄 범위에 없다». 픽스처 M17c·d |
| n4 | `_STANDING_LOC` 중복 | 반영 | 기존 `_parse_location`(`:520`) 재사용 · 상수 삭제 |
| n5 | 픽스처 공백 3(생존 변이 3) | 반영 | M13 병합 괄호 · M14 대체는 뒤 재상정 절만(G0 재승인 절 사용자 줄은 대체 아님) · M15 다중 키 부분 대체 |
| n6 | 상시 답 줄 인식이 `출처 = 상시 답` 에만 | 무변 | core `_STANDING_ANY` 와 같게 둔다(실수 둘이 겹쳐야 함) |
| n7 | «외부 동작»↔«외부 관찰 동작» 어휘 차 | 무변(관찰) | 블록 상수라 바꾸지 않는다. 옮겨 적은 «외부 동작»은 셋 밖 → 묻는다(fail-closed). 행동 시험 관찰 항목 |
| n8 | 이미 답한 뺀 항목 재보고를 새 불가로 읽을 여지 | 무변(관찰) | 행동 시험 관찰 항목 |
| n9 | 문면 길이 | 무변 | 리뷰도 «규범 명확성과 맞바꾸는 일이라 권하지 않는다» |
| n10 | 봉인 드리프트 목록 | 반영 | §8-7 에 적었다 |

**수리 뒤 검증**

| 확인 | 결과 |
|---|---|
| `fixtures_refactor_audit.sh` | PASS=115 FAIL=0(M 블록 17묶음 38단언 — M13~M17 추가 · 위치 문구 2 단언 갱신) |
| `make verify-web STANDING_CORE=<core 워크트리 refactor_audit.py>` | **exit 0** · run_fixtures 16파일 실패 0 · self-test claude/codex red 0 · 블록·문단 cmp 통과(로그 scratch `i1c/verify-web-2.log`) |
| `claude plugin validate dddjango-web --strict` | exit 0 |
| 변이 재실행(scratch `i1c/mutate2.py` · 출력 `i1c/mutate2.out`) | **28/28 잡힘** — 구현 변이 9(새 앵커) · 리뷰 변이 13(새 앵커 · 리뷰 생존 3 포함) · 수리분 6(m3 백틱·쉼표 · n1 블롭 · n2 비UTF-8 · n3 시작≤끝 · n3 절대 경로) |
| 문단 cmp · Codex byte 미러 | 같음 · 차이 0 |

**규모(수리 뒤)**: 도구 +277행(수리분 +5 · `_STANDING_LOC` 삭제 포함) · 픽스처 +115행 · Makefile +3 · 문면 ±1줄씩.

**diff 통계(수리 뒤)**
- HEAD 대비(I3·I4 포함): 11 files changed, 865 insertions(+), 115 deletions(-).
- ㉯ web 만(임시 인덱스 = HEAD + `I3I4-final.patch`): 7 files changed, 793 insertions(+), 7 deletions(-) — Makefile +3 −1 · Coordinator +3 −1 · Codex SKILL +3 −1 · `refactor_audit.py` ×2 +277 −1 · 픽스처 ×2 +115 −1. 패치 scratch `i1c/I1c-only.patch` 갱신.
