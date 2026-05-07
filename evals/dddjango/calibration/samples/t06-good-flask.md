# Flask 주문 생성 엔드포인트

순수 Flask 기준으로 작성합니다. Django, DRF, Django Ninja 구조는 적용하지 않습니다.

Flask route에서 JSON payload를 읽고 필수 필드를 검증한 뒤 주문 생성 함수를 호출합니다.
응답은 `jsonify`로 반환하고, 상태 코드는 생성 성공 시 201을 사용합니다.

```python
from flask import Blueprint, jsonify, request

orders_bp = Blueprint("orders", __name__)

@orders_bp.post("/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    if "items" not in payload:
        return jsonify({"message": "items is required"}), 400
    return jsonify({"id": 1, "status": "created"}), 201
```

실행 예시는 `pip install flask` 후 `flask --app app run`입니다.
요청 확인은 `curl -X POST http://127.0.0.1:5000/orders ...` 형태로 진행합니다.
검증은 Flask test client로 201/400 케이스를 나눠 테스트합니다. 실제 테스트는 실행하지 않았습니다.
