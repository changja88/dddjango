# rv1-B — pre-gate 차단 승격 배치 ① 적대 리뷰 · 리뷰어 B(패키지 설계·무손실 축) — 2026-09-03

브랜치 `feat/pregate-enforce` · 대상 `workspace/plan/2026-09-03-pregate-promotion-rubric.md` 패키지 초안 P1~P9.
읽기 전용 리뷰(저장소·라이브 저장소 무수정). 실측은 전부 소스 행·라이브 리포트 행으로 인용한다.

공격 축: ⓐ 진짜 검출·게이트 강도·STOP 권한을 하나라도 줄이는가 ⓑ 관찰 모드와 실질 동일한 «이름만 차단»인가 ⓒ 결정 불능 문면을 남기는가.

## 0. 판정 요약

- **BLOCKER 1** — 무손실 판정식의 유일한 실질 손실 경로: 차단 전환은 architect 의 «add → update 재라벨로 실체화 0 도피» 유인을 키우는데, 실행기는 «기준선·오버레이 어디에도 없는 update 대상» 을 판정하지 않는다(`design_pregate.py` L1029~1030 unsimulated 메모뿐 · L1173 은 boundary-imports 소비 행이 있을 때만 ⑴). 레인 R run 37 에서 이미 실측된 도피 경로(ledger L144)라 가설이 아니다. 봉쇄 없이는 «차단» 이 검출 집합을 줄이는 경로가 열린다.
- **MAJOR 5** — P3 예외 경로에 `corrected` 가 들어갈 수 있는 문면(자기모순 라벨로 배너 통과 = 관찰 모드와 동일) · P3 의 주어가 «배너» 라 무배너 재승인·Phase 2 정합 개정이 반송 의무 밖 · P6 해시 동일만 보면 형식 red/예보 red 스텁 헤더도 «최신» · exit 3 및 블록 부재 경로에 `요약:` 행 부재(R-3437 기계 출처 불성립) · architect 규범(R-3425)에 add/update 의 기준선 의미론 부재 → kkebi 형 소급 블록의 형식 red 루프.
- **검증됨** — P1 상수 방식(플래그보다 무손실) · P2 는 «손실» 이 아니라 «비용»(검출 집합 증가) · P4 성질 정의는 자기 집행적이라 결정적 · P5 ID 보존은 코퍼스 정합(rulepack 은 rdf:type 을 싣지 않음·target-counts 유형별 계수 없음) · P8 «why» 정합.
- 과적합 없음: STOP·legacy-debt 의존은 기존 Coordinator 규약이고, kkebi 형은 «형식 규범 이전 명세» 일반 클래스다. P6 의 근거는 1레인이지만 기전(해시 변동·재실행 0)은 일반적이며 라이브에서 재현했다(현 명세 `--block-hash` = `cb95a1bddb32` ≠ 마지막 헤더 `6cf8e2ffdfc3`).
- 결정 게이트로 올릴 것 7건(§4) — 그중 «`--check-report` 기계화 채택» 과 «update 대상 부재 형식 red 신설(exit 규약 코드 불변·사유 추가)» 이 차단의 실체를 가른다.

## 1. P1~P9 표

