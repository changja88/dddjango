# Task 3 implementation report

Status: **DONE — implementation frozen for independent review.** This closes the dispatched Task 3 implementation only. It does not close F4-9 in the original field report; Task 6 norm propagation and final audit remain coordinator-owned.

Workspace: `/Users/hyun/.cache/dddjango-field4-followup-20260911`. Compared against `task-3-before/manifest.json` and its six source snapshots. No primary checkout, actual spring_dream_server, environment symlink, ontology, norms, versions, seals, commits or releases were changed. The actual Parler source was not re-imported/executed; the closed origins use the already-confirmed source references in the brief.

## Exact changed files and interfaces

| File | Task 3 delta from snapshot |
|---|---:|
| `dddjango/scripts/check-public-surface-annotation.py` | +371 / -0 |
| `codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py` | byte mirror |
| `dddjango/scripts/design_pregate.py` | +77 / -18 |
| `codex-dddjango/skills/dddjango/scripts/design_pregate.py` | byte mirror |
| `workspace/tools/field_report_checker_smoke.py` | +136 / -0 |
| `workspace/tools/pregate_field_report_smoke.py` | +102 / -0 |

The requested SDD report and evidence logs are additional coordination artifacts, not plugin changes.

- `_admin_classes(mod: ast.Module) -> dict[ast.ClassDef, str]` resolves canonical Django admin/Parler origins, static same-module aliases, TYPE_CHECKING alternatives and local bases. Local fake/rebound bases are not origin proof; unresolved/dynamic origins remain candidates. No arbitrary project import or MRO execution occurs.
- `_admin_context_policy(mod, rel) -> dict[int, tuple[str, str]]` assigns `allow/candidate/ordinary` plus reason to annotation identities inside the checker process. It follows connected context bindings through copies, merges, fixed UI key writes, known framework sinks and direct private-helper arguments/returns. Business reads/comparison/calculation/state writes dominate unknown escapes; unknown calls and recursive helper paths remain candidates. Form/inline/media construction elsewhere in a function does not invalidate its context binding. Function-local transport rebinding is excluded only from body-call origin proof; signature annotations and class-base evaluation are unchanged.
- `_check_explicit_any.judge` consumes that policy only for #645/#647. It retains bare Any (including an open-dict union containing bare Any), unrelated annotation slots and separate business dictionaries. Fixed framework kwargs Any and resolved admin generic slots are narrow exceptions.
- `_generated_admin_slots(root, generated_methods) -> set[tuple[str, int, str]]` reads final generated AST only, loads the bundled checker to reuse its closed admin-origin/annotation classifiers, and indexes exact producer labels at the actual def line (or AnnAssign line). Open dict/Mapping helper slots are evidence for S1 only; parameter names do not prove UI role. Bare Any and non-open slots are excluded.
- `partition_generated_findings(gate_result, generated_methods, root: Path | None = None)` retains its `(retained, deferred)` result. The optional root preserves existing Task 2 callers; the real pregate caller supplies its materialized copy. It joins original violation **and candidate** records by exact checker and full normalized `findings.line_of_record` key. Every raw record in a cohort must have exact generated location/slot evidence. Missing numeric locations, free-form messages, unmatched lines, mixed generated/non-generated cohorts and other checkers remain undeferred. Original S1 #376 handling remains; #566 remains retained.
- Existing Task 2 materialization ordering, generated-method schema, GateResult schema, Findings schema, anchor placement and report/check-report channels are unchanged. The S1 section now also preserves the original `ⓓ` candidate line for eligible generated helper slots.

## Behavior evidence

All commands below ran in the workspace above. Logs are beside this report. Smoke and focused commands invoke the actual checker CLI and/or actual pregate CLI against isolated temporary repositories; synthetic cohort alterations are limited to the exact-join adversarial test after collecting real checker records.

