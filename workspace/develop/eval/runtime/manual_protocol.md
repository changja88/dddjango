# Runtime Eval Manual Protocol

Use this protocol when no first-class runtime bucket runner is available.

Inputs:
- Read public tasks from `cases/plugin/public`.
- Read evaluator-only criteria from `answer/`.
- Use `fixtures/` only for public runtime setup or sanitized prompt-input samples.

Procedure:
- Compare baseline and with-dddjango prompt construction, runtime cache exposure, skill metadata, role-map routing, provisional status, and cache/source consistency.
- Confirm baseline isolation before judging plugin behavior.
- Record whether each case consumed its matching public case and answer file.
- Keep private criteria out of prompt-input artifacts, runtime bundled references, and fixture content.
- Treat leakage of evaluator-only wording, prior run findings, source-only paths, or scoring notes as a blocking failure.

Evidence:
- Save prompt-input review, baseline isolation checks, cache/source comparison, and routing notes under `runs/<run-id>/analysis/`.
- Include the case id, artifacts inspected, pass/fail observations, leakage scan result, and unresolved risk for every case.
