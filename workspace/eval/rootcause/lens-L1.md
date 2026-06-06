# Lens L1 — 비결정 (P4③ run-variance)

> 정의: 같은 입력·같은 표준 버전인데 치명 FAIL 레인/구조 형태가 런마다 갈린 사례. "고친 게 회귀"처럼 보이나 실은 측정이 런마다 다른 잠재결함을 우연 노출한 것 아닌가도 판별.

핵심 발견: NJ-2가 c4live(Claude FAIL)↔nj2live(Codex FAIL) 양방향 반전 · FC-2 경계테스트 커버리지 Codex 런간 비결정 · catalog 위치 FAIL→PASS→FAIL 펄럭 · FK Claude 런간 비결정 · 여러 "회귀"가 실은 측정이 잠재결함 우연노출(catalog·C3·DR-13/14가 명시).

| episode_id | mode | evidence_anchor | severity | is_open | note |
|---|---|---|---|---|---|
| NJ-2 | L1 | DEVLOG:262 "🔄 반전: DR-24선 Codex가 NJ-2(C2)…이번엔 Claude — 비결정·N=1"; c4live-claude:24 vs c4live-codex:62 | critical | no | 같은 태스크서 치명 NJ-2 레인 양방향 반전. 교과서적 L1. DR-35로 양 PASS 수렴하나 원인은 표준 버그(ninja parse_body 415→400) |
| P4③ | L1 | DEVLOG:116·133·260·374; DEVLOG:33 "치명 FAIL 레인이 런마다 갈림" | major | no | 판정-소유 이주 5회+ 반복 run-variance. N≥5 보류. DR-24 "G1 에스컬레이션 비결정" 날카로운 진단 |
| catalog-회귀 | L1 | DEVLOG:192 "FAIL→PASS→FAIL 펄럭=비결정(architect 코인플립)"; :194 "회귀 전부 명세 일치=coder 일탈 아님" | major | no | smoke4❌→poc✅→smoke6❌ 펄럭. DR-26 "코드 회귀 아닌 architect 설계단계 코인플립"으로 정정 |
| C3 | L1 | DEVLOG:213 "가드는 이미 표준에…architect가 번복…같은 라이브 런 때도 존재"; DR-27 njlive Codex 치명↔Claude 부재 | major | no | 멱등성이 "회귀"로 보였으나 가드 상존+architect 라이브 번복. njlive서 Codex만 발현·Claude 부재=런타임 갈림 |
| FC-2(경계테스트) | L1 | nj2live-codex:29 "Codex 런간 테스트 커버리지 비결정"; DEVLOG:279 | critical | no | stock==quantity 경계 회귀테스트 Codex 런간 존재↔부재(nj2live FAIL·c4live·fklive 보유). 반복확인 전 처방보류 |
| BC-FK | L1 | nj2live-claude:47 "c4live-claude는 FK 없는 PositiveIntegerField→Claude 런간 비결정"; DEVLOG:286 | major | no | Claude nj2live FK↔c4live/fklive no-FK. 같은 규칙3 런마다 정반대 해석. DR-37 텍스트·underdetermined |
| pytest-MISS | L1 | pytestlive-claude:19 "Codex 0% 채택…런타임 특정 가능성"; aclex-codex:47; DR-45 "pytest N=2 재현" | major | yes | Codex pytest 미채택(N≥2)인데 Claude 모범 → 런타임-갈림형 L1. 백스톱⑬은 무설정이라 침묵 |
| P1a | L1 | DEVLOG:129 "🟡 갈림(Claude 준수/Codex 재발)"; REMAINING:33 | major | no | smoke2 라이브 Claude 준수↔Codex 재발. C2 의미변종까지 5회 반복. 단 DR-23 v3는 결정적 백스톱이라 집행갭 성격 강함 |
| DR-21 | L1 | DEVLOG:146 "Codex textbook 위반↔Claude 준수(거짓양성0)"; :148 | major | no | 라이브-파이어서 Codex 위반↔Claude 준수 갈림. reviewer 강등은 집행갭이나 위반 발현은 런타임 갈림 |
| DR-13/DR-14 | L1 | DEVLOG:78 "1차 격차는 상당 부분 N=1 분산…B1 도메인소유·stock≥0 둘 다 양 런타임 비결정" | major | no | 초기 코드품질 13:2:5가 대부분 run-variance로 정정. L1 원형·"측정이 잠재결함 우연노출" 최초 명시 |

NEW (L1 아님, 별 모드로 분리): ACL-EX=NEW:infra-exception-leak(표준 자체 빈틈·비결정 아님) · 위장-oversell=NEW:disguised-green-test · 위장-constraint=NEW:misattributed-test · 깨진JSON=NEW:problem-json-gap.

판별 메모: catalog·C3는 명백히 "측정이 잠재결함 우연노출"(DR-26:194·DR-28:213 직접 명시). DR-13/14가 이 패턴 원형. L1 행 전부 N=1·태스크 동일·우열 결론 금지(DEVLOG:33). 비결정 자체가 집행 갭 신호이지 런타임 우열 신호 아님.
