작업을 진행하려 했지만 현재 지정된 프로젝트 경로가 비어 있습니다.

확인한 내용:
- `/private/tmp/dddjango-codex-eval` 안에 파일이 없습니다.
- `config.toml`도 해당 경로에는 없습니다.
- `/private/tmp` 아래에서 `manage.py`, `views.py`, `AGENTS.md` 등을 찾아봤지만 Django 프로젝트 파일을 찾지 못했습니다.
- 현재 세션은 `read-only`라 파일이 있어도 직접 수정은 제한됩니다.

주문 생성 로직을 리팩터링하려면 Django 프로젝트가 있는 올바른 경로를 알려주시거나, 관련 파일을 제공해 주세요. 최소한 다음 파일이 필요합니다.

- 주문 생성 view가 들어 있는 `views.py`
- 관련 `models.py`
- form/serializer/schema가 있다면 해당 파일
- 주문 생성 관련 테스트가 있다면 테스트 파일

파일이 확인되면 view의 비즈니스 로직을 service/usecase 계층으로 분리하고, view는 요청/응답 처리에 집중하도록 리팩터링 방향과 패치를 제공하겠습니다.