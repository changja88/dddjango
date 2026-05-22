수정 대상: skill

# source-reference-audit method prompt와 artifact audit 경계 분석

## 배경

runtime `case-runtime-baseline-isolation` rerun에서 public prompt는 검증 방법을 요구했지만 with-ddjango 답변은 current-run artifact/schema/source 확인을 `run`으로 보고해 `pass-limited`가 됐다.

## 원인 분류

- 분류: `skill`
- 문제: `source-reference-audit`의 Leakage Evidence Protocol은 checked surfaces 보고를 요구하지만, 방법 설계 prompt와 실제 artifact audit prompt를 분리하지 않는다.
- 위험: public/runtime 답변이 현재 run finding을 절차 답변에 섞어 unsupported execution claim이나 leakage risk를 만든다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
skill-creator 리뷰: 기존 duplication 리뷰와 독립 source-governance review를 반영한 순차 통합 판단
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

method/procedure design prompt에서는 current-run artifact를 실제 확인 결과로 승격하지 말고, 사용자가 artifact audit을 명시한 경우에만 checked surface로 보고하도록 guardrail을 추가한다.
