# T2-1 출력 계약 설계 v2 — 공용 포매터·순서 보존 방출 (선행 리뷰 U·V 반영판)

> 지위: v1의 선행 리뷰(L-U·L-V) 44건 중재(MEDIATION-2) 반영 전면 개정. 귀속 매핑표 v2와 한 묶음 — **반영 대조 레인 W 통과 후에만 코드 적용**.
> v1 대비 핵심 변경: ① 수집·방출 분리 폐기 → **순서 보존 방출**(V1) ② line 인자 표면 전면 제거 — **전 표면에서 라인 = 레코드 필드의 순수 함수**(V2·U15) ③ 계약·guard 레인도 포매터 소유 ④ «stdout 불변» 주장 폐기 → **의도 변경 열거표**로 통제(V3 — 규약 v1.1 문면 정합) ⑤ 검증 계획 전면 확장(중재 채택분 전건 착지).

## 1. findings.py v2 아키텍처

**원칙(T12 채택 정의)**: 구조화 입력 → 단일 포매터 → stdout 라인+record 동시·동순서 산출. 레코드만으로 stdout 위반 라인을 재구성할 수 있어야 한다.

- 각 표면의 `add(...)`는 **구조화 수집만** 한다(레코드 즉시 방출 폐지). 내부에 `(rule|sentinel|contract_ref, where, symbol, severity, msg[, question])` 엔트리를 쌓고, list 내용물로는 포매터가 만든 라인을 유지(기존 `if findings:`/`len()`/앵커 `collected` 소비자 호환).
- 저장 라인은 **무들여쓰기**·인쇄 시 호출자가 2-space(`print(" ", x)` 판형 — A형 byte 동일의 근거).
- **`emit_records(*collections)`** 모듈 함수 신설: 검사기가 보고 지점에서 **stdout 인쇄 순서와 같은 순서로 1회 호출** — 이때만 JSONL 방출. 앵커 모드에서도 같은 순서로 호출(현행 레코드 의미 유지·유령 없음). record 순서 = stdout 위반 라인 순서 골든.
- 라인 문법(레코드 필드의 순수 함수):
  - violation: `[{rule}] {where}: {msg}`
  - candidate: `[ⓓ{rule}] {where}: {msg} — 물음: {question}` (record message = `{msg} — 물음: {question}` — 재구성 가능)
  - 계약(rule=null+contract_ref): `- {where}: {msg}`
  - guard(대상-0 등 검사기 단위 진단): 라인 = `{msg}` 원문(msg가 곧 라인 — 21종 기존 문면 보존 가능·record 화)
- `SliceFindings` 제거·`ContractFindings.add`의 `line` 인자 제거(과도기: 이행 커밋 열 순서상 마지막 검사기 이행 후 같은 커밋에서 제거·`rg SliceFindings` 0 확인).
- 스키마 `findings/0` 무변(생산자 재설계일 뿐 — 필드 의미 불변).

## 2. 의도 변경 열거표 (stdout 문면이 바뀌는 전 레인 — 규약 v1.1 대체 불변식의 통제 장치)

