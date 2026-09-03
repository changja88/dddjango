# pre-gate 차단 승격 배치 — ② 계획 (2026-09-03 · 범위 확정: ⓐ 승격 + D1 `--check-report` + D2 update 부재 형식 red)

루브릭 `2026-09-03-pregate-promotion-rubric.md` ① 결과와 리뷰 `workspace/eval/pregate-promotion/rv1-{A,B,C}.md`의 처방을 집행 단위로 닫는다. 브랜치 `feat/pregate-enforce`. 릴리즈는 사용자 요청 시까지 보류. 게이트: ③ 계획 적대 리뷰 → «문면 확정» → ④ → ⑤ → ⑥ 감사+재검 → «머지».

## 0. 승격의 실체 (한 문단)

실행기의 판정·exit 는 모드에 의존하지 않는다. «차단»의 실체는 셋이다 — ⓐ Coordinator 규범(R-3433 rev4)의 반송 의무 ⓑ 실행기가 그 의무 이행을 결정적으로 대조하는 `--check-report`(D1) ⓒ 회피 경로 봉쇄(D2 update 부재 형식 red · 블록 부재 형식 red). exit 코드 집합(0/1/2/3/4/5)·라벨 집합·검사기 27종·계약 실존 채널(exit 5 비차단)은 불변이다.

## 1. 실행기 `dddjango/scripts/design_pregate.py` (+ codex byte 미러)

