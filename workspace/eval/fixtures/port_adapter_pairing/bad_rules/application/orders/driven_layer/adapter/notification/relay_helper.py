from __future__ import annotations

from application.orders.application_layer.port.relay.exception import AliasedRelayError
from application.orders.application_layer.port.relay.exception import RelayDeliveryError as ReboundError

ShadowError = Exception


def relay_a() -> None:
    try:
        _send()  # noqa: F821
    except ShadowError:
        raise


def relay_b() -> None:
    try:
        _send()  # noqa: F821
    except ReboundError:
        raise


def relay_c() -> None:
    try:
        _send()  # noqa: F821
    except (ReboundError, Exception):
        raise


def relay_d() -> None:
    try:
        _send()  # noqa: F821
    except AliasedRelayError:
        raise


ReboundError = Exception
