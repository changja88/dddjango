# Raw Reviewer Output: Skill-Creator Perspective

- Review date: 2026-05-22
- Reviewer: subagent `019e4f9d-a6a2-7fa3-88bb-f2e5dc338336`
- Scope: read-only review of `workspace/plan/plugin_build_plan.md` and `workspace/plan/reviews/20260522-plugin-build-plan-review.md`
- Sanitization: absolute local repository paths in reviewer output were replaced with `<repo>/...`.

## Output

Verdict: Blocker 0 / Major 5 / Minor 2

Findings:

1. Major: review record stores raw reviewer output as conversation notification IDs, not durable raw artifacts or full pasted output.

Why it can cause real failure: the plan's validation integrity depends on auditable evidence, but future agents cannot inspect those notification IDs from the repository. That recreates a self-certification path.

Concrete fix: store each raw reviewer output as a sanitized file under `workspace/plan/reviews/raw/` or paste the full output into the review file. Add input artifact digests and link exact raw files from the summary.

2. Major: the plan still does not clearly require actual installed Codex skill usability as a final gate.

Why it can cause real failure: a skill can validate structurally, appear in a list, and pass a runner that assembles prompts manually, while real Codex users still fail to trigger or use it correctly from the installed plugin.

Concrete fix: add a P7/P8 gate: for every high-risk trigger family, run at least one installed-runtime Codex user-like task, capture actual skill loaded, source/cache path, final answer/artifacts, and false-trigger/exclusion behavior.

3. Major: concrete user examples are not a first-class input before skill trigger/body design.

Why it can cause real failure: skills may become well-sourced but badly triggered because descriptions can mirror internal taxonomy rather than user language.

Concrete fix: insert a P1.5 before P2: for each trigger family, define 2-3 realistic user prompts, one exclusion prompt, expected skill/resource loads, expected artifact behavior, and common non-goals.

4. Major: concision is checked mostly by frontmatter fields and `SKILL.md` line count.

Why it can cause real failure: skill metadata is always in context. Long descriptions across many skills can dilute triggering and consume context before any skill is loaded.

Concrete fix: add measurable concision gates: description max words/chars, body max approximate tokens/words, no duplicated sections between `SKILL.md` and bundled references, and body contains only workflow/resource navigation plus essential rules.

5. Major: forward-test contamination control is still too vague.

Why it can cause real failure: later agents can accidentally discover prior expected triggers, routing observations, or failure diagnoses from the repo and pass by leakage rather than by usable skill design.

Concrete fix: run forward-tests in a clean temp workspace containing only the plugin/skill under test and task-local artifacts. Store transcripts after the run, outside the visible test workspace. Record a contamination check showing the subagent could not access prior reviews, eval outputs, or forward-test artifacts.

6. Minor: for bundled references over 100 lines, the plan allows "TOC and search keywords or section anchor." The skill-creator guidance values a top TOC.

Concrete fix: require a top table of contents for every bundled reference over 100 lines. Treat search keywords/anchors as optional additions.

7. Minor: bundled resource rules do not explicitly require pruning unused `scripts/`, `references/`, and `assets/` resources.

Concrete fix: add a P2 gate that every bundled resource is referenced by `SKILL.md` or a declared script contract, has a stated use condition, and unused placeholder/stale resources are removed.

Open questions:

- What command or harness will prove actual skill loaded from the installed Codex runtime, rather than source-path prompt assembly?
- Can forward-tests be run in clean temp workspaces with prior `workspace/plan/**` artifacts hidden?
- What is the authoritative set of user-like prompt examples per trigger family?
- Where will raw reviewer outputs be stored so future agents can audit them without conversation-only IDs?
- Which model IDs and runner destinations are acceptable for the two-pass model-backed runs?

Pass rationale:

No blockers from the skill-creator perspective. The remaining risk is execution realism: the plan is still heavier on review/eval proof than on proving a fresh Codex user can discover, trigger, and use installed skills without leaked context.

Serena: skipped by reviewer because this was a read-only document review.
