현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고, 안내에 나온 `config.toml`도 없습니다. 게다가 이 세션은 `read-only` sandbox라 새 Django 파일을 생성하거나 수정할 수 없습니다.

확인한 내용:
- `pwd`: `/private/tmp/dddjango-codex-eval`
- `ls -la`: 프로젝트 파일 없음
- `config.toml`: `No such file or directory`

DRF `ModelViewSet`, `ModelSerializer`, router 구현을 하려면 최소한 Django 프로젝트/app 파일들이 필요합니다. 쓰기 가능한 세션이나 실제 프로젝트 파일이 있는 경로로 다시 실행해주면 바로 `Order` 모델 기준으로 serializer/viewset/router까지 연결하겠습니다.