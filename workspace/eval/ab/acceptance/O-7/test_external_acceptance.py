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
설계를 지시하게 된다. 대신 **URLconf 를 훑어 주문 생성 엔드포인트를 발견**하고,
발견 실패 자체를 인수 실패로 본다(공개 표면이 없으면 발주를 이행하지 않은 것이다).

## 개정 1 (2026-08-21 · BK1 첫 실전 실측 · 사용자 ⓑ«수리 후 잔여 런» 승인)

BK1 세 암 공통으로 이 스위트 자신의 결함 4건이 실측됐다 — **판정 문면(A0~A4 의 단언)은
한 글자도 바꾸지 않고** 측정 장치만 수리한다:

 ① Django 4.2.30 × Python 3.14 에서 테스트 클라이언트의 템플릿 계측이
    `BaseContext.__copy__` 크래시 → 깨진 환경에서만 켜지는 가드된 호환 패치.
 ② 고정 시드를 스위트가 자급하지 않았다 — 테스트 DB 는 빈 채로 만들어지므로 «고정 시드»
    가정은 스위트가 스스로 이행해야 성립한다 → `setUp` 자급(`get_or_create`).
 ③ 경로 발견이 include prefix 를 유실했다(`/orders` 를 치고 실제는 `/api/orders`)
    → 재귀 합성으로 전체 경로를 조립(admin 네임스페이스는 제외 — 로그인 302 가
    발견 프로브를 오염시킨다).
 ④ 「필드 이름을 가정하지 않는다」면서 `sku` 를 가정하고 있었다(BK1 세 암의 실제 계약은
    `product_id`) → **무해 프로브**(없는 상품 주문 = 404, 주문이 생기지 않는다)로
    상품 필드와 값 종류를 발견한다.

## 실행

    cd <타깃> && python manage.py test \\
        --pattern='test_external_acceptance.py' \\
        <이 파일을 복사해 둔 위치>

또는 pytest 계열이면 같은 파일을 직접 지목한다. 러너는 발주 봉인이 고정한다.

