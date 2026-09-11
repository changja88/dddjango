# Task 2 implementation report

Status: DONE. Implementation and tests frozen for independent review. Worktree: `/Users/hyun/.cache/dddjango-field4-followup-20260911`.

## Scope and changed files

Only these four owned product/test files changed relative to `task-2-before/`:

- `dddjango/scripts/design_pregate.py`
- `codex-dddjango/skills/dddjango/scripts/design_pregate.py` — byte-identical mirror
- `workspace/tools/pregate_field_report_smoke.py`
- `workspace/tools/pregate_fixture_run.py`

Task 1 declaration/type/effect/marker behavior is preserved. No G2 checker, rule registry, ontology, norms, primary checkout, actual user project, seal, version, commit, or release changed. SDD logs and this report are the authorized execution evidence. Serena/Graphify were omitted because neither opt-in marker exists. No subagents were used. Applicable TDD and verification-before-completion guidance was read.

## Behavior and exported interfaces

`materialize(...) -> MaterializationReport` preserves `materialized`, `already_built`, `unsimulated`, and `pruned_dirs`, and adds:

```python
generated_methods: dict[str, list[GeneratedMethod]]
# Each GeneratedMethod:
{"owner": str, "method": str, "lineno": int, "end_lineno": int}
```

Paths are plan-relative file paths. For new files, ranges come from `ast.parse(stub)` only after successful render/compile. For a successful OHS function append, ranges come from the newly rendered combined AST, retaining only new module function names absent from the original module; existing functions/classes are never labeled generated. A class method's owner is its class name (nested classes use dotted owners); a module function's owner is `""`. Method names are exact def names. `lineno`/`end_lineno` are Python AST ranges of the final rendered text, including the definition line. Ordinary update and marker-only update do not invent method provenance from stub-looking text. The coverage test checks actual rendered source ranges and original-byte preservation.

`run_gate(copy, scratch, python_bin) -> GateResult` runs the actual `registry_gate.py` subprocess and returns a TypedDict:

```python
{
    "raw_exit": int,
    "raw_stdout": str,
    "attributed_lines": list[str],
    "records": list[dict],
    "unmatched_lines": list[str],
    "candidate_lines": list[str],
    "candidate_records": list[dict],
}
```

Original sidecar records are transported without reducing or replacing their fields, including candidate records for Task 3. The registry legitimately omits both candidate keys when there are no candidates; both become empty lists. A partial candidate pair, missing/wrong-type mandatory material, unreadable/malformed JSON, non-0/2 raw exit, or raw exit 2 without attributable findings raises `RunError`. Missing records for an individual key never justify deferral.

`partition_generated_findings(gate_result, generated_methods) -> (retained, deferred)` uses the complete normalized attribution key: checker + `registry._normalize(findings.line_of_record(record), ())`. It never groups by `_stable_id` or rule/path. The sidecar has already normalized snapshot prefixes in `record.file`. Every raw record in a matching cohort must be `#376` and have a numeric suffix in `record.file` locating it inside a generated class `after_commit`. No line is recovered from `:N` or `file_raw`. A matching cohort containing another location, an unknown location, no record, or an unmatched key is retained. An unjoinable raw record conservatively prevents deferral for that result instead of being silently discarded or assigned by rule/path. `#566` is always retained.

`retained` contains the original normalized attribution strings. `deferred` contains explicit strings beginning `S1: 생성한 after_commit 본문 — on_commit 구현 미검증 · ` followed by the original attribution string. The ordinary stable-ID/disposition contract is unchanged. Reports and stdout separately show raw registry exit/count, retained count, and generated S1-unverified count; `--check-report` preserves and displays S1 count. Final pregate exit uses retained findings plus Task 1 confirmed declarations, while raw RunError remains blocking.

Execution mode appears on stdout and full/stub reports as `초기 예보(기준선 기본 HEAD)` or `명시 재예보(--base X)`. Baseline-existing add and baseline-absent/overlay-existing add explain different causes. Missing update explains initial forecast and explicit reforecast purposes. The 12 existing exit combinations and realized-add lifting stay unchanged. File-plan scope guidance identifies approved product paths and excludes coordinator records/gate reports/temp logs from plan material, without a docs/non-Python blanket ban or filename-driven deletion.

## TDD and execution evidence

All commands below ran in the worktree above. Logs are in this report's directory.

1. Initial RED command:

   `python3 -B workspace/tools/pregate_field_report_smoke.py > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-red.log 2>&1`

   RED: 30 tests, 6 failures and 8 missing-interface errors. The shell wrapper subsequently attempted to assign zsh's read-only `status` name and exited 1 before its tail command; no data was lost, and the unittest log contains its RED summary. This first test draft also exposed an imperfect minimal fixture and the anchor-policy mismatch described below, which were corrected before implementation.

