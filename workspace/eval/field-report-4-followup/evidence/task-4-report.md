# Task 4 implementation report

Status: DONE_WITH_CONCERNS — implemented and frozen for independent review. No known failing executed check. Conservative support limits below are reviewable; Task6 retains normative wording/grade alignment.

Worktree: `/Users/hyun/.cache/dddjango-field4-followup-20260911`.
SDD_DIR: `.superpowers/sdd/2026-09-11-field-report-4-followup`.
Baseline: coordinator `task-4-before/` snapshot, preceding checker smoke18. This task adds9 test methods; prior18 test AST bodies are unchanged.

## Owned changes

Only these7 product/test files changed for Task4:

- `dddjango/scripts/check-context-isolation.py`
- `codex-dddjango/skills/dddjango/scripts/check-context-isolation.py`
- `dddjango/scripts/check-domain-model.py`
- `codex-dddjango/skills/dddjango/scripts/check-domain-model.py`
- `dddjango/scripts/check-port-adapter-pairing.py`
- `codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py`
- `workspace/tools/field_report_checker_smoke.py`

Task-local logs/report and snapshot comparison are under SDD_DIR. No primary checkout/user-project execution or writes, installs, subagents, transaction-boundary/F20 work, TTL, normative docs, original field report cleanup, sealing, Make targets, versioning, commits or release. Existing Task1–3 work remains intact. Serena/Graphify omitted because this worktree has no opt-in; neither was discovered/loaded/initialized.

## Exact functions and behavior

`check-context-isolation.py`:

- New `_ohs_execution_count(entry, mod, fn) -> tuple[int, bool]`: module/import aliases, annotation receivers, constructor bindings and direct aliases are tracked only for this function. Application usecase slot must contain the named class. A `build_*_use_case` symbol from composition_root must have a readable declaration with usecase return annotation or direct construction return. Builder preparation itself contributes no execute. Inline/qualified builder results work. Reassignments invalidate origins; conflicting If/loop/try joins stay unknown. Uncalled nested function/class/lambda bodies do not contribute execute count. Repetition/comprehension execute sites retain an unknown-count candidate.
- `_check_ohs_service` uses proven execute count and unknown flag for the existing #153 candidate. Its domain-exception-property #153 violation and all other service checks remain.

`check-domain-model.py`:

- New `_closed_standard_enum(mod, cls) -> tuple[bool, bool]`: closed standard Enum/StrEnum/IntEnum detection plus enum-origin marker. Direct import alias/module alias accepted. Literal or standard auto members accepted. Flag, dynamic members, user base/metaclass/decorator/custom construction/missing hooks, import rebinding and class attribute mutations stay outside closed exemption.
- `_check_value_object_file` retains #264 and #259 checks; only closed enums avoid #268. Custom standard-enum constructors stay candidates even when they contain raise.
- New `_function_nodes(node)` prunes nested definitions. `_repo_bindings` uses it so nested parameter annotations do not retype an outer repository receiver.
- New `_transaction_write_regions(root, py, mod, fn, cls, repos)` resolves standard UoW parameters, direct constructor-injected self fields, local/imported annotated factories and aliases. It records repository/aggregate TYPE sets per lexical transaction region. Sequential outer UoWs separate; nested and multiple context items combine; explicit external Django atomic/decorator combines enclosed UoWs. Unknown context/transaction operations retain a function-wide candidate. with-as UoW aliases and newly derived UoW aliases do not escape their block.
- `_check_application_side` emits #546 violations for known regions with two repository/aggregate types; writes outside resolved boundaries or with uncertainty retain a candidate. Existing #550/#257 code remains and excludes uncalled nested bodies from the parent traversal.

`check-port-adapter-pairing.py`:

- New `_check_property_origins(root, py, mod, f, cand)`: #557 evaluates code/errno/status_code receivers throughout both left and comparator expressions; duplicate receiver/attribute in one comparison emits once. Exact vendor allowlist covers specified Django DB/sqlite/psycopg/requests/httpx families. Readable local domain or application command/query/result/port class declarations are contracts; explicit reexports resolve recursively with cycle guard, including vendor reexport through a port path. Constructors/annotations/direct aliases and except bindings are tracked; mixed origins, dynamic helper returns, rebinds and conflicting branches remain candidates. Each function gets independent state, with direct constructor fields available to methods.
- `_check_use_side` replaces only the prior blanket #557 comparison check; counterpart diagnostics are retained.

