# dddjango 플러그인 개발 반복 절차

이 문서는 `dddjango` 플러그인을 개발하고 개선할 때 따르는 반복 흐름만 정의한다. 문서 위치, 파일명, 첫 줄 `수정 대상:`, 문서 언어, 평가지 폴더 역할 같은 강제 제약은 [constraint_rules.md](/Users/hyun/Desktop/dddjango/workspace/plan/constraint_rules.md)를 따른다.

## 문서 사용법

- `Phase`는 위에서 아래로 진행하는 최상위 실행 흐름이다.
- `Checklist`는 각 Phase에서 참조하는 세부 점검표이며, 단독 실행 순서가 아니다.
- `Failure Loop`는 평가나 report 실패가 있을 때만 진입한다.
- `Validation Gate`는 변경 후 실행 범위를 정하는 검증 게이트다.
- 분석/계획 문서 작성 위치, 파일명, 첫 줄, 언어, 평가지 구조는 여기서 반복 설명하지 않고 `constraint_rules.md`를 따른다.

## A. 최상위 실행 흐름

| Phase | 체크 | 목적 | 먼저 할 일 | 참조 체크리스트 | 다음 단계 |
|---|---|---|---|---|---|
| P1 | [ ] | 기준 확인 | 개선 대상과 reference 기준/gap을 확인한다. | C-REF | 기준이 부족하면 reference 계획, 충분하면 P2 |
| P2 | [ ] | skill 반영 확인 | skill이 reference 결정을 runtime 규칙으로 반영했는지 확인한다. | C-SKILL-SOURCE, C-SKILL-RUNTIME | 충돌하면 skill 계획, 충분하면 P3 |
| P3 | [ ] | 책임 경계 확인 | skill 간 routing, handoff, subagent 책임을 확인한다. | C-SKILL-BOUNDARY | 겹치면 primary owner 결정, 충분하면 P4 |
| P4 | [ ] | eval 준비 확인 | 개별 skill과 workflow 평가가 목적을 검증하는지 확인한다. | C-EVAL-SKILL, C-EVAL-WORKFLOW | eval gap이면 eval 계획, 충분하면 P5 |
| P5 | [ ] | report 확인 | 최신 평가 결과와 HTML report를 확인한다. | C-REPORT | 실패가 있으면 F1, 없으면 P6 |
| P6 | [ ] | 반복 검증 | 변경 범위에 맞는 검증을 실행하고 기록한다. | V-GATE | 통과 또는 blocker 기록 |

## B. Phase 실행 상세

### P1. 기준 확인

목적:

- 이번 반복이 따라야 할 source reference와 gap 상태를 확정한다.

시작 조건:

- 개선 대상 skill, eval bucket, reference area, failure family 중 하나 이상이 정해져 있다.

해야 할 일:

- [ ] 개선 대상을 한 문장으로 정한다.
- [ ] C-REF를 실행한다.

분기:

- [ ] reference가 부족하면 skill이나 eval을 고치지 않고 reference 개선 계획을 만든다.
- [ ] reference가 충분하면 P2로 진행한다.

산출물:

- [ ] 기준 reference 목록
- [ ] gap, provisional, fallback 여부
- [ ] 다음 수정 대상 후보

### P2. Skill 반영 확인

목적:

- skill이 reference 결정을 runtime 실행 규칙으로 바꿔 담았는지 확인한다.

시작 조건:

- 기준 reference가 충분하거나 fallback 범위가 명확하다.

해야 할 일:

- [ ] C-SKILL-SOURCE를 실행한다.
- [ ] C-SKILL-RUNTIME을 실행한다.

분기:

- [ ] skill이 reference와 충돌하면 skill 개선 계획을 만든다.
- [ ] runtime cache 차이가 있으면 sync 필요로 분류한다.
- [ ] skill 반영이 충분하면 P3로 진행한다.

산출물:

- [ ] skill 수정 필요 여부
- [ ] runtime-sync 필요 여부
- [ ] reference gap 재분류 여부

### P3. 책임 경계 확인

목적:

- skill 간 책임과 handoff가 subagent 작업에 맞게 분리되어 있는지 확인한다.

시작 조건:

- skill의 기준 반영 상태가 확인되어 있다.

해야 할 일:

- [ ] C-SKILL-BOUNDARY를 실행한다.

