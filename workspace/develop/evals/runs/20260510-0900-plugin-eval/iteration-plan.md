# Iteration Plan

## Stop Condition

- All 17 public cases rerun with isolated baseline and with-dddjango artifacts.
- plugin hard gate failures: 0
- common hard gate failures: 0
- blocking/major/minor findings: 0
- runtime validation, diff check, leakage scan, and cache/source diff pass.
- `report.html` links only to existing artifacts.

Status: reopened after post-review.

## Reopen Reason

- `raw/case-017-with-dddjango.txt` records a Minor finding about `plugins/dddjango` being a real directory while `workspace/docs/plugin-structure.md` describes it as a symlink to `../dddjango`.
- The final `findings.md` previously said there were no open blocking, major, or minor findings.
- The eval rules treat minor findings as pass-blocking for completed plugin evals, so this run cannot keep the stop condition as satisfied until the finding is resolved, accepted with an explicit exception, or rerun with evidence.

## Current Interpretation

- The protocol rerun still produced 17/17 with-ddjango case passes, 0 plugin hard gate failures, and 0 common hard gate failures by the saved evaluator judgments.
- The comprehensive `85/85` score should be read as response-level plugin integration evidence, not as final proof of code-backed skill effectiveness.
- `case-101` remains a code-artifact capture smoke and is not part of the comprehensive score.

## Next Steps

1. Add the `case-017` Minor finding to the findings lifecycle.
2. Decide whether the `plugins/dddjango` directory-vs-symlink mismatch should be fixed in source layout/docs, or recorded as an accepted exception with owner and revisit condition.
3. Rerun `case-017` after the fix or exception record, then update `findings.md`, `report.html`, and this iteration plan.
4. Keep `validate_eval_protocol.py`, `validate_skill_docs.py --phase all`, report readability validation, diff check, source/cache diff, and leakage scan in the completion gate.
5. Add a next-iteration eval improvement item for scored code-backed cases and progressive-disclosure/trigger-mutation checks.
