# Task 5 implementation report

Status: DONE — implementation and required covering verification complete; source frozen for independent review.

Worktree: `/Users/hyun/.cache/dddjango-field4-followup-20260911`.
Evidence directory: `.superpowers/sdd/2026-09-11-field-report-4-followup` (abbreviated `$E` below).
Baseline: coordinator `task-5-before/` snapshot; Task4 gate APPROVED and prior field smoke 36.

## Ownership and implementation

The 16 owned product/test files are exactly the seven canonical scripts below, their byte mirrors under `codex-dddjango/skills/dddjango/scripts/`, and the two smoke files. Baseline hashes and unchanged prior test bodies are checked in `task-5-scope.log`.

- `dddjango/scripts/checker_target.py`: new public `cache_only_instance(path: Path) -> bool`.
- `dddjango/scripts/check-layer-skeleton.py`: skip that predicate only after a directory is recognized as a valid optional instance slot. Fixed directories/files and promoted file realizations retain their requirements. Remove `PROMO_PART_MIN_LINES` and actual #642 emission; retain `_phys_lines`, #638/#639/#640/#641/#643, and >200 nonblank physical lines as the #644 candidate boundary.
- `dddjango/scripts/check-domain-model.py`: aggregate enumeration and optional application areas exclude cache-only instances; fixed domain children and port remain separately owned.
- `dddjango/scripts/check-usecase-dto-placement.py`: optional areas/usecases and their API-area comparison exclude cache-only instances; `_check_use_case` also guards direct entry.
- `dddjango/scripts/check-context-isolation.py`: OHS service instance enumeration excludes cache-only instances.
- `dddjango/scripts/check-port-adapter-pairing.py`: optional capability/domain-bypass capability and adapter bundle/peer/system enumeration excludes cache-only instances. Fixed port parents and adapter roles remain checked.
- `dddjango/scripts/registry_gate.py`: private `_snapshot_cache_instances(root: Path) -> set[Path]` traverses the existing `standard_tree` BC rows, with fixed-name and promoted-file precedence, and calls the shared predicate on original optional instances. `_snapshot_current(root: Path, dest: Path) -> None` unions these exact relative paths with the existing copy ignore callback before copying. Nested `application/` containers are included, as existing direct checkers support them. No parent removal, no delete from the original tree, no changes to diagnostic identity or pre-gate removal policy.
- `workspace/tools/field_report_checker_smoke.py`: 3 new cache/promotion test methods with table-driven slot and source contrasts.
- `workspace/tools/registry_gate_smoke.py`: 3 new snapshot/gate regression methods; the existing main smoke runs them before its original cases.

`cache_only_instance` uses lstat and directory traversal, never Git. It requires at least one regular `.pyc` or `.pyo` below a real `__pycache__` directory, permits unrelated empty directories, and rejects every other real file, symlink, nonregular file, or observed filesystem read error. An empty `__pycache__` alone is insufficient. The coordinator explicitly confirmed this interpretation during implementation. A `.py` inside `__pycache__` is still a real source file and prevents exclusion.

No subagents, Git mutations/commits/releases, primary-checkout/user-project writes, normative edits, unrelated fixture expectation changes, dependency installs, seals, or transaction-boundary changes were performed. Temporary fixture repositories exercise the real existing Git-based gate, as required by the smoke tests. Read-only `git diff` and `git diff --check` were used. Task6 owns normative #642 retirement and remaining current documentation changes; F4-20 is untouched. Serena/Graphify were not loaded or used because this worktree has no opt-in.

## RED evidence

All commands run from the worktree above. Full redirected outputs are retained under `$E`.

1. `python3 -B workspace/tools/field_report_checker_smoke.py CacheInstanceRegression > $E/task-5-red-direct.log 2>&1`
   - Exit 1; 3 tests, 7 expected assertion failures. The preimplementation direct CLIs emitted #299/#256 for cache aggregates, #193/#570/#569 for cache usecases, #152 for cache OHS, #218/#225 for cache capabilities, and #488 for cache adapter packages. The proposed predicate was absent and short promoted parts still emitted #642. Real/empty-file and empty-instance contrasts retained their expected violations.
2. `PYTHONPATH=workspace/tools python3 -B -m unittest registry_gate_smoke.CacheSnapshotRegression -v > $E/task-5-red-snapshot.log 2>&1`
   - Exit 1; 2 tests, 1 expected assertion failure. The actual registry gate attributed 35 violations to cache-only instances and returned 2 where 0 was required. The fixed/hidden/empty boundary control already passed.
