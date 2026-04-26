# Hotel Aggregate 설계 리뷰

## 1. 핵심 문제: 애그리거트가 너무 크다

현재 `Hotel` 하나의 애그리거트가 Room, Reservation, Review, Amenity를 모두 포함하고 있다. 이는 DDD의 "작은 애그리거트" 원칙에 위배된다.

**구체적 문제점:**

- **트랜잭션 경합**: 예약을 생성할 때와 리뷰를 작성할 때 동일한 Hotel 애그리거트를 잠가야 한다. 리뷰 작성이 예약 생성을 블로킹하거나 그 반대 상황이 발생한다.
- **메모리 비효율**: Hotel을 로드할 때마다 전체 예약 이력, 모든 리뷰, 모든 객실 정보를 함께 로드해야 한다. 예약이 수천 건 쌓이면 성능이 급격히 저하된다.
- **불변식 범위 혼재**: "객실 가용성 확인"과 "리뷰 작성"은 서로 무관한 불변식인데, 하나의 애그리거트에서 보호하고 있다.

## 2. 애그리거트 분리 제안

진짜 하나의 트랜잭션에서 보호해야 하는 불변식 단위로 분리해야 한다.

### 분리 기준: "같은 트랜잭션에서 일관성을 보장해야 하는가?"

| 애그리거트 | 포함 요소 | 보호하는 불변식 |
|---|---|---|
| **Hotel** | id, name, amenities | 호텔 기본 정보의 일관성 |
| **Room** | id, hotel_id, type, price | 객실 정보의 일관성 |
| **Reservation** | id, hotel_id, room_id, guest_id, 기간, status | 동일 객실의 기간 중복 방지 |
| **Review** | id, hotel_id, guest_id, rating, comment | 리뷰 데이터 일관성 |

### 분리 후 설계 예시

```python
class Reservation:
    id: str
    hotel_id: str      # ID로만 참조
    room_id: str       # ID로만 참조
    guest_id: str
    check_in: date
    check_out: date
    status: str

    @staticmethod
    def create(guest_id, hotel_id, room_id, check_in, check_out,
               availability_checker):
        if not availability_checker.is_available(room_id, check_in, check_out):
            raise ValueError("이미 예약된 기간입니다")
        return Reservation(
            guest_id=guest_id, hotel_id=hotel_id, room_id=room_id,
            check_in=check_in, check_out=check_out, status="confirmed"
        )

    def cancel(self):
        if self.status == "cancelled":
            raise ValueError("이미 취소된 예약입니다")
        self.status = "cancelled"


class Review:
    id: str
    hotel_id: str      # ID로만 참조
    guest_id: str
    rating: int
    comment: str
```

## 3. 객체 참조 vs ID 참조

현재 코드에서 `Reservation`이 `Room` 객체를 직접 참조한다:

```python
reservation = Reservation(guest_id=guest_id, room=room, ...)
```

애그리거트 간에는 ID로만 참조해야 한다. 객체 직접 참조는 애그리거트 경계를 무너뜨리고, 한 애그리거트의 변경이 다른 애그리거트에 파급되게 만든다.

## 4. 도메인 이벤트 부재

현재 설계에는 도메인 이벤트가 전혀 없다. 애그리거트를 분리하면 애그리거트 간 결과적 일관성(eventual consistency)을 도메인 이벤트로 처리해야 한다.

```python
class Reservation:
    def cancel(self):
        self.status = "cancelled"
        self._events.append(ReservationCancelled(
            reservation_id=self.id,
            room_id=self.room_id,
            check_in=self.check_in,
            check_out=self.check_out
        ))
```

예를 들어 `ReservationCancelled` 이벤트를 발행하면, 객실 가용성 갱신이나 고객 알림 같은 후속 처리를 느슨하게 연결할 수 있다.

## 5. 가용성 확인 로직의 위치

현재 `Room.is_available()`에 가용성 확인 로직이 있는데, Room이 자신의 예약 현황을 알아야 한다는 뜻이다. 이는 Room과 Reservation이 강하게 결합되는 원인이다.

가용성 확인은 도메인 서비스나 Reservation 리포지토리 쿼리로 분리하는 것이 자연스럽다:

```python
class AvailabilityChecker:
    def __init__(self, reservation_repository):
        self._repo = reservation_repository

    def is_available(self, room_id, check_in, check_out) -> bool:
        overlapping = self._repo.find_overlapping(room_id, check_in, check_out)
        return len(overlapping) == 0
```

## 6. 기타 지적사항

- **Reservation.status가 단순 문자열**: `"cancelled"` 같은 매직 스트링 대신 Enum이나 값 객체를 사용해야 실수를 방지할 수 있다.
- **cancel_reservation에 유효성 검증 없음**: 이미 취소된 예약을 다시 취소하는 것에 대한 방어가 없다.
- **Review에 비즈니스 규칙 부재**: 실제 투숙 여부 확인 없이 누구나 리뷰를 작성할 수 있다.

## 7. 요약

| 항목 | 현재 | 개선 방향 |
|---|---|---|
| 애그리거트 크기 | Hotel이 모든 것을 포함 (God Aggregate) | 불변식 단위로 4개 분리 |
| 객체 참조 | Room 객체 직접 참조 | ID 참조로 변경 |
| 애그리거트 간 통신 | 없음 (단일 애그리거트) | 도메인 이벤트 |
| 가용성 확인 | Room 엔티티 내부 | 도메인 서비스 분리 |
| 상태 표현 | 매직 스트링 | Enum/값 객체 |
