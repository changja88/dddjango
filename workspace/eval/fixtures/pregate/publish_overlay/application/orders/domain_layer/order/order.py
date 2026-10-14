from dataclasses import dataclass


@dataclass
class Order:
    order_id: int
    note: str

    def rename(self, note: str) -> None:
        self.note = note
