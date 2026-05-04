```python
import pandas as pd

df = pd.DataFrame({
    "user_id": [1, 1, 2, 2, 3],
    "purchase_amount": [10000, 15000, 20000, 30000, 12000],
})

avg_purchase_by_user = (
    df.groupby("user_id")["purchase_amount"]
      .mean()
      .reset_index(name="avg_purchase_amount")
)

print(avg_purchase_by_user)
```

출력 예:

```text
   user_id  avg_purchase_amount
0        1              12500.0
1        2              25000.0
2        3              12000.0
```

실제 데이터프레임에 컬럼명이 다르면 `"user_id"`와 `"purchase_amount"`만 맞게 바꾸면 됩니다.