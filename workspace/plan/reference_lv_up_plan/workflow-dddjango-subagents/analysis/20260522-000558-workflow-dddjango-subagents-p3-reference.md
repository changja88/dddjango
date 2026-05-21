수정 대상: reference
원인 분류: p3-source-reference-taxonomy-followup

# workflow-dddjango-subagents P3 reference 후속 분석

## 범위

- source reference: `workspace/reference/workflow-dddjango-subagents/reference/final.md`
- 관련 constraint: `workspace/plan/constraint_rules.md`
- 관련 skill: `dddjango/skills/workflow-dddjango-subagents/`

## 발견 사항

`workspace/reference/workflow-dddjango-subagents/reference/final.md`의 eval 문제 분류 section은 분석 첫 줄 값을 설명하면서 일부 값에서 `수정 대상:` prefix를 생략한다. `constraint_rules.md`는 모든 분석 문서 첫 줄이 `수정 대상: <허용 값>` 형식이어야 한다고 요구한다.

Runtime skill과 bundled reference는 prefixed form을 사용하므로 현재 runtime 동작은 constraint와 맞는다. 이 문제는 source reference 문구의 정합성 문제이며, skill을 왜곡해서 해결할 대상이 아니다.

## 영향

- Source reference를 직접 읽는 사람이 `answer`, `evaluator`, `report`, `model-variance`처럼 prefix 없는 첫 줄을 허용된 형식으로 오해할 수 있다.
- Plan constraint validator는 prefix 없는 첫 줄을 통과시키지 않으므로 source reference와 validator 사이의 설명 불일치가 생긴다.

## 수정 내용

별도 reference 개선 계획을 작성하고 `workspace/reference/workflow-dddjango-subagents/reference/final.md`의 eval 문제 분류 section을 constraint와 맞췄다.

허용 first-line 예시는 다음 prefixed form으로 정리해야 한다.

- `수정 대상: case`
- `수정 대상: answer`
- `수정 대상: evaluator`
- `수정 대상: report`
- `수정 대상: model-variance`

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: skill-creator 관점 read-only subagent가 source reference taxonomy inconsistency를 Major로 보고했다. 메인 통합 판단은 runtime skill 수정 대상이 아니라 reference follow-up으로 분류한다.

skill-creator 리뷰: skill progressive disclosure와 validation integrity 관점에서 source reference와 constraint wording의 불일치가 후속 reference 정리 대상임을 확인했다.

## 리뷰 결과

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Runtime skill과 source reference가 모두 constraint와 맞는 prefixed form을 사용한다.