분기:

- [ ] 책임이 겹치면 primary owner와 handoff 조건을 정한다.
- [ ] 책임 경계가 충분하면 P4로 진행한다.

산출물:

- [ ] skill별 owner와 제외 조건
- [ ] handoff 조건
- [ ] workflow 조율 필요 여부

### P4. Eval 준비 확인

목적:

- 개별 skill과 skill 조합을 평가할 수 있는 case와 answer가 준비되어 있는지 확인한다.

시작 조건:

- skill 목적, 책임, routing이 확인되어 있다.

해야 할 일:

- [ ] C-EVAL-SKILL을 실행한다.
- [ ] C-EVAL-WORKFLOW를 실행한다.

분기:

- [ ] 개별 skill 평가가 부족하면 case 또는 answer 개선 계획을 만든다.
- [ ] skill 연계 평가가 부족하면 workflow eval 개선 계획을 만든다.
- [ ] 평가 준비가 충분하면 P5로 진행한다.

산출물:

- [ ] 개별 skill 평가 gap
- [ ] workflow 평가 gap
- [ ] case, answer, evaluator 수정 필요 여부

### P5. Report 확인

목적:

- 최신 평가 결과를 보고 실패 원인을 추적할 수 있는지 확인한다.

시작 조건:

- 평가 결과나 report가 생성되어 있다.

해야 할 일:

- [ ] C-REPORT를 실행한다.

분기:

- [ ] 실패가 있으면 F1로 진입한다.
- [ ] report나 latest 결과가 불명확하면 tooling 문제로 분류한다.
- [ ] 실패가 없으면 P6로 진행한다.

산출물:

- [ ] 최신 run id
- [ ] 실패 case와 variant
- [ ] report 또는 tooling 문제 여부

### P6. 반복 검증

목적:

- 변경 범위에 맞는 검증을 실행하고 다음 반복 여부를 결정한다.

시작 조건:

- 수정이 끝났거나 실패가 없음을 확인했다.

해야 할 일:

- [ ] V-GATE를 실행한다.

분기:

- [ ] 검증이 통과하면 필요한 경우 더 넓은 범위로 확장한다.
- [ ] 검증이 실패하면 F1로 진입한다.
- [ ] 반복해도 안정되지 않으면 blocker 또는 model variance로 분류한다.

산출물:

- [ ] 실행한 검증
- [ ] 실행하지 못한 검증과 이유
- [ ] 남은 risk 또는 blocker

## C. Failure Loop

실패가 없으면 이 절은 건너뛴다.

| Failure Step | 체크 | 조건 | 해야 할 일 | 참조 체크리스트 | 다음 단계 |
|---|---|---|---|---|---|
| F1 | [ ] | eval 또는 report 실패가 있다. | 실패 근거를 확인한다. | C-FAILURE-TRIAGE | 수정 대상이 정해지면 F2 |
| F2 | [ ] | 수정 대상이 분류되었다. | 대상별 개선 계획을 만들고 좁게 수정한다. | C-FAILURE-FIX | 수정 후 F3 |
| F3 | [ ] | 수정이 끝났다. | targeted, bucket, full 순서로 필요한 만큼 검증을 넓힌다. | V-GATE | 통과하면 P1 또는 종료 |

## D. 세부 체크리스트

### C-REF. Reference 기준 점검

사용 시점:

- P1에서 기준 reference와 gap 상태를 확인할 때 사용한다.

결과:

- `reference 충분`, `reference 개선 필요`, `fallback/provisional 유지` 중 하나로 결론낸다.

점검:

- [ ] 관련 reference area를 정한다.
- [ ] `workspace/reference/<area>/reference/final.md`가 현재 판단 기준으로 충분한지 확인한다.
- [ ] 필요한 경우 `review.md`, `internal.md`, `external.md`에서 gap, conflict, provisional 상태를 확인한다.
- [ ] 전용 reference가 없는 영역은 fallback 또는 provisional 상태를 명확히 한다.
- [ ] reference 자체가 부족하면 skill이나 eval을 먼저 고치지 않는다.

### C-SKILL-SOURCE. Skill의 Reference 반영도 점검

사용 시점:

- P2에서 skill이 source reference를 제대로 반영했는지 확인할 때 사용한다.

결과:

