현재 작업 디렉터리 `/private/tmp/dddjango-codex-eval`이 비어 있고, `config.toml`도 없어서 실제 React 컴포넌트를 수정할 수 없습니다. 이 세션도 읽기 전용이라 파일 수정은 불가능합니다.

정리할 컴포넌트 코드를 붙여주거나 실제 프로젝트 경로를 알려주세요. 그러면 props를 보통 이런 방향으로 정리하겠습니다:

```tsx
type UserCardProps = {
  user: {
    id: string;
    name: string;
    email: string;
    avatarUrl?: string;
  };
  variant?: "compact" | "full";
  disabled?: boolean;
  onSelect?: (userId: string) => void;
};

export function UserCard({
  user,
  variant = "full",
  disabled = false,
  onSelect,
}: UserCardProps) {
  // ...
}
```

기준은 다음처럼 잡겠습니다: 연관 값은 객체로 묶고, UI 상태는 명확한 optional/default props로 분리하고, 이벤트 핸들러는 `onX` 형태로 통일하고, 컴포넌트 내부에서만 쓰는 파생값은 props로 받지 않도록 줄이는 방식입니다.