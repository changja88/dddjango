수정 대상: reference
원인 분류: P3 source-runtime-scope-and-provenance-gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# Implementation Python P3 Reference Follow-up Analysis

## 평가 범위

- Source reference: `workspace/reference/implementation-python/reference/final.md`
- Runtime skill: `dddjango/skills/implementation-python/SKILL.md`
- Runtime bundled references: `dddjango/skills/implementation-python/references/*.md`
- 인접 source area: `workspace/reference/architecture-implementation-patterns/reference/final.md`

## 현재 판정

P3 runtime skill은 Python 언어 계층의 contract 표현, type hints, dataclass/Enum/Protocol, pydantic v2 boundary, async/concurrency, exception, Ruff/mypy/pyright 기준을 맡는 것으로 좁게 정리됐다. 반면 source reference `final.md`는 descriptor 검증 패턴, iterator/generator, profiling/performance, f-string/parser updates, debugging, docstring, precision arithmetic, Python 3.14 t-strings/annotation changes 등 더 넓은 Python general reference를 포함한다.

이 넓은 source material을 모두 runtime skill에 싣는 것은 P3의 progressive disclosure 목적과 충돌할 수 있다. 현재 runtime skill의 책임 경계는 좁은 구현 품질 판단으로 유지하고, source reference는 후속 단계에서 runtime skill scope와 source-only general Python material을 구분해야 한다.

## Finding

### Reference Follow-up 1: source reference 범위가 runtime skill보다 넓음

- Evidence: `final.md`는 descriptors, iterators/generators, profiling/performance, debugging, docstring, precision arithmetic, Python 3.14 t-strings/annotation changes 등 runtime bundled references에 없는 일반 Python material을 포함한다.
- Current runtime decision: runtime skill은 모든 Python 일반 지식을 로딩하지 않고, type contract, dataclass/Enum, Protocol/boundary, pydantic v2 중심의 high-signal implementation guidance를 직접 제공한다.
- Allowed claim now: runtime skill은 현재 명시된 Python implementation quality 영역에 대해 P3 경계를 만족한다.
- Forbidden claim now: source reference의 모든 Python general material이 runtime bundled references로 노출되어 있다고 주장하지 않는다.
- Source work to close: source reference를 runtime-owned guidance와 source-only/general Python background로 분류하거나, runtime에서 계속 지원해야 할 추가 영역만 별도 bundled reference로 승격할지 결정한다.

### Reference Follow-up 2: Repository/UoW fallback 문구가 stale

- Evidence: `final.md`의 Repository/Unit of Work 섹션은 해당 패턴이 향후 `architecture-implementation-patterns` source reference로 분리된다고 적는다.
- Current runtime decision: runtime skill과 bundled `protocols-boundaries.md`는 repository/UoW architecture 결정을 이미 `architecture-implementation-patterns`로 넘긴다.
- Allowed claim now: runtime guidance는 repository/UoW/ports/outbox decision을 `architecture-implementation-patterns`로 handoff한다.
- Forbidden claim now: implementation-python source reference가 최신 architecture-implementation-patterns source 존재를 완전히 반영한다고 주장하지 않는다.
- Source work to close: `workspace/reference/implementation-python/reference/final.md`에서 stale fallback 문구를 현재 source structure에 맞게 갱신한다.

## 통합 판단

- 이 gap은 runtime skill을 억지로 넓혀 해결할 문제가 아니다.
- P3 runtime 수정은 source/reference governance, architecture pattern decision, clean-code refactor decision을 handoff하도록 보강했다.
- Source reference 자체의 범위와 stale fallback은 별도 reference follow-up으로 남긴다.

## 최종 판정

- Blocker: 0
- Major: 0
- 열린 Minor: 0

## 후속 범위

- `workspace/reference/implementation-python/reference/final.md`

## 수정하지 말아야 할 범위

- 이번 P3 runtime skill 수정 범위에서 source reference를 직접 수정하지 않는다.
- Runtime skill에 source reference의 모든 일반 Python material을 추가하지 않는다.
