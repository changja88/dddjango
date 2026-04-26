# 회의실 예약 시스템 - Django 모델 설계

PostgreSQL Range 타입과 ExclusionConstraint를 활용한 회의실 예약 시스템.

## 사전 요구사항

```bash
pip install django psycopg2-binary
```

PostgreSQL에 `btree_gist` 확장이 필요하다.

---

## 1. 마이그레이션: btree_gist 확장 활성화

ExclusionConstraint에서 정수 등 btree 타입과 GiST 인덱스를 함께 사용하려면 `btree_gist` 확장이 반드시 필요하다.

```python
# reservations/migrations/0001_enable_btree_gist.py

from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        BtreeGistExtension(),
    ]
```

---

## 2. 모델 정의

```python
# reservations/models.py

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateTimeRangeField,
    RangeBoundary,
    RangeOperators,
)
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Room(models.Model):
    """회의실"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("회의실 이름", max_length=100, unique=True)
    floor = models.IntegerField("층수")
    capacity = models.PositiveIntegerField(
        "수용 인원",
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField("활성 여부", default=True)
    description = models.TextField("설명", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room"
        ordering = ["floor", "name"]
        indexes = [
            models.Index(fields=["floor"], name="idx_room_floor"),
            models.Index(fields=["capacity"], name="idx_room_capacity"),
            models.Index(
                fields=["is_active"],
                name="idx_room_active",
                condition=Q(is_active=True),
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.floor}층, {self.capacity}인)"


class Reservation(models.Model):
    """예약"""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "확정"
        CANCELLED = "cancelled", "취소"
        COMPLETED = "completed", "완료"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="회의실",
    )
    time_range = DateTimeRangeField("예약 시간 범위")
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="예약자",
    )
    title = models.CharField("회의 제목", max_length=200)
    status = models.CharField(
        "상태",
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    recurrence = models.ForeignKey(
        "RecurrenceRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
        verbose_name="반복 규칙",
    )
    note = models.TextField("메모", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservation"
        ordering = ["time_range"]
        indexes = [
            # GiST 인덱스: 시간 범위 겹침 검색에 사용
            models.Index(
                fields=["time_range"],
                name="idx_reservation_time_gist",
                opclasses=["range_ops"],
            ),
            models.Index(fields=["room", "status"], name="idx_reservation_room_status"),
            models.Index(fields=["reserved_by"], name="idx_reservation_user"),
            models.Index(fields=["status"], name="idx_reservation_status"),
        ]
        constraints = [
            # 핵심: 같은 회의실에서 시간이 겹치는 활성 예약을 DB 레벨에서 차단
            ExclusionConstraint(
                name="excl_room_time_overlap",
                expressions=[
                    ("room_id", RangeOperators.EQUAL),
                    ("time_range", RangeOperators.OVERLAPS),
                ],
                condition=Q(status="confirmed"),
            ),
            # 예약 시간 유효성: 시작 < 끝
            models.CheckConstraint(
                name="chk_reservation_time_valid",
                check=Q(time_range__fully_lt=models.F("time_range")),
                violation_error_message="예약 시작 시간이 끝 시간보다 앞서야 합니다.",
            ),
        ]

    def __str__(self):
        return f"[{self.room.name}] {self.title} ({self.time_range})"

    def clean(self):
        super().clean()
        if self.time_range:
            lower = self.time_range.lower
            upper = self.time_range.upper
            if lower and upper and lower >= upper:
                raise ValidationError("시작 시간이 끝 시간보다 앞서야 합니다.")

    @property
    def start_time(self):
        return self.time_range.lower if self.time_range else None

    @property
    def end_time(self):
        return self.time_range.upper if self.time_range else None

    @property
    def duration(self):
        if self.time_range and self.time_range.lower and self.time_range.upper:
            return self.time_range.upper - self.time_range.lower
        return None

    def cancel(self):
        """예약 취소. 취소된 예약은 ExclusionConstraint 조건에서 빠진다."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])


class RecurrenceRule(models.Model):
    """반복 예약 규칙"""

    class Frequency(models.TextChoices):
        DAILY = "daily", "매일"
        WEEKLY = "weekly", "매주"
        BIWEEKLY = "biweekly", "격주"
        MONTHLY = "monthly", "매월"

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "월요일"
        TUESDAY = 1, "화요일"
        WEDNESDAY = 2, "수요일"
        THURSDAY = 3, "목요일"
        FRIDAY = 4, "금요일"
        SATURDAY = 5, "토요일"
        SUNDAY = 6, "일요일"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frequency = models.CharField(
        "반복 주기",
        max_length=20,
        choices=Frequency.choices,
    )
    weekdays = models.JSONField(
        "반복 요일",
        default=list,
        blank=True,
        help_text="반복할 요일 목록 (0=월, 1=화, ..., 6=일). 예: [0, 2]는 월,수 반복.",
    )
    interval = models.PositiveIntegerField(
        "반복 간격",
        default=1,
        help_text="frequency 단위 기준 간격. 예: weekly + interval=2 = 격주",
    )
    start_date = models.DateField("반복 시작일")
    end_date = models.DateField("반복 종료일")
    start_time = models.TimeField("시작 시각")
    end_time = models.TimeField("종료 시각")
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="recurrence_rules",
        verbose_name="회의실",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurrence_rules",
        verbose_name="생성자",
    )
    title = models.CharField("회의 제목", max_length=200)
    is_active = models.BooleanField("활성 여부", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recurrence_rule"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_frequency_display()}] {self.title} ({self.start_date}~{self.end_date})"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("반복 시작일이 종료일보다 앞서야 합니다.")
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("시작 시각이 종료 시각보다 앞서야 합니다.")
```

