import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from .models import Shipment


@pytest.fixture
def shipment(db, order):
    return Shipment.objects.create(
        order=order,
        recipient_name="홍길동",
        recipient_address="서울시 강남구 테헤란로 123",
        recipient_phone="010-1234-5678",
        shipping_cost=Decimal("3000"),
        carrier=Shipment.Carrier.CJ,
        estimated_arrival_date=datetime.date(2026, 4, 7),
    )


class TestShipmentModel:

    def test_default_status_is_received(self, shipment):
        assert shipment.status == Shipment.Status.RECEIVED

    def test_str_representation(self, shipment):
        result = str(shipment)
        assert "홍길동" in result
        assert "접수" in result


class TestPickUp:

    def test_pick_up_from_received(self, shipment):
        shipment.pick_up(tracking_number="1234567890")

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.PICKED_UP
        assert shipment.tracking_number == "1234567890"

    def test_pick_up_requires_tracking_number(self, shipment):
        with pytest.raises(ValidationError, match="운송장 번호"):
            shipment.pick_up(tracking_number="")

    def test_pick_up_from_invalid_status(self, shipment):
        shipment.status = Shipment.Status.DELIVERED
        shipment.save()

        with pytest.raises(ValidationError, match="전이할 수 없습니다"):
            shipment.pick_up(tracking_number="1234567890")


class TestInTransit:

    def test_in_transit_from_picked_up(self, shipment):
        shipment.pick_up(tracking_number="1234567890")
        shipment.in_transit()

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.IN_TRANSIT

    def test_in_transit_from_received_is_invalid(self, shipment):
        with pytest.raises(ValidationError, match="전이할 수 없습니다"):
            shipment.in_transit()


class TestDeliver:

    def test_deliver_from_in_transit(self, shipment):
        shipment.pick_up(tracking_number="1234567890")
        shipment.in_transit()
        arrival = datetime.date(2026, 4, 6)
        shipment.deliver(actual_arrival_date=arrival)

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.DELIVERED
        assert shipment.actual_arrival_date == arrival

    def test_deliver_from_received_is_invalid(self, shipment):
        with pytest.raises(ValidationError, match="전이할 수 없습니다"):
            shipment.deliver(actual_arrival_date=datetime.date(2026, 4, 6))


class TestReturnBack:

    def test_return_from_received(self, shipment):
        shipment.return_back()

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.RETURNED

    def test_return_from_picked_up(self, shipment):
        shipment.pick_up(tracking_number="1234567890")
        shipment.return_back()

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.RETURNED

    def test_return_from_in_transit(self, shipment):
        shipment.pick_up(tracking_number="1234567890")
        shipment.in_transit()
        shipment.return_back()

        shipment.refresh_from_db()
        assert shipment.status == Shipment.Status.RETURNED

    def test_return_from_delivered_is_invalid(self, shipment):
        shipment.pick_up(tracking_number="1234567890")
        shipment.in_transit()
        shipment.deliver(actual_arrival_date=datetime.date(2026, 4, 6))

        with pytest.raises(ValidationError, match="전이할 수 없습니다"):
            shipment.return_back()

    def test_return_from_returned_is_invalid(self, shipment):
        shipment.return_back()

        with pytest.raises(ValidationError, match="전이할 수 없습니다"):
            shipment.return_back()


class TestCleanValidation:

    def test_tracking_number_required_after_pickup(self, shipment):
        shipment.status = Shipment.Status.PICKED_UP
        shipment.tracking_number = ""

        with pytest.raises(ValidationError, match="운송장 번호"):
            shipment.clean()

    def test_tracking_number_not_required_for_received(self, shipment):
        shipment.status = Shipment.Status.RECEIVED
        shipment.tracking_number = ""
        shipment.clean()  # should not raise
