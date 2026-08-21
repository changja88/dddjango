"""O-7 **외부** 인수 테스트 — 산출물이 쓴 테스트에 의존하지 않는다.

왜 이 파일이 있어야 하는가(전수 리뷰 레인 AU 발견 6): 앞선 인수 판형은 `manage.py test`,
곧 **처치가 직접 작성한 스위트**가 green 인지를 물었다. 그러면 두 방향으로 편향이 생긴다 —
ⓐ 필요한 테스트를 아예 안 쓴 산출물이 자기 스위트 green 으로 통과하고 ⓑ 더 철저히 쓴 암은
자기 결함을 더 드러내 인수에서 떨어진다. 인수 통과 여부가 **처치와 상관된 선택 변수**가 되고,
그건 인수 게이트가 막으려던 바로 그것이다.

이 스위트는 구현을 읽지 않고 **HTTP 표면만** 두드린다. 세 암에 같은 파일·같은 명령으로 돌고,
발주 봉인의 일부로 동결된다.

## 무엇을 가정하는가 (발주문이 고정한 것만)

- 발주문: 「재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.」
- 고정 시드: `Widget stock=10 price=1000` · `Gadget stock=3 price=2000`
- 고정 게이트: plain Django · Django 기본 test

**경로·필드 이름은 가정하지 않는다.** 그건 파이프라인의 설계 자유이고, 강제하면 인수가
설계를 지시하게 된다. 대신 **OpenAPI/URLconf 를 훑어 주문 생성 엔드포인트를 발견**하고,
발견 실패 자체를 인수 실패로 본다(공개 표면이 없으면 발주를 이행하지 않은 것이다).

## 실행

    cd <타깃> && python manage.py test \\
        --pattern='test_external_acceptance.py' \\
        <이 파일을 복사해 둔 위치>

또는 pytest 계열이면 같은 파일을 직접 지목한다. 러너는 발주 봉인이 고정한다.

exit 비-0 = **인수 실패 → 그 런은 채점하지 않는다**(판정 실패).
"""
from __future__ import annotations

# ab-diag: Django 4.2.30 x Py3.14 비호환(BaseContext.__copy__가 super()를 복사) 우회 패치.
# 진단 파생본 전용 — 동결 인수 스위트·산출물 무수정, 채점 입력 아님.
def _ab_diag_patch():
    from django.template.context import BaseContext
    def _copy(self):
        dup = self.__class__.__new__(self.__class__)
        dup.__dict__.update(self.__dict__)
        dup.dicts = self.dicts[:]
        return dup
    BaseContext.__copy__ = _copy
_ab_diag_patch()


import json
import re

from django.test import Client, TestCase
from django.urls import get_resolver


# 「주문 생성으로 보이는 POST 경로」를 URLconf 에서 찾는다. 이름을 강제하지 않되,
# 발견 실패는 인수 실패다 — 공개 표면이 없으면 발주가 이행되지 않은 것이다.
_ORDER_HINT = re.compile(r"order", re.IGNORECASE)


def _candidate_paths() -> "list[str]":
    out: "list[str]" = []
    for pattern in get_resolver().url_patterns:
        for sub in getattr(pattern, "url_patterns", [pattern]):
            raw = str(getattr(sub, "pattern", ""))
            if _ORDER_HINT.search(raw):
                out.append("/" + raw.lstrip("^").rstrip("$").lstrip("/"))
    return sorted(set(out))


