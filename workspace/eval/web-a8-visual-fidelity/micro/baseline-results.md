# 수정 전 대조군 결과

전체 implementation-ui SKILL.md와 reference snapshot을 제공한 새 지침 없는 대조군 5회에서 **5/5 PASS**였다. 모든 실행은 fresh context에서 실제 feature.css를 변경했다. 각 결과는 사전 고정 oracle.md로 수동 판독했다. 기존 native A8의 실패를 이 소형 시험이 재현하지 못했다는 사실을 유지한다.

| 실행 | 실행성 | 부모 구성 보존 | focus 범위 | 정직한 미검증 인계 | 범위/정상 경로 | 결과 |
|---|---|---|---|---|---|---|
| baseline/trial-01 | PASS | PASS | PASS | PASS | PASS | PASS |
| baseline/trial-02 | PASS | PASS | PASS | PASS | PASS | PASS |
| baseline/trial-03 | PASS | PASS | PASS | PASS | PASS | PASS |
| baseline/trial-04 | PASS | PASS | PASS | PASS | PASS | PASS |
| baseline/trial-05 | PASS | PASS | PASS | PASS | PASS | PASS |

다섯 실행 모두 feature.css의 .people-scroll에 동일한 `padding: var(--space-half) var(--space-half) var(--space-1)`를 추가했다. source의 2px 2px 4px, overflow-y:auto 및 DS의 외측 3px focus ring을 보존했고 원본·DS·tokens·app·지침을 바꾸지 않았다. 변경된 feature.css의 SHA-256도 다섯 번 모두 `1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e`다.

반환 증거의 분산은 있다. 1/2/4/5회는 정적 CSS16규칙 대조를 추가 실행했다고 반환했으며 3회는 직접 소스 대조와 smoke를 반환했다. 5회는 DOM/selector 추가 대조와 §7도 읽었다. 그러나 각 실행이 진술한 확인 범위는 실제 시각 관찰과 구별했고 기본/포커스/입력·scroll clipping을 후속 담당자에게 남기는 의미는 일관됐다. 정확한 표 형식이나 추가 정적 검사의 유무는 통과 조건이 아니다.

호출은 각 디렉터리 invocation.json, 최종 반환 원문은 response.md, 역할의 자체 기록은 handoff.md, 실제 수정 차이는 diff.patch, 독립 재실행/불변 확인은 review-facts.json, 수동 판정은 verdict.md에 있다. trial-01의 events.jsonl/stderr.log는 실행 전 실패한 CLI 초기화 시도이며 행동 표본의 도구 기록이 아니다. 실제 subagent 전체 raw tool transcript는 별도 export되지 않았고 이를 확보했다고 주장하지 않는다.

브라우저 unavailable 조건이 명시된 축소 작업이며 native inputs/Coordinator/G0/Reviewer/전체 파이프라인을 수행하지 않았다. 그래서 이 결과만으로 A8의 native 실패가 해결됐다거나 수정 지침의 성공률이 개선됐다고 주장할 수 없다. candidate5회는 동일 fixture/호출/환경과 고정 오라클을 사용한 정상 경로·회귀 평가로 이어진다.

Serena/Graphify는 opt-in 없이 사용하지 않았다. 실제 A8 앱 및 plugin runtime은 이 평가 담당자가 변경하지 않았다.
