# Phase Status

This is the only top-level progress board for the Codex-only dddjango rebuild.
Do not infer phase completion from scattered chat logs, reports, or review
files.

| phase | status | owner mode | allowed edits | current gate | last evidence | open blocker | provisional items | next action |
|---|---|---|---|---|---|---|---|---|
| p0-inventory | complete | manual | inventory only | `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md` exists and is indexed | `workspace/plan/phases/p0-inventory/evidence/20260522-223642-p0-plugin-inventory-freeze-inventory.md` | - | 6 provisional source relationships; component absences recorded as missing; `plugin.json` explicit local/private flag unknown | proceed to P1 reference sufficiency |
| p1-reference-sufficiency | complete | manual/goal | reference analysis and source-only fixes | all references classified | `workspace/plan/phases/p1-reference-sufficiency/evidence/20260522-225558-p1-reference-sufficiency-audit-evidence.md` | - | 3 provisional references: `implementation-tdd`, `source-reference-audit`, `workflow-dddjango-subagents`; not P5/P6/P8 completion evidence | proceed to P1.5 usage cards |
| p1-5-usage-cards | complete | manual | usage cards only | high-risk trigger cards exist | `workspace/plan/phases/p1-5-usage-cards/evidence/20260522-230605-p1-5-skill-usage-cards-evidence.md` | - | P1 provisional restrictions carry forward for `implementation-tdd`, `source-reference-audit`, `workflow-dddjango-subagents` | proceed to P2 skill structure |
| p2-skill-structure | complete | goal | skill structure/trigger only | skill validators and trigger boundaries pass | `workspace/plan/phases/p2-skill-structure/evidence/20260522-232040-p2-skill-structure-trigger-boundary-evidence.md` | - | P1 provisional restrictions carry forward for `implementation-tdd`, `source-reference-audit`, `workflow-dddjango-subagents`; upstream validators require PyYAML so local equivalent was used | proceed to P3 forward tests |
| p3-forward-tests | infrastructure-blocked | goal | forward-test prompts/evidence and narrow fixes | P3a prompt matrix current; P3b isolated user-like runtime tests pass before P7/P8 | `workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-evidence.md` | P3b external Codex/OpenAI runtime remains tenant-policy blocked; local Ollama and LM Studio providers unavailable | P3a prompt matrix fixed for 13 trigger families; P3b has no loaded-skill/final-answer evidence; P4 may start only under `ADR-0004` and remains runtime-routing provisional | proceed to P4 eval skeleton under `ADR-0004`; resolve P3b before P7/P8 completion |
| p4-eval-skeleton | complete | goal | eval protocol, fixture runner, report validator | mini-bucket fixtures pass/fail correctly | `workspace/plan/phases/p4-eval-skeleton/evidence/20260523-001811-p4-eval-mini-bucket-skeleton-evidence.md` | - | runtime-routing evidence deferred by `ADR-0004`; P7/P8 still require P3b or equivalent installed-runtime user-like evidence | proceed to P4.5 runtime parity; do not treat P4 as installed runtime routing proof |
| p4-5-runtime-parity | complete | goal | install/cache parity evidence and narrow fixes | source/cache/discovery evidence current | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-evidence.md` | - | P4.5 proves source/cache/install/discovery parity only; P3b runtime-routing evidence remains deferred by `ADR-0004` | proceed to model-backed P5 individual eval; do not treat P4.5 as P3b runtime-routing proof |
| p5-individual-eval | infrastructure-blocked | goal | individual skill eval only | affected bucket clean and scored | `workspace/plan/phases/p5-individual-eval/evidence/20260523-003507-p5-eval-individual-skill-fixture-preflight-evidence.md` | model-backed installed-runtime P5 has not run yet | fixture-scored P5 preflight bucket is clean/scored but `model_backed=false`; not integration evidence and not P5 completion proof | run model-backed P5 individual eval |
| p6-integration-eval | not-started | goal | integration eval only | affected bucket clean and scored | - | - | - | wait for P5 |
| p7-install-packaging | not-started | goal | install/package evidence and narrow fixes | installed runtime user-like tasks pass and P3b deferral resolved | - | - | P3b runtime evidence still blocked | wait for P6 and an approved runtime channel |
| p8-full-regression | not-started | goal | final full regression and classification | full run pass, not scored 0, leakage 0, P3b/equivalent runtime evidence current | - | - | P3b runtime evidence still blocked | wait for P7 and P3b resolution |

Allowed status values:

- `not-started`
- `active`
- `blocked`
- `infrastructure-blocked`
- `complete`
- `superseded`
