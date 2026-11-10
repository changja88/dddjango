from __future__ import annotations

from application.orders.application_layer.order.place_order.place_order_use_case.place_order_failure import PlaceOrderFailure
from application.orders.application_layer.order.cancel_order.cancel_order_use_case.cancel_order_failure import _CancelOrderFailure
from application.orders.application_layer.order.refund_order.refund_order_use_case import _RefundOrderFailure
from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
from application.orders.application_layer.order.cancel_order.cancel_order_command import CancelOrderCommand
from application.orders.application_layer.order.refund_order.refund_order_command import RefundOrderCommand
from application.orders.composition_root.dependency_wiring import build_cancel_order_use_case
from application.orders.composition_root.dependency_wiring import build_place_order_use_case
from application.orders.composition_root.dependency_wiring import build_refund_order_use_case
from application.orders.driving_layer.open_host_service.order_desk.contract.exception.order_unavailable_exception import OrderUnavailableException
from application.orders.driving_layer.open_host_service.order_desk.contract.request.cancel_order_request import CancelOrderRequest
from application.orders.driving_layer.open_host_service.order_desk.contract.response.cancel_order_response import CancelOrderResponse
from application.orders.driving_layer.open_host_service.order_desk.contract.request.place_order_request import PlaceOrderRequest
from application.orders.driving_layer.open_host_service.order_desk.contract.response.place_order_response import PlaceOrderResponse
from application.orders.driving_layer.open_host_service.order_desk.contract.request.refund_order_request import RefundOrderRequest
from application.orders.driving_layer.open_host_service.order_desk.contract.response.refund_order_response import RefundOrderResponse


def place_order_command(request: PlaceOrderRequest) -> PlaceOrderResponse:
    try:
        build_place_order_use_case().execute(PlaceOrderCommand(order_id=request.order_id))
    except PlaceOrderFailure as failure:
        if failure.category == "empty":
            raise OrderUnavailableException(category=str(failure)) from failure
        raise OrderUnavailableException(category=failure.category) from None
    return PlaceOrderResponse(order_id=request.order_id)


def cancel_order_command(request: CancelOrderRequest) -> CancelOrderResponse:
    try:
        build_cancel_order_use_case().execute(CancelOrderCommand(order_id=request.order_id))
    except _CancelOrderFailure as failure:
        raise OrderUnavailableException(category=failure.category) from None
    return CancelOrderResponse(order_id=request.order_id)


def refund_order_command(request: RefundOrderRequest) -> RefundOrderResponse:
    try:
        build_refund_order_use_case().execute(RefundOrderCommand(order_id=request.order_id))
    except _RefundOrderFailure as failure:
        raise OrderUnavailableException(category=failure.category) from None
    return RefundOrderResponse(order_id=request.order_id)
