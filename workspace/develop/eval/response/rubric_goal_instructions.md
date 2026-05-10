# Rubric Goal Instructions

이 문서는 rubric 작성 goal에서 참조하는 실행 지침이다. Goal objective에는 짧은 목표와 이 파일 경로만 적고, 자세한 작업 규칙은 이 문서를 따른다.

## 범위

`workspace/develop/eval/response/rubrics` 안의 skill별 rubric 파일을 작성한다. 단, `common_rubric.md`는 작성 대상에서 제외한다.

사용할 기준 문서는 다음과 같다.

- 공통 rubric 및 템플릿: `workspace/develop/eval/response/rubrics/common_rubric.md`
- 제품 계약 문서: `workspace/docs`
- reference corpus: `workspace/reference`
- 진행 상태 문서: `workspace/develop/plan.md`

이 goal은 다음 범위를 함께 다룬다.

- `plan.md` 1단계의 개별 skill rubric
- `plan.md` 4단계의 `workflow-dddjango-subagents_rubric.md`

작성 순서는 먼저 `plan.md` 1단계 체크리스트를 따르고, 그 다음 4단계 workflow rubric을 작성한다.

## 실행 규칙

- 문서는 반드시 한 개씩 작성한다.
- 현재 rubric이 completed, blocked, accepted-exception 중 하나가 되기 전에는 다음 rubric을 시작하지 않는다.
- 이미 유효한 내용이 있는 rubric은 기본적으로 다시 쓰지 않고, 먼저 리뷰한 뒤 필요한 부분만 수정한다.
- 각 rubric이 completed, blocked, accepted-exception 중 하나가 되는 즉시 `workspace/develop/plan.md`를 갱신한다.
- 실제로 수행하지 않은 테스트, 검증, 리뷰, subagent 실행을 완료했다고 말하지 않는다.
- 리뷰는 기본적으로 동일 agent의 네 관점 self-review다. 실제 subagent를 실행한 경우에만 subagent review라고 부른다.
- 완료 상태는 의도가 아니라 파일 내용을 다시 확인한 뒤에만 표시한다.

## Rubric별 필수 조건

각 rubric은 `common_rubric.md`의 `Per-Skill Rubric Template` 구조를 따르고, 다음 내용을 포함해야 한다.

- skill scope와 responsibility boundary
- source status
- trigger와 anti-trigger examples
- skill-specific hard gates
- analytic criteria
- reference-derived additions
- required public fixtures
- private grader key notes
- reference loading expectations
- raw artifact checklist
- scenario tags
- do-not-penalize notes
- positive prompt와 negative prompt
- expected routing
- required reference coverage
- failure criteria
- related-skill routing과 conflict boundary
- 단순 작업에서 DDD, workflow, subagent를 과적용하지 않는 negative case

공통 rubric 내용을 장황하게 반복하지 않는다. 각 문서에는 해당 skill 고유의 책임, routing, reference, evaluation 세부사항만 추가한다.

## Public/Private 배치

각 rubric 안에서 public material과 private grader material의 위치를 명확히 분리한다.

- positive prompt와 negative prompt는 `Required Public Fixtures`에 둔다.
- expected routing, expected answer, scenario tags, applicable hard gates, scoring notes, failure criteria, must-not-do items는 `Private Grader Key Notes`에 둔다.
- required reference coverage는 `Reference-Derived Additions`와 `Reference Loading Expectations`에 반영한다.

Public eval material에는 expected routing, expected answer, private grader key, scoring key, hidden failure criteria를 노출하지 않는다.

## Language Policy

dddjango 평가 자료는 한국어 사용자 입력을 우선 검증한다. section heading, skill name, hard gate id, scenario tag, canonical technical term은 영어를 유지한다. 각 skill rubric의 public prompt에는 자연스러운 한국어, 한국어/영어 혼합 개발자식 표현, 구어적이거나 모호한 표현, 단순 작업에 DDD/workflow/subagent를 과적용하지 않아야 하는 negative case가 포함되어야 한다. Private Grader Key Notes에는 각 public prompt family의 expected routing, applicable hard gates, failure criteria를 둔다. Public material에는 prompt family의 private classification이나 expected route를 노출하지 않는다.

## 리뷰 루프

각 rubric은 다음 네 관점으로 리뷰한다.

