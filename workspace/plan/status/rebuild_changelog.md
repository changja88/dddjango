# Rebuild Changelog

This changelog tracks the rebuild process only. Do not place this file inside a
skill folder.

## Unreleased

### Added

- Plan workspace governance files.
- Phase status board.
- Naming convention and failure taxonomy.
- Artifact, evidence, review, and goal indexes.
- ADR index and initial decision records.
- Phase goal prompts for P0 through P8.
- P0 inventory evidence for the current plugin, skills, bundled resources, and
  source references.
- ADR-0004 for splitting P3 into P3a static prompt matrix and P3b runtime
  forward-test evidence.
- P4 fixture-only eval skeleton, mini-bucket fixtures, run/report/validation
  artifacts, and eval protocol.
- P4.5 runtime parity evidence for Codex marketplace, source/cache diff,
  manifest validation, install refresh, and prompt-input discovery.
- P5 individual-skill fixture preflight artifacts and runner.
- Local Codex marketplace manifest at `.agents/plugins/marketplace.json` so the
  configured repository marketplace can discover `dddjango`.

### Changed

- Planning artifacts are now separated from runtime plugin files.
- Current focus now points to P1 reference sufficiency after P0 completion.
- P4 may start after P3a only under ADR-0004; P7/P8 still require P3b or
  equivalent installed-runtime evidence.
- Current focus now points to P5 model-backed individual eval after P4.5
  runtime parity completion.

### Fixed

- Added tracking rules for evidence, goals, reviews, and superseded documents.
- Cleared the pre-existing out-of-scope plan index diff that blocked the first
  P0 completion check, then marked P0 complete with current-file evidence.
- Fixed P4 report CLI output paths and private marker evidence wording.
- Normalized P4.5 raw evidence formatting and refreshed digest records.

### Blocked

- P3b runtime forward-tests remain infrastructure-blocked because the external
  Codex/OpenAI runtime path is policy-blocked and local providers are
  unavailable.
- P5 remains incomplete until model-backed installed-runtime individual eval
  runs after the completed P4.5 parity proof.

### Superseded

- None.
