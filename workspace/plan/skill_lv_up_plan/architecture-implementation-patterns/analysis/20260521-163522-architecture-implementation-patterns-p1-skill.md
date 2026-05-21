수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
원인 분류: P1 reference 반영도 점검

# architecture-implementation-patterns P1 점검 결과

## 개선 대상 한 문장

`dddjango:architecture-implementation-patterns`는 DDD 모델이 어느 정도 정해진 뒤, Django-native 구조, layered/clean/hexagonal, ports/adapters, repository/UoW, CQRS, outbox, saga, ACL 중 가장 가벼운 구현 패턴과 handoff 경계를 선택하도록 돕는 skill이다.

## 기준 reference

- 전용 source reference인 `workspace/reference/architecture-implementation-patterns/reference/final.md`는 존재하지 않는다.
- fallback source evidence는 `workspace/reference/architecture-ddd/reference/final.md`, `workspace/reference/implementation-django/reference/final.md`, `workspace/reference/implementation-python/reference/final.md`, `workspace/reference/source-reference-audit/reference/final.md`이다.
- runtime evidence는 `dddjango/skills/architecture-implementation-patterns/SKILL.md`, `dddjango/skills/architecture-implementation-patterns/references/*.md`, `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`이다.

## reference 상태

`fallback/provisional 유지`.

전용 reference가 없으므로 dedicated implementation-patterns source가 충분하다고 말할 수는 없다. 다만 P1 종료 조건은 reference 상태를 `충분`, `개선 필요`, `fallback/provisional 유지` 중 하나로 확정하는 것이며, 현재 skill은 provisional 상태와 fallback 사용을 숨기지 않는다.

- `architecture-ddd/reference/final.md`: layered 구조, DIP, hexagonal/ports-adapters, CQRS, repository/UoW, event dispatch timing, outbox, saga, ACL의 DDD 관점 근거를 제공한다.
- `implementation-django/reference/final.md`: Django model methods, service/selectors, QuerySet, Django와 DDD trade-off, repository 도입 비용을 제공한다.
- `implementation-python/reference/final.md`: Protocol 기반 boundary와 repository/UoW가 전용 implementation-patterns source로 분리될 예정임을 제공한다.
- `source-reference-audit/reference/final.md`: source authoring path와 runtime-facing guidance의 경계, provisional/fallback evidence 구분 원칙을 제공한다.

## fallback/provisional 상태

현재 skill은 provisional 상태 자체를 명시하고, bundled reference도 dedicated implementation-patterns reference가 없다는 점을 반복해서 밝힌다. 이 점은 과장 없이 정직하다.

남은 문제는 runtime-facing `SKILL.md`가 fallback scope를 설명하면서 `workspace/reference/**` source-authoring path를 직접 나열한다는 점이다. source governance 기준상 runtime-facing guidance는 skill-local 또는 bundle-relative path를 사용해야 하고, `workspace/reference/**`는 source evidence나 authoring 맥락에 머물러야 한다.

## skill 반영도

핵심 패턴 선택 규칙은 대체로 반영되어 있다.

- strategy before structure: DDD 모델, aggregate, invariant, use case, integration boundary를 먼저 확인하라는 규칙이 있다.
- lightest pattern: Django-native model methods plus service/selectors를 기본 경로로 두고, repository/UoW, CQRS, outbox, saga, ACL을 조건부 도구로 둔다.
- dependency direction: domain/application을 infrastructure 세부사항에서 분리하고, adapters가 framework/SDK/ORM 세부사항을 담당하도록 한다.
- risky write: `Risky Write Consistency Block`으로 transaction owner, side-effect timing, uniqueness/idempotency storage, DB/API/test handoff를 남기도록 한다.
- honesty rule: 실제 실행하지 않은 test, validation, review, subagent 작업을 주장하지 말라는 규칙이 있다.

수정 필요 사항:

