"""동시성 인수 테스트 — oversell 0 / 경합 소진 503 (바깥 루프 Red).

근거: 설계 명세 §3.3 Test criteria (c)·(e), §5 행위7·행위8.
블랙박스: HTTP 계약만 검증한다. 동시 요청은 Django test Client로 `/api/orders`에
스레드 병렬 POST한다. 실제 커밋이 스레드 간에 보여야 하므로 TransactionTestCase를
사용한다(TestCase의 트랜잭션 래핑으로는 동시성을 관찰할 수 없다 — implementation-test §20).

각 테스트 = 외부 관찰 가능 행위 1개:
- 행위7: 재고 M인 상품에 동시 N(>M) 주문 → 정확히 M건 201, oversell 0
- 행위8(스켈레톤): retry 상한 초과(경합 소진) → 503 + Retry-After (재현 까다로움)
"""
import json
import threading
import unittest

from django.test import Client, TransactionTestCase

from catalog.models import Product

ORDERS_URL = "/api/orders"


class OversellPreventionTest(TransactionTestCase):
    """행위7: 동시 N요청·재고 M<N → 정확히 M건 201·나머지 거절, oversell 0.

    명세 §3.3 criteria (c): "동시 N요청(재고 M<N)에 정확히 M건만 성공·oversell 0".
    차감 실패 건은 트랜잭션 롤백되어 주문 미생성(명세 §5-7).
    """

    # TransactionTestCase는 매 테스트 후 TRUNCATE로 catalog 시드를 비운다.
    # catalog 시드 데이터에 의존하지 않고 테스트가 직접 Product를 만든다.

    def test_concurrent_orders_never_oversell(self) -> None:
        stock_m = 5
        concurrent_n = 20
        quantity_each = 1
        product = Product.objects.create(name="Widget", price=1000, stock=stock_m)

        results: list[int] = []
        results_lock = threading.Lock()
        start_barrier = threading.Barrier(concurrent_n)

        def place_one() -> None:
            client = Client()
            # 모든 스레드가 동시에 출발하도록 정렬 → 경합 최대화
            start_barrier.wait()
            response = client.post(
                ORDERS_URL,
                data=json.dumps(
                    {"product_id": product.id, "quantity": quantity_each}
                ),
                content_type="application/json",
            )
            with results_lock:
                results.append(response.status_code)

        threads = [threading.Thread(target=place_one) for _ in range(concurrent_n)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        success_count = sum(1 for code in results if code == 201)
        # 정확히 M건만 성공 (oversell 0 — 성공이 재고를 절대 초과하지 않음)
        self.assertEqual(
            success_count,
            stock_m,
            f"성공 건수는 정확히 재고 {stock_m}이어야 한다. 실제 결과: {results}",
        )
        # 나머지는 거절(409 재고 부족, 또는 경합 소진 시 503) — 2xx는 M건뿐
        rejected = [code for code in results if code != 201]
        self.assertEqual(len(rejected), concurrent_n - stock_m)
        for code in rejected:
            self.assertIn(code, (409, 503), f"거절은 409 또는 503이어야 한다: {code}")

        # 관찰 가능 최종 상태: 재고는 정확히 0 (oversell이면 음수가 됐을 것)
        product.refresh_from_db()
        self.assertEqual(product.stock, 0)


class StockContentionExhaustionTest(TransactionTestCase):
    """행위8(스켈레톤): retry 상한 초과 → 503 + Retry-After (명세 §5-8, §3.3 criteria e).

    명세 §3.3: version CAS 0행 경합이 bounded retry(최대 3회)를 소진하면
    StockContentionExhausted → 503 + Retry-After (409 out-of-stock과 의미 분리).

    이 행위는 "재고는 충분하지만 경합만으로 retry가 소진되는" 상태를 결정론적으로
    재현해야 한다 — 이는 내부 retry 카운터·동시 version 충돌 타이밍에 의존하므로
    블랙박스 HTTP만으로는 안정적으로 강제하기 어렵다. 따라서 의도(계약)만 명시한
    스켈레톤으로 두고, coder가 안쪽 루프(응용 서비스 단위 테스트, §4.1 test_place_order_app)에서
    retry 소진 경로를 결정론적으로 검증한다. 여기서는 계약 형태만 고정한다.
    """

    @unittest.skip(
        "경합 소진(503)은 내부 retry 타이밍 의존 — 결정론적 재현은 단위 테스트(안쪽 루프) 영역. "
        "여기서는 503+Retry-After 계약 형태만 의도로 고정한다."
    )
    def test_retry_exhaustion_returns_503_with_retry_after(self) -> None:
        product = Product.objects.create(name="Widget", price=1000, stock=100)

        # 계약 의도(503 발생을 강제할 수 있게 되면 다음을 검증한다):
        response = self.client.post(
            ORDERS_URL,
            data=json.dumps({"product_id": product.id, "quantity": 1}),
            content_type="application/json",
        )

        # 503 Service Unavailable + Retry-After (일시적 경합 소진)
        self.assertEqual(response.status_code, 503)
        self.assertIn("Retry-After", response)
        self.assertEqual(response["Content-Type"], "application/problem+json")
        body = response.json()
        self.assertEqual(body["type"], "/problems/stock-contention")
        self.assertEqual(body["status"], 503)

        # 원자성: 부분 변경 없음 (재고 불변, 주문 미생성)
        product.refresh_from_db()
        self.assertEqual(product.stock, 100)
