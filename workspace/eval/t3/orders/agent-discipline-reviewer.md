# T3 발주 — agent-discipline-reviewer

- 원문: `dddjango/agents/discipline-reviewer.md` (현재 130행 — 센서스와 일치)
- 스코프: REF 8절 · 규범 237문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/agent-discipline-reviewer.spec.json` + `workspace/eval/t3/worksheets/agent-discipline-reviewer.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | (전문) | 1–13 | 4 | none | N | [adv 중재 정정 2026-08-19] norm 2→4 — 동상 |
| s002 | 입력 | 14–31 | 16 | none | Y:agent-design-review-db/s003 | 집행성 판정 1행 동형(Phase 1 모드 말미); change inventory 스코프 검사 포함 |
| s003 | 산출 | 32–42 | 11 | none | Y:agent-design-review-api/s004 | 산출 형식(발견/권고·심각도) 동형 4중; RESOLVED 토큰은 api와 대칭 |
| s004 | 감사 빈도 (적응형) | 43–46 | 3 | none | N | 정본 역참조(위임 — 사본 아님); «커맨드»→«dddjango SKILL의» 치환 |
| s005 | 영구 테스트 입장 감사 | 47–55 | 18 | none | Y:agent-coder/s004 | 첫-Green 비계 4중 사본·입장 표 규칙 — architect 입장 표와 병렬 |
| s006 | Phase 1·2 API 오류 scope·소유권 점검 | 56–62 | 13 | none | Y:command-dddjango/s007 | 12-slot inventory 대조 — command preflight와 병렬; bc_error_schema canonical 경로 리터럴 |
| s007 | Phase 2 점검 항목 (클린코드·TDD 규율만) | 63–125 | 163 | table | Y:agent-coder/s006 | ⓓ 물음 표 8행=구속 운반체(P0 계수 포함); 메커니즘-소유권(coder 경계와 쌍)·배선 표준 병렬; codex 차이는 스킬 접두 치환뿐 |
| s008 | 경계 | 126–130 | 9 | none | Y:agent-design-review-api/s007 | 스코프 권고 금지 동형; 소유권/정확성 구분 반복 명문화 |