---

## 3. ExclusionConstraint 동작 원리

`excl_room_time_overlap` 제약 조건의 SQL 번역:

```sql
ALTER TABLE reservation
ADD CONSTRAINT excl_room_time_overlap
    EXCLUDE USING gist (
        room_id WITH =,
        time_range WITH &&
    )
    WHERE (status = 'confirmed');
```

동작 방식:

| 조건 | 의미 |
|---|---|
| `room_id WITH =` | 같은 회의실에 대해 |
| `time_range WITH &&` | 시간 범위가 겹치면 |
| `WHERE (status = 'confirmed')` | 확정 상태인 예약만 검사 |

취소된 예약(`status='cancelled'`)은 `WHERE` 절에서 제외되므로 겹침 검사에 포함되지 않는다.

---

## 4. 겹침 확인 쿼리

### 4-1. 특정 시간대에 겹치는 예약 조회

```python
from datetime import datetime
from django.contrib.postgres.fields import DateTimeRangeField
from psycopg2.extras import DateTimeTZRange


def get_overlapping_reservations(room_id, start, end):
    """특정 회의실에서 주어진 시간 범위와 겹치는 활성 예약을 조회한다."""
    requested_range = DateTimeTZRange(start, end)

    return Reservation.objects.filter(
        room_id=room_id,
        status=Reservation.Status.CONFIRMED,
        time_range__overlap=requested_range,
    )
```

### 4-2. 예약 가능 여부 확인

```python
def is_available(room_id, start, end):
    """해당 시간에 예약이 가능한지 확인한다."""
    return not get_overlapping_reservations(room_id, start, end).exists()
```

### 4-3. 특정 날짜의 회의실별 예약 현황

```python
from psycopg2.extras import DateTimeTZRange
from django.utils import timezone
from datetime import datetime, time


def get_daily_schedule(date, room_id=None):
    """특정 날짜의 예약 현황을 조회한다."""
    day_start = timezone.make_aware(datetime.combine(date, time.min))
    day_end = timezone.make_aware(datetime.combine(date, time.max))
    day_range = DateTimeTZRange(day_start, day_end)

    qs = Reservation.objects.filter(
        status=Reservation.Status.CONFIRMED,
        time_range__overlap=day_range,
    ).select_related("room", "reserved_by")

    if room_id:
        qs = qs.filter(room_id=room_id)

    return qs.order_by("room__name", "time_range")
```

