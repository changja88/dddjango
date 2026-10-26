"""voucher_code 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VoucherCode:
    value: str
