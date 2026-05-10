Fixture repo에서 주문 생성 흐름을 개선해줘.

요구사항:
- 같은 `Idempotency-Key`로 같은 요청이 다시 들어오면 새 주문을 만들지 않고 같은 결과를 돌려줘.
- 다른 payload가 같은 key로 오면 conflict로 구분할 수 있어야 해.
- 주문 생성 API는 얇은 adapter로 남기고, 도메인 규칙과 저장소/중복 방지는 service 쪽에 둬.
- Problem Details 형태의 오류 응답을 표현할 수 있게 해.
- 관련 단위 테스트를 추가해.

가능하면 `python -m compileall apps tests`와 `python -m unittest discover -s tests`를 실행하고 결과를 보고해줘.