2. Corrected actual CLI RED command:

   `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_generated_uow_cli_defers_only_generated_body_and_preserves_original FieldReportTest.test_real_uow_cli_retains_bad_body_and_missing_robust_even_stub_text > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-cli-red.log 2>&1`

   Exit 1: 2 tests, 1 failure + 1 missing structured-interface error. Generated pregate fixture now had exactly one raw finding (`#376`), returned 2, and failed the requested expected-0 behavior. This is the precise behavior RED before implementation.

3. Execution-mode RED command:

   ```sh
   python3 -B -c 'import sys,tempfile; from pathlib import Path; sys.path.insert(0,"workspace/tools"); from pregate_fixture_run import _run_execution_modes_bundle; t=tempfile.TemporaryDirectory(); failures=[]; _run_execution_modes_bundle(Path(t.name),failures); print("\n".join(failures)); sys.exit(bool(failures))' > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-modes-red.log 2>&1
   ```

   Exit 1. All 12 expected exits already held, while mode/cause/file-plan guidance assertions failed. This isolated the required diagnostic improvement from existing exit policy.

4. First implementation attempt:

   `python3 -B workspace/tools/pregate_field_report_smoke.py > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-green-attempt1.log 2>&1`

   Exit 1: 30 tests, 2 failures. One exposed an unjoinable missing-line raw record being dropped while another record deferred; implementation now retains conservatively. The other was a combined declaration fixture missing its required class symbols row; that fixture was corrected without changing declaration policy.

5. Focused GREEN:

   `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_generated_partition_uses_full_normalized_cohort_and_all_raw_locations FieldReportTest.test_generated_uow_cli_defers_only_generated_body_and_preserves_original FieldReportTest.test_real_uow_cli_retains_bad_body_and_missing_robust_even_stub_text > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-targeted-green.log 2>&1`

   Exit 0: 3 tests. Generated-only actual pregate exit 0 with raw registry exit 2 / raw attributable 1 / retained 0 / S1 1; actual check-report exit 0 with S1 1; generated S1 plus confirmed declaration actual pregate exit 2. Actual registry CLI retains real `#376` and `#566` records. Ordinary dirty bad update remains pregate legacy / exit 0.

6. Modes GREEN: same exact `-c` command as step 3, redirecting to `task-2-modes-green.log`. Exit 0. Baseline-absent overlay-existing rows: initial add/empty/update = 3/3/3; explicit = 0/0/3. Baseline-present rows: initial and explicit add/empty/update = 3/3/4. Causes, both mode labels, scope guidance, and original source bytes are checked.

7. Required full fixture command:

   `python3 -B workspace/tools/pregate_fixture_run.py > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-fixture-green.log 2>&1`

   Exit 0. PASS includes all previous fixture bundles, E1–E4 and E1′/E2′ lifting, original red-rule sets/counts, import existence, form/skip, report dispositions, plus the 12 new execution-mode CLI cases. This was run once after the implementation became focused-green.

8. Required final smoke command:

   `python3 -B workspace/tools/pregate_field_report_smoke.py > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-smoke-green.log 2>&1`

   Exit 0: 32 tests, 47.310 seconds. This includes Task 1 regression coverage, actual CLI S1/declaration tests, generated range/source-byte provenance, full normalized cohorts, and mandatory/optional sidecar transport.

9. Self-review added one final subcase to the existing cohort test: `record.file` has `:N` while `file_raw` has a numeric line. This makes explicit that neither normalized placeholders nor raw backup paths may supply location proof. No implementation changed, and no broad suite was repeated:

   `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_generated_partition_uses_full_normalized_cohort_and_all_raw_locations > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-raw-location-green.log 2>&1`

   Exit 0: 1 test, all subcases. Total test methods remain 32.

10. Static/byte verification (`task-2-static-green.log`), exit 0:

    ```python
    # Executed with python3 -B - via stdin, output redirected to task-2-static-green.log.
    from pathlib import Path
    import subprocess
    paths = ['dddjango/scripts/design_pregate.py',
             'codex-dddjango/skills/dddjango/scripts/design_pregate.py',
             'workspace/tools/pregate_field_report_smoke.py',
             'workspace/tools/pregate_fixture_run.py']
    for path in paths:
        compile(Path(path).read_bytes(), path, 'exec')
        print('compile PASS', path)
    assert Path(paths[0]).read_bytes() == Path(paths[1]).read_bytes()
    print('byte mirror PASS')
    run = subprocess.run(['git', 'diff', '--check'], capture_output=True, text=True)
    print('git diff --check exit', run.returncode)
    print(run.stdout + run.stderr)
    raise SystemExit(run.returncode)
    ```

    All four compiled; byte mirror matched; `git diff --check` exit 0. After the final test-only subcase, that smoke file's `compile(...)` and `git diff --check` were repeated and appended, both exit 0. No bytecode files were generated by these checks.

