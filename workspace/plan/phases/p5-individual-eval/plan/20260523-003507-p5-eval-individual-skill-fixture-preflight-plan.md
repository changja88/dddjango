수정 대상: `workspace/develop/eval/fixtures/individual-skills/`, `workspace/scripts/p5_individual_eval.py`, `workspace/scripts/test_p5_individual_eval.py`, `workspace/plan/phases/p5-individual-eval/`

# P5 Individual Skill Fixture Preflight Plan

## Plan

1. Add a P5 individual-skill fixture bucket with one positive and one negative
   surface per P1.5 trigger family.
2. Keep answer/oracle scoring focused on reference criterion coverage, required
   observations, and forbidden overclaim.
3. Add a P5-specific fixture scorer instead of modifying the P4 mini-bucket
   skeleton runner, so the affected eval bucket remains `individual-skills`.
4. Record run metadata digests for the cases file, P1.5 usage cards, P4 eval
   protocol, P5 runner, and all `dddjango/skills/*/SKILL.md` files.
5. Run related unit tests.
6. Run targeted fixture cases twice with `run-targeted-suite`.
7. Run the affected bucket all-cases command, regenerate the report, and run
   `validate-run`.
8. Record evidence and mark P5 incomplete until P4.5 plus model-backed
   installed-runtime runs exist.

## Completion Guardrails

- Do not use baseline verdicts, expected deltas, or pass-or-pass-limited as a
  completion gate.
- Do not present fixture-scored runs as model-backed evidence.
- Do not present individual skill eval as integration proof.
- Do not mark P5 complete while P4.5 is not complete in
  `workspace/plan/status/phase_status.md`.
