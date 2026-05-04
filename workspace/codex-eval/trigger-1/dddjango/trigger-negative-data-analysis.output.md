## [주요 내용]

```python
import pandas as pd


class PurchaseAggregationError(Exception):
    """구매 집계에 필요한 입력 데이터가 올바르지 않을 때 발생한다."""


def calculate_average_purchase_amount_by_user(
    purchases: pd.DataFrame,
    *,
    user_column: str = "user_id",
    amount_column: str = "purchase_amount",
) -> pd.DataFrame:
    """사용자별 평균 구매 금액을 계산한다."""
    required_columns = {user_column, amount_column}
    missing_columns = required_columns - set(purchases.columns)

    if missing_columns:
        missing_names = ", ".join(sorted(missing_columns))
        raise PurchaseAggregationError(f"필수 컬럼이 없습니다: {missing_names}")

    return (
        purchases.groupby(user_column, as_index=False)[amount_column]
        .mean()
        .rename(columns={amount_column: "average_purchase_amount"})
    )


purchases = pd.DataFrame(
    {
        "user_id": [1, 1, 2, 2, 2, 3],
        "purchase_amount": [10_000, 20_000, 5_000, 15_000, 25_000, 30_000],
    }
)

average_purchases = calculate_average_purchase_amount_by_user(purchases)
print(average_purchases)
```

출력 예시는 다음과 같습니다.

```text
   user_id  average_purchase_amount
0        1                  15000.0
1        2                  15000.0
2        3                  30000.0
```

PEP 695 제네릭은 여기서 사용하지 않았습니다. 이 함수는 제네릭 자료구조를 정의하지 않고 `pd.DataFrame`을 받아 `pd.DataFrame`을 반환하는 단순 집계 함수라 적용 대상이 아닙니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - pandas 기반 데이터 처리 함수 작성 → **implementation-python** 스킬