# pre-gate 온톨로지 개정 계획서 — 절 지도·채번·문면 초안

- 날짜: 2026-09-01 · 브랜치: `norm/pregate`
- 지위: 설계 v3(`workspace/design/2026-09-01-pregate-design.md`) §4(형식 규범 신규 5+조임 2)·§5(파이프라인 삽입 1~7)·D4(트리거·앵커·대체 금지·리포트)의 **성문 계획서**. TTL 저작·집행은 별도 단계 — 이 문서는 Section/Block 배치와 «투영 후 md에 실릴 문면»까지만 확정한다.
- 정찰 근거(실측): `ontology/ISSUED` 말미 = **R-3423**(다음 채번 R-3424부터) · 두 대상 문서 전 절 `sectionOwner = owner-graph` · 블록 order는 절 내 1..n 연속 강제(`ontology_structural_check.py` ③) · 절 신설은 «다음 미사용 서수»만(authoring §14 — 리비전 10호 s018-5 «밀림 0» 실증) · 신규 규범을 기존 블록에 싣는 statesNorm append + 텍스트 확장은 확립 관례(R-3403·R-3422 선례) · Expression 리비전 관례 = `<djr#R-NNNN@YYYY-MM-DD>` + `prov:wasRevisionOf` + `djr:revision n+1` + `djr:revisionKind`(같은 날 2건이면 `@YYYY-MM-DDb` — R-3417 선례).

## 0. 노선 요약

- **절 신설 0** — 설계 §4 말미 조항대로 1차 노선은 기존 절 내 삽입. 블록 신설은 전부 **절 말미 append**(order 말번 부여 — 기존 블록 IRI·order 불변, 밀림 0). 절 중간에 새 불릿을 끼우는 노선(기존 블록 서수 재부여)은 IRI 정체성 churn이라 채택하지 않는다.
- 절 중간에 문장이 «반드시 그 자리»여야 하는 삽입(§5-2·§5-3·Phase 0 amendment·배너 1행)은 **기존 블록 텍스트 확장**으로 실현한다 — 해당 문장을 담는 규범의 Expression 리비전(amendment) 또는 신규 규범 statesNorm append.
- 신규 블록 8 · 신규 규범 채번 15(R-3424~R-3438) · Expression 리비전 5(R-0191·R-0243·R-0287·R-0419·R-0442).

## 1. 절 지도 — 설계 §5 삽입 지점 → Section/Block

두 문서 Section 키 대장(정찰 실측):

| 문서 | 키 | 절 |
|---|---|---|
| command-dddjango | s001 | (전문·front matter) |
| command-dddjango | s002 | ## 산출물 위치 (b1~b7) |
| command-dddjango | s003 | ## 진행 가시성 (b1~b12) |
| command-dddjango | s004 | ## 시작: 모드 판별 |
| command-dddjango | s005 | ## Phase 0 — 요구·스코프 (G0) (b1~b9+) |
| command-dddjango | s006 | ## Phase 1 — 설계 (G1) (b1~b8) |
| command-dddjango | s007 | ## Phase 2 — 구현 (b1~b57) |
| command-dddjango | s008 | ## Phase 3 |
| command-dddjango | s009 | ## 수정 모드 (b1~b6) |
| command-dddjango | s010 | ## 엣지 처리 (b1~b9) |
| command-dddjango | s011 | ## 경계 |
| agent-design-architect | s004 | ## 명세에 담는 것 (인트로 b1~b2뿐) |
| agent-design-architect | s005 | ### Error response contract 12-slot — **본문 불릿·입장 표 전부 여기**(b1~b32) |

주의: architect의 «도메인/계약/패키지·테스트 구조/입장 표» 불릿은 md 헤딩상 «명세에 담는 것» 소속으로 보이지만 그래프에서는 전부 **s005**(b15~b32)다. s004는 인트로 2블록뿐이라 형식 규범의 착지 절은 s005다.

### 삽입 지점 전수표

