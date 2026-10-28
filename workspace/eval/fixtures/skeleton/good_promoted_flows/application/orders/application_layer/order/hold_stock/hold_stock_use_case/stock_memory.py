from dataclasses import dataclass


@dataclass
class StockMemory:
    sku_id: int
    held: bool = False