## Self-review and named remaining concerns

No known blocking implementation defect remains. Reviewed the full canonical script diff against `task-2-before/dddjango/scripts/design_pregate.py`, rather than attributing Task 1's pre-existing work to this task. Confirmed that `_stable_id`, registry Findings schema/identity, actual G2 checker rules, declaration counts, update rendering restrictions, and baseline/lifting order are unchanged.

- **Anchor boundary (approved fixture clarification):** Pregate anchors its baseline plus dirty overlay before materialization. An unchanged/dirty real bad update body is therefore legacy, not newly attributable; demanding pregate exit 2 solely for it would change anchoring. Root explicitly approved preserving this policy. The real-body counterexample runs actual registry CLI against a clean git anchor with a bad current mutation, consumes all original introduced records through the postprocessor, and proves `#376`/`#566` remain retained. A companion actual pregate invocation proves ordinary dirty update stays legacy/exit 0. No fabricated source attribution was added.
- **Conservative incomplete evidence:** Any raw record that cannot join the normalized attributed keys prevents all deferral for that result. This can retain more findings under inconsistent/raw-unresolved evidence but cannot silently make the gate green.
- **Task 3 boundary:** `generated_methods`, unchanged candidate records, and exact function/method names/ranges are ready for consumption. Annotation S1 processing is not implemented here.
- **#566 and source #197 boundary:** `#566` has no generated-body exception. Task 1's nonstandard direct `execute(uow)` source-#197 probe remains outside this task; no new #197 source filter was introduced.
- **Repository-wide release verification:** No `make verify`, seal reissue, commit, or release was attempted; those are outside this bounded task and remain the coordinator's later approved gate.

## Round 1 independent review fix — M1

Status: DONE; frozen again for scoped re-review. The independent review in `task-2-review.md` identified one important issue (B0/M1/m0): new OHS function ranges were recorded before a subsequent marker update could shift them. This supersedes the earlier no-known-defect conclusion for round 1. The defect was reproduced and corrected without changing any filtering, G2, declaration, or execution-mode policy.

Changes relative to `task-2-fix1-before/` are limited to the canonical pregate, its byte mirror, and one new smoke test. `pregate_fixture_run.py` is unchanged in this fix. Immediately after OHS append, materialization retains only this render's new `(owner, method)` identities. After all marker composition, it collects final AST ranges for exactly those identities. Existing functions cannot become generated. This final-composition timing supersedes the earlier report's OHS range description and is the range source Task 3 should consume.

New regression `test_generated_ranges_follow_final_marker_composition` uses `spec_text` → real `parse_spec` → `materialize`, with an OHS update/new `new_query` and the same file's `[markers: slow]` signals row. It covers both inserted import/marker prefix lines and contraction of a multiline existing marker assignment. It verifies the final AST's exact line range, only `('', 'new_query')` as generated identity, preservation of the existing function body, and original source bytes.

Commands and evidence (all worktree-local):

1. Focused RED:

   `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_generated_ranges_follow_final_marker_composition > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-fix1-red.log 2>&1`

   Exit 1: one test with two failing subcases. Prefix insertion reported `(9, 11)` while final AST was `(11, 13)`; multiline contraction reported `(13, 15)` while final AST was `(11, 13)`.

2. Focused GREEN, same command redirecting to `task-2-fix1-focused-green.log`: exit 0, one test with both subcases passing (0.138 seconds).

3. Required covering smoke:

   `python3 -B workspace/tools/pregate_field_report_smoke.py > .superpowers/sdd/2026-09-11-field-report-4-followup/task-2-fix1-smoke-green.log 2>&1`

   Exit 0: **33 tests passed**, 50.332 seconds. Task 1 and other Task 2 behavior remain covered.

4. Static checks: the same exact four-file `python3 -B -` compile/byte-mirror/`git diff --check` script from item 10 above, redirected to `task-2-fix1-static-green.log`: exit 0. All four compile checks passed, canonical/Codex bytes matched, and diff whitespace check passed. No Git state was changed.

5. Reviewed `diff -u task-2-fix1-before/dddjango/scripts/design_pregate.py dddjango/scripts/design_pregate.py` (exit 1 means the expected diff): only new-identity retention and final-range collection changed. The exact command used the full SDD prefix for the snapshot path.

The previously green full fixture suite is reused as explicitly authorized because this correction only changes provenance timing during combined marker composition; it does not change CLI exit/lifting/report policy. No full fixture rerun, Task 3 work, norms, primary checkout, Git mutation, seal, or release occurred. No known unresolved M1 issue remains; independent scoped re-review is pending. Serena/Graphify remain omitted due to absent opt-in markers.
