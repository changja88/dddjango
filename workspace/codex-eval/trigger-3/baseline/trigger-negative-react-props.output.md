현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리가 비어 있어서 React 컴포넌트 파일을 찾을 수 없습니다. 또한 세션 권한이 `read-only`라 파일 수정도 불가능합니다.

확인한 내용:
- `package.json`, `src/`, `components/`, `*.tsx`, `*.jsx` 없음
- `config.toml`은 현재 프로젝트가 아니라 `../dddjango-codex-home/.codex/config.toml`에만 있음
- 현재 디렉터리에는 수정할 React 코드가 없음

React 파일이 있는 프로젝트 경로를 알려주시거나 코드를 넣어주시면 props 구조를 정리해드릴 수 있습니다. 권한이 쓰기 가능해지면 직접 리팩터링까지 진행하겠습니다.