exit 비-0 = **인수 실패 → 그 런은 채점하지 않는다**(판정 실패).
"""
from __future__ import annotations

import json
import re

from django.test import Client, TestCase
from django.urls import get_resolver

# 「주문 생성으로 보이는 POST 경로」를 URLconf 에서 찾는다. 이름을 강제하지 않되,
# 발견 실패는 인수 실패다 — 공개 표면이 없으면 발주가 이행되지 않은 것이다.
_ORDER_HINT = re.compile(r"order", re.IGNORECASE)

# 상품 참조 필드 후보(개정 1-④) — 시도 순서. kind: id=정수 PK · label=이름 문자열.
_PRODUCT_FIELDS: "tuple[tuple[str, str], ...]" = (
    ("product_id", "id"), ("sku", "label"), ("product", "id"),
    ("name", "label"), ("product_code", "label"),
)
_UNKNOWN: "dict[str, object]" = {"id": 999999999, "label": "NoSuchProduct"}


def _harden_context_copy() -> None:
    """개정 1-①: Django 4.2 × Py3.14 의 `BaseContext.__copy__` 크래시를 우회한다.

    깨진 환경에서만 켠다 — 정상 환경은 한 줄도 바꾸지 않는다. 이 패치가 없으면
    4xx/HTML 응답을 받는 순간 테스트 클라이언트 계측이 AttributeError 로 죽어
    모든 판정이 원인 불명 ERROR 로 뭉개진다(BK1 실측)."""
    from copy import copy as _copy

    from django.template.context import BaseContext, Context

    try:
        _copy(Context())
        return
    except AttributeError:
        pass

    def _fixed_copy(self):  # noqa: ANN001 — Django 내부 시그니처
        dup = self.__class__.__new__(self.__class__)
        dup.__dict__.update(self.__dict__)
        dup.dicts = self.dicts[:]
        return dup

    BaseContext.__copy__ = _fixed_copy


_harden_context_copy()


def _walk_routes(patterns, prefix: str = ""):
    """개정 1-③: include 를 재귀로 내려가며 **prefix 를 합성**한 전체 라우트를 낸다.

    admin 네임스페이스는 통째로 건너뛴다 — 그 경로들은 302(로그인)를 반환해
    «404 가 아닌 첫 응답» 발견을 오염시킨다."""
    for p in patterns:
        raw = str(getattr(p, "pattern", ""))
        subs = getattr(p, "url_patterns", None)
        if subs is not None:
            if getattr(p, "app_name", None) == "admin":
                continue
            yield from _walk_routes(subs, prefix + raw)
        else:
            yield prefix + raw


def _candidate_paths() -> "list[str]":
    out: "list[str]" = []
    for route in _walk_routes(get_resolver().url_patterns):
        if not _ORDER_HINT.search(route):
            continue
        if "<" in route:
            continue  # 경로 변수(<int:pk> 등)는 값 없이 칠 수 없다 — 생성 표면이 아니다
        route = route.replace("^", "").replace("$", "")
        out.append("/" + route.lstrip("/"))
    return sorted(set(out))


def _json_body(resp) -> "dict | list | None":
    try:
        return json.loads(resp.content)
    except ValueError:
        return None


class ExternalAcceptance(TestCase):
    """A1~A4 — 발주문이 약속한 **바깥에서 보이는 동작**만 본다."""

    maxDiff = None

    def setUp(self) -> None:
        self.client = Client()
        self.paths = _candidate_paths()
        self._ensure_seed()
        self._discover_contract()

    # ── 개정 1-② 시드 자급 ──
    def _seed_model(self):
        """(모델, 이름 필드, 전체 필드명) — stock + (sku|name) 을 가진 모델."""
        from django.apps import apps

        for model in apps.get_models():
            names = {f.name for f in model._meta.get_fields() if hasattr(f, "name")}
            if "stock" in names and ("sku" in names or "name" in names):
                return model, ("sku" if "sku" in names else "name"), names
        return None, None, set()

    def _ensure_seed(self) -> None:
        model, key, names = self._seed_model()
        if model is None:
            return  # 시드를 실을 모델이 없다 — _stock 이 기존 문면으로 실패한다
        for label, stock, price in (("Widget", 10, 1000), ("Gadget", 3, 2000)):
            defaults: "dict[str, object]" = {"stock": stock}
            if "price" in names:
                defaults["price"] = price
            model.objects.get_or_create(**{key: label}, defaults=defaults)

    # ── 개정 1-④ 계약 발견(무해 프로브) ──
    def _discover_contract(self) -> None:
        """주문 생성의 (경로, 상품 필드, 값 종류)를 «없는 상품» 프로브로 발견한다.

        올바른 경로+필드면 404 가 오고 **주문은 생기지 않는다**(무해). 경로가 틀리면
        라우팅 404(HTML), 필드가 틀리면 입력 계약 4xx — JSON 404 를 우선 채택하고,
        없으면 아무 404 나 받는다(후보 경로는 전부 URLconf 실존 라우트다)."""
        self.order_path: "str | None" = None
        self.product_field: "str | None" = None
        self.value_kind: str = "label"
        fallback: "tuple[str, str, str] | None" = None
        for path in self.paths:
            for field, kind in _PRODUCT_FIELDS:
                resp = self.client.post(
                    path,
                    data=json.dumps({field: _UNKNOWN[kind], "quantity": 1}),
                    content_type="application/json",
                )
                if resp.status_code != 404:
                    continue
                if _json_body(resp) is not None:
                    self.order_path, self.product_field, self.value_kind = path, field, kind
                    return
                if fallback is None:
                    fallback = (path, field, kind)
        if fallback is not None:
            self.order_path, self.product_field, self.value_kind = fallback

    def _ref(self, label: str):
        """상품 참조값 — 발견된 값 종류가 id 면 시드 행의 PK, 아니면 이름 그대로."""
        if self.value_kind != "id":
            return label
        model, key, _names = self._seed_model()
        obj = model.objects.filter(**{key: label}).first() if model is not None else None
        self.assertIsNotNone(obj, f"시드 상품이 없다: {label}")
        return obj.pk

    def _post(self, body: "dict"):
        """발견된 계약 경로로 던진다. 발견 실패면 후보 전체를 훑는다(기존 동작)."""
        if self.order_path is not None:
            return self.client.post(self.order_path, data=json.dumps(body),
                                    content_type="application/json")
        last = None
        for path in self.paths:
            resp = self.client.post(path, data=json.dumps(body),
                                    content_type="application/json")
            last = resp
            if resp.status_code != 404:
                return resp
        return last

    def _post_order(self, label: str, quantity: int):
        field = self.product_field or "sku"
        return self._post({field: self._ref(label), "quantity": quantity})

    def test_a0_public_surface_exists(self) -> None:
        self.assertTrue(self.paths,
                        "주문 생성으로 보이는 공개 경로를 URLconf 에서 찾지 못했다 — "
                        "발주가 요구한 API 표면이 없다")

    def test_a1_sufficient_stock_creates_order_and_decrements(self) -> None:
        """재고 충분 → 생성 성공(2xx) **그리고 재고가 실제로 줄어든다**."""
        before = self._stock("Widget")
        resp = self._post_order("Widget", 2)
        self.assertIn(resp.status_code, (200, 201),
                      f"재고 충분인데 생성이 실패했다: {resp.status_code} {resp.content[:200]!r}")
        after = self._stock("Widget")
        self.assertEqual(after, before - 2,
                         f"재고가 주문 수량만큼 줄지 않았다: {before} → {after}")

    def test_a2_insufficient_stock_is_409_and_stock_unchanged(self) -> None:
        """재고 부족 → **409** 그리고 재고 불변. 이 발주의 핵심 판정이다."""
        before = self._stock("Gadget")
        resp = self._post_order("Gadget", before + 1)
        self.assertEqual(resp.status_code, 409,
                         f"재고 부족인데 409 가 아니다: {resp.status_code}")
        self.assertEqual(self._stock("Gadget"), before, "거절했는데 재고가 변했다")

    def test_a3_unknown_product_is_404(self) -> None:
        field = self.product_field or "sku"
        resp = self._post({field: _UNKNOWN[self.value_kind], "quantity": 1})
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
            resp = self._post_order("Gadget", 1)
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
                payload = _json_body(resp)
                if payload is None:
                    continue
                rows = payload if isinstance(payload, list) else payload.get("items", [])
                for row in rows or []:
                    if not isinstance(row, dict):
                        continue
                    labels = {row.get(k) for k in ("sku", "name", "product_code")}
                    if sku in labels:
                        for key in ("stock", "quantity", "on_hand"):
                            if isinstance(row.get(key), int):
                                return row[key]
        return self._stock_from_db(sku)

    def _stock_from_db(self, sku: str) -> int:
        model, key, _names = self._seed_model()
        if model is not None:
            obj = model.objects.filter(**{key: sku}).first()
            if obj is not None:
                return int(getattr(obj, "stock"))
        self.fail(f"재고를 읽을 표면이 없다: {sku}")
        return 0
