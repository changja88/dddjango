# dddjango Eval Workspace

This directory groups evaluation material by the thing being judged.

## Current Buckets

- `response/`: response-level plugin evaluation. This includes response rubrics, source coverage crosswalks, public/private prompt packets, response report templates, and local response run artifacts.
- `code/`: future code-backed evaluation. This should include fixture repositories, prompts that require source edits, generated diffs, executable checks, and generated-code scoring.

## Likely Future Buckets

- `runtime/`: install, discovery, plugin cache, marketplace, symlink, and host integration checks when they need independent runs outside response scoring.
- `protocol/`: evaluator hygiene checks such as public/private material separation, leakage scans, report contract validation, and reproducibility audits if they grow beyond the response/code runners.

Do not create a new bucket only because a new script exists. Split only when the evaluated artifact, run inputs, and pass criteria are meaningfully different.