| # | 설계 근거 | 대상 문서 | Section | Block | 기존 Expression(개정 시) | 개정 종류 |
|---|---|---|---|---|---|---|
| 1 | §5-1 Phase 1 pre-gate 문단 (D1~D4·§5-6 skip) | command-dddjango | s006 | **b9 신설**(말미 append, order 9) | — | 신규 블록 + 신규 규범 5종(R-3432~R-3436) |
| 2 | §5-2 G1 override ②/③ 후 dispatch 전 재실행 | command-dddjango | s006 | b7 텍스트 확장 | `R-0243@2026-08-22`(rev 1) | Expression revision → rev 2 (amendment) |
| 3a | §5-3 Phase 2 step 5 설계 반송 경로 | command-dddjango | s007 | b6 텍스트 확장 | `R-0287@2026-08-22`(rev 1) | Expression revision → rev 2 (amendment) |
| 3b | §5-3 엣지 «Contract mismatch» | command-dddjango | s010 | b6 텍스트 확장 | `R-0442@2026-08-22`(rev 1) | Expression revision → rev 2 (amendment) |
| 3c | §5-3 수정 모드 G1′ | command-dddjango | s009 | b3 텍스트 확장 | `R-0419@2026-08-22`(rev 1) | Expression revision → rev 2 (amendment) |
| 4 | §5-4 Phase 0 amendment (주어 한정) | command-dddjango | s005 | b8 텍스트 교체(문장 1) | `R-0191@2026-08-22`(rev 1 — Prohibition «차분 도구(registry_gate.py) 대체 실행 금지 — Phase 0 측정기가 아니다») | Expression revision → rev 2 (amendment) + prefLabel 교체 — **채번 불요** |
| 5a | §5-5 G1 배너 예보 1행 | command-dddjango | s003 | b10 텍스트 확장 | — | 신규 규범 R-3437 statesNorm append |
| 5b | §5-5 pregate-report 등재 | command-dddjango | s002 | **b8 신설**(말미 append, order 8) | — | 신규 블록 + 신규 규범 R-3438 |
| 6 | §5-6 skip 한정 조항 | command-dddjango | s006 | b9(위 #1에 포함) | — | 신규 규범 R-3436 (Exception) |
| 7 | §5-7 codex 등가 문면 | (온톨로지 밖) | — | — | — | codex 의미 미러 손 반영(§4 체크리스트) |
| 8 | §4 형식 규범 신규 5+조임 2 | agent-design-architect | s005 | **b33~b38 신설**(말미 append, order 33~38) | — | 신규 블록 6 + 신규 규범 8종(R-3424~R-3431) |

- s006/b7의 규범 후보 중 **R-0243**(«override 반영 후에는 ①과 동일하게 Phase 2 진행»)이 정확히 그 문장의 소유자다(동일 블록의 R-0240~R-0246 대조 완료).
- s007/b6은 **R-0287**(«지적 라우팅 — … 입장/설계=architect 경유 반송»), s010/b6은 **R-0442**(«세 mismatch 토큰은 모두 design-architect/G1 반송·G2 차단»), s009/b3은 **R-0419**(«Phase 1 step 5 와 동일하게 입장 표 갱신·배너에 decision 별 owner/path 나열»)가 문장 소유자다.
- 배너 fence 템플릿(s003/b9)은 G0·G1·G2 **공용**이라 건드리지 않는다 — 예보 1행은 G1/G1′ 한정이므로 b10(배너 후속 지시 문단)의 문장 의무로 성문한다.
- s002의 새 등재는 불릿 1개 = 자연 단위 1개 = 블록 1개다. b5(마지막 불릿)와 b6(문단) 사이 삽입은 b6·b7 IRI 밀림이라 기각 — 절 말미 b8 append로 실현하고, 렌더상 두 설명 문단 뒤에 불릿이 온다(허용 — s005/b8 뒤 문단·불릿 혼재 선례와 같은 판형).

## 2. 채번 계획 — R-3424부터 15건 + 리비전 5건

ISSUED append 15행(탭 구분 `R-NNNN\t2026-09-01\trules/<파일>`). 경로 필드: R-3424~R-3431 → `rules/agent-design-architect.ttl`, R-3432~R-3438 → `rules/command-dddjango.ttl`.

### 2.1 신설 — design-architect 형식 규범 (신규 5+조임 2 → 규범 8건)

묶음 결정: 채널별 1규범(신규 1~5 = 5건) + 조임 a·b 각 1건 + **총론 1건**(상시 작성·fail-closed 전사 — 다섯 채널이 공유하는 의무라 채널 규범에 5중 복제하지 않고 한 Work로 성문). 근거: 채널마다 파서 red의 귀속 규범이 달라야 리포트 안정 ID·처분 추적이 서고(§D4), 반대로 fail-closed는 전 채널 공통이라 분리가 «같은 지식 한 출처» 원칙에 맞다.

| ID | deontic | prefLabel(안) | 착지 블록 | rev | wiring(안) |
|---|---|---|---|---|---|
| R-3424 | Obligation | 설계 명세 기계가독 채널 상시 작성 — 산문 추론 0·부재 fail-closed 전사 | s005/b33 | 1 | delegatedTo a/agent-design-architect · enforcedBy c/design_pregate.py |
| R-3425 | Obligation | file-plan 정규 블록 — 1행 1경로·조치 태그·금지 표기·삽화↔블록 차분 | s005/b34 | 1 | 〃 |
| R-3426 | Obligation | 공개 심볼 전수 표기 — Base 닫힌 목록·유도표 생략=규약 준수 확약·계약 필드 목록·중첩 타입 소속 명시 | s005/b35 | 1 | 〃 |
| R-3427 | Obligation | 경계 import 표 — 검사기 판정 관련 경계 import 전부(테스트 파일 포함) | s005/b36 | 1 | 〃 |
| R-3428 | Obligation | 물리 신호 어노테이션 — markers/base/client 정형·무기재=물리 신호 없음 | s005/b37 | 1 | 〃 |
| R-3429 | Obligation | 입장 표 header 영문 정본 6열 고정·셀 내 raw `\|` 금지 (조임 a) | s005/b37 | 1 | 〃 |
| R-3430 | Obligation | 예외 번역표 기계 블록 — published 예외↔raise 창구 표 | s005/b38 | 1 | 〃 |
| R-3431 | Prohibition | machine 마커 concrete 블록 한정 — 템플릿·예시 인용 부착 금지 (조임 b) | s005/b33 | 1 | 〃 |

### 2.2 신설 — Coordinator pre-gate 절차 규범 (7건)

| ID | deontic | prefLabel(안) | 착지 블록 | rev | wiring(안) |
|---|---|---|---|---|---|
| R-3432 | Obligation | pre-gate 실행 의무 — design-spec 내용 변경마다·배너 직전 최종본·override 후 dispatch 전 무조건(+블록 해시 캐시·git 스크립트 내부화) | s006/b9 | 1 | delegatedTo a/command-dddjango |
| R-3433 | Obligation | 관찰 모드 red 처분 — 기록·권고 반송·처분 라벨 corrected\|ignored\|filtered append | s006/b9 | 1 | 〃 |
| R-3434 | Prohibition | 예보의 대체·축약 금지 — Phase 0 빚 스캔·G2 step 6 비대체·build_anchor 불간섭·HEAD 판형 결과의 G2 증거 유용 금지 | s006/b9 | 1 | 〃 |
| R-3435 | Permission | 팬텀 스텁 = 스크립트의 결정적 투영물(격리 사본 한정) — «구현 코드 직접 작성 금지» 경계 비저촉 | s006/b9 | 1 | 〃 |
| R-3436 | Exception | skip 한정 — 형식 규범 시행 전 승인(구형) 명세 한정·블록 존재 구문 검사·차단 승격 시 폐지 | s006/b9 | 1 | 〃 |
| R-3437 | Obligation | G1/G1′ 배너 pre-gate 예보 1행 병기 — 최종본 결속(낡은 green 금지) | s003/b10 | 1 | 〃 |
| R-3438 | Obligation | pre-gate 예보 리포트 등재 — `<산출물 폴더>/pregate-report.md` append·안정 ID·헤더 병기 | s002/b8 | 1 | 〃 |

wiring 메모:
- `enforcedBy <djr#c/design_pregate.py>`를 달려면 `wiring/registry.ttl`에 Checker 개체 신설이 선행한다(`<https://numchida.com/ns/djr#c/design_pregate.py> a djr:Checker`). **결정 플래그**: 온톨로지 배치가 스크립트 실물(§9-1)과 같은 커밋으로 착지하면 enforcedBy 포함이 정직하고, 온톨로지 선행 배치라면 R-3424~R-3431도 delegatedTo만 두고 스크립트 착지 커밋에서 enforcedBy를 추가한다(무소유 Norm 구조검사는 delegatedTo만으로 green).
- Coordinator 절차 규범(R-3432~R-3438)은 R-0191 등 절차 규범 선례대로 delegatedTo만 — 실행기의 exit 매핑(D3)은 스크립트 계약이지 이 규범들의 결정적 집행이 아니다.

### 2.3 리비전 (채번 불요 — Expression rev+1)

| Work | 현행 Expression | 신규 Expression | revisionKind | 대상 문장 |
|---|---|---|---|---|
| R-0191 | `@2026-08-22` rev 1 | `@2026-09-01` rev 2 | amendment | Phase 0 «차분 도구 … 대체 실행 금지» 주어 한정 (§3.4) — prefLabel도 «차분 도구(registry_gate.py) Phase 0 빚 스캔 대체 실행 금지 — 빚 스캔의 측정기가 아니다»로 교체 |
| R-0243 | `@2026-08-22` rev 1 | `@2026-09-01` rev 2 | amendment | override 후 dispatch 전 재실행 (§3.5) |
| R-0287 | `@2026-08-22` rev 1 | `@2026-09-01` rev 2 | amendment | 설계 반송 후 재승인 전 재실행 (§3.6) |
| R-0419 | `@2026-08-22` rev 1 | `@2026-09-01` rev 2 | amendment | G1′ 제시 직전 최종본 재실행 (§3.7) |
| R-0442 | `@2026-08-22` rev 1 | `@2026-09-01` rev 2 | amendment | Contract mismatch 반송 경로 재실행 (§3.8) |

(각 Work의 현행 Expression 날짜는 저작 시 실물 확인 — 위는 정찰 시점 관측값.)

## 3. 문면 초안 — 투영 후 md 본문 전문

### 3.1 command-dddjango s006/b9 — Phase 1 pre-gate 문단 (신규 블록 · R-3432~R-3436)

Phase 1 절 말미(현행 마지막 문단 «Ninja endpoint/error contract … 새 G1을 제시한다.» 뒤)에 다음 문단이 실린다:

> **pre-gate — 설계 명세 결정적 예보(관찰 모드)**: `design-spec.md` 내용이 바뀔 때마다 실행한다 — architect 초안 수신 직후(위 2의 리뷰 다발과 병렬 1회 — 조기 신호), 리뷰 반영·개정 수신마다, 그리고 **G1/G1′ 배너 제시 직전 최종본과 G1 override(②/③) 반영 후 Phase 2 dispatch 전에는 무조건**(배너의 예보 1행은 항상 최종본에 대한 것 — 낡은 green 금지). 실행 판형은 `${CLAUDE_PLUGIN_ROOT}/scripts/design_pregate.py <산출물 폴더>/design-spec.md . --report <산출물 폴더>/pregate-report.md`(타깃 프로젝트 루트 cwd — 기계가독 블록 해시가 불변이면 재실행을 skip한다·캐시가 직렬 비용을 없앤다)이고, 팬텀 스텁·git 호출은 전부 스크립트가 격리 사본(저장소 트리 밖) 위에서 수행하는 **결정적 투영물**이라 «구현 코드 직접 쓰지 않는다» 경계와 충돌하지 않는다 — 너는 이 절차를 위해 bare git 을 직접 치지 않는다. 이 실행은 **예보다**: red 는 게이트 차단이 아니라 pregate-report 기록 + 리뷰 노트와 같은 채널의 architect 반영 **권고**이고(관찰 모드 — 차단 승격 전까지), 명세 개정 승인마다 각 red 의 처분 라벨 `corrected | ignored | filtered` 를 pregate-report 에 append 한다(관찰 모드의 유일한 추가 절차 의무). **예보는 Phase 0 빚 스캔과 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다** — 예보의 기준선은 «스텁 제외 현재 상태»라 `build_anchor` 를 읽지도 쓰지도 않으며, HEAD 판형 게이트 결과를 G2 증거로 유용하는 것은 차분 세탁으로 금지다. green 의 뜻은 «설계 검증됨»이 아니라 «P/S/I급 결정 계약 위반 예보 0»이다(사각 목록·미시뮬레이션 목록은 리포트가 상시 병기). **skip 한정**: file-plan 기계 블록 부재로 실행을 건너뛰는 것은 **형식 규범 시행 전에 승인된 구형 명세에 한한다** — 신규·개정 명세는 블록이 의무이고, 너는 블록 존재를 구문 검사해(리뷰어 노트 구문 검사 판형 준용 — 존재 검사만, 원문 대조는 하지 않는다) 형식 위반이면 architect 에 반송한다. 차단 모드 승격과 함께 이 skip 조항은 폐지된다. *왜* — 승인 명세가 registry 결정 계약과 조인되지 않은 채 동결되면 그 위반은 G1 이후 반송(레인당 평균 ≈34분)으로야 드러난다: 같은 판정 의미론을 승인 전에 결정적으로 돌리면 그 손실이 배너의 예보 1행으로 당겨진다.

문장→Work 대응(저작 검수표용): 트리거·판형·캐시·bare git = R-3432 / 결정적 투영물·경계 비저촉 = R-3435 / red 처분·처분 라벨 = R-3433 / 대체·축약 금지·앵커 불간섭·유용 금지·green 의미 = R-3434 / skip 한정·구문 검사·승격 폐지 = R-3436.

### 3.2 command-dddjango s003/b10 — G1 배너 예보 1행 (텍스트 확장 · R-3437)

현행 b10 말미 문장(대조 앵커):

> …선택·입력된 피드백과 함께 해당 단계를 재실행한다. 사용자가 승인하기 전에는 다음 단계로 넘어가지 않는다.

그 뒤에 append:

> **G1/G1′ 배너에는 pre-gate 예보 1행을 병기한다** — 형식 `pre-gate: 귀속 N건 · 커버 P/S/I · 기준선 <SHA 축약>`(red 0 이면 `귀속 0` · 실체화 0 이면 `실체화 0 — skip` · 구형 명세 skip 이면 `skip(구형 명세)` · 실행 불능이면 그 사실 그대로 — 어느 경우도 침묵 없음). 이 1행은 언제나 **배너 직전 최종본**에 대한 것이다(Phase 1 pre-gate 문단 — 낡은 green 금지).

### 3.3 command-dddjango s002/b8 — 산출물 위치 등재 (신규 블록 · R-3438)

절 말미(현행 «이 `.dddjango/` 산출물은 … 기본은 커밋이다).» 문단 뒤)에 불릿 1행이 실린다:

