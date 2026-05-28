"""schema_in 입력 검증 단위 테스트 (§2.5 / §5.6).

표현 계층 입력 어댑터가 도메인·DB 도달 전에 입력을 검증하는지 본다.
- 필드 단위 검증 실패(누락·0·음수·비정수)는 ValidationError(errors 맵)로 거절.
- JSON 자체 파싱 실패는 JsonParseError(필드 특정 불가 → errors 생략)로 거절.
- 유효한 입력은 PlaceOrderCommand로 변환.
"""
from django.test import SimpleTestCase

from application.catalog.application_layer.place_order.dto.place_order_command import (
    PlaceOrderCommand,
)
from application.catalog.presentation_layer.schema.schema_in import (
    JsonParseError,
    ValidationError,
    parse_place_order,
)


def _body(payload: str) -> bytes:
    return payload.encode("utf-8")


class ParsePlaceOrderValidTest(SimpleTestCase):
    def test_유효한_입력은_명령으로_변환한다(self) -> None:
        command = parse_place_order(_body('{"product_id": 1, "quantity": 2}'))

        self.assertEqual(command, PlaceOrderCommand(product_id=1, quantity=2))


class ParsePlaceOrderFieldValidationTest(SimpleTestCase):
    def test_quantity_누락이면_ValidationError에_quantity_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": 1}'))

        self.assertIn("quantity", ctx.exception.errors)

    def test_product_id_누락이면_ValidationError에_product_id_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"quantity": 2}'))

        self.assertIn("product_id", ctx.exception.errors)

    def test_quantity_0이면_ValidationError에_quantity_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": 1, "quantity": 0}'))

        self.assertIn("quantity", ctx.exception.errors)

    def test_quantity_음수이면_ValidationError에_quantity_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": 1, "quantity": -3}'))

        self.assertIn("quantity", ctx.exception.errors)

    def test_quantity_비정수이면_ValidationError에_quantity_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": 1, "quantity": "two"}'))

        self.assertIn("quantity", ctx.exception.errors)

    def test_quantity_불리언이면_정수로_보지_않고_거절한다(self) -> None:
        # bool 은 int 의 서브타입이라 isinstance 만으로 통과할 수 있으므로 명시적으로 거른다.
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": 1, "quantity": true}'))

        self.assertIn("quantity", ctx.exception.errors)

    def test_product_id_비정수이면_ValidationError에_product_id_사유가_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body('{"product_id": "x", "quantity": 2}'))

        self.assertIn("product_id", ctx.exception.errors)

    def test_여러_필드가_동시에_틀리면_모두_errors에_담긴다(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            parse_place_order(_body("{}"))

        self.assertIn("product_id", ctx.exception.errors)
        self.assertIn("quantity", ctx.exception.errors)


class ParsePlaceOrderJsonParseTest(SimpleTestCase):
    def test_깨진_JSON이면_JsonParseError를_던진다(self) -> None:
        with self.assertRaises(JsonParseError):
            parse_place_order(_body("{not valid json"))

    def test_JSON_최상위가_객체가_아니면_JsonParseError를_던진다(self) -> None:
        # 배열·스칼라는 필드 맵을 특정할 수 없으므로 파싱 실패 분기로 본다.
        with self.assertRaises(JsonParseError):
            parse_place_order(_body("[1, 2]"))
