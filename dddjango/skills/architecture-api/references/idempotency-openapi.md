# Idempotency And OpenAPI

Load this for duplicate-sensitive POST contracts, `Idempotency-Key` behavior, retry semantics, and OpenAPI impact.

## Idempotency-Key

Use `Idempotency-Key` for duplicate-sensitive POST operations such as payments, order creation, reservations, or other actions where retry can create harmful duplicates.

Contract decisions:

- whether the endpoint accepts or requires `Idempotency-Key`;
- key uniqueness scope, such as caller plus operation or resource owner;
- replay behavior for the same key and same request;
- conflict behavior for the same key with different request content;
- key retention window;
- storage durability handoff to `architecture-db`;
- concurrency/race handling handoff to `architecture-db`;
- test criteria for replay, conflict, and simultaneous duplicate requests.

Replay means returning the original operation result for an equivalent retry, not recomputing from mutable current resource state. For resources that can change after creation, store a stable first-response/result snapshot or equivalent DTO with the idempotency record, and include an acceptance test that changes the resource after the first response and then verifies the retry still returns the original result.

POST needs this treatment because a client may retry after the server processed the request but the response was lost. GET, PUT, and DELETE already have idempotent method semantics, though their implementation still must preserve the contract.

For browser-like POST workflows where duplicate form resubmission is the main risk, consider POST/Redirect/GET with `303 See Other` to a GET result resource. For API clients that retry unsafe POST requests, prefer `Idempotency-Key`.

## OpenAPI Impact

Record OpenAPI changes whenever the API contract changes:

- path, method, operation ID, tags;
- request body schema and examples;
- response schemas by status code;
- Problem Details error responses;
- authentication and authorization requirements;
- pagination parameters and response metadata;
- rate-limit and retry headers;
- `Idempotency-Key` header and behavior notes;
- versioning or deprecation metadata.

Keep OpenAPI aligned with the contract so tests, client SDKs, documentation, and compatibility review all use the same source.
