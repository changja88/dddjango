# Task 6 — 규범·현행 문서·미러 정합화 보고

Status: **DONE — source frozen for independent review.** This is Task6 completion only; Task7 owns final seal/full verification, final audit and approved report cleanup.

Worktree: `/Users/hyun/.cache/dddjango-field4-followup-20260911`.
Baseline: `task-6-before/manifest.json` (initial42, coordinator extended to44 for the pregate description pair) and `task-6-start-tracked-hashes.json`.

## Scope and result

31 existing Works in23 existing blocks across8 document keys were amended. Every changed Work has a new `@2026-09-11` Expression, incremented revision, `revision-amendment`, `prov:wasRevisionOf` pointing to the former current Expression and an updated currentExpression pointer. Existing Work/Expression/ISSUED history remains. No new Work was needed. Graph-owned Markdown was rendered from TTL, never directly edited.

41 of44 owned paths changed. `ontology/ISSUED` and both `workspace/reference/**/reference/final.md` sources stayed byte identical to the Task6 snapshot. The complete tracked-hash guard found zero changes outside44 owned paths. `task-6-final-owned-hashes.json` records the frozen reviewed surface; `task-6-changed-paths.json` lists the41 deltas. No primary checkout, real user project, docs/master.html, version, release, Git state, F4-20/#195 implementation, old completed report, or manifest seal was changed. No subagent was spawned.

The installed scripts still use only the standard library. Their public interfaces and detection predicates are unchanged in this task. Assigned source changes are docstrings/comments, the nine-item BLIND_SPOTS tuple's existing S1/S2/S3/S5 text, and the #268 candidate reason selected using the already-computed enum_based boolean. The existing #268 candidate condition/grade/exit is unchanged.

## Normative before/after scenarios

These are direct readings and manual application of the old/new governing text to the approved scenarios. They are **not fresh agent role execution experiments**. The four normative smoke tests prove text propagation; grep/text matches do not prove agent behavior. The independent reviewer must judge the resulting instructions. Actual CLI behavior evidence is identified separately below.

