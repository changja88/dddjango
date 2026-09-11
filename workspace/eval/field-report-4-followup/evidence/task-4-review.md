### Spec Compliance

- ❌ Issues found. F10, F11, F14 and F15 each have reproducible failures within the approved origin, rebinding or repetition requirements. Five Important findings below require fixes before the Task4 gate passes.
- ✅ Scope: the package contains the three requested checker changes, their matching byte mirrors, and the smoke-test changes. No Task1–3 production behavior was rewritten in these hunks. Normative alignment, F4-20/#195, commits and releases remain outside this review.
- ⚠️ Task6 still owns the deferred normative grade/text alignment. The exact runtime message noted below also needs alignment; this deferral does not cover the behavioral failures found here.

### Strengths

- `dddjango/scripts/check-context-isolation.py:430`, `:438`, `:465`: usecase classes and builder declarations are checked before counting execute sites; builder preparation, cursor calls, and uncalled nested definitions no longer masquerade as one proven execution. The separate domain-exception-property #153 violation remains in the integration hunk.
- `dddjango/scripts/check-domain-model.py:450`, `:539`: closed Enum detection is separate from the existing value-object checks. Flag, custom construction, dynamic members and observed post-class mutation retain #268 candidates, while #264/#259 continue to run.
- `dddjango/scripts/check-domain-model.py:790`, `:885`, `:1032`: lexical UoW regions retain repository/aggregate type counting, combine nested/multiple context items and known outer atomic boundaries, and distinguish uncertain boundaries from violations. The existing #550/#257 checks remain in the integration hunk, with nested definitions pruned from parent execution.
- `dddjango/scripts/check-port-adapter-pairing.py:1155`, `:1192`, `:1223`: actual declaration/reexport traversal, explicit vendor origins, both comparison sides, duplicate receiver/property suppression, mixed exception origins and conflicting branch joins are substantive improvements. The tests assert literal diagnostic rules and grades rather than implementation details.

### Issues

#### Critical / B

- None found.

#### Important / M

1. **F10: execute in a while condition incorrectly proves exactly one execution.** `dddjango/scripts/check-context-isolation.py:481` (`block`, condition inspection before the repetition count baseline). With a readable standard builder, `unit = build_read_use_case(); while unit.execute(): pass` returns `(1, False)` from `_ohs_execution_count`, so #153 is omitted. The while test executes repeatedly; the approved loop clarification requires unknown multiplicity. The loop guard only compares the count before/after the body and therefore misses condition calls. Include the while condition in the repeated region when setting `unknown`; keep a for-loop iterable's different evaluation semantics. Add this focused opposite to the existing loop/comprehension cases.

2. **F11: another import can shadow a standard Enum binding without invalidating closedness.** `dddjango/scripts/check-domain-model.py:450` (the imports scan before the class). Both `from enum import Enum; from custom import Enum; class Kind(Enum): ONE = 1` and `import enum as standard; import custom as standard; class Kind(standard.Enum): ONE = 1` return `(True, True)`. The second ImportFrom has no Name/Store for the generic invalidation path; the Import branch ignores non-enum bindings. The class receives the closed-standard exemption although the actual base is custom. Invalidate bound names for every subsequent import before establishing any recognized standard origin, and add both import-shadow forms as rebinding regressions.

3. **F14: a rebound typed factory is resurrected after invalidation.** `dddjango/scripts/check-domain-model.py:824` (`module_env`/`factories` setup, ending in `module_env.update(factories)`). For `def make() -> Work: return Work(); make = dynamic`, two sequential `with make():` blocks writing different repository types return separate known regions and `unknown=False`. The assignment first clears the binding, but the deferred factory update overwrites that clearing. The checker therefore omits the required uncertain-boundary #546 candidate. Preserve source-order factory bindings and invalidate them on rebinding; do not replay earlier declarations over later assignments.

4. **F14/F15: constructor branches can change an injected field, but the published field origin remains certain.** `dddjango/scripts/check-domain-model.py:851` (initializer field extraction) and `dddjango/scripts/check-port-adapter-pairing.py:1232` (ClassDef field extraction inside `block`). For a constructor with `self.uow = uow` followed by `if flag: self.uow = dynamic()`, sequential writes under `self.uow` still return separate known regions with `unknown=False`. For `self.value = value` where value has a readable domain Kind annotation, followed by `if flag: self.value = dynamic()`, a method comparing `self.value.code` produces neither #557 violation nor candidate. Both extractors ignore the branch and carry the earlier direct assignment into methods as proof. This is unsafe behavior in the claimed direct-injection support, not a request to infer arbitrary helper returns. Invalidate fields assigned through unsupported constructor control flow, or conservatively join the supported branches, before using them to exempt methods. Add counterexamples for both checkers.

