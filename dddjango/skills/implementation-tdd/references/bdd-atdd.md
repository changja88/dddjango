# BDD And ATDD

Use this reference for the relationship between TDD, ATDD, and BDD, and for the handoff boundary with detailed BDD tooling.

## Relationship

- TDD focuses on executable tests that drive code correctness and design feedback.
- ATDD uses acceptance tests to clarify externally visible behavior before or during implementation.
- BDD extends the acceptance-test idea with business-readable behavior language and stakeholder collaboration.
- In a double-loop flow, an acceptance or BDD scenario can anchor the outer loop while unit tests drive the inner Red-Green-Refactor loop.

## Boundary

- This skill owns when BDD/ATDD belongs in a TDD flow and how it affects test sequencing.
- Use `implementation-test` for pytest-bdd, Gherkin, fixtures, step definitions, test data factories, and concrete test implementation mechanics.
- If acceptance criteria, domain language, or policy ownership is unclear, use `architecture-ddd` before turning scenarios into fixed test expectations.
