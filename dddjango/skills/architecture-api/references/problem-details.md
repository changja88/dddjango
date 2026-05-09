# Problem Details

Load this for RFC 9457 error response design, error field semantics, extension fields, and status/error consistency.

## RFC 9457 Contract

Use `application/problem+json` for API errors unless an existing contract requires another format.

Core fields:

- `type`: stable URI identifying the problem type; `about:blank` is the default if omitted.
- `title`: short summary of the problem type; reuse the same title for the same type.
- `status`: HTTP status code and must match the actual response.
- `detail`: occurrence-specific explanation.
- `instance`: URI identifying this specific occurrence.

## Extension Fields

- Add extension fields only when clients can use them.
- Document extension fields as part of the problem type.
- Design clients to ignore extension fields they do not understand.

## Error Mapping

- Keep validation, conflict, permission, not-found, rate-limit, and server errors distinguishable.
- Use `409` for state conflicts or duplicate creation and `422` for semantically invalid request content.
- Use one consistent error envelope across the API.
- Do not expose secrets, stack traces, internal class names, or infrastructure topology in `detail`.

## Output Checklist

For each relevant error, record:

- HTTP status;
- problem `type`;
- reusable `title`;
- occurrence-specific `detail` shape;
- extension fields;
- whether the error is retryable;
- OpenAPI response impact.