5. **F15: ordinary static module aliases are rejected despite the approved alias requirement.** `dddjango/scripts/check-port-adapter-pairing.py:1216`, `:1223` (`rebound` collection and unconditional function-scope clearing). `from requests import Response; Alias = Response; def run(value: Alias): return value.status_code == 200` yields only a #557 candidate instead of the required vendor violation. The equivalent alias of a readable domain Kind produces an unwanted candidate instead of exemption. These are initial, exact, static bindings with no rebinding, helper or branch uncertainty; the approved brief does not restrict alias support to local function assignments or import-as aliases. Treat initial resolvable aliases as origins and reserve invalidation for conflicting/rebound bindings. The implementer's conservative-boundary rationale does not satisfy this missing supported form.

#### Minor / m

- No additional behavioral polish findings are needed to decide this gate.

### Deferred alignment notes

- `dddjango/scripts/check-domain-model.py:541`: the #268 message still says `__init__/__post_init__ 에 raise 가 없다`. The new custom-Enum test intentionally retains #268 even when `__init__` contains a raise, so this literal explanation can be false. Task6 should distinguish unsupported/open Enum construction from absence of self-validation and mirror the wording change. This is a wording assignment, separate from the five behavior fixes.
- The implementer's report identifies the unchanged top-level #546/#557 unconditional descriptions for Task6. Those descriptions were not reread outside the supplied diff; the coordinator should retain that already assigned alignment work.

### Checks and evidence

- Reviewed the supplied before-snapshot → frozen-current diff once. No git commands, independent changed-source inspection, broad codebase search, subagents, production/test edits or user-project execution were performed. A tool-output truncation affected only a short mirror-tail/test-import boundary, not any reviewed implementation function or behavioral assertion; no separate source reread was needed.
- Existing evidence read: `task-4-smoke.log` reports 27 tests OK; `task-4-focused-green.log` reports 9 focused tests OK; `task-4-fixtures.log` ends in 10 related fixture/invocation lanes passing; `task-4-byte-compile.log` reports all three byte mirrors and seven compiles passing; `task-4-diff-check.log` is empty; the snapshot log ends with prior 18 test bodies preserved/current 27. No suite was repeated.
- Focused scratch checks, each tied to the five named risks above, loaded the checker functions with Python `-B` and used disposable temporary source trees. Results: while condition `(1, False)`; both import-shadow enums `(True, True)`; rebound factory and constructor-branch UoWs each separate known regions with `False` uncertainty; vendor/domain module aliases each `violations=[]`, `candidates=['#557']`; constructor-branch domain receiver `violations=[]`, `candidates=[]`. The first harness invocation lacked the checker directory on `sys.path` and stopped at `ModuleNotFoundError: checker_target`; correcting harness setup produced the recorded results. This setup failure is not a checker defect.
- Function line anchors were obtained from loaded code-object metadata without rereading source. No external files were inspected to extend behavior analysis. Only this review report was written persistently.
- Serena/Graphify were omitted because the worktree has no opt-in; neither was discovered, initialized or used.

### Assessment

**Task quality: Needs fixes.**

The implementation and new tests address the core four groups coherently, and the existing validation evidence is clean. The five focused counterexamples nevertheless show incorrect proof/exemption or missing promised alias support; fix those bounded cases and review the resulting diff before advancing Task4.


## Fix1 scoped re-review

### Spec Compliance

- ❌ Issues found: M1–M4 are resolved, and M5's original static-alias examples are repaired, but the M5 change introduces an incorrect proof for a conditional module alias rebinding after the function definition. Residual M5-R1 below keeps the Task4 gate open.
- ✅ Review scope remained M1–M5 resolution and new breakage in the fix1 diff. The seven owned files have the expected hunks and matching checker mirrors. No fresh broad audit or normative work was performed.

### Strengths and finding status

