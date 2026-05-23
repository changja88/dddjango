수정 대상: P4.5 runtime parity precheck analysis for Codex dddjango source/cache/install/discovery state.

# P4.5 Runtime Parity Precheck Analysis

## Scope

- Source plugin: `dddjango/`
- Source manifest: `dddjango/.codex-plugin/plugin.json`
- Marketplace root configured in Codex: `/Users/hyun/Desktop/dddjango`
- Installed cache root: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`
- Phase evidence root: `workspace/plan/phases/p4-5-runtime-parity/evidence/`

## Initial Finding

Before the precheck fix, Codex had `dddjango@dddjango-local` enabled in
`/Users/hyun/.codex/config.toml` and an installed cache directory existed, but
`codex plugin marketplace list` and `codex plugin list --marketplace
dddjango-local` failed because the configured marketplace root
`/Users/hyun/Desktop/dddjango` did not contain a supported marketplace
manifest.

That made the current install/cache state too weak for P5/P6 model-backed eval:
the installed cache could be compared to source, but Codex CLI discovery could
not prove the configured marketplace/source was currently readable.

## Narrow Fix

Added `.agents/plugins/marketplace.json` at the repository root. This is a root
exception because Codex is already configured to use the repository root as the
local marketplace root, and Codex requires the marketplace metadata at that
platform-specific path.

The marketplace entry points to the actual plugin root:

- marketplace: `dddjango-local`
- plugin: `dddjango`
- source path: `./dddjango`
- policy: `AVAILABLE` / `ON_INSTALL`
- category: `Coding`

No runtime skill or reference file was changed.

## Completion Evidence Required

- Codex marketplace discovery must list `dddjango-local`.
- Codex plugin discovery must list `dddjango@dddjango-local` as installed and
  enabled.
- Codex install/cache refresh must report the installed cache path.
- Source/cache diff must be empty between `dddjango/` and the installed cache.
- Manifest validation must parse source/cache manifests, keep all manifest paths
  inside their plugin roots, and report matching skill names/counts.
- Runtime link-boundary check must show no Markdown links to paths outside the
  plugin root.
- Prompt-input discovery smoke must show at least one dddjango skill exposed
  from the installed cache.

## P3b Boundary

This phase proves install/cache/discovery parity only. It does not resolve P3b
runtime-routing evidence deferred by ADR-0004 and does not replace the P7/P8
requirement for P3b or equivalent installed-runtime user-like evidence.
