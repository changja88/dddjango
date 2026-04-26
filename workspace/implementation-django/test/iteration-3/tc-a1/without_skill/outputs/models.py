from django.db import models
from django.core.exceptions import ValidationError


class Shipment(models.Model):

    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "접수"
        PICKED_UP = "PICKED_UP", "집하"
        IN_TRANSIT = "IN_TRANSIT", "배송중"
        DELIVERED = "DELIVERED", "배달완료"
        RETURNED = "RETURNED", "반송"

    class Carrier(models.TextChoices):
        CJ = "CJ", "CJ대한통운"
        HANJIN = "HANJIN", "한진택배"
        LOTTE = "LOTTE", "롯데택배"
        POST = "POST", "우체국택배"

    VALID_TRANSITIONS = {
        Status.RECEIVED: {Status.PICKED_UP, Status.RETURNED},
        Status.PICKED_UP: {Status.IN_TRANSIT, Status.RETURNED},
        Status.IN_TRANSIT: {Status.DELIVERED, Status.RETURNED},
        Status.DELIVERED: set(),
        Status.RETURNED: set(),
    }

    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="shipments",
    )

    recipient_name = models.CharField("수령인 이름", max_length=100)
    recipient_address = models.TextField("수령인 주소")
    recipient_phone = models.CharField("수령인 연락처", max_length=20)

    status = models.CharField(
        "배송 상태",
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )

    shipping_cost = models.DecimalField(
        "배송비", max_digits=10, decimal_places=0
    )

    tracking_number = models.CharField(
        "운송장 번호", max_length=50, blank=True, default=""
    )

    carrier = models.CharField(
        "배송 업체", max_length=10, choices=Carrier.choices
    )

    estimated_arrival_date = models.DateField("예상 도착일")
    actual_arrival_date = models.DateField(
        "실제 도착일", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "배송"
        verbose_name_plural = "배송 목록"

    def __str__(self):
        return (
            f"Shipment({self.id}) - {self.recipient_name} "
            f"[{self.get_status_display()}]"
        )

    def clean(self):
        super().clean()
        if (
            self.status != self.Status.RECEIVED
            and self.status != self.Status.RETURNED
            and not self.tracking_number
        ):
            raise ValidationError(
                {"tracking_number": "집하 이후에는 운송장 번호가 필수입니다."}
            )

    def _change_status(self, new_status):
        allowed = self.VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationError(
                f"'{self.get_status_display()}'에서 "
                f"'{dict(self.Status.choices)[new_status]}'(으)로 "
                f"전이할 수 없습니다."
            )
        self.status = new_status

    def pick_up(self, tracking_number):
        if not tracking_number:
            raise ValidationError("집하 시 운송장 번호는 필수입니다.")
        self._change_status(self.Status.PICKED_UP)
        self.tracking_number = tracking_number
        self.save()

    def in_transit(self):
        self._change_status(self.Status.IN_TRANSIT)
        self.save()

    def deliver(self, actual_arrival_date):
        self._change_status(self.Status.DELIVERED)
        self.actual_arrival_date = actual_arrival_date
        self.save()

    def return_back(self):
        self._change_status(self.Status.RETURNED)
        self.save()