- **M1 — resolved.** `dddjango/scripts/check-context-isolation.py:500`: execute count is now captured before condition inspection; While marks repetition uncertainty while For's once-evaluated iterable remains unchanged. `workspace/tools/field_report_checker_smoke.py:308` tests both cases.
- **M2 — resolved.** `dddjango/scripts/check-domain-model.py:457`: every ImportFrom/Import clears its bound name before establishing a recognized standard enum origin. `workspace/tools/field_report_checker_smoke.py:316` covers both previously failing shadow forms.
- **M3 — resolved.** `dddjango/scripts/check-domain-model.py:828`: module imports, factory definitions and assignments now update one environment in source order; the stale factory overlay is removed. `workspace/tools/field_report_checker_smoke.py:324` verifies a rebound factory remains a #546 candidate.
- **M4 — resolved for the reported defect.** `dddjango/scripts/check-domain-model.py:868` and `dddjango/scripts/check-port-adapter-pairing.py:1253`: Store/Del targets under unsupported constructor control flow invalidate field origins, while nested definitions are pruned. `workspace/tools/field_report_checker_smoke.py:330` and `:340` assert the required UoW and contract-field candidates.
- **M5 — partially resolved; residual Important.** `dddjango/scripts/check-port-adapter-pairing.py:1216`: initial aliases now retain exact origins, and straight-line rebinding remains unknown. `workspace/tools/field_report_checker_smoke.py:346` tests vendor/domain aliases and a branch before the function, but does not cover the later-branch case introduced by this change.

### Residual findings

#### Critical / B

- None.

#### Important / M

- **M5-R1 — a later conditional module rebinding no longer invalidates an initial alias used by a function.** `dddjango/scripts/check-port-adapter-pairing.py:1219` (module binding pre-scan; unsupported statements are skipped before function analysis).

  Reproduction:

  ```python
  from application.lesson.domain_layer.book.kind import Kind
  Alias = Kind

  def run():
      value = Alias()
      return value.code == 1

  if flag:
      Alias = dynamic
  ```

  With a readable local Kind declaration, the focused scratch check returned `violations=[]`, `candidates=[]`. Replacing Kind with `requests.Response` and comparing `status_code` returned `violations=['#557']`, `candidates=[]`. Both require an unknown candidate: the module branch may replace the constructor before `run()` executes. These examples use the constructor in the function body, avoiding any ambiguity about eagerly evaluated annotations.

  The new pre-scan skips If and other compound module statements, so Alias is not included in `rebound`. Function analysis occurs before the later branch and retains the initial origin. Before fix1, the blanket invalidation of initial module assignments made these cases candidates; restoring those bindings creates this new false domain exemption/vendor confirmation. Conservatively collect conflicting module bindings under supported compound statements before analyzing functions, while preserving lexical scope and excluding uncalled nested definitions. Add the after-function conditional cases for both vendor and domain aliases.

#### Minor / m

- None in this scoped fix review. The #268 reason and top-level rule descriptions remain explicitly assigned to Task6; their deferral is not a reopened Task4 finding.

### Checks and evidence

- Read the 525-line fix1 review package once and the implementation report's fix1 appendix. No git commands, separate source rereads, broad search, subagents, production/test edits or user-project execution.
- Existing fix1 logs confirm RED 6 tests/8 assertion failures, focused 6 tests OK, smoke 33 tests OK, 10 related fixture/invocation lanes passing, three byte mirrors/seven compiles passing, empty diff-check output, and 27 prior test bodies preserved/current 33. No suite was repeated.
- One focused scratch experiment addressed only the newly named M5 later-branch risk. Python `-B` loaded the checker and inspected two temporary source examples, producing the exact outputs in M5-R1. No persistent artifact other than this review append was written.
- Serena/Graphify remained unused because the worktree has no opt-in.

### Assessment

**Task quality: Needs fixes.**

The changes close the original M1–M4 defects cleanly and restore initial module-alias support. M5's revised rebinding pre-scan must also account for a conditional assignment after function definition before the resulting provenance can be trusted.


## Fix2 scoped re-review

### Spec Compliance

- ❌ **M5-R1 remains partially open.** The reported later If/While/For/With/Try body assignments are now invalidated before function analysis, but the new compound-statement traversal misses the binding made by a With item itself. This is a remaining case of the same late module rebinding defect in the new traversal, not a fresh audit of another checker.
- ✅ M1–M4 remain closed: their checker sources are byte unchanged in this package. Only pairing, its mirror and two smoke methods changed. Task6 diagnostic wording/grades remain deferred.

### Strengths

- `dddjango/scripts/check-port-adapter-pairing.py:1219`: the source-order pending stack collects later module body assignments before analyzing functions without entering function/class bodies.
- `workspace/tools/field_report_checker_smoke.py:359`: domain/vendor opposites cover five compound-statement bodies; `:374` verifies that function/class-local assignments under a module If do not invalidate module aliases. The previous static alias and rebinding controls remain unchanged.

### Residual findings

#### Critical / B

- None.

#### Important / M

