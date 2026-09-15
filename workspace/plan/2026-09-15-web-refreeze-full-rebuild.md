# 재동결 전량 재건 — 구현 계획 v2

> **For agentic workers:** `superpowers:subagent-driven-development`(권장) 또는 `superpowers:executing-plans`로 Task 순서대로 실행한다. 단계는 체크박스(`- [ ]`)로 추적한다. 실행 순서: 계획 적대 리뷰 반영 → **사용자 승인** → Task 0~8 순차 → 각 Task 끝 검증 green → 독립 구현 리뷰 → `make verify` → 사용자 승인 뒤 커밋 → 봉인 chore → `make release-web`. **릴리즈는 사용자 승인 뒤 이 계획의 마지막 단계이며 권한 안이다. 권한 밖은 A8 앱 수정뿐이다.** **web 선례 관례대로 현재 작업 트리에서 그대로 작업한다** — 작업 중에는 커밋·스태시·브랜치 전환으로 사용자 미커밋 변경을 수용하지 않는다(릴리즈 직전의 보관·복원 절차는 Task 8 Step 11). 커밋은 Task 8의 사용자 승인 뒤 한 번이며, 그 전 Task 끝의 «기록»은 `git diff --stat`과 변경 파일 hash를 `execution-notes.md`에 남기는 것이다.

**Goal:** «재동결»을 **기존 동결물 전량 폐기 후 재동결**로 바꾼다 — staging에 전량 새로 동결하고, 완전성·입력 게이트를 staging에서 통과시킨 뒤, 파일 단위 재개 가능 트랜잭션으로 교체한다. 차이 대조는 하지 않는다.

**Architecture:** 파괴적 구간을 산문이 아니라 도구가 집행한다 — `refreeze.py`(begin/check/commit/abort · journal · swap-plan)가 폐기 집합 계산·교체·롤백을 맡고, `web_refreeze_contract.py`가 규범 편집의 **완전성을 기계로 보증**한다(손으로 만든 편집 목록이 두 번 샌 것이 v3·v4의 실패 원인). 기존 대조 체계는 제거한다.

**Tech Stack:** Python 표준 라이브러리, Bash 픽스처, Markdown 런타임 지침, Claude/Codex 미러. 새 런타임 의존성 없음.

