from dataclasses import dataclass


@dataclass
class Product:
    id: int
    available_stock: int
