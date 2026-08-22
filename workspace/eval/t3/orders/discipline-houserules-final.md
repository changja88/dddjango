# T3 발주 — discipline-houserules-final

- 원문: `dddjango/skills/discipline-houserules/references/final.md` (현재 242행 — 센서스와 일치)
- 스코프: REF 15절 · 규범 58문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/discipline-houserules-final.spec.json` + `workspace/eval/t3/worksheets/discipline-houserules-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | dddjango 표준 파일트리 | 1–6 | 3 | none | Y:discipline-houserules-skill/s003 | h1+정본 선언 블록. #N 정의문은 ID 체계 정의라 비계수. 복제 금지 선언이 skill s003과 상호 재진술 |
| s002 | 무엇이고 왜 | 7–12 | 1 | none | Y:discipline-houserules-final/s003-0 | #492 채널 분리 — §0에 같은 #492 재등장(문서 내 중복, P0 승계) |
| s003-0 | §0 제1원칙 — 골격은 내용과 무관하다 | 13–25 | 12 | none | N | #486~#492+실현 주체 coder+check-layer-skeleton 지목. #492 원출처(사본은 s002) |
| s004-1 | §1 표준 트리 — 140행 | 26–180 | 3 | code | N | 트리 140행(```text)=규범 «값»이나 문장 비계수(행 번호가 좌표계, P0 승계). TREE 주석 내 «손으로 고치지 않는다» 포함 |
| s006 | BC 직계 — 일곱뿐 | 183–189 | 7 | none | N | #81·#82·#10·#628. #628 불용어 목록=저장소 데이터 |
| s007 | 입구 — `driving_layer/` | 190–198 | 8 | none | N | #88~#92·#178. #92 의존 방향 예외 4종 |
| s008 | 만들지 않는 칸 | 199–205 | 5 | none | N | #20·#21·#58·#187·#314 금지 칸 열거 |
| s009 | `migrations/` — 생성물만 | 206–209 | 3 | none | N | elidable 언급은 «덤»이라 제외(P0 승계) |
| s010 | `<project>/` | 210–216 | 5 | none | N | #429~#432·#436. celery.py 조건부는 #491과의 관할 분리를 문면이 직접 방어 |
| s011-3 | §3 명명 | 217–221 | 3 | none | Y:discipline-houserules-final/s006 | «BC 이름=업무 경계»가 #82(s006) 재인용 — 편입 예정 자리표시 상태. 명시적 비커버 선언(검사기 없음) vs check-naming.py 실존(P0 발견 5) |
| s013 | 이관 종료 (2026-08-12) | 224–227 | 2 | none | N | 이관 종료 2026-08-12 — skill s006-3 신호 4가 이 절의 사본(원출처는 여기) |
| s014 | brownfield 는 «면제»가 아니라 «아직 안 갚은 빚»이다 | 228–231 | 3 | none | Y:discipline-houserules-skill/s004-1 | «빚≠면제» 문면이 skill §1·§3에도 존재. 첫 문장(그림자다)은 설명 제외 |
| s015 | 검사기의 가드 계약 | 232–235 | 1 | none | N | #74 exit 2 가드 계약 |
| s016 | 규칙 개정의 이행 순서 | 236–239 | 1 | none | N | #72 플러그인 셋 한 커밋 선행. 뒤집힘 결과는 이유 서술 제외 |
| s017 | 배경 (이 표준이 파생된 곳) | 240–242 | 1 | none | N | 대부분 서사(파생 출처) — «이 문서는 값만 싣는다» 1건 보수 포함으로 REF |
