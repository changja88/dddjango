수정 대상: case
원인 분류: case

# plugin reference-split path and claim 분석

## 문제

`case-plugin-reference-split` targeted run `20260522-152035-plugin-try01-targeted-p5-reference-split-negative-conditions`에서 with-ddjango 응답이 `/private/tmp/dddjango-eval-workspaces/...` 절대 경로 링크를 다수 출력했고, reference routing 문맥의 `red-green-refactor`/`validation` 표현이 validator/eval 실행 주장으로 잡혔다.

Public prompt가 "직접 연결된 reference 링크 목록"을 요구해 모델이 임시 workspace 절대 링크를 만들도록 유도한 것이 직접 원인이다. 또한 generic execution claim detector가 reference routing 문장을 실행 완료 주장으로 오탐할 수 있다.

## 영향

P5 public leakage와 validation honesty gate가 실패한다. plugin reference split 평가는 runtime bundle-relative path와 reference load condition을 보면 충분하며, 실제 파일 링크나 validator/eval 실행 주장을 유도하면 안 된다.

## 조치 방향

- public prompt를 runtime bundle 기준 상대 경로만 요구하도록 바꾼다.
- answer oracle에 absolute local/temp workspace link 금지와 unsupported validator/eval/browser/Serena claim 금지를 추가한다.
- `validate_eval_run.py`가 reference routing/load-condition 문장을 generic execution claim으로 오탐하지 않도록 한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 순차 fallback. 실패 run artifact와 validator finding을 직접 확인했다.

skill-creator 리뷰: 해당 없음. 이 문서는 plugin eval case/evaluator 보강 분석이다.