No project module is imported at runtime. All source inspection uses standard-library AST and local files; no shared/general dataflow engine or new instance-identity model was introduced.

## RED and GREEN evidence

All commands ran in the isolated worktree. Focused prefix is literal `python3 -B workspace/tools/field_report_checker_smoke.py`; append the exact selectors below. Each RED exit was1 (assertion failures, not test errors), each GREEN exit was0.

| Group | Selector(s) | RED evidence | GREEN evidence |
|---|---|---|---|
| F10 | `CheckerRegression.test_ohs_execution_provenance_and_count` | `task-4-f10-red.log`:8 failures | `task-4-f10-green.log`:1 test OK |
| F11 | `CheckerRegression.test_closed_enum_validation_and_dynamic_opposites` | `task-4-f11-red.log`:3 failures | `task-4-f11-green.log`:1 test OK |
| F10 repetition gap | `CheckerRegression.test_ohs_execution_provenance_and_count` | `task-4-f10-loop-red.log`:2 failures | `task-4-f10-loop-green.log`:1 test OK |
| F14 | `CheckerRegression.test_uow_lexical_regions_and_unknown_boundaries` | `task-4-f14-red.log`:11 failures | `task-4-f14-green.log`:1 test OK |
| F15 | `CheckerRegression.test_property_comparisons_use_actual_origin_on_both_sides` | `task-4-f15-red.log`:18 failures | `task-4-f15-green.log`:1 test OK |
| Scope self-review | `CheckerRegression.test_origin_scope_rebindings_remain_unknown CheckerRegression.test_uow_injected_fields_and_factory_alias_scope` | `task-4-scope-red.log`:4 failures | `task-4-scope-green.log`:2 tests OK |
| Declaration/nested parameter self-review | `CheckerRegression.test_declared_usecase_and_enum_constructor_opposites CheckerRegression.test_nested_repository_parameters_do_not_retype_outer_bindings` | `task-4-declarations-red.log`:2 failures | `task-4-declarations-green.log`:these2 plus custom enum test OK |
| Custom Enum validation | `CheckerRegression.test_custom_enum_validation_does_not_prove_closed_members` | `task-4-enum-custom-red.log`:1 failure | `task-4-declarations-green.log`:3 tests OK |

Final focused command used all9 Task4 selectors listed above once (deduplicated); exit0,9 tests OK in `task-4-focused-green.log`.

## Covering checks (after final source changes)

- `python3 -B workspace/tools/field_report_checker_smoke.py`: exit0, **27 tests OK**, `task-4-smoke.log`. Full smoke ran once after group-focused GREEN.
- Related fixture/invocation lanes: `python3 -B` heredoc imported `workspace/tools/fixture_matrix.py`, selected its cases only when command checker was one of the3 owned checkers, copied each target into a fresh TemporaryDirectory, then ran `[python, '-B', checker, copied_target, *arguments]` with temporary Findings/violations sinks. Wrapper exit0, **10/10 expected exits**. Exact per-lane outputs and findings are in `task-4-fixtures.log`:
  - context_isolation good0 / bad_rules2;
  - domain_model good0 / bad_rules2;
  - port_adapter_pairing good0 / bad_rules2 / skeleton_placeholder0;
  - three invocation contract lanes each1.
- Byte mirror + `compile(source_text, filename, 'exec')` for6 checker files and smoke test: exit0, `task-4-byte-compile.log`. No bytecode or environment install.
- `git diff --check`: exit0, empty `task-4-diff-check.log`.
- Snapshot comparison: `task-4-snapshot-diff.log` contains complete Task4-only unified diffs against `task-4-before` and an AST equality assertion for the prior18 test bodies; exit0.

Observed preservation: fixture output still has the explicit domain exception `.code` #153 violation, aggregate nested member mutation #257 and queried collection save_all #550 violations. New literal tests separately preserve value-object #264/#259. Prior Task1–3 tests all remain green. Existing fixture #546 without a resolved transaction and #557 with unknown receiver now intentionally use candidate grade; bad_rules lanes remain exit2 through their other findings.

