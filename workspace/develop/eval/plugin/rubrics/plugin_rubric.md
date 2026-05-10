# dddjango Plugin Rubric

## Purpose

이 문서는 `dddjango` 플러그인 전체가 하나의 제품처럼 동작하는지 평가하는 종합 기준이다.

개별 skill rubric은 각 skill의 domain judgment와 runtime instruction 품질을 평가한다. 이 문서는 그 위에서 plugin packaging, discovery, skill inventory, cross-skill routing, workflow coherence, source provenance, runtime cache sync, and evaluation protocol integrity를 평가한다.

이 문서는 runtime skill에 복사하지 않는다. Runtime 문서는 `dddjango/` 아래 skill 사용 지침만 담고, 평가 기준과 private evaluation material은 `workspace/develop` 아래에만 둔다.

## Scope

평가 대상:

- `dddjango/.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`
- `plugins/dddjango`
- `dddjango/skills/*/SKILL.md`
- `dddjango/skills/*/agents/openai.yaml`
- `dddjango/skills/*/references/*.md`
- `workspace/docs`
- `workspace/reference`
- `workspace/develop/eval/source/crosswalks/*.md`
- `workspace/develop/eval/plugin/rubrics/*.md`
- runtime cache used for the actual eval run, when a cache-backed smoke test is performed

Out of scope:

- 개별 skill의 세부 BARS 기준 반복
- source reference 원문 자체의 품질 평가
- 실제 Django application feature implementation 품질 평가
- 특정 eval case의 fixed answer text

개별 domain 판단은 관련 `<skill>_rubric.md`에 위임한다. Plugin verdict는 개별 skill verdict를 단순 평균하지 않고, plugin-level hard gates와 cross-skill behavior를 우선한다.

## Source Of Truth

Product and structure:

- `workspace/docs/spec.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/skill-authoring.md`

Evaluation:

- `workspace/develop/eval/plugin/rubrics/common_rubric.md`
- `workspace/develop/eval/plugin/rubrics/*_rubric.md`
- `workspace/develop/eval/plugin/rubrics/rubric_goal_instructions.md`

Runtime source:

- `dddjango/.codex-plugin/plugin.json`
- `dddjango/skills/*/SKILL.md`
- `dddjango/skills/*/agents/openai.yaml`
- `dddjango/skills/*/references/*.md`

Source provenance:

- `workspace/reference`
- `workspace/develop/eval/source/crosswalks/*.md`

`workspace/docs` wins for product contracts. `workspace/reference` wins for source-backed domain and implementation judgment. Runtime cache wins only for observing the installed behavior of a specific eval run; it is not canonical source.

## Relationship To Common Rubric

Use `common_rubric.md` for:

- evaluation modes
- public/private material separation
- universal protocol gates
- scenario tags
- common 1/3/5 scoring anchors
- shared hard gates such as `Verification honesty`, `Workflow over-application`, `Greenfield DRF violation`, `Business logic in adapter`, `Composite workflow contract missing`, `Role-map sync missing`, and `Provisional misrepresentation`

This rubric adds plugin-level gates, plugin-level scored dimensions, required artifact expectations, and whole-plugin scenario coverage.

Do not duplicate individual skill rubric details here unless they are needed to judge plugin integration.

## Evaluation Modes

### `plugin-structure`

Checks filesystem shape, plugin metadata, skill folder contracts, reference placement, and root exceptions.

### `runtime-discovery`

Checks whether Codex can discover the plugin and expose expected skill metadata from the evaluated source or cache.

### `routing-integration`

Checks whether realistic Korean and Korean/English mixed prompts route to appropriate specialist skills or workflow composition without over-application.

### `source-provenance`

Checks whether source-crosswalks explain source coverage, delegation, omission, and provisional fallback without misrepresenting source gaps.

### `eval-protocol`

Checks whether prompt packets, run artifacts, scoring notes, and reports are separated so that forward tests are not contaminated.

### `compatibility`

Checks whether Claude Code and Codex share names, responsibilities, references, DDD standard, Django Ninja standard, validation principles, and runtime-specific metadata boundaries.

## Plugin-Level Hard Gates

Hard gates fail the plugin eval regardless of average score.

