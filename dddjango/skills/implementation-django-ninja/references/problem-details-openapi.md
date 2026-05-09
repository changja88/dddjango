# Problem Details, Idempotency, And OpenAPI

Use this reference for API error responses, status codes, idempotency behavior, compatibility, and OpenAPI effects.

## Status Codes

- Use 200 for successful reads and updates that return a body.
- Use 201 for created resources and include the new resource location when the contract requires it.
- Use 202 for accepted asynchronous work.
- Use 204 for successful deletes or updates with no body.
- Use 400 for malformed requests, 401 for authentication failure, 403 for authorization failure, 404 for missing or intentionally hidden resources, 409 for conflicts, 422 for semantically invalid input when the contract uses it, and 429 for rate limits.
- Keep status-code changes compatible with existing clients or version them.

## Problem Details

- Use `application/problem+json` as the response media type for Problem Details errors.
- Use RFC 9457 Problem Details for API errors unless a legacy compatibility contract explicitly says otherwise.
- Keep `status` aligned with the HTTP response status.
- Use `title` for reusable problem type summaries and `detail` for the specific occurrence.
- Use a stable `type` URI or `about:blank` when no stable type exists.
- Include `instance` when the specific occurrence has a useful request or problem identifier URI.
- Add extension fields only when they are documented and safe for clients to ignore.

## Idempotency-Key

- Require or support `Idempotency-Key` for duplicate-prone POST operations such as order or payment creation.
- Store the first request result in durable storage such as DB or Redis according to the service transaction design.
- Return the stored response for repeated requests with the same key when the request is equivalent.
- Define conflict behavior for the same key with a different payload.
- Coordinate key TTL, storage owner, transaction boundary, and concurrency behavior with `implementation-django` and `architecture-db`.

## OpenAPI

- Ensure Router and Schema changes produce the intended OpenAPI request/response shape.
- Check names, required fields, nullable fields, enum values, status responses, error schema, auth requirements, pagination shape, and tags.
- For migrations from DRF, compare old and new generated schema when possible and document client-visible differences.
- Do not claim OpenAPI generation or schema diff was run unless it was actually executed.
