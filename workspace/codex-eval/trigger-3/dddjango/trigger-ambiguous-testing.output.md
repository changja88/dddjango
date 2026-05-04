**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없고 세션도 읽기 전용이라 실제 테스트 디렉터리/파일을 만들 수 없었습니다. 대신 적용해야 할 개선 구조를 정리합니다.

권장 구조:

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

핵심 변경 방향:

- `tests/unit`, `tests/integration`처럼 평면 분리하지 말고, 먼저 실행 환경을 `isolated` / `real`로 나눕니다.
- `tests/isolated`는 CI 기본 테스트로 둡니다. DB, 캐시, 이메일, Celery, 외부 HTTP는 in-memory, fake, mock, testcontainers 등으로 통제합니다.
- `tests/real`은 실제 DB나 외부 서비스에 붙는 테스트만 둡니다. pre-deploy나 수동 게이트에서 별도로 실행합니다.
- Django라면 isolated 테스트는 운영 settings가 아니라 `config.settings.test` 같은 별도 테스트 settings로 실행해야 합니다.

예시 `pyproject.toml` 설정:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
testpaths = ["tests/isolated"]
```

예시 실행 명령:

```bash
pytest tests/isolated -q
pytest tests/real -q --real
```

테스트 작성 규칙은 AAA 구조로 통일합니다:

```python
def test_coupon_when_expired_rejects_redemption():
    # Arrange
    coupon = Coupon(expires_at=past_time)

    # Act
    result = coupon.redeem(now=current_time)

    # Assert
    assert result.is_rejected
```

실제 저장소 파일이 제공되면 위 구조로 `conftest.py`, pytest 설정, 기존 테스트 이동까지 바로 리팩터링할 수 있습니다. 지금은 파일이 없어 테스트 실행도 하지 못했습니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/fixture/pytest 품질 개선 → **implementation-test** 스킬