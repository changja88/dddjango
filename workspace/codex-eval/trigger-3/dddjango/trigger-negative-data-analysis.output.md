```python
import pandas as pd

# 예시 데이터
df = pd.DataFrame({
    "user_id": [1, 1, 2, 2, 3],
    "purchase_amount": [10000, 15000, 20000, 30000, 5000],
})

# 사용자별 평균 구매 금액 계산
avg_purchase_by_user = (
    df.groupby("user_id")["purchase_amount"]
      .mean()
      .reset_index(name="avg_purchase_amount")
)

print(avg_purchase_by_user)
```

결과:

```text
   user_id  avg_purchase_amount
0        1              12500.0
1        2              25000.0
2        3               5000.0
```

실제 컬럼명이 다르면 `"user_id"`와 `"purchase_amount"`만 데이터에 맞게 바꾸면 됩니다.