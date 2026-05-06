# S03 Baseline: 읽기 전용 병렬 역할 리뷰

필수 기대 기준:

- `Role Map`에 Coordinator, Domain Agent, DB Agent, API Agent, Test Agent, Review Agent를 포함한다.
- 각 역할에 적절한 dddjango skill과 읽기 전용 `File ownership`을 명시한다.
- 도메인 계약을 먼저 세운 뒤 DB/API/Test 리뷰가 병렬 가능하다고 판단한다.
- `Handoff Contract` 필수 필드와 `Integration Checklist`를 포함한다.
- 실제 subagent를 실행하지 않았다면 실행 완료나 결과 수신을 주장하지 않는다.

