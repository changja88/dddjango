# aclex 라운드 2 — maj1·min1·maj4 처방 계획 (Claude 완벽화)

> **상태**: 계획 **v2** (2026-06-07) — 적대 리뷰 3렌즈(백스톱 적합성·reviewer 집행력·근본/범위) 반영. v1의 "동형 집행 갭→백스톱 1순위" 진단이 **반증되어 폐기**. 구현 착수 전 미해결 결정(§7) 사용자 확인 필요.
> **배경**: `ACLEX-AB-LIVE-VERDICT.md` 잔여 3건. 채점 정본 `20260607-0412-aclexab-claude.md`·`20260607-0341-aclexab-codex.md`.
> **목표(정정)**: "실패한 처방을 집행으로 고친다"가 **아니라** — maj1은 *첫 dual 라이브에서 런타임 간 갈린 비결정(P4③)을 줄이고*, min1은 *정의 갭을 메우고*, maj4는 *환경 의존이라 보류*한다.

---

## 1. 진단 — v1 폐기, 셋은 *서로 다른 근본*

### 1.0 v1이 틀린 점 (적대 리뷰가 반증)
v1은 maj1·min1·maj4를 "동형 집행 갭(텍스트 충분+미적용+집행 부재)→백스톱 1순위"로 묶었다. **세 렌즈가 이를 반증**:
- **min1 검증 기저 붕괴**: v1이 "known-good"으로 쓴 **Codex가 실제 min1 위반**(`aclexab-codex/schema_in.py:6-7` — `product_id`·`quantity` 둘 다 상한 없음). Claude는 product_id만 누락. **min1에선 Codex가 더 위반** → "Codex식 상한 있는 필드=known-good" 검증 매트릭스가 거짓.
- **maj1 reviewer 방향 오진**: `reviewer:41`이 *이미* transient 렌즈를 갖는데 술어가 "retryable 매핑이 *있음/없음*"이라 Claude "전부 503"을 **'있음'으로 통과**시킨다. v1의 "reviewer:41 완전성 렌즈 확장"은 방향 반대(maj1=과잉매핑↔41=미매핑누수).
- **maj4 근본 오진**: 미발화는 프로즈 약함이 아니라 **fixture design-spec §4.4:242 "sqlite에서도 CHECK 작동·PositiveIntegerField는 sqlite서 CHECK 미생성"이 reviewer에게 합법 면제 제공**(현 sqlite 환경에선 *실제로 구별됨*=미위반, PG에서만 The Liar).
- **"이전 처방 실패" 프레이밍 부정확**: 062a64f는 *처방 커밋*이지 실패한 런이 아니다. 이번이 *첫* dual 검증이고 maj1은 **런타임 간 갈림**(Codex 준수/Claude 미준수)=P4③ 비결정. N=1 "처방 실패" 단정 금지.

### 1.1 재구성된 진단 (셋 분리)
| 결함 | **진짜 근본** | 1차 레버 | 백스톱 적합성 |
|---|---|---|---|
| **maj1** | **salience** — 완성 레시피(`_is_retryable_db_error`)가 88줄 코드블록(`final.md:364-452`)에 묻힘 + **P4③ 비결정**(Codex 준수) | **레시피 salience 승격**(DR-28식) + reviewer:41 술어 교정 | **위태** — 헬퍼 위임이 핸들러 본문 분기를 가려 DR-38식 거짓양성. 보조·정밀도 관문 |
| **min1** | **내용(정의) 갭** — `api §5.1:186`이 "외부 식별자" 1회 언급·**정의 0회** + 집행 갭 | **§5.1 "외부 식별자" 정의 한 줄**(DR-22 예외) → 비대칭 백스톱 | **조건부** — 정의 선행 시 정당화. 정의 없이는 DR-39 거짓양성 |
| **maj4** | **spec 결함 + 환경 의존** — sqlite 미위반(PG-only The Liar). *집행 갭 아님* | **보류**(위반 미발생→검증 불가) | N/A |