| # | 판정 | 코퍼스 정합 | 일반화 | 무손실 | 근거(파일:행) | 처방 |
|---|---|---|---|---|---|---|
| P1 MODE 상수 | **검증됨 + MAJOR(부속)** | ○ — 모드 문자열을 파싱하는 도구 0(`workspace/tools/*.py`·`workspace/eval/tools/*.py` grep 결과 없음). 헤더 파서 대상은 `블록 해시 [0-9a-f]{12}` 토큰(`_executor_stamp` L1531~1533)이라 모드 문자열과 독립 | ○ — 설치본 버전 = 모드. 헤더 `dddjango vX.Y.Z` 스탬프(L1533)가 모드 판별 단일 출처 | ○ — `--enforce` 플래그 방식은 «플래그 누락» 이라는 새 사각을 만든다. 상수가 우월 | `design_pregate.py` L112(MODE) · 사용처 5곳 L1545·L1589·L1704·L1711·L1732 — 전부 문자열 · 판정·exit 비의존(main L1606~1741) | ① 문자열 5곳 전환. ② **MAJOR**: exit 3(L1655~1660)·블록 부재 exit 4(L1662~1665) 경로에 `요약:` 행이 없다 — R-3437 «실행기 stdout 의 `요약:` 행이 기계 출처» 가 이 두 경로에서 불성립. 전 exit 경로에 `요약:` 1행 추가(형식 `요약: 형식 red N건(<사유 종류>) · 기준선 <sha12> · 모드 차단`). ③ 선택: `--check-report` (P6 참조) |
| P2 블록 부재 → exit 3 | **검증됨(의도된 비용) + MAJOR(문면 부재)** | ○ — `parse_spec` L635~640 이 `(None, [])` 를 돌려 L1661 분기로 가는 구조라 exit 3 전환은 1분기 교체. 픽스처 러너 docstring L38 exit 규약·헤더 계수 기대(스텁도 `## pre-gate 예보` 헤더를 쓴다 L1584) 갱신 필요 | ○ — kkebi 20/20 구형(마커 0·pregate-report 0 실측) = «형식 규범 이전 승인 명세» 일반 클래스 | ○ — 구형 skip 은 검출 0 이었으므로 exit 3 전환은 검출 집합 증가. **손실이 아니라 비용**: architect 1회전 블록 전사(설계 §10 R3 ≈250행·명세 6~7%). 단 kkebi 형 소급 블록은 기실현 경로가 전부 `update` 라 대개 실체화 0 → exit 4/5 «실체화 0 — skip» 으로 착지 — 이득은 신규 add 가 있을 때만 | `design_pregate.py` L1661~1665 · L1673 `in_baseline`(기준선 실존 add = 형식 red · 픽스처 E4) · kkebi `.dddjango/*/design-spec.md` 20 파일 마커 0 · 표본 342~643행 | ① 판정 문자열을 `형식 red(블록 부재)` 로 분리(문법 형식 red 와 계수 분리 — kkebi 형 churn 지표). ② 발주측 공지 문면은 패키지에 없다 → 실행기 사유행 + Coordinator 반송 문면에 «구형 명세는 블록을 소급 작성한다 — 기준선에 실존하는 경로는 `update`, 부재 경로만 `add`» 명시. ③ R-3425(architect s005/b34)에 태그의 기준선 의미론 병기(P7 ①). ④ exit 3 vs exit 4 파서 구별은 exit 코드 + 스텁 `- 판정:` 행(«형식 red» vs «skip») 으로 결정적 — 검증됨 |
| P3 반송 의무 + 처분 예외 | **MAJOR ×3** | △ — R-3437(s003/b10)의 배너 1행 케이스 열거(`dddjango.md` L58)에 «형식 red» 케이스가 현행에도 없고, P3 의 `red N건 · 처분 전건 기재` 형식도 없다 → s006/b9 ↔ s003/b10 드리프트 | △ — «의무» 가 Coordinator 자기 판정인 한 사전 실효는 없다. 사후 실효는 있다(리포트 append-only: 마지막 헤더 판정 + 라벨 행 존재를 ledger 가 기계 대조 가능) | ✗(현 문면) — ① `corrected` 가 예외 경로에 들어간다: corrected 의 증거는 «다음 실행에서 소멸»(R-3433) → 개정이 있었다면 R-3432 가 재실행을 강제 → 최종본이 곧 재실행. 최종본 red 항목에 corrected 는 자기모순인데 현 문면 «닫힌 처분 라벨» 은 corrected 를 포함해 읽힌다 → «corrected 라고 적고 배너» = 관찰 모드 그대로. ② `ignored` 증거 2종 중 «G2 귀속 red 해소 트레이스» 는 G1 시점에 존재 불가 → 배너 시점 ignored 는 legacy-debt 매칭만 적법. 문면이 이를 안 닫으면 «ignored — G2 에서 확인» 이 통과 문면. ③ 주어가 «G1/G1′ 배너» 라 무배너 재승인(`dddjango.md` L195 «무배너 재승인 경로 포함»)·Phase 2 정합 개정(발견 ⑩)은 반송 의무 밖 | `dddjango.md` L58(R-3437 열거) · L96~99(R-3433 rev2 라벨 정의) · L195 · 카탈로그 `pregate-report.md` L133~136(처분 절 실물: corrected 2 → 재실행 green 헤더가 뒤따름 — corrected 는 언제나 재실행을 동반한다는 실측) | 예외 경로 라벨을 **`ignored(빚: <파일:행> · STOP <경로>) | filtered(ⓐ S<n> | ⓑ <대조 경로>)` 둘로 한정**·corrected 배제 명시. 주어를 «승인·재승인(배너 유무 무관)·슬라이스 dispatch 의 근거» 로 확장. R-3437 에 «형식 red → 배너 제시 불가(라벨 경로 없음 — 안정 ID 부재)» + `red N건 · 처분 전건 기재` 케이스 추가. exit 5 비차단 ↔ exit 2 차단 경계는 «red 가 아닐 때(exit 0·4·5)» 로 결정적 — 단 exit 2 의 «전건» 이 실존 결손(e-ID)까지 포함하는지 불명(§4-2) |
| P4 구조 규칙 정의 | **검증됨 + MINOR** | ○ — 발견 ⑧ #188 사례(ledger L134·L145)가 정확히 이 조항으로 닫힌다 | ○ — 성질 정의가 **자기 집행적**: filtered ⓑ 근거는 «같은 형태 실코드가 그 검사기 exit 0» 인데 경로만으로 판정하는 규칙은 같은 경로면 실코드도 red 라 ⓑ 가 성립 불가, ⓐ 사각 목록(BLIND_SPOTS 9항목 L1503~1528)에 경로 계열 항목 0. 따라서 규칙 번호 전수 열거 없이 결정적 — 단 «판정 입력» 의 기준을 **검사기 소스** 로 못 박아야 한다(«규칙 취지» 로 읽으면 비결정) | ○ — filtered 축소 = 검출 집합 증가 | 후보 집합(소스 실측): `check-layer-skeleton.py` #81 L324 · #58/#314/#393 L306~313 · #488 L232/235/245/346(부재 판정 — 스텁 존재로 해소되는 방향) · #490 L183/189/250/270 / `check-db-table.py` #324/#467 L61 · #318 L466 · #325 L470~477(`is_dir`/`name` 만) / `check-mechanism-ownership.py` #336 L292 · #337 L223(파일 이름 꼴) / `check-usecase-dto-placement.py` #183 L296~299 · #188 L302~309(폴더 집합 차) / `check-port-adapter-pairing.py` #581 L1041 · #576 L1044~1046(stem 짝 = 파일명 집합). **경계 사례**: #392 `check-test-config.py` L399~404 — 경로(factories/) ∧ 내용(factory_boy 부재) → 스텁 의존이라 레인 1 filtered 정당·레인 4 진탐 corrected 가 같은 규칙에서 성립(ledger L33·L14) · #329/#332/#630 apps/Meta 값(정형 보충) · #107 update 대상 미실체화(도구 한계) · #219/#635 존재-하나 규칙(빈 파일 발화 — 스텁 `...` 과 다름, 발견 ⑫) | 문면은 성질 정의 + «예:» 4~6개(#81·#325·#188·#318·#336·#490)로. 전수 열거는 검사기 개정마다 드리프트하므로 금지(소성물로 만들 계획이 없는 한). BLIND_SPOTS 9항목에 번호(S1~S9)를 붙여 ⓐ «인용» 을 결정적으로(실행기 상수 편집·MINOR). #392 를 «경계 사례 — 내용 판정 포함이라 filtered 가능(ⓑ 근거 의무)» 로 예시 병기 |
| P5 R-3436 Exception→Prohibition | **검증됨 + MINOR** | ○ — shapes: Prohibition 은 5형 중 하나(`ontology/shapes/djr-shapes.ttl` L116~120) · rulepack 엔트리는 rdf:type 을 싣지 않음(`rulepack.json` L60719~60732 — agents/aliases/block/…/label/expression 만) → 재생성 시 label·expression 만 변동 · wiring `command-dddjango.ttl` L681 `delegatedTo` 유형 무관 · `target-counts.json` 유형별 계수 없음(NormShape 3452 총계) | ○ | ○ — «캐시 skip·실체화 0 skip 과 구별» 은 R-3432·exit 4 와 중복이 아니라 참조. 단 R-3436 rev2 와 R-3433 rev3 가 둘 다 «블록 부재 = 형식 red = 반송» 을 말하면 같은 지식 2출처 | `command-dddjango.ttl` L2867~2879 · revision-redefinition 선례 12파일(R-0180 L443~455 는 Obligation 유지 — **rdf:type 변경 선례는 확인 못 함**) · `djr:deprecated` 어휘만(vocab L117) 선례 0 | ID 보존 찬성(rulepack·wiring·LEDGER 참조 보존 + prefLabel 변화로 감사 추적). 소유 정리: R-3436 = «블록 부재 skip 금지»(금지문)만, 반송 의무는 R-3433 이 «형식 red(exit 3 — 블록 부재 포함)» 한 마디로 소유. 유형 변경이 `ontology_render`/`spec_lint`/`hierarchy_check` 를 통과하는지는 dry-run 전 미확정(§4-3) |
| P6 G2 최신성 대조 | **MAJOR** | ○ — (a) 캐시 skip 행: skip 은 «`--block-hash` = 직전 헤더 값» 일 때만이라 skip 행 해시 = 마지막 헤더 해시(항등) → 정합. (b) `--base` 재발화 헤더: `write_report` L1544~1545·`write_report_stub` L1589~1590 모두 `_executor_stamp` 로 해시 병기, `(--base <ref>)` 만 다름 → 정합. **스텁 리포트(형식 red·skip)도 해시 병기 확인** | ○ — 라이브 재현: 카탈로그 현 명세 `--block-hash` = `cb95a1bddb32`, 마지막 헤더(L140) `6cf8e2ffdfc3` → 발견 ⑩ 이 대조 하나로 잡힘 | ✗(현 문면) — 해시 동일만 보면 마지막 헤더가 형식 red(exit 3)·예보 red(exit 2) 스텁이어도 «최신» → G2 통과 | 카탈로그 `pregate-report.md` L4·L47·L91·L140(헤더 4) · L133~136 코디네이터 처분 절에 «블록 해시 갱신» **무값 문자열** 실물 → «마지막 블록 해시 토큰» 파서는 오염됨 | ① «마지막 헤더» = **마지막 `## pre-gate 예보` 절의 `- 기준선 SHA:` 행** 으로 정의(skip 행·처분 절 제외). ② 조건에 «∧ 그 헤더 판정이 red 가 아님(또는 red 전건 닫힌 라벨 — P3 예외)» 병기. ③ 위치: G2 배너 내용은 s007/b57(R-0406~R-0411)이 소유 — R-3432 amendment 만으로는 G2 배너 블록에 그 1행이 없다 → s007/b57 에도 1행 Obligation 병기. ④ 기계화: `--check-report <리포트>` (판정 무접촉·git 0회 — `--block-hash` 와 같은 급)가 P3·P6 의 «자기 판정» 을 하나의 결정적 대조로 닫는다 — 더 무손실(§3-3) |
| P7 산문 정합 | **MAJOR 1 + MINOR** | △ | — | — | ① design-architect md/ttl: «관찰 모드»·«구형» 문자열 0(정합) — 그러나 R-3425(s005/b34 L2096)에 add/update 태그의 **기준선 의미론 부재** → kkebi 형 소급 블록에서 add 오태그 → 기준선 실존 add 형식 red(E4) 루프(MAJOR). ② codex 미러 3곳: `SKILL.md` L62(R-3437 `skip(구형 명세)`)·L81(s002/b8)·L114(s006/b9) + `design_pregate.py` byte 미러(cmp 동일 확인·러너 `CODEX_EXECUTOR` 가드) · codex architect SKILL 마커 문면 1 hit(변경 불요). ③ 픽스처: `pregate_fixture_run.py` L38 exit 규약 문면 · noblock 픽스처 exit 3 · base 묶음 헤더 계수(스텁 헤더 포함 4 → 5). ④ R-3437 케이스 열거(위 P3). ⑤ 설계 정본 §8 ⑵ «skip 레인(구형 명세) 제외»·§5-6·§6 3선 «관찰 모드» — 규범 아님, P9 «v5 추기». ⑥ `docs/work_flow.html` 조감도 «관찰 모드» 문자열 | R-3425 amendment 문면(§3-7) · 나머지는 체크리스트 등재 |
| P8 manifest | **검증됨 + MINOR** | ○ — pipeline 그룹 «why»(`manifest_seal.py` L71~73 «3암이 공유하는 실행 경로») 와 «Coordinator 가 부르는 결정적 실행체» 등재 사유 정합 · registry_gate 도 dddjango 쪽만 등재라 codex 미러 미등재 관례 일관 | ○ | ○ | `manifest_seal.py` L51~100 · L102(rulepack.json 등재 그룹) | `dddjango/scripts/pregate_symbol_kinds.json`(architect 가 소비하는 소성물)이 어느 그룹에도 없음(grep 0) → rulepack.json 과 같은 그룹에 등재 권고 |
| P9 기록 | **검증됨** | — | — | — | ledger 절 구조(L180~198 승격 판정 절 존재) · 로드맵 R-1 행 L37 | «승격 집행» 절에 kkebi 형 비용 공지 문면·발견 ⑩ 재현 수치(해시 2값)·설계 §8 v5 추기 포함 |

