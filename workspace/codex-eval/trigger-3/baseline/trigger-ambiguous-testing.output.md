현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없고 세션도 읽기 전용이라 테스트 구조를 실제로 수정하지는 못했습니다. `config.toml`도 해당 경로에는 없고, 인접한 Codex 홈 설정만 확인됐습니다.

테스트 구조 개선 기준은 이렇게 잡는 게 좋습니다. 프레임워크가 pytest/Django라면:

```text
tests/
  conftest.py
  isolated/
    conftest.py
    unit/
    integration/
  real/
    conftest.py
    integration/
    e2e/
```

핵심은 `unit/integration`을 먼저 나누는 게 아니라, 실행 환경을 먼저 나누는 겁니다.

- `tests/isolated/`: CI 기본 스위트. 네트워크 차단, 시간 고정, fake/mock/in-memory/testcontainers 사용
- `tests/real/`: 실 DB, 실 외부 API, stage 환경 등. pre-deploy 같은 별도 게이트에서 실행
- Django라면 `isolated`는 `config.settings.test`, `real`은 `config.settings.test_real`처럼 settings도 분리
- 공통 fixture는 `tests/conftest.py`, 환경 강제 규칙은 `tests/isolated/conftest.py`와 `tests/real/conftest.py`에 배치
- 테스트 함수는 AAA 구조와 `test_<대상>_<조건>_<기대결과>` 이름을 유지

실제 리팩터링을 하려면 다음 정보가 필요합니다: 사용하는 테스트 프레임워크가 `pytest`인지 Django `TestCase` 중심인지, 현재 테스트 디렉터리 구조, `pyproject.toml` 또는 `pytest.ini`, 그리고 대표 테스트 파일 2-3개입니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/fixture/pytest 설정 → **implementation-test** 스킬