3. Self-review found that direct checkers support nested application containers, so their snapshot equivalence was tested before adding that support:
   `PYTHONPATH=workspace/tools python3 -B -m unittest registry_gate_smoke.CacheSnapshotRegression.test_nested_application_container_uses_same_optional_slots_as_direct_checker -v > $E/task-5-red-nested.log 2>&1`
   - Exit 1; expected `snapshot/src/application/orders/domain_layer/vanished` to be absent, but the first implementation retained it. The snapshot discovery was then extended to the existing nested-container contract.

## GREEN evidence

- Focused direct run: `python3 -B workspace/tools/field_report_checker_smoke.py CacheInstanceRegression > $E/task-5-green-direct-focused.log 2>&1` — exit 0, 3/3. This run preceded additional edge assertions; the final full run below covers those additions.
- Focused snapshot run: `PYTHONPATH=workspace/tools python3 -B -m unittest registry_gate_smoke.CacheSnapshotRegression -v > $E/task-5-green-snapshot-focused.log 2>&1` — exit 0, 2/2 before the nested-container regression was added.
- Final field smoke: `python3 -B workspace/tools/field_report_checker_smoke.py > $E/task-5-green-direct.log 2>&1` — exit 0, **39/39**. Prior 36 test method AST bodies are unchanged, and 3 tests were added. Tests cover direct/nested cache, no-cache empty directories, empty cache directories, untracked source/empty init/hidden files, source inside cache, loose `.pyc`, links, directory/file read errors, fixed-skeleton preservation, six checker-slot contrasts, 1/49/201-line promoted parts, and preserved #638/#639/#640/#641/#643/#644 behavior.
- Final registry smoke: `python3 -B workspace/tools/registry_gate_smoke.py > $E/task-5-green-registry.log 2>&1` — exit 0, **3/3 new snapshot tests and 33/33 existing registry cases passed** (`케이스 33 · 일치 33 · 불일치 0`). The actual gate returns 0 for cache-only instances and 2 after empty init files establish real instances; all requested domain/DTO/OHS diagnostics plus pairing diagnostics are asserted. Original file path/byte maps are compared after gate/snapshot execution. Required fixed parents, hidden-file instances, empty instances, promoted file realizations, BC/layer parents, and unrelated same-named paths remain present in snapshots.

The covering fixture run uses the repository's literal `fixture_matrix.build_cases()` expectations, runs only the five modified checker families, and copies each fixture to a temporary target. Exact command:

```sh
PYTHONPATH=workspace/tools python3 -B - <<'PY' > .superpowers/sdd/2026-09-11-field-report-4-followup/task-5-green-fixtures.log 2>&1
from pathlib import Path
import fixture_matrix as matrix
import os, shutil, subprocess, tempfile
owned = {'check-layer-skeleton.py', 'check-port-adapter-pairing.py', 'check-domain-model.py', 'check-usecase-dto-placement.py', 'check-context-isolation.py'}
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
env.pop('DJR_FINDINGS_JSON', None)
count = 0
for label, argv, fixture, expected in matrix.build_cases():
    if Path(argv[1]).name not in owned or label.startswith('invocation/'):
        continue
    with tempfile.TemporaryDirectory(prefix='task5-fixture-') as td:
        source = Path(argv[2])
        target = Path(td) / 'fixture'
        shutil.copytree(source, target)
        command = [argv[0], '-B', argv[1], str(target), *argv[3:]]
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        print(f'{label}: expected={expected} actual={result.returncode}')
        if result.returncode != expected:
            print(result.stdout + result.stderr)
            raise SystemExit(1)
        count += 1
print(f'{count}/{count} covering fixture exits matched; expectations unchanged')
PY
```

Result: exit 0, **19/19** covering fixture exits matched, including `skeleton/good_promoted` exit 0 and `skeleton/bad_promoted` exit 2. No fixture expectations changed.

## Self-review and limits

- Reviewed the snapshot-relative full diff, retained in `task-5-self-review.diff`; baseline hash/syntax/prior-test-body and mirror evidence is in `task-5-scope.log`. Read-only `git diff --check` exited 0 with no output.
- Every one of the 16 paths matches a coordinator-owned baseline entry, all parse successfully, and the seven mirror pairs are byte-identical. No old field smoke method body was changed.
- Filesystem failure tests simulate permission errors at `Path.iterdir` and `Path.open`; the return value of the real predicate is asserted. They do not claim a platform-specific chmod test under privileged execution.
- Cache classification is a conservative observation of the present filesystem, not an atomic filesystem snapshot. Concurrent external changes between scanning and copying are not newly synchronized.
- Snapshot path ownership comes from existing standard-tree rows, not a global empty-folder filter. Framework optional content and arbitrary nonstandard folders are outside this BC-instance change. Cache file contents are not validated as bytecode; presence/type/location and readability establish the trace.
- No whole-project `make verify` was run in this bounded implementation task; the required Task5 direct/registry smoke and covering fixtures are the evidence here. The coordinator's later normative/final audit gates remain required.

