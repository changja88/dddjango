수정 대상: P4.5 runtime parity precheck execution plan and verification checklist.

# P4.5 Runtime Parity Precheck Plan

## Steps

1. Confirm P4 is complete and P4.5 is the next gate before model-backed P5/P6.
2. Inspect Codex config, installed cache, source manifest, and current phase
   artifacts.
3. Restore the missing local marketplace metadata required for Codex CLI
   discovery of the already-configured `dddjango-local` marketplace.
4. Refresh installed cache with `codex plugin add dddjango@dddjango-local`.
5. Capture raw evidence for marketplace list, plugin list, prompt-input
   discovery, install refresh, source/cache diff, manifest validation, runtime
   path-boundary scan, and bundled script absence.
6. Update phase analysis, evidence, closure, phase index, evidence index,
   artifact index, and phase status.
7. Run required verification:
   - `python3 -B workspace/scripts/validate_plan_governance.py`
   - source/cache diff check
   - manifest path validation
   - Codex discovery smoke
   - `git diff --check`

## Completion Gate

P4.5 can be marked complete only if:

- source/cache diff is empty after install refresh;
- plugin root outside dependency is not accepted as runtime evidence;
- at least one installed-cache dddjango skill appears in Codex prompt-input
  discovery;
- raw install/cache/discovery evidence exists for the current files;
- plan governance validation passes.

If any of these fail, P4.5 remains incomplete or infrastructure-blocked and
P5/P6 model-backed eval must not run.
