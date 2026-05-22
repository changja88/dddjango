수정 대상: answer

# P5 source eval traceability 분석

## 배경

독립 source-governance review에서 `case-source-eval-traceability` answer가 cross-bucket traceability를 요구하지만 per-case public path, answer path, case id, source basis, coverage labels, leakage boundary, run artifact mapping을 충분히 구체적으로 요구하지 않는다고 지적했다.

## 원인 분류

- 분류: `answer`
- 대상 case: `case-source-eval-traceability`
- 문제: source eval goal은 각 eval bucket의 cases/answers가 source reference로 추적되어야 한다고 요구한다. 현재 answer는 bucket-level rule 중심이라 per-case proof가 약하다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 수정 방향

target behavior와 evidence_required에 per-case public case path, answer path, case id, source basis, stable coverage labels, leakage boundary, run artifact/status mapping을 명시한다.
