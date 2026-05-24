수정 대상: P7 install packaging source/cache parity and installed-runtime routing evidence analysis.

# P7 Runtime Verification Analysis

## Preconditions

- P6 integration eval is complete.
- P4.5 runtime parity is complete.
- P3b runtime forward-test remains deferred by `ADR-0004`, so P7 must either
  resolve it with equivalent installed-runtime user-like evidence or remain
  incomplete.

## Scope

P7 needs two evidence classes:

1. Install/package parity:
   - `.codex-plugin/plugin.json` path fields start with `./`.
   - Manifest path targets stay inside the plugin root and exist.
   - `.codex-plugin/` contains only `plugin.json`.
   - Source and installed Codex cache match exactly.
   - Codex plugin list shows the intended `dddjango` namespace and installed
     cache path.
2. Installed-runtime user-like routing:
   - Run high-risk trigger-family prompts in installed Codex runtime.
   - Record actual loaded skill, source/cache path, final answer/artifacts, and
     false-trigger or exclusion behavior.

## Findings

- Install/package parity is currently clean:
  - `codex plugin add dddjango@dddjango-local` refreshed the installed cache.
  - Source and cache manifests have matching digest
    `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a`.
  - `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`
    produced empty output.
  - The stdlib manifest/path validator found 13 matching skills and no
    source/cache skill mismatch.
- `plugin-creator` validator could not run because the local script requires
  PyYAML and the current Python environment does not provide `yaml`.
  Equivalent stdlib path validation was run instead.
- `codex debug prompt-input` can observe installed-cache skill context, including
  `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills` and
  namespaced `dddjango:*` skills.
- After explicit P7 approval, installed-runtime user-like `codex exec` ran for
  all 26 P3-derived prompts.
- Runtime analysis passed:
  - 26/26 commands returned exit 0 and produced final answers.
  - 26/26 expected routes matched the actual loaded dddjango skill.
  - 26/26 JSONL artifacts include the expected installed-cache `SKILL.md` path.
  - 13/13 exclusion prompts loaded the expected exclusion target skill rather
    than the matrix target.

## Completion Impact

P7 is complete. Install/cache evidence is current and P3b-equivalent
installed-runtime user-like routing evidence is available for the P7/P8
completion path.
