# Workflow Eval Manual Protocol

Use this protocol when no first-class workflow bucket runner is available.

Inputs:
- Read public tasks from `cases/plugin/public`.
- Read evaluator-only criteria from `answer/`.
- Use `fixtures/` only for public workflow prompts or sanitized handoff examples.

Procedure:
- Evaluate role-map selection, sequential fallback, actual subagent trace honesty, handoff fields, risky write consistency, findings-first review ordering, opt-out handling, and tiny-task restraint.
- Record whether each case consumed its matching public case and answer file.
- Keep private criteria out of prompts, workflow skill files, handoff fixtures, and generated reports.
- Treat leakage of evaluator-only wording, prior run findings, or scoring notes as a blocking failure.

Evidence:
- Save role map, handoff review, sequential fallback or actual execution trace, integration checklist, and leakage scan under `runs/<run-id>/analysis/`.
- Include the case id, artifacts inspected, pass/fail observations, leakage scan result, and unresolved risk for every case.
