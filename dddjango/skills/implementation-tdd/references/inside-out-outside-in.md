# Inside Out And Outside In

Use this reference to choose classic vs London TDD, state vs behavior verification, and double-loop TDD.

## Approach Selection

- Use Inside-Out for pure domain logic, value objects, algorithms, and rules that can be tested with real objects.
- Use Outside-In when discovering an end-to-end feature shape, adapter contract, or external collaboration boundary.
- Mix approaches when useful: acceptance test for the user-visible slice, then unit tests for domain rules.
- For complex/risky dddjango work, coordinate with `workflow-dddjango-subagents` before assigning role-owned tests.

## Verification Style

- Prefer output-based tests for pure functions and deterministic domain calculations.
- Use state-based tests for object behavior where state is the observable result.
- Use behavior/communication verification for external roles such as gateways, repositories, notifiers, or adapters.
- Mock roles, not arbitrary implementation objects.
- Avoid over-mocking domain logic; it lowers refactoring resistance.

## Double Loop

- Outer loop: acceptance/API/integration test captures the user-visible behavior.
- Inner loop: smaller unit tests drive domain/application pieces.
- Walking skeleton is useful when architecture wiring must be proven end to end before depth is added.