### 4-4. 빈 회의실 검색 (특정 시간대에 예약 없는 회의실)

```python
def get_available_rooms(start, end, min_capacity=None):
    """주어진 시간대에 예약 가능한 회의실 목록을 반환한다."""
    requested_range = DateTimeTZRange(start, end)

    occupied_room_ids = Reservation.objects.filter(
        status=Reservation.Status.CONFIRMED,
        time_range__overlap=requested_range,
    ).values_list("room_id", flat=True)

    qs = Room.objects.filter(is_active=True).exclude(id__in=occupied_room_ids)

    if min_capacity:
        qs = qs.filter(capacity__gte=min_capacity)

    return qs.order_by("floor", "name")
```

### 4-5. Raw SQL로 직접 겹침 확인

ORM 없이 직접 SQL로 확인할 때:

```sql
-- 특정 회의실의 특정 시간대 겹침 확인
SELECT id, title, time_range, reserved_by_id
FROM reservation
WHERE room_id = '회의실-UUID'
  AND status = 'confirmed'
  AND time_range && tstzrange('2026-04-04 14:00+09', '2026-04-04 15:00+09');

-- 겹치는 예약이 존재하면 삽입 자체가 실패한다
INSERT INTO reservation (id, room_id, time_range, reserved_by_id, title, status)
VALUES (
    gen_random_uuid(),
    '회의실-UUID',
    tstzrange('2026-04-04 14:00+09', '2026-04-04 15:00+09'),
    '사용자-UUID',
    '팀 미팅',
    'confirmed'
);
-- 겹치면: ERROR: conflicting key value violates exclusion constraint "excl_room_time_overlap"
```

---

## 5. 반복 예약 생성 서비스

