수정 대상: reference
원인 분류: source gap

# architecture-implementation-patterns P1 reference 분석

## 평가 요약

`workspace/reference/architecture-implementation-patterns/reference/final.md`가 존재하지 않는다. 현재 `dddjango/skills/architecture-implementation-patterns/SKILL.md`와 bundled reference는 `architecture-ddd`, `implementation-django`, `implementation-python` fallback source를 사용한다고 선언한다. 따라서 P1 기준에서 layered architecture, clean architecture, hexagonal architecture, ports/adapters, dependency direction, repository, Unit of Work, CQRS, event sourcing, saga, outbox, ACL, service layer 판단을 전용 source reference로 검증할 수 없다.

## 근거

- `workspace/reference/architecture-implementation-patterns/` 경로가 없다.
- `workspace/reference/architecture-ddd/reference/final.md`에는 계층 아키텍처, DIP, 리포지토리, Unit of Work, CQRS, 도메인 이벤트, outbox, ACL 관련 기준이 있으나 implementation patterns 전용 source가 아니며 일부 항목은 향후 분리 예정이라고 적혀 있다.
- `workspace/reference/implementation-django/reference/final.md`에는 Django 서비스/셀렉터, Fat Model, Repository 도입 비용과 실용적 Django 경로가 있다.
- `workspace/reference/implementation-python/reference/final.md`에는 Repository/Unit of Work를 전용 source reference로 분리 예정이라고 적혀 있다.

## 부족 항목

| 항목 | 현재 상태 | P1 판정 |
|---|---|---|
| layered architecture | `architecture-ddd`에 근거 있음 | 전용 reference 필요 |
| clean architecture | source가 흩어져 있음 | 전용 reference 필요 |
| hexagonal architecture | `architecture-ddd`에 개략만 있음 | 전용 reference 필요 |
| ports/adapters | fallback reference와 skill에만 상세 있음 | 전용 reference 필요 |
| dependency direction/DIP | `architecture-ddd`에 근거 있음 | 전용 reference 필요 |
| repository | `architecture-ddd`, `implementation-django`에 근거 있음 | 전용 reference 필요 |
| Unit of Work | `architecture-ddd`, Django transaction 근거 있음 | 전용 reference 필요 |
| CQRS | `architecture-ddd`에 선택 적용 기준 있음 | 전용 reference 필요 |
| event sourcing | `architecture-ddd` 참고 문헌과 skill reference에만 요약 있음 | 전용 reference 필요 |
| saga | `architecture-ddd` 참고 문헌과 skill reference에만 요약 있음 | 전용 reference 필요 |
| outbox | `architecture-ddd`에 근거 있음 | 전용 reference 필요 |
| ACL | `architecture-ddd`에 근거 있음 | 전용 reference 필요 |
| service layer | `architecture-ddd`, `implementation-django`에 근거 있음 | 전용 reference 필요 |

## 리뷰 방식

리뷰 방식: sequential-fallback

Subagent 리뷰/순차 fallback: reference가 없는 첫 루프에서는 수정 전 real-subagent 리뷰보다 결손이 명확하므로 순차 fallback으로 판정했다. 이후 skill 반영 점검에서 real-subagent 리뷰를 수행한다.

리뷰 결과: Blocker 1, Major 0, 열린 Minor 0

- Blocker: dedicated source reference가 없어 P1 종료 조건인 reference 충분성을 증명할 수 없다.

## 완료 판정

Reference 생성 후 동일 기준으로 재평가해야 한다.