## 2. 필답 상세

### 2-1. P1 — 차단의 실체는 어디 있나

- 실행기 판정·exit 는 MODE 에 의존하지 않는다(`main` L1606~1741 전 분기가 gate_exit·defects·mat 만 본다). 따라서 «차단» 의 실체는 100% P3(Coordinator 규범)에 있다. 이것은 결함이 아니라 설계 §10 M2 «모드 표시 = 상수 + 헤더» 의 귀결이다 — 실행기는 «예보기» 이고 게이트는 Coordinator 라는 D4 역할 분리와 일치한다.
- 그러나 «이름만 차단» 을 피하려면 실행기가 Coordinator 의 자기 판정을 **결정적으로 대조할 수 있는 출력** 을 제공해야 한다. 지금 빠진 것 둘: ① exit 3·블록 부재 경로의 `요약:` 부재(위 표) ② 리포트 최신성·라벨 완결성의 결정적 대조(P6 `--check-report`).
- 상수 vs 플래그: 플래그(`--enforce`)는 Coordinator 가 빠뜨리면 관찰 모드로 «조용히» 떨어지는 사각을 만든다 — R-3432 «침묵 없음» 과 반대 방향. 상수 방식은 설치본 버전이 곧 모드라 헤더 스탬프(`dddjango v2.17.16`)로 사후 판별이 결정적이다. 검증됨.
- 리포트 헤더 스탬프 파서 영향: 헤더의 «모드: 관찰(observe)» → «모드: 차단(enforce)» 은 어느 도구도 파싱하지 않는다. 단 ledger 총괄 표는 수기라 «판별 즉시» 를 유지하려면 헤더 형식 자체(`· 모드: <라벨>(<MODE>) ·`)는 바꾸지 말 것.

