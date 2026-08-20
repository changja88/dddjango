# 선행 설계 리뷰 레인 AP — T2-4 선별·공정 통제 판단표 반증 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 **아직 한 줄도 구현되지 않은** 설계 판단표의 오류를 실증하라. 칭찬·요약 금지 — 결함만. 모든 주장에 **파일:행 인용 또는 재현 명령**을 붙여라.

## 리뷰 대상

`workspace/design/2026-08-20-ontology-t2-4-design.md` — SPARQL 규칙 팩(P1~P8) + 질의 카탈로그 4종(Q1~Q4) + C암 selector 배선·B/C 공정 통제(R1~R7) + 검증 자산(V1~V6).

**먼저 §1 실물 좌표(M1~M15)와 §7 자인 약점(W1~W12)을 읽어라** — 저자의 실측 근거와 자신 없는 지점이 거기 공개돼 있다. **자인된 약점을 그대로 되읊는 것은 발견이 아니다.** 자인의 **처분이 불충분함을 실증**하거나, 자인 목록에 **없는** 결함을 찾아라.

## 재료 좌표

- 그래프 정본: `ontology/rules/*.ttl`(2문서) · `ontology/wiring/*.ttl`(배선·alias) · `ontology/vocab/djr.ttl` · `ontology/shapes/djr-shapes.ttl` · `ontology/ISSUED`
- 질의 엔진: `.venv/bin/python`(rdflib 7.6.0 — 시스템 python3에는 없다). 실측 재현은 이 인터프리터로 하라.
- 주입 코어(T2-3 산출·**변경 금지 대상**): `dddjango/scripts/regen_core.py` — `FIELDS`·`assemble_prompt`·`select_records`·`identity`
- 게이트 sidecar: `dddjango/scripts/registry_gate.py`(`--introduced-json`·`gate-introduced/0`) · `dddjango/scripts/findings.py`(`_emit` 레코드 13필드·`line_of_record`)
- 루프: `workspace/tools/regen_loop_prototype.py` · `workspace/tools/regen_loop_smoke.py` · 절차 정본 `dddjango/commands/dddjango.md` step 6′ · 미러 `codex-dddjango/skills/dddjango/SKILL.md`
- 동결 문면: `workspace/design/2026-08-18-ontology-blueprint-v3.md` §2 E6·E7·E8 · §6(측정·estimand·층화 비대칭·개정 7) · §8 T2 행
- 실험 계획: `workspace/design/2026-08-19-ontology-t2-plan.md` §2 T2-0a/T2-3/T2-4/T2-0b · §5 D9~D13
- 발주 풀: `workspace/eval/ab/T1-order-pool.md`(O-7·O-4·O-5 및 밀착도 판정 기준)
- 선행 판단표: `workspace/design/2026-08-20-ontology-t2-3-design.md` · `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md`
- 규약: `workspace/design/2026-08-19-ontology-autonomous-protocol.md`(R1′ 배치표·R2 개정 2분류·R3 정지 조건)

## 검증 과제 (전부 실측·인용으로)

### 1. R3 처분의 반증 — **최우선**

저자는 「C암 payload에 규범 문면(`norms` 배열)을 추가하는 것」을 **문면 정합형 개정**(정지 불필요)으로 처분했다. 근거 4개(§4-R3의 1~4)를 **각각 원문 실독으로 대조**하고 반박하라.

