"""④-2 조각 2 — api_error_controller 픽스처(good payment 세트 · bad #648/#649) + 등재 3문서(#648·#649 · #63 stale · 집계).
실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib

G = pathlib.Path("workspace/eval/fixtures/api_error_controller/good/application/orders")
B = pathlib.Path("workspace/eval/fixtures/api_error_controller/bad_rules/application/orders")


def w(p: pathlib.Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ── good: payment 세트(상자 하나 두 허용형 · RootModel 단독) ─────────────────
w(G / "application_layer/payment/get_payment/get_payment_query.py",
  "from dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass GetPaymentQuery:\n    payment_id: str\n")
w(G / "domain_layer/payment/exception/payment_not_found.py",
  "class PaymentNotFound(Exception):\n    pass\n")
bc = G / "driving_layer/api/bc_error_schema.py"
s = bc.read_text(encoding="utf-8")
assert 'ORDER_NOT_FOUND = "order_not_found"\n' in s and "PAYMENT_NOT_FOUND" not in s
bc.write_text(s.replace('ORDER_NOT_FOUND = "order_not_found"\n', 'ORDER_NOT_FOUND = "order_not_found"\n    PAYMENT_NOT_FOUND = "payment_not_found"\n'), encoding="utf-8")
w(G / "driving_layer/api/payment/schema/schema_out.py", '''from typing import Annotated, Literal

from ninja import Schema
from pydantic import Field, RootModel


class CardPaymentOut(Schema):
    kind: Literal["card"]
    payment_id: str
    last4: str


class PointPaymentOut(Schema):
    kind: Literal["point"]
    payment_id: str
    points: int


class PaymentOut(RootModel[Annotated[CardPaymentOut | PointPaymentOut, Field(discriminator="kind")]]):
    """성공 union 응답 — 이름 붙은 RootModel 하나(ninja Schema 병행 상속 금지 · #649 · ninja §3.1)."""
''')
w(G / "driving_layer/api/payment/payment_controller.py", '''from ninja import Status
from ninja_extra import api_controller, http_get

from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery
from application.orders.domain_layer.payment.exception.payment_not_found import PaymentNotFound
from application.orders.driving_layer.api.bc_error_schema import OrdersErrorCode, OrdersErrorSchema
from application.orders.driving_layer.api.payment.schema.schema_out import PaymentOut


@api_controller("/payments")
class PaymentController:
    @http_get("/{payment_id}", response={200: PaymentOut, 404: OrdersErrorSchema})
    def get_payment(self, payment_id: str) -> PaymentOut | Status[OrdersErrorSchema]:
        try:
            result = self._use_case.execute(GetPaymentQuery(payment_id=payment_id))
        except PaymentNotFound:
            return Status(404, OrdersErrorSchema(code=OrdersErrorCode.PAYMENT_NOT_FOUND, message="payment not found"))
        return PaymentOut.model_validate(result)

    @http_get("/{payment_id}/receipt", response={200: PaymentOut, 404: OrdersErrorSchema})
    def get_receipt(self, payment_id: str) -> Status[PaymentOut | OrdersErrorSchema]:
        try:
            result = self._use_case.execute(GetPaymentQuery(payment_id=payment_id))
        except PaymentNotFound:
            return Status(404, OrdersErrorSchema(code=OrdersErrorCode.PAYMENT_NOT_FOUND, message="payment not found"))
        return Status(200, PaymentOut.model_validate(result))
''')

# ── bad: #648 상자 둘 · #649 Schema+RootModel ────────────────────────────────
pc = B / "driving_layer/api/payment/payment_controller.py"
assert pc.read_text(encoding="utf-8") == "class PaymentController:\n    pass\n"
w(pc, '''from ninja import Status
from ninja_extra import api_controller, http_get

from application.orders.driving_layer.api.payment.schema.schema_out import PaymentOut, PaymentErrorOut


@api_controller("/payments")
class PaymentController:
    @http_get("/{payment_id}", response={200: PaymentOut, 404: PaymentErrorOut})
    def get_payment(self, payment_id: str) -> Status[PaymentOut] | Status[PaymentErrorOut]:
        return Status(200, PaymentOut(kind="card", payment_id=payment_id))
''')
w(B / "driving_layer/api/payment/schema/schema_out.py", '''from typing import Annotated, Literal

from ninja import Schema
from pydantic import Field, RootModel


class CardPaymentOut(Schema):
    kind: Literal["card"]
    payment_id: str


class PointPaymentOut(Schema):
    kind: Literal["point"]
    payment_id: str


class PaymentOut(Schema, RootModel[Annotated[CardPaymentOut | PointPaymentOut, Field(discriminator="kind")]]):
    pass


class PaymentErrorOut(Schema):
    code: str
''')
print("fixtures written")

# ── 등재 3문서 ────────────────────────────────────────────────────────────────
spec = pathlib.Path("workspace/design/2026-08-08-tree-revision-spec.md"); t = spec.read_text(encoding="utf-8")
a = t.index("| 647 | 키가 정해진 값 묶음(레코드)은"); e = t.index("\n", a) + 1
rows = (
"| 648 | 컨트롤러 반환 주석의 `Status` 상자는 하나다 — `-> Status[Out | Err]` 또는 `-> Out | Status[Err]`. `Status[A] | Status[B]`(상자 둘)는 `Status[T]` 가 불변이라 concrete 직접 반환이 mypy strict 에서 막히고 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지다(형태 금지). <span>09-04 · 현장 보고 3 S-5(ninja §2.2 R-3463 · `check-api-error-controller-contract` 표준 트리 슬라이스 · 프로필 무관).</span> | D58+§4 | `ast` | principle |  | **blocker** |\n"
"| 649 | 성공 응답이 판별 키로 갈리는 union 이면 이름 붙은 `RootModel` 하나로 선언한다 — ninja `Schema` 를 함께 상속하지 않는다(메타클래스 충돌 · `[metaclass]`·`[call-arg] root`). <span>09-04 · 현장 보고 3 S-5(ninja §3.1 R-3464 · 표준 트리 슬라이스).</span> | D58+§4 | `ast` | principle |  | **blocker** |\n")
t = t[:e] + rows + t[e:]
def cell(old, new):
    global t; assert t.count(old) == 1, old; t = t.replace(old, new)
cell("| **`ast`** | 파일 내용을 파싱하면 판정된다. **사람 판단 0** | **291** |", "| **`ast`** | 파일 내용을 파싱하면 판정된다. **사람 판단 0** | **293** |")
cell("| `ast` | 279 | 7 | 4 | 1 | **291** |", "| `ast` | 281 | 7 | 4 | 1 | **293** |")
cell("| **계** | **498** | **20** | **10** | **22** | **550** |", "| **계** | **500** | **20** | **10** | **22** | **552** |")
cell("| `path`+`ast` 의 blocker | **433** |", "| `path`+`ast` 의 blocker | **435** |")
# #63 stale — 08-25 개정 span
old63 = "| 63 | 오류 응답은 operation 이 response={status: <Bc>ErrorSchema} 로 직접 선언하고"
assert t.count(old63) == 1
t = t.replace(old63, "| 63 | 오류 응답은 operation 이 response={status: 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base — base 뭉뚱그림 금지 · 2026-08-25 R-0681 rev2/R-0087 rev2)} 로 직접 선언하고")
spec.write_text(t, encoding="utf-8"); print("tree-revision-spec: +2 rows · ast 293 · 계 552 · 읽는 법 435 · #63 span")
own = pathlib.Path("workspace/plan/2026-08-11-rule-owner-map.md"); u = own.read_text(encoding="utf-8")
a = u.index("| 647 | ast+ | scripts/check-public-surface-annotation.py"); e = u.index("\n", a) + 1
u = u[:e] + ("| 648 | ast | scripts/check-api-error-controller-contract.py | — | 신설 | 09-04 현장 보고 3 S-5 — 반환 주석 `Status` 상자 하나(표준 트리 슬라이스 · 프로필 무관) |\n"
             "| 649 | ast | scripts/check-api-error-controller-contract.py | — | 신설 | 09-04 현장 보고 3 S-5 — `Schema`+`RootModel` 동시 상속 금지(표준 트리 슬라이스) |\n") + u[e:]
old63o = "| 63 | ast | scripts/check-openapi-error-declaration.py | — | 신설 |  |"
assert u.count(old63o) == 1
u = u.replace(old63o, "| 63 | ast | scripts/check-openapi-error-declaration.py | — | 신설 | 08-25 개정(base 뭉뚱그림 금지 · R-0681 rev2) 반영 — 09-04 현장 보고 3 S-5 에서 검사기 docstring·조치 문면 정합 |")
own.write_text(u, encoding="utf-8"); print("rule-owner-map: +2 rows · #63 비고")
