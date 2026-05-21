수정 대상: skill
원인 분류: P3 responsibility-boundary-progressive-disclosure gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# Implementation Python P3 Skill Analysis

## 평가 범위

- Source skill: `dddjango/skills/implementation-python/SKILL.md`
- Bundled references: `dddjango/skills/implementation-python/references/*.md`
- Metadata: `dddjango/skills/implementation-python/agents/openai.yaml`
- Source reference: `workspace/reference/implementation-python/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/`
- 인접 skill: `source-reference-audit`, `architecture-ddd`, `architecture-api`, `architecture-db`, `architecture-implementation-patterns`, `implementation-django`, `implementation-django-ninja`, `implementation-cleancode`, `implementation-test`, `workflow-dddjango-subagents`

## P3 기준별 평가

1. 직접 책임은 대체로 명확하다. 이 skill은 Python 언어 계층의 type contract, dataclass/Enum/Protocol, pydantic v2 boundary, async/concurrency, exception, Ruff/mypy/pyright 기준을 맡는다.
2. Reference loading은 `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md`로 1단계 직접 링크되어 있고, 각 reference는 source reference의 세부 내용을 runtime용 요약으로 분리한다.
3. `SKILL.md`는 500줄 미만이며 핵심 routing과 runtime rule만 담는다. 세부 규칙은 bundled references로 분리되어 progressive disclosure 구조를 만족한다.
4. 다만 source/reference governance, runtime cache sync, bundled reference parity 같은 source audit 성격의 작업을 `source-reference-audit`로 넘기는 routing이 없었다.
5. REST/API 계약과 DB/transaction/rollout 결정을 한 bullet에서 `architecture-api` 또는 `architecture-db`로 묶어 표현해, 어떤 skill이 어떤 결정을 소유하는지 즉시 판독하기 어려웠다.
6. `Protocol`과 boundary guidance는 Python 표현 책임으로 잘 좁혀져 있지만, repository/UoW/ports/outbox 같은 implementation pattern 결정은 `architecture-implementation-patterns`가 소유한다는 handoff가 `SKILL.md` Routing에는 없었다.
7. function signature와 exception guidance가 `implementation-cleancode`의 function-shape/refactor guidance와 겹칠 수 있었다.
8. `agents/openai.yaml`은 P2에서 정렬됐지만, P3 review에서 overlap-sensitive terms를 더 boundary-aware prompt로 줄이는 편이 낫다고 판단했다.

## 최초 Finding

### Major 1: source/reference governance handoff 누락

- Evidence: `source-reference-audit`는 skill/reference governance, provenance, bundled reference parity, runtime cache sync audit, leakage/boundary review를 소유한다.
- Evidence: `implementation-python` Routing에는 이 handoff가 없어, 현재 P3 같은 skill governance 작업에서 Python implementation skill만으로 처리하는 것처럼 보일 수 있다.
- Impact: architecture, implementation, test, source audit 역할 분리 기준이 P3 요구만큼 명확하지 않다.
- Required fix: source/reference governance와 runtime cache sync audit은 `source-reference-audit`로 넘기도록 `SKILL.md` frontmatter와 Routing에 명시한다.

### Major 2: API/DB handoff 표현이 넓게 묶임

- Evidence: Routing은 REST resource/status/Problem Details/OpenAPI와 DB schema/transaction/locking/migration rollout을 한 bullet에서 `architecture-api` 또는 `architecture-db`로 보낸다.
- Impact: API contract owner와 DB consistency/rollout owner가 분리되어야 하는 작업에서 handoff 기준이 덜 선명하다.
- Required fix: API contract는 `architecture-api`, DB schema/transaction/locking/rollout은 `architecture-db`로 분리해 표현한다.

### Minor 1: repository/UoW/ports/outbox pattern handoff를 SKILL.md에도 노출 필요

- Evidence: `protocols-boundaries.md`는 Repository와 Unit of Work architecture가 주로 `architecture-implementation-patterns` 책임이라고 말한다.
- Evidence: `SKILL.md` Routing과 frontmatter는 이 handoff를 직접 드러내지 않는다.
- Impact: `Protocol`을 사용한다는 이유로 pattern 결정까지 이 skill에서 처리하는 것처럼 읽힐 여지가 있다.
- Required fix: pattern 선택은 `architecture-implementation-patterns`가 소유하고, 이 skill은 이미 선택된 boundary의 Python contract 표현만 맡는다고 명시한다.

### Major 3: function-shape refactor 판단이 Clean Code와 겹칠 수 있음

- Evidence: `typing.md`는 boolean flag, optional behavior, keyword-only argument, `None` 반환 대신 exception 같은 Python call-signature guidance를 제공한다.
- Evidence: `implementation-cleancode`는 flag argument 제거, function split, responsibility, abstraction, error handling을 maintainability refactor 기준으로 판단한다.
- Impact: 두 skill이 같은 function-shape 문제를 서로 다른 기준으로 해결할 수 있다.
- Required fix: Python skill은 mutable defaults, positional-only/keyword-only syntax, annotations, type narrowing 같은 Python call-signature mechanics만 맡고, naming/function split/flag-argument 제거/responsibility separation은 `implementation-cleancode`로 넘긴다.

### Minor 2: UI default prompt가 overlap-sensitive trigger를 그대로 나열함

