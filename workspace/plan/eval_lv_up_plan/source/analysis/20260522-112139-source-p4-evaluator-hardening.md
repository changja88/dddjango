수정 대상: evaluator
원인 분류: evaluator undercheck

# source P4 evaluator hardening 분석

## 문제

독립 리뷰에서 source bucket validator가 P4에서 필요한 semantic guard를 충분히 강제하지 못한다고 확인됐다.

- `case-source-provisional-drf`는 implementation patterns, Django Ninja, Django Web 세 영역의 source status를 각각 분류하게 하지만, validator는 `architecture-implementation-patterns`와 `implementation-django-web` source basis 누락을 실패시키지 못했다.
- public case leakage validator는 private answer 필수 field인 `hard_gates`, `control_case`, `expected_outcomes`, `with_dddjango`를 public prompt에서 차단하지 못했다.
- 신규 metadata/cache sync와 routing exclusion case가 구조적으로만 존재하면 의미 없는 broad coverage tag로 통과할 수 있다.

## 영향

- P4 기준 1의 DRF guardrail/source-status source axes와 metadata/cache sync 검증이 약하다.
- P4 기준 2의 제외 조건 검증이 validator에서 보조되지 않는다.
- P4 기준 3의 public leakage 방지가 일부 answer-only field에서 불완전하다.

## 수정 대상 inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|---|
| source | `case-source-provisional-drf` | 변경 없음 | 기존 보강 유지 | source-specific semantic validator 보강 | evaluator 수정 | 예 |
| source | `case-source-metadata-cache-sync` | 신규 | 신규 | metadata/cache semantic validator 추가 | evaluator 수정 | 예 |
| source | `case-source-routing-exclusion` | 신규 | 신규 | routing exclusion semantic validator 추가 | evaluator 수정 | 예 |
| all buckets | public cases | 변경 없음 | 해당 없음 | answer-only public pattern 보강 | evaluator 수정 | 관련 bucket validator |

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

Subagent 리뷰/순차 fallback: Herschel review가 provisional/DRF source-status path undercheck와 public leakage pattern undercheck를 Major로 보고했다. Turing review도 provisional/DRF validator undercheck를 Major로 중복 확인했다.

## 판단

먼저 failing tests를 추가해 validator gap을 재현했다. 이후 validator는 source-specific semantic check를 강화하고, public leakage pattern은 private answer schema field를 추가로 차단한다.
