현재 `/private/tmp/dddjango-codex-eval` 안에는 React 소스 파일이 없어 실제 리팩터링은 적용할 수 없습니다. React 기준으로 props 구조는 보통 이렇게 정리하면 됩니다.

```tsx
type UserCardProps = {
  user: {
    id: string;
    name: string;
    email: string;
    avatarUrl?: string;
  };
  isSelected?: boolean;
  onSelect?: (userId: string) => void;
};

export function UserCard({ user, isSelected = false, onSelect }: UserCardProps) {
  return (
    <button
      type="button"
      aria-pressed={isSelected}
      onClick={() => onSelect?.(user.id)}
    >
      {user.avatarUrl && <img src={user.avatarUrl} alt="" />}
      <strong>{user.name}</strong>
      <span>{user.email}</span>
    </button>
  );
}
```

정리 기준은 다음이 좋습니다.

- 데이터는 객체로 묶기: `name`, `email`, `avatarUrl`을 각각 넘기기보다 `user`로 묶습니다.
- 상태 props는 명확히 이름 붙이기: `selected`보다 `isSelected`, `disabled`보다 `isDisabled`.
- 이벤트는 `onX` 형태로 통일: `onClick`, `onSelect`, `onSubmit`.
- 내부 계산값은 props로 받지 않기: 컴포넌트 안에서 만들 수 있는 값은 안에서 계산합니다.
- 선택값은 optional + 기본값 사용: `isSelected = false`.
- children이 필요한 컴포넌트만 `children`을 받기.

예를 들어 흩어진 props가 있다면:

```tsx
<UserCard
  id={user.id}
  name={user.name}
  email={user.email}
  avatarUrl={user.avatarUrl}
  selected={selectedId === user.id}
  handleClick={handleSelect}
/>
```

이렇게 정리하는 편이 낫습니다.

```tsx
<UserCard
  user={user}
  isSelected={selectedId === user.id}
  onSelect={handleSelect}
/>
```

프로젝트 파일을 넣어주면 실제 컴포넌트 기준으로 props 타입, 이름, 전달 구조까지 맞춰서 정리할 수 있습니다.