> - pre-gate 예보 리포트 → `<산출물 폴더>/pregate-report.md` (코디네이터 소유 — Phase 1 pre-gate 실행마다 예보 항목의 안정 ID(경로+규칙번호 해시)와 처분 라벨 `corrected | ignored | filtered` 를 append 하고, 기준선 SHA·프로필·커버 문면·사각 목록을 헤더에 병기한다. `design-spec.md` 와 별개 파일인 이유 — 예보는 명세의 일부가 아니라 명세에 «대한» 관측 기록이라 서로 다른 이유로 바뀐다)

### 3.4 command-dddjango s005/b8 — Phase 0 amendment (R-0191 rev 2)

**개정 전**(현행 원문 — b8 중앙부, 정확 인용):

> **스캔 계약(2026-08-13)**: 도구·TARGET·flag 는 6번 registry 계약 그대로다(루트 TARGET·auto 렌더) — **차분 도구(`registry_gate.py` 등)는 Phase 0 측정기가 아니다(대체 실행 금지 — 그것은 G2 판정기다)**.

**개정 후**:

> **스캔 계약(2026-08-13)**: 도구·TARGET·flag 는 6번 registry 계약 그대로다(루트 TARGET·auto 렌더) — **차분 도구(`registry_gate.py` 등)로 이 빚 스캔을 대체 실행하지 않는다(차분 도구는 빚 스캔의 측정기가 아니라 G2 판정기다 — 이 금지의 주어는 Phase 0 빚 스캔이다: Phase 1 pre-gate 가 격리 사본 위에서 같은 판정기를 예보용 앵커 차분으로 쓰는 것은 이 금지의 대상이 아니다 · 2026-09-01)**.

