# P4.5 Runtime Parity Precheck Evidence

## Paths

| item | path |
|---|---|
| source plugin root | `dddjango/` |
| source manifest | `dddjango/.codex-plugin/plugin.json` |
| Codex marketplace root | `/Users/hyun/Desktop/dddjango` |
| Codex marketplace manifest | `.agents/plugins/marketplace.json` |
| installed cache root | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` |
| installed cache manifest | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json` |

## Raw Artifacts

| artifact | raw path | digest | result | current-file match |
|---|---|---|---|---|
| marketplace manifest | `.agents/plugins/marketplace.json` | `b7eafdbad3493e49bd837b39ce4025af0101ba90d5c769b7c5302fc0e074f5e6` | valid JSON; root exception required for Codex marketplace discovery | current |
| source manifest | `dddjango/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` | source manifest parsed | current |
| cache manifest | `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` | cache manifest matches source manifest | current |
| install refresh | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-install-refresh-raw.txt` | `0de41c724efa104ff344da693ede1ed2221ab4cb43e97f9330983336bb0636c5` | `codex plugin add dddjango@dddjango-local` reported installed cache root | current |
| marketplace list | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-marketplace-list-raw.txt` | `69bfeea03540052ffefab406c37d60407e8d7877f5267728c934599eec689106` | `dddjango-local` listed at `/Users/hyun/Desktop/dddjango` | current |
| plugin list | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-plugin-list-raw.txt` | `12f903cdddf57ceec0a6f52fe457e1f74911106f330690877dfda61a2ac6af15` | `dddjango@dddjango-local` installed, enabled, version `0.1.10` | current |
| manifest validation | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-manifest-validation-raw.json` | `2139a2fde4dbdb1e0c4d07f75e4872ba77bb777eef5cb4d105b3e68c691c6193` | source/cache manifests parsed; paths inside plugin roots; 13 matching skills | current |
| source/cache diff | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-source-cache-diff-raw.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | empty `diff -qr` output; source/cache diff absent | current |
| outside path scan | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-outside-path-scan-raw.txt` | `40f3797da247201c9c23be99b1ad0aadb99f55ba1b78199f3f30ed64cf557692` | only `source-reference-audit` boundary wording mentions `workspace/reference`; not accepted as runtime dependency | current |
| runtime link boundary | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-runtime-link-boundary-raw.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | no Markdown links to `workspace/`, absolute local paths, or `../` | current |
| cache bundled scripts | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-cache-scripts-raw.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | no bundled scripts under installed cache; representative script run not required | current |
| prompt-input discovery smoke | `workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-prompt-input-raw.json` | `d0a87279294a38ce7308fe02c99a0d7d0b550c3511f99c10bee6bc727e59b51a` | raw prompt input includes `r2 = /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills` and `dddjango:source-reference-audit` | current |

## Command Results

| command/run | result |
|---|---|
| `codex plugin marketplace list` | exit 0; `dddjango-local` marketplace root is `/Users/hyun/Desktop/dddjango` |
| `codex plugin list --marketplace dddjango-local` | exit 0; `dddjango@dddjango-local` is `installed, enabled`, version `0.1.10`, path `/Users/hyun/Desktop/dddjango/dddjango` |
| `codex plugin add dddjango@dddjango-local` | exit 0; installed plugin root `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` |
| manifest validation Python command | exit 0; source/cache manifests have matching `name`, `version`, `skills`, skill count, and skill names; no manifest target outside plugin root |
| `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` | exit 0 with empty output; source/cache diff absent |
| `rg -n '\]\((workspace/\|/Users/\|/private/\|\.\./)' dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` | exit 1 with empty output; no runtime Markdown links outside plugin roots |
| `codex debug prompt-input ...` | exit 0 after escalated rerun; raw output shows at least one installed-cache dddjango skill, `dddjango:source-reference-audit` |

## Skill List

Manifest validation found 13 source skills and the same 13 cache skills:

- `architecture-api`
- `architecture-db`
- `architecture-ddd`
- `architecture-implementation-patterns`
- `implementation-cleancode`
- `implementation-django`
- `implementation-django-ninja`
- `implementation-django-web`
- `implementation-python`
- `implementation-tdd`
- `implementation-test`
- `source-reference-audit`
- `workflow-dddjango-subagents`

## Boundary Notes

- `source-reference-audit` intentionally contains public/source-governance
  wording about `workspace/reference`; this is audit guidance, not a runtime
  dependency or bundled reference path.
- The runtime link-boundary raw artifact is empty, so no Markdown link points
  outside the plugin root.
- P4.5 does not run P5/P6 model-backed eval.
- P4.5 does not resolve P3b runtime-routing evidence deferred by ADR-0004.

## Final Verification

| command | result |
|---|---|
| `python3 -B workspace/scripts/validate_plan_governance.py` | exit 0; `OK: plan governance validation passed` |
| `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` | exit 0; no output |
| manifest validation Python command | exit 0; `manifest validation ok: 13 matching skills; manifest skills paths stay inside source/cache plugin roots` |
| `rg -n 'r2 = ...|dddjango:source-reference-audit' workspace/plan/phases/p4-5-runtime-parity/evidence/20260523-011456-p4-5-runtime-parity-precheck-prompt-input-raw.json` | exit 0; raw prompt-input evidence contains installed cache skill root and `dddjango:source-reference-audit` |
| `git diff --check` | exit 0; no output |