> **핵심 교훈**: v1 "백스톱 1순위·텍스트 추가 지양"은 **부분 폐기**. DR-22 "텍스트 추가 금지"는 *중복 문구 강화* 교훈이지 **정의 부재(min1)·salience 묻힘(maj1)**엔 적용 안 됨 — DR-28(C3 salience 승격)·DR-31(음성경계 추가)이 텍스트/배치 개입을 정당화한 전례. 백스톱은 **salience(maj1)·정의(min1) 선행 후, 정밀도 관문을 통과할 때만**.

---

## 2. 결함별 처방 (교정)

### 2.1 maj1 — transient 무판정 503 (salience 1차 + reviewer 교정 + 백스톱 보조)
- **① 레시피 salience 승격**(1차·DR-28식): `implementation-django-ninja §6.2`의 88줄 코드블록에서 `_is_retryable_db_error`와 "클래스 통째 금지·시그니처만"을 **별도 강조 블록·"필수" 마커**로 끌어올림 — 코더가 거대 블록에서 그 부분을 *선택적 예시*로 흘리지 않게.
- **② reviewer:41 술어 교정**(방향 수정·확장 아님): "retryable 매핑이 *있음/없음*"(현행, Claude 통과) → "**`OperationalError` 핸들러가 영구장애 변종을 retryable과 *구별하는 분기 없이* 클래스 통째 503/409 = important**"(과잉매핑 직격).
- **③ 결정적 백스톱**(보조·정밀도 관문 통과 시): `@api.exception_handler(OperationalError|DatabaseError)` **데코레이트** 핸들러 본문에 조건 분기(`ast.If`/`IfExp`/early-return 가드)가 **0개** + retryable status(503/409) 반환 → exit2. **데코레이터 필터로 헬퍼 false positive 차단**. known-limitation 명시: 형식 분기(`if True`)·무조건 헬퍼·status 변수·부모클래스(`Error`)·대안 B는 비대상→reviewer.
- **🔴 미해결**: 헬퍼 위임(`if self._retryable(exc):` — 본문에 분기 있으나 헬퍼가 무조건 True) 거짓양성/음성을 데코레이터 필터로 완전 해결 못 하면 **백스톱 보류·reviewer-only**(DR-38 선례).

### 2.2 min1 — 외부 식별자 상한 (정의 1차 + 비대칭 백스톱)
- **① §5.1 "외부 식별자" 정의 한 줄**(1차·DR-22 예외): "외부 식별자 = 클라이언트가 보내는 조회/참조 키(`*_id`·lookup key); 내부 자동생성 PK·UUID 등 오버플로 무관 타입은 비대상". 정의 없이 휴리스틱부터 짜면 거짓양성 근거 부재.
- **② 결정적 백스톱**(정의 직역): ninja `Schema`의 **`int` 필드 + 하한 제약(`gt`/`ge`) 존재 + 상한(`le`/`lt`) 부재**의 *비대칭*(이름 불문 — `*_id` 휴리스틱 폐기) → exit2. "하한만 신경 쓰고 상한 빠뜨린" 비대칭이 신호. `UUID`/`str`/하한 없는 필드 면제.
- **③ 검증 매트릭스 수정**: **Codex를 known-good에서 제거**(Codex도 위반). 새 known-good 합성(`product_id: int = Field(gt=0, le=2**31-1)`).
- **🔴 미해결**: `Annotated[int, Gt(0)]`·`conint`·`PositiveInt` 우회 저-recall + 상한이 진짜 무의미한 `int+하한` 필드 false positive 잔존 → 정밀도 관문.

### 2.3 maj4 — 동치 가드 구별 (보류 + 예방만)
- **reviewer 프로즈 강화 = 폐기**(DR-22 재현·위반 미발생 환경서 검증 불가).
- **보류**: sqlite fixture 미위반·PG-only The Liar라, **PG 포함 N≥2 라이브에서 실재 확인 후** 처방. 지금 강화는 미검증 자기만족.
- **예방만(선택·낮은 우선)**: `implementation-test`에 "named constraint 검증 테스트는 **constraint name 핀** 또는 strictly-stronger 경계로 — 환경(sqlite/PG) 무관하게 구별"을 레시피로(예방). + (검토) `check-constraint-attribution` 백스톱(name-핀 부재 grep)이 docstring-면제 위양성을 넘기는지 *시험만*.

