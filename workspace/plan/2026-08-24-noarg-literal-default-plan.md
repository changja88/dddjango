# L1′ 병존형 canon 추가 — 수정 계획 (v2 확정)

작성 2026-08-24 · 상태: **v2 — 3인 적대 패널(P1 온톨로지·리비전 / P2 검사기·픽스처 /
P3 계약·정합) 반증 반영 확정본**. 처분 대장 §7.
결정: 사용자 확정 **L1′** — 병존형(단일값 Literal 좁힘+동일 default)을 canon에 추가.
무인자 계약 불변. 원인 정본 = `2026-08-24-noarg-concrete-errorschema-analysis.md`.

## §0 설계 원칙

- **무인자 계약 불변**: R-0043·R-0684·동반 무인자 문면 전부 한 글자도 불변.
- **피예외 규범의 정확한 특정**: 병존형의 현행 red 2계열은 무인자(R-0043)가 아니라
  **annotation 보존 계열 — b14 문장 5(R-0044 drift 금지)와 SKILL b6(R-2921 보존
  Obligation)** 소유다(P1·P3 수렴). 신규 Exception은 R-0044 직후에 붙고(R-0041 대칭),
  R-2921은 문면 단서 리비전으로 정합화한다.
- **보수적 경계(검사기 집행형으로 정밀화 — P2)**: 병존형은 ① 공통 field가 **Field
  metadata 없음**(`contract.metadata == ()`) ② 공통 annotation이 **벗겨진(bare)
  스칼라 자리**(식별자 field는 base가 좁힌 bare Enum 자리 — nullable/wrapper 공통
  불가) ③ concrete annotation **최상위가 Literal[단일값]**(Annotated 래핑 불허)
  ④ default는 **plain `=` 표기**(`Field(default=…)` 불포함) ⑤ 좁힘값 == default 값
  — 전부 충족일 때만 canon. 미충족은 기존 red 그대로.
- **검사기 메시지·red 라우팅 불변**: 통과 조건만 확장 — 값 불일치·경계 미충족은
  기존 annotation category red 경유(신규 category 없음·기존 판정의 조건 변경 없음).
- 이번이 **운용 단계 최초의 신규 채번**이다 — 리비전 판례(f4124ab·538138d)에 없는
  신규 채번 고유 단계 3종(wiring·q4 골든·계수 3키)이 §2에 명시돼 있다(P1).

## §1 문면 리비전 (rules 정본)

### 1-1. 신규 Exception Work — **R-3401** (ISSUED 다음 번호 고정)

- `implementation-django-ninja-final.ttl` §6.2 b14에 채번: `djr:Exception` · 라벨
  «concrete field의 단일값 Literal 좁힘·동일 default 병존 canon 예외(2026-08-24)» ·
  Expression `@2026-08-24` revision 1 · ISSUED append(경로 필드·같은 커밋 등장).
- b14 text에 **1문장** 삽입 — 위치는 **문장 5(R-0044) 직후**(R-0041 대칭 — 피예외
  직후). 문장→Work 대응이 «등장 순=채번 순» 관례를 벗어남(R-3401이 중간)은 본 계획
  §7 검수표 기록으로 갈음(P1 — 기계 제약 아님 확인됨). 초안(스타일: «단 » 시작·볼드
  없음·slot 6 귀속·1문장 — P3 F9):

  > 단 공통 annotation이 Field metadata 없는 벗겨진 스칼라 자리(식별자 field는
  > base가 좁힌 Enum 자리)인 concrete field는 slot 6에서 승인된 그 concrete의
  > 고정값 하나의 `Literal`로 자리를 더 좁히고 같은 값을 default로 병기해도
  > canon이다(plain `=` 표기 한정·좁힘값=default 동일·wrapper/nullability 좁힘
  > 불포함·무인자 생성 계약은 그대로 만족 — 식별자형은 §3.1 이벤트 discriminator와
  > 같은 표기·비식별자는 스칼라 상수로 확장 · 2026-08-24).

