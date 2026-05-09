# Router And Schema

Use this reference for Django Ninja Router, Schema/ModelSchema, endpoint adapter boundaries, and DRF-to-Ninja conversion. This skill is provisional: exact framework syntax must be verified against the project’s installed Django Ninja version and existing code.

## Router Boundary

- Treat a Router operation as an HTTP adapter, not a business-rule owner.
- Keep Router code limited to request parsing, auth/permission wiring, schema validation, service/usecase invocation, response mapping, and error translation.
- Keep URL registration explicit and consistent with the project’s existing Ninja API layout.
- Move state transitions, invariants, transactional writes, complex ORM query construction, and external SDK calls to model/service/usecase code owned by `implementation-django`.
- If a route needs a domain decision that has not been made, stop and route to `architecture-ddd` or `architecture-api` as appropriate.

## Schema And ModelSchema

- Use request schemas for input shape and response schemas for output shape; do not expose every model field by default.
- Separate create/update/list/detail schemas when fields, permissions, or performance needs differ.
- Keep schema validation focused on transport/input shape. Put reusable domain invariants in model/service/DB boundaries.
- Avoid leaking internal model names or DB structure when the API contract uses a different public language.
- Treat field additions as generally compatible and field removals, renames, type changes, new required fields, status-code changes, and error-shape changes as breaking unless versioned.

## DRF-To-Ninja Conversion

- Convert DRF `ViewSet`/`APIView` routing to explicit Django Ninja Router operations.
- Convert DRF `Serializer`/`ModelSerializer` responsibilities into Django Ninja request/response schemas plus service-layer validation where appropriate.
- Replace DRF-specific pagination, permissions, and exception behavior with the project’s Django Ninja equivalents while preserving the public API contract.
- Compare old and new endpoint URLs, methods, status codes, response fields, error shapes, auth behavior, pagination, and OpenAPI schema.
- Use DRF references only to understand the legacy source; do not keep DRF as the greenfield standard.

## Endpoint Review Questions

- Is the HTTP contract already decided by `architecture-api`?
- Is the Router registered in the expected API namespace/version?
- Is the Router thin enough that business behavior can be tested without HTTP?
- Are request and response schemas intentionally scoped to public API fields?
- Are domain/application errors mapped consistently to Problem Details?
- Are OpenAPI and compatibility impacts visible in the implementation notes?
