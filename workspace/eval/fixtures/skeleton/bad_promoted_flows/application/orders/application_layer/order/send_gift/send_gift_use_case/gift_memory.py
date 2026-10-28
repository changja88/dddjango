from dataclasses import dataclass


@dataclass
class GiftMemory:
    gift_id: int
    paid: bool = False
