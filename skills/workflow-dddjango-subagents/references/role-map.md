# Subagent Role Map

Use one role per responsibility area, not one role per file. A role may use more
than one dddjango skill when the responsibility naturally spans design and
implementation.

| Role | Responsibility | Primary skills |
| --- | --- | --- |
| Coordinator | Classify the task, assign roles, set file ownership, integrate outputs, resolve conflicts, and verify dddjango conformance | `workflow-dddjango-subagents` |
| Domain Agent | Ubiquitous language, bounded contexts, aggregates, entities, value objects, invariants, domain events | `architecture-ddd` |
| Architecture Agent | Dependency direction, ports/adapters, layered/hexagonal structure, repository, unit of work, CQRS, ACL, integration boundaries | `architecture-implementation-patterns`, optionally `architecture-ddd` |
| DB Agent | Relational modeling, constraints, indexes, transaction boundaries, locking, migration risks, query measurement | `architecture-db`, optionally `implementation-django` |
| API Agent | REST resource design, URL shape, status codes, errors, pagination, Django Ninja Schema/Router contract | `architecture-api`, `implementation-django-ninja` |
| Django Agent | Django models, services, selectors, QuerySet usage, settings, transactions, project structure | `implementation-django`, optionally `implementation-python` |
| Test Agent | TDD sequence, RED tests, pytest fixtures, integration tests, edge cases, coverage strategy | `implementation-tdd`, `implementation-test` |
| Review Agent | Severity-ranked findings, clean code, responsibility leaks, DRF violations, final dddjango convention review | `implementation-cleancode`, plus the relevant domain/API/DB/test skills |

## Role Selection

- Use Domain Agent first for business rules, state transitions, payments,
  inventory, reservations, refunds, or bounded-context questions.
- Use API Agent for any public HTTP contract or Django Ninja code.
- Use DB Agent when schema, indexes, migrations, concurrency, or transaction
  boundaries matter.
- Use Test Agent when the user asks for TDD, pytest, regression coverage, or
  behavior verification.
- Use Review Agent for review requests and before finalizing risky integrated
  changes.

## File Ownership Defaults

| Role | May own | Avoid owning |
| --- | --- | --- |
| Domain Agent | `domain/**`, domain contracts, invariant descriptions | routers, migrations, UI |
| Architecture Agent | architecture notes, ports/adapters contracts, integration boundaries | detailed endpoint schemas |
| DB Agent | `models.py`, `migrations/**`, DB constraints/index notes | HTTP route design |
| API Agent | `api.py`, `schemas.py`, error response contracts | domain invariant definitions |
| Django Agent | `services.py`, `selectors.py`, `repositories.py`, Django integration code | pytest-only files |
| Test Agent | `tests/**`, `conftest.py`, factories | production routing unless explicitly assigned |
| Review Agent | findings, patch suggestions | broad direct edits unless assigned by Coordinator |

