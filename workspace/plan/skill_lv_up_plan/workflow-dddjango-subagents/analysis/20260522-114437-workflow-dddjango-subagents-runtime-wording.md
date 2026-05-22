수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# workflow runtime wording P4 분석

## 배경

최종 독립 리뷰에서 runtime-facing workflow 문서가 내부 평가 용어와 작성 경로를 직접 노출한다는 Major가 나왔다. P4는 public case 누설뿐 아니라 runtime/public surface의 정직성도 확인해야 하므로, workflow runtime guidance는 내부 평가 세부 용어를 일반화해야 한다.

## 원인

원인 분류는 `skill`이다. `SKILL.md`와 bundled `integration-checklist.md`가 workflow 중 발견한 validation/report/run-variance 문제를 owning follow-up으로 넘기라는 의도는 맞지만, 내부 eval 용어와 plan path를 그대로 노출한다.

## 수정 판단

- 내부 평가 용어는 `validation-pack`, `scoring`, `report`, `run-variance` 같은 product-facing 범주로 일반화한다.
- Runtime 문서에서 구체적인 plan path와 first-line literal을 제거하고 project planning constraints를 따르라고만 안내한다.
- Source/runtime boundary와 validation honesty 의도는 유지한다.

## 검증

- `rg`로 runtime skill bundle에서 내부 평가 용어와 plan path 노출 제거 확인
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
