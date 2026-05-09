# Context Map

Load this when multiple bounded contexts, upstream/downstream relationships, legacy integrations, shared language, or team ownership boundaries are involved.

## Relationship Direction

- Name each bounded context and its language.
- Identify upstream and downstream direction.
- State who can change the contract and who must adapt.
- Choose the relationship pattern based on coordination cost, model fit, and control.

## Relationship Patterns

| Pattern | Use when | Watch for |
|---|---|---|
| Partnership | Two teams must coordinate changes for mutual success | Requires active collaboration and scheduling |
| Shared Kernel | A small model fragment is truly shared | Keep the shared part tiny and governed |
| Customer-Supplier | Upstream can plan for downstream needs | Needs negotiation and roadmap visibility |
| Conformist | Downstream accepts upstream's model | Avoid if the upstream language corrupts core domain thinking |
| Anticorruption Layer | Upstream model conflicts with downstream language | Adds translation cost but protects the model |
| Open Host Service | One context exposes a stable service to many consumers | Needs a stable public protocol |
| Published Language | Contexts exchange a shared schema or message language | Keep versioning and compatibility explicit |
| Separated Ways | Integration costs more than duplication | Document why duplication is acceptable |
| Big Ball of Mud | Legacy boundaries have collapsed | Isolate it so its language does not spread |

For an unbounded legacy model, prefer a protective boundary or translation layer instead of spreading its language into the new core model.

## Outputs

For each relationship, record:

- upstream context
- downstream context
- chosen pattern
- integration mechanism if known
- model translation responsibility
- reason for choosing the pattern
- risk or follow-up for API, DB, or implementation-pattern skills
