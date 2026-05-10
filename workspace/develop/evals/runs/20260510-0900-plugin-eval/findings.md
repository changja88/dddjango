# Findings

## EVAL-MINOR-003 - MINOR - open

- Case(s): case-017
- Defect type: eval protocol
- Gate/dimension: finding lifecycle / Claude-Codex compatibility evidence
- Before: `raw/case-017-with-dddjango.txt` reported a Minor packaging/source-of-truth risk because `workspace/docs/plugin-structure.md` describes `plugins/dddjango` as a symlink to `../dddjango`, while the observed eval workspace had `plugins/dddjango` as a real directory.
- Current gap: the previous final findings summary said there were no open blocking, major, or minor findings, so this Minor finding did not receive a resolution, accepted exception, or rerun evidence.
- Impact: not currently a runtime behavior failure because the raw output also records `diff -qr dddjango plugins/dddjango` as clean, but it blocks a completed plugin eval verdict under the private case-map severity defaults.
- Required resolution: fix the source layout/docs mismatch and rerun `case-017`, or record a narrow accepted exception with owner, revisit condition, and evidence.
- Evidence:
  - [case-017 with-dddjango raw](raw/case-017-with-dddjango.txt)
  - [private case-map severity defaults](../../cases/plugin/private/case-map.md)

No open blocking or major findings after the protocol rerun. One open minor finding remains.
