현재 `/private/tmp/dddjango-codex-eval`에는 Django 프로젝트 파일이 없습니다. `config.toml`도 해당 경로에는 없고, 실제로 확인된 것은 `/private/tmp/dddjango-codex-home/.codex/config.toml`뿐입니다. `manage.py`, `views.py`, `models.py`도 `/private/tmp` 하위에서 찾지 못했습니다.

그래서 지금은 주문 생성 로직을 직접 리팩터링할 수 없습니다. 대상 코드가 있는 프로젝트 경로를 알려주거나, 주문 생성 뷰 코드를 붙여주면 다음 기준으로 바로 정리하겠습니다:

- View에는 HTTP 입출력과 폼/API 응답 처리만 남김
- 주문 생성 비즈니스 로직은 `orders/services.py`의 `order_create(...)`로 추출
- 읽기 전용 조회는 필요하면 `orders/selectors.py`로 분리
- DB 변경은 `transaction.atomic()`으로 묶음
- 이메일/알림/외부 API 호출은 `transaction.on_commit()`으로 분리
- 인증 누락 시 `@login_required` 또는 CBV의 `LoginRequiredMixin` 적용

---
> **관련 스킬 참조:**
> - Django 서비스 레이어 리팩터링 → **implementation-django** 스킬