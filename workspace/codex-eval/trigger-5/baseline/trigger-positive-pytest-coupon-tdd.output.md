현재는 구현을 진행할 수 없습니다.

확인한 내용:
- 작업 경로 `/private/tmp/dddjango-codex-eval`가 비어 있습니다.
- 지시된 `config.toml`도 해당 경로에 없습니다.
- Django 프로젝트 파일(`manage.py`, `pyproject.toml`, `requirements.txt` 등)도 `/private/tmp` 하위에서 찾지 못했습니다.
- 현재 세션은 `read-only` sandbox라 새 파일 생성/수정도 할 수 없습니다.

쿠폰 적용 기능을 pytest/TDD로 구현하려면 Django 프로젝트 파일이 있는 실제 경로가 필요합니다. 프로젝트가 다른 디렉터리에 있다면 그 경로를 알려주세요. 또는 이 eval 디렉터리에 프로젝트 파일을 배치한 뒤 다시 요청해주시면, 테스트부터 작성하고 실패 확인 후 구현하는 순서로 진행하겠습니다.