- Evidence: `agents/openai.yaml` default_prompt는 pydantic, async/concurrency, exceptions를 직접 나열한다.
- Impact: Django Ninja schema/API boundaries, DB/test concurrency, clean-code error handling과 겹치는 요청에서 UI prompt가 이 skill을 과하게 먼저 유도할 수 있다.
- Required fix: default prompt를 Python type contract와 pydantic/Protocol mechanics 중심으로 좁히고, domain/API/DB boundary가 결정된 뒤 사용한다고 명시한다.

## 독립 리뷰 통합

### skill-creator 관점 리뷰

- Blocker: 없음.
- Major: runtime scope가 source basis보다 좁아 source-covered Python work 일부의 trigger/reference discovery가 빠질 수 있다는 지적이 있었다. 이 문제는 runtime skill을 넓히지 않고 reference follow-up으로 분류했다.
- Major: skill-creator `quick_validate.py`가 `yaml` module 부재로 실행되지 않아 validation integrity가 부족하다는 지적이 있었다. 이번 P3의 요구 검증은 project validator인 `validate_skill_docs.py --phase all --skills-dir dddjango/skills`이며, 해당 validator가 frontmatter length, required topic phrase, source/runtime cache까지 검사해 통과했다. `quick_validate.py` 환경 문제는 product finding으로 채택하지 않는다.
- Minor: UI default prompt가 dataclass/Enum/Protocol/context manager/Ruff/version gate를 모두 드러내지 않는다는 지적이 있었다. 다른 review의 over-trigger 우려와 함께 검토해, 전체 inventory를 늘리는 대신 boundary-aware prompt로 좁혔다.
- Note: `SKILL.md`는 500줄 미만이고 bundled references는 모두 1단계 직접 링크로 발견 가능하다.
- Note: reference 중복은 core runtime rule과 세부 판단의 정상적인 분리 수준이며 harmful duplication으로 보이지 않는다.

### 독립 P3 boundary 리뷰

- Blocker: 없음.
- Major: Protocol/port/repository boundary 질문이 `architecture-implementation-patterns`와 겹칠 수 있다는 지적이 있었고, 수정으로 닫았다.
- Major: function signature/error-handling guidance가 `implementation-cleancode`와 겹칠 수 있다는 지적이 있었고, Clean Code handoff를 명시해 닫았다.
- Minor: source `final.md`의 Repository/UoW fallback 문구가 stale이라는 지적은 reference follow-up으로 분류했다.
- Minor: workflow role-map에서 implementation-python이 Django Agent 아래에 있는 점은 `workflow-dddjango-subagents` role-map P3 범위의 잠재 follow-up으로 보며, 이번 target skill의 열린 finding으로 남기지 않는다.
- Minor: UI default prompt가 routing-sensitive terms를 포함한다는 지적은 boundary-aware prompt로 수정해 닫았다.
- Note: source/reference governance handoff, API/DB split, pattern decision handoff, clean-code handoff를 추가한 후 architecture/implementation/test/source-audit/workflow 역할 충돌은 남지 않았다.

## 수정 후 재평가

- `SKILL.md` frontmatter에 `source-reference-audit`와 `architecture-implementation-patterns` handoff를 추가했다.
- Routing 첫머리에 source/reference governance, provenance, bundled reference parity, runtime cache sync audit, leakage/boundary review는 `source-reference-audit`를 사용하도록 추가했다.
- API contract handoff와 DB schema/transaction/locking/rollout handoff를 별도 bullet로 분리했다.
- repository/UoW/ports/outbox/service-layer pattern 선택은 `architecture-implementation-patterns`가 맡고, 이 skill은 선택된 boundary의 Python 표현만 맡는다고 명시했다.
- naming, function split, flag-argument 제거, responsibility separation, abstraction, duplication 같은 refactor/review 판단은 `implementation-cleancode`가 맡고, 이 skill은 Python call-signature mechanics만 맡는다고 명시했다.
- `agents/openai.yaml` default_prompt를 boundary-aware prompt로 좁혔다.
- source reference의 broad general Python material과 stale Repository/UoW fallback은 `workspace/plan/reference_lv_up_plan/implementation-python/analysis/20260521-235142-implementation-python-p3-reference.md`에 후속 분석으로 남겼다.
- `SKILL.md`는 42줄로 500줄 미만이다.
- Bundled references는 모두 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- Source reference 자체의 경계 기준 부족은 발견하지 않았다.
- Source skill과 runtime cache는 sync 후 `diff -qr` 기준 동일하다.

## 최종 판정

- Blocker: 0
- Major: 0
- 열린 Minor: 0

## Reference 후속 필요 여부

- `workspace/reference/implementation-python/reference/final.md`는 Python 언어 특화 source reference로 충분하고, P3에서 발견한 문제는 runtime skill routing/handoff 표현 부족이다.
- 따라서 `reference_lv_up_plan/implementation-python/analysis/`에 새 후속 분석은 작성하지 않는다.

## 수정 필요 범위

- `dddjango/skills/implementation-python/SKILL.md`
- `dddjango/skills/implementation-python/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-python/**`는 수정하지 않는다.
- `dddjango/skills/implementation-python/references/*.md`는 P3 새 finding 없이는 수정하지 않는다.
- 다른 skill, eval case, answer oracle, evaluator, generated run artifact는 수정하지 않는다.

## 재평가 기준

- Python-specific implementation 책임과 source audit, architecture, Django implementation, test, workflow 책임이 충돌하지 않는다.
- `SKILL.md`는 핵심 절차와 routing 중심이고 500줄 미만이다.
- Bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- Source skill과 runtime cache parity를 검증한다.
