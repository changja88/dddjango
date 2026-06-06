# Lens L2 — 집행 갭 (prose/reviewer/recipe가 라이브서 미발화·강등)

> 정의: 표준 문구·reviewer prose·긍정 레시피·가드가 *존재하는데* 라이브에서 미발화하거나 blocker→권고로 강등.

핵심 사슬: P1a → DR-21 → DR-22 → DR-23(false-clearance) → C2/C3 → DR-28. 반복 뿌리 = *맞는 산문에 결정적 집행이 없으면 홀리스틱 라이브 reviewer가 조용히 강등/우회*. 프로젝트가 해결한 사례(P2·P3·DR-23·DR-28·DR-32)가 전부 같은 모양(결정적 Bash 백스톱+생산자 예방)으로 수렴.

| episode_id | mode | evidence_anchor | severity | is_open | note |
|---|---|---|---|---|---|
| P1a | L2 | DEVLOG §3 #8:398 "긍정 레시피만…차단 기대"; REMAINING:35 "긍정 레시피만 깔고 집행 백스톱 보류→Codex 재발 못 막음" | critical | yes | L2 원형: 표준 문구(§6.2 3곳 금지)·긍정레시피 존재했으나 집행 게이트 부재로 라이브 미차단·5회 반복 |
| DR-21 | L2 | DEVLOG:146 "백스톱 텍스트 로드하고도 권고로 분류(G2 통과)"; LIVEFIRE:29 | critical | yes | blocker→권고 강등의 정의적 사례 |
| DR-22 | L2 | DEVLOG:155 "사전시뮬 P1a blocker 0/3…읽고도 연결 못 함"; :156 "문구 강화만으론 부족·Claude 리뷰어조차 미적용" | critical | no | 문구(prose)만으론 집행력 안 생김 실증 |
| C3 | L2 | DEVLOG:213 "가드는 이미 표준에 있었고(ebe116e)…architect 번복…산문 가이드가 집행력 없어 첫 라이브 검증서 무력…salience 낮음" | major | yes | 가드 상존했으나 architect 라이브 번복. 핵심 L2 예시 |
| NJ-2 | L2 | c4live-claude:118 "reviewer가 권고로 강등 개연…표준 처방 둘 다 안 씀"; DEVLOG:262 "라이브 reviewer 권고 강등=DR-21류" | major | no | 표준 처방 존재했으나 라이브 reviewer 권고 강등. 단 §6.3 자체가 버그→DR-35는 표준 수정으로 해결 |
| ACL-EX | L2 | aclex-claude:8 "도메인-예외 경로만 고침·인프라 여전히 누수"; DEVLOG:383 "표준 완벽 준수 ACL도 누수…DR-44 표준 자체 빈틈" | critical | yes | 전수성 처방이 도메인 예외에만 앵커. scope-gap 측면(L4와 공기) |
| DR-26 | L2 | DEVLOG:192 "펄럭=비결정(architect 코인플립)"; :193 "§632-(2) 위치 침묵→합리화" | major | no | catalog: 표준이 정답 가능한데 architect 라이브 코인플립(C3 동형). 3-leg 백스톱으로 집행력 부여 |
| P3(이력) | L2 | REMAINING:78 §9.6 필수인데 집행층 3중 구멍→Codex 통과 | major | no | §9.6 필수 규칙 존재했으나 집행 구멍. catch 게이트 추가 후 라이브 발화로 해소 |
| P2(이력) | L2 | REMAINING:65 "§16.4 금지했는데 코더가 알고도 위반"; :66 "discipline-reviewer가 기술정확성 명시 제외(집행 구멍)" | major | no | 명시 금지(§16.4) 존재했으나 reviewer 집행 범위 밖. 결정적 백스톱으로 해소 |
| DR-23 | NEW:false-clearance | DEVLOG:165 "DR-24가 'dual 완전 준수' 정정"; §3 #11:401 | major | no | exit0을 전면 준수로 오해석 — 집행 *부재*가 아니라 집행 *범위 좁음*의 오독 |
| C2 | L2 | REMAINING:104 "P1a 의미변종…중앙핸들러 죽은코드(백스톱 미포착)"; DEVLOG:169 "의미적 커버리지 갭" | major | no | P1a 백스톱(고정밀·저recall)이 의미 변종 미포착 |
| C5/P4③ | NEW:escalation-nondeterminism | REMAINING:91 "Codex G1 미상정·Claude G1 상정"; DEVLOG:170 "design-architect.md:38/51 위반" | major | yes | architect 가드 존재하나 G1 에스컬레이션 비결정(C3 동류) |
| 깨진JSON | NEW:framework-default-leak | aclex-claude:13 "ninja 기본핸들러→400 plain…415 데코는 CT만 봄" | major | yes | problem+json 규율 존재하나 ninja 기본핸들러가 우회 발화(scope) |
| NJ-1/협상 | L2(기각측) | DEVLOG:298 "텍스트 가드 약함(architect 라이브 번복 DR-28 선례)"; :300 | minor | no | 가드 약함 인정되나 §6.3이 협상 허용→백스톱 구조적 불가. "막을 위반 아님"으로 종결 |
| DNR-10 | L2(교훈) | DEVLOG §3 #10:400 | major | no | 텍스트판별 통과≠라이브 발화 박제 |
| DNR-14 | L2(교훈) | DEVLOG §3 #14:404 | critical | yes | DR-45 ACL-EX 박제·#11 강화 |

제외(L2 아님): P1b(예방 첫 시도 성공·미스파이어 없음)·G0-plain(가드 없던 over-ask novelty)·DR-30(가드 정상 발화)·DR-39~43(텍스트만·라이브 미검증=미발화 아닌 미stress)·DR-37(underdetermined·미스파이어 없음).

핵심: 해결된 사례 전부 "결정적 Bash 백스톱+생산자 예방"으로 수렴 — LLM-reviewer 산문만으론 반복 실패(DR-22 0/3이 최청결 증거). 열린 L2 프론티어 #1 = ACL-EX(유일 표준-수준 L2 갭, 결정적 백스톱 구조적 불가).
