수정 대상: case
원인 분류: coverage gap

# implementation-python P4 평가 분석

## 범위

- 대상 skill: `dddjango/skills/implementation-python/`
- source reference: `workspace/reference/implementation-python/reference/final.md`
- 관련 bucket: `response`, `code`

## 확인한 기준

`implementation-python`은 Python 언어 계층의 구현 판단을 검증해야 한다.

- public function/method type hints, `X | None`, built-in generics
- `TypedDict`, type narrowing, decorator typing, Python version gate
- dataclass value object, `Enum`/`StrEnum`, `NamedTuple`, `match/case`
- `Protocol`은 실제 replaceable boundary에만 사용하고 과도한 protocol 생성을 금지
- context manager, explicit exception, resource cleanup
- pydantic v2는 external DTO/config/runtime validation boundary에만 사용
- async/concurrency는 async-safe 여부와 Python target을 확인하고, 필요한 경우 `TaskGroup`/`except*`를 사용
- Ruff, mypy, pyright 실행 또는 미실행 보고의 정직성

## Inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id / status |
|---|---|---|---|---|---|---|---|
| code | `case-code-python-state` | Money value object와 주문 상태 타입 개선을 요구한다. | dataclass/value object, Enum, pydantic overuse 금지를 검증한다. | Python code-backed 일부 positive coverage | 수정 없음 | 대표 관련 case로 필요 | pending |
| response | `case-response-web-typing` | Django Web 책임과 Python typing 책임 분리를 묻는다. | Enum/dataclass/type-contract와 pydantic restraint를 보조 검증한다. | mixed-boundary 보조 coverage | 수정 없음 | 불필요 | not run |
| response | `case-response-python-boundaries` | external JSON, state, Protocol, context manager, pydantic v2, async, exception, typecheck 기준을 한 번에 묻는다. | implementation-python source/runtime/bundled reference 직접 연결 | direct positive coverage | case/answer 추가 | 필요 | pending |
| response | `case-response-python-tiny-type-hint` | 짧은 Python typing 질문에 직접 답하도록 요구한다. | tiny/direct restraint와 workflow/architecture 과적용 금지를 검증한다. | negative/restraint coverage | case/answer 추가 | 필요 | pending |

## Gap

P4 기준 1, 2, 4, 5에 Major gap이 있다. 기존 `case-code-python-state`는 dataclass/value object, Enum, pydantic overuse 금지를 code-backed로 검증하지만, `TypedDict`, type narrowing, Protocol boundary, context manager, pydantic v2 API, async/concurrency, exception, Ruff/mypy/pyright 정직성까지 직접 검증하지 않는다. `case-response-web-typing`은 Django Web과 Python typing의 mixed-boundary라서 개별 `implementation-python` 평가로 충분하지 않다.

Public case에 answer oracle, private 기준, 이전 run finding 누설은 확인되지 않았다. 그러나 evaluator가 `implementation-python` 전용 coverage tag와 answer basis를 강제하지 않아 같은 gap이 다시 생길 수 있다.

## 수정 방향

- `response` bucket에 direct positive case `case-response-python-boundaries`를 추가한다.
- `response` bucket에 tiny negative/restraint case `case-response-python-tiny-type-hint`를 추가한다.
- answer oracle은 `workspace/reference/implementation-python/reference/final.md`, `dddjango/skills/implementation-python/SKILL.md`, 필요한 bundled reference만 basis로 둔다.
- `validate_eval_bucket_pack.py`가 implementation-python P4 coverage와 answer source/runtime basis를 구조적으로 확인하도록 한다.
- code-backed positive 대표 case는 기존 `case-code-python-state`를 유지하고 targeted eval 대상으로 포함한다.

## 리뷰 방식

리뷰 방식: not-run

Subagent 리뷰/순차 fallback: pending. 수정 후 real subagent 리뷰를 실행해 skill-creator 관점과 독립 P4 관점에서 Blocker/Major/Minor를 다시 분류한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
