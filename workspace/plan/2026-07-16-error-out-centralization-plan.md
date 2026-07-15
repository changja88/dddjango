# ErrorOut Centralization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Django Ninja Problem Details의 공통 `ErrorOut`을 contract scope마다 한 번 정의하고, architect가 재사용 결정을 명세하며 coder가 생성 전 재확인하고 각 검증 역할이 BC 로컬 복제와 OpenAPI/runtime drift를 자기 책임 범위에서 차단하도록 플러그인을 개정한다.

**Architecture:** 단일 canonical `NinjaExtraAPI`와 단일 problem profile을 가진 신규 dddjango 표준 표면은 첫 BC부터 `common/ninja/response/error_out.py::ErrorOut`을 사용한다. API/version/profile이 다르거나 기존 레이아웃이 확립돼 있으면 scope별 canonical 경로 또는 기존 경로를 존중한다. 같은 API/namespace/version/core profile은 같은 scope로 추정하며 BC별 extension 차이만으로 scope를 쪼개지 않는다. BC 로컬 Schema는 문서화된 extension의 concrete subclass일 때만 허용하며, BC-specific exception mapping은 계속 BC presentation이 소유한다.

**Tech Stack:** Markdown runtime prompts, Claude/Codex plugin mirrors, Python corpus mirror tooling, Django Ninja/Pydantic Schema examples, pytest/TestClient/OpenAPI contract tests, isolated fresh-context prompt-variant verification.

**Adversarial Review:** corpus/self-consistency PASS · effectiveness/overfit PASS · execution/safety PASS (2026-07-16).

## Global Constraints

- 배포 정본은 `dddjango/`; `codex-dddjango/`는 플랫폼 형식을 보존한 의미 미러다.
- 현 동기 도구와 DR-52에 따라 배포 reference 정본은 `dddjango/skills/*/references/final.md`다. Task 2의 첫 단계에서 이 실제 방향과 충돌하는 `AGENTS.md` 설명을 먼저 정정하고, 배포 reference를 수정한 뒤 `python3 workspace/tools/corpus_mirror_sync.py --write`로 `workspace/reference`와 Codex reference에 전파한다.
- 신규 표준 경로 `<root>/common/ninja/response/error_out.py`는 단일 API/problem profile과 dddjango 표준 레이아웃에만 적용한다. 기존 `src/shared/http/` 같은 공용 레이아웃과 version 규약이 있으면 그 등가 경로를 canonical로 사용한다. version만으로 분리되지 않으면 기존 API package/namespace를 우선하고, 신규 fallback은 `common/ninja/response/<api_namespace>/<version?>/<profile_slug?>/error_out.py`다.
- 중앙화 비교 단위는 `API instance/namespace + public/internal + version + problem profile`로 식별한 contract scope다. `problem profile`은 core required/default, 전역 alias/config, 공통 extension 의미의 실제 wire 차이로 증명하며 problem-specific extension 차이는 scope 분리 근거가 아니다.
- 기존 단일 BC 로컬 Schema는 새 consumer가 없고 error wire contract가 바뀌지 않으면 동일 BC의 다른 코드를 touch해도 강제 이동하지 않는다.
- DRF/plain Django/server-render 계약은 Ninja `ErrorOut`으로 강제 이주하지 않는다.
- 공통 base는 core envelope만 소유한다. BC-specific exception→status/type/title/detail/extension 값 매핑은 BC presentation이 소유한다.
- extension 없는 status는 `ErrorOut`; extension-bearing status는 승인된 concrete subclass를 `response=`에 선언한다. runtime도 해당 Schema를 `model_dump(by_alias=True, exclude_none=True)`로 serialize하며 임의 `**extensions`로 선언 밖 key를 섞지 않는다.
- generic serializer/recognizer/framework handler의 승격 규칙과 birth-common Schema 규칙을 분리한다. common 모듈이 모든 BC 도메인 예외를 import하지 않는다.
- prompt 변경 전에 현재 prompt로 RED baseline을 관측하고, 수정 뒤 같은 fixture의 GREEN과 holdout을 확인한다. simulation은 role markdown만이 아니라 선언된 role prompt+SKILL/reference bundle을 고정하고, 실제 runtime conformance 주장은 live track에만 한정한다.
- 공식 `workspace/eval` 채점 트랙과 역사 결과는 변경하지 않는다. 이번 검증은 `workspace/verification/error-out-centralization/`의 prompt-conformance 실험이다.
- checker 추가, manifest version 변경, 릴리스는 선결정하지 않는다. post-change live failure가 반복되면 구현을 멈추고 별도 설계 승인을 받는다.
- Task 1 이후 모든 shell step은 먼저 summary에서 `REVIEW_BASE`(문서 커밋 전)와 `AUDIT_BASE`(문서 커밋 후)를 복원한다. whole-feature diff는 `REVIEW_BASE..HEAD`, scripts/tools/manifests/eval 불변은 `AUDIT_BASE..HEAD`를 사용한다.

  ```bash
  REVIEW_BASE=$(awk '/^review_base:/{print $2}' workspace/verification/error-out-centralization/summary.md)
  AUDIT_BASE=$(awk '/^audit_base:/{print $2}' workspace/verification/error-out-centralization/summary.md)
  ```

---

### Task 0: 실행 격리, 승인 문서 고정, 감사 기준선

**Files:**
- Commit: `workspace/design/2026-07-16-error-out-centralization-design.md`
- Commit: `workspace/plan/2026-07-16-error-out-centralization-plan.md`
- Create after audit base: `workspace/verification/error-out-centralization/summary.md`

**Interfaces:**
- Consumes: 사용자 승인된 설계·계획.
- Produces: 문서가 보존된 기능 브랜치/격리 worktree, whole-feature `REVIEW_BASE`, 구현 불변 `AUDIT_BASE`.

- [ ] **Step 1: 현재 checkout에서 문서 전 기준과 원 브랜치를 기록한다**

  승인된 두 문서는 현재 checkout의 untracked 파일이므로 먼저 이 checkout에서 전용 planning branch로 옮겨 커밋한 뒤 격리 worktree를 만든다. 구현은 원 checkout에서 시작하지 않는다.

  ```bash
  git status --short
  git branch --show-current
  git switch -c feat/error-out-centralization
  ```

  Expected before branch creation: 위 두 문서만 `??`. 다른 dirtiness가 있으면 보존하고 사용자와 격리 방법을 조정한다.

- [ ] **Step 2: 설계 상태를 승인 반영으로 바꾸고 문서를 커밋한다**

  design 상단 상태를 `사용자 승인·구현 대기`로 바꾼 뒤 다음만 커밋한다.

  ```bash
  git add workspace/design/2026-07-16-error-out-centralization-design.md \
    workspace/plan/2026-07-16-error-out-centralization-plan.md
  git commit -m "docs: plan ErrorOut centralization"
  ```

