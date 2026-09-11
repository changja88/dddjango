# Task 6 independent review

## Spec compliance

**❌ Issues found.** F16 is incomplete: the current #189 promotion instruction still imposes a floor (`workspace/design/2026-08-08-tree-revision-spec.md:518`), and the reading guide retains an inconsistent remaining-rule count (`workspace/design/2026-08-08-tree-revision-spec.md:292`). The other reviewed Task 6 changes satisfy their task-scoped requirements.

**⚠️ Verification boundary:** this is the Task 6 normative/current-document/meaning-mirror and text-only source review. It does not approve the whole branch or independently re-audit the Task 1–5 AST implementation. Fresh role-pressure execution was not performed: the new normative tests check propagation, and reading the instructions establishes their expressed behavior, not how a fresh role will execute them. Whole-branch review, full `make verify`, final seal, and final field-report cleanup remain Task 7 work.

## Strengths

- The six F13 raw locations express the same complete boundary: already-caught known IntegrityError failures become the approved concrete exception, the remainder becomes the approved internal general repository failure, ownership remains domain/port, and public exposure retains safe 500 unless a stable public meaning is separately approved. They prohibit inventing ErrorCode/ErrorSchema/4xx/503 and adding an uncaught-unknown catch-all, while permitting observation and rethrow of declared exceptions. These are usable behavioral instructions rather than only a prohibition on raw exceptions: `dddjango/agents/design-architect.md:55`, `dddjango/agents/design-review-api.md:73`, `dddjango/agents/discipline-reviewer.md:94`, `dddjango/agents/discipline-reviewer.md:100`, `dddjango/skills/implementation-django-ninja/SKILL.md:32`, and `dddjango/skills/implementation-django-ninja/references/final.md:832`. Their reviewed Codex counterparts preserve the same meaning.
- The admin contract consistently preserves all five rule responsibilities. Confirmed Django/Parler slots and connected private helpers may assemble, merge, and forward open UI context, including separate form/inline/media preparation and container-presence/UI-metadata checks. Actual business consumption returns to the existing rules; unknown origin/escape remains a candidate. This avoids a class/path-wide exemption and retains annotation presence, generics/runtime treatment, and JSON validation: `dddjango/agents/design-architect.md:63`, `dddjango/skills/discipline-houserules/SKILL.md:81`, `dddjango/agents/discipline-reviewer.md:124`. The generated private-helper allowance remains an exact producer/slot join and does not replace real G2 validation (`dddjango/agents/discipline-reviewer.md:126`).
- The architect distinguishes the optional sixth effects input, explicit contradiction, unresolved candidate, and unsupported/omitted cases. It explains physical and module-pytestmark poststates separately from unchanged implementation bodies, including retained/empty/replaced marker lists and unsupported dynamic forms: `dddjango/agents/design-architect.md:87`, `:89`, `:91`, `:92`, `:93`, and `:94`. The coordinator appends effects marker/raw text to the existing hash inputs and gives declaration-confirmed findings the same closed disposition/exit-2 treatment as registry findings (`dddjango/commands/dddjango.md:96`, `:98`). The changed S1/S2/S3/S5 report strings agree with those boundaries (`dddjango/scripts/design_pregate.py:2459`).
- #642 is removed from the active rule table and owner mapping and recorded as retired; R-3410 keeps its surviving zero-part meaning. #643 and the #644 size signal survive, and #490/#644 range references exclude #642. #546 and #557 now distinguish resolved violations from unresolved candidates and give the reviewer the residual question, rather than treating lexical names as proof: `workspace/design/2026-08-08-tree-revision-spec.md:868`, `:879`, `:931`; matching predicate and owner-map hunks are present in the review package.
- The #268 change selects a truthful open/custom Enum diagnostic using the existing `enum_based` result. The `if not closed_enum and (not has_validation or enum_based)` condition and candidate grade are unchanged (`dddjango/scripts/check-domain-model.py:547`). Its new regression invokes the actual checker and distinguishes the Enum diagnostic from an ordinary VO, while the other four new tests explicitly check normative propagation (`workspace/tools/field_report_checker_smoke.py:850`, `:873`).
- Canonical/provenance discipline is preserved in the reviewed material: existing Work identities and ISSUED survive, prior Expressions remain history, and the 11 LEDGER rows are append-only. The two final source-address rows identify verified pre-Task-6 source spans without claiming an original migration date (`ontology/LEDGER.tsv:1635`, `:1636`). The metadata rulings supplied authority for those rows; approval here additionally rests on the preserved ledger prefix, unchanged source bytes, and successful recorded corpus/render checks.

## Issues

### Blocker / Critical

None found in this task scope.

### Major / Important — M1: retired promotion floor remains in current #189

**Location:** `workspace/design/2026-08-08-tree-revision-spec.md:518`.

The active #189 row still says the dispatch table gains the branch **“역할 밖 응집 단위 + 하한 충족 → 동명 폴더 승격”**. Although the span is dated, it is an operative amendment inside the current rule, not an entry in the retired-rule history. It therefore still tells a designer/reviewer to require a floor before promotion. This contradicts F16 and the intended allowance for a cohesive 20-line part, and can resurrect the rejection that retiring #642 was meant to remove. The adjacent #192 amendment was aligned, but this equally current instruction was missed.