b8의 나머지 문장(«27종 각각의 exact command·exit …» 이하 — 라운드 2 실증 괄호 포함)은 전부 불변. *왜* — 현행 문면은 «Phase 0 측정기가 아니다»라는 범주 전칭이라, Coordinator 가 Phase 1 에서 pre-gate(내부적으로 registry_gate 앵커 차분)를 부르는 순간 자기모순이 된다(리뷰 레인 2 M3). 주어를 «Phase 0 빚 스캔의 대체 실행»으로 한정하면 원 금지(공허 차분을 «빚 0»으로 오기록하는 사고 차단)는 그대로 서고 pre-gate 와의 충돌만 사라진다.

### 3.5 command-dddjango s006/b7 — G1 결정 처리 (R-0243 rev 2)

**개정 전**(정확 인용):

> ②·③도 override 반영이 끝나면 ①과 동일하게 Phase 2로 진행한다(분기는 결정을 반영하는 절차만 가르고 후속 단계는 같다).

**개정 후**:

> ②·③도 override 반영이 끝나면 ①과 동일하게 Phase 2로 진행한다(분기는 결정을 반영하는 절차만 가르고 후속 단계는 같다 — 단 **dispatch 전에 pre-gate 를 무조건 재실행**한다: 무배너 경로라 예보 착지는 Phase 2 진입 한 줄 상태 + pregate-report 다 · 아래 pre-gate 문단).

