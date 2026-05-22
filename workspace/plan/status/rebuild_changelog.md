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

### Changed

- Planning artifacts are now separated from runtime plugin files.
- Current focus now points to P1 reference sufficiency after P0 completion.
- P4 may start after P3a only under ADR-0004; P7/P8 still require P3b or
  equivalent installed-runtime evidence.

### Fixed

- Added tracking rules for evidence, goals, reviews, and superseded documents.
- Cleared the pre-existing out-of-scope plan index diff that blocked the first
  P0 completion check, then marked P0 complete with current-file evidence.

### Blocked

- None.

### Superseded

- None.
