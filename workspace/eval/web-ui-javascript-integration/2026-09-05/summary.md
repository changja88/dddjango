# Task 3 — native role chain and browser evaluation

**COMPLETE for the controlled evaluation.** Both native role chains reached independent design approval and final discipline approval. Both generated apps passed the frozen I1–I12 behavior checks, semantic S1/S2/S3 controls, and canonical B1 backstop. The preserved apps were then replayed successfully from a separate temporary root, without model regeneration. The parent Coordinator's independent Task 3 review remains a separate gate.

| Evidence | Codex | Claude |
|---|---|---|
| Final design approval | [design-review-1](codex/design-review-1.final.md) | [design-review-2](claude/design-review-2.final.md) closes the important include-host finding |
| Actual coder execution | [coder-1](codex/coder-1.final.md), exit 0 | [coder-1](claude/coder-1.final.md), exit 0 |
| Final browser evidence | [browser-5](codex/browser-5.json), I1–I12 PASS | [browser-2](claude/browser-2.json), I1–I12 PASS |
| Final independent discipline approval | [discipline-review-2](codex/discipline-review-2.final.md) | [discipline-review-2](claude/discipline-review-2.final.md), retaining four nonblocking nits from the full audit |
| Canonical backstop | [backstop-2](codex/backstop-2.txt), exit 0, 26-check banner, blocker 0, no skipped check | [backstop-1](claude/backstop-1.txt), same result |
| Preserved source | [hash manifest](codex/generated-source-hashes.json): 32 web files; 39 total app/input files | [hash manifest](claude/generated-source-hashes.json): 33 web files; 40 total app/input files |
| Independent saved-source replay | [replay-result](codex/replay/replay-result.json): browser and backstop exit 0 | [replay-result](claude/replay/replay-result.json): browser and backstop exit 0 |

The earlier Coordinator prose and one Claude closure prompt incorrectly said **34** Claude web files. The authoritative source/backstop manifests and exact hash-equality checks contain **33**. Original prompts are preserved; the count error did not change the actual checked file set.

## What ran

The external harness performed Coordinator artifact handoffs between separate native architect, independent design-review, coder and independent discipline-review invocations. No collaboration subagents or nested role workers were used by the evaluator. Requirements and observable oracle were written and hashed before generation; no UI implementation was supplied to either coder beforehand. Initial host setup contained only Django wiring, generic base blocks, design tokens and the verified official core.

**Claude:** native `claude -p --plugin-dir /Users/hyun/Desktop/dddjango/dddjango-web --agent dddjango-web:<role>`, JSONL output, no session persistence, strict MCP configuration and no Chrome integration. The successful chain resolved to **claude-opus-5** (native init context label `claude-opus-5[1m]`), medium effort. After observing that model resolution, later calls pinned the same model explicitly. User setting sources were excluded per invocation; user/global settings were not edited. Native init reports the repository plugin path and `dddjango-web@inline`, version 1.0.2.

The first Claude architect used the original configured **claude-fable-5-1** and default effort. It performed source reads but produced no Write call or design after approximately 1,215 seconds. It was recorded as a bounded timeout and only its verified runner-owned native process was terminated (exit 143). That invocation also had startup-hook permission errors and inherited repository `PWD`; the cause of noncompletion is not established and is not attributed solely to its model.

**Codex:** native `codex exec --ephemeral --skip-git-repo-check -C <temporary-app> --sandbox workspace-write --json`, with the actual current Codex distribution staged under app-local `.agents/skills/`. Explicit `$dddjango-web-<role>` and the exact local role source path were supplied. The observed CLI configuration is **gpt-6-astra**, initially xhigh, then medium per-call reasoning override. JSONL does not expose a server-response model field; [configuration evidence](codex-model-config-evidence.json) distinguishes that limitation from an observed server model identifier.

