수정 대상: skill
원인 분류: skill

# workflow subagent honesty Minor 분석

## 문제

P5 subagent workflow 정직성 독립 리뷰에서 core rule은 존재하지만 다음 Minor가 남았다.

- `agents/openai.yaml` default prompt가 실제 subagent 실행 승인, bounded non-critical sidecar, result collection 조건을 충분히 드러내지 않는다.
- 실제 subagent를 spawn한 뒤 최종 통합 전에 확인할 concrete status ledger가 없어 긴 workflow에서 model variance로 누락될 수 있다.
- `delegation-rules.md`는 subagent honesty를 다루지만 validator/eval/browser/Serena 같은 broader validation honesty는 `SKILL.md`와 `integration-checklist.md`에만 있어, delegation 판단 reference만 읽는 경우 누락 위험이 있다.

## 영향

Blocker나 Major는 아니지만 P5 종료 기준은 열린 Minor 0이다. 따라서 runtime-visible metadata와 delegation reference를 좁게 보강해 정직성 규칙을 더 낮은 자유도로 만든다.

## 수정 방향

- `agents/openai.yaml` default prompt에 approval, bounded sidecar, result collection 조건을 짧게 반영한다.
- `SKILL.md`와 `delegation-rules.md`에 spawned subagent status ledger 필드를 추가한다.
- `delegation-rules.md`에 tests, validators, evals, browser checks, Serena, subagent review의 false claim 금지 문장을 추가한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 3

Subagent 리뷰/순차 fallback: skill-creator 관점 subagent가 위 3개 Minor를 보고했다.

skill-creator 리뷰: progressive disclosure를 해치지 않도록 장문 절차가 아니라 final integration 직전 확인 ledger와 default prompt 보강만 적용한다.