- statesNorm 7→8(R-3401 추가). b13 코드 예시·기존 7문장·기존 Work Expression 불변
  (P1 검증 — Expression은 text 미보유라 리비전 불요).

### 1-2. SKILL b6 정합화 — R-2921 리비전 2 (P1·P3 blocker 처분)

- `implementation-django-ninja-skill.ttl` b6 text의 «BC/concrete는 공통
  annotation/nullability·Field metadata를 보존하고» 에 최소 단서:
  «…를 보존하고(§6.2가 승인한 단일값 Literal·동일 default 병존 좁힘은 예외)…».
- R-2921 Expression 리비전 2(`djr:revision-clarification`·`prov:wasRevisionOf` 연쇄).
- 반경: skill ttl → SKILL.md 재투영(`--apply implementation-django-ninja-skill`) →
  **codex SKILL.md 의미 미러 수동 갱신**(판례 2호 선례) → LEDGER(해당 절 재기준선).

### 1-3. wiring — 신규 채번 고유 단계 (P1 blocker)

- `ontology/wiring/implementation-django-ninja-final.ttl`에
  `djr:R-3401 djr:enforcedBy <…#c/check-error-centralization.py>` 간선 저작
  (NormShape sh:or fail-closed — Exception도 동일 제약).

### 1-4. 사슬 실행 순서 (신규 채번판)

① rules ttl(R-3401·b14)+skill ttl(R-2921 rev2)+ISSUED+**wiring** → ②
`ontology_gate.py --write` → ③ `ontology_render.py --apply` ×2(final·skill) → ④
`corpus_mirror_sync.py --write`(final 계열 자동 — 소스·codex 동시. §구판 ⑧ 삭제) +
codex SKILL 수동 → ⑤ `make rulepack` → ⑥ `target-counts.json` **NormShape·WorkShape·
ExpressionShape 각 +1**(3410·3410·3407 — P1 정정) → ⑥′ **q4 질의 골든 재emit**
(`query_golden_check.py --emit` — 3400→3401·사유 커밋 메시지) → ⑦ LEDGER 재기준선
(final·SKILL) → ⑨ `manifest_seal.py --write` → ⑩ `make verify`(겹마다 red가 안내 —
판례 판형).

## §2 검사기 수술 (#2 `check-error-centralization.py` + codex byte 미러)

`_literal_narrowing_allowed(field, contract, bindings, …)` 헬퍼 신설, 비교 지점
2곳에서 국소 우회(P2 실측 — 서명 함수·치환과 충돌 없음·유일 성립형):

- **(a) discriminator** (:3533-3543): 우회 조건 = `contract.discriminator_annotation
  == ('symbol','<bc-error-code>')`(**bare 전제 — P2 F1**) ∧ concrete 최상위
  `Literal[<own enum>.<member>]` 단일 ∧ plain `=` default가 **같은 member**
  (동일성 검사는 헬퍼 내부 — 불충족 시 우회 불허로 기존 annotation category red 경유·
  기존 default 판정(:3605-3623)과 proof 위임 의미 불변 — P2 F4·P3 F7).
- **(b) 비식별자 field** (:3545-3551): 우회 조건 = `contract.metadata == ()` ∧
  `contract.annotation` ∈ bare 스칼라 서명 집합(('symbol','str') 등 — **Annotated
  판별은 서명이 아니라 metadata 빈 집합으로 집행**, P2 F2) ∧ concrete 최상위
  `Literal[상수]` 단일(서명이 타입명 보존 — bool/int 구분 가능) ∧ 상수 타입 == 공통
  스칼라 타입 ∧ plain `=` default == 그 상수.
- Literal 심볼 판별만 신규(기존 검사기에 Literal 취급 전무) · own-member 판별은
  `_enum_member_name` 재사용(P2 확인).
- `Field(default=…)` 병기형은 우회 밖 — metadata 판정이 현행대로 red(F5 — 문면
  «plain `=` 한정»과 일치).
- 무인자·metadata·base·missing-default 판정 전부 불변. **codex byte 미러 동시 갱신**.

