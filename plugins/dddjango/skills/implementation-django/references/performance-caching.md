# 성능 최적화와 캐싱

## N+1 문제 탐지와 해결 [DDoc]

```python
# 탐지 도구
# 1. django-debug-toolbar -- 개발 환경에서 쿼리 수 실시간 확인
# 2. django-silk -- 프로파일링 미들웨어
# 3. nplusone -- N+1 쿼리 자동 탐지 및 경고
# 4. assertNumQueries -- 테스트에서 쿼리 수 검증

from django.test import TestCase

class ArticleTestCase(TestCase):
    def test_article_list_query_count(self):
        """목록 조회가 일정 쿼리 수 이내인지 검증."""
        self._create_test_articles(count=50)
        with self.assertNumQueries(2):  # articles + authors
            list(Article.objects.select_related("author").all())
```

## 데이터베이스 인덱스 전략 [DDoc]

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)       # unique=True가 인덱스 생성
    status = models.CharField(max_length=20, db_index=True)  # 단일 인덱스
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # FK에 자동 인덱스
    published_at = models.DateTimeField(null=True)
    category = models.CharField(max_length=50)

    class Meta:
        indexes = [
            # 복합 인덱스: status + published_at 함께 필터하는 쿼리에 효과적
            models.Index(fields=["status", "-published_at"], name="idx_status_pub"),
            # 부분 인덱스: 발행된 글만 인덱싱 (PostgreSQL)
            models.Index(
                fields=["published_at"],
                name="idx_published_only",
                condition=models.Q(status="published"),
            ),
        ]
```

**인덱스 추가 기준:**
- `filter()`, `exclude()`, `order_by()`에 자주 사용되는 필드.
- 그러나 쓰기 성능 저하가 있으므로, 프로파일링 후 추가한다.
- Django Debug Toolbar로 느린 쿼리를 식별하고, `EXPLAIN ANALYZE`로 확인한다.

## save(update_fields=...) [DDoc]

```python
# 나쁜 예: 모든 필드를 업데이트
article.title = "New Title"
article.save()  # 모든 컬럼이 SET 절에 포함

# 좋은 예: 변경된 필드만 업데이트
article.title = "New Title"
article.save(update_fields=["title"])  # title만 UPDATE
```

- 동시성이 높은 환경에서 다른 필드의 변경을 덮어쓰는 것을 방지한다.
- 업데이트되는 데이터 양을 줄여 성능이 개선된다.

## F() 표현식으로 race condition 방지 [DDoc]

```python
# 나쁜 예: Python 레벨 연산 -- 동시 요청 시 값이 덮어써짐
product.stock -= quantity
product.save(update_fields=["stock"])  # 읽기-수정-쓰기 사이에 다른 요청이 끼어들 수 있음

# 좋은 예: F() 표현식으로 DB 레벨 연산 -- 원자적 처리
from django.db.models import F

product.stock = F("stock") - quantity
product.save(update_fields=["stock"])  # UPDATE SET stock = stock - %s

# 좋은 예: 조회수 증가 같은 카운터에도 F() 사용
Post.objects.filter(pk=post_id).update(view_count=F("view_count") + 1)
```

- `F()` 표현식은 DB에서 직접 연산하므로 동시성 환경에서 안전하다.
- 재고 차감, 조회수 증가, 잔액 변경 등 **경합이 발생할 수 있는 필드**에는 반드시 `F()`를 사용한다.
- `select_for_update()`와 함께 사용하면 더 강력한 동시성 제어가 가능하다.

## exists()와 count() [DDoc]

```python
# 나쁜 예: 전체 쿼리셋을 평가하여 존재 여부 확인
if Article.objects.filter(status="published"):  # 모든 행을 로드
    ...

# 좋은 예: exists()로 존재 여부만 확인
if Article.objects.filter(status="published").exists():  # LIMIT 1
    ...

# 나쁜 예: len()으로 개수 확인
count = len(Article.objects.all())  # 모든 객체를 메모리에 로드

# 좋은 예: count()로 DB에서 카운트
count = Article.objects.count()  # SELECT COUNT(*)
```

---

## 캐싱 수준 [DDoc]

Django는 세 가지 수준의 캐싱을 제공한다.

```python
# 1. Per-View 캐싱: 전체 응답을 캐싱
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15분
def article_list(request):
    articles = Article.objects.published()
    return render(request, "articles/list.html", {"articles": articles})

# CBV에서는 URLconf에서 적용
urlpatterns = [
    path("articles/", cache_page(60 * 15)(ArticleListView.as_view())),
]

# 2. 템플릿 프래그먼트 캐싱: 템플릿의 특정 부분만 캐싱
# {% load cache %}
# {% cache 300 sidebar request.user.id %}
#   ... 비용이 큰 사이드바 렌더링 ...
# {% endcache %}

# 3. Low-Level 캐싱: 가장 세밀한 제어
from django.core.cache import cache

def get_expensive_data():
    cache_key = "expensive_data_v1"
    data = cache.get(cache_key)
    if data is None:
        data = compute_expensive_result()
        cache.set(cache_key, data, timeout=60 * 30)  # 30분
    return data
```

## 캐시 무효화 패턴 [DDoc]

```python
# 버전 기반 캐시 키
def get_article_cache_key(article_id):
    article = Article.objects.only("updated_at").get(pk=article_id)
    return f"article:{article_id}:v{article.updated_at.timestamp()}"

# 모델 save 시 관련 캐시 삭제
class Article(models.Model):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"article:{self.pk}")
        cache.delete("article_list")
```

- 자주 변경되는 데이터는 캐싱 효과가 낮다 -- 캐시 적합성을 먼저 판단한다.
- 캐시 키에 **버전 정보**를 포함하면 수동 무효화 빈도를 줄일 수 있다.
- 운영 환경에서는 Redis 또는 Memcached를 사용한다 (로컬 메모리 캐시는 멀티프로세스에서 공유 불가).
