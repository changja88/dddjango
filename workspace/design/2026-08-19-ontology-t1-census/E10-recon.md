# E10 P0 대사 노트 — command + pipeline agents

작성일: 2026-08-19. 대상: 기계 절 54(sections.tsv p0_group=E10) ↔ P0 상세 인벤토리 58절(`workspace/design/2026-08-18-p0-census/E10-command-agents.md`).

## §1 문서별 접기 규약 명문화

공통 규약(8개 문서 전부):

- **(전문) 합성절**: 기계 절 s001은 YAML frontmatter(L1~) + 헤딩 없는 서두(역할 선언 문단)를 한 절로 묶는다. P0의 «전문» 절은 서두 문단만 계수했으므로, P0 전문 ↔ 기계 s001은 **범위 확대 대응**(frontmatter 포함)이다. frontmatter `description`은 라우터 트리거 문면으로 T1 규약(«애매하면 포함+비고»)에 따라 규범 1문으로 가산했고, `tools:`/`skills:` 목록은 문장이 아닌 기계 설정 값이라 계수하지 않았다.
- **h2·h3 절 단위**: 기계 절은 h2와 h3을 각각 독립 절로 낸다. P0는 h2 단위로 계수하고 내부 h3은 비고로만 언급했으므로, 내부 h3을 가진 P0 절 하나는 기계 절 둘(h2 앞부분 + h3 이하)에 대응한다.

문서별 특칙:

- **command-dddjango**: P0는 Phase 2를 코퍼스 실참조 단위인 번호 step(1~7)으로 쪼개 7절로 계수했다. step 번호는 h2 아래 번호 목록이지 헤딩이 아니므로 기계 절 분할 단위가 아니다 → **P0 step 1~7 일곱 절이 기계 s007 하나로 접힌다**. 나머지 h2 절은 1:1.
- **agent-design-architect**: P0 «명세에 담는 것»(158) 한 절 ↔ 기계 s004(L31~36, h2 앞부분) + s005(L37~81, h3 «Error response contract 12-slot» 이하 — lens 불릿·입장 표 포함). 계수 분할은 직접 재계수로 s004=9, s005=149.
- **agent-design-review-api**: P0 «점검 항목 (계약 lens만)»(72) 한 절 ↔ 기계 s005(L45~53) + s006(L54~79, h3 12-slot 이하). 직접 재계수로 s005=10, s006=62.
- 나머지 5개 에이전트 문서(acceptance-tester·coder·design-review-db·design-review-ddd·discipline-reviewer): 내부 h3 없음 — P0 절과 기계 절이 전건 1:1(전문 규약만 적용).
- 부록·제외 절 없음. 서두 병합 없음(각 문서 서두는 전문 합성절 하나뿐).

## §2 P0 절 전건 대사 표

