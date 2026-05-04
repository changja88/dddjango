## [주요 내용]

현재 워크스페이스에서는 실제 구현을 진행할 수 없습니다.

확인한 상태:
- `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있습니다.
- `config.toml`도 현재 디렉터리에 없습니다. 상위 임시 홈의 `.codex/config.toml`만 존재합니다.
- `manage.py`, `pyproject.toml`, `pytest.ini`, Django 앱 파일을 찾지 못했습니다.
- 현재 샌드박스가 `read-only`라 파일 생성/수정도 불가능합니다.
- 따라서 실패 테스트 작성, pytest 실행, Green 구현, Refactor 적용을 실제 파일에 반영할 수 없었습니다.

요청하신 TDD 진행은 프로젝트 파일이 있으면 아래 순서로 처리합니다.

**RED**
- `tests/isolated/unit/test_coupon_application.py`에 실패 테스트부터 작성
- 예: 활성 쿠폰을 주문 금액에 적용하면 할인 금액과 최종 결제 금액이 계산되는지 검증
- `pytest tests/isolated/unit/test_coupon_application.py` 실행
- 실패 원인이 “쿠폰 적용 기능 미구현”임을 확인

**GREEN**
- `coupons/services.py` 또는 기존 도메인 서비스 위치에 최소 구현
- 쿠폰 유효성, 최소 주문 금액, 정액/정률 할인, 최대 할인 한도를 통과에 필요한 만큼만 구현
- 같은 pytest 명령으로 테스트 통과 확인

**REFACTOR**
- 할인 정책을 값 객체/도메인 서비스로 정리
- 매직 문자열은 `Enum` 또는 `TextChoices`로 정리
- 도메인 예외를 정의해 `ValueError`/`None` 반환을 피함
- 전체 관련 테스트를 다시 실행해 Green 상태 유지 확인

현재는 코드베이스가 없어서 구체 파일에 패치를 만들 수 없습니다. Django 프로젝트가 포함된 쓰기 가능한 워크스페이스로 열리면, 실제 pytest 실패 로그부터 남기면서 Red-Green-Refactor 순서로 구현하겠습니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - TDD 구현 흐름 → **superpowers:test-driven-development** 스킬
> - pytest 테스트 작성 → **dddjango:implementation-test** 스킬
> - Python/Django 도메인 코드 작성 → **dddjango:implementation-python** 스킬