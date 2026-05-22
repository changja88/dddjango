수정 대상: skill
원인 분류: skill

## 배경

P4 리뷰에서 `implementation-django-web` runtime `SKILL.md`가 `validator-visible label`이라는 평가기 관점 표현과 일부 exact acceptance phrase를 직접 담고 있다는 지적이 나왔다.

## 문제

- runtime skill은 제품/구현 기준으로 안내해야 하며 eval validator 관점의 label을 노출하면 validation integrity를 약화한다.
- 현재 `validate_skill_docs.py`도 exact phrase를 runtime skill 본문에 요구해 같은 문제를 유지한다.
- source reference는 같은 내용을 render/static acceptance 기준으로 표현하므로 skill 본문은 bundled reference를 안내하고 제품 기준만 요약하면 충분하다.

## 수정 방향

- `SKILL.md`에서 `validator-visible label` 표현을 제거한다.
- render/static acceptance 문장은 exact private label 나열이 아니라 source reference와 bundled reference의 제품 기준으로 바꾼다.
- `validate_skill_docs.py`는 exact phrase 강제가 아니라 제품 기준 group을 확인하도록 바꾼다.

## 리뷰 기록

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: skill-creator 관점 subagent가 runtime evaluator wording leakage를 Blocker로 보고했다.

skill-creator 리뷰: trigger Pass, purpose Pass, reference Major issue, progressive disclosure Pass, validation integrity Fail.
