# workflow try02 sequential-fallback-mode Plan

## Scope

- Change type: `skill`
- Target files:
  - `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
  - `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- Expected behavior after change:
  - For sequential fallback workflow answers, especially when the user says to assume subagents cannot run, the final answer visibly states that real subagents were not executed and that the workflow is being handled as sequential fallback.
  - The canonical order remains Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration.
  - Direct answer mode and explicit opt-out cases remain compact and do not gain workflow sections.

## Steps

- [x] Inspect current `workflow-dddjango-subagents` instructions and identify the narrowest location for the fallback-honesty requirement.
- [x] Add a concise instruction to `SKILL.md` requiring an explicit non-execution/fallback statement for sequential fallback workflow output.
- [x] Add the same rule to `references/delegation-rules.md` so the detailed delegation reference matches the runtime skill.
- [x] Keep the rule scoped to workflow/sequential fallback mode so pure direct answers and explicit opt-out cases are not polluted with meta tails.
- [x] Run deterministic validation.
- [x] Run a targeted workflow eval for `case-workflow-sequential-fallback`.
- [x] Refresh latest reports.
- [x] Review whether the hard gate is cleared without degrading direct-answer restraint cases.

## Verification Commands

```bash
.venv/bin/python -m unittest discover -s workspace/scripts -p 'test_*.py'
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
make eval-one BUCKET=workflow CASE=case-workflow-sequential-fallback EXTRA_ARGS=--rerun
.venv/bin/python workspace/scripts/render_eval_review_html.py --refresh-latest
```

## Follow-up Candidates

- `runtime/report gap`: workflow report conclusion currently says `12 pass, 0 partial, 0 fail` even when `blocked=1` and hard-gate failures are present.
- `eval gap`: `case-workflow-parallel-ownership` should be reviewed for acceptable mode consistency when actual subagents are unavailable.
- `eval quality`: source bucket needs seeded conflict/provenance fixtures before source quality can be considered decision-grade.
