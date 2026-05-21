# Role Map

Canonical dddjango workflow roles를 확인할 때 읽는다. Workflow output에 복사할 때 role responsibility나 related skills를 줄이지 않는다.

| Role | Responsibility | Related skills |
|---|---|---|
| Coordinator | Work scope, role assignment, result integration | `workflow-dddjango-subagents` |
| Domain Agent | Subdomain, context, language, aggregate, invariant, domain event | `architecture-ddd` |
| Architecture Agent | Implementation pattern, dependency direction, port/adapter, transaction boundary | `architecture-implementation-patterns` |
| DB Agent | Schema, constraints, indexes, transactions, rollout constraints, backfill/index-lock risk | `architecture-db`, `implementation-django` |
| API Agent | REST contract, status code, Problem Details, OpenAPI | `architecture-api`, `implementation-django-ninja` |
| Django Agent | ORM, service, selector, concrete migration files, transaction, settings/security/performance, template/static/web, templates/static files | `implementation-django`, `implementation-django-web`, `implementation-python` |
| Test Agent | TDD flow, pytest, fixtures, test doubles, API/integration tests, ownership of `tests/**` files | `implementation-tdd`, `implementation-test` |
| Review Agent | Code quality, design risk, missing verification, regressions | `implementation-cleancode` |

Domain Agent decisions feed DB Agent, API Agent, Django Agent, and Test Agent. Coordinator integrates the outputs and resolves conflicts using integration priority.

## Output Guidance

Composite 또는 risky workflow output에는 모든 role을 포함한다. Active work가 없으면 advisory 또는 read-only로 표시하되 role을 생략하거나 responsibility, related skill list를 줄이지 않는다. Django web template/static work가 범위에 있으면 Django Agent는 `implementation-django-web`, `templates/**`, `static/**`, templates/static files ownership을 포함해야 한다.
