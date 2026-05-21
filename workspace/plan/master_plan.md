# dddjango 플러그인 개발 절차

이 문서는 작업 순서만 다룬다. 위치, 파일명, 첫 줄 `수정 대상:`, 문서 언어, 평가지 폴더 역할 같은 강제 제약은 [constraint_rules.md](/Users/hyun/Desktop/dddjango/workspace/plan/constraint_rules.md)를 기준으로 한다.

## 0. 작업 유형 선택

필요한 흐름만 읽고 진행한다.

| 작업 유형 | 진행할 절차 |
|---|---|
| 평가 실패 대응 | 1, 2, 3, 4, 8 |
| reference 개선 | 1, 2, 3, 5, 8 |
| skill 책임 또는 routing 개선 | 1, 2, 3, 6, 8 |
| eval case 또는 answer 개선 | 1, 2, 3, 7, 8 |
| report, validator, runner 개선 | 1, 2, 3, 8 |
| 문서/정리/운영성 개선 | 1, 2, 3, 8 |

## 1. 시작 전 분류

- [ ] 이번 작업의 목적을 한 문장으로 적는다.
- [ ] 관련 bucket, case, reference area, skill 폴더를 확인한다.
- [ ] 한 번의 작업에서 다룰 failure family를 하나로 제한한다.
- [ ] 기록이 필요하면 `constraint_rules.md`에 맞는 `*_lv_up_plan` 위치를 선택한다.
- [ ] 강제 제약이 필요한 작업이면 `constraint_rules.md`를 먼저 확인한다.

## 2. 실패 증거 확인

평가가 실패하면 skill을 바로 수정하지 않고 증거부터 확인한다.

- [ ] 실패 bucket, case, variant, run id를 확인한다.
- [ ] raw output, stderr, oracle, report 중 실제 실패 근거를 확인한다.
- [ ] 모델 변동성인지, 평가 도구 문제인지, 실제 plugin 품질 문제인지 구분한다.
- [ ] 분석 문서를 작성한다면 `constraint_rules.md`의 위치와 첫 줄 형식을 따른다.
- [ ] 개선 계획을 작성한다면 같은 작업 식별자를 사용한다.

## 3. 수정 대상 결정

- [ ] 첫 번째 수정 대상은 `constraint_rules.md`의 `수정 대상:` 분류를 따른다.
- [ ] 대표 수정 위치는 `constraint_rules.md`의 수정 대상 표를 따른다.
- [ ] 수정 대상과 맞지 않는 파일은 고치지 않는다.
- [ ] 여러 대상이 필요하면 주된 대상 하나를 먼저 처리하고, 보조 대상은 본문에 남긴다.
- [ ] 같은 대상을 반복 수정해도 개선되지 않으면 blocker로 남긴다.

## 4. 평가 실패 대응 흐름

- [ ] 실패가 reference gap이면 reference를 먼저 보완한다.
- [ ] 실패가 skill 작성 문제이면 skill 목적, routing, runtime rule을 확인한다.
- [ ] 실패가 case 또는 answer 문제이면 public prompt와 evaluator-only 기준을 분리해서 확인한다.
- [ ] 실패가 evaluator, report, runner 문제이면 스크립트와 관련 테스트를 함께 확인한다.
- [ ] 실패가 runtime sync 문제이면 source와 runtime cache의 차이를 확인한다.
- [ ] 실패가 model variance이면 rerun evidence 또는 blocker를 남긴다.

## 5. Reference 점검

- [ ] `workspace/reference/<area>/reference/final.md`가 필요한 판단 근거를 제공한다.
- [ ] 필요한 경우 `review.md`, `internal.md`, `external.md`의 gap과 conflict를 확인한다.
- [ ] reference gap이 있으면 skill을 먼저 고치지 않는다.
- [ ] 전용 reference가 없는 영역은 provisional 또는 fallback 상태를 명확히 한다.
- [ ] runtime skill에는 source 문서를 그대로 복사하지 않고 필요한 실행 규칙만 요약한다.

## 6. Skill 점검

- [ ] 이 skill이 처리해야 하는 요청 유형이 명확하다.
- [ ] 이 skill이 처리하지 말아야 하는 요청 유형이 명확하다.
- [ ] 다른 skill로 넘겨야 하는 handoff 조건이 명확하다.
- [ ] `SKILL.md` frontmatter `description`이 positive trigger와 negative routing을 드러낸다.
- [ ] body는 runtime에서 실행 가능한 규칙 중심이다.
- [ ] 긴 설명과 세부 기준은 `references/*.md`로 분리되어 있다.
- [ ] 실제 실행하지 않은 command, test, review, subagent 작업을 주장하지 않는다.
- [ ] skill 폴더에 README, changelog, quick reference 같은 보조 문서를 추가하지 않는다.

## 7. Eval 점검

- [ ] public case와 answer 파일이 1:1로 대응한다.
- [ ] public case가 private answer나 oracle 내용을 누설하지 않는다.
- [ ] public case가 특정 정답 문구를 과하게 유도하지 않는다.
- [ ] answer oracle이 필요한 관찰 항목을 빠뜨리지 않는다.
- [ ] answer oracle이 불가능하거나 과도한 요구를 하지 않는다.
- [ ] workflow eval은 delegation, fallback, opt-out, false-claim, review-focused 상황을 구분한다.
- [ ] report는 최신 run과 latest-valid 결과를 일관되게 보여준다.

## 8. 검증과 완료

- [ ] 문서/제약 변경이면 `validate_plan_constraints.py`와 관련 테스트를 실행한다.
- [ ] skill/reference/eval 구조 변경이면 `validate_skill_docs.py --phase all`을 실행한다.
- [ ] eval pack 변경이면 `validate_eval_bucket_pack.py`를 실행한다.
- [ ] 스크립트 변경이면 관련 unit test를 실행한다.
- [ ] 필요한 경우 targeted eval, bucket eval, full eval 순서로 넓힌다.
- [ ] 실행한 검증과 실행하지 못한 검증을 기록한다.
- [ ] generated run artifact를 커밋 대상에서 제외한다.

완료 판단:

- [ ] 실패 원인이 기록되어 있다.
- [ ] 수정 범위가 원인 분류와 일치한다.
- [ ] 필요한 검증이 통과했거나 미실행 사유가 있다.
- [ ] 남은 risk 또는 blocker가 기록되어 있다.
