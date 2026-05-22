# Open Risks

| id | phase | risk | classification | mitigation | status |
|---|---|---|---|---|---|
| risk-20260522-001 | p0-p8 | Documentation sprawl hides current phase state. | governance | Use `phase_status.md` and indexes as source of truth. | active |
| risk-20260522-002 | p4-p8 | Eval output appears complete while scoring artifacts are missing. | scoring-incomplete | P4 mini-bucket fixtures before model-backed evals. | active |
| risk-20260522-003 | p5-p8 | Goal status says complete without current-file evidence. | governance | Link every goal to evidence and review indexes. | active |
| risk-20260522-004 | p1 | P0 found 6 provisional source relationships that may not support skill changes yet. | source-sufficiency | Resolve in P1 before editing `dddjango/skills/**`. | active |
| risk-20260523-005 | p3-p8 | Runtime forward-tests are unavailable, so P4/P5/P6 cannot prove real skill routing yet. | infrastructure-blocked | Use ADR-0004 to allow P4 only after P3a; require P3b or equivalent installed-runtime evidence before P7/P8 completion. | active |