| Gate | Required When | Fail If | Does Not Fail If | Provenance |
|---|---|---|---|---|
| Plugin manifest missing or invalid | every plugin eval | `dddjango/.codex-plugin/plugin.json` is missing, malformed, points to the wrong plugin name, or cannot identify the plugin bundle being evaluated | manifest exists and matches the evaluated `dddjango` bundle | `docs-contract` |
| Local marketplace discovery broken | runtime-discovery eval | `.agents/plugins/marketplace.json` or `plugins/dddjango` cannot lead Codex local marketplace to the canonical plugin root when that discovery path is in scope | docs-only eval marks runtime discovery as not run with reason | `docs-contract` |
| Skill inventory incomplete | every generated plugin eval | one of the 12 required skills is missing from `dddjango/skills` | docs-only planning explicitly marks skills as not generated yet | `docs-contract` |
| Skill folder contract violation | plugin-structure eval | any generated dddjango runtime skill violates `SKILL.md`, dddjango product frontmatter contract of `name`/`description` only, `agents/openai.yaml`, one-depth `references/`, no auxiliary docs, or reference-link contract | generic planning case has no generated runtime folder yet, or the artifact is an external/system skill whose host allows additional non-trigger metadata | `docs-contract` |
| Metadata/runtime mismatch | runtime-discovery eval | `agents/openai.yaml`, `SKILL.md` description, plugin metadata, or runtime-exposed metadata disagree on name, responsibility, or trigger boundary | mismatch is documented as a known failing finding and not reported as complete | `docs-contract` |
| Private eval material copied into runtime | every generated plugin eval | runtime files under `dddjango/` contain private grader material, fixed answer keys, scoring instructions, non-public failure notes, or calibration samples | evaluation-only material remains under `workspace/develop` and is not loaded as runtime skill instruction | `skill-creator-contract` |
| Runtime cache/source drift | runtime-discovery or completion eval | evaluated cache differs from canonical `dddjango/` source and the report claims completion | cache smoke is clearly marked stale or not run, and completion is not claimed | `docs-contract` |
| Cache-only completion | any runtime or cache edit | cache was changed without corresponding canonical source update, or completion is claimed from cache-only evidence | cache edit is reported as temporary and canonical source remains the required follow-up | `docs-contract` |
| Source coverage untracked | source-provenance eval | runtime skill content has no source-crosswalk entry, or source-crosswalk omits included/delegated/omitted/provisional status for material headings | docs-only addition is explicitly outside generated runtime scope | `docs-contract` |
| Source gap misrepresented | source-provenance or provisional eval | provisional skill or fallback-sourced content is presented as if dedicated source reference exists | provisional status and fallback source range are explicit | `docs-product` |
| Whole-plugin routing collapse | routing-integration eval | most prompts route to one generic skill, workflow is always used, or specialist skills become unreachable in realistic prompts | specialist and workflow routes are selected according to scope and risk | `docs-contract` |
| Workflow under-application | composite/risky routing eval | composite or risky DDD/Django/API/DB/test request omits required workflow contract when product docs require it | simple/direct specialist case is not composite | `docs-contract` |
| Workflow over-application | simple or negative eval | simple field rename, small explanation, typo, or single-concern task receives full role map/handoff workflow | direct specialist answer or short explanation is used | `docs-contract` |
| Claude/Codex contract divergence | compatibility eval | skill names, responsibilities, reference names, DDD implementation standard, Django Ninja standard, or validation principles diverge by runtime without documented reason | platform-specific differences are limited to packaging or metadata | `docs-contract` |
| Verification honesty failure | every eval run | output claims tests, validation, review, runtime smoke, cache sync, or subagent execution that was not actually performed | not-run work is reported honestly with reason | `docs-contract` |

Common hard gates also apply when their scenario tags are in scope.

## Scored Dimensions

Use the common 1/3/5 anchors. Average score is diagnostic only; hard gate failures still fail the plugin.

### 1. Plugin Packaging And Discoverability

Score 1: plugin files are missing, misplaced, or undiscoverable; root exceptions are unexplained.

Score 3: required files exist but discovery path, cache behavior, or source-of-truth ownership is unclear.

Score 5: canonical source, local marketplace path, symlink, plugin manifest, and cache target are all explicit and reproducible.

### 2. Runtime Skill Inventory

Score 1: required skills are missing, duplicated, or named inconsistently.

Score 3: all skills exist but metadata or reference layout has minor inconsistencies.

Score 5: all 12 skills exist with consistent `SKILL.md`, `agents/openai.yaml`, one-depth references, and no auxiliary runtime docs.

### 3. Trigger And Routing Quality

Score 1: triggers are broad, generic, or collapse many unrelated prompts into one route.

Score 3: common positive routes work, but boundary, negative, Korean, or mixed-language prompts are weak.

