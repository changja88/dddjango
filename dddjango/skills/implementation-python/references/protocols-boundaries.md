# Protocols And Boundaries

Use this reference for `Protocol`, structural subtyping, replaceable boundaries, exceptions, context managers, async/concurrency choices, and avoiding unnecessary abstraction.

## Protocols

- Use `Protocol` when callers need a structural contract across replaceable implementations.
- Good candidates: repository-like ports, clock/ID generators, external gateway adapters, file-like streams, and strategy objects.
- Avoid creating one protocol per class when there is only one implementation and no meaningful boundary.
- Compose small protocols when callers need only part of a capability.
- Use generic protocols only when type relationships matter to callers.
- Treat `@runtime_checkable` as a presence check only; it does not validate method signatures at runtime.

## Boundaries

- Keep external SDK, filesystem, HTTP, and framework details behind narrow roles when they make core code hard to test or replace.
- Prefer direct dependencies for simple stable helpers, local value objects, and implementation details that are not real boundaries.
- Repository and Unit of Work architecture belongs primarily to `architecture-implementation-patterns`; this skill only helps express the Python contract.

## Attributes And Properties

- Prefer plain attributes over boilerplate getters and setters when no behavior is needed.
- Use `@property` when access should look like an attribute but needs computed, lazy, compatibility, or validation behavior.
- Avoid broad `__getattr__` or `__getattribute__` hooks unless dynamic attribute access is the object’s core responsibility.

## Exceptions And Resource Flow

- Define a top-level module exception when a module exposes several related errors.
- Raise explicit exceptions for exceptional failure instead of returning `None` when `None` is not a valid business result.
- Use `try`/`except`/`else`/`finally` to separate expected recovery, success-only work, and cleanup.
- Use context managers for resource acquisition and release; keep cleanup behavior visible.

## Async And Concurrency

- Use `asyncio.TaskGroup` for structured concurrency when the project targets Python 3.11+ and the work is truly async.
- Before an async refactor, check whether Django ORM calls, external SDKs, file I/O, and side effects are actually async-safe in the project’s runtime.
- Use threads for blocking I/O that cannot be made async; do not assume threads improve CPU-bound code under the GIL.
- Treat free-threaded Python and subinterpreters as version-specific/runtime-specific choices, not defaults.
