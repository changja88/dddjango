# benchmark-review-fat-service

Variant: dddjango
Category: review
Title: Review overloaded application service
Fixture: none
Mode: review

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/none
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

아래 서비스가 너무 많은 책임을 갖는지 리뷰해줘.

```python
class CheckoutService:
    def checkout(self, user, items, coupon_code, payment_gateway):
        order = Order.objects.create(user=user)
        total = 0
        for item in items:
            product = Product.objects.get(id=item["product_id"])
            if product.stock < item["quantity"]:
                raise ValueError("out of stock")
            product.stock -= item["quantity"]
            product.save()
            total += product.price * item["quantity"]
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code)
            total -= coupon.discount_amount
        payment_gateway.prepare(total)
        order.total_amount = total
        order.save()
        return order
```