**Spec:** `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(v5). 진단 `…/eval/web-refreeze-completeness/diagnosis.md`. 검토 원문 `…/design-review/rv-{A,B,R,F,C}.md`·`plan-review.md`. **충돌 시 설계 v5가 우선한다.**

## Global Constraints

- 변경 범위 = `dddjango-web/` · `codex-dddjango-web/` 미러 · `workspace/tools/` · `Makefile` · `docs/DEVELOPMENT.md` §1·§4 · `workspace/design/ontology-adoption-map.html` · workspace 계획/평가 기록. **`.gitignore`는 바꾸지 않는다**(테스트 임시 산출은 OS tempdir 또는 scratchpad).
- **A8 워크트리는 읽기 전용.** 행동 시험은 scratchpad 사본에서만. backend dddjango·ontology·사용자 앱·활성 서버/DB 무수정.
- `scripts`·`assets`·references 4종·`REQUEST_GUIDE.md`는 Claude/Codex **byte 미러**. `commands/dddjango-web.md` ↔ Codex `SKILL.md`, `agents/*.md` ↔ Codex 역할 `SKILL.md`는 **의미 미러**(기계 대조 없음) — **정본과 미러를 같은 Task 같은 턴에서 고친다.**
- exit 계약: `check_design_evidence.py` 0/1/2 유지. `archive_design.py`는 compare 제거 후 **0/1만**. `refreeze.py`는 설계 §4.1 표대로 0/1/2/3.
- **폐기 집합은 포인터로만 정한다.** 어느 포인터에도 없는 `captures/**`는 «고아»로 **지우지 않고 보고**한다.
- 재동결 중 `web/static/images/`에 쓰는 것은 정상이다. 실패 시 `abort`·verified 실패 경로가 `journal.images_before` 차집합을 되돌린다.
- 새 규범 문장은 런타임 프롬프트다 — 설계 근거·메타코멘트를 본문에 넣지 않는다.
- **계약 검사 A·B는 문서 4~9곳을 가로지르므로 어느 중간 Task도 단독으로 green을 만들 수 없다.** 중간 Task의 합격 조건은 **자기 Files 안의 잔존 0**(grep)이고, **A·B·C·D 전건 green은 Task 7 Step 6에서만 요구한다**(plan-review BL-1).

## 파일 구조

| 파일 | 역할 |
|---|---|
| `dddjango-web/scripts/refreeze.py` (신규) | begin/check/commit/abort · journal · swap-plan · 고아 판정 · `--stop-after`(시험용) |
| `dddjango-web/scripts/test/test_refreeze.py` (신규) | 단위 시험 |
| `dddjango-web/scripts/test/fixtures_refreeze.sh` (신규) | 위를 `run_fixtures.sh` 글롭에 배선 |
| `workspace/tools/web_refreeze_contract.py` (신규) | 불변식 A·B·C·D1~D4 + `--self-test` |
| `dddjango-web/scripts/evidence_debt.py`·`evidence_debt_hook.py` | 중단 감지(`_refreeze-*`·`_prev-*`) · defer 문구 |
| `dddjango-web/scripts/backstop.py` | 잔존 감지 |
| `dddjango-web/scripts/archive_design.py` | compare 경로 제거 |
| `dddjango-web/scripts/check_design_evidence.py` | `carried_from` 수용 제거 |
| `dddjango-web/scripts/test/test_interaction_evidence.py` | `carried_from` exit 0 단언 수정 |
| `dddjango-web/commands/dddjango-web.md` (+Codex `SKILL.md`) | 재동결 절·`:70`·`:144`·`:171`⑤·`:227`·`<대상 폴더>` 정의·치환 |
| `dddjango-web/skills/implementation-ui/references/design-acquisition.md` | §2 재작성 · `BUILD`→`TARGET` |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md` | `carried_from`·exit 체계 절 재작성 |
| `dddjango-web/agents/design-review-web.md` (+Codex 역할 SKILL) | 감사 목록의 `carried` |
| `dddjango-web/REQUEST_GUIDE.md` | 부채 문구 |
| `Makefile` · `docs/DEVELOPMENT.md` · `ontology-adoption-map.html` | 배선·문서·조감도 |

---

### Task 0: 작업 전 보존·사본 준비

- [ ] `before/` 보존 — 변경 대상 전 파일을 scratchpad `refreeze-repair/before/`에 복사 + `before-hashes.json`
- [ ] **A8 사본** — `~/.herdr/worktrees/spring_dream_server/a8`에서 `manage.py`·`config/`·`web/`·`.dddjango-web/20260912-1640-web-related-persons`를 scratchpad로 복사한다. **사본이 Django 프로젝트 루트로 성립해야 한다**(§5가 `<ROOT>/web/static/images/`에 쓴다). 복사 후 `shasum` 대조 · A8 원본 `git status` 무변화 확인
- [ ] 합성 픽스처 2종 — ⓐ `interaction_exclusions` 1행 빌드 ⓑ `captures/external/*`를 가진 빌드
- [ ] **브라우저 전제 확인** — `DDDJANGO_WEB_PLAYWRIGHT_MODULE`(이 머신: `~/.npm/_npx/9833c18b2d85bc59/node_modules/playwright`) + `DDDJANGO_WEB_BROWSER_CHANNEL=chrome`. 없으면 Task 8의 B1·B2가 불가하므로 그 자리에서 사용자에게 보고
- [ ] `execution-notes.md` 생성

**합격**: 사본 sha 일치 · A8 원본 무변화 · env 확인 결과 기록

---

### Task 1: `refreeze.py`

**Files**: 생성 `scripts/refreeze.py` · `scripts/test/test_refreeze.py` · `scripts/test/fixtures_refreeze.sh` + **미러 3**

- [ ] **Step 1** 실패 시험 작성 — 다음을 **전부** 열거한다:
  - journal 스키마(설계 §4.2 전 필드) · 3겹 폐기 집합 계산 · **고정 폐기 목록(설계 §2.1)** · 고아 분류
  - **`check`의 검사 내용(설계 §4.4)** — staging 실재 7종(`render-audit.json`은 journal의 `has_render_audit` 조건부) · 3겹 포인터 해소 · archive 원본이면 case마다 v2 관찰 실재 · **폐기 집합 자기 검사**(3겹 ⊆ `discard_set`)
  - `check --render-audit-skipped <enum>`가 journal 값을 내리는 **유일 주체**(설계 §4.1)
  - `begin` 선점 exit 2 · `begin`이 `copied_inputs`를 staging에 복사(설계 §4.3) · `begin`이 `evidence_debt`를 `observe`로 기록(설계 R7)
  - **`commit` planned의 live `scope.md` sha 대조 → 불일치 exit 1**(설계 §3-4·§4.6-1)
  - `commit` discarded·installed의 **네 경우**(설계 §4.6-2·3) — installed는 덮어쓰기
  - verified 실패 → 되감기 + 이미지 차집합 제거 + `evidence_debt_before` 복원 → exit 3(설계 §4.6-4)
  - **`done` 순서**(설계 §4.6-5) — build-state 갱신 → `completed_at` → staging 삭제 → `_prev` 삭제
  - `abort`의 `completed_at` 거부 · `--staging` 중복 시 exit 1
  - **`--stop-after <phase>`**(시험용) — 지정 phase 직후 중단해 B3·B4의 중간 상태를 **재현 가능하게** 만든다
- [ ] **Step 2** red 확인 — `python3 -m unittest dddjango-web/scripts/test/test_refreeze.py`
- [ ] **Step 3** 구현 — 설계 §2.1·§2.2·§3·§4.1~4.6·R7
- [ ] **Step 4** `fixtures_refreeze.sh` 작성(기존 `fixtures_*.sh` 판형) → `run_fixtures.sh` 글롭에 잡히는지 확인
- [ ] **Step 5** green + 미러 3 `cp` + `diff -rq` 0 + 기록

**합격**: 단위 시험 green · `bash dddjango-web/scripts/test/run_fixtures.sh`가 새 픽스처를 실제로 실행 · 미러 0

---

### Task 2: `web_refreeze_contract.py` — **규범 편집보다 먼저**

**Files**: 생성 `workspace/tools/web_refreeze_contract.py`

- [ ] **Step 1** 검사 구현 — 설계 §8의 A·B·C·D1~D4
- [ ] **Step 2** `--self-test` — 합성 입력으로 각 검사가 red/green을 내는지 자기 확인
- [ ] **Step 3** **현재 규범에 대해 실행해 red 목록을 얻는다.** 이 목록이 Task 3·6·7의 작업 지시다
- [ ] **Step 4** red 목록을 `execution-notes.md`에 보존하고 Task별로 분배한다

**합격**: `--self-test` green · 현 규범에 대해 A·B·D1이 **red** · red 목록이 최소한 다음을 포함:
`commands` `:70`·`:129`·`:137`·`:146` · `REQUEST_GUIDE.md:116` · Codex `SKILL.md:123`·`:151` ·
`design-acquisition.md`(§2 전역·`:27`·`:116`) · `design-evidence.md`(`carried_from`·exit 체계) ·
`agents/design-review-web.md:25`

> `verify-web` 배선은 Task 7 Step 5에서 한다.

---

### Task 3: 부채 hook — 중단 감지 + defer 문구

**Files**: `scripts/evidence_debt.py`·`evidence_debt_hook.py`·`test/test_evidence_debt{,_hook}.py` + 미러 4

- [ ] **Step 1** 실패 시험 — 빌드 폴더에 **`_refreeze-*` 또는 `_prev-*`**가 있으면 `interrupted refreeze` 줄(`design-input.json` 없음·`design_status != ready` **두 경우 모두**)
- [ ] **Step 2** red 확인
- [ ] **Step 3** 구현 — 감지를 `build_debt()`/부채 줄 생성 **밖**에. `DECISION_LINE`·undecided 줄에서 defer 허용 목록의 «재동결» 제거
- [ ] **Step 4** 기존 시험의 defer 픽스처 quote 갱신 · green + 미러 0 + 기록

**합격**: 새·기존 시험 green · 미러 0 · **자기 Files 안의 «defer가 재동결 허용» 잔존 0**(계약 A 전건 green은 Task 7)

---

### Task 4: `backstop.py` 잔존 감지

**Files**: `scripts/backstop.py` · `scripts/test/fixtures_*.sh` 해당 + 미러 2

- [ ] **Step 1** 픽스처 — 빌드 폴더에 **`_refreeze-<ts>/` 또는 `_prev-<ts>/`**가 있으면 `[DESIGN] BLOCKER interrupted refreeze`
- [ ] **Step 2** red 확인
- [ ] **Step 3** 구현 — `project_design_builds` 탐색 결과의 각 빌드에 대해 검사(marker 판정 불변)
- [ ] **Step 4** `run_fixtures.sh` green + 미러 0 + 기록

**합격**: 새 픽스처 green · 기존 backstop 픽스처 전건 green

---

### Task 5: 대조 체계 제거

**Files**: `archive_design.py` · `check_design_evidence.py` · `test/test_design_archive.py` · **`test/test_interaction_evidence.py`** + 미러 4

- [ ] **Step 1** `archive_design.py`에서 `--compare-build`·`--compare-out`·`--carried`·`compare_manifests()`·exit 3/4·`_history` 자동 carried 제거
- [ ] **Step 2** `test_design_archive.py`의 `RefreezeCompareTests` 10건 제거 — 잔여 32건이 `archive()`·`archive_files()`·`archive_dependencies()`를 계속 덮는지 확인
- [ ] **Step 3** `check_design_evidence.py`의 `carried_from` 수용 제거
- [ ] **Step 4** **`test_interaction_evidence.py:626` `test_manifest_row_accepts_carried_from_only` 수정** — `carried_from`이 이제 미지 필드이므로 기대 exit를 2로. 이 시험은 `fixtures_interactions.sh:9` → `verify-web` 경로에 있어 빠뜨리면 red(plan-review BL-2)
- [ ] **Step 5** green + 미러 0 + 기록

**합격**: `bash run_fixtures.sh` green · **`dddjango-web/scripts/` 안의** `--compare-build`·`carried_from` 잔존 0(규범 쪽은 Task 6·7 소관)

---

### Task 6: 규범 — Coordinator (+Codex 의미 미러, 같은 턴)

**Files**: `commands/dddjango-web.md` · `codex-dddjango-web/skills/dddjango-web/SKILL.md`

- [ ] **Step 1** `<대상 폴더>` 정의를 «산출물 위치» 절(`:22~`)에 추가
- [ ] **Step 2** 재동결 절 전면 재작성 — 설계 **§1 · §2.1 · §2.2(고아 배너·종료 보고 «미참조 k건 지우지 않음» 1줄 포함) · §3 · §4(절차 전체) · §5(병행 실행 금지) · R6(`interaction_exclusions` 행 재작성·10% 재검증·미대응 행 배너) · R7 · R8 · R9**. «변화 0/차이 있음» 어휘 금지, 결과 보고는 «무엇을 다시 동결했는가» 목록 + `refreeze.py` exit
- [ ] **Step 3** 개별 줄 — `:70` build-state `refreeze` 키 제거 · `:144` 재기준 문장을 재동결 절차 참조로 대체 · `:171` ⑤에 «커밋 전 `_refreeze-*`·`_prev-*` 잔존 없음 확인» 추가 · `:227`을 «openapi 재동결»로 분리
- [ ] **Step 4** **Task 2 red 목록 중 `commands`·Codex `SKILL.md` 항목을 소진할 때까지** 치환 — `<산출물 폴더>`→`<대상 폴더>`(폐기·교체 대상만) · 보존 대상 제외 · `--assets-root` 제외 · `scope.md` 쓰기 수식
- [ ] **Step 5** Codex `SKILL.md`에 같은 의미로 반영(**같은 턴**)
- [ ] **Step 6** `python3 workspace/tools/web_refreeze_contract.py` 실행 → **red 목록에 `commands`·Codex `SKILL.md` 항목이 0**(A·B 전건 green은 Task 7)
- [ ] **Step 7** `claude plugin validate dddjango-web --strict` green + 기록

**합격**: 계약 검사 red 목록에서 이 Task Files 항목 0 · plugin validate green

---

### Task 7: reference·문서 + 배선

**Files**: `references/design-acquisition.md`·`design-evidence.md`·`agents/design-review-web.md`·`REQUEST_GUIDE.md` + byte 미러 4 · Codex 역할 `SKILL.md`(의미 미러) · `Makefile` · `docs/DEVELOPMENT.md`

- [ ] **Step 1** `design-acquisition.md` §2 «재동결» 전면 재작성 + `BUILD`→`TARGET` 치환(§1 `:27`·§3 `:116` 포함 — Task 2 red 목록 기준)
- [ ] **Step 2** `design-evidence.md`의 `carried_from`·exit 체계 **절 단위 재작성**
- [ ] **Step 3** `agents/design-review-web.md:25`의 `carried` 제거 + **Codex 역할 SKILL에 같은 턴 반영**(의미 미러·기계 대조 없음) · `REQUEST_GUIDE.md:116` 부채 문구
- [ ] **Step 4** byte 미러 `cp` + `cmp` 0 · **`REQUEST_GUIDE` 절차 전체**(`docs/DEVELOPMENT.md:69-77`) — 정본 편집 → byte 복사 → `cmp` → `request_guide_contract.py --self-test` → 본 검사 → `reverse_coverage.py`
- [ ] **Step 5** `Makefile verify-web`에 `web_refreeze_contract.py --self-test` + 본 검사 배선
- [ ] **Step 6** **`python3 workspace/tools/web_refreeze_contract.py` A·B·C·D1~D4 전건 green** · `make verify-web` green
- [ ] **Step 7** `docs/DEVELOPMENT.md` — §1 지도에 `scripts/refreeze.py`·`workspace/tools/web_refreeze_contract.py` 행 추가, §4에 «이 계약 검사가 무엇을 보장하는가» 한 문단(선례 `request_guide_contract.py`·`web_hooks_contract.py` 판형) + 기록

**합격**: 계약 검사 전건 green · `make verify-web` green · byte 미러 0

---

### Task 8: 행동 시험·전체 검증·게이트

- [ ] **Step 1** **B1** — A8 사본에서 재동결 완주. 실행 주체 = **별도 `claude -p /dddjango-web:dddjango-web` 세션**(`--plugin-dir`로 이 작업 트리 지정) · env는 Task 0에서 확인한 값 · 비용 수십 분. 합격 = 설계 §10 B1 전항(고아 온존·구현 캡처 온존·배너 k건 보고 포함)
- [ ] **Step 2** **B2** — 드라이버 3번째 case 호출 **직전**에 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`을 부재 경로로 바꾼다(case마다 별도 프로세스라 호출 사이 치환 가능) → `abort` 후 live 바이트 동일·이미지 동일·`evidence_debt` 복원
- [ ] **Step 3** **B3** — `refreeze.py commit --stop-after discarded`로 중간 상태 생성 → hook·backstop이 `interrupted refreeze` 발화 확인 → `commit --resume` 완주
- [ ] **Step 4** **B4** — staging이 만들 이름과 같은 파일을 **폐기 집합 밖** live `captures/`에 심어 충돌 성립 → `installed`가 덮어쓰고 verified green(livelock 없음)
- [ ] **Step 5** **B5·B7** — 재동결 후 hook 부채 없음(`design_status=ready` 상태에서) · `done` 이후 `abort` exit 1 거부·신규 이미지 온존
- [ ] **Step 6** **B6·B10** — 합성 픽스처 2종
- [ ] **Step 7** **B8·B9** — 계약 검사 green · `commands`의 인자 줄 하나를 `<산출물 폴더>`로 되돌려 **D1 red 확인 후 복원**
- [ ] **Step 8** `make verify` 6/6 green · `claude plugin validate` strict green · **조감도 `ontology-adoption-map.html` 갱신**(사용자 상시 지침)
- [ ] **Step 9** 독립 구현 리뷰(서브에이전트) → 반영 → 축소 재리뷰(미해결 0)
- [ ] **Step 10** **사용자 승인 게이트** — 변경 요약 10줄 + A8에서 확인할 것
- [ ] **Step 11** 승인 후 릴리즈 절차:
  1. 사용자 미커밋 파일(`docs/master.html`·`…lanes.md`)을 scratchpad에 보관(sha 기록)
  2. 이번 변경을 커밋 1회
  3. `git checkout -- <보관 파일>`로 **클린 트리** 확보(`Makefile:328-331`이 dirty면 die)
  4. `manifest_seal.py --write` → **별도 chore 커밋**(`docs/DEVELOPMENT.md:149` — 변경 커밋 뒤)
  5. env 확인 후 `make release-web`(선행 `verify-web-browser` ≈19분 · 입력 `printf '1\ny\n'`)
  6. 보관 파일 복원 → sha256 대조

**합격**: B1~B10 전건 · `make verify` 6/6 · 구현 리뷰 미해결 0 · 릴리즈 후 사용자 파일 sha 일치

---

## 행동 시험과 합격 기준

설계 §10 표가 정본이다. **B9가 이번 판형의 핵심 시험**이다 — 손으로 만든 편집 목록을 기계가
실제로 대체하는지 확인한다. B3·B4는 `--stop-after`와 충돌 파일 심기로 **재현 가능**하게 만든다.

## 사용자 결정이 필요한 조건 (기본값)

| 조건 | 기본값 |
|---|---|
| 고아(`captures/` 미참조 파일) | **지우지 않고 보고**. 청소는 별건 지시 |
| 완료 빌드 재동결 시 G2 재대조 | 필요하다고 배너 고지 · 실행은 사용자 지시 |
| `interaction_exclusions` 대응 단위 소실 | 버리지 않고 배너 확인 |
| 릴리즈 버전 | patch(v1.1.15) |
| 브라우저 env 부재 | B1·B2 불가 → 그 자리에서 보고하고 승인 게이트에서 결정 |

## 현재 상태

- 진단 `10faaff2` · 설계 v5 `2c99b6d6`(+§7 보강) · 적대 검토 5기 + 계획 리뷰 1기 반영
- **다음**: 계획 축소 재리뷰 → 사용자 승인 → Task 0
- 코드·규범 무접촉(현재까지 workspace 문서만 커밋)
