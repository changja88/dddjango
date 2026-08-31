# 개정 계획 — 신규 API 표면의 스택·컨트롤러 형태 자동 답습 봉합 (v2 — 적대적 리뷰 반영)

- 날짜: 2026-09-01 · 작성: Coordinator(Claude) · 상태: **확정·구현 완료(2026-09-01)** — D1=(a) 보강판 채택·D2=R-0698 amendment 포함·D3=즉시 릴리즈(사용자 확정)
- v1 → v2: 적대적 리뷰 3방면(코퍼스 모순·과적합·집행성) 발견 통합. blocker 6건 반영으로
  개정 대상 3건 → **6건 + codex 의미 미러 + 부수 산출물**로 확장. 옵션 (b)는 3개 리뷰
  모두에서 기각·열세 판정(재량 판정 회귀 통로 2곳·HTML 오포섭 최악 경로·검사기 비호환)
  — **폐기**하고 (a) 보강판만 유지.
- 발주 배경: spring_dream_server 실증 사례. 신규 REST 표면(fortune_character
  character_catalog)이 R-1645의 자동 답습 조항을 근거로 plain Django 함수형으로 G1
  승인됨. 사용자 판정: "REST/JSON 표면의 함수형 채택은 설계자 재량으로 승인되면 안 된다.
  비-REST 메커니즘만 예외 후보." 범위는 플러그인(규범)만.

## 1. 진단 (v2 확정)

1. **R-1645**(design-architect «API 스택»): 확립 스택 존재 시 신규 표면 스택을 architect가
   자동 답습 — 사건의 1차 근거.
2. **R-1980/R-1981**(architecture-api §5.4): preserve-established «범위» 경계 미정의 —
   신규 endpoint의 확립 namespace 합류를 보존 범위 편입으로 읽는 통로 — 2차 근거.
3. **R-0696~0699**(ninja §2.3): 앞단 스택 결정이 plain으로 빠지면 §2.3이 미적용 — 닫는
   문장 부재.
4. **[리뷰 발견] command-dddjango.md:74**: Coordinator 문서가 구 R-1645 규칙("확립 스택
   있으면 architect가 정한다")을 재진술 — 미개정 시 이중 진실.
5. **[리뷰 발견] 집행선 공백**: G1 참여 리뷰어 중 스택/형태 감시자 없음(api lens는 R-2704
   형태 중립, discipline-reviewer Phase 1 lightweight 점검 목록에 해당 항목 없음).
   discipline-reviewer는 ninja 스킬을 로드하지 않아 R-3403 단독으로는 감사 캐리어 부재.
   coder.md:60은 "승인된 명세의 stack 결정을 그대로 집행" — 반송 사유에 스택 미승인 없음.
6. **[리뷰 발견] codex 의미 미러 실존**: `codex-dddjango/skills/dddjango-design-architect/
   SKILL.md`가 구 문장을 그대로 보유(corpus_mirror_sync 스코프 밖·검사 사각). 레시피
   메모리의 "agents는 codex md 없음"은 낡은 정보 — 메모리도 정정.

## 2. 개정안 6건 (v2 문안)

### 개정 1 — R-1645 redefinition (`ontology/rules/agent-design-architect.ttl` s005 o17)

교체 대상(현행): "프로젝트에 확립된 DRF·plain Django contract가 있으면 보존하고(«계약
profile» 축 — preserve-established; 파일트리 축이 아니다 — …), 없으면 Django Ninja를
적용한다."

**신 문안**:

