# 테스트 패턴

## 테스트 환경 분리: isolated vs real [TSD]

테스트 디렉토리는 1차로 실행 환경(`tests/isolated/`, `tests/real/`), 2차로 범위(`unit/`, `integration/`)로 분리한다. 이 컨벤션의 일반 정의는 implementation-test의 SKILL.md를 따르고, Django 구체화는 다음과 같다.

- `tests/isolated/`는 **`config/settings/test.py`** 로 실행한다. 이 settings는 외부 의존성을 모두 차단한다 -- `DATABASES`는 SQLite in-memory(또는 testcontainers PostgreSQL), `EMAIL_BACKEND`는 `locmem`, `CACHES`는 `LocMemCache`, `CELERY_TASK_ALWAYS_EAGER=True`, `CELERY_BROKER_URL="memory://"`, `PASSWORD_HASHERS`는 `MD5PasswordHasher`(테스트 속도).
- `tests/real/`는 **`config/settings/test_real.py`** (또는 stage settings)로 실행한다. 실 DB, 실 SMTP, 실 Celery 브로커, 실 외부 API에 붙어 배포 직전 통합을 검증한다. 자격 증명이 없는 환경에서는 자동 스킵되도록 conftest 픽스처에서 가드한다.

운영 settings(`config/settings/production.py`)로 isolated 테스트를 돌리는 것은 회귀 -- 운영 DB나 SMTP가 잘못 깨어날 수 있다. CI 잡은 환경별로 분리하고 settings를 환경 변수로 주입한다.

```bash
# isolated 잡 (모든 PR/푸시)
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/

# real 잡 (pre-deploy, 자격 증명 주입)
DJANGO_SETTINGS_MODULE=config.settings.test_real pytest tests/real/
```

`config/settings/test.py`의 구체적인 내용과 conftest.py 계층은 implementation-test의 `references/pytest-configuration.md`를 따른다.

## TestCase 선택 기준 [DDoc]

| 클래스 | 특징 | 사용 시나리오 |
|--------|------|-------------|
| `SimpleTestCase` | DB 접근 불가, 가장 빠름 | 유틸리티 함수, 폼 검증 테스트 |
| `TestCase` | 트랜잭션 롤백으로 격리, 빠름 | **대부분의 테스트** |
| `TransactionTestCase` | 실제 트랜잭션 커밋, 느림 | `select_for_update()`, DB 트리거 테스트 |
| `LiveServerTestCase` | 실제 서버 실행 | Selenium 통합 테스트 |

```python
from django.test import TestCase

class ArticleModelTest(TestCase):
    def test_publish_sets_published_at(self):
        """publish()가 published_at을 설정하는지 검증."""
        article = Article.objects.create(title="Test", author=self.user)
        article.publish()
        article.refresh_from_db()
        self.assertIsNotNone(article.published_at)
        self.assertEqual(article.status, Article.Status.PUBLISHED)
```

## Factory Boy 활용 [TDD]

```python
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    status = Article.Status.DRAFT

    class Params:
        published = factory.Trait(
            status=Article.Status.PUBLISHED,
            published_at=factory.LazyFunction(timezone.now),
        )

# 테스트에서 사용
class ArticleServiceTest(TestCase):
    def test_publish_article(self):
        article = ArticleFactory()  # draft 상태
        article.publish()
        self.assertEqual(article.status, Article.Status.PUBLISHED)

    def test_published_articles_queryset(self):
        ArticleFactory.create_batch(3, published=True)
        ArticleFactory.create_batch(2)  # draft
        self.assertEqual(Article.objects.published().count(), 3)
```

- `SubFactory`로 관련 객체를 자동 생성한다.
- `Trait`로 특정 상태의 팩토리 변형을 정의한다.
- `create_batch()`로 여러 객체를 한 번에 생성한다.

## pytest-django 활용 [TDD]

```python
import pytest
from django.test import Client

@pytest.fixture
def api_client():
    return Client()

@pytest.fixture
def authenticated_user(db):
    user = UserFactory()
    return user

@pytest.mark.django_db
class TestArticleAPI:
    def test_create_article(self, api_client, authenticated_user):
        api_client.force_login(authenticated_user)
        response = api_client.post("/api/articles/", {
            "title": "Test Article",
            "body": "Content",
        })
        assert response.status_code == 201
        assert Article.objects.count() == 1

    def test_list_published_articles(self, api_client):
        ArticleFactory.create_batch(3, published=True)
        response = api_client.get("/api/articles/")
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3
```

- `@pytest.mark.django_db`로 DB 접근을 명시한다.
- pytest 픽스처로 테스트 설정 코드를 50% 이상 줄일 수 있다.
- `assertNumQueries`로 쿼리 수 회귀를 방지한다.

## 테스트에서의 Django 공식 규칙 [DCS]

```python
# 좋은 예: assertIs(x, True) -- 타입까지 검증
self.assertIs(article.is_published, True)

# 나쁜 예: assertTrue() -- truthy 값도 통과
self.assertTrue(article.is_published)  # 1, "yes" 등도 통과

# 좋은 예: assertRaisesMessage() -- 에러 메시지까지 검증
with self.assertRaisesMessage(ValidationError, "이미 등록된 이메일"):
    form.clean_email()

# 독스트링은 기대 동작을 바로 서술 (Tests that... 같은 전치사 없이)
def test_publish_sets_status(self):
    """publish() sets status to PUBLISHED and saves published_at."""
```
