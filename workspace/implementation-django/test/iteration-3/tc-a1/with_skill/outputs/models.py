from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Now


class Shipment(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "접수"
        PICKED_UP = "picked_up", "집하"
        IN_TRANSIT = "in_transit", "배송중"
        DELIVERED = "delivered", "배달완료"
        RETURNED = "returned", "반송"

    class Carrier(models.TextChoices):
        CJ = "cj", "CJ대한통운"
        HANJIN = "hanjin", "한진택배"
        LOTTE = "lotte", "롯데택배"
        EPOST = "epost", "우체국택배"

    VALID_TRANSITIONS = {
        Status.RECEIVED: {Status.PICKED_UP, Status.RETURNED},
        Status.PICKED_UP: {Status.IN_TRANSIT, Status.RETURNED},
        Status.IN_TRANSIT: {Status.DELIVERED, Status.RETURNED},
        Status.DELIVERED: set(),
        Status.RETURNED: set(),
    }

    # --- DB fields ---
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="shipments",
    )
    recipient_name = models.CharField("수령인 이름", max_length=50)
    recipient_address = models.TextField("수령인 주소")
    recipient_phone = models.CharField("수령인 연락처", max_length=20)
    status = models.CharField(
        "배송 상태",
        max_length=20,
        choices=Status,
        default=Status.RECEIVED,
    )
    shipping_cost = models.DecimalField(
        "배송비",
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    tracking_number = models.CharField(
        "운송장 번호",
        max_length=50,
        blank=True,
        default="",
    )
    carrier = models.CharField(
        "배송 업체",
        max_length=10,
        choices=Carrier,
    )
    estimated_arrival = models.DateField("예상 도착일")
    actual_arrival = models.DateField("실제 도착일", null=True, blank=True)
    created_at = models.DateTimeField("생성일", db_default=Now())
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "배송"
        verbose_name_plural = "배송 목록"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(shipping_cost__gte=0),
                name="shipment_shipping_cost_non_negative",
            ),
            models.CheckConstraint(
                check=~models.Q(
                    status__in=["picked_up", "in_transit", "delivered"],
                    tracking_number="",
                ),
                name="shipment_tracking_required_after_pickup",
            ),
        ]

    def __str__(self):
        return f"Shipment #{self.pk} ({self.get_status_display()}) - {self.recipient_name}"

    def clean(self):
        self._validate_tracking_number()

    def _validate_tracking_number(self):
        requires_tracking = {
            self.Status.PICKED_UP,
            self.Status.IN_TRANSIT,
            self.Status.DELIVERED,
        }
        if self.status in requires_tracking and not self.tracking_number:
            raise ValidationError(
                {"tracking_number": "집하 이후에는 운송장 번호가 필수입니다."}
            )

    def _transition_to(self, new_status, **update_fields):
        allowed = self.VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationError(
                f"'{self.get_status_display()}'에서 "
                f"'{self.Status(new_status).label}'(으)로 전이할 수 없습니다."
            )
        self.status = new_status
        for field, value in update_fields.items():
            setattr(self, field, value)
        self.full_clean()
        fields_to_update = ["status", "updated_at", *update_fields.keys()]
        self.save(update_fields=fields_to_update)

    def pick_up(self, tracking_number):
        """접수 -> 집하 전이. 운송장 번호 필수."""
        self._transition_to(
            self.Status.PICKED_UP,
            tracking_number=tracking_number,
        )

    def in_transit(self):
        """집하 -> 배송중 전이."""
        self._transition_to(self.Status.IN_TRANSIT)

    def deliver(self, actual_arrival=None):
        """배송중 -> 배달완료 전이."""
        from django.utils import timezone

        arrival = actual_arrival or timezone.now().date()
        self._transition_to(
            self.Status.DELIVERED,
            actual_arrival=arrival,
        )

    def return_back(self):
        """어느 단계에서든 반송 전이. 배달완료/반송 상태에서는 불가."""
        self._transition_to(self.Status.RETURNED)