- `충돌 없음`, `skill 수정 필요`, `reference gap`, `runtime-sync 필요` 중 하나로 결론낸다.

점검:

- [ ] `SKILL.md`의 실행 규칙이 reference의 핵심 판단을 빠뜨리지 않는다.
- [ ] bundled `references/*.md`가 긴 기준을 적절히 분리하고 있다.
- [ ] runtime skill에는 source reference 원문을 과하게 복사하지 않고 실행 규칙만 요약되어 있다.
- [ ] source authoring 경로를 runtime-facing allowed path처럼 노출하지 않는다.
- [ ] provisional 또는 fallback source를 사용하는 skill은 그 상태를 명확히 표시한다.
- [ ] reference 변경 후 runtime cache sync 필요 여부를 확인한다.

### C-SKILL-RUNTIME. `SKILL.md` 목적과 Routing 점검

사용 시점:

- P2에서 runtime-facing skill 문서가 에이전트 실행에 충분한지 확인할 때 사용한다.

결과:

- `routing 충분`, `description 수정 필요`, `body rule 수정 필요`, `reference 분리 필요` 중 하나로 결론낸다.

점검:

- [ ] frontmatter `description`이 positive trigger를 분명히 드러낸다.
- [ ] frontmatter `description`이 negative routing 또는 prefer 조건을 드러낸다.
- [ ] 본문은 runtime에서 바로 실행 가능한 규칙 중심이다.
- [ ] 긴 설명, 세부 기준, 체크리스트는 `references/*.md`로 분리되어 있다.
- [ ] 실제 실행하지 않은 command, test, review, subagent 작업을 주장하지 않는다.
- [ ] skill 폴더에 README, changelog, quick reference 같은 보조 문서를 추가하지 않는다.

### C-SKILL-BOUNDARY. Skill 책임 분리 점검

사용 시점:

- P3에서 skill 간 routing, handoff, subagent 책임을 확인할 때 사용한다.

결과:

- `책임 분리 충분`, `primary owner 필요`, `handoff 수정 필요`, `workflow 조율 필요` 중 하나로 결론낸다.

점검:

- [ ] 각 skill이 처리해야 하는 요청 유형이 명확하다.
- [ ] 각 skill이 처리하지 말아야 하는 요청 유형이 명확하다.
- [ ] 다른 skill로 넘겨야 하는 handoff 조건이 명확하다.
- [ ] architecture, implementation, test, source audit, workflow skill의 책임이 겹치지 않는다.
- [ ] 겹치는 책임이 있으면 어느 skill이 primary owner인지 정한다.
- [ ] 복합 작업은 `workflow-dddjango-subagents`가 조율하고, 개별 skill이 자기 역할만 맡도록 한다.

### C-EVAL-SKILL. 개별 Skill 평가 점검

사용 시점:

- P4에서 개별 skill 평가가 목적 달성을 검증하는지 확인할 때 사용한다.

결과:

- `개별 평가 충분`, `case 수정 필요`, `answer 수정 필요`, `reference basis 수정 필요` 중 하나로 결론낸다.

점검:

- [ ] 각 skill 또는 skill group에 대응하는 eval bucket과 case가 있다.
- [ ] public case가 실제 사용자가 할 법한 요청으로 작성되어 있다.
- [ ] public case가 private answer나 oracle 내용을 누설하지 않는다.
- [ ] answer oracle이 skill의 목적 달성 여부를 직접 평가한다.
- [ ] answer oracle이 불가능하거나 과도한 요구를 하지 않는다.
- [ ] reference basis가 실제 판단 근거와 연결되어 있다.

### C-EVAL-WORKFLOW. Skill 연계와 Subagent Workflow 평가 점검

사용 시점:

- P4에서 skill 조합과 subagent workflow 평가가 준비되어 있는지 확인할 때 사용한다.

결과:

- `workflow 평가 충분`, `delegation 평가 gap`, `fallback 평가 gap`, `role ownership 평가 gap` 중 하나로 결론낸다.

점검:

- [ ] workflow eval이 delegation, fallback, opt-out, false-claim 상황을 구분한다.
- [ ] subagent 역할별 책임과 산출물이 평가 기준에 반영되어 있다.
- [ ] 실제 subagent를 쓰지 않은 경우 sequential fallback을 허위로 subagent 실행처럼 말하지 않도록 평가한다.
- [ ] review-focused, risky-write, parallel ownership 같은 복합 상황이 별도 case로 검증된다.
- [ ] skill 간 handoff가 누락되거나 과도하게 겹치는 경우를 잡아낼 수 있다.

