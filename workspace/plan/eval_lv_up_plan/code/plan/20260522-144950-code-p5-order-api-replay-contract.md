수정 대상: case

# 계획

1. public prompt의 replay 요구를 fixture schema와 맞춘다.
   - 같은 key/payload는 새 주문 없이 같은 주문 응답 payload를 replay해야 한다.
   - 기존 `replayed` 필드 같은 명시적 replay indicator는 허용한다.

2. answer oracle의 required behavior와 consistency observations에 같은 해석을 명시한다.
   - snapshot 동일성 때문에 정상 구현이 `partial`로 떨어지지 않게 한다.
   - replay marker가 API schema에 있을 때 허용된다는 조건을 둔다.

3. deterministic checks에 compile command를 추가한다.
   - `python3 -m compileall apps/orders shop_service`
   - command artifact 기반으로 문법 컴파일 실행 주장을 검증한다.

4. 검증한다.
   - `validate_eval_bucket_pack.py --bucket code`
   - targeted `case-code-order-api` eval 재실행
   - 생성 run에 대해 `validate_eval_run.py --bucket code --case case-code-order-api`
