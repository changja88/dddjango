# Pagination, Versioning, And Limits

Load this for pagination selection, response metadata, versioning strategy, backward compatibility, deprecation, and rate limiting.

## Pagination

- Offset pagination is simple and supports random access, but can degrade on large datasets and can miss/duplicate rows while data changes.
- Cursor pagination is better for large or changing datasets because it preserves position more reliably.
- Keyset pagination is efficient when the API can sort by indexed, stable, unique keys.

Choose from scenario facts:

- Small data or admin pages: offset can be acceptable.
- Real-time feeds, high-volume lists, or changing datasets: prefer cursor.
- High-performance ordered reads: consider keyset.

Use stable ordering. For cursor/keyset pagination, prefer an immutable timestamp plus ID or another unique indexed ordering key. Encode cursors opaquely, include `has_more` or `next_cursor`, and keep page size bounded, commonly around 100-200 results per page unless the product has a stronger constraint.

## Versioning

- Pick one versioning strategy and apply it consistently.
- URL path versioning is visible and easy to route, but pollutes resource URLs.
- Header versioning keeps cleaner URLs, but is harder to inspect manually.
- Query parameter versioning is visible but can mix awkwardly with filters and caches.
- A common compromise is major version in the path and minor or date version in headers.

## Compatibility And Deprecation

- Additive response fields and optional request fields are usually non-breaking.
- Removing fields, renaming fields, changing field types, adding required request fields, changing URLs, changing status codes, or changing error shapes are breaking changes.
- Prefer additive changes. When breaking change is unavoidable, version it.
- For deprecation, document the change, send deprecation/sunset signals when the platform supports them, provide migration guidance, and keep a migration window.

## Rate Limiting

- Return `429 Too Many Requests` with `Retry-After`.
- Document limit, remaining quota, and reset semantics when exposing rate-limit headers.
- Choose algorithm by product need: token bucket for controlled bursts, sliding window for smoother precision, fixed window for simple internal APIs, leaky bucket for traffic shaping.
- Keep this reference focused on the API-visible policy and headers; adapter placement and middleware implementation belong to `implementation-django-ninja` or the relevant implementation skill.
