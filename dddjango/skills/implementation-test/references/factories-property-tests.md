# Factories And Property Tests

Load this when test data setup is noisy, many examples are needed, invariants must hold over broad input spaces, or a BDD-style scenario is requested.

## Factories

- Use factories when repeated object creation hides the behavior under test.
- Keep factory defaults valid, minimal, and unsurprising.
- Use `Sequence` for unique values, `Faker` for realistic but irrelevant data, `LazyAttribute` for values derived from other fields, and `LazyFunction` for values generated at creation time.
- Use `SubFactory` for required relationships and `RelatedFactory` when reverse relationships are the natural setup.
- Use `Trait` for meaningful states such as `paid`, `shipped`, `cancelled`, `expired`, or `published`.
- Use `create_batch` for volume cases and reseed factory randomness when reproducibility matters.
- For Django models, use `factory.django.DjangoModelFactory` and `django_get_or_create` only when the model's unique identity should be reused.
- For SQLAlchemy models, use `factory.alchemy.SQLAlchemyModelFactory` with explicit session handling when that project stack is in scope.

Factory data should make the assertion easier to read. If a one-line literal setup is clearer, do not introduce a factory.

## Property-Based Tests

- Use Hypothesis when behavior is an invariant, round trip, ordering property, validation rule, state transition, or algebraic law.
- Use ordinary example tests for named business examples and boundary cases; use property tests to explore the larger input space.
- Compose strategies with explicit constraints such as `min_value`, `max_value`, `min_size`, `max_size`, `allow_nan=False`, and `allow_infinity=False`.
- Add `@example` for business-critical boundary values that must always be tested.
- Tune `@settings` only for a reason: more examples in CI, deadlines for slow checks, or suppressed health checks that are understood.
- Use stateful testing when correctness depends on a sequence of operations, and compare against a simple reference model when possible.

Avoid property tests whose assertions only restate the implementation. The property must express behavior that would remain true after refactoring.

## BDD With pytest-bdd

- Use Given-When-Then when product language and stakeholder-readable scenarios matter.
- Put stakeholder-readable behavior in `.feature` files and connect each scenario with `@scenario("path/to.feature", "Scenario name")`.
- Use `parsers.parse(...)` for parameterized step text and `target_fixture` when a step should provide data to later steps.
- Keep Given steps as setup, When as the single behavior, and Then as observable outcomes.
- Do not hide complex assertions behind vague step names.
- Store reusable domain language in feature files only when the team will actually read or maintain them.
- Do not adopt pytest-bdd only to decorate developer-only tests; plain pytest is clearer when stakeholders will not read the scenarios.
