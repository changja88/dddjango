# Role Map

Load this for the canonical dddjango workflow roles. Do not reduce responsibilities or remove related skills when copying this map into workflow output.

| Role | Responsibility | Related skills |
|---|---|---|
| Coordinator | Work scope, role assignment, result integration | `workflow-dddjango-subagents` |
| Domain Agent | Subdomain, context, language, aggregate, invariant, domain event | `architecture-ddd` |
| Architecture Agent | Implementation pattern, dependency direction, port/adapter, transaction boundary | `architecture-implementation-patterns` |
| DB Agent | Schema, constraints, indexes, transactions, rollout constraints, backfill/index-lock risk | `architecture-db`, optionally `implementation-django` |
| API Agent | REST contract, status code, Problem Details, OpenAPI | `architecture-api`, `implementation-django-ninja` |
| Django Agent | ORM, service, selector, concrete migration files, transaction, settings/security/performance, template/static/web, templates/static files | `implementation-django`, `implementation-django-web`, `implementation-python` |
| Test Agent | TDD flow, pytest, fixtures, test doubles, API/integration tests, ownership of `tests/**` files | `implementation-tdd`, `implementation-test` |
| Review Agent | Code quality, design risk, missing verification, regressions | `implementation-cleancode` |

Domain Agent decisions feed DB Agent, API Agent, Django Agent, and Test Agent. Coordinator integrates the outputs and resolves conflicts using integration priority.

## Output Guidance

For composite or risky workflow output, include the full role map with all roles. Mark a role as not editing or advisory when it has no active work, but do not omit the role, narrow its responsibility, or reduce its related skill list. If Django web template/static work is in scope, Django Agent must include `implementation-django-web`.
