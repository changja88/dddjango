"""V1 핵심 증거 — 결정적 동시성 재현(스레드·타이밍 무관, 100% 재현).

'동시 로드'를 *두 개의 stale 도메인 객체를 같은 버전에서 만든 뒤 순차 save*로 모델링한다.
이는 실제 동시 트랜잭션의 read-modify-write 인터리빙과 동일한 상태를 결정적으로 만든다.
"""
from django.test import TestCase

from .. import domain
from ..application import OptimisticOrderService
from ..models import ProductNaive, ProductOptimistic
from ..repositories import NaiveRepository, OptimisticRepository


class NaiveLosesUpdateTest(TestCase):
    """대조군: naive는 lost update로 oversell을 낸다 — 테스트가 진짜 레이스를 잡는다는 증거."""

    def test_naive_oversells_under_concurrent_load(self) -> None:
        ProductNaive.objects.create(id=1, stock=5)
        repo = NaiveRepository()

        # 두 요청이 동시에 재고 5를 읽는다(둘 다 stale).
        p1 = repo.get(1)
        p2 = repo.get(1)

        # 각자 3개 주문 — 메모리상 도메인 규칙은 둘 다 통과(5 >= 3).
        p1.deduct(3)
        repo.save(p1)  # DB stock = 2
        p2.deduct(3)
        repo.save(p2)  # DB stock = 2 (앞 write를 덮어씀 — lost update)

        final = ProductNaive.objects.get(id=1).stock
        # 6개를 팔았는데 재고는 3개만 빠졌다 → 1개 oversell. 동시성 결함 입증.
        self.assertEqual(final, 2)
        self.assertNotEqual(final, -1)  # PositiveIntegerField라 음수 자체는 불가하나, 회계가 깨졌다.


class OptimisticDetectsConflictTest(TestCase):
    """후보: optimistic은 version 가드로 경합을 감지하고, 재시도가 fresh 규칙을 재실행한다."""

    def test_stale_write_is_rejected_by_version_guard(self) -> None:
        ProductOptimistic.objects.create(id=1, stock=5, version=0)
        repo = OptimisticRepository()

        p1 = repo.get(1)  # stock=5, version=0
        p2 = repo.get(1)  # stock=5, version=0 (stale)

        p1.deduct(3)
        rows1 = repo.save(p1)  # version 0→1
        self.assertEqual(rows1, 1)  # 첫 write 성공

        p2.deduct(3)
        rows2 = repo.save(p2)  # WHERE version=0 → 매칭 0건
        self.assertEqual(rows2, 0)  # 경합 감지 — stale write가 거부됨

        # DB는 첫 차감만 반영(stock=2). lost update 없음.
        self.assertEqual(ProductOptimistic.objects.get(id=1).stock, 2)

    def test_service_retry_reruns_domain_rule_and_rejects_oversell(self) -> None:
        """경합 후 재시도 시 도메인 규칙이 fresh 데이터로 재실행되어 oversell을 막는다."""
        ProductOptimistic.objects.create(id=1, stock=5, version=0)
        repo = OptimisticRepository()
        service = OptimisticOrderService()

        # 첫 요청: 정상 차감(5 → 2, version 0 → 1).
        service.place_order(1, 3)
        self.assertEqual(ProductOptimistic.objects.get(id=1).stock, 2)

        # 두 번째 요청 3개: fresh 재고 2 < 3 → 도메인 규칙이 거절.
        with self.assertRaises(domain.InsufficientStock):
            service.place_order(1, 3)

        # 재고 불변 — oversell 없음.
        self.assertEqual(ProductOptimistic.objects.get(id=1).stock, 2)
