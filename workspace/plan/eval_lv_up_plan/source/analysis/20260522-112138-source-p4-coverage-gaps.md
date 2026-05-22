수정 대상: case
원인 분류: case/answer coverage gap

# source P4 coverage gap 분석

## 문제

독립 리뷰에서 source-reference-audit P4 기준 대비 source bucket의 직접 case coverage가 부족하다고 확인됐다.

- Runtime metadata, `agents/openai.yaml`, bundled reference, runtime cache/source sync를 직접 검증하는 source case가 없다.
- source-reference-audit의 제외 조건, 즉 Django 구현/테스트 메커닉 요청을 owning skill로 넘기는 negative case가 없다.
- `case-source-conflict-gap` answer는 public case가 요구한 `internal.md`, `external.md` consulted evidence를 `reference_basis`에 포함하지 않았다.
- `case-source-provenance-crosswalk` answer는 per-skill runtime reference provenance의 source side인 `workspace/reference/*/reference/final.md`를 `reference_basis`에 직접 포함하지 않았다.

## 영향

- P4 기준 1의 metadata/openai.yaml, runtime cache sync, final/review/internal/external evidence 검증이 부족하다.
- P4 기준 2의 positive/negative 사용 조건 검증이 부족하다.
- P4 기준 4의 answer oracle under-claim이 발생한다.
- P4 기준 5에서 case 목적과 answer evidence가 일부 어긋난다.

## 수정 대상 inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|---|
| source | `case-source-metadata-cache-sync` | 신규 | 신규 | source coverage tag 및 semantic validator 대상 | case/answer 추가 | 예 |
| source | `case-source-routing-exclusion` | 신규 | 신규 | source coverage tag 및 semantic validator 대상 | case/answer 추가 | 예 |
| source | `case-source-conflict-gap` | 변경 없음 | `internal.md`, `external.md` source basis 보강 | 구조 validator 대상 | answer 수정 | 예 |
| source | `case-source-provenance-crosswalk` | 변경 없음 | `workspace/reference/*/reference/final.md` source basis 보강 | 구조 validator 대상 | answer 수정 | 예 |
| source | bucket goal | 해당 없음 | 해당 없음 | required source coverage tag 보강 | eval_goal 수정 | 아니오 |

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 4, 열린 Minor 1

Subagent 리뷰/순차 fallback: Turing review가 metadata/cache sync case 부재, exclusion case 부재, conflict-gap basis underclaim, provenance source basis underclaim을 Major로 보고했다. Herschel review는 public leakage validator gap과 provisional validator gap을 Major로 보고했고, source eval pack의 기본 case family 구조는 Note로 적합하다고 판단했다.

## 판단

Public case에는 answer oracle, private 기준, 이전 run finding을 넣지 않는다. 신규 public case는 사용자-facing source audit 요청과 routing 판단만 담고, answer-only schema field는 private answer에만 둔다.

수정 후 추가/수정한 네 case는 모두 targeted eval 대상이다.
