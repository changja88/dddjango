# 재동결 전량 재건 — 구현 계획

> **For agentic workers:** `superpowers:subagent-driven-development`(권장) 또는 `superpowers:executing-plans`로 Task 순서대로 실행한다. 단계는 체크박스(`- [ ]`)로 추적한다. 실행 순서: 계획 독립 적대 리뷰 → **사용자 승인** → Task 0~8 순차 → 각 Task 끝 검증 green(Codex 미러 `diff -rq` 0 포함) → 독립 구현 리뷰 → `make verify` → 사용자 승인 뒤 커밋·`make release-web`. **web 선례 관례대로 현재 작업 트리에서 그대로 작업한다** — 커밋·스태시·브랜치 전환으로 사용자 미커밋 변경(`docs/master.html`·`workspace/eval/field-report-4/…lanes.md`)을 수용하지 않는다. 커밋은 Task 8의 사용자 승인 뒤 한 번이며, 그 전 Task 끝의 «기록»은 `git diff --stat`과 변경 파일 hash를 `execution-notes.md`에 남기는 것이다. 릴리즈·A8 앱 수정은 이 계획의 실행 권한 밖이다.

**Goal:** «재동결»을 **기존 동결물 전량 폐기 후 재동결**로 바꾼다 — staging에 전량 새로 동결하고, 완전성·입력 게이트를 staging에서 통과시킨 뒤, 파일 단위 재개 가능 트랜잭션으로 교체한다. 차이 대조는 하지 않는다.

**Architecture:** 파괴적 구간을 산문이 아니라 도구가 집행한다 — `refreeze.py`(begin/check/commit/abort · journal · swap-plan)가 폐기 집합 계산·교체·롤백을 맡고, `web_refreeze_contract.py`가 규범 편집의 **완전성을 기계로 보증**한다(손으로 만든 편집 목록이 두 번 샌 것이 v3·v4의 실패 원인). 기존 대조 체계(`--compare-build`·`refreeze-diff.json`)는 제거한다.

**Tech Stack:** Python 표준 라이브러리(도구·검사기·계약 검사), Bash 픽스처, Markdown 런타임 지침, Claude/Codex 미러. 새 런타임 의존성 없음.