Exact argv, prompts, exit status and duration are preserved per invocation. Later [launcher metadata](claude/coder-1.launcher.json) records native subprocess cwd, inherited PWD, corrected child PWD and role source. [Claude load evidence](claude/native-load-evidence.json) and [Codex load evidence](codex/native-load-evidence.json) preserve actual Read/tool-command paths and successful command exits, plus original raw-trace paths/hashes. Both coder and full discipline audit actually read the new `implementation-javascript` knowledge. Designers also made optional JS-reference reads; the two-role direct-injection invariant concerns declared role loading, not a prohibition on other roles reading relevant knowledge.

There were eight recorded invocation attempts per runtime. Codex had six model-executing calls plus two startup failures; one failed attempt also had a harness role-name typo and never reached model execution. Claude had seven completed calls plus the first bounded timeout. Neither startup failure nor timeout is relabelled as success.

## Actual behavior and ownership coverage

Both lanes exercised two password fields with independent values/visibility, accessible pressed/action state, native Enter/Space operation and exact one-effect type assignments. They exercised two decoded local PNG previews with literal markup-containing filenames, old-resource revocation on reselect/clear, actual corrupt-image failure without stale success, native disclosure with both custom feature responses disabled, and one network load each for core and both feature scripts. Feature-disabled and delayed-completion cases are explicitly labelled test interventions.

| Boundary | Codex | Claude |
|---|---|---|
| Full UI panel replacement | A and B panels via actual HTTP; removed preview owner releases its URL, opposite panel retained | Panel B via actual HTTP; removed preview owner B releases its URL, panel A retained |
| Dependent child of retained panel | Preview-body controls replaced under the **same retained preview owner**; old dependencies disposed, new controls usable | Preview owner A itself replaced inside **retained outer panel A**; password A retained, new preview owner usable |
| Independent child near retained preview | Note inside owner, actual HTTP; owner/body/URL preserved | Note inside owner A, actual HTTP; owner/image/URL preserved |
| Repetition | Both directions, at least three of every exposed swap type | At least three of every exposed swap type, with neighbor preservation |
| Pending completion | Delay fulfillment after **real native PNG decode**, then actual note/body/panel swap; preserve valid work or make old work harmless as appropriate | Delay delivery of the app load handler after a **real native image load**, then actual note/preview-owner/panel swap; release the callback afterward |

Claude's child case does **not** prove replacement of dependent controls while retaining the same preview owner. That stronger retained-owner case is specifically covered by Codex. Claude's handler-delay intervention does not claim that native browser task ordering itself produced that delay.

Final source-app evidence:

- **Codex:** 31 real Django HTTP 200 fragment responses with distinct revisions, plus a separately labelled intercepted 503. Actual object URLs: 41 allocated / 41 revoked, no duplicate or unallocated revocation. The 503 preserves existing state; an actual Django 200 retry replaces it. Normal console errors and page errors are empty. Desktop 1280×1000 and narrow 375×812, no horizontal overflow at 375px.
- **Claude:** 16 real Django HTTP 200 fragment responses, plus a separately labelled intercepted 503. Actual object URLs: 25 allocated / 24 revoked; one valid preview remains displayed at final capture. Both genuine invalid PNG and text/plain early rejection are covered. Normal console/page errors are empty. Same desktop/narrow dimensions, recorded width 375px with no horizontal overflow.
- Both actual `manage.py check` runs report zero issues; native coders also executed Python/JS syntax and real Django-render checks. Desktop/narrow screenshots are preserved. There was no design reference, so this is rendered-functionality evidence, not visual matching to a supplied design.

S1 was accepted by actual design/code/audit roles: required local UI JavaScript is allowed. S3 assigns help disclosure to native HTML without a disclosure script. Both independent reviewer lanes explicitly rejected the isolated S2 proposal to put save authorization/final payable amount/invented business API calls in JS; the counterexample was never implemented. These semantic conclusions are reviewer evidence, not claimed deterministic checker capabilities.

