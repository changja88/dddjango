# pilot-review-fat-model

Variant: oracle-reference
Category: review
Title: Review a fat Django model
Fixture: none
Mode: review

## Prompt

아래 Django 모델을 클린 아키텍처 관점에서 리뷰해줘.

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="draft")

    def checkout(self, payment_gateway):
        if self.status != "draft":
            raise ValueError("invalid status")
        for item in self.items.all():
            if item.product.stock < item.quantity:
                raise ValueError("out of stock")
            item.product.stock -= item.quantity
            item.product.save()
        payment_gateway.prepare(self.total_amount)
        self.status = "ready_to_pay"
        self.save()
```
