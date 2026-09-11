# Whole-review combined fix wave — Task7 Step2

Status: **DONE**, source frozen for coordinator's independent scoped review. This is completion of the assigned fix wave, not whole-implementation approval or final audit completion.

Worktree: `/Users/hyun/.cache/dddjango-field4-followup-20260911`. Baseline: `whole-fix-before/manifest.json` (54 paths). Read `whole-fix-brief.md` first, both complete A/B finding sections, and `docs/DEVELOPMENT.md`. Applied systematic-debugging, receiving-code-review, test-driven-development (including writing-good-tests), and verification-before-completion. No new policy choice was needed.

## Dispositions and behavioral evidence

| Finding | Root cause and minimal correction | RED and final evidence | Disposition |
|---|---|---|---|
| A-M1 / F4-1 | Module marker traversal skipped direct `pytestmark` attribute calls. Treat those calls as unsupported final-state evidence, preserve bytes, and report S5; no test-module execution is added. | New marker test: append, pop, conditional extend × empty/replacement marker lists. In RED, the three empty-list cases failed byte preservation; the three same-slow-list cases preserved bytes but failed the method/S5-reason assertion. The CLI failed the method-reason assertion, while its exit 4 assertion already passed. GREEN preserves source and copy, materialized=[], and reports the S5 method reason. Actual CLI on the synthetic conditional-call fixture returns 4 (zero materialization), and check-report accepts the S5 report with exit 0. | Addressed |
| A-M2 / F4-9 | Fixed kwargs annotations skipped consumption graph. Register the kwargs annotation and binding as an active source in the existing finite graph; preserve fixed policy only while status stays allow. Unknown sig-star Any gets candidate #645, known consumption falls through to ordinary #645. | Real checker CLI: business read/comparison/call and alias consumption produce #645 violation; unknown(kwargs) produces #645 info; forwarding and bodyless controls produce no #645/#647. Independent #646 remains in all these cases; JSON #650 control still fires. RED had no #645 for all three bad/unknown variants. | Addressed |
| A-M3 / F4-10 | Module import environment kept imported builder after local function/async function/class replaced it. Definitions now invalidate that name's import origin. | Three definitions lose false proof and return #153 candidate, no #153 violation. Real builder + execute and uncalled nested definitions retain their prior clean #153 behavior. All three shadow forms failed RED. | Addressed |
| A-M4 / F4-14 | Source-ordered UoW environment omitted ClassDef rebinding. The defined class name now clears stale UoW origin. | Local class shadow makes sequential different-aggregate writes a #546 candidate, never confirmed violation. Standard sequential UoWs, other class, and uncalled nested class controls remain clean for #546. Class-shadow case failed RED. | Addressed |
| B-M1 / F4-1 | Candidate gating saw only the initial annotation spelling, losing named-UoW evidence after supported aliases. Thread an optional referenced-name collector through the existing type resolver; candidate gating considers the original spelling and resolved traversal names only when unresolved issues exist. DTO consumers retain the same two-value resolution contract. | Direct, simple alias, chained alias, and supported list alias all retain candidate #197 for read-only/uow=none. Unrelated P alias, int alias, proven local non-UoW class, and all write controls stay clean. Three read-only aliases failed RED. | Addressed |
| B-m1 / F4-16 | Four current descriptions still included retired #642 in a range. Changed exactly four ranges to #638~#641·#643 in canonical and byte mirror. | Complete scoped diff inspection; no behavioral test added for prose. Existing skeleton lanes and smoke controls still pass. | Addressed |

No finding remains open within this fix wave.

## Commands and raw logs

All commands ran in the worktree above. Raw logs below are relative to this report directory. The runner logs include expected nonzero checker/CLI exits as assertions; each final harness process itself exited 0. No passing suite was repeated after completion; each relevant full suite ran once after the last product-source edit.

RED before product edits (actual behavioral assertion failures, not harness errors):

