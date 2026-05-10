# Findings

## EVAL-MINOR-003 - MINOR - fixed

- Case(s): case-017
- Defect type: eval protocol
- Gate/dimension: finding lifecycle / Claude-Codex compatibility evidence
- Before: `raw/case-017-with-dddjango.txt` reported a Minor packaging/source-of-truth risk because `plugins/dddjango` was observed as a real directory in the isolated eval workspace.
- After: `run_plugin_eval.py` now preserves symlinks when preparing eval workspaces, and the targeted `case-017` with-dddjango rerun exited 0 without the real-directory finding.
- Rerun scope: targeted `case-017` with-dddjango rerun after symlink-preserving workspace copy fix
- Evidence:
  - [case-017 with-dddjango raw](raw/case-017-with-dddjango.txt)
  - [case-017 with-dddjango command](raw/case-017-with-dddjango-command.txt)
  - [case-017 with-dddjango exit](raw/case-017-with-dddjango-exit.txt)
  - [case-017 events](raw/case-017-with-dddjango-events.jsonl)

No open blocking, major, or minor findings after the protocol rerun.
