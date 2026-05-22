수정 대상: answer
원인 분류: evaluator

# P5/P4 restraint scope response 분석

## 범위

Response bucket의 tiny/direct/restraint case 중 P5 완료 근거로 세면 안 되는 P4 individual-skill negative case를 분리했다.

## 발견 사항

다음 case들은 유효한 restraint 평가지만 각 individual skill의 제외 조건을 검증한다. P5 plugin-level restraint 완료 근거로 세지 않도록 `restraint_scope: individual-skill`을 명시해야 한다.

- `case-response-simple-rename`
- `case-response-architecture-pattern-restraint`
- `case-response-db-local-crud-restraint`
- `case-response-clean-code-tiny-naming`
- `case-response-python-tiny-type-hint`
- `case-response-test-tiny-assertion`

`case-response-false-claim`은 실행하지 않은 test/subagent claim을 거부하는 plugin-level honesty case로 볼 수 있으므로 `restraint_scope: plugin-level`로 분리한다.

`case-response-django-web-one-line-edit`은 simple web edit에서 workflow/subagent/TDD/DB/API 과적용을 막는 P5 plugin-level restraint case로 분리한다.

## Inventory

| bucket | case id | 검증하는 restraint | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| response | `case-response-simple-rename` | simple Django rename restraint | answer 수정 | 예 | `20260522-030817-response-try01-targeted-implementation-django-p4` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-architecture-pattern-restraint` | implementation-pattern overapplication restraint | answer 수정 | 예 | `20260522-011954-response-try01-targeted-architecture-pattern-restraint` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-db-local-crud-restraint` | local CRUD DB restraint | answer 수정 | 예 | `20260522-014721-response-try01-targeted-architecture-db-p4` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-clean-code-tiny-naming` | tiny naming direct answer | answer 수정 | 예 | `20260522-020627-response-try01-targeted-implementation-cleancode-p4` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-python-tiny-type-hint` | tiny type-hint direct answer | answer 수정 | 예 | `20260522-025559-response-try01-targeted-implementation-python-p4` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-test-tiny-assertion` | tiny pytest assertion direct answer | answer 수정 | 예 | `20260522-111635-response-try01-targeted-implementation-test-p4` | 기존 passed, 수정 후 재실행 필요 |
| response | `case-response-false-claim` | false test/subagent claim refusal | answer 수정 | 예 | 없음 | 미실행 |
| response | `case-response-django-web-one-line-edit` | simple web edit direct answer, no workflow/subagent/TDD/API/DB overreach | case/answer 추가 | 예 | 없음 | 미실행 |

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent가 P4 individual-skill exclusion과 P5 plugin-level restraint의 구분 부재를 Major로 보고했다. 결과 수집 근거는 `wait_agent`로 완료 상태를 받은 `019e4df3-1389-7432-bfba-8346978b5fed`, `019e4df3-29e2-7d61-b972-cfbdd29b9d7f`이다.

skill-creator 리뷰: validation integrity 관점에서 같은 tag를 다른 평가 층위에 쓰면 과적합과 오판 위험이 있다고 판단했다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 완료 조건

- P4 individual-skill negative case는 `restraint_scope: individual-skill`을 가진다.
- plugin-level honesty case는 `restraint_scope: plugin-level`을 가진다.
- simple web edit P5 restraint case는 `restraint_scope: plugin-level`과 `p5-plugin-restraint`를 가진다.
- response bucket validator와 수정 case targeted eval이 통과한다.