```sh
python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_marker_method_mutations_preserve_bytes_and_report_s5 FieldReportTest.test_unresolved_named_uow_alias_keeps_declaration_candidate
python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_admin_kwargs_actual_consumption_and_unknown_escape CheckerRegression.test_ohs_module_definitions_invalidate_imported_builder CheckerRegression.test_uow_module_class_shadow_keeps_unknown_region_candidate
```

- `whole-fix-red-pregate.log`: exit 1; 2 tests, 10 failed assertions (3 empty-list marker byte-preservation cases + 3 same-slow-list method/S5-reason cases + 1 CLI method-reason case + 3 named-UoW alias cases). The CLI exit 4 assertion already passed in RED.
- `whole-fix-red-checkers.log`: exit 1; 3 tests, 7 failed assertions (3 kwargs cases + 3 builder shadows + 1 UoW class shadow).

One targeted GREEN run after each product correction, in this order:

```sh
python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_marker_method_mutations_preserve_bytes_and_report_s5
python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_unresolved_named_uow_alias_keeps_declaration_candidate
python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_admin_kwargs_actual_consumption_and_unknown_escape
python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_ohs_module_definitions_invalidate_imported_builder
python3 -B workspace/tools/field_report_checker_smoke.py CheckerRegression.test_uow_module_class_shadow_keeps_unknown_region_candidate
```

Each exited 0 / 1 test OK. Raw logs respectively: `whole-fix-green-marker.log`, `whole-fix-green-declaration.log`, `whole-fix-green-admin.log`, `whole-fix-green-ohs.log`, `whole-fix-green-uow.log`.

Final covering runs after all product edits and byte copies:

```sh
python3 -B workspace/tools/pregate_field_report_smoke.py
python3 -B workspace/tools/field_report_checker_smoke.py
PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 python3 -B workspace/tools/pregate_fixture_run.py
```

| Raw log | Fresh final result |
|---|---|
| `whole-fix-full-pregate.log` | exit 0; 38 tests, OK; includes marker ordering/subscript mutation, final generated-method AST ranges, exact raw finding joins, S1 partition, declaration/actual CLI/report boundaries |
| `whole-fix-full-checkers.log` | exit 0; 49 tests, OK; includes lexical shared/nested UoW and aggregate type counts, admin origins/helpers/consumption/#646/#650, closed Enum and contract origin opposites |
| `whole-fix-pregate-fixtures.log` | exit 0; fixture runner PASS: modes, 15 fixtures + E-series six steps + units, import existence 0/5/5, enforce cases and 14 check-report steps all match |
| `whole-fix-checker-fixtures.log` | exit 0; 20/20 selected existing lanes; full child command/stdout/stderr/expected/actual recorded |

Exact scoped fixture invocation (uses the existing matrix definitions, runs only copied fixtures, isolates output sinks):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'LANES'
import sys, os, shutil, subprocess, tempfile
from pathlib import Path
sys.path.insert(0, 'workspace/tools')
import fixture_matrix as fm
selected={'check-context-isolation.py','check-domain-model.py','check-public-surface-annotation.py','check-layer-skeleton.py','check-test-config.py'}
cases=[c for c in fm.build_cases() if Path(c[1][1]).name in selected]
for label,cmd,rel,want in cases:
 with tempfile.TemporaryDirectory(prefix='whole-fix-lane-') as td:
  dest=Path(td)/'fixture'; shutil.copytree(cmd[2],dest)
  run_cmd=[*cmd[:2],str(dest),*cmd[3:]]
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('DJR_FINDINGS_JSON',None);env['DJR_VIOLATIONS_DIR']=str(Path(td)/'violations')
  run=subprocess.run(run_cmd,capture_output=True,text=True,env=env)
  print('$ '+' '.join(run_cmd));print(run.stdout,end='');print(run.stderr,end='')
  print(f'{label}: expected={want} actual={run.returncode}')
  assert run.returncode==want,(label,run.returncode,want)