- [ ] **Step 3: 두 기준 SHA를 고정하고 격리 worktree로 이동한다**

  ```bash
  AUDIT_BASE=$(git rev-parse HEAD)
  REVIEW_BASE=$(git rev-parse HEAD^)
  claude --version
  codex --version
  git switch -
  ```

  `git switch -`는 Step 1 직전 branch로 복귀한다. 그 다음 `superpowers:using-git-worktrees`로 기존 `feat/error-out-centralization` branch를 문서 커밋에서 checkout한 격리 worktree를 만들고 이후 모든 Task를 그 worktree에서 실행한다. untracked 문서를 새 worktree로 복사하거나 재작성하지 않는다. 새 worktree에서 `AUDIT_BASE=$(git rev-parse HEAD)`와 `REVIEW_BASE=$(git rev-parse HEAD^)`를 다시 계산하고 두 SHA를 `summary.md`에 리터럴로 기록한다. 셸 블록 사이 변수 보존에 의존하지 않는다.

  ```text
  review_base: <Task 0 Step 1 pre-document SHA>
  audit_base: <Task 0 Step 2 document commit SHA>
  ```

  `REVIEW_BASE..HEAD`는 design/plan을 포함한 최종 리뷰 범위다. `AUDIT_BASE..HEAD`는 이번 구현에서 금지된 checker/tool/manifest/eval 변경을 판정하는 범위다.

### Task 1: 격리 fixture와 현행 RED baseline

**Files:**
- Create: `workspace/verification/error-out-centralization/fixtures/README.md`
- Create: `workspace/verification/error-out-centralization/fixtures/requirements.in`
- Create: `workspace/verification/error-out-centralization/fixtures/requirements.lock`
- Create: `workspace/verification/error-out-centralization/fixtures/copy_fixture.py`
- Create: `workspace/verification/error-out-centralization/fixtures/resolve_prompt_bundle.py`
- Create: `workspace/verification/error-out-centralization/fixtures/bundle-map.json`
- Create: `workspace/verification/error-out-centralization/fixtures/manifest.sha256`
- Create: `workspace/verification/error-out-centralization/fixtures/scenarios/{A1,C1,R1,T1,D1,O1}/project/**`
- Create: `workspace/verification/error-out-centralization/fixtures/holdouts/{H01..H17}/project/**`
- Create: `workspace/verification/error-out-centralization/fixtures/cost/{initial,birth-stage1,birth-stage2,conditional-stage1,conditional-stage2}/**`
- Create: `workspace/verification/error-out-centralization/fixtures/live/base/project/**`
- Create: `workspace/verification/error-out-centralization/fixtures/live/overlays/{L1,L2,L3,L4}/**`
- Create: `workspace/verification/error-out-centralization/verify_matrix.py`
- Create: `workspace/verification/error-out-centralization/test_verify_matrix.py`
- Create: `workspace/verification/error-out-centralization/summary.md`
- Create: `workspace/verification/error-out-centralization/baseline-summary.md`
- Create: `workspace/verification/error-out-centralization/raw/baseline/<prompt-variant>/<scenario>/rep-01.md` through `rep-05.md`
- Read only: current Claude agents/command and corresponding Codex role SKILLs

**Interfaces:**
- Consumes: current deployed role prompts and raw fixture trees without expected answers.
- Produces: committed bootable fixture sources, 60-row baseline matrix, raw output per rep, role-specific observed failure rationale.

- [ ] **Step 1: oracle 없는 materialized fixture 원본을 작성한다**

  `fixtures/README.md`에는 입력 tree, 요청, 실행 command만 기록하고 기대 action/PASS 조건은 쓰지 않는다. 산문 tree만 두지 않고 각 core scenario와 H01~H17의 실제 Django project를 커밋한다. 공통 최소 파일은 `manage.py`, `pyproject.toml`, `pytest.ini`, `config/{settings.py,urls.py,api.py}`, 필요한 `application/**`, `common/**`, `tests/**`, design-spec input이다.

  `requirements.in`에는 Django/django-ninja/django-ninja-extra/djangorestframework/Pydantic/pytest/pytest-django의 무핀 요구만 두고, 네트워크 설치 승인을 받은 뒤 다음처럼 현재 호환 버전을 resolve해 hash 포함 lock을 커밋한다. baseline과 GREEN은 같은 lock과 temp venv를 사용한다.

  ```bash
  uv pip compile --generate-hashes \
    workspace/verification/error-out-centralization/fixtures/requirements.in \
    --output-file workspace/verification/error-out-centralization/fixtures/requirements.lock
  uv venv /private/tmp/dddjango-error-out-venv
  uv pip sync --python /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/fixtures/requirements.lock
  /private/tmp/dddjango-error-out-venv/bin/python -c \
    'import django, ninja, ninja_extra, pydantic, pytest, pytest_django, rest_framework'
  ```

  install/resolve가 불가능하면 fixture를 bootable이라고 보고하지 않고 baseline 시작을 보류한다.

  `copy_fixture.py`는 선택한 committed project를 `/private/tmp/dddjango-error-out-<scenario>-<variant>-<rep>/`로 byte-for-byte 복사하고 새 git repo/initial commit을 만든다. `manifest.sha256`은 core/holdout/cost/live source와 lockfile의 ordered hash다. baseline과 GREEN은 같은 fixture source commit과 manifest를 사용한다. 각 rep는 새 copy를 사용하여 이전 rep 변경을 격리한다.

  Core scenarios:

  | ID | Prompt owner | Raw fixture/request |
  |---|---|---|
  | A1 | design-architect | 기존 `shared/http/api_problem.py::ApiProblem`이 controller `response=`에서 쓰이는 프로젝트에 새 orders Ninja API 설계 |
  | C1 | coder | 승인 명세는 로컬 core 생성을 요구하지만 실제 tree에는 동일 scope common `ErrorOut` 존재 |
  | R1 | discipline-reviewer | common base와 동일 core를 직접 `Schema`에서 재선언한 BC diff; 옆에는 validator가 다른 lookalike와 DRF Serializer distractor 존재 |
  | T1 | acceptance-tester | full Django API mount, 결정적인 404 core-only/409 extension/422 validation arrange state; core helper는 `type` 누락+`instance: null`, extension은 `available_quantity` 대 runtime `available_qty`, validation alias drift가 있는 실행 가능 프로젝트 |
  | D1 | design-review-api | 같은 API/namespace/version/core인데 BC 이름을 profile로 쪼갠 명세, scope evidence 누락, extension status에 base response 선언 |
  | O1 | Coordinator | 새 Ninja error contract인데 design-spec의 11-slot Error response schema 누락; 뒤이어 stale-spec coder handoff 입력 |

  T1은 full Django client 또는 canonical `NinjaExtraAPI.get_openapi_schema()`로 OpenAPI를 얻고, controller-only client와 `/api/openapi.json`을 섞지 않는다. source fixture에는 boot/smoke PASS와 mismatch 구현만 있고 새 ErrorOut 계약 assertion은 없다. acceptance-tester가 `tests/test_inventory_error_contract.py`를 새로 만들거나 수정한 뒤 exact pytest command가 non-zero Red여야 하며 traceback은 agent가 추가한 assertion을 가리켜야 한다. agent diff를 되돌린 source fixture의 smoke test는 0이어야 하므로 기존 실패 재실행으로 Red를 위장할 수 없다.

  `cost/`의 다섯 snapshot은 같은 initial tree에서 birth-common 2단계와 conditional-local→promotion 2단계를 byte-fixed하게 나타낸다. Task 5는 두 arm 전체의 변경 파일, import churn, alias 판단을 snapshot diff로 계산하며 한쪽의 첫 단계 비용을 생략하지 않는다.