### C-REPORT. 평가 결과와 HTML Report 점검

사용 시점:

- P5에서 최신 평가 결과를 확인할 때 사용한다.

결과:

- `report 충분`, `latest pointer 문제`, `report aggregation 문제`, `failure evidence 불명확` 중 하나로 결론낸다.

점검:

- [ ] targeted eval, bucket eval, full eval 중 현재 범위에 맞는 결과를 확인한다.
- [ ] 각 eval run의 `analysis/report.html`이 생성된다.
- [ ] latest 또는 latest-valid 포인터가 최신 유효 결과를 가리킨다.
- [ ] report가 raw output, stderr, oracle failure, validation failure를 구분해서 보여준다.
- [ ] 어떤 case와 variant가 실패했는지 바로 추적할 수 있다.

### C-FAILURE-TRIAGE. 평가 실패 원인 분류

사용 시점:

- F1에서 실패 근거를 확인하고 수정 대상을 정할 때 사용한다.

결과:

- `reference`, `skill`, `case`, `answer`, `evaluator`, `runtime-sync`, `report`, `model-variance`, `process`, `cleanup`, `tooling`, `none` 중 하나로 분류한다.

점검:

- [ ] 실패 bucket, case, variant, run id를 확인한다.
- [ ] raw output, stderr, answer oracle, evaluator error, report 중 실제 실패 근거를 확인한다.
- [ ] 모델 변동성인지, 평가 도구 문제인지, 실제 plugin 품질 문제인지 구분한다.
- [ ] 수정 대상이 정해지기 전에는 skill을 먼저 고치지 않는다.

### C-FAILURE-FIX. 수정 대상별 처리 규칙

사용 시점:

- F2에서 분류된 수정 대상에 맞게 개선 계획을 만들 때 사용한다.

결과:

- 수정할 파일군과 검증 방법이 좁혀져 있다.

점검:

- [ ] reference gap이면 reference를 먼저 고친다.
- [ ] skill 작성 문제이면 skill 목적, routing, runtime rule을 고친다.
- [ ] case 또는 answer 문제이면 public prompt와 evaluator-only 기준을 분리해서 고친다.
- [ ] evaluator, report, runner 문제이면 스크립트와 관련 unit test를 함께 고친다.
- [ ] runtime-sync 문제이면 source와 runtime cache 차이를 확인한다.
- [ ] model variance이면 rerun evidence 또는 blocker를 남긴다.

## E. Validation Gate

### V-GATE. 반복 검증 순서

사용 시점:

- P6 또는 F3에서 변경 범위에 맞는 검증을 정할 때 사용한다.

결과:

- 검증이 통과했거나, 실행하지 못한 검증과 남은 risk가 기록되어 있다.

검증 순서:

| 범위 | 실행 조건 | 대표 검증 |
|---|---|---|
| 문서/제약 | `workspace/plan/**` 변경 | `validate_plan_constraints.py`와 관련 테스트 |
| skill/reference/eval 구조 | skill, reference, eval 구조 변경 | `validate_skill_docs.py --phase all` |
| eval pack | case, answer, fixture, manual protocol 변경 | `validate_eval_bucket_pack.py` |
| script | runner, evaluator, report, validator 변경 | 관련 unit test |
| targeted eval | 실패 family가 좁을 때 | 해당 case만 재실행 |
| bucket eval | targeted eval이 통과했을 때 | 해당 bucket 전체 재실행 |
| full eval | bucket 단위가 안정됐을 때 | 전체 평가 재실행 |

체크리스트:

- [ ] 변경 범위에 맞는 최소 검증을 먼저 실행한다.
- [ ] targeted eval이 통과하면 관련 bucket eval로 넓힌다.
- [ ] bucket eval이 안정되면 full eval로 넓힌다.
- [ ] full eval에서만 실패하면 병렬 실행, generated artifact, evaluator nondeterminism, report aggregation 문제를 먼저 의심한다.
- [ ] 실행한 검증과 실행하지 못한 검증을 기록한다.
- [ ] generated run artifact는 커밋하지 않는다.
