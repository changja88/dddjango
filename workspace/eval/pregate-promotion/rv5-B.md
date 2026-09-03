# rv5-B — pre-gate 차단 승격 배치 ⑤ 구현 적대 리뷰 · 리뷰어 B(규범 문면·그래프·미러 정합)

- 대상: 브랜치 `feat/pregate-enforce` · 구현 diff `59817bb..2fbc111`(ontology/ · command·architect md · codex SKILL.md 2종 · target-counts · LEDGER · ISSUED) ↔ 계획 `workspace/plan/2026-09-03-pregate-promotion-plan.md` §3-A~G + v2 델타 Δ2·Δ5 ↔ ③ 리뷰 `rv3-B.md`(④ 반영 목록 14항).
- 방식: 저장소 읽기 전용(이 파일만 씀). 실행은 읽기 전용 검증기(`ontology_render_sync`·`hierarchy_check --with-golden`·`structural_check`·`query_golden_check`·`rulepack --check`·`issued_check`·`ledger_check`)와 grep/sed/python 스캔·어절 diff(`SequenceMatcher`, 공백 분절)뿐. 근거는 `파일:행`.
- Serena: skipped — 워크트리에 `.serena/project.yml` 없음. graphify: `graphify-out/graph.json` 없음 — 미사용.

## 0. 판정 요약