## Bounded support and concerns for review

- F10 counts static sites; it does not prove mutually exclusive dynamic path counts, callback/helper behavior, dynamically chosen builders or arbitrary package reexports. Missing declarations and unsupported execute origins stay candidates. Standard direct usecase files are supported; generic forward/reexport type resolution is not added to F10.
- F11 closedness is bounded to the observed class/module AST. Arbitrary runtime monkeypatching, imported decorators and indirect mutations are not globally proved. Static unknown/custom construction remains a candidate.
- F14 observes the current function's lexical regions only. It makes no whole-call independent-commit claim: external callers, ATOMIC_REQUESTS, indirect helper transactions and runtime factory behavior are outside support. Repository→aggregate TYPE proxy is retained; instance identity is not analyzed. Unknown with/decorator/transaction forms are deliberately conservative. Initializer field support is direct assignment only. A local/imported factory needs a standard return annotation; inferred arbitrary helper return is unknown.
- F15 handles direct assignments/annotations/imports, If/loop/try/with joins and explicit reexports; this is not full Python dataflow. Module assignment names are conservatively invalidated in function scopes, so a module assignment alias may receive an unknown candidate even where a direct import alias/local alias resolves. Match/walrus/dynamic mutation and general helper-return typing have no new special analysis. Review should judge this conservative boundary against the approved alias requirement; no silent vendor exemption is intended.
- Task6 owns normative grade/text alignment. This task did not edit checker top-level rule descriptions or normative owner grades, so former unconditional #546/#557 wording remains to be aligned there. Original F4 report items remain open for the later review/audit, not closed by this implementation report.

Source frozen after the checks above. Independent implementation review is the next gate; no release/commit is implied.

## Fix round1/5 — review M1–M5

Status after fix1: **DONE**, frozen for scoped independent re-review. This section supersedes the initial report's outstanding static-module-alias concern. The five Important review findings were reproduced, fixed and covered; no new policy choice was needed. Broader supported/unsupported syntax limits and Task6 ownership remain as stated above.

Baseline: coordinator `task-4-fix1-before/` snapshot. Scope remains the same7 files. No source outside the owned7 changed in this round; no external/user-project execution, environment installs, subagents, normative edits, seals or Git state changes. Read-only `git diff --check` was explicitly confirmed by the coordinator and executed.

### Changes tied to review IDs

- **M1**, `_ohs_execution_count`, nested `block`: records execute count before inspecting a while condition and marks unknown repetition if the condition contains a proven execute. This guard applies to While only, preserving the once-evaluated iterable of a For loop. Existing body/comprehension uncertainty and nested-definition pruning remain.
- **M2**, `_closed_standard_enum`: every ImportFrom or Import first invalidates the local names it binds; recognized enum imports then establish their exact standard origin. A later custom import can no longer retain an old standard Enum proof.
- **M3**, `_transaction_write_regions`, module environment assembly: imports, typed factory declarations and assignments now update the environment in source order. Removed the deferred `factories` overlay which revived a previously invalidated factory.
- **M4**, constructor field extraction in `_transaction_write_regions` and `_check_property_origins`: unsupported constructor statements are inspected for Name/Attribute Store/Del targets and invalidate those bindings. Nested uncalled function/class/lambda bodies are excluded. Direct injection remains supported; arbitrary helper return inference or new control-flow analysis was not added.
- **M5**, `_check_property_origins`: module names are tracked as they first bind. Initial static aliases retain their observed origin; subsequent rebinding of an already-bound module name is conservative unknown in function analysis. Readable domain aliases are exempt, exact vendor aliases produce violations, and dynamic reassignments/conflicting branches remain candidates.

### RED → focused GREEN

Exact common command prefix: `python3 -B workspace/tools/field_report_checker_smoke.py`.

New regression selectors (all6 were written before changing production code):