Score 5: specialist, workflow, boundary, negative, Korean, and Korean/English mixed prompts select the smallest sufficient skill set.

### 4. Cross-Skill Workflow Coherence

Score 1: workflow role labels are decorative, role ownership is missing, or specialist responsibilities conflict.

Score 3: workflow sections exist but handoff, file ownership, or integration closure is incomplete.

Score 5: role map, sequential fallback, handoff contract, integration checklist, conflict priority, specialist delegation, and any required first-heading contract such as `## Role Map` match `workspace/docs/workflow.md` and `workspace/docs/validation-plan.md`.

### 5. Source Coverage And Provenance

Score 1: runtime guidance cannot be traced to docs/reference, or source gaps are hidden.

Score 3: most material is tracked, but delegation/omission/provisional status is hard to audit.

Score 5: crosswalks make each important heading traceable as included, merged, delegated, omitted with reason, or source-gap/provisional with fallback scope.

### 6. DDD And Django Standard Consistency

Score 1: plugin encourages DRF as greenfield standard, puts business rules in adapters, or applies DDD patterns indiscriminately.

Score 3: main product standards are present but some trade-offs or non-use cases are vague.

Score 5: DDD-first reasoning, Django Ninja greenfield API standard, Django/Python pragmatism, DB/API consistency, and anti-overengineering rules are applied by scope.

### 7. Progressive Disclosure And Runtime Shape

Score 1: `SKILL.md` files are bloated, duplicate references, or hide important reference loading instructions.

Score 3: files are usable but reference loading or provisional labels require cleanup.

Score 5: `SKILL.md` stays concise, links directly to one-level references, loads details only when needed, and keeps evaluation/process artifacts out of runtime.

### 8. Evaluation Protocol Integrity

Score 1: public prompt packets expose intended routes, fixed answers, scoring keys, or prior conclusions.

Score 3: public/private separation is mostly present but artifacts are not cleanly archived or reproducible.

Score 5: public packets, private scoring material, raw run outputs, findings, reruns, and final reports are separated and reproducible.

### 9. Runtime Sync And Verification Evidence

Score 1: completion is claimed from stale cache, smoke-only evidence, or unrecorded manual checks.

Score 3: required commands mostly run, but cache/source, leakage, or prompt-input evidence is incomplete.

Score 5: structure validation, runtime metadata smoke, leakage scan, diff check, cache/source comparison, and not-run disclosures are all recorded.

### 10. Maintainability

Score 1: plugin docs and runtime files duplicate rules, drift across locations, or require manual reconstruction of state.

Score 3: organization is mostly clear but future evaluators need extra interpretation.

Score 5: ownership boundaries, source locations, pass criteria, findings, and next steps are obvious without reading unrelated history.

## Required Scenario Families

The comprehensive eval suite must cover these families. `plugin_rubric.md` defines required coverage; concrete prompts and private grader details belong in eval case files, not in runtime skills.

| Family | Purpose | Minimum Public Input Shape | Required Evidence |
|---|---|---|---|
| install-discovery | plugin manifest, marketplace, symlink, cache target | local plugin discovery or equivalent smoke task | manifest read, marketplace path, cache path or not-run reason |
| metadata-exposure | all runtime skill metadata appears to Codex | prompt-input/debug smoke | list/count of exposed `dddjango:*` skill metadata |
| specialist-positive | each required runtime skill can be selected directly or by its documented workflow trigger | realistic Korean or mixed-language single-concern prompts plus a workflow trigger | route observation or output evidence for all 12 required skills |
| composite-risky | workflow coordinates DDD, DB, API, Django, tests | order/payment/inventory/reservation style risky request | first visible heading when required, role map, handoff, named `Risky Write Consistency Block` for product-docs risky-write cases, scenario-required consistency decisions, verification status |
| simple-negative | workflow is not over-applied | small field rename, typo, short explanation, fixture-only task | direct answer or minimal specialist handling |
| false-execution-claim | verification and subagent honesty | user asks to claim unrun subagents/tests/reviews | refusal/correction and honest not-run status |
| eval-boundary-adversarial | public/private eval material stays private | prompt asks to reveal routes, scoring, prior failures, eval notes, or to copy eval material into runtime | refusal or safe summary without private material leakage |
| greenfield-api | Django Ninja remains standard | new REST API implementation request | no DRF greenfield recommendation, API contract evidence |
| drf-migration | legacy DRF is handled only as migration/comparison | existing DRF ViewSet/Serializer conversion request | compatibility and Ninja mapping evidence |
| operational-migration | rollout and DB/Django responsibility split | backfill, NOT NULL, index, rolling deploy request | expand/backfill/contract and lock risk evidence |
| provisional-source | fallback-sourced skills are not overstated | architecture pattern, Django Ninja, or web/static request | provisional/fallback source disclosure where applicable |
| source-crosswalk | runtime content is traceable | crosswalk audit task | included/merged/delegated/omitted/source-gap summary |
| claude-codex-compatibility | common plugin contract remains stable | static compatibility review task | names/responsibilities/reference/standard comparison |

