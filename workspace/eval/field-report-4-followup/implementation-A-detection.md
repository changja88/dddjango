# Whole implementation review A — detection and opposite cases

Review date: 2026-09-11. Review root: `/Users/hyun/.cache/dddjango-field4-followup-20260911`. Base identified by the supplied package: `3355710dcbaf023a16856cb2f307aa2a03fc0996`. The review concerns the uncommitted Tasks 1–6 bytes in `whole-review-hashes.json`, not a release or committed tree.

**Readiness: CHANGES REQUIRED. B 0 / M 4 / m 0.** The four findings below are reproduced behavior failures within the approved directions. Resolve and independently review them before accepting this whole implementation gate. No final `make verify`, seal, evidence audit, or user-project execution is claimed here.

## M1 — marker mutation calls survive a supposedly final module-marker replacement

- Approved requirement: F4-1 / Task 1. An update's `[markers:]` is the final empty module marker list; unsupported dynamic/incremental marker state must retain original bytes and be reported S5.
- Location: `dddjango/scripts/design_pregate.py:1430`–`:1448` (mutation discovery) and `:1465`–`:1467` (static assignment acceptance/replacement). The same defect is present in the byte-identical Codex script.
- Cause: discovery recognizes Name stores and Subscript Store/Del, but ignores calls which mutate the existing list. It accepts the initial simple assignment and leaves a following `pytestmark.append(...)` or `pytestmark.pop()` intact. The renderer reports that the module marker poststate was transcribed.

Focused scratch input, with an update entry carrying `Signals(markers=[], markers_explicit=True)`:

```python
import pytest
pytestmark = [pytest.mark.slow]
pytestmark.append(pytest.mark.django_db)
```

Actual `_render_marker_update` result is changed bytes, with `pytestmark = []` followed by the unchanged append. Evaluating only the synthetic module against a fake `pytest.mark` namespace gives **`['django_db']`**, despite the declared final list being empty. Returned reason:

```text
module marker 후상태만 전사; 함수/class decorator·본문 변경은 S5
```

Opposite failure: replace the final line with `pytestmark.pop()`. The original synthetic module evaluates successfully and ends with `[]`. The rendered module raises **`IndexError: pop from empty list`**. Both calls pass the renderer's compile check. Source bytes in the temporary tree remain unchanged; the faulty bytes are the returned proposed materialization.

This is not a request to simulate arbitrary test-module execution. Conservatively recognize direct module marker mutation calls as unsupported and preserve them with a specific S5 reason. Keep plain static replacements supported. Regression checks should assert source/copy preservation and materialization absence for the mutation cases, and final values or failure absence for supported static cases. Existing subscript mutation tests do not cover list methods.

## M2 — fixed admin kwargs bypass actual business-consumption analysis

- Approved requirement: F4-9 / Task 3. Framework UI integration receives narrow type relief, while actual business reading/comparison/calculation/state change keeps the existing rules. The current governing paragraph also states this at `dddjango/skills/discipline-houserules/SKILL.md:81`.
- Location: `dddjango/scripts/check-public-surface-annotation.py:858`–`:865` and `:1096`–`:1100`. `_ADMIN_KWARGS` is assigned a fixed policy directly. Keyword-vararg annotations/bindings are not entered into the context graph or visited as an active consumption source, and `judge` returns early for their fixed `sig-star` slots.

Reproduction:

```python
from typing import Any
from django.contrib.admin import ModelAdmin
from django.http import HttpResponse

class BookAdmin(ModelAdmin):
    def get_form(self, request: object, **kwargs: Any) -> HttpResponse:
        if kwargs['amount'] > 10:
            charge(kwargs['amount'])
        return super().get_form(request, **kwargs)
```

Actual `_check_explicit_any` in-memory probe emits **no #645 violation** for this annotation. An actual `check-public-surface-annotation.py` CLI on a disposable tree containing this source likewise emits **no #645/#647**. Its exit is 2 solely for the independent existing #646 bare-ModelAdmin diagnostic. The ordinary framework-forwarding control, with the two business lines removed, has exactly the same #646-only CLI output. Thus the test does not mistake whole-file green for the required result; it directly isolates the missing annotation diagnosis while showing #646 is preserved.

The fixed framework signature is evidence of integration origin, but it is not evidence that values remain UI transport. The approved boundary explicitly requires actual business consumption to regain ordinary treatment. Carry the kwargs binding through the same bounded consumption policy, or apply an equivalent narrow veto, so a known read/comparison such as the example prevents the exemption. Preserve relief for unchanged framework forwarding and generated bodyless fixed slots. An unknown escape should remain a review candidate rather than being silently accepted.

## M3 — an OHS builder alias keeps its imported origin after a module function/class replaces it

- Approved requirement: F4-10 / Task 4. Count a usecase execution only when the builder/receiver origin is established; rebinding invalidates the binding, and unknown execution must remain a #153 candidate.
- Location: `dddjango/scripts/check-context-isolation.py:400`–`:418`. The module import environment accounts for assignment rebinding, but does not invalidate FunctionDef/AsyncFunctionDef/ClassDef names. That environment is then used to analyze the public OHS operation.

Create readable standard declarations in a disposable tree:

