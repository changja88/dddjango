### Spec Compliance

- ❌ Issues found: cache-only exclusion is incomplete in downstream consumers. Direct and snapshot checking disagree for a cache-only usecase containing a `validation/` directory (M1), and cache-only names still affect candidate diagnostics (M2).
- ✅ All 16 owned paths have Task5 hunks: `checker_target.py`, `check-layer-skeleton.py`, `check-port-adapter-pairing.py`, `check-domain-model.py`, `check-usecase-dto-placement.py`, `check-context-isolation.py`, `registry_gate.py`, their seven Codex byte mirrors, and both smoke files. The package's before/current SHA pairs and `task-5-scope.log:1` cover the declared ownership; the diff contains no removal or rewriting of prior test methods. `task-5-scope.log:17` reports all prior 36 field-smoke AST bodies preserved and three added.
- ✅ Actual #642 emission and `PROMO_PART_MIN_LINES` are removed; `_phys_lines`, #638/#639/#640/#641/#643, and the >200 nonblank physical-line #644 boundary remain (`dddjango/scripts/check-layer-skeleton.py:91`, `:137`). Normative retirement belongs to Task6; no Task6 or F4-20 change is present in this package.
- ⚠️ Repository-wide mutation absence and later normative/final audit gates cannot be established from an owned-file package. No broader audit or Git inspection was performed.

### Strengths

- `dddjango/scripts/checker_target.py:33` centralizes the conservative filesystem predicate without Git or third-party dependencies. Real and hidden files, symlinks, no-cache empty directories, and observed I/O failures prevent exclusion; nested cache traces and empty sibling directories are supported. `workspace/tools/field_report_checker_smoke.py:666` exercises these positive and negative boundaries.
- `dddjango/scripts/check-layer-skeleton.py:237` retains fixed-path checks before the optional-instance filter at `:272`. `dddjango/scripts/registry_gate.py:119` independently retains fixed/reappearing directory and promoted-file precedence, discovers optional paths before copy ignores strip the evidence, and limits omission to exact source-relative paths in `:166`. Original-tree deletion and pre-gate removal changes are absent.
- Domain aggregates/application areas (`check-domain-model.py:172`, `:220`), capability/bypass and adapter-family enumeration (`check-port-adapter-pairing.py:187`, `:317`, `:709`, `:884`, `:902`, `:923`), DTO areas/usecases/direct entry (`check-usecase-dto-placement.py:286`, `:304`, `:316`, `:331`), and OHS instances (`check-context-isolation.py:352`) use the shared predicate at their main enumeration boundaries. Matching mirror hunks have identical current SHA256 values.
- Tests use actual checker subprocesses and the actual registry gate, including source/empty-init contrasts and original path/byte-map preservation (`workspace/tools/field_report_checker_smoke.py:700`; `workspace/tools/registry_gate_smoke.py:256`). Fixed parents, promoted realizations, unrelated parents, and nested application containers are separately exercised (`registry_gate_smoke.py:295`, `:324`).
- Existing evidence was readable: `task-5-red-direct.log:1`, `task-5-red-snapshot.log:1`, and `task-5-red-nested.log:1` show expected RED results; `task-5-green-direct.log:1` records 39/39, `task-5-green-registry.log:1` records three new tests plus 33/33 existing cases, and `task-5-green-fixtures.log:1` records 19/19 covering fixture exits with unchanged expectations. No unexpected warnings were present. These suites were not rerun.

### Issues

#### Critical / B (Must Fix)

- None found in Task5.

#### Important / M (Should Fix)

- **M1 — Cache-only usecases are re-entered by the recursive validation-folder check.** `dddjango/scripts/check-usecase-dto-placement.py:293` scans all of `application_layer` even after optional areas/usecases have been excluded. A real directory named `validation` or `validators` below an excluded instance still emits #183 at `:297`. The identical Codex mirror has the same defect. Focused scratch reproduction copied `skeleton/good_bc`, added only `application/orders/application_layer/order/vanished/validation/__pycache__/old.pyc`, and compared the direct DTO CLI with that CLI on `_snapshot_current` output: the predicate returned **True**, direct returned **2 with #183**, and snapshot returned **0 with the instance absent**. This is a supported cache-only tree, including the brief's allowed empty/nested directory structure, so a deleted usecase still blocks direct checking. Make recursive checks respect exclusion of the owning optional area/usecase, retaining validation diagnostics whenever real content establishes the instance. Add this direct/snapshot contrast to the existing regression tests.