### 2-2. P2 — 구형 명세 레인은 무엇을 겪나

- 시나리오 (i) 순수 구현 수정(설계 변경 0): pre-gate 트리거 자체가 없다(R-3432 «design-spec 내용 변경마다») → 영향 0.
- 시나리오 (ii) design-spec 개정 동반: G1′ 직전 실행 → `parse_spec` (None, []) → P2 후 exit 3 «블록 부재» → architect 반송. architect 가 소급 블록을 쓸 때 기실현 경로에 `add` 를 달면 L1673 `in_baseline` → «add 충돌(실존)» 형식 red(L999·픽스처 E4) → 재반송. `update` 로 달면 실체화 0(L1029~1030) → exit 4(결손 0) 또는 exit 5(결손 ≥1) → 배너 «실체화 0 — skip». 신규 add 가 있을 때만 예보 표면이 생긴다.
- 따라서 «의도된 손실» 이 아니다 — 구형 skip 의 검출은 0 이었으므로 검출 집합은 단조 증가한다. 대신 «의도된 비용»(architect 1회전) 이 발생하며, 이 비용의 공지 문면이 패키지에 없다. 공지 위치는 셋: 실행기 사유행(L1662 문자열) · Coordinator 반송 문면(R-3433 rev3) · architect 규범(R-3425 태그 의미론).
- 파서 수준 구별: exit 3 ≠ exit 4 는 코드로 결정적. 스텁 리포트 `- 판정:` 행도 «형식 red» / «skip» / «skip · 계약 실존 결손 N건» 으로 결정적(L1583~1596). 단 문법 형식 red 와 블록 부재 형식 red 는 exit·판정 문자열이 같아지므로 ledger 계수 분리를 위해 판정 문자열 `형식 red(블록 부재)` 를 별도로 둘 것.