| Scenario | Direct old controlling text / resulting conflict | New expected disposition and evidence |
|---|---|---|
| Confirmed Django/Parler admin override assembles UI metadata, form/inline/media and forwards context through a private helper to framework render | R-3447/R-3448 said “Any … 어디에도 쓰지 않는다”, framework overrides must use object, and returned open object dictionaries are a leak. The generic rule could return this framework assembly as a violation; architect/reviewer lacked the same scoped instruction. | Allow confirmed framework-owned slots and connected private 전달 helper context assembly/merge/forward. Actual business value reading/comparison/calculation/state update or passing values to an ORM/use case/business function receives existing rules. Unknown origin/escape is a candidate; framework-fixed kwargs outside bare Any, unrelated business dicts and entire admin classes are not exempt. The five-rule table is shared by architect/houserules/reviewer: #493 unchanged, #645 narrow framework Any, #646 unchanged, #647 UI flow, #650 actual JSON validation unchanged. Task3's actual checker opposites run again in the46-case suite. |
| An adapter already catches IntegrityError; an approved known constraint fails | Six old raw-infra paragraphs tied internal exception normalization to approval of stable public meaning. This could prevent a required concrete internal contract merely because no new HTTP outcome was approved. | Known approved constraints become concrete contract exceptions. Repository failure contracts remain domain-owned and capability failure contracts remain port-owned. Mapping to a public response needs its own approved public meaning. The same exact F13 paragraph is present at six canonical occurrences and their platform mirrors. |
| Already-caught IntegrityError is not an approved known constraint | Old “only approved stable public meaning → normalize” wording conflicted with translating the caught remainder while retaining500. | Translate the caught remainder to the approved general repository failure contract and retain the existing safe500 response. No new ErrorCode/ErrorSchema/4xx/503, catch-all of uncaught unknown infrastructure, global classifier or exception-map DSL is introduced. Observing and reraising an already-declared contract exception is allowed. #555/contract ownership remains intact. This is normative repair, not a new checker behavior claim. |
| A20-line cohesive independent component belongs in an approved promotion | R-3417 required “클러스터 개별50행 이상”; R-3410 required the same birth floor for a new part; current #642 enforced it. That independently rejected20 lines despite cohesive ownership. | Permit promotion based on responsibility/cohesion without a line floor. #642 is retired in the current spec/owner map; #638–#641/#643 forms and #644's200-line signal stay. #192 still applies to each part. Actual checker smoke covers1/49-line parts without #642 and201 lines retaining #644. This supports the below50 boundary; the20-line cohesion judgment itself remains human. |
| A promoted directory contains only its body and __init__.py | R-3410 also owned the zero-part reversion obligation, which must not be deleted with the line floor. | Keep #643 reversion. Work R-3410 survives with the remaining meaning. Existing smoke explicitly removes the final part and sees #643. Unrelated tree-row50 references and clean-code smell50 were not changed. |
| Explicit read-only usecase plus explicit UoW, versus omitted effect declarations | Old architect counted only five inputs and the emitted S2 said every internal semantic contradiction was outside detection. That conflicts with Task1's actual declaration pass. | An explicit read-only/UoW contradiction or a proven UoW injection is declaration #197 confirmed; unresolved origins are candidates. No effect block means S5 unverified. Exact effects syntax is `path.py::UseCase read-only uow=none` / `... write uow=<type expression>` in the optional use-case-effects/effects fence. Add/update needs a preceding class declaration. Missing/invalid/duplicate declarations preserve the implemented format errors. No-effect hashes preserve the prior algorithm; supplied effect marker/raw text joins last. |
| A test update supplies an empty or replacement module marker list, or a DTO update declares nested fields | Old physical signal instructions joined only add and treated omission as absent; old S5 spoke only of OHS append support. | Update marker omission preserves current state; `[markers:]` empties and a supplied static list replaces module pytestmark. Existing bodies/decorators stay; unsupported dynamic/conditional/incremental/subscript/rebinding/nodeid shapes and base/client are S5. Declared add/update type poststate supports proven DTO origins without overwriting real bodies. Public Result/Out/Response reaches private/nested/aliased standard-container DTOs; known aggregate/entity leaks confirm #202, VO/shared VO pass, unknown origins stay candidates. Declaration ownership is architect plus relevant design reviewer/discipline reviewer, distinct from real-source checkers. |
| A generated after_commit method or admin helper lacks a real body | Generated signatures cannot prove behavior. | Only exact producer-record/location/slot joins receive S1 unverified (#376 after_commit, scoped #645/#647); #566, unrelated bare Any, unjoined/mixed records and real implementations retain their diagnoses. S1 never substitutes for G2 behavior checks. |

The old exact source texts are preserved in `task-6-blocks-before.json`. `task-6-block-changes.json` records full before/after blocks, so each scenario's changed clause is reviewable without reading the whole plan.

## Current descriptions and bounded support

- #546 and #557 now consistently have `ast+` grade and checker+discipline-reviewer ownership in spec, predicates and owner map. #546 confirms different repository/aggregate types only within resolved transaction regions, separates sequential UoWs, combines nested/outer atomic regions, and asks about unresolved boundaries. Same-type instance identity is not implemented. #557 confirms resolved vendor attribute receivers, allows resolved domain/application command/query/result/port contracts, and keeps unknown/mixed/rebound origins as candidates. Names or except syntax alone are not origin proof.
- #153's header/predicate reflect proven execute count, unresolved/multiplicity candidates and exclusion of builder preparation/uncalled nested definitions. #268 distinguishes closed standard Enum/StrEnum/IntEnum exemption from custom/open Enum uncertainty; its candidate diagnostic no longer falsely says a custom constructor with raise has none.
- The active rule census is552: path172, ast290, ast+63, human27. The matrix is blocker500, checker20, transition10, exempt22. Deterministic path+ast blockers432, ast+ blockers62, human blockers6. The introductory count tables, cross-table and reading guide now agree. #490/#644's obsolete range no longer semantically includes642 (`#638~#641·#643`). Historical independent counts were retained.

## Work / block map

### agent-design-architect

- `s005/b11`: R-1617
- `s005/b33`: R-3424, R-3431
- `s005/b34`: R-3425
- `s005/b35`: R-3426
- `s005/b36`: R-3427
- `s005/b37`: R-3428, R-3429

### agent-design-review-api

- `s006/b11`: R-2677

### agent-discipline-reviewer

- `s007/b23`: R-1037
- `s007/b29`: R-1071
- `s007/b51`: R-1117, R-1118
- `s007/b46`: R-1104
- `s007/b52`: R-1119

### command-dddjango

- `s006/b9`: R-3432, R-3433, R-3434, R-3435, R-3436
- `s006/b10`: R-3445

### discipline-houserules-final

- `s003-0/b10`: R-3410
- `s003-0/b12`: R-3468

### discipline-houserules-skill

- `s007-4/b7`: R-3447, R-3448
- `s007-4/b8`: R-3451
- `s007-4/b10`: R-3452
- `s007-4/b15`: R-3457
- `s004-1/b7`: R-3417

### implementation-django-ninja-final

- `s023-6.2/b33`: R-0084

### implementation-django-ninja-skill

- `s004/b10`: R-2941

## Metadata and generation order

Canonical sequence was TTL edit → canonical serializer → ontology gate → render each of the8 keys → `make rulepack` → `corpus_mirror_sync.py --write` → platform meaning mirrors/current documents → targeted gates. Final semantic refinements repeated the canonical chain with check=True-style sequential failure stops in `task-6-final-generate.py`; the final authoring run is `task-6-ontology-gate-final.log`. The helper's first attempt lacked CanonSerializer's required allow_lists argument and failed before writing any TTL; it was corrected toFalse. This was an authoring helper error, not a passing gate.

Six Codex role/SKILL files were minimally updated from the23 changed blocks (20 role/SKILL blocks;3 reference blocks use byte mirroring). Codex-specific skill references, dispatch timing and “Phase2 6번” wording were retained. References and both rulepacks are generated byte mirrors. No blanket Markdown regeneration or platform-format replacement occurred.

`ontology_render_sync.py` checks graph-section baseline hashes as well as rendered equality. After graph rendering it reported9 baseline mismatches; the coordinator confirmed that the brief's NAR-only shorthand omitted this existing gate requirement. Nine append-only graph metadata rows update baseline_sha256 while preserving old owner/count/provenance fields. No NAR section changed. Exact rows/hashes are in `task-6-rebaseline-rows.json`:

- `agent-design-architect/s005` — `273e582ab5bf506a12a5d02a373b7ae5f09a769d2fda6de7275a004b5f1f868e`
- `agent-design-review-api/s006` — `c05d22c6bf514bb82cc894518be0e291f1362332f3518c52379f5f04baeb52c9`
- `agent-discipline-reviewer/s007` — `afd8ca21c14cb27e2089e14a00cf7bf5c6fe0af4dbf8966c872c580847d1cb0d`
- `command-dddjango/s006` — `288b3693a492dee2b39c07dfa3c330eb7832060c11175494ed37d3c61e012205`
- `discipline-houserules-final/s003-0` — `337f2f48e8157c93be09c8431e909b638192d8eb9b4068a7f2ae6258f251722d`
- `discipline-houserules-skill/s004-1` — `a1df8096b8c764514d96383c87200e93f8771f97f6bbccc6398a293d8b162331`
- `discipline-houserules-skill/s007-4` — `40c1c8416963eaf8c72560627b272c8ccf2bd63dcf4d2fb7cbb215fc1f04e5df`
- `implementation-django-ninja-final/s023-6.2` — `68ea52bea42066fd7d5d2f22e08f089fe392fba9d1af66d321935b70a8b0e70d`
- `implementation-django-ninja-skill/s004` — `ffe4dcd624079791fb136eb456a4edc39ffb8994d879dba9ab895cca16555a2d`

After these appends, corpus sync returned structure2: the two frozen workspace source spans were addressed only by their previous effective baseline because migrated_sha256 was `-`. The coordinator independently verified each old source span and approved two further metadata appends. They keep the current baseline/owner/counts and put the **verified pre-Task6 preserved source address** in the existing migrated_sha256 field; they do not assert an original migration date and do not overwrite any real existing migrated hash. Exact rows are `task-6-source-address-rows.json`:

- discipline-houserules-final/s003-0: `1b4fddca027005fc52618807bbbea8b088d5b77b141c29d404a09dd9747ae5f1`
- implementation-django-ninja-final/s023-6.2: `11b862b4cbcab5bf329b7fa3939e97c6813446543bbb1604ebd2f60b4ad2eba2`

Final corpus11/11, render sync541/red0 and ledger0 confirm the metadata resolution. Both original workspace sources remain byte unchanged. No census/normalization file outside44 needed editing; no seal was issued.

## Commands and evidence

All logs below are beside this report. Environment: worktree above, scripts invoked with their assigned installed/runtime interpreter. Only temporary fixtures were exercised; no real user application was imported or executed.

| Stage | Exact command | Result / final evidence |
|---|---|---|
| RED | `PYTHONPATH=workspace/tools python3 -B -m unittest field_report_checker_smoke.CheckerRegression.test_open_enum_reason_does_not_claim_constructor_raise_is_absent field_report_checker_smoke.NormativeContractRegression` |5 tests,11 expected failures, `task-6-red.log`. Real CLI custom Enum reason failed; ordinary VO control kept its correct old reason. Norms failed at missing/contradictory contract phrases. |
| Focused GREEN | Same command |5/5, `task-6-focused-green.log`. |
| Final authoring gate | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py` |90 files green,0 red; `task-6-ontology-gate-final.log`. |
| Final render | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render.py --apply <doc_key>` for agent-design-architect, command-dddjango, discipline-houserules-skill, discipline-houserules-final, agent-discipline-reviewer, agent-design-review-api, implementation-django-ninja-final, implementation-django-ninja-skill |All8 exit0; `task-6-render-final-<doc_key>.log`. |
| Final rulepack | `make rulepack` |exit0; `task-6-rulepack-final.log`; both generated packs byte identical. |
| Metadata RED | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render_sync.py` |9 baseline mismatches; `task-6-render-sync.log`. The earlier exploratory `task-6-sync-preflight.log` preceded final rendering and is not final evidence. |
| Corpus source-address RED | `python3 -B workspace/tools/corpus_mirror_sync.py --write` |structure2/exit3 after baseline append; `task-6-corpus-after-ledger.log`. No source was rewritten. |
| Corpus final | `python3 -B workspace/tools/corpus_mirror_sync.py --write` |11/11 in-sync, exit0; `task-6-corpus-final-green.log`. |
| Render sync final | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render_sync.py` |541 sections, red0/warn0/SyncDebt0; `task-6-render-sync-final-green.log`. |
| Ledger final | `python3 -B workspace/tools/ontology_ledger_check.py` |violations0; `task-6-ledger-final-green.log`. |
| Structural | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_structural_check.py` and same with `--self-test` |Both exit0; `task-6-structural.log`, `task-6-structural-selftest.log`. |
| Spec final | `python3 -B workspace/tools/spec_lint.py` |552rules, all8 checks, violations0; `task-6-spec-lint-final.log`. |
| Covering checker smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/field_report_checker_smoke.py` |46/46,15.024s, exit0; `task-6-checker-smoke.log`. Prior41 plus new focused diagnostic1 and normative propagation4. |
| Covering pregate smoke | `PYTHONPATH=workspace/tools python3 -B workspace/tools/pregate_field_report_smoke.py` |36/36,51.641s, exit0; `task-6-pregate-smoke.log`. |
| Scoped self-review | `python3 -B .superpowers/sdd/2026-09-11-field-report-4-followup/task-6-self-review.py` |Compile5, script byte pairs4, reference pairs2, exact platform-transformed meaning blocks20, ownership hash guard0; `task-6-self-review.log`. |
| Diff | `git diff --check` |exit0; `task-6-diff-check.log`. |

No green behavior suite was repeated without a source reason. The46/36 suites cover the final source and normative text. Later changes only aligned ledger source addresses and introductory count numbers; corpus/render/ledger/spec were rerun for those concrete metadata/document changes. Full make verify, seal and independent final audit are Task7.

## Manual and generated paths

Manual canonical/current-description/meaning-mirror/test/metadata changes:

- `ontology/rules/agent-design-architect.ttl`
- `ontology/rules/agent-design-review-api.ttl`
- `ontology/rules/agent-discipline-reviewer.ttl`
- `ontology/rules/command-dddjango.ttl`
- `ontology/rules/discipline-houserules-final.ttl`
- `ontology/rules/discipline-houserules-skill.ttl`
- `ontology/rules/implementation-django-ninja-final.ttl`
- `ontology/rules/implementation-django-ninja-skill.ttl`
- `codex-dddjango/skills/implementation-django-ninja/SKILL.md`
- `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md`
- `codex-dddjango/skills/dddjango/SKILL.md`
- `codex-dddjango/skills/dddjango-design-architect/SKILL.md`
- `codex-dddjango/skills/dddjango-design-review-api/SKILL.md`
- `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`
- `workspace/design/2026-08-08-tree-revision-spec.md`
- `workspace/design/2026-08-11-predicates.md`
- `workspace/plan/2026-08-11-rule-owner-map.md`
- `docs/file_tree.html`
- `docs/mkrev2.py`
- `ontology/LEDGER.tsv`
- `workspace/tools/field_report_checker_smoke.py`
- `dddjango/scripts/check-context-isolation.py`
- `dddjango/scripts/check-domain-model.py`
- `dddjango/scripts/check-port-adapter-pairing.py`
- `dddjango/scripts/design_pregate.py`

Rendered or byte-generated outputs (checker descriptions originate in their Claude script counterpart):

- `dddjango/skills/implementation-django-ninja/SKILL.md`
- `dddjango/skills/implementation-django-ninja/references/final.md`
- `codex-dddjango/skills/implementation-django-ninja/references/final.md`
- `dddjango/skills/discipline-houserules/SKILL.md`
- `dddjango/skills/discipline-houserules/references/final.md`
- `codex-dddjango/skills/dddjango-discipline-houserules/references/final.md`
- `dddjango/commands/dddjango.md`
- `dddjango/agents/design-architect.md`
- `dddjango/agents/design-review-api.md`
- `dddjango/agents/discipline-reviewer.md`
- `dddjango/scripts/rulepack.json`
- `codex-dddjango/skills/dddjango/scripts/rulepack.json`
- `codex-dddjango/skills/dddjango/scripts/check-context-isolation.py`
- `codex-dddjango/skills/dddjango/scripts/check-domain-model.py`
- `codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py`
- `codex-dddjango/skills/dddjango/scripts/design_pregate.py`

## Self-review and limits

I reviewed all four source-description diffs against the Task6 snapshot (`task-6-source-diff-*.txt`), all changed Work/block text, the five-rule admin table, six F13 occurrences, #642 retirement with #643 preservation, current ownership/grades and exact Codex adaptations. The added conditional changes only the #268 candidate message. Existing candidate eligibility and all Task1–5 producer/record/annotation interfaces remain intact. The preflight snapshot and final hash guard distinguish this task from earlier Task1–5 implementation present in the worktree.

No known failing executed targeted gate remains. Normative text checks and this manual scenario review do not establish how a fresh architect/reviewer agent behaves under pressure; independent review remains required. Unknown types, dynamic admin/helper flows, unknown transaction regions, custom/open Enums and vendor origins remain candidates/unverified as described. #195/F4-20 remains outside this task, and original unresolved report cleanup is not claimed.

Serena/Graphify were not used because this worktree has no opt-in; neither was searched, loaded or initialized. No subagents were spawned. Source is frozen for the coordinator's independent review.

## Fix round 1/5 — independent review M1 and m1

Status: **DONE — source frozen again for independent re-review.** Read `task-6-review.md` and applied receiving-code-review guidance: both findings were checked against the actual current spec before editing. The review was correct that an operative dated amendment can retain the retired floor even without the literal “50행”.

Only `workspace/design/2026-08-08-tree-revision-spec.md` changed relative to `task-6-fix1-before/manifest.json`:

- **M1, current #189:** `역할 밖 응집 단위 + 하한 충족 → 동명 폴더 승격` became `역할 밖 응집 단위 → 동명 폴더 승격`. All other text of #189 is preserved, including each usecase's ownership and the prohibition on sharing its parts with another usecase. The already-documented cohesive 20-line scenario now has no contradictory floor in this current branch.
- **m1, reading guide:** the remaining-rule count changed from 525 to **545**, matching the measured total 552 minus the seven first-principle rules #486–#492. The ordering explanation is unchanged.

Exact round diff: `task-6-fix1.diff`. There were no runtime, test, TTL, generated mirror, rulepack, ledger, provenance or AST changes. No new test was added for these two reversible text changes, as directed by the coordinator. Prior functional/canonical evidence is reused only for the unchanged corresponding files; no broad suite was rerun.

| Verification command | Result / log |
|---|---|
| `python3 -B workspace/tools/spec_lint.py` | exit 0; `규칙 552 · path 172 · ast 290 · ast+ 63 · human 27 · ⑧ 포함`, `위반 0건`; `task-6-fix1-spec-lint.log` |
| `git diff --check` | exit 0, no output; `task-6-fix1-diff-check.log` |
| `python3 - <<'PY'` inline SHA-256/snapshot comparison | exit 0; exactly the current spec changed, **43/44 owned files unchanged**, outside-owned tracked changes `[]`; `task-6-fix1-hash-guard.log`. It additionally compared the full after text with the before text plus exactly the two replacements above, asserted the no-floor branch and retained cross-usecase ownership clause, and checked `552 - 7 == 545`. |

The hash comparison loaded `task-6-fix1-before/manifest.json`, compared `sha256(Path(path).read_bytes()).hexdigest()` for every path, and required the changed path list to equal only the current spec. It separately compared every path outside that manifest against `task-6-start-tracked-hashes.json`. `task-6-final-owned-hashes.json` was refreshed for the re-review; all 43 other recorded hashes remain unchanged.

No new policy choice, source behavior or broader completion claim was introduced. No seal, full make verify, F4-20/#195 work, master.html edit, Git mutation or subagent activity occurred. Serena/Graphify remain unused because opt-in is absent.
