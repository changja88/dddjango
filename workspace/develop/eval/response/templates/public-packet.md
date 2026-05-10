# Public Packet Template

Use this shape for files that can be supplied to a prompt runner or forward-test agent.

Do not include intended routes, scenario labels, hard gate names, scoring notes, expected answers, private rubric findings, or prior conclusions.

## User Request

```text
<paste the user-facing request exactly as it should be executed>
```

## Context

- Repository: `/Users/hyun/Desktop/dddjango`
- Use only task-local files explicitly supplied by the operator.
- Do not read `workspace/develop/eval/response/rubrics`, `workspace/develop/eval/response/cases/plugin/private`, prior run reports, or previous findings unless the user request explicitly asks for an eval-system maintenance task.

## Output To Save

- Save the raw response or prompt-input artifact selected by the operator.
- Record commands actually run.
- State any checks that were not run.
