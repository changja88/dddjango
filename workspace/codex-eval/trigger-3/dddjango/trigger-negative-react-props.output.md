작업을 진행하려고 확인했지만 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있습니다. `config.toml`도 해당 경로에는 없고, 인접한 Codex 설정 파일만 발견됐습니다. 현재 세션은 `read-only`라 파일 생성/수정도 할 수 없습니다.

React 컴포넌트 props 구조를 실제로 정리하려면 컴포넌트 파일들이 있는 프로젝트 경로가 필요합니다. 소스가 준비되면 보통 아래 방향으로 정리하겠습니다.

```tsx
type UserCardProps = {
  user: {
    id: string;
    name: string;
    email?: string;
  };
  variant?: "compact" | "full";
  onSelect?: (userId: string) => void;
};

export function UserCard({ user, variant = "compact", onSelect }: UserCardProps) {
  // ...
}
```

정리 기준은 다음처럼 잡겠습니다.

- 관련 props는 객체로 묶기: `userName`, `userEmail` 대신 `user`
- 이벤트는 `onX` 네이밍으로 통일
- optional props에는 기본값 지정
- TypeScript 타입을 컴포넌트 근처에 명확히 선언
- 불필요한 prop drilling은 children 또는 composition으로 축소

프로젝트 파일이 있는 경로를 알려주거나 현재 디렉터리에 소스를 배치해 주면 바로 컴포넌트별로 정리안을 적용하겠습니다.