| P0 절 라벨 | 대응 기계 절 키(범위) | 규약 |
|---|---|---|
| command/전문·번호 공간 규약 (L7–11) | command-dddjango/s001 (L1–12) | 전문 합성(frontmatter 포함 확대) |
| command/산출물 위치 | command-dddjango/s002 | 1:1 |
| command/진행 가시성 | command-dddjango/s003 | 1:1 |
| command/시작: 모드 판별 | command-dddjango/s004 | 1:1 |
| command/Phase 0 — 요구·스코프 (G0) | command-dddjango/s005 | 1:1 |
| command/Phase 1 — 설계 (G1) | command-dddjango/s006 | 1:1 |
| command/Phase 2 step 1 (러너 준비) | command-dddjango/s007 (L86–140) | step 접기(7→1) |
| command/Phase 2 step 2 (한정 검색·dispatch) | command-dddjango/s007 | step 접기 |
| command/Phase 2 step 3 (슬라이스 도출) | command-dddjango/s007 | step 접기 |
| command/Phase 2 step 4 (coder 호출·슬라이스 감사) | command-dddjango/s007 | step 접기 |
| command/Phase 2 step 5 (규율 감사·suite 실행) | command-dddjango/s007 | step 접기 |
| command/Phase 2 step 6 (결정적 백스톱 27종) | command-dddjango/s007 | step 접기 |
| command/Phase 2 step 7 (G2 배너) | command-dddjango/s007 | step 접기 |
| command/Phase 3 — 마무리·검증 보고 | command-dddjango/s008 | 1:1 |
| command/수정 모드 (부분 수정) | command-dddjango/s009 | 1:1 |
| command/엣지 처리 | command-dddjango/s010 | 1:1 |
| command/경계 | command-dddjango/s011 | 1:1 |
| acceptance/전문 (L13) | agent-acceptance-tester/s001 (L1–14) | 전문 합성 |
| acceptance/입력 | agent-acceptance-tester/s002 | 1:1 |
| acceptance/산출 | agent-acceptance-tester/s003 | 1:1 |
| acceptance/인수 테스트 작성 규칙 | agent-acceptance-tester/s004 | 1:1 |
| acceptance/경계 | agent-acceptance-tester/s005 | 1:1 |
| coder/전문 (L16) | agent-coder/s001 (L1–17) | 전문 합성 |
| coder/입력 | agent-coder/s002 | 1:1 |
| coder/산출 | agent-coder/s003 | 1:1 |
| coder/작업 방식 (안쪽 루프 TDD) | agent-coder/s004 | 1:1 |
| coder/엣지·보고 | agent-coder/s005 | 1:1 |
| coder/경계 | agent-coder/s006 | 1:1 |
| architect/전문 (L13) | agent-design-architect/s001 (L1–14) | 전문 합성 |
| architect/입력 | agent-design-architect/s002 | 1:1 |
| architect/산출 | agent-design-architect/s003 | 1:1 |
| architect/명세에 담는 것 | agent-design-architect/s004+s005 (L31–36 / L37–81) | h3 분리(1→2) |
| architect/리뷰 반영·충돌 중재 | agent-design-architect/s006 | 1:1 |
| architect/경계 | agent-design-architect/s007 | 1:1 |
| review-api/전문 (L10) | agent-design-review-api/s001 (L1–11) | 전문 합성 |
| review-api/실행 모드 | agent-design-review-api/s002 | 1:1 |
| review-api/입력 | agent-design-review-api/s003 | 1:1 |
| review-api/산출 | agent-design-review-api/s004 | 1:1 |
| review-api/점검 항목 (계약 lens만) | agent-design-review-api/s005+s006 (L45–53 / L54–79) | h3 분리(1→2) |
| review-api/경계 | agent-design-review-api/s007 | 1:1 |
| review-db/전문 (L10) | agent-design-review-db/s001 (L1–11) | 전문 합성 |
| review-db/입력 | agent-design-review-db/s002 | 1:1 |
| review-db/산출 | agent-design-review-db/s003 | 1:1 |
| review-db/점검 항목 (데이터 lens만) | agent-design-review-db/s004 | 1:1 |
| review-db/경계 | agent-design-review-db/s005 | 1:1 |
| review-ddd/전문 (L9) | agent-design-review-ddd/s001 (L1–10) | 전문 합성 |
| review-ddd/입력 | agent-design-review-ddd/s002 | 1:1 |
| review-ddd/산출 | agent-design-review-ddd/s003 | 1:1 |
| review-ddd/점검 항목 (도메인 lens만) | agent-design-review-ddd/s004 | 1:1 |
| review-ddd/경계 | agent-design-review-ddd/s005 | 1:1 |
| discipline/전문 (L12) | agent-discipline-reviewer/s001 (L1–13) | 전문 합성 |
| discipline/입력 | agent-discipline-reviewer/s002 | 1:1 |
| discipline/산출 | agent-discipline-reviewer/s003 | 1:1 |
| discipline/감사 빈도 (적응형) | agent-discipline-reviewer/s004 | 1:1 |
| discipline/영구 테스트 입장 감사 | agent-discipline-reviewer/s005 | 1:1 |
| discipline/Phase 1·2 API 오류 scope·소유권 점검 | agent-discipline-reviewer/s006 | 1:1 |
| discipline/Phase 2 점검 항목 (클린코드·TDD 규율만) | agent-discipline-reviewer/s007 | 1:1 |
| discipline/경계 | agent-discipline-reviewer/s008 | 1:1 |