---

## 3. 검증 계획 (수정)
- **정적**: 백스톱 합성 발화 매트릭스 — **known-good 재합성**(Codex 제외·min1). known-bad(Claude 무판정 503·상한없는 int+하한) exit2 + 면제 경계(헬퍼·UUID·str).
- **salience/정의(텍스트)**: DR-22 교훈상 *텍스트 판별 통과≠라이브 발화* — 라이브로만 실효 확인.
- **라이브 dual 재검증**(DR-30식): 정석 clone fixture·dual `/dddjango` → maj1(salience 후 Claude 준수?)·min1(정의 후 적용?) 발화/적용. **위반 주입**으로 백스톱 차단 확인(준수 런은 미stress).
- **정직**: N=1·P4③. maj1은 salience로 *비결정 폭 축소*가 목표(결정화 아님).

## 4. 미러·정합 (처방 구체화 시 — 렌즈 D 보류분)
- 게이트 카운트 13→(maj1 백스톱 GO 시)14→(min1)15. plugin↔codex byte-identical 미러·plugin.json 버전 범프.
- maj1 백스톱 ↔ ②check-error-centralization 경계 문구 갱신("presentation transient 무판정은 ⑭이 본다").
- 기존 reviewer:41 교정은 *수정*(신규 아님)이라 미러 반영.

---

## 5. 처방 순서 (교정)
1. **maj1**(우선·가용성 영향 최대): salience 승격 → reviewer:41 교정 → 백스톱(정밀도 관문 통과 시).
2. **min1**(동급 이하 — catch-all이 결과 좌우): §5.1 정의 → 비대칭 백스톱.
3. **maj4**: 보류(PG N≥2 후) + 예방 레시피만 검토.

각 단계 후 합성 검증 → 전체 커밋 → 라이브 dual.

---

## 6. 적대 리뷰 종합 (3렌즈 발견)
| # | 렌즈 | 핵심 발견 | 반영 |
|---|---|---|---|
| A1 | 백스톱 | maj1 백스톱은 데코레이터 필터+분기0개로 조건부 GO·헬퍼 위임은 reviewer | §2.1③ |
| A2 | 백스톱 | **min1 known-good(Codex)이 실제 위반**·`*_id` underdetermined | §2.2③·§1.0 |
| B1 | reviewer | maj4 프로즈 salience↑=DR-22 재현 | §2.3 폐기 |
| B3 | reviewer | **maj1 reviewer:41이 방향 오인으로 미발화** | §2.1② |
| B4 | reviewer | **maj4 근본=spec §4.4:242 환경 탈출구**(프로즈로 안 닫힘) | §1.0·§2.3 |
| C1 | 근본 | "동형 집행 갭" 묶음 부정확·셋 근본 다름 | §1.1 |
| C2 | 근본 | **maj1=salience**(88줄 묻힘)·백스톱 헬퍼위임 거짓양성 | §1.1·§2.1① |
| C3 | 근본 | **min1=내용(정의) 갭**(외부식별자 정의 0회) | §2.2① |
| C4 | 범위 | **maj4 보류**(sqlite 미위반)·min1 우선순위 maj1 이하 | §2.3·§5 |
| C5 | 근본 | "이전 처방 실패"→"첫 라이브 비결정" | §1.0 |

---

## 7. 미해결 결정 (사용자 확인)
- **D1 (maj4)**: 보류(렌즈 C — 위반 미발생) vs 예방 레시피+백스톱 시험(렌즈 B — 환경독립). → **보류 권장**(지금 처방은 검증 불가), 환경독립 테스트 레시피는 낮은 우선 예방으로만.
- **D2 (maj1 백스톱)**: salience+reviewer 교정만으로 갈지, 백스톱(③)까지 갈지. 헬퍼 위임 거짓양성이 관문 — **salience+reviewer 먼저, 백스톱은 정밀도 시험 통과 시 추가**.
- **D3 (순서)**: maj1만 먼저 처방→라이브로 salience 효과 보고, min1·maj4는 그 다음 라운드? (작은 단위) vs maj1+min1 묶어서?

