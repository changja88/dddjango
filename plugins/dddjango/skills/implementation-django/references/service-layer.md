# Django와 서비스 레이어 아키텍처

## 서비스 레이어가 필요한 시점 [TSD] [HS] [CP]

Fat Model이 비대해지면 서비스 레이어를 도입한다. 기준점:

- 모델 파일이 500줄을 넘길 때
- 하나의 비즈니스 동작이 여러 모델에 걸칠 때
- 동일한 로직이 여러 뷰에서 중복될 때
- 외부 서비스(이메일, 결제 등) 호출이 모델에 섞일 때

## HackSoft 서비스/셀렉터 패턴 [HS]

```python
# services.py -- 쓰기(Command) 로직
def user_create(*, email: str, password: str) -> User:
    """사용자를 생성하고 환영 이메일을 보낸다."""
    user = User.objects.create_user(email=email, password=password)
    Profile.objects.create(user=user)
    send_welcome_email(user=user)
    return user

def order_confirm(*, order: Order) -> Order:
    """주문을 확정한다."""
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")
    order.status = Order.Status.CONFIRMED
    order.confirmed_at = timezone.now()
    order.save(update_fields=["status", "confirmed_at"])
    notify_warehouse(order=order)
    return order

# selectors.py -- 읽기(Query) 로직
def article_list(*, author: User | None = None, status: str | None = None):
    """필터 조건에 따라 기사 목록을 반환한다."""
    qs = Article.objects.select_related("author")
    if author:
        qs = qs.filter(author=author)
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-published_at")
```

**네이밍 규칙: `<entity>_<action>`** -- `user_create`, `order_confirm`, `article_list`

- 네임스페이싱: `user_` 접두사로 사용자 관련 서비스를 묶는다.
- 검색 용이: `grep "def user_"` 로 모든 사용자 관련 동작을 찾을 수 있다.

## 트랜잭션과 부수 효과 [DDoc] [HS]

```python
from django.db import transaction

def order_create(*, user, items, payment_method):
    """주문을 생성하고 결제를 처리한다."""
    with transaction.atomic():
        order = Order.objects.create(user=user)
        # ... 주문 아이템 생성, 재고 차감 등 DB 작업 ...
        payment = Payment.objects.create(order=order, amount=total)

    # 나쁜 예: 트랜잭션 안에서 이메일 발송
    # -> 트랜잭션이 롤백되어도 이메일은 이미 발송됨
    # send_confirmation_email(order)

    # 좋은 예: transaction.on_commit으로 트랜잭션 커밋 후 실행
    transaction.on_commit(lambda: send_confirmation_email(order))
    return order
```

- 이메일 발송, 외부 API 호출, 알림 전송 등 **되돌릴 수 없는 부수 효과**는 `transaction.on_commit()`으로 감싼다.
- 트랜잭션이 롤백되면 `on_commit` 콜백은 실행되지 않아, 데이터와 부수 효과의 정합성이 보장된다.
- 서비스 함수 내에서 `transaction.atomic()`으로 DB 작업을 묶고, 부수 효과는 블록 밖이나 `on_commit`에 배치한다.

## DDD와 Django의 트레이드오프 [CP]

```python
# Django ORM은 Active Record 패턴 -- 도메인 모델과 영속성 모델이 같은 객체
# DDD의 Repository 패턴을 적용하려면 수동 변환 레이어가 필요

# 방법 A: Django ORM 직접 사용 (대부분의 프로젝트에 적합)
# - Django의 배터리(admin, forms, migrations)를 그대로 활용
# - 도메인 로직은 모델 메서드 + 서비스 레이어에 배치

# 방법 B: Repository 패턴 도입 (복잡한 도메인에 적합)
class ArticleRepository:
    def get_by_id(self, article_id: int) -> Article:
        return Article.objects.get(pk=article_id)

    def save(self, article: Article) -> None:
        article.save()

    def published_by_author(self, author: User) -> QuerySet:
        return Article.objects.filter(
            author=author, status=Article.Status.PUBLISHED
        )
# 장점: 테스트에서 Fake Repository로 교체 가능
# 단점: Django의 풍부한 QuerySet API를 래핑하는 추가 비용
```

**실용적 권고:**
- 대부분의 Django 프로젝트에서는 **모델 메서드 + 서비스 함수**로 충분하다.
- 도메인이 정말 복잡해질 때만 Repository 패턴을 점진적으로 도입한다.
- DDD의 모든 패턴을 Django에 강제하면 Django의 장점(admin, migrations, forms)을 재구현하게 된다. [CP]
- 서비스 레이어는 좋은 출발점 -- 뷰와 모델 사이에 얇은 계층을 두어 비즈니스 로직을 격리한다.
- 복잡한 도메인에서 헥사고날 아키텍처, CQRS, Event Sourcing 등의 패턴이 필요하면 **architecture-implementation-patterns** 스킬을 참조한다.
