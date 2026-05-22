수정 대상: answer
원인 분류: answer

# P5 supporting restraint code 분석

## 범위

`code` bucket에서 P5 opt-out/restraint의 supporting evidence로 볼 수 있는 tiny edit case를 확인했다.

## 발견 사항

`case-code-small-rename`은 실제 코드 변경이 작은 rename에 머무는지, role map/architecture redesign/unsupported command claim을 피하는지 검증한다. 다만 code bucket 목적상 P5 plugin-level routing 자체가 아니라 supporting control이므로 P5 완료 근거로 단독 집계하면 안 된다.

## Inventory

| bucket | case id | 검증하는 restraint | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| code | `case-code-small-rename` | tiny code edit restraint, command honesty | answer 수정 | 예 | `20260522-034201-code-try01-targeted-implementation-django-p4` | 기존 passed, 수정 후 재실행 필요 |

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent가 `case-code-small-rename`을 useful supporting evidence지만 P5 plugin-level routing coverage로 세면 안 된다고 보고했다. 결과 수집 근거는 `wait_agent`로 완료 상태를 받은 `019e4df3-1389-7432-bfba-8346978b5fed`, `019e4df3-29e2-7d61-b972-cfbdd29b9d7f`이다.

skill-creator 리뷰: validation integrity를 위해 scope를 `supporting-control`로 명시하는 방식을 채택한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 완료 조건

- `case-code-small-rename.yaml`에 `restraint_scope: supporting-control`을 추가한다.
- code bucket validator와 해당 targeted eval이 통과한다.
