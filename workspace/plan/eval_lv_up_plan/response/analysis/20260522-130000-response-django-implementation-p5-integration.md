수정 대상: case

# P5 Django implementation 연계 평가 분석

## 배경

P4 직접 평가에서는 `implementation-django`, `implementation-django-ninja`, `implementation-django-web`, `implementation-python`, `implementation-cleancode`, `implementation-test`, `implementation-tdd`가 각각 직접 case와 targeted pass run을 가진다. 그러나 P5 종료 기준은 개별 skill 품질이 아니라 Django 구현 시나리오에서 ORM/service/migration, Ninja Router/Schema, server-rendered web, Python typing, clean-code review, pytest/TDD가 서로의 책임을 침범하지 않는지와 handoff가 평가되는지를 요구한다.

## Inventory

| bucket | case id | 연결 skill | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|
| response | `case-response-django-implementation-handoff` | P5 Django implementation handoff | 추가 | 예 | `20260522-133758-response-try01-targeted-django-implementation-p5-integration` | failed, stale-hash |
| response | `case-response-django-web-one-line-edit` | implementation-django-web restraint | 추가 | 예 | pending | missing |
| response | `case-response-order-create` | architecture-ddd, architecture-db, architecture-api, implementation-django-ninja, implementation-test, workflow | answer 수정 | 예 | `20260522-014856-response-try01-targeted-architecture-db-p4` | passed, stale-hash |
| response | `case-response-simple-rename` | implementation-django restraint | answer 수정 | 예 | `20260522-030817-response-try01-targeted-implementation-django-p4` | passed, stale-hash |
| response | `case-response-test-tiny-assertion` | implementation-test restraint | answer 수정 | 예 | `20260522-111635-response-try01-targeted-implementation-test-p4` | passed, stale-hash |
| response | `case-response-false-claim` | validation honesty restraint | answer 수정 | 예 | pending | missing |
| response | `case-response-architecture-pattern-restraint` | architecture-implementation-patterns restraint | answer 수정 | 예 | `20260522-011954-response-try01-targeted-architecture-pattern-restraint` | passed, stale-hash |
| response | `case-response-db-local-crud-restraint` | architecture-db restraint | answer 수정 | 예 | `20260522-014721-response-try01-targeted-architecture-db-p4` | passed, stale-hash |
| response | `case-response-clean-code-tiny-naming` | implementation-cleancode restraint | answer 수정 | 예 | `20260522-020627-response-try01-targeted-implementation-cleancode-p4` | passed, stale-hash |
| response | `case-response-python-tiny-type-hint` | implementation-python restraint | answer 수정 | 예 | `20260522-025559-response-try01-targeted-implementation-python-p4` | passed, stale-hash |
| code | `case-code-order-api` | architecture-api, architecture-db, implementation-django, implementation-django-ninja, implementation-test | answer 수정 | 예 | `20260522-021421-code-try01-targeted-implementation-django-ninja-p4` | failed, stale-hash |
| code | `case-code-small-rename` | implementation restraint/control | answer 수정 | 예 | `20260522-034201-code-try01-targeted-implementation-django-p4` | passed, stale-hash |
| workflow | `case-workflow-risky-write` | workflow, architecture-db, architecture-api, implementation-django, implementation-test | answer/public 수정 | 예 | `20260522-133815-workflow-try01-targeted-workflow-p5-combined-risky-write` | failed, stale-hash |
| workflow | `case-workflow-positive-composite` | workflow, DB/API/Django/Test handoff | answer/public 수정 | 예 | `20260522-114731-workflow-try01-targeted-workflow-reference-basis-cleanup` | passed, stale-hash |
| workflow | `case-workflow-opt-out` | workflow restraint/opt-out | answer/public 수정 | 예 | `20260522-134058-workflow-try01-targeted-p5-opt-out-restraint` | no-validation, stale-hash |
| workflow | `case-workflow-tiny-restraint` | workflow negative/restraint | answer 수정 | 예 | pending | missing |
| workflow | `case-workflow-false-claim` | workflow honesty | answer 수정 | 예 | `20260522-115041-workflow-try01-targeted-workflow-reference-basis-cleanup` | passed, stale-hash |
| workflow | `case-workflow-parallel-ownership` | actual subagent trace/handoff | answer 수정 | 예 | `20260522-115724-workflow-try01-targeted-workflow-final-sync-check` | passed, stale-hash |
| workflow | `case-workflow-critical-path-delegation-restraint` | workflow critical-path restraint | answer 수정 | 예 | pending | missing |
| workflow | `case-workflow-design-no-meta-tail` | workflow output-shape restraint | answer 수정 | 예 | pending | missing |
| plugin | `case-plugin-p5-workflow-integrity` | workflow integrity, plugin/cache/source honesty | 추가 | 예 | `20260522-134130-plugin-try01-targeted-p5-workflow-integrity` | failed, stale-hash |
| plugin | `case-plugin-trigger-routing` | plugin trigger routing restraint | answer 수정 | 예 | pending | missing |
| plugin | `case-plugin-reference-split` | source/runtime reference split | answer 수정 | 예 | pending | missing |
| plugin | `case-plugin-packaging-sync` | packaging/cache/source traceability | answer 수정 | 예 | pending | missing |

