from ninja import Schema


class ReserveStockOut(Schema):
    product_id: int
    stock: int