Source frozen after the owned changes and byte mirrors. Independent review is the next gate; no completion of Task6 or the overall followup is implied.

Exact static/baseline/mirror verification command (already executed; exit 0):

```sh
python3 -B - <<'PY' > .superpowers/sdd/2026-09-11-field-report-4-followup/task-5-scope.log
from pathlib import Path
import ast, hashlib, json
base = Path('.superpowers/sdd/2026-09-11-field-report-4-followup/task-5-before')
manifest = json.loads((base / 'manifest.json').read_text())
for name, old_hash in manifest.items():
    before = base / name
    current = Path(name)
    assert hashlib.sha256(before.read_bytes()).hexdigest() == old_hash
    ast.parse(current.read_text())
    print(f'{name}: baseline valid; syntax valid; changed={before.read_bytes() != current.read_bytes()}')
for name in ('workspace/tools/field_report_checker_smoke.py', 'workspace/tools/registry_gate_smoke.py'):
    def tests(path):
        tree = ast.parse(path.read_text())
        return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
    old, new = tests(base / name), tests(Path(name))
    assert all(new.get(name) == body for name, body in old.items())
    print(f'{name}: prior {len(old)} test AST bodies preserved; {len(new)-len(old)} added')
for name in manifest:
    if name.startswith('dddjango/scripts/'):
        mirror = Path('codex-dddjango/skills/dddjango/scripts') / Path(name).name
        assert Path(name).read_bytes() == mirror.read_bytes()
        print('byte mirror verified:', name)
print('16/16 owned paths syntax and baseline verified; 7/7 byte mirrors exact')
PY
git diff --check
```

## Fix round 1/5 — review M1 and M2

Status: **DONE**, source frozen for scoped independent re-review. This section supersedes the original completion claim for the two downstream-consumer omissions identified in `task-5-review.md`. Both were reproduced before repair, including executed counterparts #151 and #565 that the reviewer had identified as source-established risks.

Baseline: coordinator `task-5-fix1-before/` snapshot. Exactly seven owned files changed: `check-usecase-dto-placement.py`, `check-context-isolation.py`, `check-domain-model.py` under both canonical and Codex script directories, plus `workspace/tools/field_report_checker_smoke.py`. No new public interface, registry source/smoke change, normative change, F4-20 change, subagent, Git mutation, or primary/user-project action.

M1 repair: DTO `_check_structure` records cache-only optional areas and their direct optional usecases before the recursive validation scan. The scan ignores those exact owners and their descendants. Fixed `port/` is excluded from this optional-instance collection. A real file or empty init establishes the instance, so its validation/validators directory continues to emit #183. The scan itself retains its original recursive coverage outside excluded owners.

M2 repair: DTO and context aggregate-name sets now apply `cache_only_instance`; domain #565 usecase-name collection applies it to both optional area and usecase boundaries and excludes the cache directory itself. Real source, empty init, and cache-free empty instances retain their names. Pairing's unused aggregate-name set was not changed.

### RED and GREEN

Commands were run from the same worktree; `$E` denotes the evidence directory defined above. Each log is the full captured command output.

1. RED:
   `python3 -B workspace/tools/field_report_checker_smoke.py CacheInstanceRegression.test_validation_scan_respects_owning_cache_only_area_and_usecase CacheInstanceRegression.test_cache_only_names_do_not_change_real_usecase_service_or_enum_candidates > $E/task-5-fix1-red.log 2>&1`
   Exit 1: 2 test methods, **8 expected direct-channel failures**. #183 fired for validation/validators beneath a cache-only usecase and a cache-only area. #191, #151, and #565 fired only in direct checking for retired instance names; #565 covered an existing area and a wholly cache-only area. The same actual checker CLIs on real `_snapshot_current` copies already matched the required absence, and real-source/empty-init/empty-instance controls passed.
2. Focused GREEN, identical test selector:
   `python3 -B workspace/tools/field_report_checker_smoke.py CacheInstanceRegression.test_validation_scan_respects_owning_cache_only_area_and_usecase CacheInstanceRegression.test_cache_only_names_do_not_change_real_usecase_service_or_enum_candidates > $E/task-5-fix1-focused-green.log 2>&1`
   Exit 0, **2/2**. The tests assert literal expected exit/candidate counts independently for direct and snapshot channels, not only equality between two potentially incorrect outputs.
