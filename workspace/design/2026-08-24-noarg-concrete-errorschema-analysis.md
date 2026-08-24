# no-arg concrete ErrorSchema 사안 — 원인 규명 (v2 확정)

작성 2026-08-24 · 상태: **v2 — 3인 적대 패널(R1 문면·그래프 / R2 검사기 / R3 정황·논리)
반증 반영 확정본**. 처분 대장은 §6.
발단: kkebi tarot 런 에스컬레이션 요약(사용자 전달) — «표준은 default 기반 무인자 생성을
요구하는데 tarot 코드는 Literal 좁힘(무 default)을 썼고, 게이트가 못 잡았다. 근본 원인은
검사기-문서 갭(규칙이 검사기 27종 어디에도 없음)».

## §0 판정 요지 (TL;DR)

요약본의 **현상 서술은 참**(문면 위반 실재), **원인 진단(«규칙이 검사기 27종 어디에도
없음»)은 인용이 정확하다는 전제 아래 거짓**이다.

- 무인자 규칙의 판정은 **두 검사기에 양분 실재**한다: 소스 계약은 registry #2
  (`check-error-centralization.py:3559-3580` — R-0043)·사용측 계약은 registry #15
  (`check-api-error-controller-contract.py:2944-2945` — R-0684, prepared concrete는
  `not call.args and not call.keywords`). 둘 다 tarot 인용 형태를 red로 잡는 것을
  픽스처 재현으로 실측했다(#2: red 5건 exit 2 · #15: red 3건 exit 2).
- 단 판정 도입은 **2026-08-04 커밋 `4a3c838`**(에스컬레이션 약 3주 전)이다 — v1.x
  릴리즈 15개 태그에는 없고 v2.x 전 태그(요약이 특정한 2.16.0~2.17.2 대역 포함)에
  있다. 그리고 실전 게이트 렌더는 `--anchor`가 의무인데, **앵커 스냅숏 기존분 위반은
  red를 인쇄하고도 exit 0으로 강등**된다(실측). 이 둘을 합치면 «검사기가 발화했지만
  런은 계속 통과»라는, 요약의 관찰과 완전히 양립하는 서사가 성립한다(§3 H-f).
- 요약본이 제안한 «#15에 판정 추가»는 **#2와 #15 자신의 기존 판정 중복 신설**이 된다.
- 수정 방향(L1/L1′/L2)은 결정 게이트다 — 결정 재료는 §5(OpenAPI 광고 실측 매트릭스
  포함). 본 문서는 결정하지 않는다.

## §1 확정 사실 (전부 실물 좌표 근거)

### 1-1. 표준 문면 실재 · 4버전 동일

- 문장 ① `dddjango/skills/implementation-django-ninja/references/final.md:129-132`:
  «known domain/application exception은 컨트롤러가 구체적으로 catch하고, 준비된
  no-arg concrete `ErrorSchema`를 `Status(...)`로 직접 반환한다».
- 문장 ② 같은 파일 `:613-614`: «concrete 오류는 slot 6에서 해당 concrete의 고정값으로
  승인된 모든 required field에 default가 있어 인자 없이 생성한다».
- 두 문장 모두 태그 v2.16.0·v2.17.0·v2.17.1·v2.17.2에서 각 정확 1회 매칭.
- graph-owned 판정은 **현행(2.17.0+) 기준**: 두 문장 모두 graph-owned 절 안(마커
  :106 절·:517 절) — 개정은 rules 리비전 사슬 소관. v2.16.0에서 문장 ①은 마커 밖
  (산문 정본)이었다(R1 실측 — 당시 마커는 §6.1·§6.2 2개뿐).

### 1-2. 그래프 좌표 (규범 특정)

`ontology/rules/implementation-django-ninja-final.ttl`:

| 규범 | 유형 | 라벨 | 진술 블록 | rulepack 검사기 배선 |
|---|---|---|---|---|
| **R-0043** | Obligation | concrete 오류의 무인자 생성(전 required default) | §6.2 b14 (:3241) | check-error-centralization.py |
| **R-0684** | Obligation | known exception의 구체 catch·no-arg concrete ErrorSchema Status 직접 반환 | §2.2 b11 (:2416) | check-api-error-controller-contract.py |
| **R-0041** | Exception | 좁힌 식별자 field의 default 상실 canon 예외(2026-08-15) | §6.2 b14 (:3241) | check-error-centralization.py |

- §6.2 b14 한 블록이 R-0040~R-0046 7개 규범을 문장 1:1 순서 대응으로 진술한다(R1
  검증) — 문면 개정 시 블록 단위로 6개 이웃 규범 문면이 함께 움직인다.
- R-0041은 **BC base의 식별자(ErrorCode) field 한정** — concrete의 비식별자 field에
  적용되지 않는다(R1이 corpus 전 문면으로 반증 시도→실패: command-dddjango.ttl:2999
  «slot 9의 BC base가…», agent-design-review-api R-2672, discipline-reviewer R-1003
  «승인 concrete의 fixed value class default 제공·무인자 생성 가능» 전부 동일 방향).
- «no-arg» 동반 블록(같은 파일): §2.2 exception-path b16(:2453 — R-0691~0693)·
  §6.2 exception-path b17(:3262 — R-0054~0057).
- **동반 규범 가족은 이 파일 한정이 아니다**(R1 전수 스위프): SKILL
  `implementation-django-ninja-skill.ttl:704-716`(R-2920~2922 — b6이 §6.2 b14를
  `djr:restates`로 직접 참조·b7도 관련 4블록 restates) · `agent-coder.ttl:598,646`
  (R-2556 «prepared concrete ErrorSchema의 무인자 생성»·R-2562) ·
  `agent-design-architect.ttl:1803-1845` · `agent-design-review-api.ttl:550,1091`
  (R-2674) · `agent-discipline-reviewer.ttl:1382,2858`(R-1003) ·
  `command-dddjango.ttl:3081,3187`. **L1 계열 개정 시 최소 6개 문서 키의 병렬 규범이
  개정 반경이다.**
- L1′ 관련 선례: 같은 final.md §3.1(:333)에 `event_type: Literal[EventType.X] =
  EventType.X` — **좁힘+default 병존 canon이 이벤트 discriminator에 이미 존재**하고
  `const` 렌더 문면(:336-337)도 있다. 오류 schema 절로의 확장 앵커로 쓸 수 있다.

### 1-3. 판정 실재 — 두 검사기 양분, 단 도입은 3주 전

**소스 계약 — registry #2** `check-error-centralization.py`:
- `:3559-3566` concrete 재선언 field가 required면 «concrete field must have a no-arg
  default» · `:3567-3580` «concrete missing required default» · `:3615-3630`
  discriminator default 계열.
- Coordinator 배선 문면 `dddjango/commands/dddjango.md:116`: registry #2 =
  «Enum/base/concrete/no-arg source contract와 project-wide code inventory» 소유.

**사용측 계약 — registry #15** `check-api-error-controller-contract.py`:
- `:2944-2945` `_constructor_arguments_valid` — prepared concrete는 `not call.args
  and not call.keywords`(무인자 강제). 위반 시 «managed catch must directly construct
  FrameworkErrorSchema and return Status» 계열 발화(R2 실측: controller를 인자 생성으로
  바꾸자 red 3건 exit 2 · BC-base populated 생성은 허용 경계대로 exit 0).
- registry #15 문면(`dddjango.md:129`)도 «direct **no-arg** concrete/event-specific
  BC-base `ErrorSchema`» 소유 명시. wiring `enforcedBy`: R-0684→#15.

**도입 시점(R2·R3 교차 실측)**: 무인자 판정 도입 = `4a3c838` «feat: enforce BC-owned
API error contracts (#1)» **2026-08-04** — 저장소 최초 커밋(`881599f`, 2026-04-26)에서
460커밋 뒤. v1.0.0~v1.2.2 15개 태그에는 판정 0건, v2.x 전 태그에 존재. 요약이 런
대역을 «2.16→2.17.2»로 특정했으므로 **그 대역의 registry 실행이라면 판정은 있었다** —
단 tarot 코드의 «작성» 시점이 08-04 이전이면 §3 H-f의 시간창이 열린다.

### 1-4. 재현 실측 — 무앵커 호출 기준

`error_centralization_code/good` 픽스처 임시 사본에 tarot 인용 형태(식별자
`code: Literal[Enum.X]`·본문 `detail: Literal["…"]`, 무 default)를 주입하고 baseline
matrix CLI(무앵커)로 실행:

- #2: baseline exit 0 → tarot 형태 **exit 2 · red 5건** — 무인자 2건(code·detail) +
  annotation 계열 3건(discriminator annotation/default·field annotation).
- #15(R2): controller 인자 생성 **exit 2 · red 3건**.
- **L1′ 형태(`Literal[값] = 값` 병존)도 #2에서 red 2건** — annotation 계열이 Literal
  좁힘 표현 자체를 공통 annotation 이탈로 판정(무인자·discriminator default는 통과).
- 한정: 이 실측은 **무앵커·analysis-무결 실행** 기준이다. 실전 렌더는 `--anchor` 의무
  (`dddjango.md:109`)이고 앵커 기존분은 exit 0 강등(§3 H-f). analysis 토큰이 하나라도
  남으면 red 미인쇄 exit 1(usage) 전환(R2 실측 — selector 결함 시 판정 유실 경로).
- no-arg finding은 rule=null 계약 라인이라 `[#N]` 매칭 기반 `--legacy-debt-file`로는
  면제 불가(R2·R3 동시 확인 — 빚 목록 침묵 가설은 기각).

### 1-5. OpenAPI 광고 실측 매트릭스 (R3 — ninja 1.6.3·pydantic 2.13.4)

| concrete field 형태 | OpenAPI 광고 | 무인자 생성 |
|---|---|---|
| `Literal[X]` (무 default — tarot형) | **const + required** | 불가 |
| `X_enum = X` (default 보유 — 현행 canon형) | enum $ref + default (const·required 없음) | 가능 |
| `Literal[X] = X` (병존 — L1′형) | **const** + default (required 탈락) | 가능 |

즉 «값 고정(const) 광고 + 무인자 생성»을 동시에 갖는 것은 병존형뿐이다. kkebi 실물
OpenAPI는 미검(§4).

## §2 요약본 주장 대조표

(«참/거짓»은 사용자 전달 요약의 인용·문구가 정확하다는 전제 아래의 판정 — §4)

| # | 요약본 주장 | 판정 | 근거 |
|---|---|---|---|
| 1 | 표준 문면 = default 기반 무인자 생성 | 참 | §1-1 |
| 2 | 4버전(2.16.0~2.17.2) 동일 문면 | 참 | §1-1 |
| 3 | tarot 코드 = Literal 좁힘·무 default·controller 인자 생성 | 미확정(인용 신뢰) | §4 |
| 4 | 문면 위반이다(취지는 충족) | 참 | §1-4 |
| 5 | OpenAPI required 광고 부수효과 | 참(실측 확증) | §1-5 |
| 6 | 근본 원인 = 검사기 27종 어디에도 규칙 미구현 | **거짓** | §1-3 — #2·#15 양분 실재 |
| 7 | 그래서 어떤 registry 실행에서도 red 없었다 | **인과 거짓·관찰은 조건부 양립** | red «인쇄»는 있었을 수 있다 — exit 기준 관찰이면 H-f와 양립(§3) |
| 8 | 1런 리뷰가 Literal을 취지 충족으로 읽고 통과 | 미확정 | kkebi 기록 접근 불가 |
| 9 | 수정 = check-api-error-controller-contract에 판정 추가 | **부적절** | #2와 #15 자신의 기존 판정 중복 신설(§1-3) |

## §3 진짜 미해명 지점 — «왜 tarot 런에서 통과했나»

두 검사기가 모두 잡는다는 실측(§1-4)과 «red로 찍힌 적 없다»는 요약 관찰이 동시에
성립하려면 **#2와 #15가 동시에 침묵(또는 강등)**해야 한다. 가설(패널 반영 재구성):

- **H-f. 앵커 차분 강등(유력 — 유일하게 두 검사기를 한 번에 설명)**: 실전 렌더는
  registry #2·#15·#6·#5에 `--anchor`(기능 폴더 `build_anchor` — 1회 기록·재기록 금지)
  를 의무 렌더하고, **앵커 스냅숏 기존분 위반은 red 전문 인쇄 후 exit 0**이다
  (`anchor_diff.py:275-304` · R2 실측 재현). tarot의 bc_error_schema.py·controller가
  build_anchor 생성 이전부터 존재했다면 — 특히 **판정 신설(08-04) 이전에 작성된
  코드라면**(§1-3) — 이후 모든 런에서 «발화하되 통과»가 성립한다. exit 기준으로
  집계한 «red 없음» 관찰과 완전 양립.
- **H-b′. 프로필 분류 침묵**: 해당 슬라이스가 Error-response 무관으로 분류돼
  `--error-profile auto`로 돌았거나, error scope가 **preserve-established**로 승인된
  경우 — 둘 다 schema semantics 미적용(#2 독스트링 :4-8 · R2 실측 셋 다 exit 0).
- **H-c. red/exit 소비 오류**: red가 났으나(또는 exit 1 usage 반송) 게이트 판정·기록
  절차에서 유실. analysis-swallow(§1-4 한정)도 이 계열 — selector 결함 시 red 미인쇄
  exit 1.
- **H-d. 실물 상이**: 실제 tarot 코드가 인용과 달라(비-canonical 경로·상속 사슬)
  분석 식별에서 빠짐. 단 canonical 경로의 «미선언»은 침묵이 아니라 시끄러운 exit 1
  반송이다(R2 실측 — v1의 H-a는 이 형태로만 생존: 비-루트 target 실행 또는 exit 1
  오처리).
- **H-e. 관찰 오류**: «115건·51행 목록»이 특정 검사기 산출만 집계. 단 #15도 잡으므로
  (§1-3) 이 가설 단독으로는 성립 조건이 좁다 — tarot controller가 어떤 scope의
  `--controller-module`에도 없었어야 한다.

판별에 필요한 증거(사용자 요청 사항): kkebi tarot 런 G2 로그에서 **registry #2·#15
렌더 명령 원문 + exit + 차분 절 출력(신규분/앵커 기존분/빚 카운트)** — 특히 «앵커
기존분 N건» 라인이 있으면 H-f 즉시 확정. 부차로 tarot `bc_error_schema.py`의 git
최초 커밋 일자(08-04 전후)와 `build_anchor` 생성 시점.

## §4 한계 (정직 고지)

- kkebi-server 디스크 접근 불가(TCC) — tarot 실물 코드·게이트 로그·OpenAPI 산출·
  «115건/51행 목록»은 사용자 인용 의존. §2의 «미확정» 행과 «참/거짓» 판정의 전제
  한정이 그 경계다.
- 재현(§1-4)은 인용 형태의 충실 재구성이며 무앵커 호출 기준이다(실전 렌더 대비
  `--anchor` 부재 — H-f 판별은 재현으로 불가).

## §5 결정 재료 — L1 / L1′ / L2 (문서는 결정하지 않는다)

공통 재작업(어느 canon 변경이든): 검사기 수정 시 codex **byte 미러** 동시 갱신 ·
픽스처 양/음성 재설계 · `checker_baseline_matrix.py` EXPECTED 갱신 · 문면 리비전 시
리비전 사슬 ①~⑩(재투영·미러·rulepack·계수 기대표·LEDGER·봉인) · 동반 규범 가족
6개 문서 키(§1-2).

- **L1 (Literal 무-default 좁힘을 canon 편입)**: 리비전 반경 = R-0043·R-0684 + 동반
  가족(§1-2). 검사기 수술 = **#2 판정 4계열 + #15 `_constructor_arguments_valid`
  prepared 분기**(무 default면 무인자 생성이 런타임 불가 → controller 인자 생성을
  허용해야 함 — R-0684의 «no-arg 직접 반환» 문면 자체가 바뀐다). 얻는 것: tarot 무수정·
  const+required 광고. 잃는 것: «무인자 생성» 계약의 단순성 전면 해체·최대 수술 반경.
- **L1′ (Literal+default 병존형을 canon «추가»)**: 무인자 계약 불변(R-0043·R-0684
  존치) — 리비전은 «병존형도 canon» 명확화(§3.1 이벤트 discriminator 선례 :333이
  문면 앵커). 검사기 수술 = #2 annotation 계열 2건만(무인자·#15 무수정). tarot는
  `= 값` 추가(field당 1토큰). OpenAPI: const 유지·required만 탈락(§1-5 — «값 고정
  광고»는 보존되는 유일한 무인자 호환형).
- **L2 (표준 유지 — 코드를 현행 canon형으로)**: 플러그인 전면 무수정. tarot를
  `code: TarotErrorCode = X`·`message: str = "…"` 형태로 수정(주의: 병존형
  `Literal[X] = X`는 현행 검사기 red라 **L2에서는 쓸 수 없다** — 검사기 무수정이
  L2의 정의). 잃는 것: OpenAPI에서 required와 **const(값 고정 광고) 둘 다** 상실
  (§1-5 매트릭스).

재발 방지 축: 수정 지점의 정체는 §3 해소에 달렸다 — H-f면 검사기·preflight가 아니라
**앵커 기존분 보고의 소비 규율**(강등 라인을 사람이 읽고 처분하는 절차)이 지점이고,
L1 계열을 택하면 그 런의 침묵은 소급적으로 canon-정합이 되어 «재발»의 정의 자체가
바뀐다. 요약본의 «#15에 판정 추가»는 어느 갈래에서도 지점이 아니다.

## §6 처분 대장 (패널 발견 23건 — 채택 23 · 기각 0)

| # | 렌즈 | 수위 | 발견 | 처분 |
|---|---|---|---|---|
| 1 | R2·R3 | blocker | «최초 커밋부터 실재·전 릴리즈 존재» 사실 오류(도입=08-04 `4a3c838`·v1.x 15태그 부재) | §0·§1-3 정정·구버전 기각 논거 재구성 |
| 2 | R2 | blocker | #15 controller측 무인자 판정 실재(`:2944-2945`) — «#15 항목 없음 참» 양보 철회 | §0·§1-3·§2#9 양분 실재로 재서술 |
| 3 | R2·R3 | blocker/major | `--anchor` 차분 강등 lane(발화·exit 0) 누락 — 재현이 실전 렌더 미대표 | §3 H-f 신설·§1-4 한정 명기 |
| 4 | R1 | major | 동반 규범 가족 6개 문서 키 과소 산정 | §1-2 전수 반영·§5 공통 재작업 |
| 5 | R1 | major | :2453·:3262 절 귀속 교차 오기 | §1-2 정정(b16/b17·R-0691~93/R-0054~57) |
| 6 | R1 | major | «중복 신설 — 소유자 #2» 단정과 R-0684→#15 배선 긴장 | §1-3 이원 소유로 재서술(#2 발견과 합치) |
| 7 | R2 | major | H-a «미선언=침묵» 오류 — canonical 미선언은 exit 1 반송 | §3 H-d로 흡수·생존형 한정 |
| 8 | R3 | major | L1 수술 범위에 #15 prepared 분기 누락 | §5 L1 재산정 |
| 9 | R3 | major | L2 괄호 완화형 자가당착(병존형은 현행 red)·const 상실 누락 | §5 L2 재서술·§1-5 매트릭스 신설 |
| 10 | R2 | minor | preserve-established 침묵 lane | §3 H-b′ 병합 |
| 11 | R2 | minor | analysis-swallow(red 미인쇄 exit 1) | §1-4 한정·§3 H-c 병합 |
| 12 | R2·R3 | minor | 도입 커밋 문면(«저장소 최초» 아님) | #1에 병합 정정 |
| 13 | R1 | minor | v2.16.0 문장 ① 산문 정본(마커 밖) | §1-1 버전 한정 |
| 14 | R1 | minor | 문장 ② 좌표 :613-614 | §1-1 정정 |
| 15 | R1 | minor | §3.1 병존 canon 선례(:333) 미인용 | §1-2·§5 L1′ 앵커 반영 |
| 16 | R3 | minor | «canon 2형태 병존» 신규성 과장(R-0041 기병존) | §5 L1 문면 완화 |
| 17 | R3 | minor | 기계적 재작업 비용(byte 미러·rulepack·EXPECTED) 누락 | §5 공통 재작업 신설 |
| 18 | R3 | minor | §2 행6·7 한정어 비일관 | §2 머리말 전제 한정 통일 |
| 19 | R3 | minor | «재발 방지 축» 독립성 과장 | §5 말미 완화 |
| 20 | R2 | 유지강화 | 빚 목록(`--legacy-debt-file`) 침묵 가설 — rule=null이라 불가 | §1-4 기각 근거로 수록 |
| 21 | R3 | 유지강화 | OpenAPI 실측 매트릭스(3형태) | §1-5 신설 |
| 22 | R2 | 유지 | dynamic-proof·tree 선점·대상-0 가드는 침묵 lane 아님(실측) | 가설 공간에서 배제 유지 |
| 23 | R1 | 유지 | 좌표·배선·R-0041 한정 해석·b14 7규범 1:1 대응 전건 | §1 유지 |
