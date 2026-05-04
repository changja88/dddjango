현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있어서 React 컴포넌트 파일을 찾을 수 없습니다. 또한 세션이 `read-only`라 파일 수정도 실행할 수 없는 상태입니다.

확인한 내용:
- 작업 디렉터리: `/private/tmp/dddjango-codex-eval`
- React 관련 파일: 없음
- `config.toml`: 해당 디렉터리에는 없음
- 쓰기 권한: 현재 세션에서는 불가

컴포넌트 파일이나 프로젝트가 있는 실제 경로를 알려주면 props 구조를 분석해서 정리 방향과 구체적인 diff 형태로 제안할 수 있습니다. 권한이 쓰기 가능해지면 직접 리팩터링까지 진행하겠습니다.