class ExternalAcceptance(TestCase):
    """A1~A4 — 발주문이 약속한 **바깥에서 보이는 동작**만 본다."""

    maxDiff = None

    def setUp(self) -> None:
        self.client = Client()
        self.paths = _candidate_paths()

    def _post(self, body: "dict"):
        """후보 경로에 차례로 던져 **처음으로 4xx 가 아닌 형식 응답**을 낸 곳을 쓴다."""
        last = None
        for path in self.paths:
            resp = self.client.post(path, data=json.dumps(body),
                                    content_type="application/json")
            last = resp
            if resp.status_code != 404:
                return resp
        return last

    def test_a0_public_surface_exists(self) -> None:
        self.assertTrue(self.paths,
                        "주문 생성으로 보이는 공개 경로를 URLconf 에서 찾지 못했다 — "
                        "발주가 요구한 API 표면이 없다")

    def test_a1_sufficient_stock_creates_order_and_decrements(self) -> None:
        """재고 충분 → 생성 성공(2xx) **그리고 재고가 실제로 줄어든다**."""
        before = self._stock("Widget")
        resp = self._post({"sku": "Widget", "quantity": 2})
        self.assertIn(resp.status_code, (200, 201),
                      f"재고 충분인데 생성이 실패했다: {resp.status_code} {resp.content[:200]!r}")
        after = self._stock("Widget")
        self.assertEqual(after, before - 2,
                         f"재고가 주문 수량만큼 줄지 않았다: {before} → {after}")

    def test_a2_insufficient_stock_is_409_and_stock_unchanged(self) -> None:
        """재고 부족 → **409** 그리고 재고 불변. 이 발주의 핵심 판정이다."""
        before = self._stock("Gadget")
        resp = self._post({"sku": "Gadget", "quantity": before + 1})
        self.assertEqual(resp.status_code, 409,
                         f"재고 부족인데 409 가 아니다: {resp.status_code}")
        self.assertEqual(self._stock("Gadget"), before, "거절했는데 재고가 변했다")

    def test_a3_unknown_product_is_404(self) -> None:
        resp = self._post({"sku": "NoSuchProduct", "quantity": 1})
        self.assertEqual(resp.status_code, 404,
                         f"없는 상품인데 404 가 아니다: {resp.status_code}")

    def test_a4_no_oversell_under_contention(self) -> None:
        """경합에서 **oversell 0** — 재고가 음수로 가지 않는다.

        이 스위트가 스레드를 직접 띄우지 않는 이유: 테스트 DB 백엔드(sqlite)에서 스레드 경합은
        플랫폼 의존이라 **거짓 red** 를 낸다. 대신 «가용 재고보다 많은 요청을 순차로 밀어
        넣었을 때 성공 건수가 재고를 넘지 않는가»를 본다 — oversell 의 정의 그 자체이고,
        구현 메커니즘(CAS·락·제약)을 지시하지 않는다.
        """
        stock = self._stock("Gadget")
        ok = 0
        for _ in range(stock + 3):
            resp = self._post({"sku": "Gadget", "quantity": 1})
            if resp.status_code in (200, 201):
                ok += 1
        self.assertLessEqual(ok, stock, f"재고 {stock} 인데 성공 {ok} 건 — oversell")
        self.assertGreaterEqual(self._stock("Gadget"), 0, "재고가 음수가 됐다")

    # ── 재고 조회는 **모델을 직접 읽지 않는다**(구현 구조를 가정하지 않기 위해) ──
    def _stock(self, sku: str) -> int:
        """공개 표면에서 재고를 읽는다. 조회 표면이 없으면 DB 를 최후 수단으로 쓴다.

        DB 폴백을 두는 이유: 발주문은 조회 API 를 요구하지 않았다. 조회가 없다고 인수를
        떨어뜨리면 **발주에 없는 요구**를 인수가 추가하는 것이 된다.
        """
        for path in self.paths:
            resp = self.client.get(path)
            if resp.status_code == 200:
                try:
                    payload = json.loads(resp.content)
                except ValueError:
                    continue
                rows = payload if isinstance(payload, list) else payload.get("items", [])
                for row in rows or []:
                    if isinstance(row, dict) and row.get("sku") == sku:
                        for key in ("stock", "quantity", "on_hand"):
                            if isinstance(row.get(key), int):
                                return row[key]
        return self._stock_from_db(sku)

    def _stock_from_db(self, sku: str) -> int:
        from django.apps import apps
        for model in apps.get_models():
            names = {f.name for f in model._meta.get_fields() if hasattr(f, "name")}
            if "stock" in names and ("sku" in names or "name" in names):
                key = "sku" if "sku" in names else "name"
                obj = model.objects.filter(**{key: sku}).first()
                if obj is not None:
                    return int(getattr(obj, "stock"))
        self.fail(f"재고를 읽을 표면이 없다: {sku}")
        return 0


# ab-diag v3: 스위트가 가정만 하고 자급하지 않는 고정 시드(발주 봉인 문면)를 setUp 에서 만든다.
_orig_setUp = ExternalAcceptance.setUp
def _seeded_setUp(self):
    from django.apps import apps
    for m in apps.get_models():
        names = {f.name for f in m._meta.get_fields() if hasattr(f, "name")}
        if "stock" in names and ("sku" in names or "name" in names):
            key = "sku" if "sku" in names else "name"
            for label, stock, price in (("Widget", 10, 1000), ("Gadget", 3, 2000)):
                defaults = {"stock": stock}
                if "price" in names:
                    defaults["price"] = price
                m.objects.get_or_create(**{key: label}, defaults=defaults)
    _orig_setUp(self)
ExternalAcceptance.setUp = _seeded_setUp