### 3.6 command-dddjango s007/b6 — Phase 2 step 5 반송 경로 (R-0287 rev 2)

**개정 전**(정확 인용 — b6 말미 문장):

> 외부 assertion 지적은 acceptance-tester, 내부 assertion과 일반 구현 지적은 coder, 입장/설계 오류는 design-architect를 거쳐 G1/G1′으로 반송한다.

**개정 후**:

> 외부 assertion 지적은 acceptance-tester, 내부 assertion과 일반 구현 지적은 coder, 입장/설계 오류는 design-architect를 거쳐 G1/G1′으로 반송한다(반송으로 `design-spec.md` 가 개정되면 **재승인 전에 Phase 1 pre-gate 를 재실행**하고 예보 1행을 재승인 배너에 병기한다 — Phase 1 pre-gate 문단).

### 3.7 command-dddjango s009/b3 — 수정 모드 G1′ (R-0419 rev 2)

**개정 전**(정확 인용 — b3 둘째 문장):

> Phase 1 step 5와 동일하게 모든 영구 test artifact `add/update/move/split/rename/remove/weaken` 후보의 입장 표를 갱신하고 배너에 `add/update/reuse/retain/remove/reject/pending`을 owner/path와 함께 decision별로 직접 나열한다.

**개정 후**:

> Phase 1 step 5와 동일하게 모든 영구 test artifact `add/update/move/split/rename/remove/weaken` 후보의 입장 표를 갱신하고 배너에 `add/update/reuse/retain/remove/reject/pending`을 owner/path와 함께 decision별로 직접 나열한다. design-spec 개정이 있으면 **G1′ 제시 직전 최종본에 pre-gate 를 재실행**하고 예보 1행을 배너에 병기한다(Phase 1 pre-gate 문단 — 트리거는 수정 모드에도 같다).

### 3.8 command-dddjango s010/b6 — 엣지 Contract mismatch (R-0442 rev 2)

**개정 전**(정확 인용 — b6 첫 문장):

> `TREE_CONTRACT_MISMATCH`, `STOP_FOR_USER_APPROVAL`, `RUNTIME_CONTRACT_MISMATCH`는 모두 design-architect/G1로 반송하고 G2를 차단한다.

**개정 후**:

> `TREE_CONTRACT_MISMATCH`, `STOP_FOR_USER_APPROVAL`, `RUNTIME_CONTRACT_MISMATCH`는 모두 design-architect/G1로 반송하고 G2를 차단한다(반송으로 `design-spec.md` 가 개정되면 재승인 전 Phase 1 pre-gate 재실행이 그대로 적용된다 — 무배너 재승인 경로 포함).

### 3.9 agent-design-architect s005/b33~b38 — 기계가독 채널 형식 규범 (신규 블록 6 · R-3424~R-3431)

절 말미(현행 마지막 문단 «입장 표와 별도로 현재 계약의 유지·변경·종료·부재 의무를 짧게 설명해 …» 뒤)에 다음이 실린다:

**b33 (R-3424 + R-3431):**

> - **기계가독 채널(machine blocks)**(lens 무관, 항상 작성 — 12-slot 부재가 적법한 레인에서도 아래 블록·입장 표 규율은 상시다: 그 사실 자체를 여기 명기해 둔다): 명세의 파일 계획·공개 심볼·경계 import·물리 신호·예외 번역은 산문 서술과 «별개로» 아래 다섯 정본 문법으로 성문한다 — pre-gate(`design_pregate.py`)는 이 채널만을 전사 재료로 쓰고 산문에서 추론하는 재료는 0이다. **채널에 없으면 «부재»로 전사된다(fail-closed)** — 부재가 위반이면 red 가 나는 것이 정답이다(예: 마커 무기재 → «설계가 물리 신호를 안 정했다»는 진탐). `<!-- machine: … -->` 마커는 **concrete 계획 블록에만** 단다 — 표준 140행 템플릿·예시 인용에 달지 않는다(인용과 실계획의 구별이 파서의 유일한 판별 근거다). *왜* — 21레인 실측에서 파일 계획 방언이 6종이라, 형식 규범 없이는 어떤 결정적 파싱도 성립하지 않았다.