- [ ] **Step 2: prompt-variant 실행 매트릭스를 고정한다**

  이것은 실제 Claude/Codex runtime 우열 평가가 아니라 두 배포 role+skill bundle의 conformance simulation이다. 배포 동작의 최종 증거는 Task 5 live track이다.

  | Variant | Prompt source |
  |---|---|
  | claude-prompt | 해당 `dddjango/agents/*.md` 또는 command + frontmatter/역할 선언의 모든 SKILL 본문 + 각 SKILL이 직접 링크한 전체 `references/final.md` |
  | codex-prompt | 대응 `codex-dddjango/skills/*/SKILL.md` + 역할 선언의 모든 SKILL 본문 + 각 SKILL이 직접 링크한 전체 `references/final.md` |

  `bundle-map.json`은 owner→role/command/declared skills만 매핑하며 scenario별 정답을 담지 않는다. `resolve_prompt_bundle.py`는 이 map과 prompt의 실제 선언을 대조하고 선택적 “관련 절” cherry-pick 없이 위 파일 전체를 temp fixture 안 `prompt-bundle/`에 복사한다. 누락/여분 source가 있으면 fail-closed한다.

  A1/C1/R1/T1/D1/O1 × 2 prompt variants × 5 fresh reps = **60 rows**다. variant별 ordered file list/content SHA를 기록한다. 모든 subagent는 `fork_turns=none`, fixture path와 bundle만 받는다. 이 plan/design과 기대 답, 원 workspace path는 전달하지 않는다. runner는 모든 tool call/path access를 JSONL로 캡처한다. 사용 runner가 전체 tool trace를 제공하지 않으면 그 rep를 conformance 증거로 쓰지 않고 trace 가능한 CLI runner로 교체한다. transcript/tool trace가 fixture와 bundle 밖 경로를 읽으면 그 rep는 오염으로 무효화하고 새 rep로 대체한다.

- [ ] **Step 3: raw output과 provenance를 rep별로 저장한다**

  각 raw 파일은 다음 header와 agent 원문 전체를 가진다.

  ```text
  phase: baseline
  prompt_variant: claude-prompt | codex-prompt
  scenario: A1 | C1 | R1 | T1 | D1 | O1
  rep: 01..05
  model:
  host_cli_version:
  plugin_source_sha:
  prompt_blob_sha:
  prompt_bundle_manifest_sha:
  fixture_sha:
  tool_trace_sha:
  fresh_context: fork_turns=none
  ```

  filesystem을 수정하는 역할은 rep 전후 `git status --short`와 `git diff`를 raw 파일에 포함한다. 읽기 전용 역할은 실제 `file:line` 근거와 search 대상이 원문에 있어야 한다.

- [ ] **Step 4: evaluator가 filesystem/action 기준으로 60 rows를 판정한다**

  `baseline-summary.md` row 형식:

  ```text
  | scenario | prompt_variant | rep | raw link | search evidence |
  filesystem/design action | import/response result | handoff | PASS/FAIL | rationale |
  ```

  자기보고의 `reuse`, `searched`, `blocker` 단어만으로 PASS하지 않는다. A1은 design-spec diff, C1은 로컬 파일 미생성+구조화된 handoff, R1은 실제 duplicate `file:line`, T1은 추가된 outside-in test와 실제 pytest Red, D1은 scope evidence/alias/concrete response finding, O1은 Phase 2 미진입과 G1/G1′ handoff를 본다.

- [ ] **Step 5: matrix 완전성 verifier를 먼저 테스트한다**

  `verify_matrix.py`는 `itertools.product`로 phase별 exact composite key set을 만들고 actual table key의 duplicate/missing/extra를 fail-closed한다. row schema를 파싱해 verdict가 정확히 한 칸이고 값이 `PASS | FAIL` 중 하나인지 강제한다. 각 summary row의 raw link가 유일한 실제 파일이고 raw header의 phase/variant/scenario/rep와 일치하는지도 확인한다. `test_verify_matrix.py`는 정상 set, 한 cell 누락+다른 cell 중복, extra cell, raw 파일 누락, header mismatch, verdict 누락/빈 값/UNKNOWN/복수 verdict를 각각 테스트한다.

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python -m pytest -q \
    workspace/verification/error-out-centralization/test_verify_matrix.py
  ```

  Expected: PASS. verifier test가 green이 아니면 matrix 실행을 시작하지 않는다.

- [ ] **Step 6: RED matrix의 고유 cell과 역할별 실패를 검증한다**

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/verify_matrix.py \
    baseline workspace/verification/error-out-centralization/baseline-summary.md
  FAILS=$(awk '/\| FAIL \|/{n++} END{print n+0}' workspace/verification/error-out-centralization/baseline-summary.md)
  test "$FAILS" -ge 1
  ```

  Expected: exact 60 unique composite cells와 1:1 raw artifacts, 최소 1 FAIL. 더 중요한 적용 규칙은 각 prompt 변경 대상 역할의 해당 cell에 최소 1 FAIL이 있어야 한다는 것이다. 양 variant가 모두 5/5 PASS인 역할 prompt는 Task 3에서 rationalization 문구를 강화하지 않고 새 정본 계약의 필수 배선과 인용 정합만 반영한다.

- [ ] **Step 7: RED artifact를 커밋한다**

  ```bash
  git add workspace/verification/error-out-centralization
  git commit -m "test: capture ErrorOut reuse baseline"
  ```

### Task 2: 공통 Schema·extension·계약 테스트 정본

**Files:**
- Modify first: `AGENTS.md`
- Modify: `dddjango/skills/discipline-houserules/references/final.md`
- Modify: `dddjango/skills/implementation-django-ninja/references/final.md`
- Modify: `dddjango/skills/implementation-test/references/final.md`
- Modify: `dddjango/skills/discipline-houserules/SKILL.md`
- Modify: `dddjango/skills/implementation-django-ninja/SKILL.md`
- Modify: `dddjango/skills/implementation-test/SKILL.md`
- Generated: `workspace/reference/discipline-houserules/reference/final.md`
- Generated: `workspace/reference/implementation-django-ninja/reference/final.md`
- Generated: `workspace/reference/implementation-test/reference/final.md`
- Generated: `codex-dddjango/skills/discipline-houserules/references/final.md`
- Generated: `codex-dddjango/skills/implementation-django-ninja/references/final.md`
- Generated: `codex-dddjango/skills/implementation-test/references/final.md`
- Modify: `codex-dddjango/skills/discipline-houserules/SKILL.md`
- Modify: `codex-dddjango/skills/implementation-django-ninja/SKILL.md`
- Modify: `codex-dddjango/skills/implementation-test/SKILL.md`

**Interfaces:**
- Consumes: design §2의 scope/canonical/base/extension/runtime decisions and Task 1 observed corpus failures.
- Produces: 모든 역할이 인용할 배치·명명·wire profile·outside-in test recipe.

- [ ] **Step 1: 코퍼스 편집 전에 AGENTS.md의 stale corpus-master 설명을 고친다**

  `workspace/reference/**`를 “1차 정본”이라고 한 설명을 배포 reference의 source mirror로 정정한다. `dddjango/skills/*/references/final.md`를 배포 정본으로 편집하고 `corpus_mirror_sync.py --write`가 workspace/Codex reference를 갱신한다는 현재 `write_skill()` 동작과 DR-52를 기록한다. 또한 `codex-dddjango/` 전체가 byte-identical이라는 과도한 설명을 `references/final.md는 corpus tool byte mirror, checker scripts는 별도 cmp byte mirror, role/Coordinator/SKILL 본문은 플랫폼 형식을 보존한 의미 mirror`로 좁힌다. sync 도구 방향은 바꾸지 않는다. 이 정정을 먼저 적용한 뒤 아래 reference 편집을 시작한다.