| # | 변경 | 상세 | 근거 |
|---|---|---|---|
| E1 | `MODE = "enforce"` · 모드 문면 | docstring :2 «(관찰 모드)»→«(차단 모드)» · :73-74 exit 4/5 설명(«구형 명세 한정» 삭제·exit 5 «권고·비차단» 유지) · 헤더 3곳 «모드: 차단({MODE})» · 요약 2곳 «모드 차단». 헤더 형식 `· 모드: <라벨>(<MODE>) ·` 유지 | P1 · C-5(러너 문면 고정) |
| E2 | 전 exit 경로 `요약:` 1행 | exit 3(문법)·exit 3(블록 부재)·exit 3(update 부재)에 `요약: 형식 red N건(<사유 종류>) · 기준선 <sha12> · 모드 차단` · exit 1 은 stderr 그대로(실행 불능은 리포트 밖) | B P1 MAJOR · R-3437 «`요약:` 행이 기계 출처» |
| E3 | 블록 부재 → exit 3 | `plan is None` 분기: 판정 `형식 red(블록 부재)` · 사유행 «machine 블록 부재(`<!-- machine: file-plan -->` 없음): 차단 모드는 블록이 의무다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 update · 부재 경로만 add)» · `write_report_stub` 경유(헤더·해시 병기) · return 3 | P2 · P5 |
| E4 | **D2 update/remove 대상 부재 → 형식 red** | `in_baseline`(오버레이 «전» 기준선 실존 집합 — 이미 :1673 계산)으로 판정: `update <p>` 또는 비후행 `remove <p>` 의 p 가 기준선 트리에 없으면 `FormError("update 대상 부재: <p> — 기준선(<sha12>)에 없는 경로는 add 다(재라벨 도피 금지)")` → exit 3. **예외**: 동명 승격 폴더 `<stem>/` 디렉터리가 기준선에 실존하면 실존으로 본다(architect 경로 표기 «언제나 `<칸>.py`»와 정합) · 후행 `remove@Ln` 은 현행 unsimulated 유지 · `empty` 는 현행 유지(새 빈 파일 — 부재가 정상). 오버레이 실존은 판정에 넣지 않는다(미커밋 기실현 add 를 update 로 재라벨한 경우도 기준선 부재라 red — reading run 37 판형 봉쇄) | B BLOCKER · R-3425 amendment 와 1:1 |
| E5 | **D1 `--check-report <report>`** | 출력 전용·git 0회·판정 무접촉(`--block-hash` 와 같은 급). 절차: ⑴ 리포트에서 마지막 `## pre-gate 예보` 절을 취한다(skip 행·처분 절은 절이 아니다) ⑵ 그 절 `- 기준선 SHA:` 행의 `블록 해시 <12hex>` = `block_hash(spec)` 이어야 한다(다르면 «stale») ⑶ `- 판정:` 이 `형식 red` 로 시작하면 «형식 red 미해소» ⑷ `예보 red` 면 `### 예보 항목` 목록의 안정 ID 전건에 대해 그 절 이후 텍스트에 `` `<ID>` `` 와 `**ignored**` 또는 `**filtered**` 를 함께 가진 행이 있어야 한다(`corrected` 는 불인정 — 재실행이 곧 최종본) ⑸ `예보 green`·`skip`·`skip · 계약 실존 결손 N건`·`… 실존 결손 N건` 은 통과. exit 0 = 정합 · 3 = 불비(사유 열거) · 1 = 리포트 부재/절 부재/파싱 불능. `요약: check-report <정합|불비 N건> · 블록 해시 <spec>=<report> · 마지막 판정 <…>` 1행 | B §3-8 · P3·P6 자기 판정 폐쇄 |
| E6 | 사각 목록 번호·문면 | `BLIND_SPOTS` 각 항목 앞에 `S1`~`S9` 번호 · S3 문면 교체: «BC 내부 계층 의존(#92/#93류): 유도 삽입은 규약 준수형이라 예보 불가 · 블록에 기재된 경계 import 는 스텁에 방출되어 예보된다 — **산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖**이다(현장 보고 G)» | A Q3-b · P4 ⓐ 인용 결정성 |
| E7 | codex byte 미러 | `cp` → `codex-dddjango/skills/dddjango/scripts/design_pregate.py` · verify-base-core `diff -rq` | C-9 |

exit 규약(docstring 갱신 문면): `0 green · 2 귀속 red(결손 병기) · 3 형식 red(문법 · 블록 부재 · add 충돌 · update 대상 부재) · 4 skip(실체화 0·결손 0 — 공허 차분 가드) · 5 결손 ≥1 ∧ (귀속 0 ∨ 실체화 0)(권고·비차단) · 1 실행 불능`. `--check-report` 는 `0 정합 · 3 불비 · 1 실행 불능`.

## 2. 규범 (그래프 정본 — 전부 Expression `@2026-09-03b`)

| 규범 | 블록 | 리비전 | 종류 | 변경 |
|---|---|---|---|---|
| R-3433 | command s006/b9 | **rev4** | redefinition | «관찰 모드 red 처분» → «차단 모드 red 처분·반송 의무·처분 전건 예외·filtered 근거 유형(구조 규칙 제외)» — §3-A 문면 |
| R-3436 | command s006/b9 | **rev3** | redefinition | Exception → **Prohibition**(dry-run 통과 시) «machine 블록 부재 skip 금지» — §3-B. 실패 시 유형 유지·문면만 |
| R-3432 | command s006/b9(+ b10 statesNorm 부착) | rev3 | amendment | ③ Phase 2 최신성 — dispatch 전 `--base` 재발화 선행 · G2 전 `--check-report` exit 0 — §3-C |
| **R-3444(신규)** | command s007 신규 블록(b58 뒤) | rev1 | Obligation | G2 배너 «pre-gate 최신성» 1행 + `--check-report` 근거 — §3-D. ISSUED 채번 · wiring delegatedTo 없음(Coordinator 자기 소유 — R-3440 선례 대조) |
| R-3437 | command s003/b10 | rev3 | amendment | 배너 1행 케이스 열거: `skip(구형 명세)` 삭제 · 형식 red → 배너 없음(반송) · `red N건 · 처분 전건 기재` — §3-E |
| R-3438 | command s002/b8 | rev3 | amendment | «skip 행의 종류(캐시 skip·실체화 0)» — 구형 명세 삭제 · 처분 행의 증거 토큰 성문(§3-F) |
| R-3425 | agent-design-architect s005/b34 | rev(+1) | amendment | 태그의 기준선 의미론 — §3-G |

건드리지 않음: R-3434 · R-3435 · R-3439~3441 · R-3424·3426~3431(architect 블록 문법) · 라벨 집합 · exit 코드 집합.

### §3-A R-3433 rev4 (s006/b9 — 문단 안 4곳 교체: 제목 · «예보다…권고» 문장 · «유일한 추가 절차 의무» · skip 조항)

제목: `**pre-gate — 설계 명세 결정적 예보(차단 모드)**`.

«이 실행은 **예보다** … (관찰 모드의 유일한 추가 절차 의무).» 을 다음으로 교체:

> 이 실행은 **게이트다**(차단 모드 — 2026-09-03 승격): 귀속 red(exit 2)·형식 red(exit 3 — 문법·블록 부재·add 충돌·update 대상 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다(`--base` 재발화의 red 도 같다 — G2 앵커 차분은 실물 판정자이지 계획 red 의 대체가 아니다). 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시한다. 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 기재하고 배너 예보 1행에 `red N건 · 처분 전건 기재` 를 병기하는 것뿐이며, 그 기재 완결은 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 의 exit 0 으로 확인한다(자기 판정이 아니다). `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다 — corrected 행에는 «소멸 run 시각 · 블록 해시 전→후» 를 병기한다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 명세 개정 승인마다 각 red 의 처분 라벨을 pregate-report 에 append 한다.

라벨 정의 문장은 유지하되 `filtered` 정의 뒤에 삽입:

> `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(S1~S9) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다.

배너 시점 `ignored` 는 legacy-debt 행 인용만 적법(«G2 귀속 red 해소 트레이스» 증거는 Phase 2 사후 라벨에만) — 기존 ignored 정의 문장에 «(배너 시점에는 후자만 — 전자는 G1 시점에 존재할 수 없다)» 삽입.

skip 조항 «**구형 명세 skip 한정** … 폐지된다.» 은 삭제하고 R-3436 문면(§3-B)으로 대체. «*왜*» 문장은 유지.

prefLabel: `차단 모드 red 처분 — 귀속·형식 red 는 architect 반송 의무 · 배너 예외 = 예보 항목 전건 ignored(빚)|filtered(ⓐ S<n>|ⓑ 실코드 exit 0) + --check-report exit 0 · 구조 규칙은 filtered 불가 · corrected 는 예외 경로 밖`.

### §3-B R-3436 rev3 (같은 블록)

> **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)이며 반송은 위 형식 red 조항을 따른다(캐시 skip(아래 판형 ①)·실체화 0 skip(exit 4 — 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update` · 부재 경로만 `add`).

prefLabel: `pre-gate machine 블록 부재 skip 금지 — 부재 = 형식 red(exit 3) · 구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)`.

### §3-C R-3432 rev3 (s006/b10 에 ③ 추가 · b10 `statesNorm djr:R-3432` 부착)

> ③ **Phase 2 최신성** — Phase 2 중 design-spec 변경(G1′ 반송 개정·정합 개정·설계 진화 전부)은 슬라이스 dispatch 전 ②의 `--base` 재발화가 선행한다(red 면 반송 — 위 문단). G2 배너 직전에는 `scripts/design_pregate.py <산출물 폴더>/design-spec.md . --check-report <산출물 폴더>/pregate-report.md` 를 실행해 exit 0(마지막 예보 절의 블록 해시 = 최종 명세 해시 ∧ 판정 비형식red ∧ red 면 예보 항목 전건 처분 기재)을 얻어야 G2 를 제시한다 — 다르면(stale) 재발화 후 G2 다. skip 행·처분 절의 문자열은 대조 대상이 아니다.

prefLabel 갱신: 기존 + ` · Phase 2 변경은 dispatch 전 재발화 · G2 전 --check-report exit 0`.

### §3-D R-3444 신규 (s007 신규 블록 — b58 다음 order)

> **G2 배너 pre-gate 최신성 1행**(2026-09-03 차단 승격): 7번 G2 배너에 `pre-gate 최신성: 블록 해시 <값> = 리포트 <값> · 마지막 판정 <green|skip|실존 결손 N|red N(처분 전건)>` 1행을 둔다 — 기계 출처는 `--check-report` 의 `요약:` 행이며 exit 0 이 아니면 G2 를 제시하지 않는다(R-3432 ③). 이 행은 legacy 잔존·승인 유입 항목과 별개다.

prefLabel: `G2 배너 pre-gate 최신성 1행 — --check-report 요약 행 기계 출처 · exit 0 아니면 G2 미제시`. wiring: `ontology/wiring/command-dddjango.ttl` 에 R-3440 과 같은 판형(delegatedTo/enforcedBy 유무를 R-3440 행에 맞춘다).

### §3-E R-3437 rev3 (s003/b10 배너 1행 케이스)

`… 실체화 0 이면 \`실체화 0 — skip\`(결손 M>0 이면 …) · 구형 명세 skip 이면 \`skip(구형 명세)\` · 실행 불능이면 그 사실 그대로 — 어느 경우도 침묵 없음)` →
`… 실체화 0 이면 \`실체화 0 — skip\`(결손 M>0 이면 \`실체화 0 · 실존 결손 M건\`) · 형식 red(exit 3 — 블록 부재 포함)면 배너를 제시하지 않는다(반송) · 귀속 red 를 처분 전건 경로로 통과시키면 \`red N건 · 처분 전건 기재\` · 실행 불능이면 그 사실 그대로 — 어느 경우도 침묵 없음)`.

### §3-F R-3438 rev3 (s002/b8)

«skip 행의 종류(캐시 skip·실체화 0·구형 명세)는 관찰 대장 계수에서 합산한다» → «skip 행의 종류(캐시 skip·실체화 0)는 관찰 대장 계수에서 합산한다 · 처분 행은 안정 ID 와 라벨에 증거 토큰(ignored = 빚 파일:행·STOP 경로 · filtered = ⓐ S<n>|ⓑ 실코드 경로 · corrected = 소멸 run·해시 전→후)을 함께 적는다 — `--check-report` 가 이 형식을 읽는다».

### §3-G R-3425 rev (architect s005/b34) — 태그 의미론 추가문

> 태그의 뜻은 기준선(G1 시점 HEAD — Phase 2 재발화 시 `--base` 기준선) 기준이다: `add` = 기준선에 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — 그 경로는 `add` 로 적는다 · 동명 승격 폴더 `<칸>/` 실존은 실존이다) · `remove[@Ln]` = 기준선 실존 경로 · `empty` = 새 빈 파일. 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0 이 나오면 그것이 정답이다(`add` 를 `update` 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다).

codex 의미 미러: `codex-dddjango/skills/dddjango-design-architect/SKILL.md` 해당 문단에 같은 취지(C-15: 현재 81~86행 동형).

## 3. 하네스·픽스처 (`workspace/tools/pregate_fixture_run.py` · `workspace/eval/fixtures/pregate/`)

| # | 항목 |
|---|---|
| H1 | docstring exit 규약 문면 갱신(§1) · «(권고·비차단)» 검사 유지 · 기존 헤더 계수(base 4·p1 1/1·mid 6·imports 1/1/1) 불변 |
| H2 | 묶음 **enforce**(별도 리포트 파일): `noblock-spec.md`(마커 없음 → exit 3 · 판정 `형식 red(블록 부재)` · 헤더 1·해시 병기) · `update-missing-spec.md`(`update` 대상 기준선 부재 → exit 3 «update 대상 부재») · `update-promoted-spec.md`(`update foo.py` · 기준선에 `foo/` 폴더 실존 → exit 0/4 — 예외 고정) · `remove-missing-spec.md`(비후행 remove 부재 → exit 3) |
| H3 | `--check-report` 픽스처 4케이스(합성 리포트 텍스트 — 카탈로그 판형 축소): 정합(green) → 0 · stale(해시 불일치) → 3 · red-미라벨 → 3 · red-corrected-오라벨 → 3 · red-ignored/filtered 전건 → 0 · 형식 red 마지막 → 3 · 처분 절의 무값 «블록 해시 갱신» 문자열 오염 → 파서 무영향 |
| H4 | 유닛: `요약:` 행이 exit 3 두 경로에서 출력됨 · BLIND_SPOTS 번호 S1~S9 · 모드 문자열 «enforce» 헤더 |
| H5 | `gen_pregate_symbol_kinds.py --check` · `reverse_coverage.py`(:139 why 문자열 «관찰 모드» → «차단 모드») · `rulepack_smoke.py` 재확인 |

## 4. 소급 대조 (④ 증거 — 무손실·오차단)

- spring 레인 1~4 최종 design-spec 을 새 실행기로 `--base <G1 기준선 SHA>` 소급 실행(격리 사본 — 라이브 저장소 무변경 · `DJR_FINDINGS_JSON` 격리): 기대 = 귀속 ID 집합 불변 · exit 불변(카탈로그 0 · notification 0 …) · **E4 로 새로 형식 red 가 되는 레인**은 reading(승격 부품 update 계획 · 의도된 판정)뿐이어야 한다 — 다른 레인에서 새 형식 red 가 나오면 E4 예외 정의를 재검토.
- 카탈로그 현 명세 + 현 리포트로 `--check-report` → 기대 exit 3(stale: `cb95a1bddb32` ≠ `6cf8e2ffdfc3`) — 발견 ⑩ 의 기계 재현. 카탈로그 리포트 run 1(#392 red)·run 2 상태에서 처분 절 기재 후 → 기대 통과(corrected 는 불인정이므로 실제로는 재실행 헤더가 최종 — stale 아님 확인).
- kkebi 20 명세: 새 실행기로 1건 실행 → exit 3 «블록 부재» 메시지 실물(첫 메시지 인용용).

## 5. 미러·소성물·봉인·기록

1. rdflib+canon 편집(왕복 byte 동일 선확인) → `ontology_gate.py` → `ontology_render.py --apply command-dddjango` · `--apply agent-design-architect` → LEDGER 재기준선(s002·s003·s006·s007 / architect s005) → `target-counts.json`(ExpressionShape 3548 → 3548+7 = 3555 · NormShape/WorkShape 3452 → 3453) → `query_golden_check.py --emit`(채번 1) → `make rulepack` → rulepack codex 복사(scripts byte 미러) → codex 손 미러(Coordinator SKILL.md 62·81·114·116(+G2 배너 행 182~184) · design-architect SKILL.md) → `manifest_seal.py`: GROUPS.pipeline += `dddjango/scripts/design_pregate.py` · GROUPS.packs += `dddjango/scripts/pregate_symbol_kinds.json` → `--write`(draft) → `make verify` 6/6.
2. 기록: ledger «승격 집행(2026-09-03)» 절(§8 판정 표 v5 — 신판 1+구판 3 이월 근거·효과 문면 교체·중반 계수 미관측·kkebi 20/20 비용 공지·발견 ⑩ 재현값) · 설계 v4 §5-6/§8 ⑵(«기계 대조 스크립트» → «--check-report + 슬라이스·G2 registry 귀속 ∩ 예보 ID 수기 대조 + 근거 파일 첨부»)/§9-6/§10 M2 «v5 집행 추기» · 로드맵 R-1(진행) · 현장 보고 G 행에 «사각 S3 문면 반영·규범 조항은 제보 수정 단계» · 조감도 HTML 행 · `ledger.md:4` «R-3433 rev3» → rev4.
3. 이월 등재: exit 4(실체화 0·결손 0) 픽스처 부재 · 승격 후 첫 실전 레인 = ledger 레인 5 관찰(형식 반송 계수에 «구형 명세 블록 부재 반송»은 별도 계수).

## 6. ③ 계획 적대 리뷰 공격 질문

- A(무손실·판정식): E4 예외(승격 폴더)가 새 도피 경로가 되는가 · E5 ⑷ «절 이후 텍스트» 매칭이 다른 절의 처분 행을 오인하는가(같은 ID 가 다른 run 에서 재발화) · corrected 불인정이 «재실행 → green → 배너» 정상 경로를 막지 않는가 · exit 5 비차단과 «red 가 아닐 때(0·4·5)» 경계.
- B(코퍼스 정합): §3-A~G 문면이 R-3434·R-3435·R-0411·R-0418~0421(s009/b3 재발화 판형)과 중복/충돌 없는가 · R-3444 착지 블록·wiring 판형 · Exception→Prohibition 유형 변경의 렌더/rulepack/spec_lint 영향 · LEDGER 절 5곳.
- C(하네스·소급): H2·H3 픽스처가 기존 헤더 계수를 깨지 않는가 · §4 소급 대조 기대값이 성립하는가(reading 외 레인에서 E4 red 0) · codex 3어절 보존 · manifest 재봉인 순서.
