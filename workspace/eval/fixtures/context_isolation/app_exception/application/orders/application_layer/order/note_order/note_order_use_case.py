from __future__ import annotations

from application.orders.application_layer.order.note_order.note_order_command import NoteOrderCommand
from application.orders.application_layer.order.note_order.note_order_result import NoteOrderResult



class NoteOrderUseCase:
    def execute(self, command: NoteOrderCommand) -> NoteOrderResult:
        if not command.order_id:
            raise ValueError("empty")
        return NoteOrderResult(order_id=command.order_id)
