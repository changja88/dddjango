# Findings

## EVAL-MAJOR-001 - MAJOR - open

- Case(s): case-002, case-003, case-004, case-005, case-006, case-015
- Defect type: eval protocol
- Gate/dimension: Evaluation Protocol Integrity / baseline comparison validity
- Before: Baseline was intended to run without dddjango plugin guidance, but agents could read repo runtime skill files and nested `codex debug prompt-input` used active user config.
- After: Not fixed in this run.
- Rerun scope: Rerun baseline outside repo plugin source or with dddjango runtime files hidden; ensure nested codex debug uses isolated config.
- Evidence:
  - [case-002 baseline](raw/case-002-baseline.txt)
  - [case-003 baseline](raw/case-003-baseline.txt)
  - [case-005 baseline](raw/case-005-baseline.txt)

## EVAL-MAJOR-002 - MAJOR - open

- Case(s): case-002, case-003, case-004
- Defect type: eval protocol
- Gate/dimension: Required artifacts / reproducibility
- Before: Public packets ask for raw artifacts but runner wrapper also says `Do not modify files`; several agents therefore refused to save requested per-request artifacts.
- After: Operator runner saved case-level raw outputs, but public packet wording was not fixed in this run.
- Rerun scope: Update runner wrapper/public packet execution wording so forward agents answer normally while operator, not agent, owns artifact persistence.
- Evidence:
  - [case-003 baseline](raw/case-003-baseline.txt)
  - [case-004 baseline](raw/case-004-baseline.txt)
  - [case-003 with-dddjango](raw/case-003-with-dddjango.txt)
