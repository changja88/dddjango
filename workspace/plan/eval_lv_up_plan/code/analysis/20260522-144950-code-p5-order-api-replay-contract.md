수정 대상: case
리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# 분석

`case-code-order-api` targeted run에서 with-dddjango 산출물은 서비스 계층 멱등성, DB unique constraint, transaction boundary, replay/conflict 테스트, Django check/test 통과를 제공했지만 evaluator가 `replayed` 플래그 차이를 이유로 `partial`로 판정했다.

fixture의 기존 public API schema인 `OrderOut`에는 `replayed: bool`이 이미 포함되어 있다. 따라서 public prompt의 "같은 응답 snapshot"을 바이트 단위 동일 JSON으로 해석하면 fixture 계약과 충돌한다.

동시에 baseline/with-dddjango 응답은 문법 컴파일 통과를 보고하는 경향이 있으나 기존 deterministic check artifact는 Django check/test만 남겼다. 실행 주장 검증을 유지하려면 compile check도 명시적 command artifact로 남겨야 한다.

결론: 같은 주문 payload replay는 유지하되 기존 schema의 명시적 replay marker는 허용하고, `python3 -m compileall apps/orders shop_service`를 deterministic check에 추가한다.
