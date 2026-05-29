"""POST /api/orders 엔드포인트 계약 인수 테스트 (바깥 루프 Red).

근거: 설계 명세 §2(계약)·§5(외부 관찰 가능 행위 목록).
블랙박스: HTTP 계약만 검증한다. ordering 구현 심볼이나 미설치 의존성
(Django Ninja 등)을 import하지 않고, Django test Client로 `/api/orders`에만
접근한다. 재고는 catalog.Product 픽스처로 구성한다.

각 테스트 = 외부 관찰 가능 행위 1개:
- 행위1: 재고 충분 → 201 + 가격 스냅샷 + Location + 재고 차감
- 행위2: 재고 부족 → 409 problem+json, 재고·주문 상태 불변
- 행위3: 없는 product_id → 404
- 행위4: quantity<1·타입 오류·필수 필드 누락 → 422
- 행위5: malformed JSON → 400
- 행위6: 미지원 Content-Type → 415
"""
import json

from django.test import TestCase

from catalog.models import Product

ORDERS_URL = "/api/orders"


class PlaceOrderSuccessTest(TestCase):
    """행위1: 재고 충분 시 주문 생성·재고 차감 (명세 §5-1, §2.2, §3.3 criteria a)."""

    def test_sufficient_stock_creates_order_and_deducts_stock(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id, "quantity": 3}),
            content_type="application/json",
        )

        # 201 Created
        self.assertEqual(response.status_code, 201)

        body = response.json()
        # 가격 스냅샷·주문 표현 (명세 §2.2 schema_out)
        self.assertIn("order_id", body)
        self.assertEqual(body["product_id"], product.id)
        self.assertEqual(body["quantity"], 3)
        self.assertEqual(body["unit_price"], 1000)
        self.assertEqual(body["total_price"], 3000)
        self.assertEqual(body["status"], "PLACED")
        self.assertIn("created_at", body)

        # Location 헤더 (생성 리소스 위치)
        self.assertIn("Location", response)
        self.assertEqual(response["Location"], f"/api/orders/{body['order_id']}")

        # 재고가 요청 수량만큼 차감됨 (관찰 가능 상태 변화)
        product.refresh_from_db()
        self.assertEqual(product.stock, 7)


class PlaceOrderOutOfStockTest(TestCase):
    """행위2: 재고 부족 시 409 + 상태 불변 (명세 §5-2, §2.3, §3.3 criteria b)."""

    def test_insufficient_stock_returns_409_and_leaves_state_unchanged(self) -> None:
        product = Product.objects.create(name="Gadget", price=2000, stock=3)

        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id, "quantity": 5}),
            content_type="application/json",
        )

        # 409 Conflict
        self.assertEqual(response.status_code, 409)
        # RFC 9457 Problem Details 미디어 타입
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], "/problems/out-of-stock")
        self.assertEqual(body["status"], 409)
        # 요청 수량 에코 (명세 §2.3 detail 확장)
        self.assertEqual(body["requested"], 5)

        # 재고 불변 (차감되지 않음)
        product.refresh_from_db()
        self.assertEqual(product.stock, 3)
        # 주문 미생성 — 응답에 order_id 없음 (블랙박스 관찰)
        self.assertNotIn("order_id", body)


class PlaceOrderProductNotFoundTest(TestCase):
    """행위3: 없는 상품 → 404 (명세 §5-3, §2.3)."""

    def test_unknown_product_returns_404(self) -> None:
        # 어떤 상품도 만들지 않음 → 존재하지 않는 id
        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": 999999, "quantity": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], "/problems/product-not-found")
        self.assertEqual(body["status"], 404)


class PlaceOrderValidationErrorTest(TestCase):
    """행위4: 검증 실패(수량<1·타입 오류·필수 필드 누락) → 422 (명세 §5-4, §2.3)."""

    def test_quantity_below_one_returns_422(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id, "quantity": 0}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], "/problems/validation-error")
        self.assertEqual(body["status"], 422)
        # errors[] 확장 (명세 §2.3 api minor m2)
        self.assertIn("errors", body)
        self.assertIsInstance(body["errors"], list)
        self.assertTrue(len(body["errors"]) >= 1)

        # 주문 미생성 → 재고 불변
        product.refresh_from_db()
        self.assertEqual(product.stock, 10)

    def test_missing_required_field_returns_422(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        # quantity 누락
        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        self.assertEqual(response.json()["type"], "/problems/validation-error")

    def test_wrong_type_returns_422(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        # quantity 가 정수가 아님
        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id, "quantity": "three"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["type"], "/problems/validation-error")


class PlaceOrderMalformedJsonTest(TestCase):
    """행위5: 파싱 불가 JSON → 400 (명세 §5-5, §2.3 — 422와 구분)."""

    def test_malformed_json_returns_400(self) -> None:
        response = self.client.post(
            ORDERS_URL,
            data="{not valid json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], "/problems/bad-request")
        self.assertEqual(body["status"], 400)


class PlaceOrderUnsupportedMediaTypeTest(TestCase):
    """행위6: 미지원 Content-Type → 415 (명세 §5-6, §2.3 — 400/422와 구분)."""

    def test_non_json_content_type_returns_415(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=10)

        # 본문은 폼 데이터이고 Content-Type 이 application/json 이 아님
        response = self.client.post(
            ORDERS_URL,
            data=f"product_id={product.id}&quantity=1",
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, 415)
        self.assertEqual(response["Content-Type"], "application/problem+json")

        body = response.json()
        self.assertEqual(body["type"], "/problems/unsupported-media-type")
        self.assertEqual(body["status"], 415)
