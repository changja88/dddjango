# Strategic Design

Load this when the problem needs subdomain classification, bounded context discovery, ubiquitous language, event storming, distillation, or team-boundary reasoning.

## Strategic Order

1. Identify the business domain and the subdomains that matter.
2. Classify each subdomain as core, supporting, or generic.
3. Define bounded contexts and the ubiquitous language inside each context.
4. Map relationships between contexts.
5. Apply tactical patterns only after the strategic boundaries are clear.

Starting with entities, repositories, or aggregates before the context boundary is known often produces good code in the wrong model.

## Knowledge Crunching

- Build the model through repeated conversation with domain experts and developers together.
- Treat the model as provisional until examples, exceptions, and language conflicts have been explored.
- Refactor the model beneath the code when a better business concept appears.
- Prefer concrete scenarios, policies, and state transitions over abstract nouns.

## Subdomains

- Core subdomain: competitive advantage, high complexity or volatility, worth focused in-house modeling.
- Supporting subdomain: necessary to business but not differentiating; keep the implementation simpler.
- Generic subdomain: common problem space; prefer proven external products or libraries when appropriate.

Do not apply the same DDD intensity everywhere. CRUD-like supporting areas may not need rich aggregates.

## Problem Space And Solution Space

- Problem space asks what business problem exists: domains, subdomains, policies, constraints, and goals.
- Solution space asks how software responds: bounded contexts, models, integrations, and implementation structure.
- Subdomains are discovered; bounded contexts are designed.

## Ubiquitous Language

- Use business terms from domain experts, not technical placeholder names.
- Keep one term to one meaning inside a bounded context.
- Allow the same word to have different meanings across contexts when the business uses it differently.
- Put the language into code names, tests, API terms, and handoff documents.

## Distillation And Discovery

- Distill the core domain so it receives the most modeling effort.
- Separate complex mechanisms that are not the domain's meaning from the domain model itself.
- Use event storming when state transitions, commands, policies, actors, or unclear process boundaries need discovery.
- Consider team ownership: a bounded context should have a clear owning team or responsibility boundary when possible.

## Large-Scale Structure

- Let large-scale structure evolve with the model instead of imposing a complete taxonomy upfront.
- Use a system metaphor, responsibility layers, or knowledge-level model only when they clarify a large domain.
- Keep these structures aligned with bounded contexts and team ownership.
