# 회의실 예약 시스템 -- Django 모델 설계

## 사전 준비: btree_gist 확장 마이그레이션

`ExclusionConstraint`에서 Range 필드 외의 필드(FK 등)를 등가 비교하려면 `btree_gist` 확장이 필요하다.

```python
# bookings/migrations/0001_initial.py (dependencies에 포함)
from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):
    operations = [
        BtreeGistExtension(),
    ]
```

## 모델 정의

```python
# bookings/models.py
from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Now
from psycopg.types.range import Range

if TYPE_CHECKING:
    from datetime import datetime


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    floor = models.PositiveSmallIntegerField()
    capacity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["floor", "name"]
        constraints = [
            models.CheckConstraint(
                check=Q(capacity__gte=1),
                name="room_capacity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.floor}F, {self.capacity}명)"


class ReservationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Reservation.Status.CONFIRMED)

    def cancelled(self):
        return self.filter(status=Reservation.Status.CANCELLED)

    def for_room(self, room: Room):
        return self.filter(room=room)

    def overlapping(self, room: Room, time_range: Range) -> ReservationQuerySet:
        """주어진 회의실과 시간 범위에 겹치는 활성 예약을 반환한다."""
        return self.active().filter(
            room=room,
            time_slot__overlap=time_range,
        )

    def upcoming(self):
        return self.active().filter(time_slot__startswith__gte=Now())


class Reservation(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    # -- DB fields --
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    time_slot = DateTimeRangeField()
    title = models.CharField(max_length=200)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.CONFIRMED,
    )
    recurrence_group = models.ForeignKey(
        "RecurrenceGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
    )
    created_at = models.DateTimeField(db_default=Now())

    # -- Manager --
    objects = ReservationQuerySet.as_manager()

    class Meta:
        indexes = [
            GistIndex(
                fields=["time_slot"],
                name="idx_reservation_timeslot_gist",
            ),
            models.Index(
                fields=["room", "status"],
                name="idx_reservation_room_status",
            ),
            models.Index(
                fields=["reserved_by"],
                name="idx_reservation_user",
            ),
            models.Index(
                fields=["recurrence_group"],
                name="idx_reservation_recurrence",
            ),
        ]
        constraints = [
            # 같은 회의실에 시간이 겹치는 활성 예약 방지 (DB 레벨)
            ExclusionConstraint(
                name="no_overlapping_reservations",
                expressions=[
                    ("room", RangeOperators.EQUAL),
                    ("time_slot", RangeOperators.OVERLAPS),
                ],
                condition=Q(status="confirmed"),
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.room.name}] {self.title}"

    def clean(self) -> None:
        if self.time_slot:
            lower = self.time_slot.lower
            upper = self.time_slot.upper
            if lower and upper and lower >= upper:
                raise ValidationError(
                    {"time_slot": "종료 시간은 시작 시간 이후여야 합니다."}
                )

    def cancel(self) -> None:
        """예약을 취소한다. 취소된 예약은 겹침 검사에서 제외된다."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])


class RecurrenceGroup(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    # -- DB fields --
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="recurrence_groups",
    )
    title = models.CharField(max_length=200)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurrence_groups",
    )
    day_of_week = models.IntegerField(choices=Weekday)
    start_time = models.TimeField()
    end_time = models.TimeField()
    recur_start = models.DateField(help_text="반복 시작 날짜")
    recur_end = models.DateField(help_text="반복 종료 날짜")
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(recur_end__gte=models.F("recur_start")),
                name="recurrence_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"[{self.room.name}] {self.title} "
            f"(매주 {self.get_day_of_week_display()})"
        )

    def clean(self) -> None:
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {"end_time": "종료 시간은 시작 시간 이후여야 합니다."}
            )
        if self.recur_start and self.recur_end and self.recur_start > self.recur_end:
            raise ValidationError(
                {"recur_end": "반복 종료일은 시작일 이후여야 합니다."}
            )
```

## 반복 예약 생성 서비스

반복 예약은 개별 `Reservation` 레코드를 일괄 생성하는 방식으로 처리한다. 이렇게 하면 `ExclusionConstraint`가 각 개별 예약에 동일하게 적용되어 겹침 방지가 일관되게 동작한다.

```python
# bookings/services.py
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from django.db import IntegrityError, transaction
from psycopg.types.range import Range

from .models import RecurrenceGroup, Reservation, Room


def recurrence_create(
    *,
    room: Room,
    title: str,
    reserved_by,
    day_of_week: int,
    start_time: time,
    end_time: time,
    recur_start: date,
    recur_end: date,
) -> tuple[RecurrenceGroup, list[Reservation]]:
    """반복 예약 그룹과 개별 예약을 일괄 생성한다.

    ExclusionConstraint에 의해 겹치는 시간이 있으면
    IntegrityError가 발생한다.
    """
    with transaction.atomic():
        group = RecurrenceGroup.objects.create(
            room=room,
            title=title,
            reserved_by=reserved_by,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            recur_start=recur_start,
            recur_end=recur_end,
        )

        reservations = []
        current = recur_start
        # day_of_week에 맞는 첫 날짜로 이동
        while current.weekday() != day_of_week:
            current += timedelta(days=1)

        while current <= recur_end:
            time_range = Range(
                datetime.combine(current, start_time),
                datetime.combine(current, end_time),
            )
            reservations.append(
                Reservation(
                    room=room,
                    time_slot=time_range,
                    title=title,
                    reserved_by=reserved_by,
                    status=Reservation.Status.CONFIRMED,
                    recurrence_group=group,
                )
            )
            current += timedelta(weeks=1)

        Reservation.objects.bulk_create(reservations)

    return group, reservations


def recurrence_cancel(group: RecurrenceGroup) -> int:
    """반복 예약 그룹의 미래 예약을 모두 취소한다."""
    return (
        Reservation.objects
        .filter(recurrence_group=group)
        .active()
        .upcoming()
        .update(status=Reservation.Status.CANCELLED)
    )
```

