from .gift_memory import GiftMemory


class GiftCardPayment:
    def pay(self, memory: GiftMemory) -> None:
        memory.paid = True