- [ ] **Step 2: houserules의 기본 트리와 승격 예외를 고친다**

  dddjango 표준 layout은 다음을 보인다.

  ```text
  common/ninja/response/error_out.py -> ErrorOut
  application/<bc>/presentation_layer/schema/ -> schema_in.py, schema_out.py,
  그리고 problem-specific extension이 실제로 있을 때만 <problem>_error_out.py
  ```

  첫-BC 예외가 Schema에만 적용되고 generic helper/handler는 실제 공유 승격, BC-specific mapping은 항상 BC presentation 소유임을 일반 `common/` 규칙 옆에 적는다. 기존 공용 layout 우선, version 경로, 비-version 충돌 시 API package/namespace fallback을 함께 적는다. 같은 API/namespace/version/core profile은 같은 scope로 추정하고 BC별 extension 차이로 profile을 분리하지 않는다.

- [ ] **Step 3: Ninja 예제를 canonical `ErrorOut`으로 통일한다**

  로컬 `ProblemOut` 정의를 제거하고 dddjango 표준 예제는 다음 import를 쓴다.

  ```python
  from common.ninja.response.error_out import ErrorOut
  ```

  기존 프로젝트는 established equivalent path/name을 재사용한다. core-only status만 `ErrorOut`을 선언하고 extension-bearing status는 concrete subclass를 선언한다.

- [ ] **Step 4: 신규 output profile을 명시한다**

  ```python
  class ErrorOut(Schema):
      type: str = "about:blank"
      title: str
      status: int
      detail: str
      instance: str | None = None
  ```

  이 required/default 정책은 RFC 자체가 아니라 dddjango 신규 output profile이다. runtime은 core 4필드를 항상 내고 `instance`는 값이 있을 때만 포함한다. OpenAPI 기대는 `title/status/detail` required, `type` default, `instance` optional nullable로 고정한다.

- [ ] **Step 5: local/shared/validation extension recipe를 추가한다**

  Local concrete example:

  ```python
  class InventoryConflictErrorOut(ErrorOut):
      available_quantity: int
  ```

  API-scope validation example:

  ```python
  class ValidationErrorOut(ErrorOut):
      invalid_params: list[InvalidParamOut] = Field(alias="invalid-params")
  ```

  generic `extensions: dict`, `extra="allow"`, core 복제, base-only extension response, runtime helper의 임의 `**extensions`를 금지한다. core helper는 `ErrorOut`, extension mapping은 승인 concrete Schema를 만들고 모두 `model_dump(by_alias=True, exclude_none=True)`를 사용하는 단일 response 변환점을 통과한다. 동일 scope의 실제 공유 concrete contract는 common으로 승격하고 의미가 불명확하면 architect로 반송한다.

- [ ] **Step 6: implementation-test에 core와 extension 실제 contract test recipe를 추가한다**

  contract scope마다 대표 core-only status 한 개를 먼저 outside-in으로 검사한다. runtime key 집합은 `type/title/status/detail`이고 `type == "about:blank"`, `instance`와 선언되지 않은 extension key는 없음을 단언한다. generated OpenAPI는 `title/status/detail` required, `type` default, `instance` optional nullable인지 확인한다.

  extension-bearing status마다 concrete Schema 밖 key가 없는지까지 다음 테스트를 추가한다.

  ```python
  def _resolve_response_schema(document, path, method, status):
      content = document["paths"][path][method]["responses"][status]["content"]
      media_schema = next(iter(content.values()))["schema"]
      if "$ref" not in media_schema:
          return media_schema
      name = media_schema["$ref"].rsplit("/", 1)[-1]
      return document["components"]["schemas"][name]


  def test_inventory_conflict_problem_contract(client):
      response = client.post(
          "/api/inventory/reservations",
          json={"sku": "SKU-001", "quantity": 2},
      )
      assert response.status_code == 409
      assert response.headers["content-type"].startswith("application/problem+json")
      body = response.json()
      assert body["status"] == 409
      assert isinstance(body["available_quantity"], int)
      assert set(body) == {
          "type", "title", "status", "detail", "available_quantity"
      }


  def test_inventory_conflict_openapi_uses_concrete_schema(api):
      document = api.get_openapi_schema()
      schema = _resolve_response_schema(
          document,
          "/api/inventory/reservations",
          "post",
          "409",
      )
      assert "available_quantity" in schema["properties"]
      assert "available_quantity" in schema["required"]
  ```

  `resolve_response_schema`의 프로젝트 helper가 없으면 테스트 안에서 `$ref`를 한 단계 해소하는 작은 helper를 둔다. 프로젝트가 `get_openapi_schema()`를 노출하지 않으면 실제 URL resolver에 mount된 full Django client로 OpenAPI를 가져오며 controller-only client에 임의 `/api/openapi.json`을 호출하지 않는다. OpenAPI media type은 현 Ninja 한계상 `application/json`일 수 있으므로 Schema ref/shape를 검사하고, runtime에서만 problem+json을 단언한다. `invalid-params`는 wire alias를 리터럴로 단언한다. 테스트는 작성 여부가 아니라 fixture의 exact pytest command에서 예상 Red/최종 Green이 실제 관측되어야 한다.

- [ ] **Step 7: SKILL 요약 세 쌍을 최소 문구로 갱신한다**

  houserules는 canonical placement/scope/local-extension, Ninja는 import/concrete response/helper separation, implementation-test는 OpenAPI+runtime exact contract만 노출한다. reference 전문을 SKILL에 복제하지 않는다.

- [ ] **Step 8: reference mirror와 summary mirror를 검증한다**

  ```bash
  python3 workspace/tools/corpus_mirror_sync.py --write
  python3 workspace/tools/corpus_mirror_sync.py --check
  ```

  Expected: `11/11 in-sync`, exit 0. Codex SKILL 요약은 platform frontmatter를 보존해 수동 의미 미러한다.

- [ ] **Step 9: Task 2를 커밋한다**

  ```bash
  git add AGENTS.md \
    dddjango/skills/discipline-houserules \
    dddjango/skills/implementation-django-ninja \
    dddjango/skills/implementation-test \
    codex-dddjango/skills/discipline-houserules \
    codex-dddjango/skills/implementation-django-ninja \
    codex-dddjango/skills/implementation-test \
    workspace/reference/discipline-houserules \
    workspace/reference/implementation-django-ninja \
    workspace/reference/implementation-test
  git commit -m "docs: define the scoped ErrorOut contract"
  ```

### Task 3: Architect→API review→acceptance/coder→discipline review→Coordinator 배선

**Files:**
- Modify: `dddjango/agents/design-architect.md`
- Modify: `dddjango/agents/design-review-api.md`
- Modify: `dddjango/agents/acceptance-tester.md`
- Modify: `dddjango/agents/coder.md`
- Modify: `dddjango/agents/discipline-reviewer.md`
- Modify: `dddjango/commands/dddjango.md`
- Modify: `codex-dddjango/skills/dddjango-design-architect/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-design-review-api/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-coder/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango/SKILL.md`

**Interfaces:**
- Consumes: Task 2 normative contract and only the failures actually observed in Task 1.
- Produces: 11-slot design decision, reuse-before-create preflight, external contract Red, narrow DRY audit, live handoff/gate.

