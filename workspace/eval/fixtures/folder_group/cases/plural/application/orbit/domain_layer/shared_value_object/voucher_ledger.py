"""voucher_ledger 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoucherLedger:
    value: str
