# Pattern Selection

This reference is provisional and uses fallback sources until a dedicated implementation-patterns reference exists.

Load this when deciding whether to use layered, clean, hexagonal, CQRS, event sourcing, saga, transaction script, or a simpler Django-native structure.

## Selection Order

1. Confirm the DDD model: bounded context, aggregate, invariant, use case, and integration boundary.
2. Identify the pressure: external dependency, persistence mapping, transaction boundary, query/read complexity, reliability, legacy model mismatch, or testability.
3. Choose the lightest pattern that addresses that pressure.
4. State patterns intentionally not chosen and why.

## Defaults

- Layered call flow is the default fallback: interface/presentation -> application -> domain, while infrastructure implements details behind inward-facing abstractions.
- Django-native model methods plus service/selectors are enough for many projects.
- Supporting or simple CRUD subdomains can use transaction script or straightforward service functions.
- Do not introduce repository, Unit of Work, ports, or CQRS just to look like DDD.

## Pattern Triggers

| Pattern | Consider when | Avoid when |
|---|---|---|
| Layered architecture | You need clear presentation/application/domain/infrastructure responsibility | The app is simple enough that extra folders only hide the flow |
| Clean/hexagonal architecture | External adapters, SDKs, persistence, or API frameworks would otherwise shape the domain | The domain is simple and Django conventions remain clear |
| Ports/adapters | A core use case must be independent from framework or external service details | There is only one stable local implementation and no testing or replacement need |
| Repository/UoW | Aggregate persistence and transaction boundaries need a replaceable seam | It would be a thin QuerySet wrapper with no domain benefit |
| CQRS | Command and read models have genuinely different needs | A simple query method or selector is enough |
| Event sourcing | Audit, replay, or event history is central to the domain | You only need notification or integration after a state change |
| Saga | A long-running or distributed transaction needs compensation | A single local transaction can protect the invariant |
| Outbox | External message delivery must be reliable after a DB commit | There is no external side effect or at-least-once delivery need |
| ACL | An upstream/legacy model would corrupt downstream domain language | The external model already matches the bounded context language |

## Django Pragmatism

- Preserve Django advantages such as admin, migrations, forms, QuerySet, and straightforward model behavior when they do not obscure the domain.
- Split pure domain and ORM models only when ORM lifecycle, lazy loading, schema fields, or framework concerns distort the domain rule.
- Prefer incremental pattern adoption around the boundary that hurts now.