> 신규 표면(이번 delivery가 새로 노출하는 route/operation — endpoint 단위; 기존 배포
> endpoint의 수정은 이 결정의 대상이 아니다 — §R-0697·R-0698 축)의 stack은, 확립
> 스택(이 작업이 관찰하는 저장소 상태에서 배포·소비 evidence로 확인되는 스택)이 없으면
> Django Ninja가 무언 기본이고, 확립 DRF·plain Django 스택이 존재하면 **스택 결정
> 자체를 `STOP_FOR_USER_APPROVAL`로 표면화**한다(선택지마다 대가 한 줄 — 표준 Ninja
> 채택: 확립 리소스와의 2-스택 분열 | 확립 스택 답습: 옛 스택 답습은 규약이 아니라 빚).
> 관찰은 스택 «정체» 식별과 STOP 선택지의 재료이지 답습 «채택»의 확정 근거가 아니며,
> Ninja 기본에서 벗어나는 신규 표면 스택 결정은 사유를 불문하고(답습·인프라/의존성 실물
> 부재·비-JSON 반환 메커니즘 포함) 이 STOP 경로로만 확정한다. G0 스코프 메모·발주서에
> 기록된 사용자의 명시적 스택 지시는 이 STOP 승인과 동격이다 — 명세는 그 기록(경로·
> 인용)을 스택 결정 근거로 인용하고, 인용 가능한 명시 기록이 없으면 STOP이다(승인
> 효력은 그 발주의 명세에 한한다). 이 결정의 대상은 새 HTTP/JSON API surface뿐이다 —
> server-render HTML 표면(아래 HTML 문장·`implementation-django-web` §11 관할)·admin·
> 정적 자원은 대상이 아니다. 오류 **wire 계약** 보존(«계약 profile» 축)은 별개 축이다 —
> 확립(배포된) 표면의 wire 보존은 그대로되, 신규 endpoint의 error profile은 12-slot
> `error profile` 기준으로 별도 결정하고(같은 공개 namespace 합류는 스택·컨트롤러 형태
> 답습의 근거가 아니다), 신규 Ninja 표면에 preserve wire를 지우는 조합은 게이트
> 미열거라 그 취급 결정을 G1에서 표면화한다. SSE·스트리밍·파일 반환 표면의 기본 대안은
> 클래스 컨트롤러의 framework-native 반환(`implementation-django-ninja` §2.2 carveout)
> 이며, plain 채택 선택지가 성립하려면 carveout으로 표현 불가하다는 관찰 근거를 그
> STOP 대가 줄에 기록한다.

- 리비전: Expression `R-1645@2026-09-01`(rev 2, redefinition) + **currentExpression 교체**
  + prefLabel 교체("신규 HTTP/JSON API 표면 스택 — 확립 스택 존재 시 STOP 표면화·명시
  기록 동격·부재 시 Ninja 기본").
- wiring 처분: `delegatedTo design-review-api` 해제(R-2704 형태 중립과 긴장) →
  `agent-discipline-reviewer`로 교체, `command-dddjango` 유지. 근거를 검수표에 기록.
- 리뷰 반영: 과적합 S1(승인 발주 한정+명시 기록 인용)·S2(잔여 포괄형+«확립» 정의)·
  S3(주어 한정+HTML 배제)·S4(carveout 관찰 근거)·S5(«신규» 정의), 모순 B-1(정체/채택
  분리)·B-3·B-4(명시 지시 동격)·B-5(전건 STOP 주어화)·C-2(§2.2 스킬명 병기)·A-4(wire
  재문언).

### 개정 2 — R-3403 신설 + (D2 시) R-0698 amendment (`implementation-django-ninja-final.ttl` s010-2.3/b1)

b1 말미 추가(신설 R-3403, statesNorm 추가 — 문장 등장 순 마지막):

> 신규 표면(새로 노출하는 endpoint)을 함수형 Router·plain Django view로 만드는 결정은
> **승인 evidence 참조**(STOP 승인 기록 파일 경로 또는 발주서·사용자 명시 지시 인용)를
> 스택 결정과 함께 적은 명세만 근거다(G1/STOP은 파이프라인 게이트 용어 — 파이프라인
> 밖에서는 사용자의 명시적 지시 기록이 이에 준한다). 오류 wire 프로필
> (`preserve-established`)·확립 namespace 합류·오류 응답·스트리밍 반환은 형태 근거가
> 아니며(스트리밍은 §2.2 framework-native carveout으로 클래스 컨트롤러 메서드가
> 반환한다), 그 참조 없는 함수형 결정은 집행하지 않고 명세 반송으로 올린다.

- (D2 채택 시) 같은 블록의 R-0698 문장 amendment:
  "**touched(신규·수정) presentation 표면은 클래스 컨트롤러로 만든다(승인 evidence
  참조를 가진 함수형 표면의 보존·수정은 그 기록이 관할한다).**"
  → Expression `R-0698@2026-09-01`(rev 2, amendment) + currentExpression 교체.
- 신설: `R-3403 a djr:Obligation`, prefLabel "신규 표면 함수형 채택의 승인 evidence 참조
  요구", ISSUED append. wiring: `delegatedTo agent-discipline-reviewer`.
- s009-2.2/b2·s024-6.3/b5(재진술 이웃 둘)는 불변 — 요약 블록, 신 문안과 모순 없음(리뷰
  확인·집행성 B-6 등재).