### 2-3. P3 — 관찰 모드와 무엇이 다른가

관찰 모드: red 여도 배너 제시 → 사후 라벨 append 의무. 차단(초안): red 면 배너 불가, 단 «red 전건 닫힌 라벨 + 근거 기재 + 배너 1행 병기» 면 가능. 차이는 «전건» 과 «배너 전 기재» 뿐이다. 그 차이가 실질이 되려면 라벨 하나하나가 배너 시점에 **증거를 동반**해야 한다. 현 문면의 구멍:

1. `corrected` — 증거가 «다음 실행에서의 소멸» 이므로 corrected 를 적으려면 개정이 있었고, 개정이 있으면 R-3432 가 재실행을 강제하며, 재실행 결과가 곧 «배너 직전 최종본» 이다. 최종본 red 항목에 corrected 라벨은 논리적으로 성립하지 않는다. 카탈로그 실물(L133~136)도 corrected 2건 → 재실행 green 헤더(L138~143) 순서다. 현 문면은 corrected 를 배제하지 않아 «corrected 라 적고 배너» 가 열려 있다 — 이것이 관찰 모드와 실질 동일해지는 첫 구멍.
2. `ignored` — 증거 2종(«G2 귀속 red 해소 트레이스» 또는 «legacy-debt 매칭 기록(STOP 병기)») 중 전자는 G1 시점에 존재할 수 없다. 배너 시점 ignored 는 후자만 적법하다고 못 박지 않으면 «ignored — G2 에서 확인 예정» 이 통과 문면이 된다 — 둘째 구멍. 처방: 배너 시점 ignored 는 빚 목록 행 인용(파일:행) + STOP 문서 경로 필수. 이러면 «빚 매칭 없는 ignored» 는 형태로 불가.
3. `filtered` — P4 가 근거 유형을 닫는다. ⓐ «사각 목록 항목 인용» 은 BLIND_SPOTS 가 번호 없는 산문 9항목이라 인용의 결정성이 약하다 → 항목 번호 부여.
4. «의무» 의 실효 반론에 대한 답: 사전 실효는 Coordinator 자기 판정인 한 없다 — 맞다. 그러나 (a) 리포트가 append-only 이고 마지막 헤더 판정 + 라벨 행이 남으므로 «red 헤더 뒤 배너 = 라벨 행 전건 존재 ∧ 각 행에 증거 토큰» 을 ledger 가 결정적으로 대조할 수 있다(사후 실효). (b) 사전 실효는 `--check-report` 기계화가 유일하다. 채택하지 않으면 P3 는 «자기 판정 규범 + 사후 감사 가능» 수준이며, 관찰 모드보다 강하지만 «차단» 의 이름값은 사후 감사에 의존한다 — 이 점을 결정 브리프에 그대로 적어야 한다.
5. exit 5 비차단 vs exit 2 차단 경계: «최종본 예보가 red 가 아닐 때(exit 0·4·5)» 는 exit 코드로 결정적이다. 단 exit 2 는 «귀속 ≥1 ∧ 결손 병기» 이므로 예외 경로의 «red 전건» 이 실존 결손(e-ID)까지 포함하는지 문면이 말하지 않는다. R-2(exit 5 비차단 유지)와 일관되게 «예보 항목만» 으로 한정해야 한다 — 명시 필요(§4-2).
6. 주어 범위: «G1/G1′ 배너» 만 주어로 두면 무배너 재승인(`dddjango.md` L195)·Phase 2 정합 개정(발견 ⑩ — 배너 없이 명세가 바뀌는 경로)이 반송 의무 밖이다. 주어를 «승인·재승인(배너 유무 무관)·슬라이스 dispatch 의 근거» 로 확장해야 P6 와 맞물린다. 그리고 재발화 red(exit 2)의 처분이 «반송 의무» 인지 «G2 앵커 차분 위임(R-3432 rev2 문면)» 인지 결정해야 한다(§4-7).

### 2-4. P4 — «경로·폴더 존재뿐» 은 결정적 집합인가

