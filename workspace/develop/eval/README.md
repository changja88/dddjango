# dddjango Eval Workspace

This directory groups evaluation material by the thing being judged.

## Current Buckets

- `response/`: response-level plugin evaluation. This includes response rubrics, public/private prompt packets, response report templates, and local response run artifacts.
- `code/`: code-backed evaluation. This includes fixture repositories, prompts that require source edits, generated diffs, executable checks, and generated-code scoring.
- `runtime/`: install, discovery, plugin cache, marketplace, symlink, and host integration checks.
- `source/`: source-provenance evaluation. This includes crosswalks that trace runtime skill guidance back to `workspace/docs` and `workspace/reference`.
- `workflow/`: process evaluation. This covers TDD, DDD, subagent coordination, verification honesty, and over-application or under-application of workflow rules.
- `plugin/`: integrated plugin acceptance material that intentionally spans response, code, runtime, source, and workflow checks.

## Shared Protocol Checks

Evaluator hygiene checks such as public/private material separation, leakage scans, report contract validation, destructive-command safety, user-change preservation, and reproducibility should stay in the relevant bucket unless they become large enough to need an independent protocol eval.

Do not create a new bucket only because a new script exists. Split only when the evaluated artifact, run inputs, and pass criteria are meaningfully different.
