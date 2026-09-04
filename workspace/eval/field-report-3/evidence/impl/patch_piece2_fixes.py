"""⑤-2 정정 — rv5-2-A N2-1(_exempt_override 별칭 전부) · N2-2(smoke Q′ 공허 단언) · N2-4(good payment 픽스처 mypy — use case 주입 Protocol).
B·C 정정은 결과 뒤 append. 실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib

P = pathlib.Path("dddjango/scripts/check-public-surface-annotation.py"); t = P.read_text(encoding="utf-8")
old = ("    want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]\n    for b in cls.bases:\n        base = _resolved_base(b, bindings, aliases)\n        if base in want or (fn.name == \"deconstruct\" and base.endswith(\"Field\")):\n            return True\n    return False\n")
new = ("    want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]\n    for b in cls.bases:\n        for base in _resolved_bases(b, bindings, aliases):  # 별칭 정의 전부(mixin-first 중간 ClassDef 포함) — `_is_declarative_class` 와 같은 해소\n            if base in want or (fn.name == \"deconstruct\" and base.endswith(\"Field\")):\n                return True\n    return False\n")
assert t.count(old) == 1; t = t.replace(old, new)
# _resolved_base 호출처 0 → 삭제
i = t.index("def _resolved_base(node: ast.AST, bindings: dict[str, str],"); j = t.index("\n\n\ndef _resolved_bases(", i)
t = t[:i] + t[j + 3:]
assert "_resolved_base(" not in t.replace("_resolved_bases(", "")
P.write_text(t, encoding="utf-8"); print("check-public-surface-annotation.py: N2-1 (+ _resolved_base 삭제)")

S = pathlib.Path("workspace/tools/registry_gate_smoke.py"); u = S.read_text(encoding="utf-8")
old = "            and all(\"fresh_probe\" in l for l in payload_q2.get(\"candidate_lines\", []))\n        )\n"
new = ("            and payload_q2.get(\"candidate_lines\") and all(\"fresh_probe\" in l for l in payload_q2[\"candidate_lines\"])\n"
       "            and payload_q2.get(\"candidate_records\") and all(r.get(\"rule\") == \"#69\" for r in payload_q2[\"candidate_records\"])\n        )\n")
assert u.count(old) == 1; S.write_text(u.replace(old, new), encoding="utf-8"); print("registry_gate_smoke.py: N2-2")

# N2-4 — good payment 컨트롤러에 use case 주입(Protocol 은 application_layer 의 use case 실체 대신 컨트롤러 파일 최소성 편의)
G = pathlib.Path("workspace/eval/fixtures/api_error_controller/good/application/orders")
uc = G / "application_layer/payment/get_payment/get_payment_use_case.py"
uc.write_text('''from typing import Protocol

from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery


class GetPaymentUseCase(Protocol):
    def execute(self, query: GetPaymentQuery) -> object: ...
''', encoding="utf-8")
pc = G / "driving_layer/api/payment/payment_controller.py"; c = pc.read_text(encoding="utf-8")
old = ("from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery\n")
new = ("from application.orders.application_layer.payment.get_payment.get_payment_query import GetPaymentQuery\n"
       "from application.orders.application_layer.payment.get_payment.get_payment_use_case import GetPaymentUseCase\n")
assert c.count(old) == 1; c = c.replace(old, new)
old2 = "@api_controller(\"/payments\")\nclass PaymentController:\n    @http_get(\"/{payment_id}\", response={200: PaymentOut, 404: OrdersErrorSchema})\n"
new2 = ("@api_controller(\"/payments\")\nclass PaymentController:\n    def __init__(self, use_case: GetPaymentUseCase) -> None:\n        self._use_case: GetPaymentUseCase = use_case\n\n"
        "    @http_get(\"/{payment_id}\", response={200: PaymentOut, 404: OrdersErrorSchema})\n")
assert c.count(old2) == 1; pc.write_text(c.replace(old2, new2), encoding="utf-8"); print("good payment fixture: N2-4 (use case Protocol 파일 + 주입)")
