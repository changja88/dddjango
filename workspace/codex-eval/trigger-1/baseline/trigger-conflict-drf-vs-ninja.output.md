현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리가 비어 있어서 Django 프로젝트 파일을 찾을 수 없습니다. `manage.py`, `settings.py`, `urls.py`, 앱 코드가 전혀 없고, 세션도 `read-only`라 새 파일을 만들 수 없습니다.

확인한 내용:
- `/private/tmp/dddjango-codex-eval`: 비어 있음
- `/private/tmp` 아래 Django 프로젝트 파일 검색: 없음
- `config.toml`은 `/private/tmp/dddjango-codex-home/.codex/config.toml`에만 있음

프로젝트 파일이 마운트된 상태로 다시 열어주면, 기존 Django Ninja 구조는 유지하고 이번 API만 DRF의 `APIView`/`Serializer`/`urls.py` 패턴으로 구현하겠습니다.