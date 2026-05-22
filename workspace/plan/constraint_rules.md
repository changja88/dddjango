# Plan Constraint Rules

These rules apply to rebuild-related document and planning edits under
`workspace/plan/**`, `workspace/reference/**`, `workspace/develop/eval/**`, and
`dddjango/skills/**` during the dddjango Codex plugin rebuild.

## Scope

- Use this directory for planning, analysis, review, evidence, phase status,
  goal prompts, and decision records.
- Do not put process records inside `dddjango/skills/**`.
- Do not use files in this directory as runtime bundled references.
- Do not treat this directory as plugin source or installed runtime evidence.
- For `workspace/reference/**`, keep source evidence and provenance records
  there, but track the work item and closure in `workspace/plan/**`.
- For `workspace/develop/eval/**`, keep eval cases, answers, fixtures, runner,
  and report code there, but track the analysis, plan, evidence, and closure in
  `workspace/plan/**`.
- For `dddjango/skills/**`, keep runtime skill instructions/resources there, but
  do not add rebuild logs, changelogs, planning notes, or review summaries.

## Required Links

Every non-index work item in the rebuild must be traceable through these
records:

- `indexes/artifact_index.md`
- `indexes/evidence_index.md` when it claims verification
- `indexes/review_index.md` when it cites review
- `indexes/goal_index.md` when it was run as a goal
- `status/phase_status.md` when it changes phase state

## File Rules

- Existing review artifacts created before this file may keep their original
  filenames if they are listed in an index as bootstrap or pre-convention
  artifacts. New files must follow the canonical grammar.
- Use lowercase ASCII kebab-case filenames.
- Use Asia/Seoul timestamps in `YYYYMMDD-HHMMSS`.
- Use the filename grammar in `governance/naming_convention.md`.
- One work item keeps the same timestamp, phase, scope, and topic across
  analysis, plan, evidence, closure, review, and prompt files.
- Do not create ad hoc names such as `final-final`, `latest-real`, or
  `retry-fixed`.
- Superseded files are not deleted. Mark them in the relevant index and move
  them to `archive/superseded/<phase>/` only after the replacement is indexed.

## Content Rules

- Analysis files must start with `수정 대상: ...`.
- Plan files must start with `수정 대상: ...`.
- Evidence files must include command/run, raw artifact path, digest or explicit
  digest-not-available reason, result, and current-file match status.
- Review summaries must include reviewer perspective, input artifacts, raw
  review output path, finding counts, closure mapping, and remaining risk.
- Goal prompt files must state allowed edit scope, required gates, approval
  behavior, and completion evidence. A goal prompt must not allow completion
  without current-file evidence.

## Completion Rules

- Phase completion is recorded only in `status/phase_status.md`.
- A chat message, goal status text, or HTML report is not completion evidence by
  itself.
- `not scored`, missing oracle, stale report, digest mismatch, and unclassified
  infrastructure failure keep the relevant phase incomplete.
- Blocked is not complete. Use `infrastructure-blocked` when execution cannot
  proceed because of permissions, runner policy, or external service access.