**b34 (R-3425):**

> - **파일 계획 정규 블록**: `<!-- machine: file-plan -->` 마커 + ```` ```paths ```` 펜스. 1행 1경로(project-relative)에 조치 태그 `add|update|remove[@Ln]|empty` 를 병기하고 `#` 주석만 허용한다. 브레이스 전개·`·` 병렬·`*`/`…` 축약·미해소 `<placeholder>`·승격 폴더 표기(경로는 언제나 `<칸>.py` — 동명 폴더 승격은 구현 캐스케이드 소유)·**동일 경로의 태그 이중 서술**은 전부 형식 위반이다(이중 서술은 파서 결정 불능을 낳는다). glyph 트리 삽화를 남기려면 블록에서 렌더해 생성하거나 파서의 삽화↔블록 차분 판정을 받는다 — 같은 계획의 이중 표현이 서로 어긋나는 드리프트 축을 봉쇄한다.

**b35 (R-3426):**

> - **공개 심볼 표기**: 자리표시자 실현 파일의 **공개 심볼 전부**를 `경로.py::Symbol(Base)` 꼴로 적는다(«대표 1회»가 아니라 전수다). Base 병기가 의무인 종류는 재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**(소성물 — rulepack 과 함께 재생성)이고, 명명규약으로 유도 가능한 생략은 **성문 유도표**(final.md §1 칸→베이스 결정표) 등재분에 한한다 — **생략 = 규약 준수 확약**이다(생략분은 자동 정규화되어 위반 예보가 불능이 된다: 규약을 벗어날 계획이면 반드시 명기). published-language 칸(contract/·published_error)의 심볼은 **필드 목록**(`code` 필드 유무 포함)을 병기하고, **주 계약이 참조하는 보조·중첩 타입은 소속 파일을 명세가 명시**한다 — 안 박으면 coder 가 즉흥 배치해 예보·판정이 그 파일을 못 본다.

**b36 (R-3427):**

> - **경계 import 표**: 검사기 판정에 관련되는 **경계 import 전부**를 표로 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — 경계만 성문한다(그 밖의 import 는 구현 재량).

**b37 (R-3428 + R-3429):**

> - **물리 신호 어노테이션**: 영구 테스트 입장 표의 `owner/path` 셀 값 뒤에 정형 어노테이션 `[markers: django_db,…] [base: TestCase] [client: yes]` 를 단다 — 테스트 물리 신호(마커·베이스·클라이언트)의 유일한 전사 채널이다. **무기재 = «물리 신호 없음»으로 전사된다(fail-closed)** — 마커를 안 적으면 red 가 그 결손을 알린다. 입장 표 header 는 영문 정본 6열(`candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path`)로 고정하고 셀 안에 raw `|` 를 두지 않는다 — 열 구조가 곧 파서 계약이라, 열이 흔들리면 어노테이션 채널이 통째로 죽는다.

**b38 (R-3430):**

> - **예외 번역표 기계 블록**: 이 명세가 이미 요구하는 예외 번역 산출물(도메인→published 매핑)을 `<!-- machine: exception-map -->` 마커의 `| published 예외 | raise 창구 |` 표로 성문한다 — 번역표에 없는 published 예외는 어느 창구도 raise 하지 않는 «죽은 계약»으로 예보된다.

배치 메모: [신규 4]의 어노테이션은 owner/path **셀 내부** 표기라 기존 입장 표 블록(b28~b30 — 열 정의·header)은 무변경이다(열 구조 불변 — b28 개정 불요, 중복 서술 회피). 입장 표 규율과 기계 채널 규율이 한 절(s005) 안에 있으므로 상호 참조는 렌더 순서로 자연 성립한다.

## 4. 검증 체크리스트 — 이 개정이 건드리는 부속물