---

## 8. 구현 완료 (2026-06-07) — 결정: D1 maj4 보류 · D2 백스톱 ⑭ GO(정밀도 통과) · D3 maj1만 먼저

사용자 "권장대로 진행" + 적대 리뷰 3렌즈 반영. **maj1 3층 처방** 구현·검증 완료(커밋 전).

### 처방 (적대 리뷰 개정 반영)
- **① §6.2 salience**(`implementation-django-ninja/references/final.md`): 코드블록 직전 **"필수 불변식" 박스** 신설 — *결과* 불변식("핸들러 본문이 몇 줄이든 영구장애 구별 분기 필수"·"레시피 채택"이 아님; 렌즈 A 인과 교정) + 레시피 데코 주석 강화(복사 따라옴). **①보조(기존 산문 굵게)는 DR-22 무효라 폐기**(렌즈 A·C).
- **② reviewer (ii)**(`agents/discipline-reviewer.md`·codex `skills/dddjango-discipline-reviewer/SKILL.md`): **"transient 과잉매핑" 별도 마이크로 불릿** 신설(렌즈 C: 6166자 거대 불릿 인라인 회피) + (i) 완전성 문장에 포인터. "분기 0개=무조건 important·코더위임 면책 배제(렌즈 A)·(i)누수↔(ii)과잉 **배타적 진단**(렌즈 B-F7)·`DatabaseError` 병기 대신 분기 유무가 판정 핵심(B-F6)·⑭ 못 보는 의미 변종(헬퍼 무조건-True 위장·register-only) 보조".
- **③ 백스톱 ⑭ `check-transient-overmapping.py`**(신규): AST로 `OperationalError`/`DatabaseError` 핸들러(데코 또는 `exc:` 어노테이션)가 **분기 부재 ∧ retryable(503/409) 반환** 시 exit2. 게이트 **13종→14종** 배선(`commands/dddjango.md`·codex `skills/dddjango/SKILL.md`). plugin.json 1.5.0→**1.6.0**.

### 검증 (전부 통과)
- **정밀도 시제품**(렌즈 B 관문): known-bad E(Claude 무판정 503) **차단** / known-good 5종(Codex 분기·§6.2 분기·IntegrityError 500·StockContention 도메인 503·대안 B) **거짓양성 0**. DR-38 함정 3종 면제.
- **⑭ STANDARD 합성 매트릭스**: Claude `handle_operational_error:157`만 VIOLATION·exit2, clean exit0.
- **미러 정합**: scripts 14개 byte-identical · ninja final.md IDENTICAL · reviewer (ii) 양쪽 1회 · 게이트 14종 양쪽(13종/열셋 잔존 0) · plugin.json 1.6.0 양쪽.

### 정직 경계 / 다음
- **N=1·P4③**. salience 효과는 텍스트 판별 불가(DR-22)→**라이브로만**. ⑭이 라이브 배선 강제(DR-30식)라 coder 무판정 503은 게이트서 반송된다 — 렌즈 A가 짚은 "reviewer important는 게이트 미차단"을 ⑭이 메움.
- **known-limitation**: 헬퍼 무조건-True 위장·register-only+무어노테이션은 ⑭ 못 봄 → reviewer (ii) 보조.
- **다음(D3)**: maj1 **라이브 dual 재검증**(정석 clone·캐시 신선화·dual `/dddjango`·위반 주입으로 ⑭ 차단 DR-30식 확인) → 효과 보고 → **min1**(§5.1 외부식별자 정의 + `int`+하한有+상한無 비대칭 백스톱; known-good 재합성=Codex 제외). maj4 보류(PG N≥2 후).
