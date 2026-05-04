현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 Git 저장소도 아닙니다.

확인 결과:
- `config.toml` 없음
- `AGENTS.md` 없음
- 소스 파일 없음
- `.git` 없음
- 현재 세션은 `read-only`라 파일 생성/수정도 불가능

그래서 지금 상태에서는 API 구조를 실제로 정리해 적용할 수 없습니다. 작업하려면 저장소 파일이 이 경로에 있어야 하고, 쓰기 가능한 세션이 필요합니다.

API 구조를 잡을 때는 보통 Django 기준으로 이렇게 정리하겠습니다:

```text
apps/
  users/
    models.py
    serializers.py
    services.py
    selectors.py
    urls.py
    views.py
  ...
config/
  urls.py
  settings/
api/
  v1/
    urls.py
    routers.py
common/
  exceptions.py
  responses.py
  pagination.py
  permissions.py
  filters.py
```

쓰기 가능한 상태로 다시 열리면, 기존 코드 패턴을 읽고 `api/v1`, app별 `urls/views/serializers/services/selectors` 경계까지 실제 파일 구조로 정리하겠습니다.