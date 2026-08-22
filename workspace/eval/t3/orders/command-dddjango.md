# T3 발주 — command-dddjango

- 원문: `dddjango/commands/dddjango.md` (현재 187행 — **센서스 176행에서 드리프트: 아래 행 번호는 참고값, spec은 반드시 현재 파일에서 재확정**)
- 스코프: REF 11절 · 규범 314문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/command-dddjango.spec.json` + `workspace/eval/t3/worksheets/command-dddjango.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | (전문) | 1–12 | 6 | none | N | frontmatter description=라우터 트리거(+1 애매 포함); codex는 description 재작성·$ARGUMENTS/allowed-tools 부재(번호 공간 규약 문면은 동일) |
| s002 | 산출물 위치 | 13–25 | 9 | none | N | - |
| s003 | 진행 가시성 | 26–56 | 22 | code | N | 배너 코드 펜스=앵커화된 출력 계약(구속); codex는 task 리스트 보조 채널·배너 «task 리스트» 필드 삭제, 승인 질문이 별도 절로 재편 |
| s004 | 시작: 모드 판별 | 57–60 | 5 | none | N | Read/Grep/Glob→네이티브 도구 치환 |
| s005 | Phase 0 — 요구·스코프 (G0) | 61–72 | 39 | none | Y:agent-coder/s004 | 배선 표준 #105~#112 문장 사본; AskUserQuestion→게이트 질문 채널 치환 |
| s006 | Phase 1 — 설계 (G1) | 73–85 | 52 | none | Y:agent-design-architect/s005 | 12-slot label·순서 리터럴 재등장(3중 병렬); codex는 병렬 정의 재정의(spawn 먼저·wait 뒤)·리뷰어 입력 «플러그인 설치 루트» 문장 부재 |
| s007 | Phase 2 — 구현 (G2, 이중 루프 TDD) | 86–140 | 129 | none | Y:agent-coder/s003 | P0 step1~7(5+5+4+10+18+81+6) 합산; 보고 형식 리터럴·비계 제거 사본; codex는 coder 입력 플러그인 루트 부재·registry 경로 표기 상이·G2 배너 문면 가감 |
| s008 | Phase 3 — 마무리·검증 보고 | 141–144 | 3 | none | N | - |
| s009 | 수정 모드 (부분 수정) | 145–156 | 17 | none | N | step6 «그대로 적용»은 정본 역참조(사본 아님); 직접 쓰기→직접 patch 치환 |
| s010 | 엣지 처리 | 157–168 | 17 | none | Y:command-dddjango/s007 | checker exit 1/2 처리 축약 재서술(P0 비고); codex는 «서브에이전트 결과 미수신» 불릿 추가 |
| s011 | 경계 | 169–176 | 15 | none | Y:agent-design-architect/s004 | 게이트 질문·STOP 기록 형식 쌍; codex는 입력 채널 문단을 request_user_input 규격으로 재작성+보일러플레이트 금지 불릿 추가 |