- **M2 — Cache-only aggregate/usecase names still participate in semantic name comparisons.** `dddjango/scripts/check-usecase-dto-placement.py:674` and `dddjango/scripts/check-context-isolation.py:1286` collect aggregate names without the predicate, although their downstream #191 (`DTO :353`) and #151 (`context :359`) consumers affect real usecases/services. `dddjango/scripts/check-domain-model.py:1072` likewise collects usecase names without excluding cache-only areas/usecases for #565. Their Codex mirrors are equally affected. A separate focused scratch reproduction added only `domain_layer/place_order/__pycache__/old.pyc` to `skeleton/good_bc`: the direct DTO CLI emitted **[ⓓ#191] for the existing real `place_order` usecase**, while the same CLI on `_snapshot_current` output emitted no #191; both exits were 0. Thus the retired instance still changes reviewer input on direct execution. Filter these name sets at their optional-instance boundaries, preserving real/empty-instance names. Cover the confirmed #191 contrast and analogous #151/#565 consumers; the latter two are source-established risks, not claimed executed reproductions. This is an explicit direct/snapshot consistency requirement, even though these candidate channels do not change exit status.

#### Minor / m (Nice to Have)

- None beyond the required fixes above.

### Checks and Scope

- Read the full 1,448-line Task5 package once. Additional source reads were limited to named risks: the skeleton `_check_level` function was cut off in the hunk and was completed to verify fixed/promoted precedence; `standard_tree.ROWS` was read to check the snapshot walk's fixed/optional boundary; directory/name consumers in the five affected checker families were searched and narrowly inspected to test whether excluded instances could still influence direct results. Pairing's remaining aggregate-name set is passed through but has no observed consumer in the current adapter-family implementation, so it is not reported as a defect.
- Ran only the two focused temporary-copy reproductions described in M1/M2. No green suite, package-wide verification, Git command, source/test edit, or subagent dispatch was performed. The only checkout write is this review report.
- Serena/Graphify were not loaded or used because this worktree has no opt-in.

### Assessment

**Task quality: Needs fixes.** The shared predicate, fixed-path boundary, byte mirrors, and #642 removal are well constrained and have useful behavior tests. Two remaining downstream-consumer paths violate the promised direct/snapshot equivalence, including a reproduced blocking false positive, so Task5 should remain at its current gate until those are repaired.

### Fix1 Scoped Re-review — Spec Compliance

- ✅ **Spec compliant for Task5 after Fix1; M1 and M2 are closed.** This assessment supersedes the preceding Needs fixes verdict. The complete 475-line Fix1 package was reviewed against those two findings; no new correctness issue was found in this repair diff.
- ✅ **M1 closed:** `dddjango/scripts/check-usecase-dto-placement.py:285` collects cache-only optional area/usecase owners; the recursive scan at `:300` skips an excluded owner and its descendants. The explicit `port` branch remains outside optional collection. Real files and empty init files prevent collection through the unchanged shared predicate, so validation diagnostics remain for actual instances.
- ✅ **M2 closed:** DTO aggregate names (`check-usecase-dto-placement.py:682`), OHS aggregate names (`check-context-isolation.py:1286`), and both area/usecase levels of the #565 name set (`check-domain-model.py:1072`) now filter cache-only instances. The latter also excludes `__pycache__` itself. Each affected canonical script has the corresponding identical Codex mirror hunk.
- ✅ Exactly seven files changed in Fix1: the three canonical scripts, their three mirrors, and the field smoke file. The package's unchanged SHA pairs preserve predicate, skeleton/#642 work, pairing, registry implementation, and registry smoke. Task6 normative retirement remains deferred.

### Fix1 Strengths and Evidence

- `workspace/tools/field_report_checker_smoke.py:740` tests validation and validators at both owner levels, with literal expected exits and #183 presence/absence for each direct/snapshot channel. Empty init and real-source controls verify that the repair does not suppress real-instance violations.
- `workspace/tools/field_report_checker_smoke.py:762` now executes all three candidate channels, including #151 and #565, with cache-only, empty-init, real-source, and cache-free empty-instance contrasts. Independent expected candidate counts prevent equal but wrong outputs from passing the direct/snapshot comparison.
- Read `task-5-fix1-red.log`: eight expected direct-channel assertion failures cover both M1 owner levels/names and all M2 candidate paths. Read existing green logs: focused 2/2, field 41/41, snapshot 3/3, and 11/11 relevant fixture exits. `task-5-fix1-scope.log` confirms unchanged prior 39 test AST bodies, seven exact byte mirrors, and unchanged registry source/smoke. Outputs contain no unexpected warnings. The unchanged registry smoke's prior 33/33 evidence remains applicable alongside the new snapshot covering run.

### Fix1 Residual Issues

- **B:** None.
- **M:** None.
- **m:** None.

### Fix1 Assessment

**Task quality: Approved.** The repair applies the existing predicate at the missed owners/name consumers without changing its contract or fixed-path policy. Both original findings have implementation and behavior evidence, and no new breakage was identified in the scoped diff.

- Review remained limited to Fix1 and existing evidence; no suite reruns, extra experiments, broader source audit, source/test/Git mutations, or subagents. Only this report was appended. Serena/Graphify remain unused because opt-in is absent.
