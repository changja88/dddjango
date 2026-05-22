# Source Eval Goal

## Goal

`source` 평가는 `workspace/reference`, runtime bundled references, eval source basis가 `dddjango` plugin의 판단 근거로 충분하고 추적 가능하며 서로 충돌하지 않는지 평가한다.

핵심 목표는 reference corpus 전체가 skill, eval case, answer oracle, runtime reference split의 source of truth로 작동하는지 확인하는 것이다.

## Reference Basis

평가 대상 source는 다음 전체 집합이다.

- `workspace/reference/spec.md`
- `workspace/reference/source-reference-audit/reference/final.md`
- `workspace/reference/architecture-ddd/reference/final.md`
- `dddjango/skills/source-reference-audit/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
- `workspace/develop/eval`
- `dddjango/.codex-plugin/plugin.json`
- `workspace/reference/*/reference/final.md`
- `workspace/reference/*/reference/internal.md`
- `workspace/reference/*/reference/external.md`
- `workspace/reference/*/reference/review.md`
- `dddjango/skills/*/references/*.md`

## Case Families

- Source coherence: product goal, skill list, skill contracts, workflow, validation rules, plugin manifest, and authoring inputs point to the same decisions.
- Reference provenance: every runtime bundled reference traces to the appropriate `workspace/reference/<area>/reference/final.md` or explicitly documented fallback source.
- Conflict and gap handling: `review.md` conflicts, decisions, gaps are either resolved in docs or explicitly marked as out of scope/provisional.
- Provisional source handling: implementation patterns, Django Ninja, Django Web are not treated as dedicated-source-complete unless `final.md` exists and substantively covers the skill's main decisions.
- DRF guardrail: DRF content is not used as greenfield API implementation standard; Django Ninja remains the default new API implementation target.
- Runtime metadata/cache sync: `SKILL.md`, `agents/openai.yaml`, bundled references, validation output, and source/runtime cache parity are checked as semantic evidence, not file-existence smoke.
- Validation coverage: validation scenarios cover DDD, DB, API, Django, Ninja, Web, Python, TDD, Test, Clean Code, workflow, negative cases, validation honesty.
- Eval traceability: each eval bucket's `cases/plugin/public` and `answer` can trace required observations back to source references.
- Boundary protection: public case, answer oracle, runtime skill source, prior run artifact, and workspace source reference stay in separate roles.
- Source-audit routing restraint: application design, Django implementation, test mechanics, or workflow execution requests are routed to owning skills instead of being forced through source-reference-audit ceremony.

## Minimum Coverage

완성된 source eval pack은 source coherence, source provenance, conflict/gap decision, provisional handling, DRF guardrail, runtime metadata/cache sync, validation coverage, eval traceability, boundary protection, source-audit exclusion/routing restraint를 각각 최소 하나 이상의 case로 덮어야 한다. seeded conflict나 missing provenance fixture를 포함해 사람이 대충 읽고 통과시키는 audit을 방지한다.

Crosswalk는 모든 first-class dimensions를 per-skill로 확인한다: DDD, implementation patterns, DB, API, Django, Django Ninja, Django Web, Python, Clean Code, TDD, Test, Workflow. `final.md`가 모호하거나 source gap/review conflict가 걸린 경우 `internal.md`, `external.md`, `review.md`를 consulted evidence로 남긴다.

Validation coverage는 운영 마이그레이션, 동시성, Django Web, Python typing, architecture-pattern selection, false-subagent negative case까지 포함해야 한다. DRF guardrail은 별도 항목으로 두어, DRF가 legacy/migration/comparison이고 greenfield API standard는 Django Ninja임을 검증한다.

## Answer Oracle

각 source case는 `answer/case-*.yaml`에 evaluator-only oracle을 둔다.

`answer`는 최소한 다음을 담는다.

- source files that must be consulted
- expected decision or conflict resolution
- required runtime reference trace
- gap/provisional status
- allowed and forbidden claims
- required validation command or manual evidence
- leakage checks for public case/runtime skill boundaries
- hard gates for evaluator leakage, source/runtime contamination, unsupported validation claims, and unsupported subagent claims
- `control_case` label when safety, honesty, or restraint behavior makes baseline pass acceptable
- `expected_outcomes` for baseline, `with_dddjango`, expected delta, and whether baseline pass is acceptable

## Evidence To Capture

- source inventory
- source-to-skill-to-runtime-reference crosswalk
- conflict/gap/provisional ledger
- validation scenario coverage map
- skill/reference validation command output
- public/answer/runtime boundary check

## Non-Goals

- source 문서를 runtime skill에 그대로 복사해 context를 낭비하지 않는다.
- private `answer/` oracle을 public case나 skill instructions에 넣지 않는다.
- 전용 source가 없는 skill을 완성된 reference 기반 skill처럼 표시하지 않는다.

## Completion Gate

Source eval은 `workspace/develop/eval/source/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 존재할 때만 완료 후보가 된다.

`python3 workspace/scripts/validate_skill_docs.py --phase generated`를 통과해야 한다. 추가로 사람이 읽을 수 있는 crosswalk가 source provenance, conflict/gap decision, provisional handling, DRF guardrail, validation coverage, eval bucket traceability를 실제로 덮어야 한다.

완료 판정은 source 문서 존재만으로 하지 않는다. 현재 runner가 source bucket을 first-class로 실행하지 못하면 dedicated source validator/runner를 추가하거나 `cases`, `answer`, `fixtures`, `runs`를 실제로 소비하는 manual run protocol을 남겨야 한다. `answer/` oracle이 reference 전체 집합과 runtime bundled references 사이의 추적성, 충돌 처리, leakage 방지를 확인하고 그 결과가 `runs/<run-id>/analysis/` 또는 동등한 평가 산출물에 남아야 통과다.
