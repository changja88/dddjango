# ADR-0004: P3 Runtime Forward-Test Deferral

Status: accepted
Date: 2026-05-23
Phase: p3
Decision Owner: codex
Supersedes: none
Superseded by: none

## Context

P3 originally required fresh isolated user-like runtime forward-tests before P4.
The forward-test prompt matrix was created, but actual Codex/OpenAI runtime
execution was blocked by tenant policy even after user approval. Local OSS
providers were also unavailable: Ollama had no running server, and LM Studio did
not respond.

Keeping P3 as a single hard gate would stop all later eval-system work even
though the static/user-prompt matrix is available and useful as input to P4.
Marking P3 complete would be false because no actual loaded-skill/final-answer
evidence exists.

## Options Considered

- Stop at P3 until an approved external or local runtime is available.
- Mark P3 complete based on the prompt matrix alone.
- Split P3 into a completed static prompt-matrix gate and a deferred runtime
  forward-test gate.

## Decision

P3 is split into two gates:

- P3a static/user-prompt matrix: can be treated as complete when prompt matrix,
  blocked runtime evidence, indexes, and governance validation are current.
- P3b runtime forward-test: remains `infrastructure-blocked` until an approved
  external Codex/OpenAI runtime or a running local/offline provider can produce
  actual loaded-skill, final-answer, routing, overclaim, and leakage evidence.

P4 may start after P3a is complete and this ADR is accepted. P4, P5, and P6
must record that runtime routing evidence is deferred. P7 and P8 cannot be
complete until P3b runtime forward-test evidence is current, or until a later
accepted ADR replaces this gate with an equivalent installed-runtime evidence
gate.

## Consequences

- `p3-forward-tests` is not recorded as fully complete while P3b is blocked.
- P4/P5/P6 outputs are provisional with respect to runtime routing until P3b is
  resolved.
- P7/P8 remain hard gates for installed runtime/user-like evidence.
- Future agents must not claim final plugin completion from P3a, P4, P5, or P6
  alone.

## Evidence

- `workspace/plan/phases/p3-forward-tests/prompts/20260522-234529-p3-eval-forward-tests-prompt.md`
- `workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-evidence.md`
- `workspace/plan/phases/p3-forward-tests/evidence/20260522-234529-p3-eval-forward-tests-raw.md`
- `workspace/plan/status/phase_status.md`