| 레인 | 구 문면 | 신 문면 | 소비자 영향 |
|---|---|---|---|
| tree B형(≈26곳) | `  [#N] {rel}:{lineno} {msg}` | `  [#N] {rel}:{lineno}: {msg}` | registry 정규식 매치 유지·**debt substring 전수 대조 의무**(§5-9) |
| dataclass code-profile #N 승격 사이트(매핑표 v2) | `  - {path}:{lineno}  {category}: {shown}` | `  [#N] {path}:{lineno}: {category}: {shown}` | registry parsed 증가(기대표 사유 갱신)·backstop fragment 14종 정적 대조(§5-8) |
| openapi code/repo(#63) | `  - {rp}:{lineno}  [#63] {detail}` / repo 자유문 | `  [#63] {rp}:{lineno}: {category}: {detail}` — **msg에 category 포함으로 확정**(V8: stdout·record 동일 msg) | `#63` fragment 잔존 확인 |
| 계약 레인(자유 출력 5종·response-schema·common-container·code 계약 잔류분) | 검사기별 자유 문면 | `  - {where}: {msg}` (msg는 기존 사유 문면 승계) | registry 미파싱 유지(현행 동일)·fixture 골든 갱신 |
| EC blocker 혼성·composition DI 혼성(V9) | `  - {문면}` | 판정별 분기: BC경로=#114·V1=#497 → violation 문법 / 나머지 → 계약 문법 (구조화 discriminant — 문자열 prefix 분기 금지) | 상동 |
| guard 21종·헤더·근거 블록·clean 라인 | — | **무변**(guard는 라인 무변+record 신규) | 없음 |
| 타 소유자 이관(EC #117 사건·composition DI V2/V3) | 해당 라인 방출 | **방출 제거**(소유자 단독 — layer-skeleton·context-isolation) | 적용 커밋에서 소유자 실발화 픽스처 실증 후 제거(U11 의무) |

보존 표면의 정확한 한정(R#3 처분 착지): **{정상 red/green stdout(위 열거 외 무변), exit 의미론, 위반 incident multiset, 소비자 계약(registry 파싱·backstop 판정·debt 매칭·gate 판정 결과)}**. uncaught traceback byte는 계약 밖. `_entries()` OSError 안정 문면화는 백로그(별도 개선·T2-2 전 아님).

## 3. incident-key·이중 방출 (U13·U14·V4)

- 기본: dedupe **하지 않는다** — multiset(message·occurrence 보존)이 정본.
- 동일 사건 이중 탐지(정밀 code 레인 ↔ 광의 tree 술어)는 **overlap 표(매핑표 v2 소유)에 등재된 쌍에 한해 tree 쪽 방출을 선점 억제**(코드에서 code 레인 활성·해당 대상 적중 시 tree 사이트 skip — locator 차이 문제 원천 제거). openapi 앵커 레인 포함.
- 억제는 «같은 실행에서 같은 사건»에만 — 억제 쌍마다 픽스처로 (억제 전 2건 → 억제 후 1건) 실증.

## 4. 적용 순서 (V25 — 고정)

1. **하네스 확장 선행**(신규 레인·oracle이 구현을 기다리며 red여도 됨 — 단 verify 편입은 green 후):
   baseline `(exit, parsed_raw, normalized_unique, unparsed, synthetic)` 확장(gate `_normalize` import — S#4 처분 완성) · `(script,lane)` 키 공간 · git 3레인(영향 7종: response-schema·app-container·idempotency·transient·choices·synthetic·db-table) · 위험 레인 4종 픽스처(api #59 code·composition 단일 `composition_root.py`·openapi 직접 선언 누락·EC code) · cross_matrix violation/info 정규식 분리 · findings/0 **13필드 전건 oracle**+stdout↔record **ordered multiset 양방향 대조**(잉여·누락·중복·순서 각각 실패) · multiset fingerprint `(rule|sentinel|contract_ref, file, symbol, message, occurrence_index)`(동일 4-튜플 내 방출 순 서수·JSON ensure_ascii=False 직렬화·**구 sha 열과 병기 과도기**) · `--scripts-dir`/`--fixtures-dir` 주입점+mutation self-test(message-empty·record-drop·reorder·duplicate 4종 필수 red) · **전 메타 하네스 DJR_FINDINGS_JSON 제거**(fixture·cross·backstop — S#7 잔여)+verify 선두 env preflight.
2. findings.py v2(순서 보존 emitter) — findings_smoke 골든으로 DM/CC 무변 실증.
3. **검사기별 «매핑 v2+포매터» 원자 이행**(분리 커밋 — EXPECTED·픽스처 골든 갱신을 같은 커밋에서 검사기별 사유와 함께): 순서 = response-schema → EC → openapi → composition → api-error(리스크 오름차순) → 자유 출력 5종·common-container(계약 문법 이행) → guard 21종.
4. regen severity 봉인(`choices=("violation",)` — info는 review-only 별도 함수).
5. `SliceFindings`·`ContractFindings(line=)` 제거(`rg` 0 실증·codex 미러 0 diff).
6. debt 자산 전수 수집·구/신 매치 대조 리포트(V21 — B형 콜론 경계).
7. D11: byte 골든 **총 8종**(domain-model·common-container·api-error·EC·composition·openapi·response-schema·context-isolation — 구판 기준=각 검사기 이행 직전 커밋 봉인) + **construct drift 리포트** `workspace/eval/ab/T2-construct-drift.md`(동일 픽스처·구판/신판 stdout·exit·record multiset 차이 전건 표).
8. 혼성 패널 재검(codex+신선 Claude) → T2-1 완료 재선언.

## 5. 검증 계획 (적용 각 단계의 green 조건)

1. 단계 1 종료: 신규 oracle이 **의도 red**(미이행 검출)임을 확인 후 스위치 방식으로 보류 편입 — 기존 green 세트는 전 단계 유지.
2. 단계 3 각 커밋: 해당 검사기의 {baseline 확장 행·count(레인별)·픽스처 골든·backstop(679)·make verify 전체} green + EXPECTED 변경 사유 커밋 메시지 전건.
3. 최종: mutation self-test 4종 red 실증 · stdout↔record ordered 대조 27종 green · drift 리포트 생성·검토 · verify 전체 green.
4. «synthetic 군 축소» 같은 예단 없음 — 레인별 실측값만 기록(V22).

## 6. 백로그 등재 (이번 범위 밖 — 소유 단계 명시)

- lazy-open record writer + 8,000건 성능·FD 회귀 기준: **T2-5 진입 조건**(MEDIATION R#4 처분).
- `_entries()` OSError 안정 진단 문면: 별도 개선(T2-2 전 불요).
- registry_gate의 findings/0 주 채널 소비 전환: T2-3 재론(MEDIATION S#4 잔여).
- 배포 코드 주석 규율: 로컬 절대 경로 금지·#N+정본명+요약만(V26) — 단계 3 이행 시 준수.