```python
# reservations/services.py

from datetime import datetime, timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange

from .models import RecurrenceRule, Reservation, Room


class RecurrenceService:
    """반복 예약 생성 서비스"""

    @staticmethod
    @transaction.atomic
    def create_recurring_reservations(rule: RecurrenceRule) -> list[Reservation]:
        """
        RecurrenceRule에 따라 개별 Reservation 레코드를 일괄 생성한다.
        각 예약은 독립적인 Reservation이며, recurrence FK로 규칙에 연결된다.
        ExclusionConstraint 덕분에 겹치는 예약은 DB가 자동으로 거부한다.
        """
        dates = RecurrenceService._generate_dates(rule)
        reservations = []

        for date in dates:
            start_dt = timezone.make_aware(
                datetime.combine(date, rule.start_time)
            )
            end_dt = timezone.make_aware(
                datetime.combine(date, rule.end_time)
            )

            reservation = Reservation(
                room=rule.room,
                time_range=DateTimeTZRange(start_dt, end_dt),
                reserved_by=rule.created_by,
                title=rule.title,
                status=Reservation.Status.CONFIRMED,
                recurrence=rule,
            )
            reservations.append(reservation)

        # bulk_create에서 ExclusionConstraint 위반 시
        # IntegrityError가 발생한다.
        # ignore_conflicts=True로 충돌 건만 건너뛸 수도 있다.
        created = Reservation.objects.bulk_create(reservations)
        return created

    @staticmethod
    def create_recurring_reservations_skip_conflicts(
        rule: RecurrenceRule,
    ) -> tuple[list[Reservation], list[dict]]:
        """
        충돌이 발생하는 날짜는 건너뛰고 가능한 날짜만 예약한다.
        성공한 예약 목록과 실패 정보를 함께 반환한다.
        """
        dates = RecurrenceService._generate_dates(rule)
        created = []
        skipped = []

        for date in dates:
            start_dt = timezone.make_aware(
                datetime.combine(date, rule.start_time)
            )
            end_dt = timezone.make_aware(
                datetime.combine(date, rule.end_time)
            )
            time_range = DateTimeTZRange(start_dt, end_dt)

            # 겹침 사전 확인
            conflict = Reservation.objects.filter(
                room=rule.room,
                status=Reservation.Status.CONFIRMED,
                time_range__overlap=time_range,
            ).first()

            if conflict:
                skipped.append({
                    "date": date,
                    "conflict_with": str(conflict),
                })
                continue

            reservation = Reservation.objects.create(
                room=rule.room,
                time_range=time_range,
                reserved_by=rule.created_by,
                title=rule.title,
                status=Reservation.Status.CONFIRMED,
                recurrence=rule,
            )
            created.append(reservation)

        return created, skipped

    @staticmethod
    def cancel_recurring_reservations(
        rule: RecurrenceRule,
        from_date: Optional[datetime] = None,
    ) -> int:
        """
        반복 예약을 일괄 취소한다.
        from_date가 주어지면 해당 일시 이후의 예약만 취소한다.
        """
        qs = Reservation.objects.filter(
            recurrence=rule,
            status=Reservation.Status.CONFIRMED,
        )
        if from_date:
            range_after = DateTimeTZRange(from_date, None)
            qs = qs.filter(time_range__overlap=range_after)

        count = qs.update(status=Reservation.Status.CANCELLED)
        return count

    @staticmethod
    def _generate_dates(rule: RecurrenceRule) -> list:
        """반복 규칙에 따라 예약 대상 날짜 목록을 생성한다."""
        dates = []
        current = rule.start_date

        if rule.frequency == RecurrenceRule.Frequency.DAILY:
            while current <= rule.end_date:
                dates.append(current)
                current += timedelta(days=rule.interval)

        elif rule.frequency in (
            RecurrenceRule.Frequency.WEEKLY,
            RecurrenceRule.Frequency.BIWEEKLY,
        ):
            week_interval = rule.interval
            if rule.frequency == RecurrenceRule.Frequency.BIWEEKLY:
                week_interval = 2

            weekdays = rule.weekdays or []
            if not weekdays:
                weekdays = [current.weekday()]

            week_start = current
            while week_start <= rule.end_date:
                for wd in sorted(weekdays):
                    # 해당 주의 wd 요일 날짜 계산
                    days_ahead = wd - week_start.weekday()
                    target = week_start + timedelta(days=days_ahead)
                    if rule.start_date <= target <= rule.end_date:
                        dates.append(target)
                week_start += timedelta(weeks=week_interval)

        elif rule.frequency == RecurrenceRule.Frequency.MONTHLY:
            day_of_month = current.day
            while current <= rule.end_date:
                try:
                    target = current.replace(day=day_of_month)
                    if rule.start_date <= target <= rule.end_date:
                        dates.append(target)
                except ValueError:
                    # 해당 월에 해당 일이 없는 경우 (예: 2월 31일) 건너뜀
                    pass

                # 다음 달로 이동
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    current = current.replace(month=current.month + rule.interval, day=1)

        return sorted(set(dates))
```

---

## 6. 사용 예시

