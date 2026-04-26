# Django 5.x 새 기능

## Django 5.0 주요 기능 [DDoc]

### db_default -- 데이터베이스 기본값

```python
from django.db.models.functions import Now, Pi

class Event(models.Model):
    # Python 기본값이 아닌 DB 기본값 사용
    created_at = models.DateTimeField(db_default=Now())
    pi_value = models.FloatField(db_default=Pi())
```

- `default`는 Python에서 계산, `db_default`는 DB에서 계산된다.
- `DEFAULT` 절이 SQL에 직접 포함되어, `bulk_create` 등에서도 올바르게 동작한다.

### GeneratedField -- DB 생성 필드

```python
class Rectangle(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()
    area = models.GeneratedField(
        expression=F("width") * F("height"),
        output_field=models.IntegerField(),
        db_persist=True,  # True: stored, False: virtual
    )
```

- `db_persist=True`: 저장 시 계산하여 디스크에 저장 (인덱싱 가능).
- `db_persist=False`: 읽기 시마다 계산 (저장 공간 절약).

### 딕셔너리 기반 Choices

```python
# Django 5.0+ 간결한 구문
class Shirt(models.Model):
    size = models.CharField(
        max_length=2,
        choices={"S": "Small", "M": "Medium", "L": "Large"},
    )
```

## Django 5.1 주요 기능 [DDoc]

```python
# LoginRequiredMiddleware -- 전체 사이트에 로그인 요구
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
]

# 개별 뷰에서 제외
from django.contrib.auth.decorators import login_not_required

@login_not_required
def public_page(request):
    ...
```

## Django 5.2 주요 기능 (LTS) [DDoc]

### Composite Primary Key -- 복합 기본키

```python
from django.db.models import CompositePrimaryKey

class OrderItem(models.Model):
    pk = CompositePrimaryKey("order_id", "product_id")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
```

- `pk` 속성은 구성 필드 값의 **튜플**이다.
- **제약사항**: 기존 모델에서 복합 PK로 마이그레이션 불가, ForeignKey가 복합 PK 모델을 가리킬 수 없음, admin 미지원.

### 자동 모델 임포트 in shell

```bash
# Django 5.2+: shell 실행 시 모든 앱의 모델이 자동 임포트됨
python manage.py shell
>>> Article.objects.count()  # 별도 import 불필요
```

### 모델 제약 유효성 검증 개선

```python
# Django 5.2: GeneratedField를 사용하는 CheckConstraint 검증 지원
# GeneratedField가 자동으로 DB에서 리프레시 (SQLite, PostgreSQL, Oracle)
```

### 참고

- Django 5.2는 **LTS** (Long-Term Support)로, 2028년 4월까지 보안 업데이트를 받는다.
- Python 3.10 ~ 3.13을 지원한다 (3.14는 5.2.8+부터 추가).
