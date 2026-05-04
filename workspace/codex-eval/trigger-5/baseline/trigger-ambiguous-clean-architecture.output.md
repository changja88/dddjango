작업을 진행할 수 없습니다. `/private/tmp/dddjango-codex-eval`가 비어 있고, `config.toml`, `AGENTS.md`, Django 프로젝트 파일(`manage.py`, `settings.py`, 앱 코드 등), Git 저장소가 모두 없습니다.

또한 현재 세션은 `read-only` sandbox라 파일 생성/수정도 차단되어 있습니다.

프로젝트 파일이 있는 실제 경로를 알려주거나, 이 디렉터리에 소스를 넣은 뒤 다시 요청해 주세요. 그러면 구조를 읽고 Django 코드를 Clean Architecture 기준으로 `domain / application / infrastructure / interface` 경계로 정리하겠습니다.