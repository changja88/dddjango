현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고 `.git`, `config.toml`, Django 프로젝트 파일이 없습니다. 또 세션이 `read-only`라 파일 생성/수정도 불가능합니다.

DRF로 해당 API를 구현하려면 다음 중 하나가 필요합니다.

1. 실제 Django 프로젝트 파일이 있는 경로 제공
2. 구현할 API 스펙 제공: endpoint, method, request/response schema, 인증/권한
3. 쓰기 가능한 세션으로 다시 실행

지침 자체는 확인했습니다: 프로젝트가 Django Ninja를 쓰더라도 이번 API는 DRF로 구현하겠습니다.