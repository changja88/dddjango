# Source Eval Manual Protocol

Use this protocol when no first-class source bucket runner is available.

Inputs:
- Read public tasks from `cases/plugin/public`.
- Read evaluator-only criteria from `answer/`.
- Use `fixtures/` only for public source snippets or seeded non-private conflict examples.

Procedure:
- Trace workspace docs, source references, runtime bundled references, validation scenarios, provisional gaps, and DRF guardrails.
- Record whether each case consumed its matching public case and answer file.
- Keep private criteria out of public cases, runtime skill files, source fixtures, and generated crosswalks.
- Treat leakage of evaluator-only wording, prior run findings, or scoring notes as a blocking failure.

Evidence:
- Save source inventory, provenance crosswalk, conflict/gap ledger, coverage map, validation command output, and leakage scan under `runs/<run-id>/analysis/`.
- Include the case id, sources inspected, pass/fail observations, leakage scan result, and unresolved risk for every case.