1. `CheckerRegression.test_while_guard_execute_repeats_but_for_iterable_executes_once`
2. `CheckerRegression.test_later_import_shadow_invalidates_standard_enum_origin`
3. `CheckerRegression.test_rebound_annotated_factory_is_not_revived`
4. `CheckerRegression.test_constructor_branch_invalidates_uow_field_origin`
5. `CheckerRegression.test_constructor_branch_invalidates_contract_field_origin`
6. `CheckerRegression.test_initial_static_module_alias_preserves_origin_but_rebinding_does_not`

Running the common prefix followed by all6 selectors produced exit1, **6 tests /8 assertion failures**, recorded in `task-4-fix1-red.log`. No errors were test-setup failures.

After each bounded correction, the corresponding selector(s) were rerun:

- M1 selector1: exit0, `task-4-fix1-m1-green.log`.
- M2 selector2: exit0, `task-4-fix1-m2-green.log`.
- M3 selector3: exit0, `task-4-fix1-m3-green.log`.
- M4 selectors4+5: exit0, `task-4-fix1-m4-green.log`.
- M5 selector6 plus existing `CheckerRegression.test_origin_scope_rebindings_remain_unknown`: exit0, `task-4-fix1-m5-green.log`.
- All6 new selectors together: exit0, **6 tests OK**, `task-4-fix1-focused-green.log`.

### Covering checks after final source change

- `python3 -B workspace/tools/field_report_checker_smoke.py`: exit0, **33 tests OK**, `task-4-fix1-smoke.log`. One covering full-smoke execution in fix1.
- Same temporary-copy `fixture_matrix.build_cases()` harness described above, selecting only the3 owned checkers: exit0, **10/10 expected exits**, `task-4-fix1-fixtures.log`. All three good/bad pairs, port skeleton and three invocation lanes passed. No unrelated matrix lane ran.
- Three byte mirror pairs, six checker compiles and smoke compile: exit0, `task-4-fix1-byte-compile.log`.
- `git diff --check`: exit0, empty `task-4-fix1-diff-check.log`.
- Snapshot unified diff/self-review and AST preservation assertion: exit0, `task-4-fix1-snapshot-diff.log`; prior **27 test bodies unchanged**, current33. Diff inspection confirmed changes only in the review-named origin/count blocks and6 new test methods. Counterpart diagnoses remain covered by the unchanged tests and fixture lanes.

Task6 deferred wording location: `dddjango/scripts/check-domain-model.py:546` (and byte mirror), `_check_value_object_file` #268 message containing `__init__/__post_init__ 에 raise 가 없다`. Its custom-Enum-with-raise behavior remains correctly candidate, but the explanatory text needs the already assigned Task6 alignment. Header grades/descriptions also remain Task6 work. No wording/normative change was made here.

Serena/Graphify were not used because this worktree has no opt-in. Source frozen after the checks above for the scoped Task4 re-review.

## Fix round2/5 — residual M5-R1

Status: **DONE**, frozen for scoped independent re-review. M1–M4 code is unchanged in this round. M5-R1's after-function conditional rebinding is now collected before function analysis; initial static aliases and nested-definition boundaries remain intact.

Baseline: coordinator `task-4-fix2-before/` snapshot. Exactly3 files changed: `dddjango/scripts/check-port-adapter-pairing.py`, its Codex byte mirror, and `workspace/tools/field_report_checker_smoke.py`. The other4 Task4 files are byte unchanged against fix2-before. No norms, original report cleanup, F20, Task5, primary/user-project work, Git state changes, installs or subagents.

### Minimal correction

`_check_property_origins` module binding pre-scan (pairing script around1219) now traverses existing supported module compound statements using a source-order stack. If/For/While/Try/With and their existing async/handler forms expose their module-scope bindings before any function body is analyzed. Function/class declarations bind only their declared name; their bodies are not traversed as module bindings. An alias potentially reassigned after the function definition therefore becomes unknown for a constructor call inside that function. No helper-return inference or new dataflow engine was added.

### RED → GREEN

Common command prefix: `python3 -B workspace/tools/field_report_checker_smoke.py`.

New selectors:

- `CheckerRegression.test_later_module_compound_rebinding_invalidates_function_constructor`
- `CheckerRegression.test_nested_definition_bindings_do_not_rebind_module_constructor_alias`

The first tests both actual domain and exact vendor constructors referenced inside a function, followed by module If/While/For/With/Try alias reassignment. The second tests function/class bodies nested in a later module If and verifies their local assignments do not invalidate the module alias.