```python
from datetime import date, time, datetime
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange
from reservations.models import Room, Reservation, RecurrenceRule
from reservations.services import RecurrenceService


# --- 회의실 생성 ---
room = Room.objects.create(
    name="대회의실 A",
    floor=3,
    capacity=20,
    description="프로젝터, 화이트보드 구비",
)

# --- 단건 예약 ---
start = timezone.make_aware(datetime(2026, 4, 6, 14, 0))
end = timezone.make_aware(datetime(2026, 4, 6, 15, 0))

reservation = Reservation.objects.create(
    room=room,
    time_range=DateTimeTZRange(start, end),
    reserved_by=user,
    title="프로젝트 킥오프",
)

# --- 같은 시간에 같은 회의실 예약 시도 -> DB 에러 발생 ---
# django.db.utils.IntegrityError:
#   conflicting key value violates exclusion constraint "excl_room_time_overlap"
try:
    Reservation.objects.create(
        room=room,
        time_range=DateTimeTZRange(start, end),
        reserved_by=another_user,
        title="다른 회의",
    )
except IntegrityError:
    print("시간이 겹치는 예약은 불가합니다.")

# --- 예약 취소 후에는 같은 시간 예약 가능 ---
reservation.cancel()  # status -> 'cancelled'

new_reservation = Reservation.objects.create(
    room=room,
    time_range=DateTimeTZRange(start, end),
    reserved_by=another_user,
    title="다른 회의",
)
# 성공: 취소된 예약은 ExclusionConstraint에서 제외됨

# --- 반복 예약: 매주 월요일 10:00-11:00, 4주간 ---
rule = RecurrenceRule.objects.create(
    frequency=RecurrenceRule.Frequency.WEEKLY,
    weekdays=[0],  # 0 = 월요일
    interval=1,
    start_date=date(2026, 4, 6),
    end_date=date(2026, 4, 27),
    start_time=time(10, 0),
    end_time=time(11, 0),
    room=room,
    created_by=user,
    title="주간 스탠드업",
)

created = RecurrenceService.create_recurring_reservations(rule)
print(f"{len(created)}건의 반복 예약 생성 완료")
# 4건의 반복 예약 생성 완료 (4/6, 4/13, 4/20, 4/27)

# --- 충돌 건너뛰기 모드 ---
created, skipped = RecurrenceService.create_recurring_reservations_skip_conflicts(rule)
print(f"성공: {len(created)}건, 충돌로 건너뜀: {len(skipped)}건")

# --- 빈 회의실 검색 ---
available = get_available_rooms(
    start=timezone.make_aware(datetime(2026, 4, 6, 14, 0)),
    end=timezone.make_aware(datetime(2026, 4, 6, 15, 0)),
    min_capacity=10,
)
```

---

## 7. 인덱스 및 제약 조건 요약

| 종류 | 이름 | 대상 | 목적 |
|---|---|---|---|
| **Exclusion** | `excl_room_time_overlap` | `reservation(room_id, time_range)` WHERE `status='confirmed'` | 같은 회의실 시간 겹침 방지 |
| **Check** | `chk_reservation_time_valid` | `reservation.time_range` | 시작 < 끝 보장 |
| **GiST Index** | `idx_reservation_time_gist` | `reservation.time_range` | 범위 겹침 쿼리 성능 |
| **B-tree Index** | `idx_reservation_room_status` | `reservation(room_id, status)` | 회의실별 상태 필터링 |
| **B-tree Index** | `idx_reservation_user` | `reservation.reserved_by` | 사용자별 예약 조회 |
| **B-tree Index** | `idx_reservation_status` | `reservation.status` | 상태별 필터링 |
| **B-tree Index** | `idx_room_floor` | `room.floor` | 층수별 검색 |
| **B-tree Index** | `idx_room_capacity` | `room.capacity` | 수용인원 검색 |
| **Partial Index** | `idx_room_active` | `room.is_active` WHERE `is_active=True` | 활성 회의실만 빠르게 조회 |
| **Unique** | (Django auto) | `room.name` | 회의실 이름 중복 방지 |

---

## 8. 설계 포인트 정리

**DB 레벨 겹침 방지**: ExclusionConstraint + `WHERE status='confirmed'` 조건으로 애플리케이션 레이스 컨디션과 무관하게 겹침을 차단한다. 두 트랜잭션이 동시에 같은 시간대를 예약하더라도 하나는 반드시 `IntegrityError`로 실패한다.

**취소 예약 제외**: `condition=Q(status="confirmed")` 덕분에 취소된 예약은 제약 조건 검사에서 자동 제외된다. 취소 후 같은 시간에 새 예약이 가능하다.

**반복 예약**: 반복 규칙(`RecurrenceRule`)과 개별 예약(`Reservation`)을 분리했다. 각 반복 인스턴스는 독립적인 `Reservation` 레코드이므로 개별 수정/취소가 가능하고, ExclusionConstraint가 각 건에 대해 동일하게 적용된다.

**UUID PK**: 분산 환경에서의 ID 충돌을 방지하고 URL 노출 시 보안성을 높인다.

**Range 타입**: `DateTimeRangeField`를 사용해 시작/끝을 하나의 컬럼으로 관리한다. PostgreSQL의 범위 연산자(`&&`, `@>`, `<@` 등)를 GiST 인덱스와 함께 사용하면 겹침 검색 성능이 뛰어나다.
