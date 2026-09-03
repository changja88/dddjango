# rv3-B — pre-gate 차단 승격 배치 ③ 계획 적대 리뷰 · 리뷰어 B(코퍼스 정합 축)

- 대상: `workspace/plan/2026-09-03-pregate-promotion-plan.md` §2·§3-A~G·§5 · 브랜치 `feat/pregate-enforce`.
- 방식: 저장소 읽기 전용(이 파일만 씀) · 실행은 grep/sed/python 스캔뿐(도구 소스 판정 — 실행 없음). 근거는 `파일:행`. 근거 없는 주장은 «미확인».
- 전제 확인: ISSUED 마지막 = R-3443(`ontology/ISSUED` tail) → 신규 채번 R-3444 ✓ · s007 블록 최대 = b58, order 1..58 연속(awk 계수) ✓ · 코퍼스 전수 3443 규범 중 2+ 블록이 statesNorm 하는 규범 **0건**(rules/*.ttl 스캔 — rv1-C C-3 재확인) ✓.
- Serena: skipped — 워크트리에 `.serena/project.yml` 없음(기본 도구로 진행). graphify: `graphify-out/graph.json` 없음 — 미사용.

## 0. 판정 요약

| # | 심각도 | 요지 | 근거 |
|---|---|---|---|
| B-1 | **BLOCKER** | §3-C «s006/b10 에 `statesNorm djr:R-3432` 부착» 은 rulepack 생성기의 «한 Work = 한 블록» 계약을 깨 `make rulepack`·`--check` 가 exit 2 로 선다(b9 가 이미 R-3432 를 진술) | `workspace/tools/ontology_rulepack.py:123-125,222,245-250` · `workspace/tools/queries/q4-injection-order.rq` 주석 «둘 이상이면 생성기가 fail-closed» |
| B-2 | **MAJOR** | s006/b10 ② 말미 «재발화의 판정자는 G2 앵커 차분이다» 가 §3-A «`--base` 재발화의 red 도 같다(반송)» 와 정면 충돌 — b10 을 손대는 김에 정정하지 않으면 한 절 안에 관찰·차단 두 의미론이 남는다 | `ontology/rules/command-dddjango.ttl:3217`(b10 말미) · 계획 §3-A |
| B-3 | **MAJOR** | «`--check-report` exit ≠ 0 → G2 미제시» 는 새 G2 차단 조건인데 R-0411(b57)의 닫힌 목록에 넣지 않고 R-3432 ③·R-3444 두 곳에 진술 — 선례(귀속 red·캐스케이드·승인 유입 전부 b57 목록 개정 동반 — R-0411 rev2 는 R-3440 신설과 같은 커밋)에 어긋남 | `command-dddjango.ttl:2381-2391`(R-0411 rev2 @2026-09-03) · `:3651`(b57 목록) · `ontology/LEDGER.tsv:1545-1546` |
| B-4 | **MAJOR** | §3-F «`--check-report` 가 이 형식을 읽는다» 는 과장 — E5 ⑷ 는 백틱 ID + `**ignored**`/`**filtered**` 만 읽고 증거 토큰은 읽지 않는다. 그런데 그 **기계 가독 행 정형이 어느 규범에도 성문돼 있지 않다**. 실전 리포트는 두 판형이 혼재(09-03 catalog `→ **corrected**` vs 09-02 media-library `**[#…]**: filtered —`) → 후자 판형은 «불비» 오판 | `design_pregate.py:1554`(예보 항목 행 = `` - `<ID>` … ``) · `~/Desktop/spring_dream_server/.dddjango/20260903-1214-fortune-catalog/pregate-report.md:134-135` · `…/20260902-0128-media-library/pregate-report.md:116-120` |
| B-5 | **MAJOR** | §5 계수표에 **BlockShape 2900 → 2901**(s007/b59 신설) 누락 → `ontology_hierarchy_check` RED | `workspace/eval/fixtures/ontology_gate/target-counts.json` · `ontology_hierarchy_check.py:31-36` |
| B-6 | MINOR | §3-C ③ 첫 문장은 s009/b3(G1′ 재발화 판형)·md:92(G1 override 무배너 경로 «dispatch 전 무조건 재실행»)의 재진술이고, 열거한 «정합 개정·설계 진화» 는 코퍼스에 0건인 미정의 용어 | `command-dddjango.ttl:3725` · `dddjango/commands/dddjango.md:92,113,180` · grep 0건 |
| B-7 | MINOR | 배너 토큰 «`red N건 · 처분 전건 기재`» 가 1행 문법의 «귀속 N건» 과 중복(§3-A·§3-E 동일 정정 필요) · §3-E «배너를 제시하지 않는다» 가 같은 괄호의 «어느 경우도 침묵 없음» 과 문면 충돌 | `command-dddjango.ttl:3053`(s003/b10 1행 형식) |
| B-8 | MINOR | §3-A ⓐ 가 «S1~S9» 범위를 하드코딩(사각 목록이 늘면 낡음) · 미탐 사각(S3·S4·S7~S9)도 filtered 근거로 읽힘 · «구조 규칙» 판정 기준을 손목록 대신 rule-owner-map 등급 `path` 로 명시 가능(인용 6건 전부 `path`·#392 는 `ast` — 정합) | `design_pregate.py` BLIND_SPOTS 9항 · `workspace/plan/2026-08-11-rule-owner-map.md:76,336` 등 |
| B-9 | MINOR | §3-G: `remove` 부재의 형식 red 범위(비후행만 — E4)가 미성문 · b10 «형식 red(계획↔실물 모순)» ↔ 실행기 «add 충돌(실존)»·§1·§3-G «add 충돌» 라벨 불일치 | `design_pregate.py:999` · `command-dddjango.ttl:3217` |
| B-10 | MINOR | R-3444 rev1 Expression IRI 는 `@2026-09-03`(b 접미 없음 — R-3439~3441 선례) · q4 골든은 `distinct_works` 와 `rows` 둘 다 +1 | `command-dddjango.ttl:2909-2933` · `workspace/eval/fixtures/rulepack/query-golden.json:36-38` |
| B-11 | MINOR | prefLabel 초안 길이: §3-A 169자(전체 5위) · §3-C 덧붙임 228자(최장 동률) — 도구는 통과하나 rulepack `label` = 6′ 재생성 프롬프트의 «명칭» 이라 문단급 라벨은 관례 밖 | 분포 실측(아래 B6) · `dddjango/scripts/regen_core.py:134,143` |
| B-12 | 검증됨 | R-3436 Exception→Prohibition: Norm 클래스를 읽는 도구는 `ontology_structural_check.py` 의 `?cls rdfs:subClassOf djr:Norm`(하위 클래스 무관)뿐 · SHACL NormShape sh:or 5형 통과 · hierarchy 계수 불변 · rulepack 에 deontic 필드 없음 · render/issued/golden 무관 → **소스 판정 통과**(선례 0 — LEDGER note 명기 의무) | 아래 B3 표 |
| B-13 | 검증됨 | R-3434·R-3435·R-3440·R-3427·architect R-3424/R-3426 과의 충돌 없음(상세 B1) · R-3444 wiring 판형 = R-3440 과 동일(`delegatedTo` 만 · enforcedBy 없음) · ISSUED 행 형식 · spec_lint 는 R-번호와 무관(트리 명세 #N 전용) | 아래 B1·B2 |
| B-14 | 검증됨 | codex 손 미러 실측: 9 행 중 byte 동일 5(28↔81·98↔116·167↔184·architect 88↔82·58 꼬리↔62) · 어절 차이 3행(96↔114 4 hunk/3 어절 · 165↔182 2 어절 · 180↔195 1 어절) — 검사기 0(`ontology_render_sync.py` codex 참조 0) | 아래 B7 표 |

## B1. §3-A~G 문면 ↔ 기존 규범 — 중복·충돌·약화 전수

| 기존 규범(블록 · 행) | §3 문면 | 판정 | 상세 |
|---|---|---|---|
| **R-3434** Prohibition «예보의 대체·축약 금지 — G2 게이트 비대체·HEAD 판형 유용 금지» (s006/b9 · `:2845-2857` · wiring `:677`) | §3-A «`--base` 재발화의 red 도 같다 — G2 앵커 차분은 실물 판정자이지 계획 red 의 대체가 아니다» | 검증됨(역방향 — 충돌 아님) | R-3434 = pre-gate ↛ G2 · §3-A = G2 ↛ pre-gate red. 같은 블록 b9 가 R-3432~3436 을 다중 statesNorm 하므로 그래프 층에서는 소유 모호가 생기지 않는다. R-3434 prefLabel 은 한 방향(«G2 게이트 비대체»)만 말하나 +1 Expression 을 들일 가치는 없음 — LEDGER note 에 «양방향 비대체 문장은 R-3433 rev4 소유» 한 줄로 충분 |
| **s006/b10 ②** 말미 «재발화의 판정자는 G2 앵커 차분이다» (R-3432 rev2 carrier · `:3217` · md:98 · codex:116) | §3-A 위 문장 + §3-C ③ | **MAJOR(B-2)** | 관찰 모드 문장이 그대로 남으면 «재발화 red = 판정자 아님» 으로 읽혀 §3-A 와 모순. 실행기 사각 S7 «유일 판정자는 G2 앵커 차분» 은 «기실현 실물↔스텁 차이» 한정이라 정합. **정정 문면**: «재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7)» |
| **R-3435** Permission «팬텀 스텁 = 스크립트의 결정적 투영물 · bare git 직접 금지» (b9 · `:2859-2865`) | §3-A·§3-C `--check-report` 실행 | 검증됨 | E5: 출력 전용·git 0회·판정 무접촉 → 스크립트 수행 범위 안. 격리 사본을 만들지 않으므로 «격리 사본 한정» 조항과 무관 |
| **R-0411** Prohibition «…잔존 시 G2 제시 금지(legacy 잔존은 별도 보고 항목)» (s007/b57 · `:2381-2391` rev2 @2026-09-03 amendment · `:3651` 목록 · md:165 · codex:182) | §3-C ③ «exit 0 을 얻어야 G2 를 제시한다» · §3-D «exit 0 이 아니면 G2 를 제시하지 않는다(R-3432 ③)» | **MAJOR(B-3)** | b57 목록(Red·pending·입장-diff·첫-Green 비계·미해소 exit·미해소 귀속 red·캐스케이드·contract mismatch)이 G2 차단 조건의 닫힌 열거다. 선례: 승인 유입 항목 신설(R-3440/b58) 때 **같은 커밋에서 R-0411 rev2 로 b57 에 «승인 유입도 별도 항목» 삽입**(LEDGER:1545-1546). 계획 «건드리지 않음» 목록이 R-0411 을 빼면 목록 결손 + 한 금지의 3중 진술. **처방**: R-0411 rev3 amendment(`@2026-09-03b` — rev2 가 이미 `@2026-09-03` 점유): b57 목록에 «pre-gate 최신성 불비(`--check-report` exit ≠ 0 — 아래 최신성 문단)» 삽입 · R-3444 문면의 «exit 0 이 아니면 G2 를 제시하지 않는다(R-3432 ③)» 를 «(G2 제시 금지 조건은 7번 목록 — R-0411)» 참조로 격하 · R-3432 ③ 는 절차 의무(«exit 0 을 얻는다»)만 보유. 비용: ExpressionShape +1 · codex 182 손 미러(2 어절 보존) · LEDGER s007 행은 이미 대상 |
| **R-0418~R-0421** (s009/b3 · `:3721-3726` · md:180 · codex:195) «design-spec 개정이 있으면 G1′ 제시 직전 최종본에 pre-gate 를 재실행 … Phase 2 중이면 재발화 판형: `--base <G1 기준선 SHA>`·WIP 커밋/stash» | §3-C ③ 첫 문장 «Phase 2 중 design-spec 변경(G1′ 반송 개정·정합 개정·설계 진화 전부)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다» | MINOR(B-6) | Phase 2 의 design-spec 개정 경로는 ⑴ 반송 → architect → G1′(s009/b3 · R-0420 «pending 잔존 시 Phase 2 진행 금지» · md:113 contract mismatch → G1 반송) ⑵ G1 override 무배너 경로(md:92 «dispatch 전에 pre-gate 를 무조건 재실행») 둘뿐이고(R-0421 «design-spec 직접 저작 금지») 둘 다 재실행 의무가 이미 성문. ③ 첫 문장은 재진술 + 미정의 용어. **정정 문면**: «③ **Phase 2 최신성** — Phase 2 중 design-spec 개정의 재발화 의무는 위 ②·G1′ 재승인 문단(수정 모드)·G1 override 문단이 이미 진다 — 차단 모드에서는 그 재발화의 red 도 반송이다(위 문단). 여기 추가 의무는 하나다: G2 배너 직전 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 를 실행해 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻는다 — 다르면(stale) 재발화 후다. skip 행·처분 절의 문자열은 대조 대상이 아니다.» |
| **R-3440** Obligation «G2 배너 «승인 유입 N건» 별도 항목» (s007/b58 · `:2917-2923` · wiring `:689`) | §3-D «이 행은 legacy 잔존·승인 유입 항목과 별개다» | 검증됨 | R-3440 은 배너 항목 목록을 소유하지 않는다(목록 소유 = R-0406/R-0411). b58 뒤 b59 신설은 b57 뒤 b58 신설 선례와 동형 |
| **R-3427** Obligation «경계 import 표 — 전부 성문 · 행 삭제 = 채널 은폐» (architect s005/b36 · `agent-design-architect.ttl:2104-2110`) | E6 S3 «블록에 기재된 경계 import 는 스텁에 방출되어 예보된다 — 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖» | 검증됨 | R-3427(전수 성문 의무)·R-3424(«산문 추론 0» · b33 `:2084-2089`)과 같은 방향. S3 는 사각 «진술» 이지 규범이 아님 |
| §3-A ⓐ «filtered(ⓐ S<n>)» ↔ 사각 목록 9항 | — | MINOR(B-8) | S3(미탐 «예보 불가»)·S4(앵커 축)·S7(기실현 add)·S8/S9(계약 실존 경계)는 귀속 red 의 오탐 원인이 아니라 filtered 근거가 될 수 없다. «S1~S9» 범위 하드코딩은 목록 증가 시 낡는다. **정정**: «ⓐ 리포트 사각 목록 항목 번호 인용(S<n> — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다)». «구조 규칙» 예시 6건(#81·#325·#188·#318·#336·#490)은 전부 rule-owner-map 등급 `path`(`:76` 등)·#392 는 `ast`(`:336`) — 정합. 기준을 «검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 규칙(rule-owner-map 등급 `path`)» 로 적으면 손목록 의존이 사라진다(A 축 판단과 겹침 — 여기서는 문면 정합만) |
| **architect R-3425** (s005/b34 · `:2091-2096` · md:88 · codex:82 byte 동일) «승격 폴더 표기 금지 — 경로는 언제나 `<칸>.py`» | §3-G «동명 승격 폴더 `<칸>/` 실존은 실존이다» | 검증됨 | 표기 규칙은 불변(`<칸>.py`)·판정만 폴더 실존 인정 — 충돌 없음. E4 예외와 1:1 |
| **architect R-3424·R-3426** (b33·b35) | §3-G | 검증됨 | R-3424 «부재 fail-closed» ↔ R-3436 rev3 «소급 작성» 동방향. R-3426(symbols 문법)은 §3-G 가 건드리지 않음 |
| **s006/b10 ②** «기준선 트리에 있는 add 는 여전히 형식 red(계획↔실물 모순)» ↔ 실행기 `:999` «add 충돌(실존)» ↔ §1 «add 충돌» ↔ §3-G «형식 red «add 충돌»» | — | MINOR(B-9) | 같은 판정의 라벨이 b10 만 다르다. b10 편집 시 «형식 red(add 충돌 — 계획↔실물 모순)» 로 통일. §3-G 의 add 규칙은 b10 ② 의 architect 독자용 이중 진술 — 의도된 이중 진술로 LEDGER note 에 명기 |
| §3-G «`remove[@Ln]` = 기준선 실존 경로» ↔ E4 «비후행 remove 부재 → exit 3 · 후행 `remove@Ln` 은 unsimulated 유지» | — | MINOR(B-9) | 규범이 검사보다 넓은 것은 무방하나 어느 부재가 형식 red 인지 무언. **정정**: «`remove[@Ln]` = 기준선 실존 경로(비후행 `remove` 부재는 형식 red «update 대상 부재» 와 같은 급 · 후행 `remove@Ln` 은 판정 밖 — 사각 S5)» |
| **R-3437** (s003/b10 `:3052-3053` · md:58 · codex:62) 1행 형식 «… 어느 경우도 침묵 없음» | §3-E «형식 red … 면 배너를 제시하지 않는다(반송)» · «`red N건 · 처분 전건 기재`» | MINOR(B-7) | ⑴ 배너 부재 = 1행 부재라 «침묵 없음» 과 어긋나 보임 → «형식 red(exit 3 — 블록 부재 포함)면 이 배너 자체가 없다(반송 메시지가 그 자리 — 침묵이 아니다)». ⑵ 1행 문법이 이미 «귀속 N건» 을 갖는다 → «귀속 N건(처분 전건 기재)» 로 §3-A·§3-E 동일 정정 |
| **R-3438** (s002/b8 `:3022-3027` · md:28 · codex:81 byte 동일) | §3-F «처분 행은 … 증거 토큰을 함께 적는다 — `--check-report` 가 이 형식을 읽는다» | **MAJOR(B-4)** | E5 ⑷ 의 판독 = «그 절 이후 텍스트에 `` `<ID>` `` 와 `**ignored**`/`**filtered**` 를 함께 가진 행». 증거 토큰은 판독 밖이고, 백틱 ID + 굵은 라벨 정형이 규범 어디에도 없다. 실전 판형 혼재(catalog `:134` `` - `869e0acd832f` [#392] … → **corrected** — … `` vs media-library `:116` `- **[#160/#484] …**: filtered — …`). **정정 문면(§3-F 대체)**: «처분 행의 정형은 `` - `<안정 ID>` <규칙·경로> → **<라벨>**(<증거 토큰>) `` 이다 — 증거 토큰: ignored = 빚 파일:행·STOP 경로 · filtered = ⓐ S<n>|ⓑ 실코드 경로·검사기 exit 0 · corrected = 소멸 run 시각·블록 해시 전→후. `--check-report` 는 이 행의 **안정 ID(백틱)와 라벨(굵게)만** 읽는다 — 증거 토큰은 사람 감사용이다. 계약 실존 행(e-ID)은 판독 밖이다.» |
| **R-3433** «명세 개정 승인마다 각 red 의 처분 라벨을 … append» (유지 문장) | §3-A | MINOR | 차단 모드에서 red 명세는 승인되지 않으므로 «승인마다» 시점이 비게 된다 → «개정 수신 후 재실행 시점마다(승인 시점이 아니다 — red 명세는 승인되지 않는다)» |
| «무배너 재승인» 용어 | §3-A | 검증됨 | md:92·s009/b3 꼬리에 실재(2건) |

## B2. R-3444 신규 채번의 착지

| 항목 | 실측 | 판정 |
|---|---|---|
| s007 현 최대 order | b58 · order 값 1..58 연속(awk 계수 — `:3640-3659`) | 신규 = **`s007/b59` · `djr:order 59`**. 렌더러 `ontology_render.py:72-78` 는 order 로 정렬한 뒤 `orders != range(1, n+1)` 이면 raise · `ontology_structural_check.py` ③ 도 «절 내 1..n 연속» 검사 → 임의 값 불가 |
| 투영 위치 | `blocks.sort()`(`:75`) = order 오름차순 단순 연결(IRI 서수는 정렬 키 아님) | b58 텍스트 직후·«## Phase 3» 헤딩 직전(md:167 → 신설 168 · 169 빈 줄 · 170 «## Phase 3»). §13(`ontology-authoring.md:124-133`): 블록 간 구분자는 선행 블록 후행 귀속 → **b59 text 말미 `\n\n` 의무**(b58 이 그렇게 끝남) |
| 블록 노드 판형 | b58(`:3654-3659`) 동형 | `<https://numchida.com/ns/djr#s/dddjango/commands/dddjango.md/s007/b59> a djr:Block ; djr:inSection <…/s007> ; djr:kind djr:kind-norm ; djr:order 59 ; djr:statesNorm djr:R-3444 ; djr:text "…\n\n"@ko .` |
| Work·Expression 판형 | R-3440(`:2917-2923`) 동형 | `djr:R-3444 a djr:Obligation ; skos:prefLabel "…"@ko ; djr:currentExpression <https://numchida.com/ns/djr#R-3444@2026-09-03> .` + `<…#R-3444@2026-09-03> a djr:Expression ; prov:specializationOf djr:R-3444 ; djr:revision 1 .` — **rev1 은 `b` 접미 없음**(R-3439~3441 선례 · `b` 는 같은 Work 의 같은 날 2차 Expression 에만 — rv1-C C-1). 계획 §2 헤더 «전부 `@2026-09-03b`» 는 R-3444 에 한해 정정(B-10). 도구는 접미를 검사하지 않으므로(structural ⑤ 는 revision·specializationOf 만) 어느 쪽도 red 는 아님 |
| wiring 판형 | `ontology/wiring/command-dddjango.ttl:689` `djr:R-3440 djr:delegatedTo <…#a/command-dddjango> .` · R-34xx enforcedBy 0건 | **동일**: `djr:R-3444 djr:delegatedTo <https://numchida.com/ns/djr#a/command-dddjango> .` 1행(canon 이 정렬). NormShape sh:or(HasChecker HasDelegate) 충족 · structural ① 무소유 규범 0 유지 |
| ISSUED 행 | `ontology-authoring.md:38-42` · `ontology_issued_check.py:3-4,20`(형식·연속·양방향) | `R-3444<TAB>2026-09-03<TAB>rules/command-dddjango.ttl` append(마지막 R-3443 → 연속 ✓). 결정 B4-(c) 채택 시 R-3445 도 같은 행 |
| spec_lint.py | 대상 = `workspace/design/2026-08-08-tree-revision-spec.md`(#N 531 규칙)·predicates·`rule-owner-map.md`(`spec_lint.py:44-47` · 검사 ①~⑧) | **R-번호와 무관** — ⑧ 소유자 매핑은 트리 규칙 #N 신설 시만. R-3444·`--check-report` 는 #N 을 만들지 않음 → 등재 불요(검증됨). ISSUED↔rules 정합은 `ontology_issued_check.py` + `ontology_structural_check.py ⑥′` 소관 |
| 계수 영향 | — | NormShape/WorkShape +1 · ExpressionShape +1 · **BlockShape +1(B-5)** · q4 `distinct_works`·`rows` +1 |
| 봉인 | `manifest_seal.py` graph 그룹(ontology/**) | 재봉인 대상(rv1-C C-6 — C 축) |

## B3. R-3436 Exception → Prohibition — Norm 유형을 읽는 지점 전수

| 도구 | 유형을 읽는 지점 | 판정 |
|---|---|---|
| `workspace/tools/ontology_structural_check.py` | q1 무소유 규범·q4b 고아 Work·q5b currentExpression 부재(`:257-303`): `?w a ?cls . ?cls rdfs:subClassOf djr:Norm` | 하위 5클래스 무차별 → **통과** |
| `workspace/tools/ontology_hierarchy_check.py` | COUNT_QUERY(`:31-36`) `rdf:type/rdfs:subClassOf* ?cls` per `sh:targetClass` | NormShape(djr:Norm)·WorkShape(djr:Work) 는 Exception·Prohibition 둘 다 산입 → 계수 불변. Prohibition/Exception 을 targetClass 로 갖는 shape 없음(`djr-shapes.ttl` — IsException/IsProhibition 은 NormShape sh:or 의 sh:class 노드) → **통과** |
| SHACL `ontology/shapes/djr-shapes.ttl` NormShape | `sh:or (IsObligation IsProhibition IsPermission IsException IsOverride)` | Prohibition ∈ 목록 → **통과** |
| `workspace/tools/ontology_render.py` | `:60-79` Section/Block/order/text 만 | 유형 무접촉 → **통과** |
| `workspace/tools/ontology_rulepack.py` + `queries/q4-injection-order.rq` | SELECT work/label/document/section/block/order/expression/checkers/agents/aliases — rdf:type 없음 · 팩 필드(`:131-141`)에 deontic 없음 | **통과**(rv1-C C-8 확인) |
| `workspace/tools/ontology_issued_check.py` | IRI 정규식(`:20-22`) · 리터럴 제거 | 유형 무관 → **통과** |
| `workspace/tools/query_golden_check.py` | `" a djr:Violation"` 계수(`:99`)만 | **통과** |
| `workspace/tools/spec_lint.py` | 온톨로지 미참조 | 해당 없음 |
| `ontology_gate.py`/canon | 재직렬화(`a djr:Prohibition` 트리플) | **통과** |
| vocab `djr:deprecated`·`djr:replacedBy`(`djr.ttl:88,113`) | rules 사용 0 | 불요 |

**판정: 유형 변경은 전 도구를 소스 근거로 통과한다(선례 0 — rv1-C C-12).** revisionKind 는 `djr:revision-redefinition`(vocab «지시 대상 변경») 이 맞다. 어떤 도구도 클래스 이력을 기록하지 않으므로 **LEDGER s006 note 에 «R-3436 rev3 redefinition — 유형 Exception→Prohibition(선례 0)» 명기**가 감사 흔적의 전부다.

**대안(유형 유지 시 문면)** — `a djr:Exception` 유지 · redefinition · b9 문면: «**구형 명세 skip 예외의 폐지**(2026-09-03 차단 승격): file-plan 기계 블록 부재로 실행을 건너뛰는 예외는 더 이상 없다 — 부재는 신규·개정·구형을 가리지 않고 형식 red(exit 3 «블록 부재»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4)과 구별). 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`).» · prefLabel «pre-gate 구형 명세 skip 예외 폐지 — 블록 부재 = 형식 red(exit 3) · 구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)». 단 «예외가 없다» 를 Exception 개체가 진술하는 것은 의미론적으로 뒤틀리므로 **유형 변경을 권고**한다.

## B4. s006/b10 `statesNorm djr:R-3432` 부착 — BLOCKER

- `ontology_rulepack.py:123-125`: `if wid in works: problems.append("Work … 가 블록 2개 이상에서 진술된다 — 정렬 키가 모호하다"); continue` → `:222` `[rulepack] RED` → `:245-250` `if red: return 2`. `q4-injection-order.rq` 헤더 «한 Work 를 진술하는 블록이 둘 이상이면 생성기가 fail-closed». `R-3432.block`(`:138`)은 단일 문자열 — 복수 수용 구조 없음. verify-base-core(`ontology_rulepack.py --check`)·`make rulepack` 둘 다 exit 2.
- 코퍼스 실측: 3443 규범 전수 중 2+ 블록 진술 0건 → 계획대로 집행하면 저장소 최초의 위반.

| 선택지 | 내용 | 계수 영향 | 대가 |
|---|---|---|---|
| (b) ③ 을 b9 에 두고 b10 은 그대로 | R-3432 rev3 텍스트 = b9(«무조건» 문장 뒤) · b10 은 ② 말미 정정(B-2)만 — b10 무규범 상태(rv1-C C-4)는 «판형 carrier — 규범은 b9 소유» 사유로 LEDGER 기록 | 계획 그대로(+7) | b9 가 더 길어짐 · C-4 고아 블록 잔존 |
| (c) **신규 R-3445** «pre-gate 캐시 skip·재발화 판형·Phase 2 최신성» 을 b10 이 statesNorm | b10 = ①②(정정)③ · R-3432 는 rev3 불요(prefLabel 은 요약이라 중복 무해) 또는 prefLabel 만 다듬으면 rev3 | R-3432 rev3 생략 시 ExpressionShape 3548+7(=3433·3436·3437·3438·3425·3444·3445) · NormShape/WorkShape +2 · q4 +2 · ISSUED 2행 · wiring 2행 | 채번 +1 · 1:1 관례·C-4 고아 둘 다 해소 |
| (a) R-3432 를 b9 에서 떼어 b10 으로 이동 | b9 statesNorm = 3433~3436 | +7 | b9 의 «내용이 바뀔 때마다 실행한다 … 무조건» 이 R-3432 문장인데 그래프상 다른 규범 블록에 놓임 — 비권고 |

권고: **(c)**. (b) 는 최소 비용이나 C-4 를 다음 배치로 다시 이월한다. 어느 쪽이든 «b10 에 R-3432 부착» 문구는 계획에서 삭제.

## B5. LEDGER 재기준선 · 계수식 · 골든

| 절 | 현 graph 기준선 최신 행 | 배치 후 |
|---|---|---|
| command-dddjango s002 | `LEDGER.tsv:1553` | +1 행(R-3438 rev3) |
| command-dddjango s003 | `:1550` | +1 행(R-3437 rev3) |
| command-dddjango s006 | `:1555` | +1 행(R-3433 rev4·R-3436 rev3·b10 정정·(b)/(c)) |
| command-dddjango s007 | `:1556` | +1 행(b59 신설 R-3444 · R-0411 rev3 채택 시 병기) |
| agent-design-architect s005 | `:1558` | +1 행(R-3425 rev2) |

- 행 형식(선례 `:1545`): `command-dddjango<TAB>s006<TAB><렌더 절 sha256><TAB>graph<TAB>-<TAB>-<TAB>-<TAB>-<TAB>rebaseline:2026-09-03 승격 배치 — …`. `ontology_ledger_check.py:61` 은 owner=prose 만 대조 → graph 행은 관례(누락해도 red 아님 — 감사 지적 대상, rv1-C C2 4단계).
- `target-counts.json`(`workspace/eval/fixtures/ontology_gate/`): ExpressionShape 3548 → **3555**(계획 산식 R-3432·3433·3436·3437·3438·3425 rev + R-3444 rev1 = 7 ✓) — R-0411 rev3 채택 시 3556 · B4-(c) 채택 시 R-3432 rev3 생략이면 3555 그대로(+R-0411 = 3556). NormShape/WorkShape 3452 → 3453(계획 ✓ · (c) 면 3454). **BlockShape 2900 → 2901 — 계획 누락(B-5)**. 나머지(AliasEntry 30·Section 545·SyncDebt 2·Violation 2·MetaNodeShapeIri 22) 불변.
- q4 골든(`query-golden.json:36-38`): `distinct_works` 3443 → 3444 **와 `rows` 3443 → 3444**(Work 1건 1행 계약 — (c) 면 3445). `query_golden_check.py --emit` 로 재생성(계획 ✓).
- `reverse_coverage.py:139` why 문자열 «관찰 모드·G2 비대체 — R-3432~R-3438» — R-3444 는 enforcedBy 가 없어 roster 무영향 · H5 문면 갱신 시 «R-3432~R-3438·R-3444» 로 함께.

## B6. prefLabel 초안 3건 — 관례 정합

실측(rules/*.ttl 3443건): 길이 min 6 · median 37 · mean 40.8 · p90 68 · p95 82 · p99 115 · max 228(R-3275). 구두점 선례: « » 81건 · ⓐ 9/ⓑ 5 · 백틱 111 · `|` 17 · `--` 22 · `<` 32 · `=` 95 · `+` 81 → 초안이 쓰는 문자는 전부 선례 있음. 소비처: `rulepack.json` `label` → `dddjango/scripts/regen_core.py:134,143`(6′ 재생성 `<rules>` 의 «번호와 명칭» — 본문 미동봉)·`rulepack.py:31,236`. 절단 없음·xml escape 처리(`regen_core.py:149`).

| 초안 | 길이 | 위치 | 판정 |
|---|---|---|---|
| §3-A R-3433 | 169 | 전체 5위(p99 115 초과) | MINOR — «명칭» 이 아니라 문단. 권고: «차단 모드 red 처분 — 귀속·형식 red 는 architect 반송 의무 · 배너 예외 = 귀속 red 전건 ignored(빚)\|filtered(사각 S<n>\|실코드 exit 0) + `--check-report` exit 0 · 구조 규칙(`path` 등급)은 filtered 불가»(≈115) |
| §3-B R-3436 | 92 | p95 근방 | 통과 |
| §3-C R-3432 덧붙임 | 228 | 최장 동률 | MINOR — 덧붙이지 말고 교체: «pre-gate 실행 의무 — design-spec 내용 변경마다·배너 직전 최종본·override 후 dispatch 전 무조건 · 캐시 skip 은 `--block-hash` 동일 시만 + skip 행 기록 · Phase 2 재발화 `--base <G1 기준선 SHA>`(red 는 반송) · G2 전 `--check-report` exit 0»(≈150). B4-(c) 채택 시 이 라벨은 R-3445 로 가고 R-3432 는 불변 |
| §3-D R-3444 | 69 | p90 | 통과 — `--check-report` 는 백틱(R-3432 «`--block-hash`» 관례) |

## B7. codex 손 미러 대상 행 전수 · «3어절 병렬 문면» 보존 — ④ 체크리스트

어절 diff 실측(Claude `dddjango/commands/dddjango.md` ↔ `codex-dddjango/skills/dddjango/SKILL.md` · architect `dddjango/agents/design-architect.md` ↔ `codex-dddjango/skills/dddjango-design-architect/SKILL.md`):

| 블록 | Claude 행 | codex 행 | 현 상태 | 배치 변경 | ④ 보존 조건 |
|---|---|---|---|---|---|
| s002/b8 | 28 | 81 | byte 동일 | §3-F(정정 문면) | 렌더 결과 그대로 복사 |
| s003/b10 | 58 | 62 | codex 는 «**G1/G1′ 배너에는…** 이후 꼬리만 `- ` 불릿으로 분리 · 꼬리 byte 동일 | §3-E | `- ` 접두 유지 · 열거 부분만 교체 |
| s006/b9 | 96 | 114 | 4 hunk = 3 어절: «리뷰 다발과 병렬 1회 — 조기 신호» ↔ «리뷰어 spawn 다발을 **전부 띄운 뒤 wait 수집 전에** shell 로 1회 — 조기 신호·codex 병렬 정의와 정합» · 조사 «이» 삽입 · «step 6(G2» ↔ «6번(G2» | §3-A(제목·게이트 문장·filtered 유형 삽입·ignored 삽입·skip 조항 교체)+§3-B | 3 어절 보존 · 배치 후 어절 diff 가 **정확히 이 4 hunk** 여야 함 |
| s006/b10 | 98 | 116 | byte 동일 | §3-C ③ + ② 말미 정정(B-2) + add 충돌 라벨(B-9) | 그대로 복사 |
| s007/b57 | 165 | 182 | 2 어절: «scope에서» ↔ «scope에서는» · «evidence는» ↔ «evidence(ErrorSchema 별도 shape 승인 포함)는» | R-0411 rev3 채택 시만 | 2 어절 보존 |
| s007/b58 | 167 | 184 | byte 동일 | 불변 | — |
| **s007/b59(신설)** | 168(신설) | 185 빈 줄 · 186 본문 · 187 빈 줄(«## Phase 3» 는 188 로) | — | §3-D | 본문 byte 동일 |
| s009/b3 | 180 | 195 | 1 어절: «쓰지» ↔ «patch하지» | 불변(③ 을 여기로 옮기지 않는 한) | — |
| architect s005/b34 | 88 | 82 | byte 동일 | §3-G | 그대로 복사 |

- 검사기 실측: `ontology_render_sync.py` codex 참조 0 · `corpus_mirror_sync.py` 스코프 = final.md 11종 · manifest pipeline 그룹은 «변경됐는가» 만 → **손 미러 누락은 어떤 게이트도 잡지 않는다**(rv1-C C1 요약 재확인). ④ 산출물로 위 표의 «기대 hunk»(합계 7 · byte 동일 5행은 0)를 스크립트 diff 로 첨부.
- md 투영 행(28·58·96·98·165·167·180·architect 88)은 graph-owned 마커 절(`dddjango.md:2,15,33,65,70,83,101,170,175,188,201`) — 직접 수정 금지, `ontology_render.py --apply` 로만.

## ④ 반영 목록(문면 정정 포함)

1. **[B-1 BLOCKER]** §3-C «b10 `statesNorm djr:R-3432` 부착» 삭제. 선택 (b) ③ 을 b9 로 / **(c) R-3445 신규 채번 + b10 statesNorm** — 결정 게이트 항목으로 승격(계수표 B4).
2. **[B-2 MAJOR]** b10 ② 말미 교체: «재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7)». codex 116 동일.
3. **[B-3 MAJOR]** R-0411 rev3 amendment(`@2026-09-03b`) 추가 — b57 목록 «…contract mismatch가 하나라도 남으면» 앞에 «pre-gate 최신성 불비(`--check-report` exit ≠ 0 — 아래 최신성 문단)» 삽입 · R-3444 문면의 «exit 0 이 아니면 G2 를 제시하지 않는다(R-3432 ③)» → «(G2 제시 금지 조건은 7번 목록 — R-0411)» · «건드리지 않음» 목록에서 R-0411 제거 · ExpressionShape +1 · codex 182 손 미러(2 어절).
4. **[B-4 MAJOR]** §3-F 를 B1 표의 «정정 문면(§3-F 대체)» 로 교체 — 처분 행 정형(백틱 ID · `→ **<라벨>**` · 증거 토큰 괄호) 성문 + «`--check-report` 는 안정 ID 와 라벨만 읽는다 · e-ID 행은 판독 밖». §3-A 예외 경로 문장도 «pregate-report 에 (위 정형으로) 기재» 로 참조.
5. **[B-5 MAJOR]** §5 계수표에 `BlockShape 2900 → 2901` 추가(B4-(c) 여도 2901).
6. **[B-6 MINOR]** §3-C ③ 을 B1 표의 정정 문면으로 교체(«정합 개정·설계 진화» 삭제 · s009/b3·G1 override 문단 참조).
7. **[B-7 MINOR]** «`red N건 · 처분 전건 기재`» → «`귀속 N건(처분 전건 기재)`» — §3-A·§3-E 동시 · §3-E «배너를 제시하지 않는다» → «이 배너 자체가 없다(반송 메시지가 그 자리 — 침묵이 아니다)» · R-3433 «명세 개정 승인마다» → «개정 수신 후 재실행 시점마다».
8. **[B-8 MINOR]** §3-A ⓐ «S1~S9» → «S<n> — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다» · 구조 규칙 기준에 «(rule-owner-map 등급 `path`)» 병기.
9. **[B-9 MINOR]** §3-G `remove` 문면 보강(비후행 부재 = 형식 red · 후행 판정 밖) · b10 «형식 red(계획↔실물 모순)» → «형식 red(add 충돌 — 계획↔실물 모순)».
10. **[B-10 MINOR]** §2 헤더 «전부 `@2026-09-03b`» → «리비전은 `@2026-09-03b` · 신규 R-3444(·R-3445) rev1 은 `@2026-09-03`» · 착지 «s007/b59 · order 59 · text 말미 `\n\n`» 명기 · q4 골든 `rows` 도 +1.
11. **[B-11 MINOR]** §3-A·§3-C prefLabel 을 B6 권고 문면으로 축약(≤ p99 근방) · `--check-report` 백틱.
12. **[B-12]** §2 R-3436 행에 «유형 변경 Exception→Prohibition — 도구 통과(소스 판정 rv3-B B3) · 선례 0 → LEDGER s006 note 명기» 추기 · 대안 문면은 B3 에 보관.
13. **[B-14]** §5 codex 손 미러 항목을 B7 표(행·hunk 기대값)로 교체 · 어절 diff 산출물 의무.
14. §5 LEDGER 행 5개의 note 에 «양방향 비대체 문장 R-3433 소유 · §3-G add 규칙은 b10 ② 의 architect 독자용 이중 진술» 명기(B1).

## 결정 불능 잔여(사용자 결정 필요)

1. **B4 착지**: (b) ③ 을 b9 로(계수 +7, C-4 고아 이월) vs (c) R-3445 신규(계수 표 B4 · C-4 해소) — 그래프 정합상 (c) 권고.
2. **R-0411 rev3 채택 여부**: 선례(승인 유입 = b57 목록 개정 동반) 준수 vs 계획의 «건드리지 않음» 원칙 — 미채택 시 «G2 제시 금지 조건» 의 단일 출처가 깨진다는 사실을 계획에 명기해야 함.
3. **유형 변경(Exception→Prohibition)**: 도구 통과는 확정(B3) · 선례 0 · 의미론 선택 — 권고는 변경.
4. **§3-A ⓐ 인용 가능 사각의 범위**(오탐 원인 항목 한정 여부): 판정식 축(리뷰어 A)과 겹침 — 여기서는 문면 정합만 지적.
