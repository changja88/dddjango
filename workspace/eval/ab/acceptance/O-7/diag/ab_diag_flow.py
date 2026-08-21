# ab-diag-flow: 발주 이행 최종 진단 — 채점 입력 아님.
# 동결 인수 스위트가 결함 3건(Py3.14 크래시·시드 미자급·경로 prefix 유실)으로 판정 불능이라,
# 실제 경로(/api/orders)·실제 계약(product_id)으로 네 시나리오를 직접 관측한다.
import json

from django.test import Client, TestCase


def _patch_context_copy():
    # Django 4.2.30 x Py3.14: BaseContext.__copy__ 가 super() 를 복사해 크래시 — 진단 전용 우회.
    from django.template.context import BaseContext

    def _copy(self):
        dup = self.__class__.__new__(self.__class__)
        dup.__dict__.update(self.__dict__)
        dup.dicts = self.dicts[:]
        return dup

    BaseContext.__copy__ = _copy


_patch_context_copy()


class DiagFlow(TestCase):
    def _post(self, client, body):
        return client.post(
            "/api/orders", data=json.dumps(body), content_type="application/json"
        )

    def test_flow(self):
        from catalog.models import Product

        w = Product.objects.create(name="Widget", stock=10, price=1000)
        g = Product.objects.create(name="Gadget", stock=3, price=2000)
        c = Client()
        out = {}

        r = self._post(c, {"product_id": w.id, "quantity": 2})
        w.refresh_from_db()
        out["a1_충분"] = [r.status_code, r.content[:100].decode("utf-8", "replace"), f"재고 10→{w.stock}"]

        r = self._post(c, {"product_id": g.id, "quantity": 99})
        g.refresh_from_db()
        out["a2_부족"] = [r.status_code, r.content[:100].decode("utf-8", "replace"), f"재고 {g.stock}"]

        r = self._post(c, {"product_id": 999999, "quantity": 1})
        out["a3_없는상품"] = [r.status_code, r.content[:100].decode("utf-8", "replace")]

        ok = 0
        for _ in range(g.stock + 3):
            if self._post(c, {"product_id": g.id, "quantity": 1}).status_code in (200, 201):
                ok += 1
        g.refresh_from_db()
        out["a4_oversell"] = [f"성공 {ok}건", f"잔여재고 {g.stock}"]

        print("DIAG:", json.dumps(out, ensure_ascii=False))