| Stage | Exact command | Exit / evidence |
|---|---|---|
| Initial RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_context_real_parler_helper_and_business_opposite field_report_checker_smoke.CheckerRegression.test_admin_context_origin_alias_fixed_slots_and_local_business pregate_field_report_smoke.FieldReportTest.test_generated_admin_cli_defers_open_slots_but_keeps_bare_any` | exit 1; 3 tests, 3 failures; `task-3-red.log` |
| First focused green | same three tests | exit 0; 3 tests; `task-3-first-green.log` |
| Source-construction RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_context_sources_consumption_rebind_and_bare_slots` | exit 1; each_context/UI source not connected; `task-3-sources-red.log` |
| Source-construction green | preceding source test plus the two initial checker tests | exit 0; 3 tests; `task-3-sources-green.log` |
| Helper-return RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_helper_return_cycles_and_mixed_bare_annotation` | exit 1; chained helper return still blocked; `task-3-helper-red.log` |
| Seven focused tests | the initial 3, source-construction, helper-return, `pregate_field_report_smoke.FieldReportTest.test_generated_admin_exact_multiline_slots_and_mixed_cohorts`, and `pregate_field_report_smoke.FieldReportTest.test_admin_source_business_body_is_legacy_not_generated_s1` | exit 0; 7 tests; `task-3-focused-green.log` (before final shadow hardening and source-fixture simplification) |
| Required checker smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/field_report_checker_smoke.py` | exit 0; 16 tests; `task-3-checker-smoke.log` (before final shadow test/hardening) |
| Required pregate smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/pregate_field_report_smoke.py` | exit 0; 36 tests; `task-3-pregate-smoke.log` (before the source-fixture-only skip4 correction and final body-call shadow hardening) |
| Local shadow RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_context_shadowed_transport_names_are_not_framework_proof` | exit 1; local Response rebound was still treated as framework proof; `task-3-shadow-red.log` |
| Module shadow RED | same shadow test, adding module-level `dict = unknown` | exit 1; `task-3-module-shadow-red.log` |
| Final focused covering run | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_context_shadowed_transport_names_are_not_framework_proof pregate_field_report_smoke.FieldReportTest.test_generated_admin_cli_defers_open_slots_but_keeps_bare_any pregate_field_report_smoke.FieldReportTest.test_generated_admin_exact_multiline_slots_and_mixed_cohorts pregate_field_report_smoke.FieldReportTest.test_admin_source_business_body_is_legacy_not_generated_s1` | exit 0; 4 tests on final source; `task-3-final-focused.log` |
| Final checker covering smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/field_report_checker_smoke.py` | exit 0; 17 tests on final source; `task-3-final-checker-smoke.log` |
| Existing typing good | `python3 -B dddjango/scripts/check-public-surface-annotation.py workspace/eval/fixtures/public_surface/good` | exit 0; `task-3-final-typing-good.log` |
| Existing typing bad | `python3 -B dddjango/scripts/check-public-surface-annotation.py workspace/eval/fixtures/public_surface/bad_rules` | exit 2 as expected; #493/#645/#646/#647/#650 presence asserted; `task-3-final-typing-bad_rules.log` |
| Final syntax/mirror/diff | Python `compile(source, filename, 'exec')` on both canonical scripts and both smoke files; byte comparison for both mirrors; `git diff --check` | exit 0; mirror bytes identical, no syntax/whitespace errors |

Typing CLI runs used a temporary `DJR_FINDINGS_JSON`/`DJR_VIOLATIONS_DIR`; no fixture files were modified. Full `make verify` was not run: the coordinator owns the single final broad verification after later tasks.

### Fixture oracle corrections (not production defects)

- Initial normal-flow fixtures used unrelated `-> object` placeholders and expected all #647 lines to disappear. They were changed to `-> HttpResponse`, preserving the existing unrelated placeholder diagnosis rather than relaxing the checker.
- The #646 preservation probe initially used a runtime generic alias form the old #646 checker did not diagnose. The probe now uses the supported direct runtime generic base. `task-3-checker-first.log` records this oracle failure.
- The real admin `update` alone has no materialization and correctly returns skip4, not green0. An intermediate dummy add first hit the existing direct-framework-file #395 policy (`task-3-helper-green.log`); moving it to a valid path made the intermediate seven-test/full-smoke run pass. Per coordinator guidance, the final fixture removes that dummy entirely, expects skip4 and no S1, and independently runs the actual checker to assert real #647/exit2. `task-3-final-focused.log` covers that final test-only correction. `task-3-slots-first.log` records the original skip4 expectation error. Anchor/zero-materialization production semantics were never changed.

## Preserved and removed diagnoses

