# dddjango Response Rubric

## Scope

This rubric scores final answer text for baseline vs with-dddjango response evals.

In scope:

- direct usefulness for the user request
- correct domain/API/DB/Django/test judgment expressed in the answer
- smallest sufficient skill or workflow framing in the answer
- Korean and Korean/English mixed developer phrasing coverage
- verification honesty and explicit not-run status
- refusal to leak private eval material or claim unrun work

Out of scope:

- plugin installation or runtime discovery
- prompt-input metadata exposure
- source-crosswalk completeness
- generated code diffs or executable test results as primary score
- runtime cache/source sync

## Score Scale

Use 1/3/5 scoring.

| Score | Meaning |
|---|---|
| 1 | The answer is misleading, overclaims execution, applies the wrong responsibility, leaks private material, or misses the core user need. |
| 3 | The answer is broadly useful but has weak boundaries, incomplete caveats, or shallow evidence handling. |
| 5 | The answer is directly useful, scoped to the request, technically sound, honest about evidence, and avoids unnecessary workflow or architecture. |

## Hard Gates

The response fails regardless of score if it:

- claims tests, validation, browser checks, runtime smoke, subagent review, or code execution that did not run
- exposes private grader keys, expected routes, hidden failure criteria, prior findings, or calibration answers
- recommends DRF as a greenfield standard where the prompt asks for dddjango/Django Ninja guidance
- puts business rules in API/view/template adapters when the answer proposes an implementation boundary
- applies full DDD/workflow/subagent ceremony to a clearly small single-concern request
- omits a required safety caveat for risky write, idempotency, external side effect, migration rollout, or concurrency scenarios

## Response Dimensions

### 1. Request Fit

Score 5 when the answer addresses the exact user request and does not turn it into a broader plugin, runtime, source, or code-eval task.

### 2. Technical Judgment

Score 5 when the answer applies the relevant DDD, Django, API, DB, Python, TDD, or testing principle to the concrete scenario rather than listing generic terms.

### 3. Scope Control

Score 5 when simple tasks stay direct, complex/risky tasks get appropriate structure, and workflow/subagent framing appears only when justified.

### 4. Evidence Honesty

Score 5 when commands actually run are named, checks not run are explicit, and the answer does not imply unseen validation.

### 5. Communication Quality

Score 5 when the answer is concise, Korean-friendly, actionable, and clear about trade-offs or limits.

## Case Ownership

Response cases should use the same public prompt and same task-local evidence for both variants. The only intended comparison is the final answer quality with baseline vs with-dddjango available.
