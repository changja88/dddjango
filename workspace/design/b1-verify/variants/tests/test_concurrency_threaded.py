"""V1 보강 증거 — 실제 스레드 동시 부하(best-effort).

⚠️ 기판 주의: SQLite는 쓰기를 직렬화하므로 진짜 병렬 인터리빙이 제한된다. 따라서
   - optimistic/conditional: oversell이 없어야 한다(엄격 단언) — 안전성은 기판과 무관하게 성립.
   - naive: SQLite에선 lost update가 항상 재현되진 않는다(직렬화). 결함은 결정적 테스트가 이미 입증하므로
     여기서는 관찰만 하고 엄격 단언하지 않는다.
Postgres(READ COMMITTED)였다면 naive의 oversell도 부하에서 직접 재현된다 — FINDINGS.md 참조.
"""
import threading
from concurrent.futures import ThreadPoolExecutor

from django.db import OperationalError, connection
from django.test import TransactionTestCase

from .. import domain
from ..application import (
    ConditionalOrderService,
    NaiveOrderService,
    OptimisticOrderService,
)
from ..models import ProductConditional, ProductNaive, ProductOptimistic

INITIAL_STOCK = 20
WORKERS = 50


def _run_concurrent(place_order):
    """WORKERS개 스레드가 동시에 1개씩 주문. (성공수, 거절수, 충돌수, 락수) 반환."""
    barrier = threading.Barrier(WORKERS)
    results: list[str] = []
    lock = threading.Lock()

    def worker():
        barrier.wait()  # 가능한 한 동시에 출발
        try:
            place_order(1, 1)
            outcome = "ok"
        except domain.InsufficientStock:
            outcome = "rejected"
        except domain.ConcurrencyConflict:
            outcome = "conflict"
        except OperationalError:
            # SQLite 기판 한계(락). 안전성과 무관하므로 결과로 흡수한다 — FINDINGS 참조.
            outcome = "locked"
        finally:
            connection.close()  # 스레드별 연결 정리
        with lock:
            results.append(outcome)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(worker) for _ in range(WORKERS)]
        for f in futures:
            f.result()
    return (
        results.count("ok"),
        results.count("rejected"),
        results.count("conflict"),
        results.count("locked"),
    )


class OptimisticThreadedTest(TransactionTestCase):
    def test_no_oversell_under_load(self) -> None:
        ProductOptimistic.objects.create(id=1, stock=INITIAL_STOCK, version=0)
        ok, _rejected, _conflict, _locked = _run_concurrent(OptimisticOrderService().place_order)
        final = ProductOptimistic.objects.get(id=1).stock
        # 안전성: 성공 수가 초기 재고를 넘지 않고, 재고는 정확히 맞아떨어진다.
        self.assertLessEqual(ok, INITIAL_STOCK)
        self.assertEqual(final, INITIAL_STOCK - ok)
        self.assertGreaterEqual(final, 0)


class ConditionalThreadedTest(TransactionTestCase):
    def test_no_oversell_under_load(self) -> None:
        ProductConditional.objects.create(id=1, stock=INITIAL_STOCK)
        ok, _rejected, _conflict, _locked = _run_concurrent(ConditionalOrderService().place_order)
        final = ProductConditional.objects.get(id=1).stock
        self.assertLessEqual(ok, INITIAL_STOCK)
        self.assertEqual(final, INITIAL_STOCK - ok)
        self.assertGreaterEqual(final, 0)


class NaiveThreadedObservationTest(TransactionTestCase):
    """naive는 관찰만 — SQLite 직렬화로 결함이 가려질 수 있어 엄격 단언하지 않는다."""

    def test_observe_naive_accounting(self) -> None:
        ProductNaive.objects.create(id=1, stock=INITIAL_STOCK)
        ok, _rejected, _conflict, _locked = _run_concurrent(NaiveOrderService().place_order)
        final = ProductNaive.objects.get(id=1).stock
        sold = INITIAL_STOCK - final
        # 회계 일관성이 깨지면(판매수 != 차감수) lost update가 부하에서도 잡힌 것 — FINDINGS에 기록만.
        print(
            f"\n[naive observation] ok={ok} sold_by_stock={sold} final_stock={final} "
            f"(lost_update {'OBSERVED' if ok != sold else 'not observed on this substrate'})"
        )
        self.assertGreaterEqual(final, 0)  # PositiveIntegerField 하한만 보장
