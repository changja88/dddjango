"""POST /orders 인수 테스트 (바깥 루프 Red).

설계 명세 §3 외부 관찰 가능 행위 #1~#5를 블랙박스로 검증한다.
- 근거: design-spec.md §2(API 계약)·§2.4(성공 본문)·§2.5(Problem Details)·§3(행위 목록).
- 블랙박스 원칙: HTTP 상태 코드·헤더·JSON 본문과 외부 관찰(주문 생성 여부·재고 값)만 검증한다.
  내부 클래스·함수·DB 컬럼을 직접 호출하지 않는다. 단 "재고 감소/불변"·"주문 생성 여부"의
  관찰은 영속 데이터를 읽어 확인하는 것이 허용된다(외부 관찰 사실 — 명세 규율).
- 동시성(#6 over-sell)은 명세 §4.6에 따라 리포지토리 레벨 결정적 증명(내부 메커니즘)이 권위이므로
  여기(인수 레벨)에서는 검증하지 않는다.

이 시점에는 표준 트리(application.catalog ...) 프로덕션 모듈과 /orders 엔드포인트가 아직 없다.
따라서 임포트/엔드포인트 부재로 실패하는 것이 정상적인 Red다.
"""
import json

from django.test import TestCase
from django.urls import reverse, NoReverseMatch

# 명세 §5.2 표준 트리의 ORM 위치. 아직 프로덕션 코드가 없어 임포트 실패가 정상 Red다.
from application.catalog.infra_layer.django_catalog.models.product_model import ProductModel
from application.catalog.infra_layer.django_catalog.models.order_model import OrderModel


ORDERS_PATH = "/orders"


class PlaceOrderSuccessTest(TestCase):
    """행위 #1: 재고 충분 → 201 + Location + 성공 본문, Order 1건 생성, 재고 정확히 차감."""

    def setUp(self) -> None:
        # 재고 10, 단가 1000 짜리 상품 1건. 주문 수량 2.
        self.product = ProductModel.objects.create(name="위젯", price=1000, stock=10)

    def test_재고_충분하면_201과_성공_본문을_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 상태 코드 201
        self.assertEqual(response.status_code, 201)
        # 헤더: Location 과 Content-Type (명세 §2.3)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        body = response.json()
        self.assertEqual(response.headers["Location"], f"/orders/{body['id']}")
        # 성공 본문 형태 (명세 §2.4)
        self.assertEqual(body["product_id"], self.product.id)
        self.assertEqual(body["quantity"], 2)
        self.assertEqual(body["unit_price"], 1000)
        self.assertEqual(body["total_price"], 2000)
        self.assertEqual(body["status"], "CREATED")
        self.assertIn("id", body)

    def test_재고_충분하면_주문_1건이_생성된다(self) -> None:
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 외부 관찰: Order 정확히 1건 생성
        self.assertEqual(OrderModel.objects.count(), 1)

    def test_재고_충분하면_재고가_정확히_수량만큼_감소한다(self) -> None:
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 외부 관찰: stock 10 → 8 (정확히 quantity=2 감소)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)


class PlaceOrderInsufficientStockTest(TestCase):
    """행위 #2: 재고 부족 → 409 + Problem Details, Order 미생성, 재고 불변."""

    def setUp(self) -> None:
        # 재고 1 인데 2개 주문 → 부족.
        self.product = ProductModel.objects.create(name="위젯", price=1000, stock=1)

    def test_재고_부족하면_409와_problem_details를_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 상태 코드 409 + Content-Type problem+json (명세 §2.3)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        # Problem Details (명세 §2.5): title/status + 확장 필드
        body = response.json()
        self.assertEqual(body["title"], "Insufficient stock")
        self.assertEqual(body["status"], 409)
        self.assertEqual(body["product_id"], self.product.id)
        self.assertEqual(body["available_stock"], 1)
        self.assertEqual(body["requested_quantity"], 2)

    def test_재고_부족하면_주문이_생성되지_않는다(self) -> None:
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 외부 관찰: Order 미생성
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_재고_부족하면_재고가_변하지_않는다(self) -> None:
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
            content_type="application/json",
        )

        # 외부 관찰: stock 불변(1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)


class PlaceOrderProductNotFoundTest(TestCase):
    """행위 #3: 존재하지 않는 product_id → 404 + Problem Details, Order 미생성, 재고 불변."""

    def test_존재하지_않는_상품이면_404와_problem_details를_반환한다(self) -> None:
        # 어떤 상품도 만들지 않음 → 임의 PK 는 존재하지 않음.
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": 999999, "quantity": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["title"], "Product not found")
        self.assertEqual(body["status"], 404)

    def test_존재하지_않는_상품이면_주문이_생성되지_않는다(self) -> None:
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": 999999, "quantity": 1}),
            content_type="application/json",
        )

        self.assertEqual(OrderModel.objects.count(), 0)


class PlaceOrderValidationTest(TestCase):
    """행위 #4: 입력 검증 실패 → 400. 필드 실패는 errors 맵, JSON 파싱 실패는 errors 생략.

    모든 케이스에서 Order 미생성. (재고 불변은 검증 실패 시 차감 자체가 일어나지 않으므로
    대표로 한 케이스에서 재고 불변을 확인한다.)
    """

    def setUp(self) -> None:
        self.product = ProductModel.objects.create(name="위젯", price=1000, stock=10)

    def test_quantity_누락이면_400과_errors_맵을_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["title"], "Invalid request")
        self.assertEqual(body["status"], 400)
        # errors 는 필드명→사유 문자열 맵 (명세 §2.5)
        self.assertIn("errors", body)
        self.assertIn("quantity", body["errors"])
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_quantity_0이면_400과_errors_맵을_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 0}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["title"], "Invalid request")
        self.assertIn("quantity", body["errors"])
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_quantity_음수이면_400과_errors_맵을_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": -3}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.json()["errors"])
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_product_id_누락이면_400과_errors_맵을_반환한다(self) -> None:
        response = self.client.post(
            ORDERS_PATH,
            data=json.dumps({"quantity": 2}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["title"], "Invalid request")
        self.assertIn("product_id", body["errors"])
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_JSON_파싱_실패이면_400과_errors를_생략한다(self) -> None:
        # 깨진 JSON 본문 → 필드를 특정할 수 없어 errors 생략, detail 만 (명세 §2.5 분기 규칙)
        response = self.client.post(
            ORDERS_PATH,
            data="{not valid json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["title"], "Invalid request")
        self.assertEqual(body["status"], 400)
        self.assertNotIn("errors", body)
        self.assertIn("detail", body)
        self.assertEqual(OrderModel.objects.count(), 0)

    def test_검증_실패시_재고가_변하지_않는다(self) -> None:
        # 대표 케이스(quantity=0)로 차감 미발생 확인.
        self.client.post(
            ORDERS_PATH,
            data=json.dumps({"product_id": self.product.id, "quantity": 0}),
            content_type="application/json",
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)


class PlaceOrderMethodNotAllowedTest(TestCase):
    """행위 #5: 잘못된 메서드(GET /orders) → 405 + Allow: POST."""

    def test_GET_요청이면_405와_Allow_POST_헤더를_반환한다(self) -> None:
        response = self.client.get(ORDERS_PATH)

        self.assertEqual(response.status_code, 405)
        # Allow 헤더에 POST 광고 (명세 §2.3 / RFC 9110)
        self.assertEqual(response.headers["Allow"], "POST")