- `SKILL.md`의 source policy/fallback scope 문단에서 source-authoring path를 runtime-facing allowed reference처럼 보이게 하지 않도록 표현을 바꿔야 한다.
- fallback source 목록은 source evidence로 유지하되, runtime 실행 지시는 `references/pattern-selection.md`, `references/ports-adapters.md`, `references/repository-uow.md`, `references/outbox-acl.md` 같은 skill-local path 중심으로 정리해야 한다.
- `agents/openai.yaml`의 default prompt는 path leakage는 없지만, `fallback sources`가 무엇인지 runtime-facing 문맥에서 skill-local reference로 이어지도록 skill 본문과 맞춰야 한다.

## 책임 경계

handoff 조건은 대체로 충분하다.

- DDD model이 불명확하면 `architecture-ddd`로 넘긴다.
- table, locking, isolation, migration safety는 `architecture-db`로 넘긴다.
- REST contract, Problem Details, idempotency header, OpenAPI는 `architecture-api`로 넘긴다.
- Django model/service/migration/router/template/Python code 구현은 관련 implementation skill로 넘긴다.
- coordinated work나 subagent 요청은 `workflow-dddjango-subagents`로 넘긴다.

다만 source/path-boundary cleanup을 할 때, `architecture-implementation-patterns`가 concrete DB/API/test detail을 소유하는 것처럼 보이지 않게 현재 handoff 문구를 유지해야 한다.

## eval 점검 필요 여부

현재 P1 범위에서는 eval 수정 후보를 확정하지 않는다. 다만 P2에서 skill 문구를 고친 뒤에는 runtime/source boundary를 검증하는 source 또는 plugin bucket case가 이미 충분한지 확인할 필요가 있다.

## Subagent 리뷰/순차 fallback

real-subagent를 실행했다. Subagent는 `skill-creator` 관점에서 `SKILL.md` 목적 명확성, trigger description, progressive disclosure, reference 중복/누락, validation integrity를 점검했고, 파일 수정은 하지 않았다.

Subagent 원결과:

- Blocker 0, Major 1, 열린 Minor 1.
- Major: 전용 source reference 부재로 follow-up reference analysis가 필요하다는 의견.
- Minor: frontmatter의 `service layer`, `구현 구조`, `아키텍처 패턴`, `프로젝트 구조` trigger가 넓어 false-positive 가능성이 있다는 의견.
- 원본 subagent 실행 로그는 저장소 파일로 별도 보존하지 않았다. 이 P1 분석 문서에는 원결과 요약과 통합 판단만 남긴다.

추가 검증:

- 2026-05-21에 같은 파일 범위를 독립 subagent로 재검토했다.
- 추가 subagent 원결과: Blocker 0, Major 0, Minor 1.
- 추가 Minor: 기존 subagent/`skill-creator` 리뷰 실행 주장이 원본 artifact path 없이 요약만 남아 있어 검증 무결성 관점에서 `raw artifact path`, prompt/output 위치, 또는 `not retained` 명시가 있으면 더 좋다는 의견.
- 통합 조치: 위 `not retained` 명시를 추가했으므로 열린 Minor로 유지하지 않는다.

통합 판단:

- 전용 source reference 부재는 현재 P1 prompt와 source policy가 허용한 `fallback/provisional 유지` 상태로 분류한다. 전용 reference 작성은 별도 reference 개선 후보로 확정하지 않는다.
- 넓은 trigger 가능성은 현재 description 안에 coordinated work, DDD/DB/API/implementation handoff와 simple CRUD 제외 조건이 함께 있어 P1 결론을 왜곡하지 않는다. 실제 오트리거 evidence가 나오면 skill 개선 계획에서 보조 점검 항목으로 다룬다.
- 추가 subagent의 auditability Minor는 원본 subagent 로그를 repo artifact로 보존하지 않았다는 사실을 명시해 해소한다.
- 따라서 subagent들의 Major/Minor는 열린 항목으로 유지하지 않고 Note 또는 다음 단계의 보조 확인으로 내린다.

## skill-creator 리뷰

