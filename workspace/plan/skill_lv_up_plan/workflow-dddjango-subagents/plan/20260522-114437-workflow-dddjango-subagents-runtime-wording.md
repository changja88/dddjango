수정 대상: skill

# workflow runtime wording P4 계획

## 수정 순서

1. `dddjango/skills/workflow-dddjango-subagents/SKILL.md`에서 내부 평가 용어와 구체 plan-path instruction을 product-facing follow-up wording으로 바꾼다.
2. `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`도 같은 방식으로 정리한다.
3. Runtime skill docs validator를 실행한다.
4. 관련 eval bucket validator를 재실행해 public/answer 구조가 유지되는지 확인한다.

## 완료 조건

- Runtime-facing workflow docs가 내부 oracle/evaluator/model-variance/path wording을 노출하지 않는다.
- Source/reference governance handoff와 validation honesty rule은 유지된다.
