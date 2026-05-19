# Red Green Refactor

Use this reference for the core TDD cycle, red/green/refactor rules, green strategies, and honest execution reporting.

## Cycle

- Red: add one small test and verify it fails for the expected reason when execution is available.
- Green: write the minimum code needed to pass the current test.
- Refactor: remove duplication, improve names, and clarify design while tests stay green.
- Repeat in small steps; do not batch many unverified requirements into one large implementation.
- If a new test passes immediately against existing production code, do not report a Red step. Treat that check as regression or characterization coverage unless you also capture a deliberate failing proof, such as an earlier failing run or mutation/revert check.

## Green Strategies

- Fake it when a hard problem can start with a concrete example and later generalize.
- Use triangulation when one example is not enough to justify abstraction.
- Use obvious implementation when the solution is truly clear and small.
- Keep the current green step narrower than the full final design.

## Refactor Checkpoints

- Refactor only after tests pass.
- Preserve externally visible behavior unless the next test deliberately changes it.
- If tests cannot be run, keep the refactor smaller and report that the red/green status is unverified.
