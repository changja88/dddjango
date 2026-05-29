"""V2 증거 — B1(빈혈/죽은 도메인)이 구조적으로 발생하는지/막히는지 결정적으로 점검.

두 축:
  (a) domain-owns-rule: 프로덕션 경로가 domain.Product.deduct()를 실제로 호출하는가? (spy)
  (b) repo-logic-free : 리포지토리 쓰기 가드에 비즈니스 규칙(stock>=qty)이 새어드는가? (소스 검사)
"""
import inspect
from contextlib import contextmanager
from unittest.mock import patch

from django.test import TestCase

from .. import domain
from ..application import ConditionalOrderService, OptimisticOrderService
from ..models import ProductConditional, ProductOptimistic
from ..repositories import ConditionalRepository, OptimisticRepository


@contextmanager
def track_deduct_calls():
    """domain.Product.deduct 호출을 추적하되 실제 동작은 보존한다(wraps)."""
    calls: list[tuple[int, int]] = []
    original = domain.Product.deduct

    def wrapper(self, quantity):
        calls.append((self.id, quantity))
        return original(self, quantity)

    with patch.object(domain.Product, "deduct", wrapper):
        yield calls


class DomainOwnsRuleTest(TestCase):
    """(a) 도메인 규칙이 프로덕션 경로에서 실제로 호출되는가."""

    def test_optimistic_calls_domain_rule_in_production_path(self) -> None:
        ProductOptimistic.objects.create(id=1, stock=5, version=0)
        with track_deduct_calls() as calls:
            OptimisticOrderService().place_order(1, 3)
        # 도메인 규칙이 권위로 호출됨 → 죽은 코드 아님.
        self.assertEqual(calls, [(1, 3)])

    def test_conditional_never_calls_domain_rule(self) -> None:
        ProductConditional.objects.create(id=1, stock=5)
        with track_deduct_calls() as calls:
            ConditionalOrderService().place_order(1, 3)
        # 판정이 SQL에 있어 도메인 규칙이 한 번도 안 불림 = B1(죽은 도메인 메서드).
        self.assertEqual(calls, [])


class RepoLogicFreeTest(TestCase):
    """(b) 비즈니스 규칙이 리포지토리(인프라)에 새어드는가 — 'repo는 로직 없음' 원칙."""

    def test_optimistic_repo_has_no_business_rule(self) -> None:
        src = inspect.getsource(OptimisticRepository)
        # 재고 판정(stock>=qty)이 repo에 없어야 한다.
        self.assertNotIn("stock__gte", src)
        self.assertNotIn("stock >=", src)
        self.assertNotIn("stock>=", src)
        # 대신 경합 감지(version 가드)만 존재.
        self.assertIn("version", src)

    def test_conditional_repo_embeds_business_rule(self) -> None:
        src = inspect.getsource(ConditionalRepository)
        # 대조: 현행 패턴은 비즈니스 규칙을 SQL WHERE에 복제한다(원칙 위반 가시화).
        self.assertIn("stock__gte", src)


class StockInvariantBackstopTest(TestCase):
    """보너스: PositiveIntegerField가 stock>=0 CHECK를 자동 생성하는지(불변식 백스톱) 실증."""

    def test_optimistic_table_has_stock_check_constraint(self) -> None:
        from django.db import connection

        table = ProductOptimistic._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=%s",
                [table],
            )
            ddl = cursor.fetchone()[0]
        # Django 4.2 + SQLite는 PositiveIntegerField에 CHECK("stock" >= 0)을 자동 emit.
        self.assertIn("stock", ddl)
        self.assertIn(">= 0", ddl.replace('"stock"', "stock"))
