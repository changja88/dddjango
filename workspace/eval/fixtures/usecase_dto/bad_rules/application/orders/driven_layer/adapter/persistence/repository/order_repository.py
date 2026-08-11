class OrderRepository:
    def save(self, order) -> None:
        events = order.pull_events()
        self._stash(events)
