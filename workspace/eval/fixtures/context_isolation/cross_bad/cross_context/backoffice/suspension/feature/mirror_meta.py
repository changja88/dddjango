from framework.pure.table_view import TableView


class MetaMirror(TableView):
    class Meta:
        db_table = "orders_order"