- [ ] **Step 1: design-architect 조사와 11-slot 산출을 추가한다**

  조사 범위:

  ```text
  established shared HTTP packages
  common/ninja/response/**
  application/*/presentation_layer/schema/**/*{error,problem}*.py
  controller response={...}
  problem helper/handler and public import consumers
  ```

  필수 slots:

  ```text
  contract scope
  scope evidence
  existing canonical path
  base action: reuse | create-common | promote-to-common | preserve-brownfield
  canonical base
  common core profile
  local concrete action: none | reuse | create | promote
  local concrete schema
  local justification
  response declaration
  compatibility
  ```

  `scope evidence`는 같은 API/namespace/version/core profile이면 same-scope 추정을 쓰고, 별도 scope면 관찰 가능한 wire 차이와 compatibility 이유를 쓴다. problem-specific extension 차이만으로 scope를 나누지 않는다. missing/ambiguous slot은 G1로 올린다. 기존 Ninja 존재만으로 발화하지 않고 승인 scope가 endpoint/error contract/response Schema를 새로 만들거나 변경할 때만 요구한다.

- [ ] **Step 2: design-review-api는 외부 계약 의미만 검토한다**

  contract scope/evidence, required/default, 전역 alias/config, extension wire key/type/meaning, version compatibility, status별 concrete response의 완결성을 검토한다. BC 이름만 바꾼 profile 분리와 base-only extension response는 반송한다. 물리 경로와 import DRY는 검사하지 않는다.

- [ ] **Step 3: acceptance-tester에 OpenAPI+runtime 바깥 Red를 추가한다**

  contract scope마다 core-only 대표 status의 OpenAPI required/default/nullable과 runtime core 4필드/instance omission/예상 밖 key 부재를 먼저 실패시킨다. extension-bearing status가 있으면 Task 2 recipe로 generated OpenAPI concrete shape/alias와 TestClient runtime content-type/body/정확한 key 집합을 추가로 실패시킨다. 내부 helper를 직접 import/test하지 않는다.

- [ ] **Step 4: coder에 reuse-before-create preflight와 실제 검증을 추가한다**

  ```text
  Search canonical/common and BC-local error schemas → compare contract scope and
  approved slots → reuse base or create approved concrete extension → declare the
  concrete response → run OpenAPI/runtime contract tests.
  ```

  stale spec, duplicate request, tree mismatch면 파일을 만들지 않고 Coordinator에 구조화된 mismatch를 보고한다. coder가 설계를 조용히 보정하거나 직접 architect를 호출하지 않는다.

- [ ] **Step 5: discipline-reviewer는 DRY·배치·import만 blocker로 감사한다**

  Blockers:

  ```text
  same-scope common base가 있는데 direct core 재선언
  이름만 다른 exact core 복제
  승인 명세 없는 신규 local schema
  승인 명세상 extension인데 common base 미상속
  domain/application의 Ninja ErrorOut import
  stale spec을 발견하고도 Coordinator에 미반송
  ```

  required/default/alias/validator/config/meaning과 generated OpenAPI/runtime 기술 정확성은 새로 판정하지 않고 owner에게 반송한다. versioned/lookalike/DRF distractor를 거짓 blocker로 잡지 않는다.

- [ ] **Step 6: Coordinator에 scope-limited G1/G1′/G2 배선을 추가한다**

  대상 scope에서 11-slot이 불완전하면 Phase 2 미진입. G1 배너 제시 시점뿐 아니라 승인 응답 뒤 Phase 2 dispatch 직전에 current design-spec을 다시 읽어 slot 완결성을 확인한다. 완결 slot은 API reviewer, acceptance-tester, coder, discipline-reviewer 입력에 각 책임 범위만 전달한다. coder stale-spec과 reviewer duplicate blocker는 Coordinator가 G1′로 반송한다. G2에는 canonical import, local concrete 근거, core-only 및 extension OpenAPI/runtime 테스트 실행 결과를 표시한다.

- [ ] **Step 7: baseline에서 실제 관찰된 rationalization만 닫는다**

  “명세가 시켰으므로 검색 생략”, “클래스명이 달라 별개”, “base response로도 runtime extension이 나간다” 등 Task 1 raw output에 실제 존재한 우회만 해당 owner prompt에 최소 보강한다. 다만 scope evidence, 11-slot, core contract test처럼 Task 2에서 새로 확정한 계약의 필수 배선은 baseline PASS 여부와 무관하게 역할별 최소 인용을 추가한다.

- [ ] **Step 8: Claude/Codex 역할 블록을 의미 미러하고 커밋한다**

  각 신규 block에 동일 제목 anchor를 두고 path:line을 verification summary에 기록한다.

  ```bash
  git add dddjango/agents dddjango/commands/dddjango.md \
    codex-dddjango/skills/dddjango-design-architect/SKILL.md \
    codex-dddjango/skills/dddjango-design-review-api/SKILL.md \
    codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md \
    codex-dddjango/skills/dddjango-coder/SKILL.md \
    codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md \
    codex-dddjango/skills/dddjango/SKILL.md
  git commit -m "feat: enforce ErrorOut reuse across pipeline roles"
  ```

### Task 4: 사용자 문서 정렬

**Files:**
- Modify: `README.md`
- Do not modify: `workspace/eval/**`
- Do not yet modify: `workspace/DEVLOG.md`

**Interfaces:**
- Consumes: final public structure and role flow.
- Produces: user-visible standard tree without reopening the closed product eval track.

- [ ] **Step 1: README 표준 트리와 설명을 갱신한다**

  `common/ninja/response/error_out.py`를 단일-scope 신규 표준으로 보이고 BC 로컬 `error_out.py` 기본 생성을 제거한다. 기존 layout/version scope 우선과 local concrete extension 예시를 한 단락으로 추가한다. handler/helper와 BC mapping 소유는 Schema 경로와 분리한다.

- [ ] **Step 2: 공식 eval 파일 무변경을 확인하고 README를 커밋한다**

  ```bash
  git diff --name-only "$AUDIT_BASE"..HEAD -- workspace/eval
  git add README.md
  git commit -m "docs: document the shared ErrorOut contract"
  ```

  Expected before README commit: eval 출력 없음.

### Task 5: Prompt-variant GREEN, holdout, Coordinator live injection

**Files:**
- Modify: `workspace/verification/error-out-centralization/summary.md`
- Create: `workspace/verification/error-out-centralization/green-summary.md`
- Create: `workspace/verification/error-out-centralization/raw/green/**`
- Create: `workspace/verification/error-out-centralization/raw/holdout/**`
- Create: `workspace/verification/error-out-centralization/live-summary.md`
- Create when first escape occurs: `workspace/verification/error-out-centralization/live-retry-summary.md`
- Create: `workspace/verification/error-out-centralization/live/run_live.py`
- Create: `workspace/verification/error-out-centralization/live/scenarios/{L1,L2,L3,L4}.json`
- Create: `workspace/verification/error-out-centralization/live/README.md`
- Create: `workspace/verification/error-out-centralization/live/**`

**Interfaces:**
- Consumes: Task 1 identical fixtures and final prompt pairs.
- Produces: 60/60 core GREEN, 34/34 holdout GREEN, 24-row actual Coordinator gate evidence.

