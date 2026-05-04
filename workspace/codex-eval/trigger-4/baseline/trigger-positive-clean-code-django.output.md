`/private/tmp/dddjango-codex-eval` 안을 확인했는데, 현재 디렉터리가 비어 있습니다. `config.toml`, `AGENTS.md`, `views.py`, `manage.py` 같은 Django 프로젝트 파일도 없습니다.

또한 현재 세션은 `read-only` sandbox라 파일 수정도 불가능합니다. 리팩터링을 진행하려면 다음 중 하나가 필요합니다.

1. Django 프로젝트 파일이 실제로 있는 경로를 알려주세요.
2. 주문 생성 view 코드를 붙여주세요.
3. 쓰기 가능한 세션으로 다시 실행해주세요.

코드를 받으면 view의 주문 생성 로직을 service/use-case 계층으로 분리하고, validation, transaction, side effect 처리를 기준으로 클린 코드 형태로 정리하겠습니다.