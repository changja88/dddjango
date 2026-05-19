#!/usr/bin/env python3
"""Evaluator-owned behavior and source-shape checks for code eval cases."""

from __future__ import annotations

import argparse
import ast
import importlib
import sys
from pathlib import Path


def use_workspace_modules(workspace: Path) -> None:
    workspace_text = str(workspace)
    if workspace_text not in sys.path:
        sys.path.insert(0, workspace_text)
    for module_name in list(sys.modules):
        if module_name == "apps" or module_name.startswith("apps."):
            del sys.modules[module_name]
    importlib.invalidate_caches()


def require_order_behavior(workspace: Path) -> None:
    model_path = workspace / "apps/orders/models.py"
    tree = ast.parse(model_path.read_text(encoding="utf-8"))
    order_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Order"
        ),
        None,
    )
    if order_class is None:
        raise AssertionError("Order aggregate root is missing")
    method_names = {
        node.name
        for node in order_class.body
        if isinstance(node, ast.FunctionDef)
    }
    missing = {"place", "confirm"} - method_names
    if missing:
        raise AssertionError(f"Order aggregate behavior missing: {', '.join(sorted(missing))}")


def require_service_does_not_mutate_status_directly(workspace: Path) -> None:
    service_text = (workspace / "apps/orders/services.py").read_text(encoding="utf-8")
    if ".status =" in service_text:
        raise AssertionError("application service must call aggregate behavior instead of assigning status")


def run_ddd_order_placement(workspace: Path) -> None:
    use_workspace_modules(workspace)
    require_order_behavior(workspace)
    require_service_does_not_mutate_status_directly(workspace)

    models = importlib.import_module("apps.orders.models")
    services = importlib.import_module("apps.orders.services")

    order = services.place_order("customer-1", ["sku-1"])
    assert order.status == models.OrderStatus.PENDING_PAYMENT
    confirmed = services.confirm_order(order.id)
    assert confirmed.status == models.OrderStatus.CONFIRMED
    try:
        services.confirm_order(order.id)
    except ValueError:
        pass
    else:
        raise AssertionError("confirmed order must not be confirmed twice")
    try:
        services.place_order("customer-1", [])
    except ValueError:
        pass
    else:
        raise AssertionError("empty order must fail")


def require_reservation_behavior(workspace: Path) -> None:
    model_path = workspace / "apps/reservations/models.py"
    tree = ast.parse(model_path.read_text(encoding="utf-8"))
    reservation_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Reservation"
        ),
        None,
    )
    if reservation_class is None:
        raise AssertionError("Reservation aggregate root is missing")
    method_names = {
        node.name
        for node in reservation_class.body
        if isinstance(node, ast.FunctionDef)
    }
    missing = {"request", "confirm", "expire"} - method_names
    if missing:
        raise AssertionError(
            f"Reservation aggregate behavior missing: {', '.join(sorted(missing))}"
        )


def require_reservation_service_does_not_mutate_status_directly(workspace: Path) -> None:
    service_text = (workspace / "apps/reservations/services.py").read_text(encoding="utf-8")
    if ".status =" in service_text:
        raise AssertionError(
            "application service must call Reservation behavior instead of assigning status"
        )


def require_availability_boundary(workspace: Path) -> None:
    candidate_paths = [
        workspace / "apps/reservations/services.py",
        workspace / "apps/reservations/inventory.py",
        workspace / "apps/reservations/availability.py",
        workspace / "apps/inventory/services.py",
    ]
    boundary_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in candidate_paths
        if path.is_file()
    ).lower()
    if not any(term in boundary_text for term in ("availability", "inventory", "hold")):
        raise AssertionError("room availability hold boundary is missing")


def run_ddd_reservation_boundary(workspace: Path) -> None:
    use_workspace_modules(workspace)
    require_reservation_behavior(workspace)
    require_reservation_service_does_not_mutate_status_directly(workspace)
    require_availability_boundary(workspace)

    models = importlib.import_module("apps.reservations.models")
    services = importlib.import_module("apps.reservations.services")

    reservation = services.request_reservation("customer-1", "room-101", 2)
    assert reservation.status == models.ReservationStatus.REQUESTED
    confirmed = services.confirm_reservation(reservation.id)
    assert confirmed.status == models.ReservationStatus.CONFIRMED
    try:
        services.confirm_reservation(reservation.id)
    except ValueError:
        pass
    else:
        raise AssertionError("confirmed reservation must not be confirmed twice")

    expiring = services.request_reservation("customer-2", "room-102", 1)
    expired = services.expire_reservation(expiring.id)
    assert expired.status == models.ReservationStatus.EXPIRED
    try:
        services.expire_reservation(reservation.id)
    except ValueError:
        pass
    else:
        raise AssertionError("confirmed reservation must not expire")
    try:
        services.request_reservation("customer-3", "room-103", 0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero-night reservation must fail")


def run_web_detail_render_boundary(workspace: Path) -> None:
    use_workspace_modules(workspace)
    template_path = workspace / "apps/orders/templates/orders/detail.html"
    view_path = workspace / "apps/orders/views.py"
    css_path = workspace / "apps/orders/static/orders/detail.css"
    template_text = template_path.read_text(encoding="utf-8", errors="replace")
    view_text = view_path.read_text(encoding="utf-8", errors="replace")

    forbidden_template_access = (
        "order.status",
        "order.memo",
        "order.confirm",
        "order.cancel",
    )
    for token in forbidden_template_access:
        if token in template_text:
            raise AssertionError(f"template must render display values instead of {token}")

    models = importlib.import_module("apps.orders.models")
    views = importlib.import_module("apps.orders.views")
    order = models.Order(customer_id="customer-1", items=["sku-1"], memo="")
    context = views.order_detail_context(order)
    memo_values = [
        value
        for key, value in context.items()
        if "memo" in str(key).lower()
    ]
    if not memo_values:
        raise AssertionError("order_detail_context must expose a display memo value")
    if not any(str(value).strip() for value in memo_values):
        raise AssertionError("empty memo must have a display fallback")

    if "status_label" not in context and not any("status" in str(key).lower() for key in context):
        raise AssertionError("order_detail_context must expose display status")
    if ".confirm(" in view_text or ".cancel(" in view_text or ".status =" in view_text:
        raise AssertionError("view/context must not perform domain state transitions")
    if css_path.is_file() and "detail.css" not in template_text:
        raise AssertionError("detail.css exists but is not referenced by detail template")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    if args.case == "case-code-ddd-order-placement":
        run_ddd_order_placement(args.workspace.resolve())
    elif args.case == "case-code-ddd-reservation-boundary":
        run_ddd_reservation_boundary(args.workspace.resolve())
    elif args.case == "case-code-web-detail":
        run_web_detail_render_boundary(args.workspace.resolve())
    else:
        raise SystemExit(f"unknown behavior check case: {args.case}")
    print(f"behavior checks passed: {args.case}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