- Actual Parler-shaped override → `_render_failed_submission` includes form creation, inline instances, media, UI metadata from GET/POST, `each_context`, and `context.update(extra_context or {})`. Connected open context #645/#647 lines disappear; #493 and other independent rules still run.
- Reading `context['amount']`, comparing it, using `get`, computing container values or storing business state preserves ordinary #647. An unrelated payload dict in the same function remains a violation. Unknown calls and recursion produce nonblocking candidates, not a verified pass.
- Canonical alias/TYPE_CHECKING variants, UI literals, dict/copy/unpack/update and helper returns are covered; local fake/rebound bases and shadowed transport names do not prove a framework flow.
- #493 annotation presence, #646 generic runtime/bare rules and #650 JSON validation diagnostics remain independent. Existing typing bad fixture still emits all five typing rules.
- Generated helper open Any and object slots produce S1 lines with original messages, including original candidate records. Renamed slots behave identically. Bare Any and non-open `list[Any]` stay outside S1. Two classes with the same method name, multiline def/argument separation, mismatched checker, free prose, `:N`/`file_raw`, and mixed cohorts are covered.
- Real existing business bodies are never marked generated or moved to S1. The final update-only case is skip4 because there is no materialization; its actual checker remains exit2. Generated helper S1 is never described as verified, and G2 actual-flow checks remain necessary.

## Self-review and concrete limits

No blocking defect remains identified in the implemented/tested contract; independent Task 3 review is still pending. This is bounded AST analysis, not arbitrary interprocedural execution: unsupported/dynamic callees and recursive helper paths remain candidates; unresolved annotation-slot provenance remains the original diagnosis. Only the closed Django/Parler origin list and supported static same-module relationships provide origin proof. Nested/dynamic class/scope forms that cannot be associated with that proof receive no blanket exemption. Opaque custom helper semantics are not inferred from names.

The full pregate smoke completed before the final source-only body-shadow change. The final focused run covers both generated S1 CLI and raw slot cohorts after that change; the final full checker smoke covers actual-flow behavior. The final skip4 adjustment changed only the source-fixture oracle. No unrelated suites were rerun.

Final canonical hashes:

- public-surface checker and byte mirror: `60696373a2717f59128b8281896545be085bf8585616a859d9d38cb641ce8635`
- design_pregate and byte mirror: `50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd`

Serena/Graphify: omitted because neither worktree opt-in marker exists, as established by the coordinator. No discovery, initialization or use occurred. No subagents were spawned.

## Fix round 1 — review M1/M2 (frozen for scoped re-review)

Independent `task-3-review.md` found two concrete defects after the initial freeze. Both are corrected relative to `task-3-fix1-before/`; no other scope was added.

- **M1:** A fixed-string subscript Store is permitted only when its enclosing node is not `AugAssign`. Plain `extra_context['title'] = 'Books'` remains allowed; `extra_context['amount'] += 1` now produces the same #647 violation as the ordinary-read control `total = extra_context['amount'] + 1`.
- **M2:** The existing `super()` framework-sink proof now requires absence from both function-local and already-collected module bindings. `super = unknown` followed by a context-bearing `super().changeform_view(...)` produces a #647 candidate. Annotation/global evaluation and class-base origin lookup were not changed.
- Only `dddjango/scripts/check-public-surface-annotation.py` (two narrow branch changes), its byte mirror, and `workspace/tools/field_report_checker_smoke.py` (one four-case actual-CLI regression) changed. Pregate files, source/API signatures, generated-slot classifiers, schemas and anchor semantics are unchanged.

Evidence in this SDD directory:

| Check | Exact command | Result / log |
|---|---|---|
| RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_admin_augmented_write_and_module_super_shadow_preserve_diagnostics` | exit 1; augmented-write and module-super subcases both failed with missing diagnostics; plain UI-write and ordinary-read controls passed; `task-3-fix1-red.log` |
| GREEN | same focused command | exit 0; all four cases passed; `task-3-fix1-green.log` |
| Covering checker smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/field_report_checker_smoke.py` | exit 0; 18/18; `task-3-fix1-checker-smoke.log` |
| Generated S1 actual CLI | `PYTHONPATH=workspace/tools python3 -B -m unittest pregate_field_report_smoke.FieldReportTest.test_generated_admin_cli_defers_open_slots_but_keeps_bare_any` | exit 0; 1/1; `task-3-fix1-generated-cli.log` |
| Syntax/mirrors/diff | compile all six snapshot-scoped Python files with `compile(source, filename, 'exec')`; compare both canonical/mirror pairs byte-for-byte; `git diff --check` | exit 0; tool output confirmed all checks passed and only the three files above differed from the fix1 snapshot |

No full pregate or typing fixture suite was repeated in this round. No additional unresolved defect was found in the scoped self-review; independent re-review remains pending. This is a fix-round completion, not F4-9 or Task6 completion.

Updated public-surface checker/mirror SHA-256: `47afd19d407adc3318a68bb799841b368f860a7b703880d522d14108e78d6e06`. The design_pregate hash above is unchanged. Serena/Graphify remained unused because opt-in is absent; no subagents were spawned.
