# Integration Checklist

Composite dddjango work를 마무리하기 전에 읽는다.

## Integration Priority

충돌은 다음 순서로 해결한다.

1. Domain invariants
2. Data consistency
3. Transactions and security
4. API contract and backward compatibility
5. Testability
6. Django/Python idioms
7. Names and style

## Checklist

- Domain and invariants: domain invariant, state transition, ubiquitous language가 implementation, tests, API와 충돌하지 않는다.
- Data and transaction: DB constraints, transaction boundary, locking/idempotency, migration rollout risk가 처리됐거나 owning role에 배정됐다.
- API contract: Django Ninja Router/Schema mapping, status codes, Problem Details, OpenAPI impact, no greenfield DRF implementation 여부를 확인했다.
- Implementation mapping: domain logic이 Router, view, schema, template에 소유되지 않고 Django service/selector/model boundary가 명확하다.
- Tests and verification: domain rules, API contract, migration risk에 test 또는 explicit not-run verification note가 연결된다.
- Integration owner: Coordinator 또는 named owner가 role results 수집, conflict resolution, follow-up closure를 책임진다.
- Role handoff closure: 각 role의 `Risks`와 `Required Follow-up`이 closed 또는 unresolved로 명시됐다.
- Source/runtime boundary: Runtime-facing guidance는 skill-local `references/*.md`를 사용하고 source authoring path를 allowed runtime reference처럼 제시하지 않는다.
- Eval follow-up: eval case, answer oracle, evaluator, report, model variance 문제가 발견되면 P1에서 직접 수정하지 않는다. `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`에 후속 분석으로 분류하고 첫 줄은 `수정 대상: case`, `수정 대상: answer`, `수정 대상: evaluator`, `수정 대상: report`, `수정 대상: model-variance` 중 하나를 사용한다.
- Cache sync report: plugin cache outside workspace를 수정했다면 cache path, matching workspace canonical source, validation status를 보고한다. `workflow-dddjango-subagents` role-map 변경 시 `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`를 parity source로 사용해 runtime/cache role names, responsibility scope, related skills가 축소되지 않았는지 확인한다.

## Risky Write Consistency Block

Order, payment, inventory, reservation, refund, permission, ledger 같은 risky writes가 있으면 관련 role이 다음을 제공하는지 확인한다.

- transaction owner
- locking strategy
- uniqueness or idempotency storage location
- `Idempotency-Key` API behavior
- external side-effect timing such as Django `transaction.on_commit()` or domain event handling
- isolation/retry decision
- integration or concurrency test criteria

현재 role에서 결정할 수 없는 항목은 생략하지 말고 responsible role에 배정한다.

## Runtime Cache Sync

Source skill과 runtime cache가 다르면 `workspace/plan/skill_lv_up_plan/workflow-dddjango-subagents/analysis/`에 첫 줄 `수정 대상: runtime-sync` 분석을 작성하고, 같은 timestamp 파일명으로 `workspace/plan/skill_lv_up_plan/workflow-dddjango-subagents/plan/`에 matching plan을 작성한 뒤 sync한다. Sync 후에는 `SKILL.md`, `references/*.md`, `agents/openai.yaml` parity를 실제 diff 또는 validator로 확인한다.

## Validation Honesty

실행한 validation과 planned 또는 recommended validation을 분리해서 보고한다. Tests, review, browser checks, subagent work, eval, Serena를 실제로 실행하지 않았다면 완료됐다고 쓰지 않는다.
