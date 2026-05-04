맥락이 불명확합니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `config.toml`도 없어서, “Django + pytest 프로젝트”라는 가정으로 구조 개선안을 제시합니다.

**[주요 내용]**

**Django라면** 테스트 구조는 실행 환경을 1차 축으로 나누는 편이 좋습니다.

```text
tests/
  isolated/
    conftest.py
    unit/
    integration/
  real/
    conftest.py
    integration/
    e2e/
```

`tests/isolated/`는 CI 기본 스위트입니다. 네트워크, SMTP, Celery 브로커, 외부 API를 Fake/Mock/in-memory로 대체하고 항상 결정적으로 실행되게 둡니다.

`tests/real/`는 실제 DB, 실제 외부 서비스, staging급 인프라를 검증하는 별도 게이트입니다. 기본 CI에 섞지 않습니다.

`Django라면` isolated 전용 settings도 분리하세요.

```text
config/
  settings/
    base.py
    test.py
    test_real.py
```

`config.settings.test`에는 보통 아래 정책을 둡니다.

```python
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "memory://"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

pytest 설정은 다음 방향이 적절합니다.

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated"]
python_files = ["test_*.py"]
```

테스트 작성 규칙은 다음으로 통일하세요.

```python
def test_order_cancel_when_paid_order_cannot_be_cancelled():
    # Arrange

    # Act

    # Assert
```

핵심 기준은 세 가지입니다.

1. 테스트명은 `test_<대상>_<조건>_<기대결과>` 형식으로 둡니다.
2. Act는 한 줄이어야 합니다. Act가 두 개면 테스트를 나눕니다.
3. 도메인 로직은 Mock하지 말고 실제 객체나 InMemory Fake로 검증합니다. Mock은 이메일, 결제, HTTP 같은 외부 경계에만 씁니다.

현재는 파일이 없어 실제 리팩터링과 pytest 실행은 하지 못했습니다. 프로젝트 파일을 넣어주면 `tests/isolated`, `tests/real`, `conftest.py`, pytest 설정까지 실제로 재배치하는 방식으로 이어갈 수 있습니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/fixture/Mock 개선 → **implementation-test** 스킬
> - Red-Green-Refactor 흐름 정리 → **implementation-tdd** 스킬