## §3 픽스처·계수 회귀 (P2 F3 — 러너 비자동 인식 반영)

- **good**: 병존형 field(식별자+비식별자)를 가진 신규 concrete 추가 — exit 0 유지
  (green 실증·P2 실측으로 구조 장애 없음 확인). `findings_count_matrix`의 good
  green 축(exit 0·레코드 0)이 집행 — «fixture_matrix 레인»이 아님(구판 오기 정정).
- **bad_rules 확장**: ① tarot형(무 default Literal) ② `Literal[X] = Y` 값 불일치 —
  기존 red 구성에 추가 발화(P2 실측 성립). `checker_baseline_matrix` EXPECTED
  `(2,1,1,4)`와 `findings_count_matrix` 지문 3열을 실측값으로 갱신(사유 병기).
- **신규 레인**(③ 경계): nullable 공통(`str | None` discriminator) 자리의 Literal
  좁힘 red 유지 — 공유 common 개조가 필요하므로 **별도 케이스 디렉터리 + RISK_LANES
  선언 + baseline·findings_count EXPECTED 키 신설 의무**(선언 없으면 무집행 회귀 —
  P2 F3). Annotated-metadata 공통 자리의 병존형 red 케이스도 이 레인에 동거.
- guard-zero 레인 무영향(argv 불변).

## §4 검증 게이트 (구현 완료 조건)

1. 재현 3종: 병존형 → #2 exit 0(red 2건 소멸) · tarot형 → red 유지 · 값 불일치 →
   red(기존 category).
2. 병존형 schema+무인자 controller → #15 exit 0(P2 기실측 — 회귀 확인).
3. baseline·findings_count·fixture_matrix·construct green(기대표 갱신 반영).
4. 리비전 사슬 §1-4 완주 → `make verify` green.
5. codex 검사기 byte 동일·rulepack 재소성·조감도·메모리 갱신.

## §5 kkebi 회신 문면 (구현·릴리즈 후)

- 순서: **릴리즈 → `/plugin` 갱신 → 코드 수정 → 게이트**. tarot 수정 = 병존형
  (`code: Literal[TarotErrorCode.X] = TarotErrorCode.X` · `message:
  Literal["…"] = "…"` — plain `=` 표기·`Field(default=…)` 아님) + controller 무인자
  생성 유지.
- **관찰 기준(P3 F6)**: 게이트 확인은 exit가 아니라 **차분 절 카운트**(해당 파일
  «신규분 0·앵커 기존분 0»)로 읽는다 — anchor 강등 환경에서는 구 설치본 red도
  신 canon green도 exit 0으로 동일하게 보인다. «구 설치본이면 red» 경고는 무앵커
  수동 실행(`python3 …check-error-centralization.py <root> <selector…>`) 기준.
- 침묵 원인 판별(H-f)은 사용자 증거 회신 대기 별건.

## §6 명시적 비변경 목록

- R-0043·R-0684·R-0041·R-0040·R-0044~46 문면과 Expression — 불변(예외는 신규
  R-3401이 소유·R-0044 자체는 무단서 금지로 존치 — 직후 예외 문장이 한정).
- #15 검사기 전체·#2의 무인자/metadata/base/missing-default 판정 — 불변.
- §2.2 b11·b15·b16, §6.2 b17·b29 — 불변(P3 «준비된» 포섭 검증 완료).
- agent 4종·command 문서 키 — 불변(P1·P3 이중 스위프: annotation 형태 진술 전무).
- 앵커 차분 강등(H-f) 규율 개정 — 범위 밖(증거 확정 전 결정 게이트 초과 — P3 유지 8).

## §7 처분 대장 (패널 발견 21건 — 채택 21 · 기각 0) + 문장-Work 검수표

