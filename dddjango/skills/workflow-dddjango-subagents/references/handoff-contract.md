# Handoff Contract

Role work를 배정하거나 role output을 통합할 때 읽는다.

각 role handoff는 다음 field를 포함한다.

- `Scope`
- `Inputs Used`
- `Decisions`
- `Files`
- `Output`
- `Risks`
- `Required Follow-up`
- `dddjango Checks`

`Files`에는 반드시 다음을 포함한다.

- `May edit`
- `Must not edit`

## Field Meanings

- `Scope`: 이 role이 이번 task에서 책임지는 범위.
- `Inputs Used`: role이 읽은 docs, source files, user constraints, existing code, prior role outputs.
- `Decisions`: 내린 결정과 의도적으로 미룬 결정.
- `Files`: ownership과 edit limits.
- `Output`: expected artifact, patch, plan, review findings, test criteria.
- `Risks`: unresolved correctness, migration, compatibility, verification risks.
- `Required Follow-up`: 다음 role 또는 integrator가 닫아야 할 질문이나 check.
- `dddjango Checks`: 적용해야 할 domain, DB, API, Django, test, review standards.

## Handoff Discipline

- Parallel work 전에 ownership을 명시한다.
- Approval-before-execution planning에서도 proposed handoff를 작성한다. `pending approval`, `not executed`, `read-only`, `unknown until code inspection`을 사용할 수 있지만 required field는 생략하지 않는다.
- 같은 file 또는 module을 여러 subagent에게 write scope로 주지 않는다.
- Parallel `May edit` scopes는 concrete file path 또는 module owner 기준으로 disjoint해야 한다.
- 두 role이 같은 파일을 필요로 하면 한 role만 write owner로 지정하고 다른 role은 read-only review 또는 advisory로 둔다.
- Review-only role은 file을 수정하지 않는다고 적는다.
- Earlier decision에 의존하는 role은 그 의존성을 `Required Follow-up`에 적는다.
- Integration 단계에서 각 risk를 close하거나 unresolved로 carry forward한다.