## Preserved failures and owning-stage corrections

1. **Runtime startup:** Codex's inherited sandbox prevented in-process app-server initialization (EPERM). Scoped automatic approval allowed native execution while keeping the child workspace-write sandbox. Claude's initial user startup hooks hit session-env EPERM; later per-session setting-source isolation avoided that hook context. No global installation or user configuration change occurred.
2. **Initial host static prefix:** the harness omitted the canonical `web` static tuple prefix. Before coder execution, both hosts were corrected. Real `findstatic` and HTTP core/CSS checks passed; the core response SHA256 matched the pinned file. Codex's already-created design contained stale loader names, so its architect corrected only those sections before independent review.
3. **Claude output-path contract deviation:** the first completed design was written to the durable directory rather than app/design.md. The [initial artifact](claude/initial-wrong-path-design.md), [path-deviation record](claude/architect-output-path-deviation.json), and [exact-byte reviewer read proof](claude/design-review-1-source-proof.json) preserve this fact. The Coordinator copied its bytes into the app; the architect then corrected a real include-host ambiguity there, and a scoped independent design review closed it before coding. Native cwd was correct; inherited PWD was still the repository path. Whether that contributed is unproven. Later absolute write boundaries and corrected PWD were explicit.
4. **Premature browser probe:** Codex browser-2 queried a changed DOM revision before HTMX finished its real settle/load lifecycle and failed an immediate child interaction. The harness now waits for actual `htmx:afterSettle`. Browser-3 passed behavior on unchanged generated code. The original failure is retained.
5. **Common host favicon:** browser-3's remaining I12 error was automatic `/favicon.ico` returning 404. Both test hosts now return empty 204 outside generated web code. The original 404 evidence is retained. No blanket console filtering was added; later deliberate 503 console entries are separately labelled and checked.
6. **Codex discipline bounce:** initial discipline review found missing evidence for approved pending-work/bidirectional/focus/failure/narrow conditions, not a source defect. Browser-5 executed those conditions; independent discipline-review-2 closed the blocker/important findings.
7. **Claude evidence completion:** full discipline audit approved code and recorded two missing concrete branches. Browser-2 added non-image MIME and failed GET/real retry probes. Exact source hashes were unchanged, and a scoped final discipline review closed only those two omissions. Four nonblocking code nits remain documented; no optional fixes were made.

No runtime corpus or checker source was changed by Task 3. No user-repository commit, worktree, push, release or marketplace operation was performed. Canonical distribution [source hashes](distribution-source-hashes.json) identify the checked working-copy contents.

## Backstop and replay limits

Initial Codex non-Git `--all` reported zero blockers but explicitly skipped WS5. Final B1 checks use byte-identical temporary validation copies, real empty Git tree objects and `--all --diff-base <empty-tree>`; every web file is treated as new. No legacy baseline is fabricated, no finding ID suppressed, and no commit is created. Source/copy hashes match, with no skipped-mode notice in either final run.

The [replay instructions](README.md) were actually executed through `replay_preserved.py` in `/tmp/dddjango-web-js-integration-20260905/isolated-replay`, separated from the model-generated apps. Both replay browsers and backstops exited 0. Original frozen input hashes and durable app manifests were rechecked and match. Model calls were not repeated for replay.

This is one controlled generated sample per runtime, with corrective verification runs rather than statistical sampling. It covers the current new-host classic/defer setup in installed Chrome 152.0.7977.82. It does not prove legacy core layouts, module loading, all browsers, native file-picker operating-system UI, marketplace installation, full slash-command gates, production deployment, business authorization, or a broad business-logic detector. The defensive `readyState === "loading"` branch is not exercised by this defer host. Native reviewer claims of visual matching or actual execution are bounded by the supplied evidence; final human/product G2 acceptance is separate.

Serena / graphify: skipped — no opt-in markers; basic reads and temporary native/browser tools were sufficient.
