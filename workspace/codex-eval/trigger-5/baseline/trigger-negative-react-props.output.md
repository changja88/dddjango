현재 `/private/tmp/dddjango-codex-eval`에는 React 소스가 없습니다. `rg --files` 결과도 비어 있고, `package.json`, `.tsx`, `.jsx` 파일도 `/private/tmp` 아래에서 찾지 못했습니다. 또한 현재 세션은 읽기 전용이라 파일 생성/수정도 할 수 없습니다.

확인한 내용:
- 작업 디렉터리: `/private/tmp/dddjango-codex-eval`
- 디렉터리 상태: 비어 있음
- 지시 파일로 언급된 `config.toml`: 현재 경로에는 없고 `../dddjango-codex-home/.codex/config.toml`만 존재
- React 컴포넌트 파일: 없음

React 컴포넌트 props 정리는 보통 다음 형태로 맞추면 됩니다:

```tsx
type ComponentNameProps = {
  id: string;
  title: string;
  isActive?: boolean;
  onSelect?: (id: string) => void;
};

export function ComponentName({
  id,
  title,
  isActive = false,
  onSelect,
}: ComponentNameProps) {
  // ...
}
```

파일이 있는 실제 프로젝트 경로를 주거나 소스가 이 디렉터리에 준비되면, 컴포넌트별로 props 타입을 분리하고 optional/default props, event handler 네이밍, children 처리까지 일관되게 정리하겠습니다.