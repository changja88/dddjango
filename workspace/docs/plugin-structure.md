# Plugin Structure

이 문서는 `dddjango` 플러그인의 파일 구조와 배치 기준을 정의한다. 개발은 기본적으로 workspace 안에서 진행한다.

## 1. 개발 위치

모든 개발 산출물은 원칙적으로 workspace 안에 둔다.

루트 아래 파일은 플러그인 시스템이나 에이전트 런타임이 반드시 요구하는 경우에만 만든다.

## 2. 목표 구조

```text
workspace/
  docs/
    spec.md
    reference-index.md
    ddd-implementation-standard.md
    skill-hierarchy.md
    skill-contracts.md
    workflow.md
    validation-plan.md
    plugin-structure.md
    skill-authoring.md
  reference/
    architecture-ddd/
    architecture-db/
    architecture-api/
    implementation-django/
    implementation-python/
    implementation-cleancode/
    implementation-tdd/
    implementation-test/

dddjango/
  .codex-plugin/
    plugin.json
  skills/
    source-reference-audit/
      SKILL.md
      agents/
        openai.yaml
    architecture-ddd/
      SKILL.md
      agents/
        openai.yaml
      references/
    architecture-implementation-patterns/
      SKILL.md
      agents/
        openai.yaml
      references/
    architecture-db/
      SKILL.md
      agents/
        openai.yaml
      references/
    architecture-api/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-django/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-django-ninja/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-django-web/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-python/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-cleancode/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-tdd/
      SKILL.md
      agents/
        openai.yaml
      references/
    implementation-test/
      SKILL.md
      agents/
        openai.yaml
      references/
    workflow-dddjango-subagents/
      SKILL.md
      agents/
        openai.yaml
      references/

.agents/
  plugins/
    marketplace.json
plugins/
  dddjango -> ../dddjango
```

`workspace/docs`는 스킬 개발 전 설계 문서의 canonical 위치다. `workspace/reference`는 기존 source reference corpus다. 런타임 플러그인에 들어가는 skill-bundled reference는 `dddjango/skills/<skill>/references/` 아래에 둔다.

`dddjango/`가 workspace 밖 또는 repo root 아래에 생성되는 경우는 플러그인 런타임이 해당 위치를 요구할 때만 허용한다. 그 외 개발 산출물은 `workspace/` 아래에 둔다.

`.agents/plugins/marketplace.json`은 Codex local marketplace가 repo root를 source로 읽을 때 `dddjango` plugin bundle을 발견하기 위한 repo-root 예외 파일이다. Codex local marketplace의 표준 배치가 `./plugins/<plugin-name>`이므로 `plugins/dddjango`는 canonical plugin root인 `../dddjango`를 가리키는 symlink다. 실제 수정 source of truth는 `dddjango/`이다.

현재 `dddjango/skills/...`는 계획된 런타임 플러그인 구조다. 실제 스킬 폴더를 생성하기 전에는 `workspace/docs`와 `workspace/reference`를 authoring source로 사용한다.

## 2.1 Runtime 동기화 기준

runtime skill을 생성하거나 설치된 plugin cache를 갱신할 때는 `workspace/docs`와 `workspace/reference`를 canonical source로 본다. `workspace/docs`는 제품/구조/검증 기준의 canonical source이고, `workspace/reference`는 skill-bundled reference를 만들 때의 source corpus다.

- 기본 수정 대상은 workspace 안의 문서와 소스다. 설치된 plugin cache는 현재 세션의 활성 runtime 동작을 검증하거나 긴급히 보정해야 할 때만 수정한다.
- plugin cache를 수정한 경우 같은 변경 의도는 반드시 workspace canonical source에 먼저 있거나 같은 작업에서 반영되어야 한다. cache-only 변경은 완료 상태로 보지 않는다.
- plugin cache의 내용을 workspace canonical source로 역수입하지 않는다. cache와 workspace가 충돌하면 `workspace/docs`와 `workspace/reference`를 기준으로 cache를 다시 생성하거나 보정한다.
- workspace 밖 runtime 위치를 수정한 경우 완료 보고에 수정한 cache 경로와 workspace 반영 위치를 함께 남긴다.
- `workflow-dddjango-subagents`의 role map은 `workspace/docs/workflow.md`의 역할 분해 표와 동일한 책임 및 skill 구성을 유지한다.
- runtime `SKILL.md`와 `references/role-map.md`는 표현 언어를 바꿀 수 있지만 역할의 책임과 관련 skill을 축소하지 않는다.
- Django Agent가 template/static/web 책임을 포함하면 `implementation-django-web`을 반드시 포함한다.
- runtime 갱신 후에는 `validation-plan.md`의 workflow contract와 skill folder validation을 다시 확인한다.

## 3. Skill 파일 기준

각 skill은 반드시 `SKILL.md`를 가진다.

`SKILL.md`에는 다음만 둔다.

- YAML frontmatter의 `name`
- YAML frontmatter의 `description`
- 핵심 절차
- 읽어야 할 reference 안내
- 경계와 금지 사항

긴 설명, 예시, 논거, 비교표는 `references/`로 분리한다.

## 4. Reference 파일 기준

각 skill의 reference는 한 단계 아래에 둔다.

