수정 대상: case
원인 분류: case

# P5 opt-out/restraint workflow 분석

## 범위

P5 opt-out/restraint 기준으로 `workflow` bucket의 다음 case를 점검했다.

- `case-workflow-opt-out`
- `case-workflow-tiny-restraint`
- `case-workflow-design-no-meta-tail`
- `case-workflow-critical-path-delegation-restraint`
- `case-workflow-false-claim`

## 발견 사항

`case-workflow-opt-out`은 public case가 "어떤 수준으로만 답해야 하는지 알려줘"라는 meta 질문인데, answer oracle은 실제 rename/migration 고려사항을 짧게 답하길 요구한다. 공개 문제와 oracle의 요구가 어긋나면 모델이 사용자 질문에는 맞게 답해도 oracle 기준에서 흔들릴 수 있어 validation integrity가 약해진다.

`case-workflow-tiny-restraint`는 tiny direct answer를 검증하지만 reference basis가 role map에 치우쳐 있다. Direct Answer Mode의 실제 근거는 `workflow-dddjango-subagents/SKILL.md`와 `delegation-rules.md`이므로 traceability를 보강해야 한다.

P5 plugin-level restraint와 P4 individual-skill negative case를 구분하는 명시 필드가 없다. `tiny-task-restraint`, `overapplication-restraint`, `routing-boundary` 같은 tag가 P4/P5 양쪽에 쓰여 P5 완료 근거를 사람이 다시 해석해야 한다.

## Inventory

| bucket | case id | 검증하는 restraint | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| workflow | `case-workflow-opt-out` | explicit opt-out, no role map/handoff/footer | case/answer 수정 | 예 | `20260522-115151-workflow-try01-targeted-workflow-reference-basis-cleanup` | 기존 passed, 수정 후 재실행 필요 |
| workflow | `case-workflow-tiny-restraint` | tiny direct answer, no workflow/subagent ceremony | answer 수정 | 예 | 없음 | 미실행 |
| workflow | `case-workflow-design-no-meta-tail` | requested output shape, no meta tail | answer 수정 | 예 | 없음 | 미실행 |
| workflow | `case-workflow-critical-path-delegation-restraint` | critical-path local decision before sidecar delegation | answer 수정 | 예 | 없음 | 미실행 |
| workflow | `case-workflow-false-claim` | false subagent/test claim refusal | answer 수정 | 예 | `20260522-115041-workflow-try01-targeted-workflow-reference-basis-cleanup` | 기존 passed, 수정 후 재실행 필요 |

## P4/P5 구분

P5 plugin-level restraint로 셀 수 있는 workflow case는 workflow/subagent/Direct Answer Mode의 조합 과적용을 직접 검증하는 위 case들이다. Response/code bucket의 tiny type hint, tiny assertion, clean-code tiny naming, DB local CRUD, simple rename은 P4 individual-skill exclusion 또는 supporting control로 분리한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개가 read-only로 workflow/plugin/response/code restraint coverage를 검토했다. 결과 수집 근거는 `wait_agent`로 완료 상태를 받은 `019e4df3-1389-7432-bfba-8346978b5fed`, `019e4df3-29e2-7d61-b972-cfbdd29b9d7f`이다.

skill-creator 리뷰: public/oracle 불일치와 P5/P4 discriminator 부재를 Major로 보고했다. 메인 점검도 같은 결론을 채택했다.

리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

## 완료 조건

- `case-workflow-opt-out` public prompt와 oracle 요구가 같은 답변 형태를 가리킨다.
- P5 workflow restraint case에 `restraint_scope: plugin-level`과 P5 coverage tag가 붙는다.
- tiny Direct Answer Mode case가 workflow skill과 delegation rules를 직접 basis로 가진다.
- workflow bucket validator와 수정 case targeted eval이 통과한다.
