# Plugin Eval Manual Protocol

Use this protocol when no first-class plugin bucket runner is available.

Inputs:
- Read public tasks from `cases/plugin/public`.
- Read evaluator-only criteria from `answer/`.
- Use `fixtures/` only for public, non-oracle setup material.

Procedure:
- For each selected case, inspect the plugin source tree, runtime skill folders, `agents/openai.yaml`, bundled references, manifest files, marketplace entry, and cache/source sync evidence.
- Record whether each case consumed its matching public case and answer file.
- Keep private criteria out of prompts, runtime skill files, bundled references, and fixture content.
- Treat leakage of evaluator-only wording, prior run findings, or scoring notes as a blocking failure.

Evidence:
- Save review notes, command output, source/cache comparison, and packaging checks under `runs/<run-id>/analysis/`.
- Include the case id, files inspected, pass/fail observations, leakage scan result, and unresolved risk for every case.
