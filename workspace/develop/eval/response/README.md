# dddjango Response Eval

This bucket contains response-only eval material for `dddjango`.

A response eval compares the final answer text from baseline and with-dddjango variants. It may inspect raw command/event artifacts to verify honesty, but it does not treat runtime discovery, source provenance, workflow execution, or generated code as primary completion criteria.

## Scope

In scope:

- Korean and Korean/English public prompts
- baseline vs with-dddjango final response transcripts
- private response scoring keys
- response-only rubric criteria
- answer usefulness, technical judgment, scope control, and verification honesty
- refusal to leak private eval material or claim unrun work
- self-contained HTML report for inspecting response artifacts

Out of scope:

- plugin install/discovery/cache checks: use `workspace/develop/eval/runtime`
- source crosswalk coverage: use `workspace/develop/eval/source`
- role-map/handoff process adherence as a primary outcome: use `workspace/develop/eval/workflow`
- generated source, diffs, and executable checks: use `workspace/develop/eval/code`
- integrated plugin acceptance verdicts: use `workspace/develop/eval/plugin`

## Directory Layout

```text
workspace/develop/eval/response/
  rubrics/
    response_rubric.md
  cases/plugin/public/
    case-003.md
    case-004.md
    case-007.md ... case-015.md
  cases/plugin/private/
    case-map.md
  templates/
    case-analysis.html
    public-packet.md
    private-evaluator.md
    run-report.html
  runs/
```

## Execution Rules

- Give prompt runners only files from `cases/plugin/public/` plus task-local files required by the user request.
- Do not give prompt runners `cases/plugin/private/`, rubrics, prior findings, expected routes, scoring notes, or intended fixes.
- Run baseline and with-dddjango against the same public prompt and same task-local evidence.
- Record raw outputs under `workspace/develop/eval/response/runs/<run-id>/raw/`.
- Store case-level human analysis under `workspace/develop/eval/response/runs/<run-id>/analysis/`.
- Store findings, reruns, and final report under the same run directory.
- The report must label missing raw response, command, event, or evaluator artifacts as `blocked` or `not scored`; do not retain a pass from stale static data.
- If a command, smoke check, review, or subagent pass was not run, the response evaluation may score only whether the answer reported that honestly.

## Required Run Artifacts

Each complete response run records:

- git commit or working-tree state
- public packet paths actually supplied
- raw baseline and with-dddjango response transcripts
- command and event artifacts when available
- case-level response analysis
- response scores loaded from run-specific evaluator output or recorded human judgment
- findings with severity, case id, failed response criterion, artifact path, and rerun scope
- final not-run list for any omitted checks mentioned by a response

## Completion Rule

The response eval is complete only when:

- every response public case has been run or is explicitly marked not-run as a blocker
- response hard gate failures are 0
- blocking, major, and minor response findings are all 0
- raw response evidence exists for every scored row
- private grader material is not included in public packets or runtime files
- non-response cases are not counted in the response score

Do not use this bucket to claim the plugin is complete. Passing response eval only means the final answer text satisfied the response rubric for the cases in this bucket.