- 근거 1(「E8의 본문 미동봉은 무접두 #N 축 한정」)은 E8 원문의 문장 구조가 실제로 그 한정을 지지하는가? 「무접두 #N 축의 주입 재료는 …로 한정」 앞에 있는 「위반 피드백 재생성은 «위반된 제약+핵심 맥락만» 간결 주입, **전체 규범 재주입 금지**」가 축 무관 전칭 제약이라면 근거 1은 무너진다. 어느 쪽인지 문면으로 판정하라.
- 근거 3(「폴백 조항의 존재가 재료 차등을 함의한다」)은 §6 원문에서 «재료»가 무엇을 가리키는지 확인하라. 「B암과 동일 재료로 폴백」의 «재료»가 **규칙 팩(선별 결과)**을 뜻한다면 함의는 성립하지 않는다.
- 근거 4(「L-M #6은 교란 통제 요구이지 처치 정의가 아니다」)를 t2-plan §2의 estimand 문면 「**selector만 교체 전제**」와 대조하라. 이 문면이 처치 정의라면 R3은 **방향 변경형**이고 저자는 정지했어야 한다.
- 결론을 «문면 정합형 / 방향 변경형 / 그 자체로 동결 위반» 중 하나로 **명시 판정**하라. 판정에는 어느 조항이 결정적이었는지 밝혀라.

### 2. 대안 ⓐ(엄격 해석)가 정말 «C암 공허»인가

저자는 「C가 `(rule,file,message)`만 쓰면 위반 집합은 게이트가 확정하므로 차이 ≈ 0」이라며 ⓐ를 기각했다. 이 기각을 반박하라.

- `regen_core.select_records`와 `registry_gate._write_introduced`를 실독해, **selector가 위반 집합을 실제로 바꿀 수 있는 자유도**를 전수로 세라(순서·중복 제거·범위 필터·상한·우선순위·`symbol` 단위 병합 등). 자유도가 0이 아니라면 저자의 기각은 과장이다.
- 「같은 위반 목록을 **다르게 정렬·묶어서** 주는 것」만으로 C가 B와 다른 처치가 될 수 있는가? 그것이 «규칙 선별 층»의 원래 뜻일 가능성을 검토하라.

### 3. checker 축의 정밀도 손실 (W3의 처분 불충분성)

- `.venv/bin/python`으로 절×검사기 교차를 재현하고, `check-api-error-controller-contract.py` 위반 **1건**이 발생했을 때 C가 주입하게 될 규범 31건 중 **그 위반과 실제로 관련된 것이 몇 건인지** 문면을 읽고 추정하라.
- E8의 「위반된 제약+핵심 맥락만 / 전체 규범 재주입 금지」 대비 이탈 규모를 정량화하라. 이탈이 크다면 R2 상한(40/14,000)은 **제약이 아니라 이탈의 승인**이다.
- C암이 이 재료로 **B보다 나빠질** 구체 경로를 하나 이상 구성하라(주의 분산·잘못된 규범 준수·무관 파일 수정 유발).

### 4. R2 상한 유도의 순환성

저자는 상한을 「파일럿 최대 축(31규범·13,303자)이 **무손실로 통과하는 최소 상한**」으로 잡았다. 이것이 「상한이 T2에서 아무것도 막지 않는다」와 동치인지 실측으로 보이고, 그렇다면 상한·강등 사슬 3단계(W5·W9)가 **테스트되지 않는 죽은 코드**임을 실증하라. 죽은 코드가 T2-0b manifest에 «사전 등록치»로 봉인되는 것의 문제를 지적하라.

### 5. R4 「B암 프롬프트 byte 불변」의 실물 검증

`regen_core.py`를 실독하고, `build_payload(violations, norms=None)` 신설이 **B 경로 출력을 byte 불변으로 유지할 수 있는지** 코드 수준에서 검증하라.

- 현재 `assemble_prompt`는 `payload(records)`를 직접 부른다. 최상위가 **배열**에서 **객체**로 바뀌면 B의 JSON이 바뀐다. 저자는 「B는 `norms` 키가 없다」고만 썼을 뿐 **최상위 형상이 배열로 유지되는지 명시하지 않았다** — 이 공백이 B암 회귀를 낳는 경로를 구성하라.
- 헤더/푸터에 문장을 조건부로 추가하는 설계가 B 문면에 새는 경로(공백·개행·조건 분기 오류)를 구성하라.
- V3(골든)이 이 결함을 **잡는지** 판정하라. 못 잡으면 무엇을 추가해야 하는지 말하라.

### 6. P1·P2의 배포 경계 정합 — 팩이 실런에 실제로 도달하는가

- DEVLOG 실측(「서브에이전트는 working tree 가 아니라 **설치 cache 에서 로드**」)과 T2-0b 신선도 blocker를 근거로, `dddjango/scripts/rulepack.json`이 **실런 시점에 설치 cache 안에 존재하는지** 검증하라. 현재 cache 상태(버전·파일 목록)를 실측하라.
- 팩이 cache에 없으면 R7(fail-closed)에 의해 C암 18런 중 6런이 **전부 실패**한다. 이 위험이 판단표에 등재돼 있는가? 없다면 blocker로 올려라.
- 팩·조회 모듈의 **codex 미러**(`codex-dddjango/scripts/`) 의무가 판단표에 빠져 있는지 확인하라(T2-3에서 미러 누락이 실제 verify red를 냈다).

### 7. Q1 pathGlob 신규 저작의 선정-처치 독립

- O-7 발주(「재고 부족 409 거절 + 재고 차감 주문 생성 API」)가 만들 파일 경로를 DEVLOG·기존 스모크 산출물에서 실측하라.
- 저자가 제안한 절→층 글롭이 그 경로에 **맞춰 설계될 수 있는 여지**를 지적하고, 독립성을 기계적으로 보장할 절차(예: 글롭을 검사기 로스터의 대상 경로에서 **기계 유도**)를 제시하라.
- `ontology/wiring/paths.ttl` 신설이 E4 4단 게이트·`prefixes.ttl` 등록·`ontology_structural_check`·`ontology_gate`·LEDGER/ISSUED 규율과 충돌하는 지점을 전수로 찾아라.

### 8. 폴백률이 밀착 층에서 처치를 무력화하는가

- O-7이 실제로 유발하는 검사기 red 집합을 기존 스모크 이력(`workspace/eval/`·DEVLOG)에서 실측하고, 그 검사기들이 `enforcedBy`에 걸려 있는 16종 안에 있는지 대조하라.
- 밀착 발주에서조차 폴백률이 높다면 C−B 대비는 **처치가 걸리지 않은 비교**다. 실측 근거로 폴백률을 추정하고, 판정 무효화 문턱(예: 폴백률 > X면 그 런은 uninformative)을 사전 등록할 것을 요구할지 판단하라.

## 산출 형식

발견마다: **ID · 심각도(blocker/major/minor) · 주장 · 실측 근거(인용/명령) · 저자 처분 대비 왜 불충분한가 · 요구 조치**. 마지막에 「저자가 **놓친 축**」 절을 두고, 위 8과제 밖에서 발견한 것을 적어라. 발견이 없으면 없다고 쓰라 — 채우지 마라.