- [ ] **Step 1: 동일 core matrix 60회를 GREEN으로 재실행한다**

  A1/C1/R1/T1/D1/O1 × 2 prompt variants × 5 fresh reps. fixture source commit/manifest와 provenance/raw/diff 판정은 baseline과 동일하고, prompt bundle만 final commit에서 다시 resolve한다.

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/verify_matrix.py \
    green workspace/verification/error-out-centralization/green-summary.md
  FAILS=$(awk '/\| FAIL \|/{n++} END{print n+0}' workspace/verification/error-out-centralization/green-summary.md)
  test "$FAILS" -eq 0
  ```

  `green-summary.md`에는 GREEN과 holdout 표만 둔다.

- [ ] **Step 2: holdout 17 cells를 두 prompt variants에서 1회씩 실행한다**

  총 **34 runs**, 기대를 agent에 노출하지 않는다.

  | ID | Owner | Variation |
  |---|---|---|
  | H01 | architect | touched single-local brownfield, no new consumer |
  | H02 | reviewer | H01 existing local diff must not be new-duplicate blocker |
  | H03 | architect | established DRF error serializer |
  | H04 | architect | plain Django JSON error view |
  | H05 | architect | server-render form/handler500 |
  | H06 | architect | public v1 and internal v1, observable different core profiles; namespace fallback paths |
  | H07 | reviewer | same fields, different required/default |
  | H08 | reviewer | same Python name, different wire alias |
  | H09 | reviewer | validator/config/meaning difference |
  | H10 | architect | API-wide `invalid-params` first-use concrete Schema |
  | H11 | architect | two problems share identical concrete extension |
  | H12 | design-review-api | scope/version/alias/concrete response contract review |
  | H13 | design-review-api | same API/namespace/version/core인데 BC 이름으로 problem profile 분리 시도 |
  | H14 | architect | first Ninja BC, no existing error Schema; birth-common and BC-local core file 0 |
  | H15 | architect | H14 결과에 second same-scope BC 순차 추가; base 이동/import 갱신/alias 비용 0 |
  | H16 | reviewer | 동일 initial의 birth-common 2단계와 conditional-local→promotion 2단계 cost snapshot 대칭 감사 |
  | H17 | architect | H14 결과에 second divergent version/profile 추가; 별도 canonical, false share 0 |

  H14→H15의 실제 final-policy 결과와 `cost/`의 두 2단계 arm을 함께 사용한다. H16은 동일 initial에서 두 arm 각각의 stage1+stage2 전체 변경 파일 수, import churn, 공개 alias 판단 수를 snapshot diff로 다시 계산한다. 이는 first-BC 정책의 우월성을 전제하는 점수가 아니라 채택 trade-off의 대칭 증거다.

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/verify_matrix.py \
    holdout workspace/verification/error-out-centralization/green-summary.md
  FAILS=$(awk '/^\| H(0[1-9]|1[0-7]) .*\| FAIL \|/{n++} END{print n+0}' workspace/verification/error-out-centralization/green-summary.md)
  test "$FAILS" -eq 0
  ```

  Expected: 34 rows, FAIL 0.

- [ ] **Step 3: 실패는 결과 문서가 아니라 소유 Task로 되돌린다**

  정본 실패는 Task 2, 역할/배선 실패는 Task 3으로 돌아간다. Claude/Codex pair를 함께 수정·커밋하고 영향 core 5 reps와 실패 holdout을 fresh context로 전부 다시 실행한다. Task 5에서 prompt 파일을 결과와 섞어 커밋하지 않는다.