| 항목 | 내용 | 예상 규모 |
|---|---|---|
| ISSUED | R-3424~R-3438 append | +15행 |
| LEDGER.tsv 재기준선 | 재투영되는 graph 절 전부 — command-dddjango **s002·s003·s005·s006·s007·s009·s010**(7) + agent-design-architect **s005**(1) | +8행 (`rebaseline:2026-09-01 pre-gate 성문 — R-3424~R-3438 신설·리비전 5건`) |
| target-counts.json | NormShape/WorkShape 3432→**3447**(+15) · ExpressionShape 3500→**3520**(+15 신설 +5 리비전) · BlockShape 2888→**2896**(+8) · SectionShape **545 불변** | diff 사유 병기 의무 |
| q4 골든 | `query_golden_check.py --emit` — distinct_works +15 | rulepack/query-golden.json |
| rulepack | `make rulepack` 재소성(built_from 해시 연동 — 생략 시 verify red). §9-2의 [신규 2] Base 닫힌 목록·유도표 소성물 신설은 구현 배치 소관이나 rulepack 체인 편입을 여기서 예약 | 1회 |
| EXPECTED 하네스 | 검사기 27종 무변경 → checker_baseline/findings_count/cross_matrix **재실측 불요**. `design_pregate.py` 는 `check-*` 패턴이 아니라 checker_registry 로스터↔글롭 동등 assert 비침습(D3). §9-3 드리프트 불변식 하네스(정본 미니 플랜→귀속 0 + 발화 매트릭스 EXPECTED)의 `make verify` 상주 등재는 구현 배치 항목 | 신설 예약 |
| corpus 미러 | **해당 없음** — commands/agents md 는 final.md 코퍼스(11종) 밖이라 `corpus_mirror_sync` 스코프 밖. workspace/reference 소스 미러 교체도 불요 | 0건 |
| codex 의미 미러(손) | ① `codex-dddjango/skills/dddjango/SKILL.md`(Coordinator) — pre-gate 문단·배너 1행·산출물 등재·Phase 0 amendment·반송 경로 문면을 같은 취지로. 병렬 정의가 다르므로 초안-병렬 트리거는 **«스폰 완료 후 wait 수집 전 shell 실행»** 등가 문면(§5-7). ② `codex-dddjango/skills/dddjango-design-architect/SKILL.md` — §3.9 형식 규범 동일 취지(스킬 참조 표기는 codex 이름 접두 주의). 어떤 검사기도 이 드리프트를 못 잡는다 — 누락 시 두 런타임이 정반대 규범 | 2건 |
| codex scripts byte 미러 | `design_pregate.py`+보조 모듈 착지 시 `codex-dddjango/skills/dddjango/scripts/` rsync byte 동일(verify-base `diff -rq`) | 구현 배치 |
| manifest_seal | scripts tree-hash 변경으로 **관찰 릴리즈에서도 재봉인 필요**(`manifest_seal.py --write`) — 승격 릴리즈에서 pipeline 그룹 등재(§9-6) | 1회 |
| spec_lint | 검사기 `#N` 규칙 신설 없음(R- 규범만) → 트리 개정 명세·rule-owner-map·귀속 매핑표 갱신 **불요** | 0건 |
| 게이트·검증 | pre-commit 4단 저작 게이트 → `ontology_render.py --apply command-dddjango` · `--apply agent-design-architect` → `make verify` green | 상시 |

## 5. 주의·저작 단계 결정 플래그

1. **TTL 저작은 이 계획서의 범위 밖** — rdflib 구조 편집 + `ontology_canon` 재직렬화 판형(개정 레시피 1~8단)은 집행 단계가 따른다. 이 문서는 배치·문면의 단일 근거다.
2. 리비전 5건의 현행 Expression 날짜(`@2026-08-22` 가정)는 저작 직전 실물 재확인한다 — 같은 날 재리비전이면 `@2026-09-01b` 접미 관례(R-3417 선례).
3. s006/b9·s002/b8·s005/b33~b38 은 전부 **절 말미 append** — 기존 블록 order·IRI 불변(밀림 0). 렌더 위치가 산문 흐름상 «말미»가 되는 것은 §1 표의 각 배치 메모대로 수용한다.
4. 배너 fence(s003/b9)는 공용 템플릿이라 무변경 — 예보 1행은 b10 의 G1/G1′ 한정 의무로만 성문한다(G0·G2 배너 오염 방지).
5. enforcedBy 부착 시점(스크립트 실물 동시 착지 여부)은 §2.2 wiring 메모의 결정 플래그를 따른다 — 사용자 확정 발화 전 임의 확정하지 않는다.
6. 트리거 문면의 재진술 4곳(§3.5~3.8)은 신규 Work 를 만들지 않고 **인접 규범의 amendment** 로 실었다(리비전 10호 «한 취지 다규범 rev+1» 선례 — R-0089·R-0683·R-2932·R-0339). 축자 재진술(`djr:restates`)이 아닌 이유: 삽입 문장이 각 경로의 착지(배너/한 줄 상태/무배너)를 달리 말해 축자 쌍이 성립하지 않는다.
