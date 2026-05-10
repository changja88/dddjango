# Iteration Plan

## Stop Condition

- All 17 public cases rerun with isolated baseline and with-dddjango artifacts.
- plugin hard gate failures: 0
- common hard gate failures: 0
- blocking/major/minor findings: 0
- runtime validation, diff check, leakage scan, and cache/source diff pass.
- `report.html` links only to existing artifacts.

## Next Steps

1. Fix baseline isolation so baseline cannot read `dddjango/skills`, runtime cache skill files, or active dddjango prompt-input metadata.
2. Fix public packet/operator wrapper wording so agents answer normally while the operator runner owns artifact persistence.
3. Rerun cases affected by eval protocol findings: `case-002`, `case-003`, `case-004`, `case-005`, `case-006`, `case-011`, `case-015`.
4. If rerun changes any with-ddjango result, update case analysis and report.
5. Only after major findings reach 0, decide whether runtime skill improvements are needed.