P0 58건 전건 대응 완료(일반 1:1 41건 · 전문 합성 8건 · step 접기 7건(→기계 s007 1절) · h3 분리 2건(→기계 4절)) — [adv 중재 정정 2026-08-19: L-B 발견 2 — 구판 «1:1 44건» 산식 오기 교정. P0 측 41+8+7+2=58 · 기계 측 41+8+1+4=54]. 기계 절 54건 전건이 표에 등장한다(s007은 7건 수용, architect s004·s005 / api s005·s006은 분리 수용).

## §3 잔차

**설명 불가 잔차 0.**

경계 사례(규약 안으로 설명됨): ① frontmatter는 P0 계수 범위 밖이었으나 기계 (전문) 절에 포함 — §1 전문 합성 규약으로 흡수(description +1 계수는 §4에 반영). ② P0의 step 단위·h3 언급은 절 목록의 계수 단위 차이일 뿐 본문 누락·초과가 아님을 라인 범위 합으로 확인(command L86–140 = step1~7 전체, architect L31–81 = «명세에 담는 것» 전체, api L45–79 = «점검 항목» 전체).

## §4 규범 계수 대조

이번 분류 norm_count 합 = **1082** vs P0 = **1060**. 차이 **+22**. [adv 중재 정정 2026-08-19: L-D 발견 4 — 구판은 description «필드당 1문» 가산(합 1068·+8)이었으나 P0 규약의 계수 단위는 «문장»이므로 문장 단위 재계수로 교정.]

- **+22 전액 = frontmatter description 가산(문장 단위)**: 8개 문서의 YAML description(라우터/디스패치 트리거 문면)을 문장 단위로 재계수 — command 1(2문 중 주제 설명 1문 제외)·acceptance 4·coder 2·architect 3·review-api/db/ddd 각 3·discipline-reviewer 3 = 22문. P0는 헤딩 본문만 계수해 이 22문이 없었다.
- 본문 계수는 P0 절 계수를 측정 연속성 의무에 따라 그대로 승계하고 기계 절 경계로 재배분만 했다: command s007 = P0 step1~7 합(5+5+4+10+18+81+6=129), architect 158 → s004 9 + s005 149(분할점 직접 재계수), api 72 → s005 10 + s006 62(동일). 재배분 합은 각 P0 원값과 일치한다.
- 문서별: command 314(=313+1) · acceptance 76(=75+1) · coder 104(=103+1) · architect 179(=178+1) · api 95(=94+1) · db 36(=35+1) · ddd 29(=28+1) · discipline 235(=234+1).

부기 — codex 대응 요약(3값): SAME 47 · DIFF 7 · ABSENT 0. DIFF 7건 = command s001·s003·s006·s007·s010·s011(실행 모델·게이트 채널·병렬 정의·플러그인 루트 전달 등 플랫폼 재작성이 문면 치환 범위를 넘음) + coder s004(검사기 확장-리터럴 경로 불릿 부재·«읽기 전용 한 턴 묶기» 불릿 추가). 에이전트 7종의 나머지 절은 «Coordinator→코디네이터»·스킬 접두(`dddjango-`) 치환·«로드할 지식 스킬» 절 신설(frontmatter skills: 목록의 형식 치환) 이내로 SAME. architect «산출물-우선 쓰기» 문단은 codex에서 산출 절로 이동했으나 규범 등가라 SAME 유지(절 이동은 비고 기재).
