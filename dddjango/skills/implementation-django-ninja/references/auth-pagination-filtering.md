# Auth, Pagination, Filtering, And Versioning

Use this reference when implementing Django Ninja authentication/authorization wiring, list endpoints, filtering, sorting, pagination, rate limiting, and versioning.

## Authentication And Authorization

- Authentication answers who the caller is; authorization answers whether the caller can perform the action.
- Return 401 when authentication is required or invalid; return 403 when the caller is authenticated but lacks permission.
- Prefer `Authorization` headers for API credentials. Do not put secrets in query parameters.
- Require HTTPS for API traffic unless the environment is an explicitly local development setup.
- Keep adapter-level auth checks in the API boundary, but move reusable object/action authorization rules into services or domain policies when multiple entry points need them.
- For object-level permission checks, avoid loading more data than the endpoint needs; coordinate query shape with selectors/services.

## Filtering, Sorting, And Search

- Keep filtering and sorting parameters part of the public API contract.
- Use Django Ninja `FilterSchema` or the project’s existing filtering pattern when it improves validation and OpenAPI clarity.
- Prefer query parameters for filters, sort keys, sparse fieldsets, and search terms.
- Do not reflect internal DB table names or accidental ORM structure in public parameter names.
- Validate allowed filters and sort fields. Avoid arbitrary user-controlled ORM field names.
- Delegate reusable read logic and N+1 optimization to selectors or QuerySet methods from `implementation-django`.

## Pagination

- Choose pagination strategy from the API contract. Use offset for small/admin-like collections and cursor/keyset for large, real-time, or consistency-sensitive lists.
- Enforce a maximum page size.
- Return enough metadata for clients to fetch the next page, such as `has_more`, `next_cursor`, or equivalent project contract.
- For cursor/keyset pagination, use stable indexed ordering, usually timestamp plus ID.
- If pagination behavior is undecided, route to `architecture-api` before implementation.

## Rate Limiting

- Apply rate limiting before expensive authentication, database, or external work when the project has a rate-limit mechanism.
- Return 429 with `Retry-After` and rate-limit headers such as limit, remaining, and reset information when the project exposes them.
- Keep rate-limit policy visible in API documentation/OpenAPI notes when public clients depend on it.

## Versioning And Compatibility

- Follow the project’s chosen versioning strategy; do not mix URL, header, and query strategies without a compatibility reason.
- Prefer additive changes for existing clients.
- Use deprecation and migration windows for breaking changes.
- When converting from DRF, compare version behavior and document any change that can affect clients.