- 리뷰 반영: 과적합 S6(evidence-참조 형식+파이프라인 밖 gloss), 집행성 A-3·A-5(기계
  판정 가능 술어), 모순 C-3(D2로 처분).

### 개정 3 — §5.4 관할 경계 clarification (`architecture-api-final.ttl` s024-5.4 o6)

관할 배제 문단에 추가(anchor 규범은 구현 시 문장-규범 대응 재확인 — R-1980 잠정, R-1981
가능성 검토 후 확정):

> 이때 preserve-established **범위**의 보존 대상은 이미 배포된 표면·계약이다 — 신규
> endpoint가 확립 namespace에 합류하는 사실은 wire 보존(①)의 근거일 뿐 신규 endpoint의
> 구현 스택·컨트롤러 형태의 근거가 아니고(형태·스택은 G1 스택 결정과 구현 스킬 소유),
> 신규 표면이 preserve wire를 지는 조합의 게이트 취급 역시 위 미열거-STOP 조항을 따른다.

- 리비전: rev 2(clarification) + currentExpression 교체 + prefLabel 유지(명시).
- 리뷰 반영: 모순 A-4(개정 1과의 wire 귀속 정합·R-1983 경유 명시)·C-1(anchor 재확인),
  모순 B-2(설계자 12-slot 쪽은 개정 1 문안의 wire 문장이 동취지 봉합 — 별도 slot 개정
  불요 판단, 구현 시 재검).

### 개정 4 — Coordinator 스택 재진술 동반 개정 (`command-dddjango.ttl`)

`commands/dddjango.md:74` "스택 판정은 design-architect 소유다 — 기존 프로젝트에 확립된
API 스택이 있으면 그 정체를, 없으면 기본 Django Ninja를 architect가 §API스택 결정 순서로
정한다" 문장을 개정 1과 정합하게 리비전(정체 «식별»과 답습 «채택» 분리, 확립 존재 시
STOP 표면화·명시 기록 동격 명시). 해당 문장의 소유 규범 번호는 구현 시 ttl에서 확정.
"framework를 결정 축으로 띄우지 않는다"(G0 배너 관할)는 문장은 불변 — G1 STOP과 관할이
다름을 검수표에 기록.

- 리뷰 반영: 모순 A-1.

### 개정 5 — discipline-reviewer 감사 캐리어 신설 (`agent-discipline-reviewer.ttl`, R-3404)

Phase 1 lightweight 점검 항목(및 Phase 2 감사 공통)에 신설:

> 신규 HTTP/JSON API 표면이 함수형 Router·plain Django view로 결정(Phase 1: 명세)·구현
> (Phase 2: 코드)돼 있으면, 명세의 스택 결정에 승인 evidence 참조(STOP 승인 기록 파일
> 경로 또는 발주서·사용자 명시 지시 인용)가 있는지 대조한다. 참조가 없으면
> design-architect 소유 발견(blocker)으로 올린다.

- 신설: `R-3404 a djr:Obligation`, ISSUED append. 자기 문서 규범 — 추가 wiring은 구조
  검사 기준으로 확정.
- 리뷰 반영: 집행성 A-1·A-2(G1 감시자+감사 캐리어), 모순 A-3.

### 개정 6 — coder 반송 사유 추가 (`agent-coder.ttl`)

coder.md:60 "JSON API presentation은 승인된 명세의 stack·controller·module 결정을 그대로
집행한다"의 소유 규범 리비전 — 반송 사유 셋째 추가: 신규 표면 함수형/plain 결정에 승인
evidence 참조가 없으면 집행하지 않고 반송(토큰 표기는 coder.md 기존 반송 관례
(`TREE_CONTRACT_MISMATCH` 류)에 맞춰 구현 시 확정).

- 리뷰 반영: 집행성 A-4, 모순 A-3(coder 상반 지시 해소).
- **구현 확정 노트(2026-09-01)**: 기존 규범 리비전 대신 **R-3405 Override 신설**로 확정 — R-2588/R-2589와 동형(«그대로 집행 금지 + `TREE_CONTRACT_MISMATCH` 반송» Override가 R-2584를 리비전 없이 예외 처리하는 기존 패턴 재사용·신규 토큰 불요). 따라서 채번은 R-3403~R-3405 3건, 계수는 Norm/Work +3·Expression +7(신설 3·리비전 4)로 실측 확정(§4-2·§4-5의 계획 수치를 대체).

