ORDERS_URL = "/api/orders/"


def place_order(client, payload):
    return client.post(ORDERS_URL, data=payload, content_type="application/json")


def get_order(client, order_id):
    return client.get(f"{ORDERS_URL}{order_id}/")
