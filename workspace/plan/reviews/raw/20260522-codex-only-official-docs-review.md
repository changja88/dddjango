# Raw Reviewer Output: Codex Plugin / Official Docs Perspective

- Review date: 2026-05-22
- Reviewer: subagent `019e4f9d-a8da-7373-8005-3ae924c002b4`
- Scope: read-only review of `workspace/plan/plugin_build_plan.md` and `workspace/plan/reviews/20260522-plugin-build-plan-review.md`
- Sanitization: absolute local repository paths in reviewer output were replaced with `<repo>/...`.

## Output

Verdict: Blocker 0 / Major 4 / Minor 1

Findings:

1. Major: P2 treats `agents/openai.yaml` as Codex UI metadata only.

Issue: the plan checks display name, short description, default prompt, and trigger intent, but official Codex skill docs say `agents/openai.yaml` can also set invocation policy and tool dependencies.

Why it can cause real failure: a skill can look correct in UI while `policy.allow_implicit_invocation: false` disables expected implicit triggering, or undeclared/unavailable tool dependencies make runtime behavior fail after installation.

Concrete fix: change the P2 check from UI metadata only to Codex optional metadata: interface, invocation policy, and dependencies. Validate `policy.allow_implicit_invocation` against trigger expectations, and validate `dependencies.tools` against available/required MCP/app tools. Include those fields in stale/digest comparisons.

2. Major: plugin-root boundary scanning is too narrow.

Issue: the plan bans `workspace/reference`, absolute local paths, and path traversal only in `SKILL.md` and bundled references.

Why it can cause real failure: runtime files outside those two surfaces can still hard-code source-tree paths. Scripts, `agents/openai.yaml`, manifest asset paths, hooks, `.mcp.json`, or app mappings could work in the repository but fail from Codex's installed cache.

Concrete fix: expand the boundary scan to every runtime file under the plugin root: `.codex-plugin/plugin.json`, `skills/**/SKILL.md`, `skills/**/references/**`, `skills/**/scripts/**`, `skills/**/agents/openai.yaml`, assets, hooks, `.mcp.json`, and `.app.json` if present. For scripts, require representative execution from the installed cache with `PLUGIN_ROOT` pointing at the cached plugin root.

3. Major: P4.5 runtime parity precheck lacks the same raw evidence contract as P7.

Issue: P4.5 gates model-backed verification on install/cache parity, but the reproducible command/API evidence contract is only defined later in P7.

Why it can cause real failure: P5/P6 can be run against a stale or wrong cache and only discover the evidence gap at final packaging time.

Concrete fix: move or duplicate the P7 command evidence contract into P4.5. Before model-backed runs, require raw evidence for manifest parse, installed/cache path, marketplace source, plugin enabled state, skill count/name list, source/cache diff, and at least one `skills/list` or `plugin/read` discovery result.

4. Major: cache version matching is not aligned with local Codex plugin installs.

Issue: P7 requires Codex manifest version and installed cache version match.

Why it can cause real failure: official Codex plugin docs say local plugins are installed under a cache version of `local`. If the manifest has a semantic version, a literal cache-directory version check can falsely fail a valid local install.

Concrete fix: split the check. For local plugins, require cache path version `local` and separately record/compare the manifest `version` from source vs installed copy. For non-local marketplace installs, compare the marketplace entry/version semantics that Codex actually exposes.

5. Minor: manifest path validation is under-specified beyond `skills`.

Issue: P7 explicitly checks `skills: "./skills/"`, but official plugin docs also allow path-bearing fields for apps, MCP servers, hooks, icons, logos, and screenshots.

Why it can cause real failure: if the manifest later gains any optional path field, a bad path may evade the current checklist until install or UI rendering.

Concrete fix: add a manifest-path validation rule: every manifest path field must start with `./`, resolve relative to plugin root, stay inside plugin root, and exist when required. Also verify only `plugin.json` lives under `.codex-plugin/`.

Open questions:

- Is `dddjango` intended to remain a local/private Codex plugin through P8? If yes, the P7 version rule should explicitly use local-cache semantics.
- Will any skill declare MCP/tool dependencies in `agents/openai.yaml`? If yes, P2/P4.5 should include dependency availability evidence, not just trigger/display checks.
- Does the plugin currently include only skills, or are hooks, `.mcp.json`, `.app.json`, or interface assets planned before P8?

Pass rationale:

The Codex-only scope is correctly stated and other runtime compatibility is not an active gate in P0-P8. The plan anchors `.codex-plugin/plugin.json`, `skills/`, marketplace/cache behavior, progressive disclosure, and OpenAPI boundaries to official sources. OpenAPI is restricted to REST/HTTP API contract use and direct use is limited to `architecture-api` and `implementation-django-ninja`.

Official docs consulted by reviewer: OpenAI Codex Build Plugins, Agent Skills, and app-server API overview. Serena: skipped by reviewer because this was a read-only document review.