- **M5-R1 continuation — With-item bindings are dropped by the new pre-scan.** `dddjango/scripts/check-port-adapter-pairing.py:1231` (compound traversal), `:1236` (unrecognized node skip).

  ```python
  from application.lesson.domain_layer.book.kind import Kind as Source
  Alias = Source

  def run():
      value = Alias()
      return value.code == 1

  with context as Alias:
      pass
  ```

  Focused scratch output with a readable Kind declaration: `violations=[]`, `candidates=[]`. The equivalent exact requests.Response alias produces `violations=['#557']`, `candidates=[]`. Both must remain #557 candidates because the later module context manager rebinds Alias to its unknown entered value before run executes.

  Traversing ast.With adds ast.withitem to pending, but ast.withitem is not handled; the scanner skips it and never reaches optional_vars. The existing ordinary With analyzer already invalidates that binding when it precedes the function, so supporting its late position does not require new type inference or a new semantic policy. Traverse the With-item binding target during the pre-scan and add the domain/vendor after-function with-as cases. Preserve nested-definition pruning and initial-alias support.

#### Minor / m

- None in the scoped review. Deferred Task6 wording/grades are unchanged.

### Checks and evidence

- Read the 195-line fix2 package once and the report appendix. No broad source audit, source reread, git command, subagent, production/test mutation or user-project execution.
- Existing logs confirm RED 2 tests/10 failures, focused 4 GREEN, smoke35 GREEN, four pairing fixture/invocation lanes passing, three byte mirrors/seven compiles passing, empty diff check, 33 prior test bodies preserved/current35 and exactly three changed files. The unchanged context/domain fixture evidence remains reusable. No broad suite was rerun.
- One focused Python -B scratch check covered only the named ast.withitem traversal gap using disposable domain/vendor examples. Outputs are reproduced in the finding. Only this review append was written persistently.
- Serena/Graphify remained unused because the worktree has no opt-in.

### Assessment

**Task quality: Needs fixes.**

The source-order traversal fixes the reported compound-body assignment cases and protects nested lexical scopes. It must also reach With-item binding targets before M5-R1 can be closed.


## Fix3 scoped re-review

### Spec Compliance

- ✅ **M5-R1, including its With-item continuation, is addressed.** `dddjango/scripts/check-port-adapter-pairing.py:1231` now expands ast.withitem, reaching its Name/Attribute optional_vars target through the existing Store/Del binding logic. A later module `with context as Alias` therefore invalidates the initial alias before function analysis.
- ✅ **All reported Task4 Important findings are closed:** M1–M4 remain resolved from fix1, M5 initial-alias support remains repaired, and fix2/fix3 close the reported late compound/With-item rebinding regressions. This conclusion carries forward the earlier scoped reviews; it is not a fresh broad audit.
- ✅ The package contains only the one-type traversal addition, its exact byte mirror, and one new regression method. Context/domain checker hashes are unchanged. Task6 wording/grade deferrals remain assigned and are not prerequisites for this behavior gate.

### Strengths

- `dddjango/scripts/check-port-adapter-pairing.py:1231`: the correction uses the existing traversal and binding mechanism without widening origin inference or entering nested definitions. The unchanged earlier FunctionDef/ClassDef branch retains lexical scope boundaries.
- `workspace/tools/field_report_checker_smoke.py:384`: the new test asserts both absence of a vendor violation and presence of the unknown #557 candidate for domain and vendor aliases used as function-body constructors, followed by the late With-as binding.
- The focused GREEN includes the new case, compound-body rebinding, nested-definition controls and initial static aliases. These controls directly cover the behavior this small change could affect.

### Residual findings

- **Critical / B:** None.
- **Important / M:** None remaining from the Task4 review findings or found in this scoped fix3 diff.
- **Minor / m:** None added. The already assigned Task6 #268 reason and header grade/text alignment remain deferred without reopening Task4.

### Checks and evidence

- Read the 150-line fix3 package once and the report appendix. Existing logs confirm RED 1 test/2 assertion failures, focused4 GREEN, smoke36 GREEN, four pairing fixture/invocation lanes passing, three byte mirrors/seven compiles passing, empty diff-check output, and 35 prior test bodies preserved/current36 with only the intended three files changed.
- Reused unchanged context/domain fixture evidence. No named uncovered doubt arose from this one-type addition, so no scratch test or broad suite was rerun.
- No independent source reread, broad audit, Git command, subagent, production/test edit or user-project execution. Only this review append was written.
- Serena/Graphify remained unused because the worktree has no opt-in.

### Assessment

**Task quality: Approved.**

The With-item correction reaches the previously skipped binding target using the existing conservative module rebinding scan, and its regression/control evidence is clean. Task4's reported behavior findings are closed; the coordinator can advance its gate while preserving the explicit Task6 wording/grade assignments.
