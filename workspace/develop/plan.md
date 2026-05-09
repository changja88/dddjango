# dddjango Plugin Development Plan

이 문서는 `dddjango` 플러그인을 실제 스킬 묶음으로 개발하기 위한 실행 계획이다. 기준 문서는 `workspace/docs`이고, source reference corpus는 `workspace/reference`이다.

개발 산출물은 기본적으로 workspace 안에 둔다. 플러그인 런타임이 요구하는 경우에만 repo root의 `dddjango/` 또는 설치된 plugin cache를 다룬다.

## 1. 플러그인 골격 확정

목적:

- 실제 생성할 플러그인 파일 구조를 고정한다.
- 문서 기준과 runtime skill 구조가 어긋나지 않게 한다.

산출물:

- `dddjango/.codex-plugin/plugin.json`
- `dddjango/skills/<skill>/SKILL.md`
- `dddjango/skills/<skill>/agents/openai.yaml`
- `dddjango/skills/<skill>/references/*.md`

기준 문서:

- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-authoring.md`

통과 기준:

- 모든 스킬 이름과 위치가 `plugin-structure.md`와 일치한다.
- `implementation-*` 스킬이 바닥 스킬이라는 위계가 유지된다.
- 전용 source reference가 부족한 스킬은 완성본처럼 표시하지 않는다.

## 2. 개별 스킬 평가표 작성

목적:

- 각 스킬을 구현하기 전에 독립 평가 기준을 먼저 고정한다.
- trigger, routing, reference 반영, 금지 행동을 스킬별로 검증 가능하게 만든다.

산출물:

- 개별 스킬별 평가표
- positive prompt
- negative prompt
- expected routing
- required reference coverage
- failure criteria

대상 스킬:

- `implementation-django`
- `implementation-django-ninja`
- `implementation-django-web`
- `implementation-python`
- `implementation-cleancode`
- `implementation-tdd`
- `implementation-test`
- `architecture-ddd`
- `architecture-implementation-patterns`
- `architecture-db`
- `architecture-api`

통과 기준:

- 각 평가표가 해당 스킬 단독 책임을 검증한다.
- 다른 스킬을 호출해야 하는 상황과 호출하지 않아야 하는 상황을 구분한다.
- 단순 작업에 DDD나 subagent workflow를 과하게 적용하지 않는 negative case가 포함된다.
- provisional 스킬의 평가표는 fallback source와 한계를 명시한다.

## 3. 개별 스킬 구현

목적:

- 각 스킬을 독립적으로 사용할 수 있는 최소 runtime 단위로 구현한다.
- `SKILL.md`는 짧게 유지하고 세부 판단 기준은 `references/`로 분리한다.

구현 순서:

1. `implementation-*` 바닥 스킬
2. `architecture-*` 상위 판단 스킬
3. provisional 스킬 보강 또는 provisional 표시

산출물:

- 각 스킬의 `SKILL.md`
- 각 스킬의 `references/*.md`
- 각 스킬의 `agents/openai.yaml`

작성 기준:

- frontmatter에는 `name`과 `description`만 둔다.
- `description`에는 trigger와 routing 기준을 충분히 포함한다.
- 본문에는 핵심 절차, reference 읽기 기준, 경계와 금지 사항만 둔다.
- 긴 설명, 비교, 예시는 `references/`로 분리한다.
- skill 내부에 README, installation guide, changelog를 만들지 않는다.

통과 기준:

- `SKILL.md`에서 모든 runtime reference가 직접 링크된다.
- `agents/openai.yaml`이 `SKILL.md`와 의미적으로 일치한다.
- `implementation-*` 스킬이 상위 workflow 없이도 단순 작업을 처리할 수 있다.

## 4. 개별 스킬 평가 및 개선 반복

목적:

- 개별 스킬이 평가표 기준을 통과할 때까지 구현을 개선한다.

반복 절차:

1. 구조 검증을 실행한다.
2. 개별 평가 prompt를 실행한다.
3. 실패 원인을 분류한다.
4. `description`, 본문, reference, 평가표 중 수정 대상을 정한다.
5. 수정 후 같은 평가를 다시 실행한다.

검증 명령:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase generated --skills-dir dddjango/skills
```

통과 기준:

- 개별 평가표의 필수 항목을 충족한다.
- negative prompt에서 과한 skill routing이 발생하지 않는다.
- 실행하지 않은 테스트나 검증을 완료했다고 말하지 않는다.
- 실패가 발생하면 원인과 수정 위치가 기록된다.

## 5. 스킬 연계 평가표 작성

목적:

- 상위 스킬이 여러 하위 스킬을 조합하는 동작을 평가한다.
- DDD 구현 흐름이 실제 개발 작업에서 유지되는지 확인한다.

산출물:

- 연계 평가표
- 역할별 handoff 기대 산출물
- sequential fallback 기준
- integration checklist 기준

대표 흐름:

- DDD 설계에서 Django 구현까지
- Django Ninja API 설계와 구현
- DB schema, transaction, migration 연계
- TDD와 pytest 구현 연계
- 단순 작업에서 workflow를 생략하는 negative routing

통과 기준:

- 복합 작업에서는 `Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`가 유지된다.
- 역할별 책임과 관련 skill 구성이 `workspace/docs/workflow.md`와 일치한다.
- Django template/static/web 책임이 있으면 `implementation-django-web`이 누락되지 않는다.
- 연계 평가가 개별 스킬 평가와 중복되지 않고 조합 실패를 잡는다.

## 6. 스킬 연계용 스킬 구현

목적:

- 여러 하위 스킬을 조합하는 workflow skill을 구현한다.
- subagent 사용 가능 여부와 무관하게 같은 기준으로 작업을 진행할 수 있게 한다.

대상 스킬:

- `workflow-dddjango-subagents`

산출물:

- `workflow-dddjango-subagents/SKILL.md`
- `workflow-dddjango-subagents/references/delegation-rules.md`
- `workflow-dddjango-subagents/references/role-map.md`
- `workflow-dddjango-subagents/references/handoff-contract.md`
- `workflow-dddjango-subagents/references/integration-checklist.md`
- `workflow-dddjango-subagents/agents/openai.yaml`

통과 기준:

- subagent를 실제로 사용하지 않았다면 사용했다고 주장하지 않는다.
- subagent를 사용할 수 없을 때 sequential fallback을 제공한다.
- 역할 분해가 DDD, DB, API, Django, Test, Review 책임을 축소하지 않는다.
- cache를 수정한 경우 workspace canonical source와 대응 관계를 보고하도록 한다.

## 7. 스킬 연계 평가 및 개선 반복

목적:

- 개별 스킬은 통과하지만 조합에서 실패하는 문제를 찾아 개선한다.

반복 절차:

1. 연계 평가 prompt를 실행한다.
2. role map과 handoff 산출물을 확인한다.
3. 하위 스킬 reference가 필요한 시점에만 읽히는지 확인한다.
4. 과한 구조 적용이나 역할 누락을 수정한다.
5. 같은 평가를 다시 실행한다.

검증 기준:

- `workspace/docs/validation-plan.md`
- `workspace/docs/workflow.md`

통과 기준:

- 복합 작업에서 DDD 판단이 구현보다 먼저 나온다.
- Django Ninja가 API 구현 표준으로 유지된다.
- DB transaction, constraint, migration 책임이 구현 책임과 구분된다.
- 테스트가 도메인 규칙과 API 계약을 보호한다.
- 단순 prompt에서는 workflow를 출력하지 않는다.

## 8. 종합 평가표 작성

목적:

- 플러그인 전체가 하나의 제품처럼 동작하는지 평가한다.

산출물:

- 종합 평가표
- install/discovery 검증 항목
- Claude Code와 Codex 공통성 검증 항목
- runtime cache 동기화 검증 항목
- 전체 eval prompt 묶음

평가 항목:

- 플러그인 구조
- 스킬 발견과 trigger
- 스킬 위계
- reference 반영
- DDD 구현 일관성
- Django Ninja 표준
- 과적용 방지
- 검증 정직성
- runtime cache와 workspace source 동기화

통과 기준:

- 모든 스킬이 발견 가능한 구조로 생성된다.
- `agents/openai.yaml`이 모든 스킬에 존재하고 `SKILL.md`와 일치한다.
- `workspace/docs`와 runtime skill 구조가 충돌하지 않는다.
- cache-only 변경이 완료 상태로 남지 않는다.

## 9. 종합 플러그인 평가 및 개선

목적:

- 실제 사용 가능한 플러그인 상태까지 검증하고 반복 개선한다.

반복 절차:

1. 전체 구조 검증을 실행한다.
2. 개별 평가표를 실행한다.
3. 연계 평가표를 실행한다.
4. 종합 평가표를 실행한다.
5. 실패를 skill trigger, instruction, reference, workflow, eval 문제로 분류한다.
6. 수정 후 전체 검증을 다시 실행한다.

완료 게이트:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

완료 기준:

- docs phase가 통과한다.
- generated/all phase가 실제 `dddjango/skills`를 대상으로 통과한다.
- runtime smoke만으로 완료 처리하지 않는다.
- 평가 실패가 남아 있으면 실패 항목과 다음 수정 계획을 명시한다.

## 개발 원칙

- 평가표를 먼저 만들고 스킬을 구현한다.
- 스킬은 간결하게 만들고 reference는 필요할 때만 읽히게 한다.
- 구현은 바닥 스킬에서 시작해 상위 workflow로 올라간다.
- 검증은 prompt, 산출물, diff, 로그, 리뷰 findings 같은 raw artifact를 기준으로 한다.
- subagent 검증은 가능한 경우 forward-test로 사용하되, 정답이나 의도한 수정 방향을 노출하지 않는다.
- 실제로 실행하지 않은 검증, 테스트, subagent 리뷰를 완료했다고 말하지 않는다.