| # | 렌즈 | 수위 | 발견 | 처분 |
|---|---|---|---|---|
| 1 | P1 | blocker | wiring enforcedBy 단계 부재(신규 채번 고유) | §1-3 신설 |
| 2 | P1·P3 | blocker | 피예외 규범 오귀속(R-0043→실제 R-0044·R-2921)·SKILL b6 모순 | §0 재특정·§1-1 위치·§1-2 R-2921 rev2 편입 |
| 3 | P1 | major | q4 골든 3400→3401 재emit 누락 | §1-4 ⑥′ |
| 4 | P1 | major | 계수 3키 동시 +1(«Exception» 키 없음) | §1-4 ⑥ 정정 |
| 5 | P1·P3 | major | 신규 문장 위치 미정·2문장 vs 1문장 불일치·«위 문장» 지시 실패 | §1-1 — R-0044 직후·1문장 재작성 |
| 6 | P2 | major | (a) bare 전제 부재 — nullable 공통에서 §0 모순 | §2(a) bare 조건 명기 |
| 7 | P2 | major | (b)① Annotated 판별 불가(서명이 extras 제거 — 죽은 조건) | §2(b) — metadata 빈 집합 + bare 서명 집합으로 재기술 |
| 8 | P2 | major | 픽스처 러너 비자동 인식 — 별도 케이스는 레인 선언 의무·fixture_matrix 오기 | §3 재구성 |
| 9 | P3 | major | Field metadata 결합형 미해결 | §0 경계 ①·④ + §2 — plain `=` 한정으로 배제(Field(default=) red 유지) |
| 10 | P3 | major | «스칼라 자리» 문면이 경계보다 넓게 읽힘(Optional 내부 좁힘) | §1-1 «벗겨진» 명시·식별자/비식별자 분리 |
| 11 | P3 | major | kkebi 안내 관찰 기준(anchor 환경 exit 무의미) | §5 차분 절 카운트 기준 |
| 12 | P2 | minor | 값 불일치의 category 재사용 시 거짓 메시지 | §2(a) — 헬퍼 내부 동일성·기존 annotation category 경유 |
| 13 | P2 | minor | Field(default=) 병존 변형이 문면상 canon으로 오독 | §1-1 «plain `=` 한정» 괄호 |
| 14 | P3 | minor | «§3.1 동형» 과대(enum member형 한정) | §1-1 식별자형 한정 서술 |
| 15 | P3 | minor | 스타일(«단, »·볼드·slot 6 귀속 탈락) | §1-1 반영 |
| 16 | P1 | minor | «R-0041 대칭» 호칭 — 운용 단계 최초 신규 채번 | §0 말미 명기 |
| 17 | P1 | minor | ⑧=④ 중복 | §1-4 통합 |
| 18 | P1 | major | R-2921 개정 반경(SKILL 재투영·codex 수동) | §1-2 |
| 19 | P2 | 유지 | 수술 사이트 전수성·헬퍼 성립·#15 무수정·pydantic 런타임(wire byte 동일)·EXPECTED 귀속 — 실측 9종 | §2·§3 근거 확정 |
| 20 | P1·P3 | 유지 | 동반 agent/command 불변·b11 «준비된» 포섭·b13 불변·기존 Expression 불변 | §6 확정 |
| 21 | P3 | 유지 | H-f 규율 개정 범위 밖(결정 게이트)·값 불일치 red는 L1′ 정의 내부 | §6 확정 |

검수표(b14 문장→Work · 개정 후): 1→R-0040 · 2→R-0041 · 3→R-0042 · 4→R-0043 ·
5→R-0044 · **6→R-3401(신규 — 채번 순서 예외는 피예외 직후 배치 우선의 의도적 결정)**
· 7→R-0045 · 8→R-0046.

**구현 후 정오(Phase 4 대조 리뷰 2026-08-24)**: §1-4 ⑥ «ExpressionShape +1(3407)»은
산술 오류 — §1-2의 R-2921 리비전 2도 Expression 노드 +1이라 **+2(3408)가 옳다**
(실물·계수 회귀 green이 확증). 상태: **v2 구현 완료 — 대조 리뷰 편차 0·make verify
전 그룹 green·plugin validate 통과**.