- [ ] **Step 4: 실제 `/dddjango` Coordinator 위반 주입을 24 runs로 확인한다**

  역할 격리 simulation과 구분해 기록한다.

  ```text
  L1 missing 11-slot → G1 차단
  L2 stale spec detected by coder → Coordinator G1′ 반송
  L3 base-only extension response 또는 runtime alias drift → acceptance Red → coder handoff/Green → G2
  L4 exact duplicate found by reviewer → blocker 유지, G2 차단
  ```

  `run_live.py`는 stdlib `subprocess`/PTY로 runtime별 resumable session을 구동하고 stdout/stderr JSONL, process PID, session ID, gate banner, gate answer, overlay 적용 전후 fixture SHA와 overlay manifest SHA를 한 run event stream에 기록한다. `scenarios/L*.json`은 동일 raw command, 사전등록 G0/G1/G2 답, 적용할 overlay/hook, expected owner, expected event sequence, final gate outcome(`allow | block`)만 가진다. L3는 Red→Green 뒤 `allow`, L1/L2/L4는 해당 반송 지점에서 `block`이다. expected model wording은 넣지 않는다.

  Claude 첫 turn은 `claude -p --plugin-dir <feature-worktree>/dddjango --session-id <uuid> --output-format stream-json --include-hook-events <command>`이고, 후속 turn은 같은 plugin-dir에 `--resume <uuid> -p --output-format stream-json <gate-answer>`를 사용한다. Codex 첫 turn은 `codex exec --json -C <fixture> <command>`이고 JSONL의 thread/session id를 파싱하여 후속 turn을 `codex exec resume --json <session-id> <gate-answer>`로 잇는다. 각 turn은 정규식 추정이 아니라 Coordinator의 고정 `dddjango · G0/G1/G2 ... 승인` 배너를 확인하고, 예상 배너가 없거나 session id가 달라지면 fail-closed한다.

  Claude는 feature tree를 직접 로드한다. Codex는 현재 프로젝트에서 proven된 installed-cache freshening 경로를 쓴다. `codex plugin list --json`에서 단일 installed/enabled/version row를 해소하고, workspace 밖 cache 수정 승인을 별도로 받은 뒤 다음 fail-closed block 전체를 한 shell에서 실행한다. `run_live.py hash-tree`는 상대 경로+SHA-256 ordered manifest를 출력한다.

  ```bash
  set -euo pipefail
  VERSION=$(codex plugin list --json | python3 -c \
    'import json,sys; rows=json.load(sys.stdin)["installed"]; hits=[x for x in rows if x["pluginId"]=="dddjango@changja88-dddjango" and x["installed"] and x["enabled"]]; assert len(hits)==1; print(hits[0]["version"])')
  CODEX_CACHE="/Users/hyun/.codex/plugins/cache/changja88-dddjango/dddjango/$VERSION"
  test -d "$CODEX_CACHE"
  BACKUP_ROOT=$(mktemp -d /private/tmp/dddjango-codex-cache-backup.XXXXXX)
  BACKUP="$BACKUP_ROOT/cache"
  ORIGINAL_MANIFEST="$BACKUP_ROOT/original.sha256"
  BACKUP_MANIFEST="$BACKUP_ROOT/backup.sha256"
  RESTORED_MANIFEST="$BACKUP_ROOT/restored.sha256"
  FEATURE_MANIFEST="$BACKUP_ROOT/feature.sha256"
  LOADED_MANIFEST="$BACKUP_ROOT/loaded.sha256"
  rsync -a "$CODEX_CACHE/" "$BACKUP/"
  python3 workspace/verification/error-out-centralization/live/run_live.py \
    hash-tree "$CODEX_CACHE" > "$ORIGINAL_MANIFEST"
  python3 workspace/verification/error-out-centralization/live/run_live.py \
    hash-tree "$BACKUP" > "$BACKUP_MANIFEST"
  cmp "$ORIGINAL_MANIFEST" "$BACKUP_MANIFEST"
  restore_cache() {
    rsync -a --delete "$BACKUP/" "$CODEX_CACHE/"
    python3 workspace/verification/error-out-centralization/live/run_live.py \
      hash-tree "$CODEX_CACHE" > "$RESTORED_MANIFEST"
    cmp "$ORIGINAL_MANIFEST" "$RESTORED_MANIFEST"
  }
  trap 'restore_cache' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  rsync -a --delete codex-dddjango/ "$CODEX_CACHE/"
  python3 workspace/verification/error-out-centralization/live/run_live.py \
    hash-tree codex-dddjango > "$FEATURE_MANIFEST"
  python3 workspace/verification/error-out-centralization/live/run_live.py \
    hash-tree "$CODEX_CACHE" > "$LOADED_MANIFEST"
  cmp "$FEATURE_MANIFEST" "$LOADED_MANIFEST"
  FEATURE_ROOT=$(pwd)
  for scenario in L1 L2 L3 L4; do
    for rep in 01 02 03; do
      python3 workspace/verification/error-out-centralization/live/run_live.py run \
        --runtime codex --scenario "$scenario" --rep "$rep" \
        --feature-root "$FEATURE_ROOT"
    done
  done
  restore_cache
  trap - EXIT INT TERM
  ```

  같은 HEAD 재시도도 새 `mktemp` backup을 쓴다. cache 승인, 단일 경로 해소, backup/feature/restore manifest 중 하나라도 실패하면 stale cache로 대체하지 않고 completion을 보류한다.

  Claude도 같은 runner interface로 별도 12 runs를 실행한다.

  ```bash
  set -euo pipefail
  FEATURE_ROOT=$(pwd)
  for scenario in L1 L2 L3 L4; do
    for rep in 01 02 03; do
      python3 workspace/verification/error-out-centralization/live/run_live.py run \
        --runtime claude --scenario "$scenario" --rep "$rep" \
        --feature-root "$FEATURE_ROOT"
    done
  done
  ```

  각 runtime의 command는 `/dddjango ErrorOut 중앙 계약 위반 주입 검증`으로 고정한다. runner는 G1 배너에서 멈춘 같은 session에 L1(11-slot 하나 제거), L2(common과 충돌하는 tree 추가), L3(base/concrete 또는 runtime alias drift) overlay를 적용한 뒤 사전등록 G1 답으로 재개한다. L1은 Coordinator 재검증으로 Phase 2 미진입, L2는 coder preflight mismatch와 G1′ 반송이 PASS다. L3는 `overlay → acceptance 실제 Red → 같은 Red를 coder에 전달 → coder Green → Red 상태에서는 G2 미진입 → Green 뒤 G2 허용`의 전체 event sequence가 있어야 PASS다.

  L4는 G1에서 넣지 않는다. stream의 coder subagent-completed event 직후, discipline-reviewer dispatch event 직전에 exact duplicate overlay를 적용한다. event stream에서 `overlay_applied_at < reviewer_dispatch_at`이 확인되지 않거나 reviewer dispatch가 이미 시작됐으면 그 run은 무효로 폐기하고 fresh rep로 다시 실행한다. L4 PASS는 discipline-reviewer의 duplicate `file:line` blocker와 Coordinator G2 차단이 둘 다 있어야 하며 coder의 선제 수정은 PASS로 세지 않는다. raw transcript와 같은 event stream에 loaded path/hash, fixture SHA, owner finding, gate 결과를 묶는다.

  `live-summary.md`는 runtime/scenario/rep별 한 row를 가지며 다음 gate로 정확히 검증한다.

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/verify_matrix.py \
    live workspace/verification/error-out-centralization/live-summary.md
  FAILS=$(awk '/\| FAIL \|/{n++} END{print n+0}' workspace/verification/error-out-centralization/live-summary.md)
  ```

  Expected initial result는 FAIL 0이다. `FAILS > 0`이면 결과를 숨기거나 덮어쓰지 않고 Step 5의 escape 분류/return path로 이동한다. key/raw/verdict 구조 실패는 escape가 아니라 harness failure이므로 먼저 verifier를 고친다.

- [ ] **Step 5: checker decision gate를 증거 뒤 적용한다**

  L3/L4에 위반 input이 존재했다는 사실 자체는 checker 신호가 아니다. 주입된 위반이 기대 owner gate를 탈출해 mismatch가 남은 채 G2가 잘못 허용됐거나 agent가 새 exact same-scope direct core duplicate/base-only extension response를 생성한 run만 escape failure로 센다.

  initial `live-summary.md`에서 첫 escape가 나오면 Task 3으로 돌아가 해당 Claude/Codex owner pair를 한 차례 보강·의미 미러하고 별도 commit한다. 영향 core 5 reps/variant와 관련 holdout을 fresh context로 다시 통과시킨 뒤, Codex cache safe block을 새 feature SHA로 처음부터 재실행하여 source/loaded hashes를 갱신한다. initial 24 rows와 raw는 덮어쓰지 않는다.

  post-reinforcement L1~L4 × 2 runtimes × 3 reps는 `live/retry-01/**`와 `live-retry-summary.md`에 별도 저장한다. `verify_matrix.py live-retry ... --epoch 01`은 새 exact 24-key set/verdict/raw를 검증한다. 24/24 PASS면 checker를 채택하지 않는다. 같은 escape가 서로 다른 fresh run에서 2회 이상이면 구현을 멈추고 고정밀 checker 별도 설계 승인을 요청한다. 1회면 checker 근거는 부족하지만 completion도 보류하고 prompt failure를 다시 설계 리뷰한다. broad name/field-set checker를 즉흥 추가하지 않는다.

  ```bash
  /private/tmp/dddjango-error-out-venv/bin/python \
    workspace/verification/error-out-centralization/verify_matrix.py \
    live-retry workspace/verification/error-out-centralization/live-retry-summary.md \
    --epoch 01
  RETRY_FAILS=$(awk '/\| FAIL \|/{n++} END{print n+0}' workspace/verification/error-out-centralization/live-retry-summary.md)
  test "$RETRY_FAILS" -eq 0
  ```

- [ ] **Step 6: verification artifact를 커밋한다**

  ```bash
  git add workspace/verification/error-out-centralization
  git commit -m "test: verify ErrorOut reuse pipeline behavior"
  ```

### Task 6: Range 기반 미러·불변·구조 검증

**Files:**
- Verify whole feature since `REVIEW_BASE`; verify forbidden implementation surfaces since `AUDIT_BASE`
- Verify unchanged: `dddjango/scripts/`, Codex checker mirror, `workspace/tools/corpus_mirror_sync.py`, both manifests, `workspace/eval/**`

**Interfaces:**
- Consumes: all implementation and verification commits.
- Produces: range-based proof that committed changes, mirrors, checker catalog, manifests, and history boundaries are intact.

- [ ] **Step 1: corpus mirror를 확인한다**

  ```bash
  python3 workspace/tools/corpus_mirror_sync.py --check
  ```

  Expected: `11/11 in-sync`, exit 0.

- [ ] **Step 2: Claude/Codex 수동 의미 미러 증거를 summary에 기록한다**

  다음 여섯 pair의 신규 anchor path:line과 `scope/slots/preflight/external tests/blockers/handoff` 일치 여부를 checklist로 기록한다.

  ```text
  Coordinator
  design-architect
  design-review-api
  acceptance-tester
  coder
  discipline-reviewer
  ```

  Expected: 6/6 PASS. “수동 확인” 한 줄만 쓰지 않는다.

- [ ] **Step 3: checker 파일·byte mirror·Coordinator catalog 불변을 검사한다**

  ```bash
  test "$(find dddjango/scripts -maxdepth 1 -name 'check-*.py' | wc -l | tr -d ' ')" -eq 19
  test "$(find codex-dddjango/skills/dddjango/scripts -maxdepth 1 -name 'check-*.py' | wc -l | tr -d ' ')" -eq 19
  for file in dddjango/scripts/check-*.py; do
    cmp -s "$file" "codex-dddjango/skills/dddjango/scripts/${file##*/}" || exit 1
  done
  ```

  Expected: exit 0.

  ```bash
  test "$(git show "$AUDIT_BASE":dddjango/commands/dddjango.md | rg -o 'scripts/check-[a-z0-9-]+\.py' | wc -l | tr -d ' ')" -eq 19
  test "$(rg -o 'scripts/check-[a-z0-9-]+\.py' dddjango/commands/dddjango.md | wc -l | tr -d ' ')" -eq 19
  test "$(git show "$AUDIT_BASE":codex-dddjango/skills/dddjango/SKILL.md | rg -o 'scripts/check-[a-z0-9-]+\.py' | wc -l | tr -d ' ')" -eq 19
  test "$(rg -o 'scripts/check-[a-z0-9-]+\.py' codex-dddjango/skills/dddjango/SKILL.md | wc -l | tr -d ' ')" -eq 19
  diff -u \
    <(git show "$AUDIT_BASE":dddjango/commands/dddjango.md | rg -o 'scripts/check-[a-z0-9-]+\.py') \
    <(rg -o 'scripts/check-[a-z0-9-]+\.py' dddjango/commands/dddjango.md)
  diff -u \
    <(git show "$AUDIT_BASE":codex-dddjango/skills/dddjango/SKILL.md | rg -o 'scripts/check-[a-z0-9-]+\.py') \
    <(rg -o 'scripts/check-[a-z0-9-]+\.py' codex-dddjango/skills/dddjango/SKILL.md)
  ```

  Expected: 각 base/current occurrence가 정확히 19이고 ordered sequence diff 출력 없음. 중복 추가나 순서 변경도 실패한다.

- [ ] **Step 4: scripts/tools/manifests/eval range 불변을 검사한다**

  ```bash
  git diff --exit-code "$AUDIT_BASE"..HEAD -- \
    dddjango/scripts \
    codex-dddjango/skills/dddjango/scripts \
    workspace/tools/corpus_mirror_sync.py \
    dddjango/.claude-plugin/plugin.json \
    codex-dddjango/.codex-plugin/plugin.json \
    workspace/eval
  git status --short -- dddjango/scripts codex-dddjango/skills/dddjango/scripts
  ```

  Expected: 출력 없음, exit 0. 새 untracked checker도 두 번째 명령이 잡는다.

- [ ] **Step 5: 명명·경로 잔존 모순을 검색한다**

  ```bash
  rg -n "class ProblemOut|schema_in.py / schema_out.py / error_out.py|error_out.py -> ErrorOut" \
    dddjango codex-dddjango README.md
  ```

  Expected: 신규 표준을 로컬 `ProblemOut`/기본 BC `error_out.py`로 지시하는 잔존 0. 금지·brownfield·이주 설명의 정당한 match는 summary에 path:line과 사유를 기록한다.

- [ ] **Step 6: plugin 구조와 manifest JSON을 검증한다**

  ```bash
  claude plugin validate dddjango --strict
  python3 -m json.tool codex-dddjango/.codex-plugin/plugin.json >/dev/null
  ```

  Expected: Claude `Validation passed`, 두 명령 exit 0.

- [ ] **Step 7: 검증 증거를 커밋한다**

  ```bash
  git add workspace/verification/error-out-centralization/summary.md
  git commit -m "test: record ErrorOut validation evidence"
  ```

- [ ] **Step 8: committed range 전체를 감사한다**

  ```bash
  git diff --check "$REVIEW_BASE"..HEAD
  git diff --stat "$REVIEW_BASE"..HEAD
  git diff "$REVIEW_BASE"..HEAD -- AGENTS.md dddjango codex-dddjango README.md workspace
  git status --short
  ```

  Expected: `diff --check`와 `status` 출력 없음; stat/diff는 계획의 허용 파일만 포함한다.

### Task 7: 실제 결과 DEVLOG와 최종 재검증

**Files:**
- Modify: `workspace/DEVLOG.md`
- Modify: `workspace/verification/error-out-centralization/summary.md`

**Interfaces:**
- Consumes: actual RED/GREEN/live/range validation outputs.
- Produces: honest decision record and clean final branch.

- [ ] **Step 1: DEVLOG에 실제 결과만 기록한다**

  최근 작업 한 줄과 새 DR에 다음을 쓴다.

  ```text
  발단과 contract-scope 결정
  first-BC Schema 예외와 helper/mapping 분리
  architect/coder/reviewer/Coordinator 소유권
  RED 60 rows의 실제 FAIL 수
  GREEN 60/60, holdout 34/34, initial live L1-L4 24행 실제 결과와 (발생 시) retry-01 24/24 결과
  mirror 11/11, checker 19/19 불변, strict validation 결과
  checker 채택/비채택 decision gate 결과
  manifest bump/release 비범위
  codex mirror 범위: reference/checker byte mirror, role/Coordinator/SKILL 의미 mirror
  ```

  DEVLOG 상단의 현재 요약에 남은 “codex 전체 byte-identical” 표현도 위 scoped mirror로 정정한다. 기존 역사적 manifest/version 불일치는 이번 DR에서 소급 정리하지 않고 선재 상태로 남긴다.

- [ ] **Step 2: summary에 최종 command와 path:line 증거를 연결한다**

  raw transcript, prompt blob SHA, role mirror checklist, 정당한 grep 잔존, range validation exit 결과를 링크한다.

- [ ] **Step 3: 최종 문서를 커밋한다**

  ```bash
  git add workspace/DEVLOG.md workspace/verification/error-out-centralization/summary.md
  git commit -m "docs: record ErrorOut centralization verification"
  ```

- [ ] **Step 4: Task 6 전체 range 검증을 마지막 커밋 뒤 다시 실행한다**

  Expected: mirror 11/11, checkers 19/19, strict validation PASS, scripts/tools/manifests/eval `AUDIT_BASE..HEAD` diff 없음, `git diff --check "$REVIEW_BASE"..HEAD` exit 0, `git status --short` 출력 없음.

## Self-Review

- [ ] 첫-BC common은 단일 API/problem profile + dddjango 표준 layout에만 적용되고 versioned/alternate canonical을 거짓 통합하지 않는다.
- [ ] 기존 single-local brownfield는 unrelated touch만으로 이동하지 않는다.
- [ ] base action과 local concrete action이 분리되어 첫 BC+extension 동시 행동을 표현한다.
- [ ] BC-specific mapping, generic framework handlers, birth-common Schema의 위치 규칙이 서로 분리돼 있다.
- [ ] architect/API reviewer/acceptance/coder/discipline reviewer/Coordinator의 소유권이 겹치지 않는다.
- [ ] core-only와 extension runtime/OpenAPI shape 및 예상 밖 key 부재를 실제 outside-in test가 검증한다.
- [ ] baseline/GREEN은 같은 60-cell role+skill bundle matrix이며 committed fixture·oracle·rep 상태가 격리된다.
- [ ] Coordinator live injection은 isolated simulation과 구분되고 L1-L4 × 2 runtimes × 3 reps = 24 rows를 요구한다.
- [ ] checker 비채택은 baseline 전에 고정되지 않고 반복 post-change failure 뒤 별도 승인을 요구한다.
- [ ] 공식 eval과 역사 result는 변경하지 않는다.
- [ ] final whole-feature diff는 `REVIEW_BASE..HEAD`, 금지 surface 불변은 `AUDIT_BASE..HEAD`를 본다.
- [ ] design/plan, raw verification, DEVLOG가 모두 명시된 커밋에 포함된다.