| # | 심각도 | 요지 | 근거 |
|---|---|---|---|
| 5B-1 | **MAJOR** | R-3444(s007/b59) 배너 행의 «마지막 판정» 토큰 `귀속 N(처분 전건)` 이 기계 출처로 지정한 `--check-report` `요약:` 행의 실제 토큰 `red N(처분 전건)` 과 다르다 — «기계 출처 1:1 · 자기 판정 0» 이 D1 의 요지인데 코디네이터가 한 단어를 고쳐 적어야 성립한다. 계획 자체가 E5′(`red N`)와 Δ2 R-3444(`귀속 N`)로 갈려 있어 실행기 축(A)은 잡지 못한다 | `ontology/rules/command-dddjango.ttl:3719`(b59 text) · `dddjango/scripts/design_pregate.py:1747`(`short = f"red {attributed}(…처분 전건…)"`)·`:1781-1783`(요약 행) · 계획 Δ1 E5′ ↔ Δ2 R-3444 |
| 5B-2 | MINOR | R-3433 rev4 문면 «pregate-report 에 **아래** «처분 행 정형»(산출물 위치 절)으로 기재» — 산출물 위치 절(s002)은 Phase 1 절(s006)보다 **위**다(md 28행 ↔ 96행 · codex 81 ↔ 114) | `command-dddjango.ttl:3327` · `dddjango/commands/dddjango.md:14,28,82,96` |
| 5B-3 | MINOR | R-3425 rev2 «`--base` 기준선은 이동하지 않으므로 기실현 remove 는 실존이다 — 이미 지워진 경로의 행은 거둔다» — 앞 절(기준선 실존·HEAD 부재 = 실존 = 행 유지)과 뒤 절(행을 거둔다)이 «—» 로 이어져 같은 경우로 읽힌다. 실행기 E4′는 «기준선에도 없는 비후행 remove» 만 형식 red 이므로 «거둔다» 의 대상은 그 경우로 한정해야 한다 · Δ2 ⓑ 의 «(R-3445 ②)» 인용도 탈락 | `ontology/rules/agent-design-architect.ttl:2108` · 계획 Δ1 E4′·Δ2 R-3425 ⓑ |
| 5B-4 | MINOR | R-3433 prefLabel 147자 — Δ2 가 «≤115자» 를 명시하며 준 문자열 자체가 147자라 그대로 옮겨졌다(전체 3445건 중 6위 · p99 116). R-0411 123·R-3427 120·R-3425 118 은 p99 근방(통과) | 아래 B4 표 · rv3-B B-11 |
| 5B-5 | MINOR | R-3444 문면 «Phase 1 pre-gate 문단의 한정» — Phase 1 절에는 pre-gate 문단이 둘(b9 «결정적 예보» · b10 «캐시 skip·재발화 판형»)이고 한정은 b10 ③ 에 있다 — 지시 대상 모호 | `command-dddjango.ttl:3719` ↔ `:3270`(b10 ③ 한정) |
| 5B-6 | 검증됨(편차 기록) | R-3444 «(G2 제시 금지 조건은 7번 목록 — «pre-gate 최신성 불비»)» — Δ2 는 «— R-0411» 로 적으라 했으나 목록 항목 라벨로 격하했다. «격하(참조화)» 는 성립·의미 동일 · 본문 안 R-번호 인용 선례(`(R-3434)`·`(R-0459/R-0460)`)와 라벨 인용 둘 다 있음 | `command-dddjango.ttl:3719` · `:3270,3327` |
| 5B-7 | 검증됨 | 그래프 구조 전항 정합 — Expression IRI·revision·revisionKind·wasRevisionOf 사슬 10건 · R-3436 `a djr:Prohibition`(Exception 트리플 0) · s007/b59 order 59(최대) · b10 statesNorm = R-3445 만(`statesNorm.*R-3432` = 1) · wiring 2행 · ISSUED 2행 · LEDGER 5행 SHA **재계산 일치** · target-counts 3558/3454/3454/2901 · q4 3445/3445 · 검증기 7종 green | 아래 B2 표 |
| 5B-8 | 검증됨 | 렌더 투영 ↔ codex 손 미러: byte 동일 8행(28↔81 · 58꼬리↔62 · 98↔116 · 167↔184 · 169↔186 · 170↔187 · architect 88↔82 · 90↔84) · 병렬 정의 어절만 다른 2행(96↔114 4 hunk · 165↔182 2 hunk) · b59 착지(184 뒤 · 188 «## Phase 3» 앞) · `scripts/…` 경로 규약 동형 · 본문 내 절 참조(«7번 목록»·«수정 모드 절»·«산출물 위치 절») codex 에서도 해소 | 아래 B3 표 · `codex-mirror-diff.md` 재검증 |
| 5B-9 | 검증됨 | 잔존 문자열: 정본(ttl)·투영물(md)·미러(SKILL.md)·스킬·docs 에 «관찰 모드»·«구형 명세 skip»·`skip(구형 명세)` 0 · 도구·픽스처·LEDGER·설계 문서의 잔존은 전부 과거형/역사 기록 · exit 5 «권고·비차단» 5곳은 의도 잔존 | 아래 B5 표 |
| 5B-10 | 검증됨 | R-3434·R-3435·R-0418~0421·R-3440 과 충돌 0 · «G2 앵커 차분 = 기실현 실물의 판정자 ≠ 계획 red 대체»(R-3433) ↔ b10 ② 정정문 ↔ 사각 S7 세 문장 동의 | 아래 B6 표 |
| 5B-11 | MINOR(선택) | 소소한 편차 3: ⓐ R-3438 prefLabel 안 markdown 굵게 `**라벨**`(라벨 안 굵게 선례 0 — 나머지 `**` 2건은 경로 글롭) ⓑ `codex-mirror-diff.md` 의 s003/b10 행이 «대응 행 없음(수동 확인)» 으로 남음(실측 꼬리 byte 동일 — 산출물에 기록 없음) ⓒ rv3-B ④-14 의 LEDGER note(«양방향 비대체 문장 R-3433 소유 · §3-G add 규칙 = b10 ② 이중 진술») 미기재 — Δ5 가 요구한 R-3436 note 는 있음 | `command-dddjango.ttl:2926` · `codex-mirror-diff.md:8-9` · `ontology/LEDGER.tsv:1562-1566` |

BLOCKER 0 · MAJOR 1 · MINOR 4(+선택 3) · 검증됨 5.

## B1. 문면 ↔ 계획 델타(Δ2) 대조

| 규범(블록) | Δ2 요구 | 구현 문면(ttl 행) | 판정 |
|---|---|---|---|
| R-3433 rev4 (s006/b9) ⓐ | «배너(G1/G1′) 전건은 `--check-report` exit 0 을 근거로 한다» | «**배너(G1/G1′)의 근거는 언제나 `scripts/design_pregate.py … --check-report …` 의 exit 0 이다**(마지막 예보 절의 블록 해시 = 최종본 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재 — 자기 판정이 아니다 · 낡은 green 은 stale 로 선다)» `:3327` | 검증됨 |
| 〃 ⓑ | `귀속 N건(처분 전건 기재)` | «배너 예보 1행에 `귀속 N건(처분 전건 기재)` 를 병기» | 검증됨 |
| 〃 ⓒ | «개정 수신 후 재실행 시점마다 red 절 뒤에 append(이전 절의 처분은 재기재)» | «개정 수신 후 재실행 시점마다 각 red 의 처분 라벨을 그 red 절 뒤에 append 한다(이전 절의 처분은 재기재 — `--check-report` 는 마지막 절 이후만 읽는다)» | 검증됨 |
| 〃 ⓓ | «S<n> — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다» · 구조 규칙 «(rule-owner-map 등급 path)» 병기 | «ⓐ 리포트 사각 목록 항목 번호 인용(`S<n>` — 그 항목이 이 red 의 오탐 원인임을 한 줄로 잇는다)» · «구조 규칙(rule-owner-map 등급 path — 예: #81 …)» · `S1~S9` 하드코딩 0 | 검증됨 |
| 〃 §3-A 본문 | 제목 «(차단 모드)» · 게이트 문장 · 형식 red 열거 · 예외 경로 · corrected 제외 · e-ID 제외 · ignored 배너 시점 한정 | 전부 실재. 형식 red 열거는 «문법·블록 부재·블록 공허·add 충돌·update/remove 대상 기준선 부재 전부» 로 Δ1 E3′·E4′까지 반영. 실행기의 FormError 2종(`add 충돌(실존)` `:1011` · `스텁 렌더 파싱 불가` `:1021` → 요약 «형식 red 1건(실체화)» `:1901`)은 각각 add 충돌·문법에 귀속 — 열거 밖 종류 없음 | 검증됨 |
| 〃 라벨 정의 | §3-A «라벨 정의 문장은 유지하되 filtered 정의 뒤에 삽입» | filtered 정의의 옛 괄호 «(실코드 대조·기존 통과 선례 등 근거 병기 의무)» 는 **삭제**되고 «근거 유형은 둘뿐이다 ⓐ/ⓑ» 로 대체 — «기존 통과 선례» 는 새 닫힌 ⓐ/ⓑ 밖이라 남기면 충돌했을 것. 의도적 정리로 타당(LEDGER note 미기재) | 검증됨(편차 기록) |
| 〃 «아래 «처분 행 정형»(산출물 위치 절)» | (B-4 ④-4 «위 정형으로 기재» 참조) | 참조 대상 s002 는 문서 상 **위**(md 28행 ↔ 96행) — «아래» 오기 | **MINOR 5B-2** |
| R-3436 rev3 (s006/b9) | §3-B + «빈 블록(0행)도 형식 red(블록 공허)» 1구 · Prohibition | «**machine 블록 부재 skip 금지**: … 부재는 형식 red(exit 3 «블록 부재»)이고 file-plan 0행(빈 펜스·주석뿐)도 형식 red(«블록 공허»)이며 … 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`)» · `a djr:Prohibition` `:2885` | 검증됨 |
| R-3432 rev3 (b9) | clarification · 텍스트 불변 · prefLabel 을 b9 문장으로 좁히고 R-3445 참조 | b9 의 «내용이 바뀔 때마다 … 무조건» 문장 불변 · prefLabel «…(캐시 skip·재발화·Phase 2 최신성 판형은 R-3445)» `:2818` | 검증됨 |
| R-3445 rev1 (s006/b10) ② 말미 | «재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7)» · «형식 red(add 충돌 — 계획↔실물 모순)» | 두 문장 그대로 실재 `:3270` | 검증됨 |
| 〃 ③ | dispatch 전 `--base` 재발화 선행 · G2 전 `--check-report` exit 0 · **한정**(리포트 없음 ∧ 블록 없음 ∧ 변경 0 → `미실행(구형 명세 · 변경 0)` · `--check-report` 미호출 · 블록 있는 명세는 한정 밖) | 전부 실재. 개정 경로 열거 «(G1′ 반송·Contract mismatch 반송·수정 모드 개정 — 수정 모드 절)» 의 «수정 모드 절» = s009 «## 수정 모드 (부분 수정)» `:3763` 실재. 말미 보강 «(초안 수신 트리거로 리포트가 반드시 있다)» 는 Δ2 밖 추가이나 R-3432 «초안 수신 직후 실행» 과 정합 | 검증됨 |
| R-3444 rev1 (s007/b59) | «(G2 제시 금지 조건은 7번 목록 — R-0411)» 로 격하 · 배너 행 판형 · 기계 출처 = `--check-report` 요약 행 · `미실행(구형 명세 · 변경 0)` | 격하 ✓(라벨 인용 — 5B-6) · 기계 출처 ✓ · 미실행은 별도 문장 «한정에 드는 레인은 `pre-gate 최신성: 미실행(구형 명세 · 변경 0)` 으로 적는다» ✓ · **판정 토큰 `귀속 N(처분 전건)` ≠ 실행기 `red N(처분 전건)`**(`design_pregate.py:1747`) · 열거 안 `실존 결손 M` 단독 대안도 실행기는 `green · 실존 결손 M`/`skip · 실존 결손 M` 접미로만 낸다(`:1749,1751`) | **MAJOR 5B-1** · «Phase 1 pre-gate 문단» 모호 **MINOR 5B-5** |
| R-0411 rev3 (s007/b57) | b57 닫힌 목록에 «pre-gate 최신성 불비(`--check-report` exit ≠ 0 — 최신성 문단)» 삽입(contract mismatch 앞) | «… 미해소 캐스케이드 ①/② … 발견, pre-gate 최신성 불비(`--check-report` exit ≠ 0 — 아래 최신성 항목 · 2026-09-03), 또는 contract mismatch가 하나라도 남으면 G2를 제시하지 않는다» `:3705` — «아래» 는 b59(169행 > 165행) 라 옳음 · prefLabel 갱신 ✓ | 검증됨 |
| R-3437 rev3 (s003/b10) | 기계 출처 «`--check-report` 의 `요약:` 행(exit 0 일 때만 배너 — stale·red 미처분이면 이 배너 자체가 없다: 반송 메시지가 그 자리)» · `skip(구형 명세)` 삭제 · `귀속 N건(처분 전건 기재)` | «(기계 출처는 `--check-report` 의 `요약:` 행이다 — exit 0 일 때만 배너가 있다: … 귀속 red 를 처분 전건 경로로 통과시키면 `귀속 N건(처분 전건 기재)` · 형식 red(블록 부재·공허 포함)·stale·처분 미기재면 이 배너 자체가 없다(반송 메시지가 그 자리 — 침묵이 아니다) · 실행 불능이면 그 사실 그대로 — 어느 경우도 침묵 없음)» `:3105` · `skip(구형 명세)` 0 | 검증됨. 부기: 1행 형식의 `커버 P/S/I` 는 `--check-report` 요약 행(`:1781-1783`)에도, 종전 `--report` 실행 요약 행(`:1947`)에도 없다 — 승격 전부터의 결손(출처는 리포트 헤더 `COVER_NOTE` `:125`) · 비회귀 · 선택 정정 |
| R-3438 rev3 (s002/b8) | 처분 행 정형 성문 · 증거 토큰 3종 · 마지막 절 뒤 append · `--check-report` 는 ID(백틱)+라벨(굵게)만 · e-ID 판독 밖 · skip 종류(캐시 skip·실체화 0) | 전부 실재 `:3079`. 렌더 결과 md 28행 `` `- \`<안정 ID>\` <규칙·경로> → **<라벨>**(<증거 토큰>)` `` — 코드 스팬 안 백틱 이스케이프가 그대로 노출되나 s002/b8 은 2026-09-01 이래 같은 표기 관례(직전 렌더와 동형) | 검증됨 |
| R-3425 rev2 (architect s005/b34) | ⓐ 예외 «유효 승격 형태(`<칸>/__init__.py` ∧ `<칸>/<칸>.py`) 기준선 실존» ⓑ «비후행 remove 부재는 형식 red(예외 없음) · 후행은 판정 밖 · `--base` 기준선은 이동하지 않으므로(R-3445 ②) 기실현 remove 는 실존이다» ⓒ «add 충돌» | ⓐ ✓ ⓒ ✓ · ⓑ 는 «(비후행 remove 의 부재는 형식 red «remove 대상 부재» — 예외 없음 · 후행 `@Ln` 은 판정 밖 · `--base` 기준선은 이동하지 않으므로 기실현 remove 는 실존이다 — 이미 지워진 경로의 행은 거둔다)» — (R-3445 ②) 인용 탈락 · 말미 «이미 지워진 경로의 행은 거둔다» 가 직전 «기실현 remove 는 실존」과 «—» 로 붙어 모순처럼 읽힘 | **MINOR 5B-3** |
| R-3427 rev3 (architect s005/b36) | «부재면 ⑴ 모듈 부재» → «승격 형태 예외로 통과한 update 대상에 한해 ⑴(그 외 부재는 형식 red 로 먼저 선다)» | «(사본에 실물이 있을 때만 — 기준선 부재 update 는 형식 red 로 먼저 서고, 유효 승격 형태 예외로 통과한 대상만 update 로는 생기지 않으므로 ⑴ 모듈 부재)» `:2122` | 검증됨(문면. 승격 폴더가 실존하는데 ⑴ «모듈 부재» 로 보는 의미론은 계획 E4′ «실존 채널 현행 유지» 의 결정 — A 축) |

## B2. 그래프 구조

| 항목 | 실측 | 판정 |
|---|---|---|
| Expression IRI·revision·revisionKind | R-3433@2026-09-03b rev4 redefinition(`:2857-2861`, wasRevisionOf @2026-09-03 rev3) · R-3436@…03b rev3 redefinition(`:2899-2903` ← @…03 rev2 clarification) · R-3432@…03b rev3 clarification(`:2831-2835`) · R-3437@…03b rev3 amendment(`:2919-2923`) · R-3438@…03b rev3 amendment(`:2939-2943`) · R-0411@…03b rev3 amendment(`:2395-2399`) · R-3427@…03b rev3 amendment(architect `:1743-1747`) · R-3425@2026-09-03 rev2 amendment(architect `:1704-1708` ← @2026-09-01 rev1 — 그날 첫 개정이라 `b` 없음이 맞음) · R-3444@2026-09-03 rev1 · R-3445@2026-09-03 rev1(wasRevisionOf 없음) — 세 revisionKind 전부 vocab 실재(`djr.ttl:195,198,201`) | 검증됨 |
| R-3436 유형 | `djr:R-3436 a djr:Prohibition` `:2885` · `R-3436 a djr:Exception` 0건 · wiring `:681` 유지 | 검증됨 |
| s007/b59 | inSection s007 · kind-norm · order 59(s007 order 최대 57·58·59 연속) · statesNorm R-3444 · text 말미 `\n\n` `:3714-3719` | 검증됨 |
| s006/b10 | statesNorm = `djr:R-3445` 만 `:3269` · b9 statesNorm 3432~3436 5건 `:3326` · `grep -c "statesNorm.*R-3432"` = 1 | 검증됨 |
| wiring | `djr:R-3444 djr:delegatedTo <…#a/command-dddjango>` · R-3445 동형(`wiring/command-dddjango.ttl:693,695` — R-3440 판형) | 검증됨 |
| ISSUED | `R-3444<TAB>2026-09-03<TAB>rules/command-dddjango.ttl` · R-3445 동형(`ISSUED:3444-3445`) · `ontology_issued_check.py` 위반 0 | 검증됨 |
| LEDGER 5행 | command s002 `7c6153…` · s003 `4bff33…` · s006 `dcd515…` · s007 `923e98…` · architect s005 `00ee15…`(`LEDGER.tsv:1562-1566`, 9열) — `sha256(strip_marker(span))` 재계산 5/5 일치 · `ontology_render_sync.py` 그래프 소유 절 540 red 0 · `ontology_ledger_check.py` 위반 0 · s006 note 에 Δ5 요구 «Exception→Prohibition · 유형 변경 선례 0 · 대안 문면 rv3-B B3 보관» 실재 | 검증됨 |
| target-counts | Expression 3558 · Norm/Work 3454 · Block 2901(Δ2 계수식과 일치) · `ontology_hierarchy_check.py --with-golden` 셰이프 9종 불일치 0 | 검증됨 |
| q4 골든 | `query-golden.json:37-38` distinct_works 3445 · rows 3445 · `query_golden_check.py` 7종 일치 | 검증됨 |
| rulepack | `ontology_rulepack.py --check` «정합 — 팩 == render · 양 런타임 미러 동일» · `R-3432.block` = s006/b9 단일 · R-3445.block = s006/b10 | 검증됨 |
| structural | `ontology_structural_check.py` 7종 조인·순서 정합 | 검증됨 |

## B3. 렌더 투영 ↔ codex 손 미러(어절 diff 직접 재실행)

| Claude 행 | codex 행 | 실측 | 판정 |
|---|---|---|---|
| dddjango.md:28 (s002/b8) | SKILL.md:81 | byte 동일 | 검증됨 |
| :58 (s003/b10) | :62 | codex 는 `- ` 불릿으로 «**G1/G1′ 배너에는…» 꼬리만 분리 — 꼬리 byte 동일(이번 변경은 전부 꼬리 안) · 머리부(AskUserQuestion 문단)는 codex 에 부재가 정상(게이트 모델 상이 — SKILL.md:53 절) | 검증됨 |
| :96 (s006/b9) | :114 | hunk 4 = 병렬 정의 어절만: «리뷰 다발과 병렬»→«리뷰어 spawn 다발을 **전부 띄운 뒤 wait 수집 전에** shell 로» · «신호),»→«신호·codex 병렬 정의와 정합),» · «이» 삽입 · «step 6(G2»→«6번(G2» — rv3-B B7 기대 hunk 와 정확히 일치 | 검증됨 |
| :98 (s006/b10) | :116 | byte 동일 | 검증됨 |
| :165 (s007/b57) | :182 | hunk 2 = «scope에서»→«scope에서는» · «evidence는»→«evidence(ErrorSchema 별도 shape 승인 포함)는» — 기대와 일치 | 검증됨 |
| :167 (s007/b58) | :184 | byte 동일 | 검증됨 |
| :169 (s007/b59 신설) | :186 | byte 동일 · 위치 = 184(승인 머지 목록) → 185 빈 줄 → 186 → 187 빈 줄 → 188 «## Phase 3» | 검증됨 |
| :170 빈 줄 · :171 «## Phase 3» | :187 · :188 | 동형 | 검증됨 |
| design-architect.md:88 (s005/b34) · :90 (b36) | architect SKILL.md:82 · :84 | byte 동일 | 검증됨 |
| 경로 규약 | codex 114 «`scripts/…` 는 registry 게이트와 같은 규약 — **이** 스킬 폴더의 절대 경로로 펴고» (병렬 어절) · codex 116/186 의 `scripts/design_pregate.py … --check-report …` 와 codex 131 `scripts/registry_gate.py …` 동형 — 새 문면이 codex 규약을 깨지 않음 | 검증됨 |
| 본문 내 절 참조 | «7번 목록»(codex 182 = «7. **G2 배너**») · «수정 모드 절»(codex 192) · «산출물 위치 절»(codex 68 — codex 에서도 Phase 1(101) **위**) · «Phase 1 pre-gate 문단»(codex 101 절) 전부 해소 | 검증됨(«아래» 오기는 양쪽 공통 — 5B-2) |
| `codex-mirror-diff.md` | 어절 계수(27/8)·byte 동일 6행 재현 · 단 s003/b10 행은 «대응 행 없음 — 수동 확인» 으로 남아 실측 결과가 산출물에 없음 | MINOR(선택) 5B-11ⓑ |

## B4. prefLabel

| 규범 | 길이 | 위치(3445건 · p90 68 · p95 82 · p99 116 · max 228) | 판정 |
|---|---|---|---|
| R-3433 | 147 | 6위 — Δ2 «≤115자» 미충족(Δ2 문자열 자체가 147) | MINOR 5B-4 |
| R-0411 | 123 | 20위 | 통과(p99 근방) |
| R-3427 | 120 | 25위 | 통과 |
| R-3425 | 118 | 28위 | 통과 |
| R-3432 | 108 | p99 이내 | 통과 |
| R-3445 | 104 | 〃 | 통과 |
| R-3437 | 102 | 〃 | 통과 |
| R-3436 | 98 | 〃 | 통과 |
| R-3438 | 97 | 〃 — 라벨 안 `**라벨**`(굵게 선례 0 · 나머지 `**` 2건은 글롭) | MINOR(선택) 5B-11ⓐ |
| R-3444 | 94 | 〃 | 통과 |

- 구두점: 백틱 없는 `--check-report`(R-3433·R-3437·R-3444·R-3445)는 선례 13건(백틱 9건)으로 관례 안 · `S<n>`·`|`·«»·ⓐ 전부 선례 있음.
- rulepack: `dddjango/scripts/rulepack.json` works 의 R-3433/R-3436/R-3444/R-3445(+R-3432·3437·3438·0411·3425·3427) label·expression 이 ttl 과 일치 · codex `codex-dddjango/skills/dddjango/scripts/rulepack.json` byte 동일(`cmp`) · `design_pregate.py` 도 byte 동일.

## B5. 잔존 문자열 전수

| 문자열 | 위치 | 성격 | 판정 |
|---|---|---|---|
| «관찰 모드» | ontology/rules·wiring · dddjango/**(commands·agents·skills·scripts) · codex-dddjango/** · docs/ | **0건** | 검증됨 |
| 〃 | `workspace/tools/pregate_fixture_run.py:39` «(관찰 모드의 exit 4 skip 폐지)» · `workspace/eval/fixtures/pregate/noblock-spec.md:4`·`empty-block-spec.md:3` «관찰 모드에서는 … 였으나» | 과거형 역사 기록 | 의도 잔존 |
| 〃 | `ontology/LEDGER.tsv:1553-1557` 이전 재기준선 note | 원장(append-only) | 의도 잔존 |
| 〃 | `workspace/design/2026-09-01-pregate-design.md:6,8,86,103,115,121,126,146,155` · `pipeline-speed-baseline.md:5,66` · `pregate-backtest.md:43,47` | v1~v3 결정 기록. 86행 «(관찰 모드의 유일한 추가 절차 의무)»·103행 «(관찰 모드 «권고» → 승격 후 «반송 의무»)» 는 v3 본문이나 196행 «§10 M2 모드 표시: MODE = "enforce" …» 추기가 현행을 진술 | 역사 기록(선택: 86행에 «(승격 후 §10 M2)» 포인터) |
| «구형 명세 skip»·`skip(구형 명세)`·«구형 명세 skip 한정»·«차단 승격 전까지»·«이 실행은 **예보다**»·«차단 승격 시 폐지» | 전 범위 | **0건** | 검증됨 |
| «권고·비차단» | `design_pregate.py:58,75,1537,1914,1939`(+codex 동일) · `pregate_fixture_run.py:36,674,678,692,878,879,887` · md/ttl b9 «exit 5 비차단» | 전부 계약 실존 결손(exit 5) 문맥 | 의도 잔존 |
| `reverse_coverage.py:139` | «차단 모드 2026-09-03 승격 · G2 비대체 — R-3432~R-3438·R-3444·R-3445» | rv3-B B5 요구 반영 | 검증됨 |
| «구형 명세» 신문면 | md 88(소급 작성 시 update)·96(소급 작성 의무)·98(`미실행(구형 명세 · 변경 0)`)·169(동) | 현행 규정으로서 의도된 사용 | 검증됨 |

## B6. 인접 규범과의 중복·충돌

| 대조 | 문장 | 판정 |
|---|---|---|
| R-3433 rev4 (b9) | «`--base` 재발화의 red 도 같다 — G2 앵커 차분은 **기실현 실물의 판정자**이지 계획 red 의 대체가 아니다» | 세 문장 동의 — (i) 재발화 red = 계획 red = 반송 · (ii) G2 앵커 차분의 소관 = 기실현 실물↔스텁 차이 |
| R-3445 rev1 (b10 ② 정정문) | «재발화의 red 는 계획 red 로서 반송 사유이고(위 문단 — 차단 모드), 기실현 실물이 스텁과 다른 위반의 판정자만 G2 앵커 차분이다(사각 S7)» | 〃 (rv3-B B-2 처방 그대로) |
| 사각 S7 (`design_pregate.py:1529-1532`) | «오버레이 실존 add 는 … 스텁으로 실체화해 예보하므로(… 실물 판정 혼입 0 …) 실물이 스텁과 다른 위반은 예보 표면 밖이고, 유일 판정자는 G2 앵커 차분이다» | 〃 — «유일 판정자» 의 주어가 «실물이 스텁과 다른 위반» 으로 한정돼 있어 (i) 과 충돌 없음 |
| R-3434 Prohibition(b9 공유) «예보는 Phase 0 빚 스캔·step 6(G2) 실행·증거 요구를 대체·축약하지 않는다» | b9 에 그대로 잔존 — 방향 pre-gate↛G2 · R-3433 문장은 G2↛pre-gate red | 양방향 비대체 · 충돌 0(소유 명기는 LEDGER note 미기재 — 5B-11ⓒ) |
| R-3435 Permission(팬텀 스텁 = 스크립트 투영물 · bare git 금지) | `--check-report` 는 출력 전용·git 0회(`run_check_report` `:1763-1784`) | 충돌 0 |
| R-0418~0421 (s009/b3 `:3786`) «design-spec 개정이 있으면 G1′ 제시 직전 최종본에 pre-gate 를 재실행 … Phase 2 중이면 재발화 판형: `--base <G1 기준선 SHA>`» | b10 ③ «Phase 2 중 design-spec 변경(…수정 모드 개정 — 수정 모드 절)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다» — G1′ 직전 ⊂ dispatch 전 · s009 는 «Phase 1 pre-gate 문단 — 트리거는 수정 모드에도 같다» 로 위임하므로 R-3437 «exit 0 일 때만 배너» 도 G1′ 에 상속 | 재진술 아닌 시점 보강 · 충돌 0 · rv3-B B-6 의 미정의 용어(«정합 개정·설계 진화») 삭제 확인 |
| R-3440 (s007/b58) «승인 유입 N건» 별도 항목 | b59 «이 행은 legacy 잔존·승인 유입 항목과 별개다» | 중복 0 |
| R-0411 rev3 ↔ R-3444 ↔ R-3445 ③ | 금지 조건의 단일 출처 = b57 목록 · R-3444 는 참조 · R-3445 ③ 은 절차 의무(«exit 0 을 얻는다»)만 | rv3-B B-3 처방대로 3중 진술 해소 |
| R-3424/R-3426(architect b33/b35) | R-3425 rev2·R-3427 rev3 가 건드리지 않음 | 충돌 0 |

## ⑥ 반영 목록(문면·그래프 수정 필요 항목 — 정확한 old→new)

그래프 소유 절이므로 전부 ttl 정본 → `ontology_render.py --apply` → codex 손 미러 → LEDGER 재기준선(command s006·s007 · architect s005 각 +1행) 경로. rev1/rev4 가 같은 배치 안 미배포이므로 in-place(R-3427 rev2 in-place 선례 `LEDGER.tsv:1559`) — ExpressionShape 불변.

1. **[MAJOR 5B-1] `ontology/rules/command-dddjango.ttl:3719` (s007/b59 text)** — 둘 중 하나. 권고 (a) 규범을 실행기에 맞춘다:
   old `마지막 판정 <green|skip|실존 결손 M|귀속 N(처분 전건) · 실존 결손 M>` → new `마지막 판정 <green|skip|red N(처분 전건)>[ · 실존 결손 M]`(실행기 `short` 문법 `design_pregate.py:1747-1751` 그대로). 렌더 후 md 169 · codex SKILL.md 186 손 미러 · LEDGER s007 재기준선. rulepack 은 본문 미동봉이라 불변.
   대안 (b) 실행기 `design_pregate.py:1747` `short = f"red {attributed}(…"` → `f"귀속 {attributed}(…"` + 픽스처 문자열(`pregate_fixture_run.py` check-report 묶음) + codex byte 미러 — A 축 합의 필요. 어느 쪽이든 계획 Δ1 E5′ ↔ Δ2 R-3444 의 표기 불일치를 계획에도 한 줄 정정.
2. **[MINOR 5B-2] `command-dddjango.ttl:3327` (s006/b9 text)** — old `를 pregate-report 에 아래 «처분 행 정형»(산출물 위치 절)으로 기재하고` → new `를 pregate-report 에 위 «처분 행 정형»(산출물 위치 절)으로 기재하고`. 렌더 md 96 · codex 114(병렬 어절 4 hunk 보존) · LEDGER s006.
3. **[MINOR 5B-3] `agent-design-architect.ttl:2108` (s005/b34 text)** — old `· \`--base\` 기준선은 이동하지 않으므로 기실현 remove 는 실존이다 — 이미 지워진 경로의 행은 거둔다)` → new `· \`--base\` 기준선은 이동하지 않으므로(R-3445 ②) 기실현 remove 는 실존이다 · 기준선에도 없는(승인 전에 이미 지워진) 경로는 remove 행을 거둔다)`. 렌더 md 88 · codex architect 82(byte 동일 유지) · LEDGER architect s005.
4. **[MINOR 5B-4] `command-dddjango.ttl:2846` R-3433 prefLabel** — old(147자) → new(113자) `차단 모드 red 처분 — red 반송 의무 · 배너 근거 --check-report exit 0 · 예외 = 귀속 red 전건 ignored(빚)|filtered · path 등급 filtered 불가`. `make rulepack` + codex rulepack byte 미러. (도구는 통과하므로 사용자 선택 — 결정 불능 2.)
5. **[MINOR 5B-5] `command-dddjango.ttl:3719` (s007/b59 text)** — old `Phase 1 pre-gate 문단의 한정(구형 명세 · 변경 0 레인)에 드는 레인은` → new `Phase 1 «캐시 skip·재발화 판형» ③ 의 한정(구형 명세 · 변경 0 레인)에 드는 레인은`. 1번과 같은 블록 — 한 번에.
6. **[선택 5B-11ⓐ] `command-dddjango.ttl:2926` R-3438 prefLabel** — old `처분 행 정형(백틱 ID → **라벨**(증거))` → new `처분 행 정형(백틱 ID → 굵은 라벨(증거))`. rulepack 재생성 동반.
7. **[선택 5B-11ⓑ] `workspace/eval/pregate-promotion/codex-mirror-diff.md:8-9`** — «대응 행 없음(codex 병렬 문면 상이 — 수동 확인)» → «codex 62 `- ` 불릿 = Claude 58 의 «**G1/G1′ 배너에는…» 꼬리 · 꼬리 byte 동일(이번 변경 전부 꼬리 안)».
8. **[선택 5B-11ⓒ] `ontology/LEDGER.tsv` s006 note** — 다음 재기준선 행(2번)에 «양방향 비대체 문장은 R-3433 소유(R-3434 는 pre-gate↛G2 방향만) · §3-G add 규칙은 b10 ② 의 architect 독자용 이중 진술» 병기(rv3-B ④-14).
9. **[선택] `workspace/design/2026-09-01-pregate-design.md:86,103`** — 문장 끝에 «(승격 후: §10 M2 · R-3433 rev4)» 포인터. 역사 기록이라 미수정도 적법.

## 결정 불능 잔여(사용자·A 축 결정 필요)

1. **5B-1 정정 방향** — (a) 규범 토큰을 실행기 `red N(처분 전건)` 에 맞출지 (b) 실행기·픽스처를 «귀속 N» 으로 바꿀지. 문면 축 권고는 (a)(변경 표면 최소 · G1 1행의 «귀속 N건» 필드와는 다른 행이라 혼동 없음). 실행기 픽스처가 문자열을 단언하는지는 A/C 축 확인.
2. **R-3433 prefLabel 축약 여부** — 147자는 도구 통과·관례 상위 6위. Δ2 의 «≤115자» 를 지킬지(4번 문면) 아니면 Δ2 문자열을 확정본으로 볼지.
3. **R-3425 «이미 지워진 경로의 행은 거둔다» 의 의도** — 3번 문면은 «기준선에도 없는 경로» 한정으로 읽었다. 만약 «기준선 실존·HEAD 부재(기실현 remove)도 다음 개정에서 행을 걷는다» 는 뜻이라면 «실존이다» 와 정면 충돌하므로 그 경우 별도 재작성 필요.
4. **R-3444 참조 표기** — «(… 7번 목록 — «pre-gate 최신성 불비»)» 유지 vs Δ2 문자대로 «— R-0411». 의미 동일 · 취향 결정.