## 3. 사용자 결정 필요

- **D1**: 개정 1 문안 확정 — (a) 보강판(위 문안, 3개 리뷰 권고) 채택 여부.
  (b) 열거형은 리뷰 만장 기각 — 폐기 권고.
- **D2**: R-0698 amendment(STOP 승인 함수형 표면의 후속 수정 예외 후크) 포함 여부 —
  권장: 포함(미포함 시 R-0698 절대문과 R-3403이 discipline-reviewer에서 충돌).
- **D3**: 커밋 후 즉시 릴리즈(`make release`) 여부.

## 4. 절차 (레시피 + 리뷰 보정)

1. rdflib 구조 편집 + `ontology_canon.canon_turtle` 재직렬화 — 대상 ttl 6:
   agent-design-architect · implementation-django-ninja-final · architecture-api-final ·
   command-dddjango · agent-discipline-reviewer · agent-coder.
   (왕복 byte 동일: 3건 기확인, command-dddjango·discipline-reviewer·coder는 편집 전 확인.)
   모든 리비전 Expression에 prov:wasRevisionOf·djr:revision n+1·revisionKind +
   **Work currentExpression 교체** [집행성 B-5].
2. 채번: ISSUED에 R-3403·R-3404 append(말미 R-3402 확인됨 — 결번 없음).
3. `ontology_gate.py` green → `ontology_render.py --apply` ×6 doc_key.
4. LEDGER 재기준선: 재투영 graph 절 전건(6 문서 해당 절) append.
5. 계수표: NormShape **+2** · **WorkShape +2** [집행성 B-2] · ExpressionShape +6(신설 2·
   리비전 4; D2 포함 시 +7) — 구현 시 실측 재산정. q4 골든 `--emit` · `make rulepack`.
6. 소스 미러: `workspace/reference/{implementation-django-ninja,architecture-api}/reference/
   final.md` 옛 span 수동 교체 → `corpus_mirror_sync --write`.
7. **codex 의미 미러 손 반영** [집행성 B-1·모순 A-2]: `codex-dddjango/skills/
   dddjango-design-architect/SKILL.md`(«API 스택» 불릿) · `codex-dddjango/skills/dddjango/
   SKILL.md`(coordinator :74 상당) · discipline-reviewer·coder 상당 파일(실존 확인 후).
8. `manifest_seal.py --write` 재봉인 [집행성 B-3] → `make verify` green → 커밋.
9. 조감도 `ontology-adoption-map.html` 갱신 [집행성 B-4·상시 지침] + 레시피 메모리 정정
   ("agents codex md 없음" → design-architect 등 SKILL.md 실존).
10. (D3 승인 시) `make release`.

## 5. 리뷰 처분 대장

| 발견 | 처분 |
|---|---|
| 모순 A-1(coordinator 이중 진실) | 개정 4 신설 |
| 모순 A-2·집행성 B-1(codex 미러) | 절차 7 + 메모리 정정 |
| 모순 A-3·집행성 A-1·A-2(집행선) | 개정 5·6 신설 + R-3403 문안 반송 문장 |
| 모순 A-4(개정1↔3 wire 모순) | 개정 1 wire 재문언 + 개정 3 미열거-STOP 명시 |
| 모순 B-1(R-3134 닫힌 목록) | 개정 1 «정체/채택 분리» 문안으로 무력화 — R-3134 불변 |
| 모순 B-2(12-slot preserve 분기) | 개정 1 wire 문안이 동취지 — slot 개정 불요(구현 시 재검) |
| 모순 B-3·과적합 S3(HTML 오포섭) | 주어 한정+배제문+prefLabel 주어 |
| 모순 B-4·과적합 S1(명시 지시) | 동격+인용 조항 |
| 모순 B-5(전건/선반영) | 전건 조건 주어화 |
| 모순 C-1(anchor)·C-2(§2.2 표기)·C-3(R-0698) | 구현 시 확정·스킬명 병기·D2 |
| 과적합 S2(잔여 포괄)·S4(carveout 근거)·S5(정의)·S6(형식·gloss) | 개정 1·2 문안 반영 |
| 집행성 A-3(기록 형식)·A-5(기계 술어)·A-6(wiring) | 개정 1·2 문안+wiring 처분 |
| 집행성 B-2·B-3·B-4·B-5·B-6 | 절차 5·8·9·1·검수표 등재 |