```python
# application/lesson/application_layer/books/read/read_use_case.py
class ReadUseCase: pass

# application/lesson/composition_root/books.py
from application.lesson.application_layer.books.read.read_use_case import ReadUseCase
def build_read_use_case() -> ReadUseCase:
    return ReadUseCase()
```

And inspect this OHS entry:

```python
from application.lesson.composition_root.books import build_read_use_case as _prepare

def _prepare():
    return cursor

def read_query(request):
    _prepare().execute()
```

Actual `_ohs_execution_count` returns **`(1, False)`** for the function-shadow and class-shadow forms. In the exact private-function example above, actual `_check_ohs_service` produces **no #153 violation and no #153 candidate**. The control with no rebinding also produces no #153, as expected. A private helper name was used so an unrelated public helper operation cannot mask this missing result.

At runtime `_prepare` is the local helper, not the imported composition builder, and `cursor` has no proven usecase origin. This is a simple explicit module binding, not unsupported interprocedural inference. Invalidate replaced module definitions before treating the imported address as proof, and add private-function/class shadow controls alongside existing assignment-rebind tests. The expected result is an unknown #153 candidate, not a confirmed business violation.

## M4 — a local class can replace a UoW import while sequential regions still pass as proven UoWs

- Approved requirement: F4-14 / Task 4. Separate sequential regions only for resolved standard UoWs; local/unknown boundary origins remain candidates and must not be certified by a matching name.
- Location: `dddjango/scripts/check-domain-model.py:834`–`:842`. The source-ordered module environment handles imports, functions, and assignments but omits ClassDef rebinding. Parameter annotation resolution therefore retains the obsolete imported UoW address.

Minimal focused source:

```python
from application.lesson.application_layer.port.unit_of_work.lesson_unit_of_work import LessonUnitOfWork as Work

class Work:
    pass

def run(uow: Work, books: BookRepository, loans: LoanRepository):
    with uow:
        books.save(a)
    with uow:
        loans.save(b)
```

Actual `_check_application_side` on a disposable source tree returns **no #546 violation and no #546 candidate**. The standard-import control without the local class has the same empty #546 result. The old imported type is thus still used to split the two writes into known separate regions after its name has been replaced.

The empty class is sufficient to expose the AST provenance bug; this probe does not execute it or claim it implements a runtime context manager. Giving the local class ordinary context-manager methods would not restore a standard UoW origin. The required disposition is uncertainty/candidate for the two aggregate kinds, not proof of independent transaction regions. Clear the stale origin on module class definitions and cover a local class shadow with the standard sequential-UoW control. No instance-identity or global transaction solver is required.

## Coverage and evidence

- Read `whole-review-brief.md` first, then the approved user directions and inventory. Read the complete 5,124-line canonical code/test diff in bounded ranges, covering all 13 files. A truncated initial domain section was reread in a smaller range before assessment. Relevant Task 1–5 contracts, prior fix conclusions, and Task 6's current boundary/scenario text were consulted for exact supported behavior. The broader normative review belongs to lens B; a large Codex meaning-diff display was truncated and is **not** claimed as a complete independent semantic-mirror read here.
- Independently hashed all **54** entries in `whole-review-hashes.json`: **zero mismatches**. Compared the **10** changed script/rulepack pairs: all canonical/Codex bytes are equal. Therefore the findings apply to the frozen reviewed bytes and both script distributions. This is byte verification, not semantic proof of every prompt.
- Fresh execution was limited to the named doubts above: Python `-B` checker/helper calls, the actual public-surface checker CLI, and evaluation of synthetic marker modules against a fake pytest namespace. Disposable directories contained only invented source. No real user project was imported or executed, and no suite was rerun.
- The first admin CLI probe shared a disposable root with a marker probe; a second isolated admin-root run established the exact #646-only output reported in M2. This harness refinement did not change the observed absence of #645/#647. The report does not call either admin source globally green.
- Read and inspected the new regression assertions for declaration/hash/marker/report interfaces; exact generated-method provenance and full normalized-key cohort joins; generated-versus-real #376 and #566; admin origin/helper/business/JSON/generic opposites; OHS execution, Enum, lexical UoW, vendor/domain/unknown comparisons; cache-only direct/snapshot controls; and #642 retirement versus retained shape/200-line signals. No additional blocking defect was established in those other changed paths during this review. Their existing passing logs are not represented as this reviewer's reruns.
- Declaration checking still precedes the zero-materialization branch; confirmed declaration results remain separate from source attribution and combine into exit 2. S1 remains an explicit unverified channel, with full cohort/location joins and mixed/unmatched preservation. These are source/test inspection conclusions, not a claim that S1 behavior has been implemented or verified in a user application.
- F4-13 is a normative repair, not a newly executed exception-normalization implementation. Its manual scenario table is not fresh-agent behavior evidence. Unknown origins, unsupported dynamic scopes, caller-owned transactions, and deferred/generated bodies remain limitations; no absence of a diagnostic is used to prove those unknown cases safe.

Only this assigned report was written persistently. No production/test/Git changes, subagents, seal, release, report-item removal, or final full verification were performed. Serena/Graphify were not discovered or used because the worktree has no opt-in, as required by the review brief.
