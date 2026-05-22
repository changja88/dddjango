수정 대상: tooling
원인 분류: report, tooling

# P6 HTML report 최신성 분석

## 점검 범위

- `workspace/scripts/render_eval_review_html.py`
- `workspace/scripts/run_initial_eval.py`
- `workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/runs/`
- `workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/latest/report.html`
- `workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/latest-valid/report.html`

## 최신성 점검표

| bucket | latest full run | HTML report run id | latest alias | latest-valid 의도 | 문제 여부 |
|---|---|---|---|---|---|
| response | `20260522-175638-response-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |
| code | `20260522-175638-code-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |
| plugin | `20260522-175638-plugin-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |
| runtime | `20260522-175647-runtime-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |
| source | `20260522-175807-source-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |
| workflow | `20260522-175813-workflow-try01-full-current-baseline` | 일치 | 해당 run report로 redirect | 검증 통과 full run 없음, placeholder | 닫힘 |

## 확인된 gap

1. 실패 case 상세 화면에서 raw response와 answer-oracle 평가는 본문으로 보이지만, `stderr`, `command`, `exit`, answer-oracle raw/stderr/command/exit 같은 원본 artifact 링크가 variant/evaluator별로 노출되지 않았다. P6의 "raw output, stderr, evaluator 결과, answer-oracle 근거로 추적 가능" 조건을 HTML에서 직접 증명하기 어려웠다.
2. `run_initial_eval.py`는 bucket 실행 중 `run_eval_bucket.py`, `evaluate_eval_run.py`, `validate_eval_run.py` 중 하나가 실패하면 이후 명령을 중단했다. 이 경우 raw artifact가 생성되어 있어도 bucket report 렌더가 생략되어 eval-all 중간 실패 시 report와 실패 근거가 최신 alias에 반영되지 않을 수 있었다.
3. 첫 수정 후 response 최신 report가 `RUN_VALIDATION.json` 생성 전 렌더되어 `validation: missing`을 보여주는 stale report가 확인되었다. best-effort 렌더 전 validator 실행과 재렌더로 닫았다.
4. answer YAML의 `failure_modes`, `leakage_checks`, `evidence_required` 같은 evaluator-only 기준이 HTML payload에 들어가는 validation-integrity 위험이 확인되었다. P6 추적성을 위해 answer-oracle/evaluator artifact 링크는 유지하되, answer YAML 기준 필드는 report data에서 제거했다.
5. 현재 latest alias는 최신 full run report를 가리키고 stale pointer는 확인되지 않았다. latest-valid는 검증 통과 full run이 없음을 placeholder로 보여주며 이전 run을 최신 valid로 오인시키지는 않는다.

## 영향

- 최신 run id와 HTML report run id 일치는 현재 충족한다.
- latest/latest-valid stale pointer는 현재 관측되지 않았다.
- 실패 원인 추적성과 중간 실패 report 보존은 renderer와 orchestrator 수정으로 닫았다.
- response 최신 report는 최신 `RUN_VALIDATION.json`을 반영해 `validation: failed`를 보여준다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: 1차 real subagent 리뷰에서 stale validation report를 Blocker로, best-effort renderer 전 validation 생략과 evaluator-only YAML field 노출을 Major로 보고했다. 이후 validator-before-render, rerender, answer YAML 기준 필드 제거, validation finding sanitization을 적용했다. 최종 real subagent 재리뷰에서 열린 Blocker/Major/Minor 없음으로 확인했다.

skill-creator 리뷰: 1차 real subagent 리뷰에서 validation integrity 관점의 report stale과 evaluator-only 기준 노출 위험을 확인했다. P6의 answer-oracle 추적성은 artifact link로 유지하고 private answer YAML 기준은 HTML payload에서 제거했다. 최종 재리뷰에서 validation integrity 관련 열린 항목 없음으로 확인했다.
