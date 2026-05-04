작업을 진행하려고 확인했지만, `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있습니다. `config.toml`도 해당 경로에 없고, 현재 세션 권한도 `read-only`라 파일 생성/수정이 불가능합니다. 그래서 실제 테스트 구조 리팩터링이나 `pytest` 실행은 하지 못했습니다.

적용하려던 구조는 다음 기준입니다:

```text
tests/
  isolated/
    conftest.py
    unit/
    integration/
  real/
    conftest.py
    integration/
```

핵심 방향:
- `tests/isolated/`: CI 기본 테스트. 네트워크/외부 서비스 차단, Fake/Mock/in-memory 의존성 사용
- `tests/real/`: 실제 DB/외부 서비스 연동 검증. 별도 게이트에서 실행
- Django라면 `config/settings/test.py`를 두고 `DJANGO_SETTINGS_MODULE=config.settings.test`로 isolated 테스트를 고정
- 공통 fixture는 `tests/isolated/conftest.py`로 이동
- 테스트 함수는 AAA 구조와 `test_<대상>_<조건>_<기대결과>` 네이밍으로 정리

실제 프로젝트 파일이 있는 경로를 알려주거나 쓰기 가능한 상태로 다시 실행하면, 기존 테스트를 이 구조로 직접 이동하고 `pytest` 설정까지 정리하겠습니다.

---
> **관련 스킬 참조:**
> - 테스트 구조/fixture/pytest 개선 → **implementation-test** 스킬