**Spec:** `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(v5). 진단 `workspace/eval/web-refreeze-completeness/diagnosis.md`. 검토 원문 `…/design-review/rv-{A,B,R,F,C}.md`. **충돌 시 설계 v5가 우선한다.**

## Global Constraints

- 변경 범위 = `dddjango-web/` · `codex-dddjango-web/` 미러 · `workspace/tools/` · `Makefile`(verify-web 배선) · `docs/DEVELOPMENT.md` §1 지도 · workspace 계획/평가 기록. **`.gitignore`는 바꾸지 않는다**(테스트 임시 산출은 OS tempdir 또는 scratchpad).
- **A8 워크트리(`~/.herdr/worktrees/spring_dream_server/a8`)는 읽기 전용.** 행동 시험은 scratchpad 사본에서만 한다. backend dddjango·ontology·사용자 앱·활성 서버/DB 무수정.
- `scripts`·`assets`·references 4종·`REQUEST_GUIDE.md`는 Claude/Codex **byte 미러**(각 Task 끝 `cp` 후 `diff -rq`·`cmp` 0). `commands/dddjango-web.md` ↔ Codex `SKILL.md`는 **의미 미러**(`${CLAUDE_PLUGIN_ROOT}` ↔ `${SKILL_DIR}`·`spawn_agent` 관례 유지) — 기계 대조가 없으므로 Task 6에서 두 파일을 같은 턴에 고친다.
- exit 계약: `check_design_evidence.py` 0/1/2 **유지**. `archive_design.py`는 compare 제거 후 **0/1만** 남는다(3·4 폐기). `refreeze.py`는 설계 §4.1 표대로 0/1/2/3.
- **설계 §2.1의 폐기 집합은 포인터로만 정한다.** 어느 포인터에도 없는 `captures/**`는 «고아»로 **지우지 않고 보고**한다.
- 재동결 중 `web/static/images/`에 쓰는 것은 정상이다(§5). 실패 시 `abort`·verified 실패 경로가 `journal.images_before` 차집합을 되돌린다.
- 새 규범 문장은 런타임 프롬프트다 — 설계 근거·메타코멘트를 본문에 넣지 않는다(AGENTS.md).

## 파일 구조

| 파일 | 역할 |
|---|---|
| `dddjango-web/scripts/refreeze.py` (신규) | begin/check/commit/abort · journal · swap-plan · 고아 판정 |
| `dddjango-web/scripts/test/test_refreeze.py` (신규) | 위 단위 시험 |
| `workspace/tools/web_refreeze_contract.py` (신규) | 규범 편집 완전성 불변식 A·B·C·D1~D4 + `--self-test` |
| `dddjango-web/scripts/evidence_debt.py`·`evidence_debt_hook.py` | 중단 감지 · defer 문구 정렬 |
| `dddjango-web/scripts/backstop.py` | 잔존 `_refreeze-*`/`_prev-*` 감지 |
| `dddjango-web/scripts/archive_design.py` | compare 경로 제거 |
| `dddjango-web/scripts/check_design_evidence.py` | `carried_from` 수용 제거 |
| `dddjango-web/commands/dddjango-web.md` (+Codex `SKILL.md`) | 재동결 절·`:144`·`:227`·`<대상 폴더>` 정의·치환 |
| `dddjango-web/skills/implementation-ui/references/design-acquisition.md` | §2 재작성 · `BUILD`→`TARGET` |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md` | `carried_from`·exit 체계 절 재작성 |
| `dddjango-web/agents/design-review-web.md` (+Codex 역할 SKILL) | 감사 목록의 `carried` |
| `dddjango-web/REQUEST_GUIDE.md` | 부채 문구 |
| `Makefile` | `verify-web`에 계약 검사 배선 |

---

### Task 0: 작업 전 보존·사본 준비

- [ ] `before/` 보존 — 변경 대상 전 파일을 scratchpad `refreeze-repair/before/`에 복사하고 `before-hashes.json` 기록
- [ ] A8 **사본** 생성 — `~/.herdr/worktrees/spring_dream_server/a8`의 `web/`·`.dddjango-web/20260912-1640-web-related-persons`를 scratchpad로 복사(원본 무수정 · 복사 후 `shasum` 대조)
- [ ] 합성 픽스처 2종 준비 — ⓐ `interaction_exclusions` 1행 빌드 ⓑ `captures/external/*`를 가진 빌드
- [ ] `execution-notes.md` 생성(각 Task 끝 기록처)

**검증**: 사본 sha가 원본과 일치 · A8 원본 `git status` 무변화

---

### Task 1: `refreeze.py`

**Files**: 생성 `dddjango-web/scripts/refreeze.py` · `dddjango-web/scripts/test/test_refreeze.py` · 미러 2

- [ ] **Step 1** 실패 시험 작성 — journal 스키마(설계 §4.2) · 3겹 폐기 집합 계산 · 고아 분류 · `begin` 선점 exit 2 · `abort`의 `completed_at` 거부 · `commit` 단계별 멱등(설계 §4.6-2·3의 네 경우) · verified 실패 시 이미지·`evidence_debt` 되감기
- [ ] **Step 2** 시험 red 확인 — `python3 -m unittest dddjango-web/scripts/test/test_refreeze.py`
- [ ] **Step 3** 구현 — 설계 §4.1 인자·exit · §4.2 journal · §4.6 swap-plan phase 전이. `begin`이 `build-state.json.evidence_debt`를 `observe`로 기록(설계 R7)
- [ ] **Step 4** green 확인 + 미러 `cp` + `diff -rq` 0
- [ ] **Step 5** 기록

**합격**: 단위 시험 green · 미러 0 · `refreeze.py --help`가 4 서브커맨드 노출

---

### Task 2: `web_refreeze_contract.py` — **규범 편집보다 먼저**

**Files**: 생성 `workspace/tools/web_refreeze_contract.py`

- [ ] **Step 1** 검사 구현 — 설계 §8의 A·B·C·D1~D4. D1은 두 문서의 **코드 조각 안** 자리표시자(`<산출물 폴더>`·`BUILD`) + 폐기 대상 이름(고정 목록 + `captures` + `--build`) 인접 패턴을 0으로 요구. D2는 보존 대상(`motion-notes.md`·`build-state.json`·`visual-check.md`·`design-spec.md`·`visual-evidence.json`)이 치환돼 있으면 red
- [ ] **Step 2** `--self-test` 추가 — 합성 입력으로 각 검사가 red/green을 내는지 자기 확인
- [ ] **Step 3** **현재 상태에서 실행해 red 목록을 얻는다** — 이 목록이 Task 6·7의 작업 지시다(사람이 만든 열거를 대체)
- [ ] **Step 4** 기록 — red 목록을 `execution-notes.md`에 보존

**합격**: `--self-test` green · 현 규범에 대해 D1이 **red**(= 그물이 실제로 작동) · red 목록이 rv-F B-1·rv-C N-B1·N-B2의 실측 위치를 **포함**

> `verify-web` 배선은 Task 7 끝에서 한다 — 그 전에는 verify가 red이므로.

---

### Task 3: 부채 hook — 중단 감지 + defer 문구 정렬

**Files**: `dddjango-web/scripts/evidence_debt.py`·`evidence_debt_hook.py`·`test/test_evidence_debt{,_hook}.py` + 미러 4

- [ ] **Step 1** 실패 시험 — 빌드 폴더에 `_refreeze-*`가 있으면 `interrupted refreeze` 줄이 난다(`design-input.json` 없음·`design_status != ready` 두 경우 **모두**에서)
- [ ] **Step 2** red 확인
- [ ] **Step 3** 구현 — 감지를 `build_debt()`/부채 줄 생성 **밖**에 둔다(설계 R9). `DECISION_LINE`·undecided 줄에서 defer 허용 목록의 «재동결» 제거
- [ ] **Step 4** 기존 시험의 defer 픽스처 quote 갱신 · green + 미러 0
- [ ] **Step 5** 기록

**합격**: 새 시험 green · 기존 `test_evidence_debt{,_hook}.py` green · 계약 검사 A green

---

### Task 4: `backstop.py` 잔존 감지

**Files**: `dddjango-web/scripts/backstop.py` · 픽스처 + 미러 2

- [ ] **Step 1** 픽스처 — 빌드 폴더에 `_refreeze-<ts>/`가 있으면 `[DESIGN] BLOCKER interrupted refreeze`
- [ ] **Step 2** red 확인
- [ ] **Step 3** 구현 — 기존 `project_design_builds` 탐색 결과의 각 빌드에 대해 검사(marker 판정을 바꾸지 않는다)
- [ ] **Step 4** `run_fixtures.sh` green + 미러 0
- [ ] **Step 5** 기록

**합격**: 픽스처 green · 기존 backstop 픽스처 전건 green

---

### Task 5: 대조 체계 제거

**Files**: `archive_design.py` · `check_design_evidence.py` · `test/test_design_archive.py` + 미러 3

- [ ] **Step 1** `archive_design.py`에서 `--compare-build`·`--compare-out`·`--carried`·`compare_manifests()`·exit 3/4·`_history` 자동 carried 제거
- [ ] **Step 2** `test_design_archive.py`의 `RefreezeCompareTests` 10건 제거 — **잔여 32건이 `archive()`·`archive_files()`·`archive_dependencies()`를 계속 덮는지 확인**
- [ ] **Step 3** `check_design_evidence.py`의 `carried_from` 수용 제거(`:1140-1143` 부근)
- [ ] **Step 4** green + 미러 0 + 계약 검사 B green
- [ ] **Step 5** 기록

**합격**: 남은 시험 전건 green · `--compare-build` 참조 0

---

### Task 6: 규범 — Coordinator (+Codex 의미 미러)

**Files**: `commands/dddjango-web.md` · `codex-dddjango-web/skills/dddjango-web/SKILL.md`

- [ ] **Step 1** `<대상 폴더>` 정의를 «산출물 위치» 절에 추가(설계 §4.3)
- [ ] **Step 2** 재동결 절 전면 재작성 — 설계 §1·§2·§3·§4(절차)·R7·R8·R9. «변화 0/차이 있음» 어휘 금지, 결과 보고는 «무엇을 다시 동결했는가» 목록 + `refreeze.py` exit
- [ ] **Step 3** `:144` 재기준 문장을 재동결 절차 참조로 대체(설계 §1) · `:227`을 «openapi 재동결»로 분리
- [ ] **Step 4** **Task 2의 red 목록을 소진할 때까지** 치환 — `<산출물 폴더>`→`<대상 폴더>`(폐기·교체 대상만) · 보존 대상은 그대로 · `--assets-root` 제외 · `scope.md` 쓰기 수식
- [ ] **Step 5** Codex `SKILL.md`에 같은 의미로 반영(같은 턴에서)
- [ ] **Step 6** `python3 workspace/tools/web_refreeze_contract.py` 실행 → **A·D1~D4 green**
- [ ] **Step 7** 기록

**합격**: 계약 검사 A·D1~D4 green · `claude plugin validate dddjango-web --strict` green

---

### Task 7: reference·문서 + 배선

**Files**: `references/design-acquisition.md`·`design-evidence.md`·`agents/design-review-web.md`·`REQUEST_GUIDE.md` + byte 미러 4 · Codex 역할 SKILL · `Makefile` · `docs/DEVELOPMENT.md`

- [ ] **Step 1** `design-acquisition.md` §2 «재동결» 전면 재작성 + `BUILD`→`TARGET` 치환(§1·§3 수집 인자 포함 — Task 2 red 목록 기준)
- [ ] **Step 2** `design-evidence.md`의 `carried_from`·exit 체계 **절 단위 재작성**(행 지정 집행 금지)
- [ ] **Step 3** `agents/design-review-web.md`의 `carried` 제거 · `REQUEST_GUIDE.md` 부채 문구(설계 R8)
- [ ] **Step 4** byte 미러 `cp` + `cmp` 0
- [ ] **Step 5** `Makefile verify-web`에 `web_refreeze_contract.py --self-test`와 본 검사 배선 · `docs/DEVELOPMENT.md` §1 지도에 신규 2파일 행 추가
- [ ] **Step 6** `make verify-web` green
- [ ] **Step 7** 기록

**합격**: `make verify-web` green(계약 검사 포함) · byte 미러 0

---

### Task 8: 행동 시험·전체 검증·게이트

- [ ] **Step 1** B1 — A8 사본에서 재동결 완주(설계 §10 합격 조건 전항)
- [ ] **Step 2** B2 — 드라이버 실패 주입 → `abort` 후 바이트 동일
- [ ] **Step 3** B3 — `commit`을 `discarded`에서 중단 → `--resume` 완주 · 중간 상태에서 hook·backstop 발화
- [ ] **Step 4** B4 — `installed` 이름 충돌 주입 → 덮어쓰기 통과(livelock 없음)
- [ ] **Step 5** B5·B7 — 재동결 후 hook 부채 없음(ready 상태) · `done` 이후 `abort` 거부
- [ ] **Step 6** B6·B10 — 합성 픽스처 2종(예외 행 · `captures/external/*` 고아 온존)
- [ ] **Step 7** B8·B9 — 계약 검사 green · **치환 누락 주입 시 D1 red**(그물 실효 확인)
- [ ] **Step 8** `make verify` 6/6 green · `claude plugin validate` strict green
- [ ] **Step 9** 독립 구현 리뷰(서브에이전트) → 반영 → 축소 재리뷰
- [ ] **Step 10** **사용자 승인 게이트** — 변경 요약 10줄 + A8에서 확인할 것
- [ ] **Step 11** 승인 후 커밋 1회 → 봉인 재발행(별도 chore 커밋) → `make release-web`

**합격**: B1~B10 전건 · `make verify` 6/6 · 구현 리뷰 미해결 0

---

## 행동 시험과 합격 기준

설계 §10 표가 정본이다. 요약: **B1**(완주·고아 온존·구현 캡처 온존) · **B2**(실패 롤백 바이트 동일) ·
**B3**(중단 재개) · **B4**(이름 충돌) · **B5**(부채 해소) · **B6**(예외 행 이월) · **B7**(done 후 abort 거부) ·
**B8**(계약 green) · **B9**(치환 누락 주입 → D1 red) · **B10**(`external/` 고아 온존).

B9가 이번 판형의 핵심 시험이다 — 손으로 만든 편집 목록을 기계가 실제로 대체하는지 확인한다.

## 사용자 결정이 필요한 조건 (기본값)

| 조건 | 기본값 |
|---|---|
| 고아(`captures/` 미참조 파일) 처리 | **지우지 않고 보고**(설계 §2.2). 청소를 원하면 별건 지시 |
| 완료 빌드 재동결 시 G2 재대조 | 필요하다고 배너 고지(설계 R7). 재대조 실행은 사용자 지시 |
| `interaction_exclusions` 대응 단위 소실 | 버리지 않고 배너 확인(설계 R6) |
| 릴리즈 버전 | patch(v1.1.15) — `make release-web`에서 선택 |

## 현재 상태

- 진단 `10faaff2` · 설계 v5 `2c99b6d6` · 적대 검토 5기(rv-A·rv-B·rv-R·rv-F·rv-C) 반영 완료
- **다음**: 계획 독립 적대 리뷰 → 사용자 승인 → Task 0
- 코드·규범 무접촉(현재까지 workspace 문서만 커밋)
