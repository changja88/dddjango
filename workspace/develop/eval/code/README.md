# dddjango Plugin Code Eval

This directory is reserved for code-backed evaluation of `dddjango`.

Use `eval/response` for response-level routing, workflow, and judgment quality. Use this directory only when the eval asks an agent to modify a fixture repository and then scores the generated code, captured diff, and verification output.

## Scope

- fixture repositories used as code-generation targets
- public prompts that request concrete code changes
- captured generated source, changed-file manifests, and diffs
- command evidence such as `pytest`, `ruff`, type checks, migrations, API contract checks, or focused smoke tests
- scoring rubrics for generated-code correctness, maintainability, safety, and verification honesty

## Expected Layout

```text
workspace/develop/eval/code/
  cases/
  fixtures/
  rubrics/
  templates/
  runs/
```

Create those subdirectories when the first code-backed eval is specified. Keep generated run outputs under `runs/<run-id>/`; they are local artifacts and are ignored by git.

## Boundary

This directory should not replace `eval/response`. A passing response eval proves that the plugin routes and explains work well. A passing code eval should prove that the plugin can produce source changes that satisfy executable project checks.