print(f'PASS {len(cases)}/{len(cases)} scoped existing lanes')
LANES
```

20 lanes comprise skeleton five shapes; context-isolation/public-surface/domain-model/test-config good and bad pairs; test-config-entrance good/bad; and those five checkers' invalid-target invocation controls. Synthetic temporary repositories created by the existing smoke/fixture harnesses use their existing scratch-only Git setup; no Git mutation was performed in this worktree or primary.

## Self-review and preservation

Read the entire canonical fix diff (`whole-fix.diff`), including all five product files and both smoke additions. Canonical scripts were copied byte-for-byte to Codex after their edits. Final scope proof is `whole-fix-preservation.json`; final hashes for all 54 baseline entries are `whole-fix-final-hashes.json`.

- All 54 snapshot-copy hashes match the supplied manifest.
- Exactly the 12 allowed product/test paths changed. Remaining 42 frozen paths retain their hashes, including all normative/TTL/rulepack/current-document files and other scripts/tests.
- All 5 affected script pairs are byte-identical.
- AST-addressed source-segment comparison preserves all 44 prior methods in pregate smoke and all 63 prior methods in checker smoke (107 test/helper methods). Only 2 + 3 new regression methods were added. No golden expectation or prior test body was relaxed.
- The four skeleton prose replacements are the only changes in that file; no executable behavior changes there.
- The collector is opt-in to declaration #197 analysis; existing DTO resolution result shape and decisions are unchanged. It collects symbolic type spellings, not arbitrary unresolved diagnostic text or module-path substrings.
- Marker policy remains bounded static AST analysis and explicitly S5 for direct method calls. It neither executes user test modules nor claims the final marker list was materialized in such cases.
- Rebinding fixes clear the current name only and do not descend into uncalled nested scopes. No global transaction identity or helper-execution solver was added.

## Final hashes

Each canonical script hash below is also the hash of its matching `codex-dddjango/skills/dddjango/scripts/` file. The JSON companion records each path separately.

| Source path | SHA-256 |
|---|---|
| `dddjango/scripts/design_pregate.py` | `7a16f052b671c8dc6a605293aae3a0786d3daa1a7e71c14c4931fc5020d099fe` |
| `dddjango/scripts/check-public-surface-annotation.py` | `b94b4101403d59926bdbdbe3aa64595afcb1547330215cd4e33cb4128555954b` |
| `dddjango/scripts/check-context-isolation.py` | `bb68853338db1326575c954040bc8bdb1006440a855036e4fac3b8f8838389b5` |
| `dddjango/scripts/check-domain-model.py` | `ded715d2026c7556b7ad35a125951eadc7239b9ff04913d52912e2987592e3a4` |
| `dddjango/scripts/check-layer-skeleton.py` | `32810abb897f3dfc580c2880457fe894a68ea5e080ec6e71d4fef9b814425924` |
| `workspace/tools/pregate_field_report_smoke.py` | `ec2ec71b40f855587a93abac85e40091e944fa3a510a6c89f470a79c9cc56604` |
| `workspace/tools/field_report_checker_smoke.py` | `c8b3eed3de9b63cb50dbc715dba123a55884a48ae3188fd6934739436bf7989b` |

## Limits and handoff

The observed results establish these regression cases and their covering harness boundaries. S1 remains explicitly unverified generated-body evidence; unknown calls/provenance and unsupported dynamic scopes remain candidates/S5 rather than pass proofs. Marker aliases and arbitrary module execution are not simulated. Same-type transaction instance identity and arbitrary helper execution remain outside the bounded checker.

No independent fix review, full `make verify`, seal, final audit, commit/release, F20 change, original-report cleanup, or primary/master edit was performed. Those are coordinator-owned later steps. No subagents were created. Serena/Graphify were not searched, loaded, initialized, or called because the worktree has no opt-in and the brief prohibits them.

Source and tests are now frozen at the attached hashes for independent review. Report/evidence files are confined to this SDD directory.
