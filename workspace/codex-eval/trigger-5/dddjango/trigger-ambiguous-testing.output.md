맥락이 불명확합니다. 확인 질문은 하나입니다: `pytest + pytest-django` 기준으로 테스트 구조를 재편하면 될까요?

**[주요 내용]**

현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, AGENTS 지시의 `config.toml`도 존재하지 않습니다. 또한 세션이 읽기 전용이라 파일 생성/이동/테스트 실행은 하지 못했습니다.

Django라면 다음 구조를 권합니다.

```text
tests/
  isolated/
    conftest.py
    unit/
      domain/
      application/
    integration/
      django/
      repositories/
  real/
    conftest.py
    integration/
      external_services/
      database/
```

핵심 기준은 “실행 환경”을 먼저 나누고, 그 아래에서 “테스트 범위”를 나누는 것입니다.

`tests/isolated/`는 CI 기본 스위트입니다. 외부 네트워크, 실제 SMTP, 실제 Celery 브로커, 운영 DB를 쓰지 않아야 합니다. Django라면 `config.settings.test` 같은 전용 settings를 두고 `EMAIL_BACKEND=locmem`, `CACHES=LocMemCache`, `CELERY_TASK_ALWAYS_EAGER=True`, 빠른 password hasher를 사용합니다.

`tests/real/`는 실제 DB나 외부 서비스에 붙는 검증용입니다. 기본 CI가 아니라 pre-deploy나 수동 게이트로 분리합니다.

DDD 기준으로는 `isolated/unit/domain`에 엔티티/값 객체/도메인 서비스 테스트를 두고, DB나 Django ORM 없이 순수 객체로 검증합니다. 유스케이스는 `isolated/unit/application`에 두며 Repository/Gateway는 `MagicMock` 남발 대신 `InMemoryRepository` Fake로 대체합니다. ORM repository, Django signal, serializer, view처럼 프레임워크 경계는 `isolated/integration/django`나 `isolated/integration/repositories`로 분리합니다.

진행 순서는 이렇게 잡겠습니다.

```text
RED: 현재 테스트 파일을 환경/범위 기준으로 분류하는 실패 기준 작성
GREEN: tests/isolated, tests/real 구조와 pytest 설정 최소 추가
REFACTOR: 중복 setup을 conftest.py, factory, fake repository로 이동
```

테스트 함수는 `test_<대상>_<조건>_<기대결과>` 형식과 AAA 구조를 기준으로 정리하는 것이 좋습니다.

실행 명령 예시는 다음입니다.

```bash
pytest tests/isolated -q
pytest tests/real -q
```

실제 실행은 하지 못했습니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/fixture/fake 개선 → **implementation-test** 스킬
> - RED/GREEN/REFACTOR 흐름 유지 → **implementation-tdd** 스킬