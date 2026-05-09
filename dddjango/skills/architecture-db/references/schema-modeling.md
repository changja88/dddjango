# Schema Modeling

Load this for ERD, conceptual/logical/physical modeling, normalization, denormalization, hierarchy, inheritance, and polymorphic modeling decisions.

## Modeling Flow

1. Understand the business process, domain invariants, query patterns, and write contention.
2. Create a conceptual model: entities, attributes, relationships.
3. Create a logical model: keys, cardinality, optionality, normalization, data types.
4. Create a physical model: indexes, partitioning, constraints, and performance trade-offs.

Do not start from Django field convenience when the domain invariant belongs in the database.

## ERD Decisions

- Identify entities as cohesive information groups.
- Track attributes as columns and relationships as PK/FK links.
- Choose primary keys from candidate keys; use surrogate keys when no natural key is stable.
- Record cardinality: 1:1, 1:N, or N:M through a join table.
- Record optionality explicitly: whether a relation or column can be absent.

## Normalization And Denormalization

- Normalize first: 1NF removes repeating groups, 2NF removes partial dependency, 3NF removes transitive dependency, and BCNF requires determinants to be superkeys.
- Stop normalization deliberately when extra joins cost more than the anomaly risk, and document the trade-off.
- Denormalize only after query optimization, indexing, and caching have been considered.
- If adding derived columns, duplicated data, or merged tables, state how consistency is maintained.

## Hierarchy Patterns

- Adjacency List: simplest and update-friendly; recursive/CTE queries for tree traversal.
- Closure Table: best for frequent ancestor/descendant queries; higher write/storage cost.
- Nested Set: read-friendly for stable trees; expensive moves.
- Materialized Path: simple prefix queries; path updates on moves.

## Inheritance And Polymorphism

- Single Table Inheritance: simple and fast when most attributes are shared; many nullable columns when types diverge.
- Class Table Inheritance: normalized and integrity-friendly when subtype fields differ; requires joins.
- Concrete Table: independent tables for independent types; schema duplication and weaker common FK semantics.
- Polymorphic associations weaken DB-level FK enforcement. Prefer explicit tables or join models when integrity matters.
