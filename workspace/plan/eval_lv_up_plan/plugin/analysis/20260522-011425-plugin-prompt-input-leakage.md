수정 대상: evaluator
원인 분류: evaluator

# prompt-input private material leakage 분석

## 문제

독립 `skill-creator` 관점 리뷰에서 with-ddjango prompt-input artifact 검증이 private evaluation material 노출 방지 claim을 충분히 뒷받침하지 못한다는 Blocker가 나왔다.

현재 validator는 prompt-input artifact의 존재와 JSON shape, 금지 local path marker는 확인하지만, prompt-input 내부에 evaluator-only marker나 private eval sentinel이 들어간 경우를 직접 실패시키는 회귀 테스트가 부족하다.

## 영향

- P4 기준 3인 public/runtime prompt-input leakage 방지 claim이 약하다.
- case/answer가 누설되지 않았더라도 prompt-input artifact validation이 private material 노출을 놓칠 수 있다.

## 수정 방향

- prompt-input artifact 전용 leakage 검증을 추가한다.
- 과도한 generic path scan은 prompt-input에 정상 포함되는 시스템/개발자 지침 때문에 false positive 위험이 있으므로, evaluator-only marker와 private eval sentinel 같은 validator-only private material marker를 좁게 검사한다.
- `test_validate_eval_run.py`에 prompt-input private sentinel 회귀 테스트를 추가한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: skill-creator 관점 subagent가 prompt-input leakage validator gap을 Blocker로 보고했다. 본 분석은 해당 Blocker를 닫기 위한 후속이다.

skill-creator 리뷰: validation integrity 관점에서 prompt-input artifact가 private evaluation material leakage hard gate를 뒷받침해야 한다는 지적을 채택한다.
