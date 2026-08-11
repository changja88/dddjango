from typing import Iterator


class ShipOrderUseCase:
    def execute(self, command) -> Iterator[dict]:
        events = self.order.pull_events()
        self.uow.after_commit(self.broker.publish, events)
        self.broker.publish(events)
        if not command:
            raise ValueError("bad")
        yield {}
