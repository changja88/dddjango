# ADR-0001: Codex-only P0-P8 Scope

Status: accepted
Date: 2026-05-22
Phase: p0
Decision Owner: user
Supersedes: none
Superseded by: none

## Context

The rebuild target is the dddjango Codex plugin. Prior work mixed broader
runtime compatibility concerns into the same completion path, which made success
criteria harder to verify.

## Options Considered

- Build for Codex first, then handle other runtimes separately.
- Build one shared cross-runtime completion plan.

## Decision

P0-P8 are Codex-only. Other runtime compatibility is optional P9 work and cannot
block or certify the Codex plugin rebuild.

## Consequences

- Codex official plugin and skill rules are the active runtime source.
- Other runtime files must not be used as Codex completion evidence.
- If compatibility work is needed later, it gets its own source ledger, plan,
  evidence gates, and decision records.

## Evidence

- `workspace/plan/plugin_build_plan.md`
- OpenAI Codex skills documentation: https://developers.openai.com/codex/skills
- OpenAI Codex plugin documentation: https://developers.openai.com/codex/plugins/build

