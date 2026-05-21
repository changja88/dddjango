# REST Contracts

Load this for REST resource design, URL structure, HTTP method choice, status codes, headers, authentication/authorization semantics, content negotiation, and cache contracts.

## REST Shape

- Treat resources as nouns identified by stable URIs.
- Keep the interface uniform: HTTP method, status code, representation, and headers must carry the contract.
- Keep requests stateless; every request contains what the server needs to process it.
- Balance REST purity with practical client workflow needs.

## URL And Resource Design

- Use plural nouns, lowercase kebab-case, and no trailing slash.
- Do not expose database table names or internal implementation structures in URLs.
- Use parent-child subresources when the relationship is part of the client workflow, but avoid nesting deeper than three levels.
- Use query parameters for filtering, sorting, search, sparse fieldsets, and pagination.

## HTTP Methods

- `GET`, `HEAD`, and `OPTIONS` are safe and idempotent.
- `POST` creates resources or triggers non-idempotent actions.
- `PUT` replaces a whole resource and should be idempotent.
- `PATCH` updates part of a resource; confirm whether the patch document itself is idempotent.
- `DELETE` removes a resource and should be idempotent from the client contract perspective.

## Status Codes

- Use 2xx for successful processing, 3xx for required follow-up action, 4xx for client/request problems, and 5xx for server-side or temporary service failures.
- `200 OK`: successful read or update with a response body.
- `201 Created`: successful creation; include `Location` for the new resource when possible.
- `202 Accepted`: asynchronous or long-running work accepted but not completed.
- `204 No Content`: successful delete or update with no body.
- `303 See Other`: redirect to a GET result after POST when applying PRG.
- `400 Bad Request`: malformed request syntax or shape.
- `401 Unauthorized`: authentication is missing or invalid.
- `403 Forbidden`: authenticated principal lacks permission.
- `404 Not Found`: resource missing or intentionally hidden.
- `409 Conflict`: duplicate creation or concurrent state conflict.
- `422 Unprocessable Entity`: syntactically valid but semantically invalid request.
- `429 Too Many Requests`: rate limit exceeded.
- `500 Internal Server Error`: unexpected server failure.
- `503 Service Unavailable`: temporary overload or maintenance; include retry guidance when possible.

## Request And Response Contracts

- Treat the contract as the combination of URL, method, request fields, response status, response body, and response headers.
- For requests, distinguish path, query, header, and body fields. Mark required versus optional fields, validation rules, defaults, units, and allowed ranges.
- For responses, define body schema and headers per status code. `201` should include `Location` when possible, `202` should include how to observe the accepted work, and `204` must not include a body.
- Include client-behavior headers in the contract when relevant: retry, rate-limit, cache, deprecation/sunset, and idempotency replay headers.
- Keep Problem Details error responses part of the response contract, not a separate undocumented exception path.

## Headers And Representation

- Use `Content-Type` to state representation format.
- Use `Accept`, `Accept-Language`, and `Accept-Encoding` for content negotiation when the API supports multiple representations.
- When using content negotiation, honor quality values and choose the most specific acceptable representation before falling back to less specific matches.
- Use `Cache-Control`, `ETag`/`If-None-Match`, or `Last-Modified`/`If-Modified-Since` when caching is part of the contract.
- Return `304 Not Modified` only when validators show the representation has not changed.

## Auth And Security

- Authentication asks who the caller is; authorization asks what that caller may do.
- Return `401` for missing or invalid authentication and `403` for authenticated but unauthorized access.
- For `401`, include `WWW-Authenticate` when the client needs to know the authentication method.
- Choose the mechanism by client type: API keys for simple server-to-server/internal APIs, OAuth 2.0 for delegated third-party access, and bearer JWTs for stateless service or user-token contracts when expiry and revocation are addressed.
- Put credentials in `Authorization`, not query parameters.
- Require HTTPS for all API communication.
