# AI Assisted TDD

Use this reference for AI-assisted TDD workflow, test-as-prompt thinking, validation, and false claim prevention.

## AI Workflow

- Plan: convert requirements into a test list.
- Red: write the failing test or exact test case first.
- Green: implement the smallest code that should satisfy the current test.
- Refactor: improve design with the test safety net.
- Validate: run the relevant tests and inspect failures, diffs, and behavior.

## Prompting With Tests

- Tests are executable prompts: they define what to build and when done means done.
- A failing test is stronger guidance than prose when AI is implementing.
- Keep tests focused on observable behavior so generated code is not overfit to internals.

## Honesty And Limits

- Do not claim Red unless the test was executed and failed for the expected reason.
- Do not claim Green unless the relevant test command was executed and passed.
- If the environment is read-only or missing dependencies, provide the test list and test code, then state what was not run.
- Security, concurrency, and performance often need additional analysis beyond ordinary TDD examples.