## 겹침 확인 쿼리

```python
# bookings/queries.py
from __future__ import annotations

from datetime import datetime

from django.db.models import Q
from psycopg.types.range import Range

from .models import Reservation, Room


def get_overlapping_reservations(
    room: Room,
    start: datetime,
    end: datetime,
    *,
    exclude_pk: int | None = None,
) -> list[Reservation]:
    """특정 회의실에서 주어진 시간 범위와 겹치는 활성 예약을 조회한다."""
    time_range = Range(start, end)
    qs = Reservation.objects.overlapping(room, time_range).select_related(
        "room", "reserved_by",
    )
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    return list(qs)


def is_room_available(
    room: Room,
    start: datetime,
    end: datetime,
) -> bool:
    """특정 회의실이 해당 시간에 사용 가능한지 확인한다."""
    time_range = Range(start, end)
    return not Reservation.objects.overlapping(room, time_range).exists()


def get_available_rooms(
    start: datetime,
    end: datetime,
    *,
    min_capacity: int = 1,
    floor: int | None = None,
) -> list[Room]:
    """주어진 시간에 예약 가능한 회의실 목록을 반환한다."""
    time_range = Range(start, end)

    occupied_room_ids = (
        Reservation.objects
        .active()
        .filter(time_slot__overlap=time_range)
        .values_list("room_id", flat=True)
    )

    qs = Room.objects.filter(capacity__gte=min_capacity).exclude(
        pk__in=occupied_room_ids,
    )
    if floor is not None:
        qs = qs.filter(floor=floor)
    return list(qs)
```

## 사용 예시

```python
from datetime import datetime, time, date
from psycopg.types.range import Range
from bookings.models import Room, Reservation
from bookings.services import recurrence_create, recurrence_cancel
from bookings.queries import is_room_available, get_available_rooms

# 회의실 생성
room_a = Room.objects.create(name="Alpha", floor=3, capacity=10)
room_b = Room.objects.create(name="Beta", floor=5, capacity=20)

# 단건 예약
Reservation.objects.create(
    room=room_a,
    time_slot=Range(datetime(2026, 4, 7, 9, 0), datetime(2026, 4, 7, 10, 0)),
    title="스프린트 플래닝",
    reserved_by=user,
)

# 겹치는 예약 시도 -> IntegrityError 발생
from django.db import IntegrityError

try:
    Reservation.objects.create(
        room=room_a,
        time_slot=Range(datetime(2026, 4, 7, 9, 30), datetime(2026, 4, 7, 11, 0)),
        title="디자인 리뷰",
        reserved_by=user,
    )
except IntegrityError:
    print("해당 시간에 이미 예약이 있습니다.")

# 다른 회의실은 같은 시간에 예약 가능
Reservation.objects.create(
    room=room_b,
    time_slot=Range(datetime(2026, 4, 7, 9, 30), datetime(2026, 4, 7, 11, 0)),
    title="디자인 리뷰",
    reserved_by=user,
)

# 예약 취소 -> 해당 시간 다시 예약 가능
reservation = Reservation.objects.get(title="스프린트 플래닝")
reservation.cancel()

# 반복 예약 (매주 월요일 14:00~15:00, 4주간)
group, reservations = recurrence_create(
    room=room_a,
    title="위클리 스탠드업",
    reserved_by=user,
    day_of_week=0,  # Monday
    start_time=time(14, 0),
    end_time=time(15, 0),
    recur_start=date(2026, 4, 6),
    recur_end=date(2026, 4, 27),
)

# 빈 회의실 조회
available = get_available_rooms(
    start=datetime(2026, 4, 7, 14, 0),
    end=datetime(2026, 4, 7, 15, 0),
    min_capacity=5,
)

# 반복 예약 전체 취소
cancelled_count = recurrence_cancel(group)
```

## 설계 요약

| 구성 요소 | 설명 |
|-----------|------|
| **Room** | 회의실 기본 정보 (이름, 층수, 수용인원). `CheckConstraint`로 수용인원 양수 보장. |
| **Reservation** | 개별 예약. `DateTimeRangeField`로 시작~끝 시간을 단일 필드로 표현. `TextChoices`로 상태 관리. |
| **RecurrenceGroup** | 반복 예약의 메타 정보 (요일, 시간, 반복 기간). 개별 `Reservation`과 FK로 연결. |
| **ExclusionConstraint** | `room` 동일 + `time_slot` 겹침 조건으로 DB 레벨에서 중복 예약 방지. `condition=Q(status="confirmed")`로 취소된 예약 제외. |
| **GistIndex** | `time_slot`에 GiST 인덱스를 걸어 Range 조회 및 ExclusionConstraint 성능 확보. |
| **ReservationQuerySet** | `active()`, `overlapping()`, `upcoming()` 등 체이닝 가능한 커스텀 쿼리셋 메서드. |
| **서비스 레이어** | `recurrence_create`로 반복 예약 일괄 생성 (`bulk_create`), `recurrence_cancel`로 미래 예약 일괄 취소 (`update`). `transaction.atomic()`으로 원자성 보장. |
| **btree_gist** | `ExclusionConstraint`에서 FK(`room`) 등가 비교를 위해 필수. 마이그레이션에서 `BtreeGistExtension()` 설치. |
