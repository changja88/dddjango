# Test Doubles

Load this when choosing between dummy, stub, spy, mock, fake, monkeypatch, time mocking, HTTP mocking, or async mocking.

## Double Selection

| Double | Use when | Avoid when |
|---|---|---|
| Dummy | A required argument is not used | The value affects behavior |
| Stub | The test needs a fixed returned value | You need to verify the call itself |
| Spy | You need call history after the action | Output or state verification is enough |
| Mock | The collaboration itself is the contract | It replaces core domain behavior |
| Fake | A simple working implementation is clearer | It diverges from the real contract |

Verification priority:

1. Output-based: returned value or raised error.
2. State-based: object or persisted state after the action.
3. Communication-based: calls to an external role.

Use communication checks mainly for external systems, adapters, or side-effect boundaries such as email, payment, HTTP, message broker, cache, SDK, and clock.

## Mocking Rules

- Prefer dependency injection or an adapter seam over patching deep internals.
- Use `spec`, `autospec`, or `create_autospec` so mocks fail when the interface changes.
- Use `seal()` after configuring a mock when accidental attribute creation would hide a typo.
- Use `ANY` only for values irrelevant to the behavior; keep important arguments explicit.
- Use `side_effect` for errors, retries, and input-dependent behavior.
- Use `PropertyMock` sparingly; if property mocking is hard, check whether the production interface is too implicit.
- Use `AsyncMock` for async functions and assert awaited calls with `assert_awaited_once_with`.
- Use `pytest-mock`'s `mocker` fixture when the project standardizes on it; prefer `mocker.patch`, `mocker.spy`, and `mocker.Mock` over mixing several patching styles in one test file.
- Use spies only when call observation is the behavior. Do not spy on private helpers to prove an algorithm was used.

Do not replace all collaborators with mocks just because it is possible. For domain objects and value objects, real objects usually produce more durable tests.

## Time And Environment

- Prefer `time-machine` for CPython projects that need fast global time travel.
- Prefer `freezegun` when PyPy support or selective patching matters.
- Avoid manually patching `datetime` across many modules; import paths are easy to miss.
- Use `tick`, `shift`, or fixture-wrapped time travel when the scenario depends on time moving forward.
- Use `monkeypatch.setenv` and `monkeypatch.delenv` for environment-dependent logic.

## HTTP And External Calls

- Use `responses` for code built on `requests`.
- Use `aioresponses` for `aiohttp` clients.
- Use HTTPretty or another socket-level interceptor only when the HTTP client cannot be targeted more narrowly.
- Register exact methods, URLs, response bodies, status codes, and exceptions that matter to the contract.
- For Django Ninja APIs inside the project, prefer this skill's `TestClient` contract tests instead of mocking the router.
