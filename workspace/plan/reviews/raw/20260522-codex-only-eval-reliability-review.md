# Raw Reviewer Output: Eval/Reliability Perspective

- Review date: 2026-05-22
- Reviewer: subagent `019e4f9d-a7c2-71e0-bd4f-8dda605f71f7`
- Scope: read-only review of `workspace/plan/plugin_build_plan.md` and `workspace/plan/reviews/20260522-plugin-build-plan-review.md`
- Sanitization: absolute local repository paths in reviewer output were replaced with `<repo>/...`.

## Output

Verdict: Blocker 0 / Major 2 / Minor 1

Findings:

1. Major: local path leakage detection is ordered ambiguously because the plan says local path scanning applies to raw artifacts, but then says raw artifacts are redacted before storage.

Why it can cause real failure: if the scanner only sees persisted post-redaction artifacts, a run that originally leaked local paths, cache paths, or other local-only paths can be sanitized into a passing state. That recreates the previous local path leakage hidden by report/artifact processing failure mode.

Concrete fix: define a two-phase leakage gate. First scan unredacted raw event JSONL/stdout/stderr/report inputs in an ephemeral controlled location and fail the run if forbidden local paths or private fields are present. Store only a sanitized finding summary with counts/classes/hashes. Then redact persisted artifacts and run a second scan to ensure the sanitizer worked. Update the P4 local-path fixture so a sanitizer-only pass is treated as failure.

2. Major: final review evidence is not durably auditable from the workspace. The review file records raw reviewer output as conversation subagent notification IDs, not full raw output text or a file path with digest.

Why it can cause real failure: P8 requires the last independent review evidence to prove Blocker 0 / Major 0 / open Minor 0, but a future runner or reviewer cannot independently read those notification IDs from the repository.

Concrete fix: store each raw reviewer output under a durable path such as `workspace/plan/reviews/raw/<timestamp>-<perspective>.md`, include input artifact digests, and have the summary link each closed finding to the plan/review lines or diff evidence that closed it.

3. Minor: model variance handling is present for new/modified model-backed cases, but P8 does not explicitly require a variance ledger or known-flake clearance before final completion.

Why it can cause real failure: a model-backed case that has prior pass/fail disagreement could pass the final full regression once and still be promoted as clean, especially if it was not newly modified in P5/P6.

Concrete fix: add a `flake_history` or variance status to run metadata. P8 should require no unresolved flaky cases and should reject final completion if any case has recent pass/fail disagreement that has not been classified and fixed in case/answer/evaluator/runner.

Open questions:

- Are conversation subagent notification IDs retrievable by future agents/runners, or should all reviewer outputs be persisted into `workspace/plan/reviews/` as repository artifacts?
- Should local path leakage be considered a run failure even if redaction succeeds before artifact persistence?

Pass rationale:

The plan covers most named prior failure modes well: targeted-only completion is blocked by affected-bucket and full-run gates; `not scored`, missing/malformed oracle JSON, stale reports, expected outcome conflicts, validator false positives, current-file fingerprints, and sandbox/runner permission failures all have explicit gates or fixtures. The remaining issues are about proof ordering and audit durability.

Serena: skipped by reviewer because Serena MCP tools were not available in that session.