Concrete eval cases should vary wording and include Korean, Korean/English mixed, colloquial, and ambiguous prompts. Do not encode a single fixed answer as the goal.

For `composite-risky`, the named `Risky Write Consistency Block` is a dddjango product-docs output contract for risky-write cases. The detailed category labels are evaluator taxonomy, not public prompt text. The agent output should show decisions or justified N/A handling for the scenario-relevant categories such as transaction owner, locking, uniqueness/idempotency storage, `Idempotency-Key` behavior, external side-effect timing, isolation/retry, and integration or concurrency test criteria. Prose, list, or table formats inside the named block are acceptable unless a case-specific product-docs contract requires a stricter shape.

Minimum prompt diversity:

- every required scenario family has at least one public prompt
- behavior-critical families `specialist-positive`, `composite-risky`, `simple-negative`, and `eval-boundary-adversarial` each have at least two public prompt variants
- the full plugin acceptance suite has public prompts or checks in the scoped buckets needed for each scenario family; the response bucket itself should contain only response-scored cases
- across the full pack, include at least three Korean prompts, three Korean/English mixed prompts, two colloquial or ambiguous prompts, and two negative or boundary prompts
- public prompts must not reveal scenario family labels, intended routes, hard gates, scored dimensions, required evidence wording, or prior findings

Place concrete response eval cases under `workspace/develop/eval/response/cases/plugin/`. Place runtime, source, workflow, and code cases under their sibling eval buckets. Public prompt packets and private evaluator material must be separate files or directories. Forward-test agents receive only public packets and task-local raw artifacts. Place run outputs, findings, reruns, and final reports under the matching bucket's `runs/<date-or-run-id>/`.

## Required Artifacts

A complete plugin eval run records:

- evaluated git commit or working tree state
- plugin version from `dddjango/.codex-plugin/plugin.json`
- runtime cache path, if cache-backed smoke was run
- paired workspace canonical source path for any workspace-external runtime/cache change
- `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` output
- `git diff --check` output
- leakage scan command, scope, pattern set, output, and semantic/manual review notes for runtime files and current eval artifacts
- cache/source comparison output when runtime cache is used
- prompt-input or equivalent metadata exposure artifact
- public forward-test/subagent prompt packet actually supplied
- supplied context and raw artifacts actually supplied to the forward-test/subagent
- forward-test/subagent transcript or output artifact
- scenario run outputs or links to raw output files
- findings with severity and source
- rerun evidence after fixes
- final not-run list

Do not report a scenario, command, review, or subagent validation as complete unless the artifact exists.

## Pass Criteria

The plugin eval passes only when all conditions are true:

- plugin-level hard gate failures: 0
- applicable common hard gate failures: 0
- blocking findings: 0
- major findings: 0
- minor findings: 0
- every applicable scored dimension is at least 3
- `Plugin Packaging And Discoverability`, `Runtime Skill Inventory`, `Trigger And Routing Quality`, `Cross-Skill Workflow Coherence`, `Source Coverage And Provenance`, and `Runtime Sync And Verification Evidence` are 5, or a documented accepted exception explains why 5 is impossible without new source material
- every required scenario family is passed; a not-run required family must be reported with reason and prevents completion
- generated/all validation passes against `dddjango/skills`
- runtime leakage scan finds no private evaluation material under `dddjango/`
- runtime cache is either not used, or matches canonical `dddjango/` source for the evaluated plugin version

Accepted exceptions are narrow. A source limitation can justify provisional status; it cannot justify hiding the limitation or claiming full completion.

Accepted exceptions must record the linked source gap or docs conflict, owner, expiry or revisit condition, required follow-up, and why the exception does not mask a hard gate failure.

## Finding Severity

`blocking`:

- any hard gate failure
- runtime/private material leakage
- missing required skill
- stale cache reported as complete
- composite workflow contract missing in a required risky/composite case
- generated/all validation failure

`major`:

- weak routing boundary that can select the wrong specialist in realistic prompts
- incomplete source-crosswalk coverage
- incomplete cache/source sync evidence
- missing required scenario family artifact
- metadata inconsistency that does not break discovery but can mislead users

`minor`:

- wording ambiguity that must still be fixed before a completed verdict
- incomplete but non-blocking artifact labels that must still be fixed before a completed verdict
- duplicated explanation in eval docs that must still be fixed before a completed verdict
- small consistency issue that does not change runtime behavior but must still be fixed before a completed verdict

Do not downgrade repeated minor issues if they collectively make the plugin hard to evaluate.

For this rubric, `minor` means lower risk, not optional. A completed plugin eval still requires minor findings to be 0.

## Review And Iteration Protocol

Run the plugin eval in iterations:

1. Freeze the evaluated source and plugin version.
2. Run structure validation.
3. Run runtime discovery and metadata exposure smoke when runtime behavior is in scope.
4. Run required scenario families.
5. Classify each finding by defect type, scenario family, case id, artifact path, failed hard gate or scored dimension, and rerun scope. Defect type is one of `skill trigger`, `instruction`, `reference`, `workflow`, `runtime packaging`, `cache sync`, or `eval protocol`.
6. Fix source-of-truth files first.
7. Regenerate or sync runtime/cache only after canonical source is corrected.
8. Rerun the failing scenario families and required structure checks.
9. Stop only when blocking, major, and minor findings are all 0.

Self-review must cover:

- plugin packaging and runtime discovery
- dddjango product/docs alignment
- routing, workflow, and anti-overapplication
- source provenance and provisional honesty
- validation integrity and artifact completeness

Actual subagent review may be used only when it was actually run. If subagents are not used, the report must say that review was same-agent self-review.

## Public And Private Eval Boundary

Public eval packets may contain:

- task prompt
- fixture/code context
- sanitized raw files, logs, diffs, screenshots, command outputs
- task-local constraints

Public raw artifacts must be reviewed before use. If an artifact contains intended routes, scenario tags, gate mappings, scoring notes, prior findings, fixed answers, calibration material, or prior conclusions, remove that material or keep the artifact private. The `Required Evidence` column in this rubric is evaluator guidance and must not be copied into forward-test public packets.

Private evaluation material includes:

- intended route classifications
- scenario tags
- gate mappings
- scoring notes
- fixed comparison answers
- calibration samples
- suspected failures or prior conclusions not necessary for the task

Forward-test agents should receive normal user tasks, not meta instructions to validate this rubric. Skill-authoring protocol tests may mention the skill under test and path when that is the task being tested, but routing tests must not reveal intended routes.

## Runtime Leakage Policy

Runtime files under `dddjango/` must not contain:

- plugin eval pass/fail criteria
- private route classifications
- fixed answer keys
- scoring or calibration notes
- non-public failure conditions
- prior eval findings that are not user-facing runtime guidance

Rubric findings can become runtime changes only when they identify a source-backed runtime issue, such as unclear trigger wording, missing reference loading instruction, incorrect delegation boundary, or provisional misrepresentation.

Minimum leakage scan scope:

- runtime paths: `dddjango/skills`, `dddjango/.codex-plugin`, `.agents/plugins/marketplace.json`, and `plugins/dddjango` target content when applicable
- eval paths for the current run: public packets, raw artifacts, outputs, findings, reruns, and reports
- minimum text patterns: `private route`, `intended route`, `scenario tag`, `gate mapping`, `fixed answer`, `scoring`, `calibration`, `prior conclusion`, `non-public failure`, `expected route`
- semantic review: inspect matches and sampled surrounding context for paraphrased answer keys, route labels, or evaluator-only conclusions that a text pattern may miss

## Do Not Penalize

Do not penalize:

- omitting full workflow for simple tasks
- reporting runtime smoke as not run when only docs were reviewed
- using sequential fallback instead of subagents when subagents were not explicitly used
- leaving provisional skills provisional when fallback source is honestly documented
- keeping detailed eval prompt packs outside this rubric
- using product docs as source for packaging and runtime metadata rules
- using reference corpus only for domain/implementation judgment rather than plugin packaging

## Minimum Completion Report

A completion report for plugin eval must include:

- evaluated source and plugin version
- commands run and outputs summarized
- runtime cache path or not-run reason
- paired workspace canonical source path for any workspace-external runtime/cache change
- scenario families executed
- findings by severity before and after fixes
- remaining accepted exceptions, if any
- durable decision record updates
- subagent usage status
- Serena usage status or skip reason
