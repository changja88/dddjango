# T3 발주 — agent-acceptance-tester

- 원문: `dddjango/agents/acceptance-tester.md` (현재 54행 — 센서스와 일치)
- 스코프: REF 5절 · 규범 79문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/agent-acceptance-tester.spec.json` + `workspace/eval/t3/worksheets/agent-acceptance-tester.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | (전문) | 1–14 | 6 | none | N | [adv 중재 정정 2026-08-19] SAME→DIFF(codex 로드 목록 4종 — ninja 삭제 실측)·norm 3→6(description 문장 단위 4문) |
| s002 | 입력 | 15–18 | 5 | none | N | - |
| s003 | 산출 | 19–22 | 5 | none | Y:agent-coder/s003 | 보고 형식 `path::test \| decision \| …` 리터럴 3중 사본(command s007 포함) |
| s004 | 인수 테스트 작성 규칙 | 23–48 | 57 | none | Y:agent-coder/s004 | [adv 중재 정정 2026-08-19] SAME→DIFF — 양판 동일 문자열이나 codex에서 implementation-test·architecture-ddd가 부재 스킬명(치환 누락형 잠재 표류) |
| s005 | 경계 | 49–54 | 6 | none | N | - |