Both selectors together before production changes: exit1, **2 tests /10 assertion failures**, `task-4-fix2-red.log`. The nested-definition boundary control passed before and after the fix.

Both new selectors plus existing `CheckerRegression.test_initial_static_module_alias_preserves_origin_but_rebinding_does_not CheckerRegression.test_origin_scope_rebindings_remain_unknown` after correction: exit0, **4 tests OK**, `task-4-fix2-focused-green.log`.

### Covering checks

- `python3 -B workspace/tools/field_report_checker_smoke.py`: exit0, **35 tests OK**, `task-4-fix2-smoke.log`; one full-smoke run after the final source change.
- Temporary-copy `fixture_matrix.build_cases()` harness, only pairing checker cases: exit0, **4/4** expected exits (good0, bad_rules2, skeleton_placeholder0, invocation1), `task-4-fix2-fixtures.log`. Previous fix1 context/domain fixture evidence is reused because those sources are unchanged.
- Three byte mirror pairs and7 compiles: exit0, `task-4-fix2-byte-compile.log`.
- `git diff --check`: exit0, empty `task-4-fix2-diff-check.log`.
- `task-4-fix2-snapshot-diff.log`: complete scoped diff reviewed, AST equality confirms **33 prior test bodies unchanged /35 current**, and changed-file assertion confirms only the3 files listed above. Exit0.

Task6 wording/grade alignment remains untouched, including the #268 explanation previously located at `check-domain-model.py:546`. Serena/Graphify remain unused due to absent opt-in. Source frozen after these checks for the same reviewer's scoped re-review.

## Fix round3/5 — M5-R1 With-item continuation

Status: **DONE**, frozen for scoped re-review. Baseline is coordinator `task-4-fix3-before/`. Only pairing, its byte mirror and the smoke test changed. Source change is one AST type added to the existing module-binding traversal: `_check_property_origins` now expands `ast.withitem` to reach its `optional_vars` binding target. This makes a later `with context as Alias` invalidate the prior module alias before a function's constructor call is analyzed. No new type inference or semantic policy was introduced; compound-body and nested-definition handling is otherwise unchanged.

New literal regression: `CheckerRegression.test_later_with_item_rebinding_invalidates_function_constructor` covers domain Kind and vendor requests.Response aliases used as constructors inside a function, followed by a module With-as binding. Both require a #557 candidate and no #557 violation.

Commands and evidence:

- RED: `python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_later_with_item_rebinding_invalidates_function_constructor` — exit1, **1 test /2 assertion failures**, `task-4-fix3-red.log`.
- Focused GREEN: `python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_later_with_item_rebinding_invalidates_function_constructor CheckerRegression.test_later_module_compound_rebinding_invalidates_function_constructor CheckerRegression.test_nested_definition_bindings_do_not_rebind_module_constructor_alias CheckerRegression.test_initial_static_module_alias_preserves_origin_but_rebinding_does_not` — exit0, **4 tests OK**, `task-4-fix3-focused-green.log`.
- Full smoke: `python3 -B workspace/tools/field_report_checker_smoke.py` — exit0, **36 tests OK**, `task-4-fix3-smoke.log`. One covering run after final source change.
- Existing temporary-copy fixture harness restricted to pairing: exit0, **4/4 expected exits** (good0, bad_rules2, skeleton_placeholder0, invocation1), `task-4-fix3-fixtures.log`. Unchanged context/domain fixture evidence was reused.
- Three byte mirror pairs and7 `compile` checks: exit0, `task-4-fix3-byte-compile.log`.
- `git diff --check`: exit0, empty `task-4-fix3-diff-check.log`.
- Scoped snapshot diff/self-review: exit0, `task-4-fix3-snapshot-diff.log`; **35 prior test bodies preserved /36 current**, only the3 intended files differ. The source diff is exactly the `ast.withitem` traversal addition plus its byte mirror, and the test diff adds one method.

No norms, F20, unrelated suite, primary/user-project work, Git mutation or subagents. Task6 wording/grade ownership remains unchanged. Serena/Graphify omitted because there is no worktree opt-in. Source frozen for the next scoped re-review.
