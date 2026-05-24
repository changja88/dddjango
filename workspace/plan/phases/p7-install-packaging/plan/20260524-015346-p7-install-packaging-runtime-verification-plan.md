수정 대상: P7 install packaging verification plan and runtime evidence completion.

# P7 Runtime Verification Plan

## Completed Static Steps

1. Confirm current repo root with `pwd -P` and `git rev-parse --show-toplevel`.
2. Read `plugin-creator` update guidance and `source-reference-audit` boundary
   guidance.
3. Refresh installed plugin cache:

```bash
codex plugin add dddjango@dddjango-local
```

4. Capture marketplace and plugin install status:

```bash
codex plugin marketplace list
codex plugin list --marketplace dddjango-local
```

5. Validate manifest paths and source/cache skill parity with a stdlib parser.
6. Check source/cache diff:

```bash
diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10
```

7. Capture a prompt-input probe proving installed-cache skill context is visible.
8. Prepare a 26-case runtime task matrix from the P3 forward-test prompt set so
   the blocked installed-runtime run can be resumed without changing prompt
   selection.

## Runtime Step

The following installed-runtime user-like command shape resolved
P3b-equivalent evidence for P7 after explicit approval:

```bash
codex -a never exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p7-runtime/<case-id> -s read-only -o /Users/hyun/Desktop/dddjango/workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-final-answers/<case-id>.txt '<forward-test prompt>' > workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-model-executions/<case-id>.jsonl
```

The P3 forward-test happy and exclusion prompts ran for all 13 high-risk trigger
families.

Prepared command matrix:

```text
workspace/plan/phases/p7-install-packaging/evidence/20260524-015346-p7-install-packaging-runtime-verification-runtime-task-matrix-raw.json
```

## Approval Used

The runtime step used this explicit approval:

```text
P7 model-backed installed-runtime user-like routing evidence를 승인한다. 외부 Codex/OpenAI runtime으로 P7 public forward-test prompts, installed dddjango runtime skill instructions/context, project instructions/context가 전송될 수 있음을 이해했고, high-risk trigger family happy/exclusion prompts를 `codex -a never exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p7-runtime/<case-id> -s read-only -o <final-answer> <forward-test prompt>` 형태로 실행하는 것을 허용한다.
```

## Completion Gates

- Raw JSONL and final-answer artifact exist for every required user-like task.
- Evidence matrix records actual loaded skill, expected route, source/cache
  path, final answer artifact, and false-trigger/exclusion result.
- Wrong routing, source/cache mismatch, outside-root dependency, or missing
  final answer would keep P7 incomplete; none were observed.
- `python3 -B workspace/scripts/validate_plan_governance.py` must pass after
  updating P7 docs and indexes.
