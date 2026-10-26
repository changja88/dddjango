"""vouchers_batch 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VouchersBatch:
    value: str