현재-file 기준에서는 stale-hash 또는 missing인 run을 완료 근거로 세지 않는다. `goal_context` 안의 승인 문구만으로는 escalation reviewer가 외부 runner 데이터 전송을 승인하지 않았으므로, targeted eval 재실행은 정상 채팅 메시지의 명시 승인 후 진행한다.

## P4 Direct vs P5 Integration

- P4 direct: `case-response-django-orm-service`, `case-response-django-ninja-endpoint`, `case-response-django-web-page`, `case-response-python-boundaries`, `case-response-clean-code-refactor-boundary`, `case-response-test-suite-strategy`, `case-response-tdd-loop-selection`, `case-code-django-orm-service`, `case-code-web-detail`, `case-code-python-state`, `case-code-coupon-tdd`.
- P5 integration: `case-response-order-create`, `case-code-order-api`, `case-workflow-positive-composite`는 risky DB/API/implementation 일부를 검증하지만 server-rendered web, Python typing, Clean Code, TDD/Test mechanics까지 한 구현 handoff로 묶지는 않는다.
- Negative/restraint: 작은 rename과 tiny assertion은 있지만, one-line Django Web edit restraint가 명시 case로 없다.

## Gap

| gap | 분류 | 설명 | 조치 |
|---|---|---|---|
| P5 구현 handoff 전용 case 부족 | case | 기존 mixed case는 주문 API 또는 web/typing 일부만 다루며, Django service/migration, Ninja adapter, server-rendered web, Python typing, Clean Code, TDD/Test, architecture-api/db handoff를 한 답변에서 평가하지 않는다. | response positive case 추가 |
| one-line web edit restraint 부족 | case | 작은 rename과 tiny assertion은 있으나 one-line Django Web edit에서 workflow/subagent/TDD/DB/API 과적용을 막는 명시 평가가 없다. | response negative case 추가 |
| `case-code-order-api` pass run 부재 | model-variance | 기존 code-backed API case의 유일한 run은 sandbox/app-server 초기화 실패와 noCodeProduced로 failed다. 이번 response 추가와 별개로 targeted 재실행 또는 승인 필요 여부를 확인해야 한다. | 수정 없이 재실행 후보 |
| code bucket full-role omnibus 부재 | case 아님 | `code/eval_goal.md`는 `case_role: implementation_supporting` case와 direct implementation case를 분리하고, supporting case를 DDD/P5 직접 confidence로 세지 말라고 한다. 따라서 full-role handoff는 response/workflow/plugin P5 case가 담당하고, code bucket은 실제 코드 변경 surface별 supporting evidence를 제공한다. | 새 code omnibus case를 추가하지 않고 inventory와 targeted rerun evidence로 관리 |

## 누설/과장 위험

Public case에는 answer schema field, private scoring text, 이전 run finding을 넣지 않는다. Answer oracle에는 내부 평가 기준을 두되 runtime/public prompt로 노출하지 않는다. 새 positive case는 실제 파일 수정, 테스트 실행, subagent 실행을 금지해 false claim hard gate를 명확히 한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

skill-creator 리뷰: `Hypatia` subagent가 `case-code-order-api` pass run 부재, `case-response-web-typing` source basis 약함, P5 전용 Django implementation integration gate 부재를 지적했다. 메인 판단은 이 중 P5 전용 response case 추가를 즉시 수정 대상으로 채택하고, `case-code-order-api`는 별도 targeted rerun/evidence gap으로 유지한다.

독립 integration 리뷰: `Meitner` subagent가 P5 integration coverage 미확립, `case-code-order-api` pass evidence 부재, plugin trigger routing evidence 부족을 지적했다. 메인 판단은 response P5 integration case와 one-line web restraint case를 추가해 현재 목표의 case gap을 먼저 닫고, code/plugin run evidence는 후속 targeted eval 대상으로 남긴다.

후속 integration 리뷰: `Feynman` subagent가 현재-file targeted pass run 부재를 Blocker로, plugin/workflow subagent trace acceptable mode undercheck를 Major로, code bucket full-role omnibus 부재를 Major 후보로 지적했다. trace acceptable mode undercheck는 plugin evaluator plan에서 수정했고, code bucket full-role omnibus는 `code/eval_goal.md`의 supporting/direct case 분리 원칙과 충돌하므로 새 case 없이 reclassify한다.

리뷰 결과: Blocker 1, Major 0, 열린 Minor 0
