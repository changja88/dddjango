# Iteration Plan

## Stop Condition

- All 17 public cases rerun with isolated baseline and with-dddjango artifacts.
- plugin hard gate failures: 0
- common hard gate failures: 0
- blocking/major/minor findings: 0
- runtime validation, diff check, leakage scan, and cache/source diff pass.
- `report.html` links only to existing artifacts.

Status: satisfied after targeted `case-017` rerun.

## Resolution

- `case-017` originally reported `plugins/dddjango` as a real directory in the isolated eval workspace.
- Root cause: the runner used `shutil.copytree()` without `symlinks=True`, so the eval copy dereferenced `plugins/dddjango -> ../dddjango`.
- Fix: eval and code-capture workspace preparation now preserves symlinks.
- Evidence: targeted `case-017` with-ddjango rerun exited 0 and no longer reports the real-directory Minor finding.

## Next Steps

1. Keep the current protocol validator in the completion gate for future eval runs.
2. Add scored code-backed cases and progressive-disclosure/trigger-mutation checks in the next eval iteration.
3. If runtime skill behavior changes later, rerun the full public pack with the same isolated baseline protocol.