- skill authoring과 validation integrity
- dddjango product/docs alignment
- routing, reference, protocol correctness
- Korean user coverage와 한영 혼합 prompt routing correctness

각 rubric은 아래 순서를 반복한다.

1. rubric 초안을 작성하거나 기존 내용을 검토한다.
2. 위 네 관점으로 리뷰 finding을 작성한다.
3. finding을 `blocking`, `major`, `minor`로 분류한다.
4. 수정 계획을 짧게 세운 뒤 rubric을 수정한다.
5. 같은 네 관점으로 다시 리뷰한다.
6. `blocking`, `major`, `minor` finding이 모두 0개가 될 때까지 반복한다.

실제 subagent를 실행할 수 있고 실행한 경우에만 subagent review라고 부른다.
실제 subagent를 실행하지 않은 경우에는 동일 agent의 네 관점 self-review라고
명시한다. 어떤 경우에도 실행하지 않은 agent review를 완료했다고 말하지 않는다.

리뷰 finding은 다음 기준으로 분류한다.

- `blocking`: hard gate 충돌, 필수 섹션 누락, public/private leakage, provisional misrepresentation, skill responsibility conflict, validation/review/subagent 실행에 대한 false claim
- `major`: trigger 또는 anti-trigger 불명확, reference coverage 부족, prompt coverage 부족, scenario tag 또는 hard gate mapping 부족, workflow 과적용 위험, core scored dimension의 evidence 부족
- `minor`: 표현 개선, 예시 보강, 중복 정리, scoring note 명확화, 비필수 clarity 개선

Rubric은 다음 조건을 모두 만족하면 completed로 본다.

- 필수 섹션과 필수 내용이 존재한다.
- applicable hard gates가 pass이거나 정당한 N/A다.
- applicable scored dimensions가 모두 3점 이상이다.
- core scored dimensions는 5점을 목표로 하되, 낮은 점수는 source limitation, provisional status, accepted trade-off로 정당화되어야 한다.
- blocking finding과 major finding이 0개다.
- minor finding이 0개다.
- 네 리뷰 관점 사이에 해결되지 않은 충돌 판단이 없다.

일반적인 minor finding은 accepted exception으로 넘기지 않는다. 표현 개선,
예시 보강, 중복 정리, scoring note 명확화 같은 minor는 수정한 뒤 다시
리뷰한다.

Source limitation, docs conflict, 상위 지침 충돌 때문에 completed 조건을
만족할 수 없으면, 해당 rubric을 `plan.md`에 blocked 또는
accepted-exception으로 기록하고 이유를 남긴다. 이 경우에도 남은 finding이
무엇이며 왜 문서 수정으로 해결할 수 없는지 구체적으로 기록한다.

## 제품 규칙

- Greenfield API 구현 표준은 Django Ninja다.
- DRF는 legacy review, DRF-to-Ninja migration, 비교, compatibility 맥락에서만 허용한다.
- 신규 표준으로 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`를 권장하지 않는다.
- Provisional skill은 fallback source와 limitation을 명시해야 한다.
- 현재 provisional skill은 docs가 바뀌지 않았다면 `architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web`이다.
- `workflow-dddjango-subagents`는 generic fallback이 아니라 `workspace/docs/workflow.md`를 source로 삼는다.
- `skill-creator`는 skill authoring과 validation integrity를 위한 protocol source이며, dddjango 제품 기준의 source of truth가 아니다.

## 검증

각 rubric 작성 후 다음을 수행한다.

- `rg -n "^## " <rubric-file>` 또는 동등한 heading check를 실행하거나 수동으로 수행한다.
- 파일이 비어 있지 않은지 확인한다.
- `workspace/develop/plan.md`를 갱신한다.

최종 점검에서 다음을 수행한다.

- `wc -l workspace/develop/eval/response/rubrics/*_rubric.md`
- 가능하면 `python3 workspace/scripts/validate_skill_docs.py --phase docs`
- 실행한 명령, 실행하지 못한 명령, 실행하지 못한 이유를 보고한다.

실행하지 않은 검증을 완료했다고 보고하지 않는다.

## 완료 보고

완료 보고에는 다음을 포함한다.

- completed, blocked, accepted-exception 파일 목록
- 파일별 리뷰 요약
- 남은 finding이 없는지, 또는 blocked/accepted-exception의 source limitation
- 검증 결과
- `plan.md` 갱신 내용
