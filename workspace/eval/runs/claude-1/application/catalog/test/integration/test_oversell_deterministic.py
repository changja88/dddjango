"""over-sell 불가 결정적 증명 (§4.6 1차·권위, 옵션 A).

DjangoProductRepository.deduct_stock 조건부 UPDATE를 같은 stock=1 행에 순차로 두 번 호출.
- 첫 호출 rowcount=1(차감 성공), 둘째 rowcount=0(재고 부족).
- 최종 stock=0.
스레드 타이밍에 의존하지 않아 엔진 무관·결정적이다(2차 스레드 테스트는 옵션 A라 필수 아님).
"""
from django.test import TestCase

from application.catalog.infra_layer.django_catalog.models.product_model import (
    ProductModel,
)
from application.catalog.infra_layer.repository.django_product_repository import (
    DjangoProductRepository,
)


class OversellDeterministicTest(TestCase):
    def setUp(self) -> None:
        self.product = ProductModel.objects.create(name="위젯", price=1000, stock=1)
        self.repository = DjangoProductRepository()

    def test_조건부_UPDATE_두번_호출시_둘째는_차감되지_않는다(self) -> None:
        first = self.repository.deduct_stock(self.product.id, 1)
        second = self.repository.deduct_stock(self.product.id, 1)

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
