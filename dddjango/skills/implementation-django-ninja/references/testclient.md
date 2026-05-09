# TestClient And API Verification

Use this reference for Django Ninja API test acceptance criteria and verification reporting. Detailed pytest fixture and test-double mechanics belong to `implementation-test`; TDD workflow belongs to `implementation-tdd`.

## What To Test

- Request schema validation for valid and invalid payloads.
- Response schema fields and types for list/detail/create/update/delete operations.
- Status codes and headers for success, validation errors, auth errors, conflicts, rate limits, and async acceptance.
- Problem Details shape for errors.
- Authentication and authorization behavior, including 401 vs 403.
- Pagination and filtering behavior, including maximum page size and stable ordering.
- Idempotency replay, conflict behavior, and concurrent duplicate request handling for risky POST endpoints.
- DRF-to-Ninja compatibility: URL, method, field, status, auth, pagination, error, and OpenAPI differences.

## Test Boundaries

- Test business rules at the domain/service layer where possible.
- Use API tests for HTTP contract, auth/permission wiring, serialization, error mapping, and compatibility.
- Do not hide domain behavior only inside API tests when faster domain/service tests would express the rule more clearly.
- Coordinate model, transaction, and migration behavior tests with `implementation-django`.

## Verification Reporting

- Report the exact command run, such as a focused pytest path, TestClient test run, OpenAPI generation command, or schema comparison command.
- If tests were not run, say `Not run` and state why.
- Do not claim endpoints, schemas, OpenAPI, or compatibility checks passed without command output or reviewed artifacts.
- When source is provisional, mention any framework syntax that still needs verification against the installed Django Ninja version.
