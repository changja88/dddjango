# T2-1 선행 설계 리뷰(U·V) 중재 기록 (2026-08-20)

> 대상: **L-U**(귀속 반증 — 발견 18+반증 실패 5) · **L-V**(열린 스코프 — 발견 26+반증 실패 4) = 발견 44건.
> 결과: **채택 40 · 부분 채택 4 · 기각 0** → 설계 문서 2건을 v2로 재작성 후 반영 대조 레인(W) 경유, 통과 시 코드 적용.
> blocker 기각 0 — 규약의 «기각 시 재현 실증» 조항 발동 없음.

## 귀속 판정 변경 (L-U — v2 매핑표에 반영)

| 출처 | 판정 | v2 반영 |
|---|---|---|
| U1·V5 | 채택 | `caught exception forwarding forbidden` 전건 #474는 과포섭(#474 주어=도메인 예외·검사기는 응용 예외도 승인) → **catch 출처로 사건 분할: 도메인=#474·응용=계약**. category 분리 저작 필요 |
| U2 | 채택 | `raise inside managed try`·`raise inside managed catch` → **#125 귀속**(controller 입구 허용 동작 밖 — code 레인의 확정 술어. tree ⓓ와의 이중 방출은 incident-key로 처리) |
| U3 | 채택 | `mapping body` 합성 category → 실패 원인 분해: **helper/factory/serializer 위임=#126**·본문 형태 오류=계약 |
| U4 | 채택 | `outside canonical registrar owner` → lexical 밖=#109·함수 안 wrong receiver/rebind=계약(별도 category 분리) |
| U5 | 채택 | `decorator side effect` → 파일·parent별 분할: api_router 모듈층=#109·project API=#437·URLconf=#440·함수 내부=계약 |
| U6·V6 | 채택 | `exactly once` → **count==0만 #440**·count≥2=계약(category 분리) |
| U7 | 채택 | EC 행42 default 술어는 규칙 문면 초과 → **계약 유지로 정정**(#572 승격 취소) |
| U8 | 채택 | base additional field 는 #572 행36과 동일 사건 → **주체 분리(common/base/concrete)·base는 #572 단독**(계약 중복 제거) |
| U9 | 채택 | EC 행23·24 주체 분할: second direct-common=#572 기존 finding만·second ErrorCode/functional Enum=**#117 소유자(context-isolation) 존중 — EC 방출 억제**·기타만 계약 |
| U10 | 채택 | 불확실 행30~33 확정: 행30 **0개=#572·복수=#117(EC 방출 제거)**·행31=#117 사건(EC 계약 방출 제거)·행32=**#636**·행33=**#572** |
| U11 | 채택(검증 의무 부가) | DI V2=#81·V3=#488(소유=layer-skeleton) — composition 중복 검사 제거로 **단독 소유 회복**. 단 적용 커밋에서 «해당 사건을 layer-skeleton 이 실제 발화»함을 픽스처로 실증 후 제거(발화 안 하면 소유자 쪽 보강이 선행) |
| U12 | 채택 | 불확실 15행 최종 장부 전건 수용(API18=계약·API19/20=#126/계약 분할·EC23/24 주체분할·EC30~33 상기·EC34/39/41=계약·B1=BC→#114/common→계약·V2/V3=소유자 이관) |
| U19~23 | — | 반증 실패 확인(21행·52행·부속 3건) — v2에서 «리뷰 확정» 표기 |

## 설계 결함 (L-U 13~18 · L-V — v2 설계에 반영)

| 출처 | 판정 | v2 반영 |
|---|---|---|
| V1 | **채택(최중량)** | 수집·방출 분리가 «동시 산출» 위반(레코드=수집 순·stdout=재배열 순) → **findings.py 재설계: add()는 구조화 수집만, 공용 `emit_all()`이 라인 인쇄+레코드 방출을 한 순서로 수행**. record 순서=stdout 위반 라인 순서 골든 |
| U13·U14·V4 | 채택 | `(rule,where)` dedupe 불성립(레인별 locator 상이·openapi 앵커 레인 동축) → **incident-key 설계: 정밀 레인(code-profile) 활성 대상에서 겹침 tree 술어 방출을 선점 억제**(overlap 표 명시)·dedupe 기본은 message·occurrence 보존 multiset |
| U15·V2 | 채택 | ContractFindings/guard의 line 인자 표면 제거 — **전 표면에서 라인은 레코드 필드의 순수 함수**: violation `[{rule}] {where}: {msg}`·candidate `[ⓓ{rule}] {where}: {msg} — 물음: {q}`·계약 `  - {where}: {msg}`·guard=msg 원문. 계약 레인 문면 변경은 «의도 변경 열거표»에 등재 |
| U16·V7 | 채택 | ⓓ#511 튜플 확정을 v2 매핑표 부속에 저작(question 의 «물음:» 접두 제거·msg 신규·골든 병기) |
| U17·V10 | 채택 | Finding dataclass 에 `symbol` 추가 — FunctionDef/ClassDef/AnnAssign/operation name 등 확정 재료는 채움·불명만 null |
| U18 | 채택 | 통계를 category 행수가 아닌 **분할 후 원자 술어 수**로 재산출·부록 B 재작성 |
| V3 | **채택 — 규약 v1.1 문면 정합**(잠정·마일스톤 추인 목록 등재) | 규약의 기계 정의 «stdout byte 등가»는 T2-1 byte 전략 시점의 과협소 조작화 — 사용자가 승인한 t2-plan v1.1 원문이 이미 «[#N] 접두 신설(stdout 변경)이 목적»이므로 목표 자체가 아니다. **대체 불변식으로 정정: exit 의미론·위반 incident multiset·소비자 계약(registry 파싱·backstop·debt)·검사 판정 결과 불변 + stdout 문면 변경은 «의도 변경 열거표»(레인·구/신 diff)로 통제**. 방향(성능·동작 저하 0)은 불변 |
| V8 | 채택 | OA msg 구성 재확정 — stdout 무변 주장 폐기: 신 stdout 을 한 곳에서 확정(category 포함 여부 결정)·기록 |
| V9 | 채택 | EC blocker 혼성·DI 혼성의 이행 행 추가(구조화 discriminant·순서 보존·픽스처) |
| V21 | 채택 | debt 자산 전수 수집·구/신 매치 대조를 적용 단계에 편입(B형 콜론 경계) |
| V22 | 채택 | «synthetic 축소 예상» 삭제 |
| V25 | 채택 | **적용 순서 고정**: ①하네스 확장(다레인 키·oracle — 신규 레인은 red 로 먼저) ②공용 ordered emitter ③검사기별 «매핑+포매터» 원자 이행(EXPECTED 사유 갱신 동반) ④`rg SliceFindings` 0 확인 후 표면 제거 ⑤multiset 구/신 열 병기 과도기 |
| V26 | 채택 | 배포 코드 주석에 로컬 절대 경로 금지 — #N·정본명·요약만 |

## 중재 채택분 미착지 (L-V 11~20·23·24 — v2 검증 계획·백로그에 전건 등재)

regen severity 봉인(choices=violation) · baseline `(exit,parsed_raw,normalized_unique,unparsed,synthetic)` 확장(gate `_normalize` 단일 출처) · git 3레인 EXPECTED 분리 · cross_matrix violation/info 정규식 분리 · findings/0 13필드 전건 oracle+ordered multiset 양방향 대조 · `(script,lane)` 키 공간+위험 레인 4종(#59 code·composition 단일 파일·openapi 직접 선언 누락·EC code) · multiset fingerprint 튜플/직렬화 확정 · D11 **총 8종 열거**(구판 커밋 봉인·drift 리포트 경로·생성 명령) · `--scripts-dir`/`--fixtures-dir`+mutation self-test · verify 전 하네스 env 격리 preflight · traceback 제외 범위 명시+`_entries()` OSError 백로그 · lazy-open writer 를 T2-5 진입 조건 등재.

## 부분 채택 4건

- U3(«현 category 로는 판정 불능») — 분해 채택하되 분해 결과 판정 불능 잔여가 남으면 계약 보수(전면 재분석은 비용 대비 기각).
- V3 — 상기(규약 개정은 잠정·추인 대기 — 사용자 승인 문면(t2-plan v1.1)이 근거라 문면 정합형으로 처리하되 마일스톤 보고의 추인 목록 최상단 등재).
- V18(D11 «총 8종 확정») — 8종 채택: domain-model·common-container(기존 2) + api-error·error-centralization·composition-root·openapi(#N 승격 4) + response-schema-bypass(계약) + context-isolation(다규칙 대형) = 8. 구판 기준 = 각 검사기 «이행 직전» 커밋으로 봉인.
- V24(lazy-open) — T2-5 진입 조건 등재 채택·회귀 기준 수치는 T2-5 설계 시 확정(지금 확정은 과잉).

## 다음 절차

① 매핑표 v2 재작성(에이전트 — U12 장부·분할 category·통계 재산출·#511 튜플·symbol 명세) ② 포매터 계약 v2 재작성(직접 — ordered emitter·표면 재설계·의도 변경 열거표·검증 계획 전면) ③ 규약 v1.1 문면 정정(잠정) ④ **반영 대조 레인 W**(경량 codex — v2 문서 2건이 본 중재 전건을 착지시켰는지) ⑤ 통과 시 코드 적용(V25 순서).