깊은 중첩 reference를 만들지 않는다. `SKILL.md`에서 직접 링크할 수 있어야 한다.

reference는 필요한 경우에만 읽히도록 분리한다.

`workspace/reference/<area>/reference/final.md`는 source reference다. 이를 런타임 skill reference로 옮길 때는 그대로 복사하지 않고, 각 skill이 실제로 읽을 주제 단위 문서로 요약하거나 분할한다.

DRF처럼 신규 구현 표준이 아닌 내용은 runtime reference로 옮길 때 `legacy`, `migration`, `comparison` 범위를 명시한다.

예:

```text
skills/architecture-ddd/
  SKILL.md
  references/
    strategic-design.md
    tactical-patterns.md
    context-map.md
```

## 5. Claude Code와 Codex 공통성

Claude Code와 Codex에서 같은 결론을 내리도록 다음을 공통으로 유지한다.

- 스킬 이름
- 스킬 책임
- reference 파일명
- DDD 구현 표준
- Django Ninja API 표준
- 검증 원칙

플랫폼별 차이는 packaging 또는 metadata에만 둔다. 도메인 판단과 구현 기준을 플랫폼별로 다르게 만들지 않는다.

## 6. 작성 순서

1. `workspace/docs` 문서를 기준으로 제품/설계 기준을 고정한다.
2. `skill-contracts.md`를 기준으로 각 skill의 책임을 확정한다.
3. `ddd-implementation-standard.md`와 `reference-index.md`를 기준으로 각 skill reference를 나눈다.
4. `skill-authoring.md`를 기준으로 `SKILL.md` frontmatter의 `name`과 `description`을 작성한다.
5. `SKILL.md`는 짧게 작성한다.
6. `agents/openai.yaml`은 최종 `SKILL.md`와 일치하도록 생성하거나 갱신한다.
7. runtime reference split plan에 따라 `references/`를 구성한다.
8. validation scenario와 skill folder validation으로 실제 동작과 구조를 확인한다. 문서 단계 검증은 `python3 workspace/scripts/validate_skill_docs.py --phase docs`로 실행하고, skill folder 생성 뒤에는 `python3 workspace/scripts/validate_skill_docs.py --phase generated --skills-dir dddjango/skills`를 실행한다.

## 7. Runtime Reference Split Plan

최종 skill reference는 다음처럼 시작한다. 전용 source reference가 없는 항목은 먼저 source reference를 만들거나 provisional로 표시한다.

`architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web`은 현재 전용 source reference가 부족하다. 이 세 skill은 다음 중 하나를 만족하기 전까지 완성된 runtime skill로 표시하지 않는다.

- 전용 source reference를 `workspace/reference/<skill>/reference/final.md`에 만든다.
- `SKILL.md` frontmatter 또는 body에 provisional 상태와 fallback source를 명시한다.
- `agents/openai.yaml`의 설명이 완성된 전용 reference가 있는 것처럼 과장하지 않는다.
- validation에서 provisional 상태를 허용할지, 생성 차단할지 명시적으로 선택한다.

| Skill | Source status | Runtime references |
|---|---|---|
| `source-reference-audit` | ready | none; loads existing source docs and runtime references conditionally |
| `architecture-ddd` | ready | `strategic-design.md`, `tactical-patterns.md`, `context-map.md`, `domain-events.md` |
| `architecture-implementation-patterns` | provisional until dedicated source reference exists | `pattern-selection.md`, `ports-adapters.md`, `repository-uow.md`, `outbox-acl.md` |
| `architecture-db` | ready | `schema-modeling.md`, `constraints-indexes.md`, `transactions-locking.md`, `rollout-constraints.md` |
| `architecture-api` | ready | `rest-contracts.md`, `problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md` |
| `implementation-django` | ready | `models-orm.md`, `services-selectors.md`, `migrations.md`, `transactions-performance-security.md` |
| `implementation-django-ninja` | provisional until dedicated source reference exists | `router-schema.md`, `auth-pagination-filtering.md`, `problem-details-openapi.md`, `testclient.md` |
| `implementation-django-web` | provisional until dedicated source reference exists | `templates.md`, `static-assets.md`, `templateview-htmx.md`, `csrf-ajax.md` |
| `implementation-python` | ready | `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md` |
| `implementation-cleancode` | ready | `responsibility.md`, `naming-functions.md`, `encapsulation-abstraction.md`, `legacy-review.md` |
| `implementation-tdd` | ready | `red-green-refactor.md`, `inside-out-outside-in.md`, `test-list.md`, `ai-assisted-tdd.md` |
| `implementation-test` | ready | `pytest-fixtures.md`, `test-doubles.md`, `factories-property-tests.md`, `coverage-mutation.md` |
| `workflow-dddjango-subagents` | ready | `delegation-rules.md`, `role-map.md`, `handoff-contract.md`, `integration-checklist.md` |

## 8. 금지 사항

- 스킬마다 README, 설치 가이드, changelog 같은 보조 문서를 늘리지 않는다.
- `SKILL.md`에 reference 전체 내용을 복사하지 않는다.
- 단순 CRUD에 DDD 구조를 강제하지 않는다.
- 실제로 실행하지 않은 검증을 완료했다고 기록하지 않는다.