real-subagent로 수행했다. `skill-creator` 기준상 목적과 progressive disclosure는 대체로 적절하나, runtime-facing `SKILL.md`에서 source-authoring path를 직접 노출하는 표현은 skill 개선 계획에서 정리해야 한다.

## 후속 분석 문서 위치

현재 문서:

`workspace/plan/skill_lv_up_plan/architecture-implementation-patterns/analysis/20260521-163522-architecture-implementation-patterns-p1-skill.md`

## 다음 단계

`skill 개선 계획`.

P1에서는 skill, reference, eval을 바로 수정하지 않는다. 다음 단계에서 같은 대상의 `plan/` 아래에 개선 계획을 작성한 뒤, `SKILL.md`의 runtime-facing source/path-boundary wording을 좁게 수정한다.

## 산출 형식 요약

```text
수정 대상 후보: skill
기준 reference: architecture-ddd final, implementation-django final, implementation-python final, source-reference-audit final
reference 상태: fallback/provisional 유지
fallback/provisional 상태: 전용 architecture-implementation-patterns source reference 없음, fallback source 사용 고지 필요
skill 반영도: 핵심 패턴 선택, lightest pattern, dependency direction, risky write handoff는 반영됨. runtime-facing source path wording은 개선 필요
책임 경계: DDD/DB/API/Django implementation/workflow handoff는 대체로 충분함
eval 점검 필요 여부: P1에서는 확정하지 않음. P2 이후 runtime/source boundary 평가 coverage 확인 필요
후속 분석 문서 위치: workspace/plan/skill_lv_up_plan/architecture-implementation-patterns/analysis/20260521-163522-architecture-implementation-patterns-p1-skill.md
다음 단계: skill 개선 계획
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
Subagent 리뷰/순차 fallback: real-subagent 실행, 원결과 Major 1/Minor 1은 통합 판단에서 Note/다음 단계로 정리
skill-creator 리뷰: real-subagent 수행. 원본 실행 로그는 repo artifact로 보존하지 않았고, 2026-05-21 추가 독립 subagent 재검토에서 artifact 미보존 사실 명시 필요 Minor를 확인해 본문에 반영함
통합 리뷰 결과: 수정 대상 후보 skill, reference 상태 fallback/provisional 유지, 열린 Blocker/Major/Minor 없음
종료 조건 충족 여부: 충족
검증/미검증: validate_plan_constraints.py 및 test_validate_plan_constraints.py 통과. skill docs validator, eval validator, runtime cache sync는 P1 범위에서 미실행
```

## 리뷰 결과

- Blocker: 0개
- Major: 0개
- 열린 Minor: 0개
- Note: dedicated source reference 부재는 현재 `fallback/provisional 유지`로 분류한다.
- Note: broad trigger 가능성은 실제 오트리거 evidence가 확인되면 skill 개선 계획에서 함께 점검한다.
- Note: subagent 원본 실행 로그는 repo artifact로 보존하지 않았고, 분석 문서에는 원결과 요약과 통합 판단만 남긴다.

## 종료 조건 충족 여부

- 기준 reference 상태: `fallback/provisional 유지`로 확정.
- 수정 대상 후보: `skill`.
- Blocker/Major: 0개.
- 열린 Minor: 0개.
- Subagent 리뷰: real-subagent 실행.
- skill-creator 리뷰: real-subagent 실행.
- 다음 단계: `skill 개선 계획`.
- 후속 분석 문서: 작성 완료.
- P1에서 개선 계획 문서, skill 수정, reference 수정, eval 수정은 하지 않음.
- 실제로 실행하지 않은 검증, 리뷰, subagent 작업을 수행한 것처럼 쓰지 않음.

## 검증/미검증

- 검증 완료: `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- 검증 완료: `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- 미검증: skill docs validator, eval validator, runtime cache sync. P1 범위에서는 실행하지 않았다.

## Serena

Serena: skipped because this P1 work was document/source-boundary analysis without symbol tracing; verified with scoped file reads and `rg`.