Remove the floor precondition from that current branch while preserving the ownership/no-cross-use-case-sharing rule. Include this exact current-document residual in the focused F16 verification; a scan limited to the literal “50행” cannot detect it.

### Minor — m1: remaining-rule count was not synchronized

**Location:** `workspace/design/2026-08-08-tree-revision-spec.md:292` (current total at `:279`).

The reading guide still says that after the seven first-principle rules #486–#492, the remaining **525** rules need not run. The newly measured current total is **552**, making that remainder **545**. F16 explicitly includes the current tables and reading-guide counts. This does not change checker behavior, but leaves the human-facing explanation inconsistent with the corrected census.

Use 545, or remove the redundant hard-coded count while retaining the ordering explanation.

## Evidence and scope checks

- Reviewed the 4,975-line package covering all 44 snapshot paths, including unchanged provenance paths. Read it in bounded passes because initial larger tool outputs were truncated; repeated identical rendered text was compared with its earlier complete text, and the duplicate rulepack/checker diff bodies were confirmed equal rather than treated as omitted material. No commit-range or Git command was used.
- Named risk **snapshot/mirror drift**: independently hashed all 44 current owned paths against `task-6-final-owned-hashes.json`; zero mismatches. Independently compared the four script pairs, both reference pairs, and rulepack pair byte-for-byte; all equal. Platform-specific role/SKILL context was reviewed as meaning mirrors rather than required byte equality.
- Named risk **metadata append/source-provenance corruption**: compared the current ledger with the frozen Task 6 before ledger; the entire old prefix is unchanged and exactly 11 rows are appended. ISSUED and both frozen workspace reference-source files are byte-identical to their before copies. This focused check does not infer unavailable original migration dates.
- Named risk **semantic floor/count remnants visible in current spec context**: a focused search in that one current spec confirmed the two locations above. No broader codebase crawl or AST audit was performed.
- Inspected recorded evidence rather than rerunning suites: focused regression 5/5; checker smoke 46/46; pregate smoke 36/36; ontology gate 90/90; render sync 541 sections with red/warn/SyncDebt 0; corpus 11/11; ledger violations 0; structural gate and its 12/12 self-test; spec lint 552 rules and violations 0. The recorded initial 11 failures across five tests are expected red-phase evidence, not final-run noise. The spec-lint success does not resolve M1 or m1, which its current checks do not catch.
- No production/test/Git state was changed and no test suite was rerun. Only this review file was written. Serena and Graphify were not used, as explicitly required by the task and its opt-in constraints; no subagents were dispatched.

## Assessment

**Task quality: Needs fixes.**

The runtime-facing normative alignment is precise, the diagnostic change is narrowly scoped, and the mirrors/provenance checks support the implementation report. The remaining current promotion-floor instruction is a behavioral contradiction that must be closed before Task 6 approval; the stale count should be corrected in the same scoped pass.

## Fix round 1 independent re-review — final Task 6 verdict

**Spec compliance: ✅ Spec compliant within the Task 6 review scope.**

**Task quality: Approved. Residual findings: Blocker/Critical 0; Major/Important 0; Minor 0.** This verdict supersedes the initial Needs fixes assessment above; the initial findings remain recorded as review history.

- **M1 addressed — `workspace/design/2026-08-08-tree-revision-spec.md:518`:** the current #189 branch now reads “역할 밖 응집 단위 → 동명 폴더 승격”. Removing only “+ 하한 충족” closes the retired-floor contradiction. The role/cohesion condition, use-case ownership, cross-use-case sharing prohibition, and remaining amendment text are unchanged. The replacement agrees with the adjacent #192 exception and introduces no new permission or policy beyond the approved floor retirement.
- **m1 addressed — `workspace/design/2026-08-08-tree-revision-spec.md:292`:** the remainder is now 545, correctly equal to 552 current rules minus the seven first-principle rules #486–#492. The ordering instruction is unchanged.
- **Review evidence:** read the complete 447-line `task-6-fix1-review-package.md`, including all 44 inventory sections and both actual replacement hunks, and the implementer's Fix round 1 appendix. The package records equal before/after hashes for the other 43 paths. Inspected `task-6-fix1-spec-lint.log` (552 rules, violations 0), `task-6-fix1-diff-check.log` (empty successful output as recorded in the report), and `task-6-fix1-hash-guard.log` (only the current spec changed; 43/44 unchanged; outside-owned changes empty; exact two-replacement and ownership/count checks pass). No new breakage is apparent in either replacement. Prior evidence is reused only for unchanged corresponding files.
- **Limits:** this re-review covers closure of M1/m1 and new breakage in those two replacements; it adds no whole-branch or Task 1–5 AST approval. Fresh role-pressure execution remains unverified and is not asserted to have run. It is a stated evidence limitation, not an additional Task 7 execution requirement imposed by this review. The approved Task 7 whole-branch review, full `make verify`, final seal and report cleanup remain pending.
- **Execution:** no suite, Git command, source/test edit, broader audit, or subagent dispatch was performed during re-review. Only this review appendix was written. Serena and Graphify remain unused under the task's explicit restrictions and absent opt-in.
