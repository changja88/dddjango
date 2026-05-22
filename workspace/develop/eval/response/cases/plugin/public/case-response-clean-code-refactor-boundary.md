아래 checkout helper를 바로 고치기 전에 dddjango 관점으로 리뷰해줘. 파일 수정은 하지 말고 findings를 심각도 순서로 쓰고, 어떤 refactor가 최소한으로 필요한지 제안해줘.

```python
def process(data, user, send_email=False, dry=False):
    total = 0
    for item in data["items"]:
        if item["qty"] <= 0:
            raise Exception("bad")
        total += item["price"] * item["qty"]
    if data.get("coupon"):
        if data["coupon"]["type"] == "percent":
            total = total - (total * data["coupon"]["value"] / 100)
        if data["coupon"]["type"] == "fixed":
            total = total - data["coupon"]["value"]
    order = Order()
    order.user = user
    order.total = total
    order.status = "paid"
    if not dry:
        order.save()
    if send_email:
        mailer.send(user.email, "paid")
    return {"id": order.id, "total": total, "status": order.status}
```

추가 맥락:
- 비슷한 할인 계산이 serializer에도 중복되어 있어.
- Django Ninja Schema validator가 DB 조회와 주문 상태 변경까지 하고 있어.
- 당장 repository/UoW나 큰 아키텍처 전환이 필요한지는 불확실해.
- 테스트가 거의 없어서 동작 보존 근거도 함께 제안해줘.
