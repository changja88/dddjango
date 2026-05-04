```python
import pandas as pd

# 예시 데이터
df = pd.DataFrame({
    "user_id": [1, 1, 2, 2, 3],
    "purchase_amount": [10000, 20000, 15000, 25000, 30000]
})

# 사용자별 평균 구매 금액 계산
avg_purchase_by_user = (
    df.groupby("user_id")["purchase_amount"]
      .mean()
      .reset_index(name="avg_purchase_amount")
)

print(avg_purchase_by_user)
```

출력 예시:

```text
   user_id  avg_purchase_amount
0        1              15000.0
1        2              20000.0
2        3              30000.0
```

이미 `df`가 있다면 핵심 코드는 이 부분입니다:

```python
avg_purchase_by_user = df.groupby("user_id")["purchase_amount"].mean()
```