3. Final field smoke:
   `python3 -B workspace/tools/field_report_checker_smoke.py > $E/task-5-fix1-field-green.log 2>&1`
   Exit 0, **41/41**; all prior 39 test method AST bodies remain unchanged.
4. Snapshot covering tests:
   `PYTHONPATH=workspace/tools python3 -B -m unittest registry_gate_smoke.CacheSnapshotRegression -v > $E/task-5-fix1-snapshot-green.log 2>&1`
   Exit 0, **3/3**. This includes the actual registry gate cache/source contrast and original-file preservation. Registry implementation and smoke source are byte-identical to the fix-round baseline, so the original **33/33** full registry evidence in `task-5-green-registry.log` is reused, as instructed, rather than rerun.
5. Relevant fixture lanes: exact command below; exit 0, **11/11**, unchanged expectations.

```sh
PYTHONPATH=workspace/tools python3 -B - <<'PY' > .superpowers/sdd/2026-09-11-field-report-4-followup/task-5-fix1-fixtures.log 2>&1
from pathlib import Path
import fixture_matrix as matrix
import os, shutil, subprocess, tempfile
owned = {'check-domain-model.py', 'check-usecase-dto-placement.py', 'check-context-isolation.py'}
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
env.pop('DJR_FINDINGS_JSON', None)
count = 0
for label, argv, fixture, expected in matrix.build_cases():
    if Path(argv[1]).name not in owned or label.startswith('invocation/'):
        continue
    with tempfile.TemporaryDirectory(prefix='task5-fix1-fixture-') as td:
        target = Path(td) / 'fixture'
        shutil.copytree(Path(argv[2]), target)
        result = subprocess.run([argv[0], '-B', argv[1], str(target), *argv[3:]], env=env, text=True, capture_output=True)
        print(f'{label}: expected={expected} actual={result.returncode}')
        if result.returncode != expected:
            print(result.stdout + result.stderr)
            raise SystemExit(1)
        count += 1
print(f'{count}/{count} covering fixture exits matched; expectations unchanged')
PY
```

Self-review: the snapshot-relative diff and assertions are retained in `task-5-fix1-scope.log`. The owner collection is limited to optional area/usecase directories; it does not globally exempt validation paths or fixed parents. All seven byte mirror pairs match. The predicate and snapshot implementation remain unchanged, so their documented conservative filesystem limits remain unchanged. No known remaining correctness concern from M1/M2 was found; independent review remains required. Serena/Graphify remain unused because opt-in is absent.

Exact scope/static/self-review command (exit 0; trailing `git diff --check` had empty output):

```sh
python3 -B - <<'PY' > .superpowers/sdd/2026-09-11-field-report-4-followup/task-5-fix1-scope.log
from pathlib import Path
import ast, difflib, hashlib, json
base = Path('.superpowers/sdd/2026-09-11-field-report-4-followup/task-5-fix1-before')
manifest = json.loads((base / 'manifest.json').read_text())
changed=[]
for name, digest in manifest.items():
    before=base/name
    current=Path(name)
    assert hashlib.sha256(before.read_bytes()).hexdigest()==digest
    ast.parse(current.read_text())
    if before.read_bytes()!=current.read_bytes():
        changed.append(name)
        print('CHANGED',name)
        print(''.join(difflib.unified_diff(before.read_text().splitlines(True),current.read_text().splitlines(True),fromfile='before/'+name,tofile=name)))
expected={'workspace/tools/field_report_checker_smoke.py'}
for name in ('check-usecase-dto-placement.py','check-context-isolation.py','check-domain-model.py'):
    expected.add('dddjango/scripts/'+name)
    expected.add('codex-dddjango/skills/dddjango/scripts/'+name)
assert set(changed)==expected,changed
for name in manifest:
    if name.startswith('dddjango/scripts/'):
        assert Path(name).read_bytes()==(Path('codex-dddjango/skills/dddjango/scripts')/Path(name).name).read_bytes()
for name in ('dddjango/scripts/registry_gate.py','workspace/tools/registry_gate_smoke.py'):
    assert Path(name).read_bytes()==(base/name).read_bytes()
p='workspace/tools/field_report_checker_smoke.py'
def tests(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
old,new=tests(base/p),tests(Path(p))
assert all(new.get(k)==v for k,v in old.items())
print(f'Prior {len(old)} test AST bodies unchanged; {len(new)-len(old)} new tests')
print('7 changed owned files; registry source/smoke unchanged; all 7 byte mirrors exact; 16 syntax checks passed')
PY
git diff --check
```
