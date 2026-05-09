# Encapsulation And Abstraction

Use this reference for information hiding, deep modules, object design, SOLID, DRY, error handling, and dependency management.

## Encapsulation

- Expose stable behavior and intent; hide representation, ordering requirements, and invariant maintenance.
- Tell objects what to do instead of pulling their internals apart and applying rules outside them.
- Keep data and the logic that protects that data close together unless there is a clear boundary reason to separate them.
- Keep variable/state scope and lifetime as narrow as the behavior allows.
- Use value objects for immutable meaningful values when mutation or primitive obsession hides rules.
- Avoid exposing public mutable state when callers can use an intention-revealing method or read model instead.

## Abstraction

- Prefer deep modules: simple interfaces backed by useful hidden implementation.
- Avoid shallow wrappers, pass-through methods, and pass-through variables that add indirection without reducing complexity.
- Depend on roles or protocols only when the collaborator is genuinely replaceable or volatile.
- Prefer composition over inheritance when behavior needs to vary or inheritance would expose unwanted methods.
- Apply SOLID as judgment, not ceremony: SRP by reason to change, OCP for proven repeated extension, LSP for substitutable contracts, ISP for client-specific roles, DIP for volatile details.

## Errors And DRY

- First try to remove unnecessary error states by design; use exceptions and explicit contracts for remaining failures.
- Handle exceptions at the abstraction level that can make a useful decision.
- Use guard clauses to separate exceptional paths from the main flow.
- Use contract-style checks where boundary assumptions must be explicit; distinguish internal assertions from user-facing or runtime error handling.
- Treat DRY as single-source knowledge. Do not abstract coincidentally similar code that represents different domain facts.
- Remove duplicated business rules earlier than duplicated mechanics.
