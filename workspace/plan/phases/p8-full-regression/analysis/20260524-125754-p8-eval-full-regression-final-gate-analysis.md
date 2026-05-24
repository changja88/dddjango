수정 대상: `workspace/develop/eval/**`, `workspace/scripts/**`, `workspace/plan/phases/p8-full-regression/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P8 Full Regression Final Gate Analysis

## Scope

P8 must judge plugin completion from final full-run artifacts and current
installed-runtime evidence only. The accepted equivalent for original P3b is the
P7 installed-runtime user-like routing evidence, but it remains usable only if
source skill files, plugin manifest, and installed cache still match.

## Current State

- P7 install packaging is recorded complete.
- Source/cache diff is empty at the current pre-run check.
- Source and installed-cache manifest digests still match:
  `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a`.
- Existing P5/P6 model-backed validation artifacts passed before the P8 runner
  leakage fix, but they are not P8 final full-run evidence.
- The P8 full regression external model-backed run is not executed yet because
  this phase needs explicit P8 data-export approval.

## Gap Classification

| gap | classification | required resolution |
|---|---|---|
| P8 model-backed full run absent | execution pending | Run P5 and P6 installed-runtime targeted 2x and all-cases bucket runs after explicit approval. |
| Persisted model execution raw streams can contain local paths | final narrow runner fix | Redact local runtime paths in persisted stdout/stderr, execution metadata, and report source paths before P8 runs. |
| P8 independent review absent | review pending | Review final P8 raw/report/evidence after full run; Blocker 0, Major 0, open Minor 0 required. |
| P8 closure absent | completion pending | Write closure only after full run, validation, leakage, fingerprint, P7 current, flaky, and review gates pass. |

## Non-Goals

- Do not reuse P5/P6 targeted passes as P8 completion.
- Do not treat HTML reports as primary truth.
- Do not claim P8 completion while external model-backed full-run artifacts are
  missing.
