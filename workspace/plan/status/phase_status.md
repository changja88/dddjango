# Phase Status

This is the only top-level progress board for the Codex-only dddjango rebuild.
Do not infer phase completion from scattered chat logs, reports, or review
files.

| phase | status | owner mode | allowed edits | current gate | last evidence | open blocker | provisional items | next action |
|---|---|---|---|---|---|---|---|---|
| p0-inventory | complete | manual | inventory only | `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md` exists and is indexed | `workspace/plan/phases/p0-inventory/evidence/20260522-223642-p0-plugin-inventory-freeze-inventory.md` | - | 6 provisional source relationships; component absences recorded as missing; `plugin.json` explicit local/private flag unknown | proceed to P1 reference sufficiency |
| p1-reference-sufficiency | not-started | manual/goal | reference analysis and source-only fixes | all references classified | - | - | - | wait for P0 |
| p1-5-usage-cards | not-started | manual | usage cards only | high-risk trigger cards exist | - | - | - | wait for P1 |
| p2-skill-structure | not-started | goal | skill structure/trigger only | skill validators and trigger boundaries pass | - | - | - | wait for P1.5 |
| p3-forward-tests | not-started | goal | forward-test prompts/evidence and narrow fixes | isolated user-like tests pass | - | - | - | wait for P2 |
| p4-eval-skeleton | not-started | goal | eval protocol, fixture runner, report validator | mini-bucket fixtures pass/fail correctly | - | - | - | wait for P3 |
| p4-5-runtime-parity | not-started | goal | install/cache parity evidence and narrow fixes | source/cache/discovery evidence current | - | - | - | wait for P4 |
| p5-individual-eval | not-started | goal | individual skill eval only | affected bucket clean and scored | - | - | - | wait for P4.5 |
| p6-integration-eval | not-started | goal | integration eval only | affected bucket clean and scored | - | - | - | wait for P5 |
| p7-install-packaging | not-started | goal | install/package evidence and narrow fixes | installed runtime user-like tasks pass | - | - | - | wait for P6 |
| p8-full-regression | not-started | goal | final full regression and classification | full run pass, not scored 0, leakage 0 | - | - | - | wait for P7 |

Allowed status values:

- `not-started`
- `active`
- `blocked`
- `infrastructure-blocked`
- `complete`
- `superseded`