- 소스 열거(위 표)에서 순수 경로 규칙은 약 16개(#58·#81·#183·#188·#314·#318·#324·#325·#336·#337·#393·#429/#436·#467·#488·#490·#576·#581). 이 집합은 검사기 개정마다 바뀌므로 문면에 전수 열거를 박으면 드리프트한다. 성질 정의가 결정적인 이유는 정의가 **자기 집행적** 이라는 데 있다: filtered ⓑ 근거(같은 형태 실코드가 exit 0)는 경로 규칙에서 원리적으로 성립하지 않고, ⓐ 근거(사각 목록)엔 경로 계열이 없다. 따라서 «filtered 인데 ⓐ도 ⓑ도 못 대는 항목» 은 곧 구조 규칙 위반 항목이며, 이는 문면이 아니라 근거 요구가 판정한다. 다만 «판정 입력» 의 기준을 **검사기 소스** 로 못 박아야 한다 — Coordinator 가 «규칙 취지» 로 판정하면 #392 같은 혼합 규칙에서 비결정이 된다.
- 경계 사례 3종을 문면에 병기할 가치: #392(경로 ∧ 내용 → 스텁 의존 → filtered 가능·ⓑ 의무) · #488(부재 판정 — 스텁 존재로 해소되는 방향이라 오탐 아님) · #107(update 미실체화 — 도구 한계·ⓐ «미시뮬레이션» 항목 인용으로 filtered).

### 2-5. P5 — ID 보존 vs 폐지

- 코퍼스 정합: 위 표. rdf:type 변경이 렌더·린트 도구를 통과하는지는 선례가 없어 dry-run 전 미확정이다(revision-redefinition 12파일 중 rdf:type 변경 선례 확인 못 함 — R-0180 은 Obligation 유지). `ontology_hierarchy_check.py` 는 `sh:targetClass` 폐포 계수인데 target-counts 에 Exception/Prohibition 항목이 없어 영향 없음.
- 중복/충돌: 「캐시 skip·실체화 0 skip 과 구별」 은 R-3432(캐시 skip)·exit 4(실체화 0) 를 참조하는 문장이라 충돌이 아니다. 대신 R-3436 rev2 와 R-3433 rev3 가 둘 다 «블록 부재 → 형식 red → 반송» 을 서술하면 지식 2출처가 된다. R-3436 은 금지문(«skip 하지 않는다»)만, 반송 의무는 R-3433 의 «형식 red(exit 3)» 일반 조항이 소유하도록 문면을 나눈다.

### 2-6. P6 — 해시 대조의 정합과 구멍

- (a)(b) 정합은 위 표. 스텁 리포트도 헤더에 해시를 쓴다(L1589~1590) — 이것이 오히려 구멍이다: 형식 red 스텁 헤더의 해시가 현 명세와 같으면 «최신» 판정이 나고, 판정 행은 보지 않으므로 G2 가 열린다. «해시 동일 ∧ 판정 비red(또는 red 전건 닫힌 라벨)» 로 조건을 닫아야 한다.
- 파서 정의: «마지막 헤더» 는 «마지막 `## pre-gate 예보` 절의 `- 기준선 SHA:` 행» 이어야 한다. 카탈로그 L133~136 처럼 코디네이터가 리포트 말미에 처분 절을 쓰고 그 안에 «블록 해시 갱신» 같은 무값 문자열을 남기므로, «파일 끝에서 가장 가까운 `블록 해시` 토큰» 파서는 비결정이다.
- 기계화 판정: `--check-report <리포트>` 가 더 무손실이다. 근거 ① Coordinator 자기 판정 2건(P3 라벨 완결·P6 최신성)을 실행기 1회 호출로 결정적 대조 ② `--block-hash` 와 같은 급(판정 무접촉·git 0회·스크래치 0) ③ exit 규약 코드 불변(0 = 정합 · 3 = 불비 — 형식 red 의미 재사용) ④ 픽스처 1개로 회귀 고정. 비용 ≈ 60~80행 + 픽스처. 채택 여부는 결정 게이트(§4-1).
- 위치 드리프트: G2 배너 구성은 s007/b57(R-0406~R-0411)이 소유한다. P6 을 R-3432 amendment 로만 두면 Coordinator 가 G2 배너를 쓸 때 참조하는 블록에 그 1행이 없다.

### 2-7. P7·P8·P9 — 누락 정합 지점

- **R-3425(architect s005/b34) 태그 의미론 부재(MAJOR)**: 실행기는 «기준선 실존 add = 형식 red»(L999·E4) 와 «update 는 파일을 만들지 않는다»(L1030) 를 집행하지만 architect 규범은 태그 목록만 준다. 차단 모드에서 kkebi 형 소급 블록·레인 R 형 add→update 재라벨이 모두 이 공백에서 나온다. amendment 문면은 §3-7.
- codex 미러 3곳(`SKILL.md` L62·L81·L114) + byte 미러 + 픽스처 러너 docstring/기대 + R-3437 열거 + 설계 §8 ⑵ v5 추기 + 조감도. codex architect SKILL 은 변경 불요.
- manifest: `pregate_symbol_kinds.json` 미등재(MINOR).

### 2-8. 전체 — 무손실 판정식과 과적합

- D(observe) = {exit 2 귀속} ∪ {exit 3 형식} ∪ {exit 5 결손} (전건 기록·비차단). 패키지 후 D(enforce): P2 로 «블록 부재» 가 skip(검출 0) → 형식 red(검출 1), P4 로 filtered 축소 → ignored/corrected 증가, P6 로 Phase 2 재실행 의무 → 표본 증가. 즉 D(enforce) ⊇ D(observe).
- **유일한 실질 감소 경로(BLOCKER)**: 차단은 architect 에게 red 회피 유인을 준다. 가장 싼 회피는 add 를 update 로 재라벨해 실체화 0(exit 4 «skip») 으로 떨어지는 것이며, 레인 R run 37 에서 이미 관찰됐다(ledger L144 «기실현 add 24경로를 update 로 재라벨 — 구판 형식 red 회피»). 실행기는 «기준선·오버레이 어디에도 없는 update 대상» 을 형식 red 로 보지 않는다(L1029~1030 unsimulated 메모 · L1173 은 boundary-imports 소비 행이 있을 때만 ⑴). 봉쇄: file-plan `update`/`remove`/`empty` 대상이 사본(기준선 + 오버레이)에 부재하면 형식 red «update 대상 부재 — 이 경로는 add 다»(exit 3 · 파서 수준 · 결정적). `remove(실존 없음)` 은 현재 unsimulated(L1028)인데 같은 논리로 형식 red 가 맞다. 이 신설 없이는 차단이 «실체화 0 도피» 를 유도해 검출 집합을 줄일 수 있다.
- 과적합: STOP 규약(R-0459/R-0460)·legacy-debt 파일·approved-merges 는 spring 이전부터의 Coordinator 규약이라 발주 관행 의존이 아니다. herdr 의존 0. kkebi 형은 «형식 규범 이전 명세» 일반 클래스. P6 근거는 1레인이지만 기전이 일반적이며 라이브에서 재현했다.

## 3. ④ 패키지 수정안 — 문면 초안

### 3-1. P1 실행기 — `요약:` 행 전 경로화 + 판정 문자열 분리

- exit 3(파싱): `요약: 형식 red N건(문법) · 기준선 <sha12> · 모드 차단`
- exit 3(블록 부재 — P2): 판정 `형식 red(블록 부재)` · 사유행 `형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — 구형 명세(형식 규범 이전 승인)는 블록을 소급 작성한다(기준선에 실존하는 경로는 update · 부재 경로만 add)` · `요약: 형식 red 1건(블록 부재) · 기준선 <sha12> · 모드 차단`
- exit 3(신설 — §2-8): `형식 red — update 대상 부재: <경로> — 사본(기준선+오버레이)에 없는 경로는 add 다(재라벨 도피 금지)` · remove(실존 없음)·empty 부재도 같은 사유 계열.
- 헤더 형식은 유지(`· 모드: 차단(enforce) ·`).

### 3-2. P3 R-3433 rev3 (s006/b9) — 문면

> 이 실행은 **게이트다**(차단 모드): 귀속 red(exit 2)·형식 red(exit 3 — 블록 부재·문법·add 충돌·update 대상 부재 전부)는 architect **반송 의무**이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다. 예보가 red 가 아닐 때(exit 0·4·5)만 배너를 제시한다. 반송 없이 배너를 내는 유일한 경로는 **귀속 red(exit 2)의 예보 항목 전건**에 `ignored(빚: <legacy-debt 파일:행> · STOP <문서 경로>)` 또는 `filtered(ⓐ 사각 S<n> | ⓑ <같은 형태 실코드 경로 · 검사기 exit 0>)` 를 pregate-report 에 기재하고 배너 예보 1행에 `red N건 · 처분 전건 기재` 를 병기하는 것뿐이다 — `corrected` 는 이 경로에 없다(corrected 의 증거는 재실행에서의 소멸이라 재실행 결과가 곧 최종본이다). 형식 red 는 안정 ID 가 없으므로 이 경로 자체가 없다. 계약 실존 결손(e-ID)은 이 «전건» 에 들지 않는다(exit 5 비차단 — 별도 게이트). 라벨 집합은 관찰 모드와 같다(예보 항목 `corrected | ignored | filtered` · 실존 `corrected | deferred | filtered`).

### 3-3. P4 (R-3433 rev3 같은 문면 또는 신규 Prohibition R-3444) — 문면

> `filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 번호 인용(S1~S9) ⓑ 같은 형태의 실코드 파일이 해당 검사기에서 exit 0 인 대조 경로. **검사기 소스에서 판정 입력이 경로·폴더·파일 이름의 존재뿐인 구조 규칙**(예: #81 BC 직계 · #325 ORM 산출물 위치 · #188 area 1:1 · #318 driven_layer 자식 · #336 중앙 마이그레이션 · #490 트리 밖 경로)은 스텁 내용과 무관하므로 ⓑ 가 성립할 수 없고 filtered 대상이 아니다 — corrected 또는 ignored+빚 매칭이다. 경로와 내용을 함께 보는 규칙(예: #392 factories/ 의 factory_boy 부재)은 ⓑ 근거를 대면 filtered 가 가능하다.

### 3-4. P5 R-3436 rev2 (Exception → Prohibition · redefinition) — 문면

> **machine 블록 부재 skip 금지**: file-plan 기계 블록 부재로 실행을 건너뛰지 않는다 — 부재는 형식 red(exit 3 «블록 부재»)다(캐시 skip(R-3432)·실체화 0 skip(exit 4 — 공허 차분 가드)과 구별). 신규·개정·구형 명세를 가리지 않는다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 `update`). 반송은 R-3433 의 형식 red 조항을 따른다.

prefLabel: `pre-gate machine 블록 부재 skip 금지 — 부재 = 형식 red(exit 3)·구형 명세 포함(«캐시 skip»·«실체화 0 skip» 과 구별)`.

### 3-5. P6 R-3432 rev3 (amendment) + s007/b57 1행 — 문면

R-3432 추가문:
> ③ **Phase 2 최신성**: Phase 2 중 design-spec 변경(G1′ 반송 개정·정합 개정·설계 진화 전부)은 슬라이스 dispatch 전 `--base <G1 기준선 SHA>` 재발화가 선행한다. G2 배너 직전 최종 design-spec 의 `--block-hash` 값이 pregate-report **마지막 `## pre-gate 예보` 절 헤더**의 `블록 해시` 와 같고 그 헤더의 판정이 red 가 아니어야(또는 R-3433 의 처분 전건 경로) G2 를 제시한다 — skip 행·처분 절의 문자열은 대조 대상이 아니다. 다르면 재발화 후 G2 다.

s007/b57(G2 배너) 추가 1행(R-0406 amendment 또는 신규 Obligation):
> 배너에 `pre-gate 최신성: 블록 해시 <값> = 리포트 <값> · 마지막 판정 <green|skip|결손 N|red N(처분 전건)>` 1행을 둔다.

기계화 채택 시 위 두 문면의 판정 주어를 «`scripts/design_pregate.py <spec> . --check-report <리포트>` exit 0» 으로 바꾼다.

### 3-6. R-3437 rev3 (s003/b10) — 열거 보강

> … · 형식 red(exit 3) 이면 배너를 제시하지 않는다(반송) · 귀속 red 를 처분 전건 경로로 통과시키면 `red N건 · 처분 전건 기재` · 실행 불능이면 그 사실 그대로 — 어느 경우도 침묵 없음. (구형 명세 skip 케이스 삭제)

### 3-7. R-3425 rev (architect s005/b34) — 태그 의미론

> 태그의 뜻은 기준선(G1 시점 HEAD — 재발화 시 `--base`) 기준이다: `add` = 기준선·작업트리 어디에도 없는 경로(실존하면 형식 red «add 충돌») · `update` = 기준선에 실존하는 경로(부재면 형식 red «update 대상 부재» — add 로 적는다) · `remove[@Ln]` = 실존 경로 · `empty` = 새 빈 파일. 구형 명세에 블록을 소급 작성할 때 기실현 경로는 전부 `update` 다 — 실체화 0 이 나오면 그것이 정답이다(add 를 update 로 바꿔 red 를 피하는 것은 형식 red 로 잡힌다).

### 3-8. `--check-report` 사양(선택 — 결정 게이트)

- 입력: `<spec> <repo> --check-report <pregate-report.md>` · 출력 전용 · git 0회.
- 판정: ⑴ 마지막 `## pre-gate 예보` 절 헤더 해시 = `block_hash(spec)` ⑵ 그 절 판정이 «형식 red» 아님 ⑶ 판정이 «예보 red» 면 그 절의 안정 ID 전건에 대해, 그 절 이후에 `<ID> … → **ignored**(빚: …)` 또는 `**filtered**(ⓐ S<n>|ⓑ …)` 행이 존재.
- exit 0 = 정합(«G2/승인 근거 가능») · 3 = 불비(사유 열거 — 형식 red 의미 재사용) · 1 = 실행 불능. `요약:` 1행 동반.
- 픽스처: 카탈로그 판형(헤더 4 + 처분 절)을 축소 합성 — stale·red-미라벨·corrected-오라벨·정합 4케이스.

### 3-9. 기타 체크리스트(P7·P8·P9)

codex `SKILL.md` L62·L81·L114 손 미러 · `design_pregate.py` byte 미러 · 러너 docstring L38 + noblock/update-부재 픽스처 + 헤더 계수 · `pregate_symbol_kinds.json` manifest 등재 · 설계 §8 ⑵ «skip 레인(구형) 제외» 삭제·§6 3선 «차단 모드» v5 추기 · 조감도 «관찰 모드» → «차단 모드» · ledger «승격 집행» 절에 kkebi 형 비용 공지 + 발견 ⑩ 재현값(`6cf8e2ffdfc3`→`cb95a1bddb32`).

## 4. 결정 불능 잔여 (사용자 결정 게이트 항목)

1. **`--check-report` 기계화 채택 여부** — 채택 안 하면 P3·P6 은 «자기 판정 규범 + 사후 감사» 수준이며 «차단» 의 사전 실효는 없다. 채택하면 exit 규약 코드는 불변(0/3/1 재사용)이나 «실행기 판정 추가» 라 «건드리지 않는 것» 목록의 해석이 필요하다.
2. **P3 예외 경로의 «전건» 범위** — 예보 항목만(권고 · R-2 일관) vs 실존 결손 포함.
3. **R-3436 rdf:type 변경(Exception→Prohibition)의 도구 통과 여부** — 선례 0 · `make verify`(render·spec_lint·hierarchy_check) dry-run 으로만 확정 가능. 실패 시 대안 = 유형 유지(Exception 의 부정문 «예외 없음») 또는 신규 ID.
4. **P4 열거 방식** — 성질 정의만 vs «예:» 4~6개 병기(권고) vs 소성물 목록(비권고 — 드리프트 관리 비용).
5. **«update/remove/empty 대상 부재 → 형식 red» 신설** — BLOCKER 봉쇄이나 «exit 규약 불변» 약속의 범위(코드 불변·사유 추가)와 「검사기 27종 불변」 밖의 실행기 판정 추가라는 점을 범위 확정 게이트에서 결정. 미채택 시 차단 모드가 재라벨 도피를 유도한다는 사실을 브리프에 명기.
6. **형식 red(블록 부재)의 판정 문자열 분리** — ledger 계수 분리를 위해 `형식 red(블록 부재)` 권고. 문법 형식 red 와 합산할지.
7. **재발화 red(exit 2)의 처분** — R-3432 rev2 «재발화의 판정자는 G2 앵커 차분» 과 P3 «red 는 dispatch 근거 불가» 의 긴장. 권고 = dispatch 전 반송 의무(G2 앵커 차분은 실물 판정자, 재발화는 계획 판정자 — 둘은 대체 관계가 아니다). 이 결정 없이는 발견 ⑩ 집행선(P6)이 «재실행은 하되 red 여도 진행» 으로 읽힌다.

Serena: skipped — 읽기 전용 리뷰·`.serena/project.yml` 없음(기본 도구 grep/sed 로 충분).
