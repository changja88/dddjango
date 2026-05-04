현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있습니다.

확인 결과:
- `config.toml` 없음
- `AGENTS.md` 없음
- `tests/`, `pytest.ini`, `pyproject.toml` 등 테스트 관련 파일 없음
- 현재 환경도 `read-only`라 파일 생성/수정 불가

그래서 지금 상태에서는 테스트 구조를 실제로 개선할 수 없습니다. 저장소 파일이 있는 올바른 경로를 알려주거나, 작업 디렉터리에 프로젝트 파일을 넣어주면 테스트 구조를 분석해서 정리 방향을 잡고 변경하겠습니다.