# T2-1 보강 — category→규칙 귀속 매핑표 v2 (설계 정본)

> **지위**: v1(2026-08-20 작성)에 대한 적대 리뷰 2레인(L-U 귀속 반증 · L-V 열린 스코프)과 그 중재
> **MEDIATION-2**(채택 40·부분 채택 4·기각 0)의 «귀속 판정 변경» 표 전건(U1~U12)과 부분 채택 4건을
> 사양으로 삼아 전면 재작성한 **v2 정본**이다. 원 처분(MEDIATION P#2·3·4+Q#1)의 본지 — «#N 귀속
> category는 실규칙 violation 구조화 엔트리로 이행·진짜 계약 전용만 계약 엔트리 존치» — 는 유효하되,
> 표면은 포매터 계약 v2를 따른다(**`SliceFindings`는 제거 대상** — 이행은 `Findings`/`Candidates`
> 구조화 엔트리+공용 `emit_all` 경유 · W2 정정). 재작성 2026-08-20 · 다음 관문: 반영 대조 레인 W → 코드 적용(V25 순서).
>
> **판정 기준**(v1 계승 — L-Q #1·MEDIATION 표): «규칙 ID가 tree-slice에 등장하는가»가 아니라
> **«이 category가 잡는 사건이 어느 규칙 문면의 술어에 포함되는가»**다. v2 추가 기준(U1~U6·U18):
> category가 서로 다른 술어의 사건을 섞으면 **category 를 원자 술어로 분할**하고, 분할된 각 술어가
> 자기 판정을 가진다 — «불확실» 분류는 소멸했다(U12 최종 장부 전건 확정). 판정 값 공간은
> {**#N 귀속** · **계약 유지** · **타 소유자 이관(방출 억제 — 소유자 단독)**} 셋뿐이다.
>
> **표면 전제**: 이 표는 귀속 «판단»만 정한다. 방출 표면(ordered emitter — findings.py 재설계 V1 ·
> line 인자 표면 제거 U15)과 판형·의도 변경 열거표는 포매터 계약 v2 가 소유하며, 귀속 판단은 표면
> 결정(동결 개정 5 — 사용자 결정 대기)과 독립으로 이월된다. «stdout byte 등가»는 V3 채택으로
> 대체 불변식(exit 의미론·위반 incident multiset·소비자 계약·검사 판정 결과 불변 + stdout 변경은
> «의도 변경 열거표» 통제)으로 정정됐다(잠정 — 마일스톤 추인 목록 등재).
>
> **적용 시 동반 의무**(V26 개정): 배포 검사기 코드 주석에는 **로컬 절대 경로를 쓰지 않는다** —
> 안정적인 `#N`·정본 문서명·규칙 문면 요약만 남긴다(부속 A-5). 상세 행 인용·중재 provenance 는
> 이 매핑표가 소유한다. 계수 골든 EXPECTED 갱신은 검사기별 사유와 함께(부록 B).

## 출처 핸들

| 핸들 | 실경로 |
|---|---|
| SPEC | `workspace/design/2026-08-08-tree-revision-spec.md` (규칙 문면 정본) |
| OWNER | `workspace/plan/2026-08-11-rule-owner-map.md` (소유 정본) |
| OVERLAP | `workspace/design/2026-08-12-prior-contract-overlap-review.md` (겹침 처분) |
| REG | `dddjango/commands/dddjango.md` (registry 레인 선언) |
| API | `dddjango/scripts/check-api-error-controller-contract.py` |
| EC | `dddjango/scripts/check-error-centralization.py` |
| CR | `dddjango/scripts/check-composition-root.py` |
| OA | `dddjango/scripts/check-openapi-error-declaration.py` |
| F0 | `dddjango/scripts/findings.py` (findings/0) |
| L-P·L-Q·MED | `workspace/design/2026-08-19-ontology-t2-1-adversarial/{L-P,L-Q,MEDIATION}.md` (1차 적대 검증) |
| L-U·L-V·MED2 | `workspace/design/2026-08-19-ontology-t2-1-adversarial/{L-U,L-V,MEDIATION-2}.md` (**v2 사양** — 선행 설계 리뷰·중재) |

## 저자 판단 요약 (v2)

1. **원자 술어 단위 판정**: 한 category가 서로 다른 규칙 술어의 사건을 섞으면(과포섭·주체 혼합)
   category 를 분할해 각 술어에 자기 판정을 준다 — v1 의 «과포섭이므로 계약 보수» 처분은 U1·U3~U6·
   U8~U10 이 전건 뒤집었다. 분할 category 의 신규 문자열은 본 표가 제안하고 적용 커밋이 확정한다.
2. **타 소유자 사건은 «계약 유지»가 아니라 «방출 억제»**: 술어가 타 검사기 소유 규칙(#117=
   context-isolation · #81/#488=layer-skeleton)과 축자 대응하는 사건은 이 검사기가 rule=null 로도
   방출하지 않는다 — 소유자 단독 방출로 이중 계수를 원천 차단한다(U9·U10·U11). 단 제거는
   **소유자 실발화를 픽스처로 실증한 뒤**에만 한다(U11 검증 의무 — 실증 실패 시 소유자 보강 선행).
3. **이중 방출은 선점 억제 + multiset 보존**: v1 의 `(rule, where)` dedupe 는 폐기(U13·U14 — 레인별
   locator 상이·openapi 앵커 레인 동축). §5 의 incident 설계로 교체 — 정밀 레인(code-profile) 활성
   대상에서 겹치는 tree 술어 방출을 선점 억제하고, 그 밖의 dedupe 는 하지 않는다(기본 원칙:
   **message·occurrence 보존 multiset — 제거 아님**, V4).
4. **불확실 분류 소멸**: v1 불확실 15행은 U12 최종 장부대로 전건 확정했다 — v2 에는 확정 판정만 남는다.
5. **리뷰 실증분 계승**: L-P/L-Q 실증(v1 계승)에 더해 L-U 반증 실패분(#N 21행 · 계약 52행 · 부속
   3건 — L-U 19·20·21·22·23)은 «리뷰 확정» 표기로 갈음한다. 수치는 실측이 계획을 이긴다(v1 계승 —
   api 20 · error-central 55+3 · composition 10+3 실측 확정).

## 자인 약점 (v2 에서 여전히 자신 없는 것 3)

1. **#125 귀속(API 행3·6)의 tree ⓓ 관계**: 같은 #125 가 tree 레인에서는 ⓓ 후보(info — API:6719),
   code 레인에서는 확정 violation 으로 나간다 — 한 규칙의 severity 이원 채널이 소비자(cross_matrix 의
   violation/info 분리 — MED2 V14)·debt 문법과 안 어긋나는지는 적용 커밋 실측 전이다. §5 의
   «확정이 후보를 이긴다»(code #125 발화 대상 handler 의 tree ⓓ#125 선점 억제) 방향도 저자 판단이다.
2. **분할 category 의 코드 구현 가능성**: U1 의 도메인/응용 provenance 분할은
   `_exception_origin_valid`(API:3162)의 layer 판별 재사용을 전제하는데, 혼합 tuple catch
   (`except (DomainErr, AppErr) as e`) 처럼 한 catch 가 양 층을 묶으면 전달 사건의 층이 단일 확정되지
   않는다 — 이 잔여는 U3 부분 채택 문면(«판정 불능 잔여는 계약 보수»)을 준용해 계약으로 내리지만,
   그 준용 자체가 U1 문면 밖의 저자 판단이다. U5 의 파일·parent 별 분할도 `_bare_registration_decorators`
   (CR:1334)가 수집 시점에 parent 문맥을 버리는 현행 구조의 재작성을 요구한다.
3. **U11 실발화 실증의 성공 여부**: layer-skeleton 이 V2 사건(`composition/` 여덟째 폴더)을 #81 로,
   V3 사건(`composition_root/` 부재)을 #488 로 **실제 발화하는지 미실측**이다 — 골든(#81×1,
   `workspace/tools/findings_count_matrix.py:65`)은 규칙 발화만 증명하지 이 사건 모양을 증명하지
   않는다. 실증 실패 시 소유자 보강이 선행되어 적용 순서(V25)가 늘어진다. (차순위 — CR 행6 의
   #437 분할분과 composition 자기 tree #437(CR:1844–1858)의 겹침은 픽스처 실측 전이다.)

---

## 1. check-api-error-controller-contract.py — code-profile 20 category → 원자 술어 23

레인 선언: registry #15(REG:122) — 08-04 API-error 선행 계약 레인 + 표준 트리 슬라이스(#120~#132·#474·#62).
현행 처분: `HANDLER_CATEGORIES` 2종만 `SliceFindings("#59")`, 나머지 18종 전부 `ContractFindings(rule=null)`
(API:34–46 · 방출부 API:6875–6894).

### 1.0 소유 규칙 11종 문면 (SPEC 정본 · OWNER 소유 행) — v1 무변

| # | 문면(축자) | SPEC | OWNER |
|---|---|---|---|
| #59 | «전역 예외 핸들러나 catch-all mapper 로 오류를 가로채지 않는다.» | 385 | 59 |
| #62 | «except Exception 을 쓰지 않고, 폴백을 둘 경우 도메인·응용 base 단위 catch 로 한정한다.» | 386 | 60 |
| #120 | «api/ 의 1차 축은 `<area>/` 다 — 기술 폴더(ninja/)를 만들지 않는다.» | 450 | 111 |
| #121 | «api/<area>/ 의 이름은 안쪽 application_layer/<area>/ 와 글자까지 같아야 한다.» | 451 | 112 |
| #123 | «api/<area>/ 의 진입점은 `<area>_controller.py` 파일 하나다.» | 452 | 113 |
| #124 | «컨트롤러는 요청 하나당 메서드 하나를 갖는다.» | 453 | 114 |
| #125ⓓ | «컨트롤러 메서드는 schema_in→command 변환 · 유스케이스 1회 호출 · result→schema_out 변환만 한다 — 입구에 로직을 두지 않는다.» (ast+ · discipline-reviewer 병기) | 454 | 115 |
| #126 | «도메인 예외를 ErrorSchema·상태 코드로 바꾸는 매핑을 컨트롤러 메서드 안에 직접 쓴다 — helper·factory·serializer·handler 등록 decorator·global mapper 로 옮기지 않는다.» | 455 | 116 |
| #131 | «기술 이름은 파일이 아니라 클래스에 붙는다 — NinjaTurnController.» | 458 | 119 |
| #132 | «라우트 데코레이터 · 인증 선언 · 상태 코드는 컨트롤러 파일에 온다.» | 459 | 120 |
| #474 | «바깥에 계약을 공개하는 입구 파일(…`<area>_controller.py`…)은 도메인 예외를 «타입»으로만 쓴다 — `except … as e` 로 묶은 이름을 그 파일 안에서 참조하면 위반이다.» | 771 | 399 |

인접(소유 밖 — 귀속 금지 근거): #129(SPEC:457)는 check-synthetic-infra-exc 소유(OWNER:118) ·
#63(SPEC:387)은 OA 소유(OWNER:61).

### 1.1 category 실측 — 20종 확정 · 분할 후 원자 술어 23

`_append_finding` 콜사이트 20곳 AST 전수 추출(v1 실측 유지): 정적 18 + 동적 2 = **20**.
v2 분할(U1·U3): 행7 → 2술어 · 행19 → 2술어 · 행20 → 2술어 ⇒ **원자 술어 23**.
Finding dataclass(API:198–204): 현행 `path·lineno·category·shown` — `symbol` 필드 추가는 부속 A-1(U17·V10).

### 1.2 매핑표 (원자 술어 23 = #N 12 · 계약 11 · 억제 0)

| # | category(코드 문면 그대로) | 생성 지점 | 판정 | 근거(규칙 문면 인용+출처) |
|---|---|---|---|---|
| 1 | `managed try cannot have else/finally` | API:3229 | 계약 | 소유 11종 어느 문면에도 try 문 형태(else/finally) 술어가 없다 — managed-try 형태는 08-04 계약 고유(«narrow one-call try» — REG:122). **리뷰 확정(L-U 20)** |
| 2 | `managed try body must be one root-call statement` | API:3237 | 계약 | «one-call try» 형태는 08-04 계약 문면(REG:122) 소유 — #125 의 «유스케이스 1회 호출»은 메서드 수준 술어라 별개. **리뷰 확정(L-U 20)** |
| 3 | `raise inside managed try` | API:3245 (방출 API:3244) | **#125** | «컨트롤러 메서드는 변환·유스케이스 1회 호출·변환**만** 한다 — 입구에 로직을 두지 않는다»(SPEC:454) — code-profile 대상은 route decorator 가 있는 operation 뿐(API:2337)이라 그 안의 `raise` 는 허용 동작 밖의 확정 위반 · OWNER:115. **U2 채택**(L-U 2 — tree ⓓ 채널의 존재는 code 확정 술어를 rule=null 로 만들 근거가 아니다). tree ⓓ#125 와의 이중 방출은 §5 선점 억제 |
| 4 | `bare catch forbidden` | API:3251 | **#62** | «except Exception 을 쓰지 않고 … base 단위 catch 로 한정한다»(SPEC:386) — bare `except:` 는 catch-all 의 극단형 · L-P #2 실증 · OWNER:60. **리뷰 확정(L-U 19)**. tree #62 겹침은 §5 |
| 5 | `catch must be direct own-BC application/domain exception` | API:3263 | **#62** | 같은 문면 — 자기 BC 도메인·응용 예외 밖 catch = «한정» 위반 · L-P #2 실증 · OWNER:60. **리뷰 확정(L-U 19)** |
| 6 | `raise inside managed catch` | API:3274 (방출 API:3270) | **#125** | 행3 과 동일 — catch arm 안 `raise` 도 «입구 로직 금지»(SPEC:454) 밖 동작. **U2 채택** |
| 7 | `caught exception forwarding forbidden` | API:3278 (방출 API:3277) | **분할(U1·V5)** — ⓐ 도메인 예외 전달 = **#474** · ⓑ 응용 예외 전달 = **계약** | #474 의 주어는 «도메인 예외»뿐(SPEC:771 · OWNER:399)인데 `_exception_origin_valid` 는 application/domain 양 층을 승인하고(API:3162) 구분 없이 한 category 로 방출한다(API:3277) — catch 출처(provenance)로 category 분리 저작: ⓐ `caught domain exception forwarding forbidden`(#474) · ⓑ `caught application exception forwarding forbidden`(계약 — 08-04 managed catch 규율 고유). 층 미확정 잔여(혼합 tuple catch)는 계약 보수(U3 부분 채택 문면 준용 — 자인 약점 2). ⓐ와 tree #474 겹침은 §5 |
| 8 | `same call cannot use exception and Result mapping` | API:3585 | 계약 | Result 매핑 채널은 08-04 계약 고유 개념. **리뷰 확정(L-U 20)** |
| 9 | `orphan/pre-call error mapping is not causally owned by an application call` | API:3597 | 계약 | «호출 인과 소유» 술어는 08-04 고유 — #126(SPEC:455)은 매핑의 «장소»만 문다. **리뷰 확정(L-U 20)** |
| 10 | `Result/error mapping must immediately follow its try-free call assignment` | API:3610 | 계약 | 인접 배치 술어는 08-04 고유. **리뷰 확정(L-U 20)** |
| 11 | `FrameworkErrorSchema construction is not owned by an approved catch/Result arm` | API:3633 | 계약 | arm 소유 개념은 08-04 고유 — 컨트롤러 안 사건이라 #126 «옮기지 않는다» 밖. **리뷰 확정(L-U 20)** |
| 12 | `error Status mapping is not owned by an approved catch/Result arm` | API:3645 | 계약 | 행11 동일 논거. **리뷰 확정(L-U 20)** |
| 13 | `custom Ninja exception_handler forbidden` | API:4006 | **#59 (유지)** | «전역 예외 핸들러 … 로 가로채지 않는다»(SPEC:385) · OWNER:59 · L-P «#59 집중 검증 — 반증 실패»(L-P.md:13). **리뷰 확정(L-U 19)** |
| 14 | `custom Ninja add_exception_handler forbidden` | API:4014 | **#59 (유지)** | 행13 동일. **리뷰 확정(L-U 19)** |
| 15 | `prepared FrameworkErrorSchema factory/helper forbidden` | API:4302 | **#126** | «helper·factory·…로 옮기지 않는다»(SPEC:455) — 축자 · L-P #2 실증 · OWNER:116. **리뷰 확정(L-U 19)** |
| 16 | `FrameworkErrorSchema raw HTTP serializer helper forbidden` | API:4310 | **#126** | «…serializer…로 옮기지 않는다»(SPEC:455) — 축자 · OWNER:116. **리뷰 확정(L-U 19)** |
| 17 | `exception-to-FrameworkErrorSchema mapping helper forbidden` | API:4318 | **#126** | «매핑을 … helper…로 옮기지 않는다»(SPEC:455) — 축자(판정 재료 API:4317) · OWNER:116. **리뷰 확정(L-U 19)** |
| 18 | `FrameworkErrorSchema/model config mutation in controller forbidden` | API:6534 | **계약 (확정 — 불확실 소멸)** | mutation 대상(controller 안 model config — API:4352–4439)과 #63 의 OpenAPI `response`/postprocessor 술어(SPEC:387)는 객체가 다르다 — **U12 확정**(L-U 12 실측: API:4365). #63 소유자는 OA(OWNER:61)라 교차 방출도 금지(v1 논거 유지) |
| 19 | `managed catch must directly construct FrameworkErrorSchema and return Status` | 동적 — API:3294 지정·3087/3134 방출 | **분할(U3)** — ⓐ helper/factory/serializer 위임 = **#126** · ⓑ 본문 형태 오류 = **계약** | `_validate_mapping_body` 는 본문 길이(len<2)·constructor 불명·constructor 인자·중간 문장·Status 반환 오류를 한 category 로 합친다(API:3084·3105·3119). 그중 helper/factory 경유 constructor 는 #126 «helper·factory 로 옮기지 않는다»(SPEC:455) 직접 포섭 — 실패 원인별 category 분해 저작: ⓐ `managed catch delegates error construction to helper/factory/serializer`(#126) · ⓑ 기존 문면 유지(계약). 분해 후 판정 불능 잔여는 계약 보수(**U3 부분 채택** — 전면 재분석 기각) |
| 20 | `Result arm must directly construct FrameworkErrorSchema and return Status` | 동적 — API:3564 지정·3087/3134 방출 | **분할(U3)** — 행19 와 동일 2분(ⓐ #126 · ⓑ 계약) | 행19 와 같은 방출 지점 공유 — 동일 논거·동일 분해 |

### 1.3 이중 방출 — §5 로 이관

v1 의 «(rule, where) 단위 dedupe» 처분(구 §1.3-a·b)은 **폐기**(U13 — tree #474 는 Name 참조 행,
code 는 handler 행이라 키가 애초에 안 맞는다). #62(행4·5)·#474(행7ⓐ)·#125(행3·6)의 tree 겹침 처분은
§5 overlap 표가 소유한다. (c) 행15~17 의 #126 은 tree #126(API:6707 — decorator 형)과 사건이 달라
겹침 없음(v1 유지).

### 1.4 #59 현행 유지 확인

`HANDLER_CATEGORIES` 2종(API:41–46)의 `SliceFindings("#59")` 방출(API:6880–6887)은 옳다 — OWNER:59 +
SPEC:385 + L-P 반증 실패. `symbol=finding.category` 오입력 정정은 부속 A-1(전건 null 처분이 아니라
**symbol 필드 신설·확정 재료 채움**으로 개정 — U17).

---

## 2. check-error-centralization.py — code-profile 55 category + blocker 3패턴 → 원자 술어 65

레인 선언: registry #2(REG:109). 현행 처분: code-profile 전건 `ContractFindings(rule=null)`(EC:4677–4688).

### 2.0 소유 규칙 4종 문면 — v1 무변

| # | 문면(축자) | SPEC | OWNER |
|---|---|---|---|
| #114 | «driving_layer/api/bc_error_schema.py 는 BC 당 정확히 한 파일이고 **항상 있다** — HTTP 오류를 아직 안 여는 BC 에도 «빈 파일»로 있다.» | 446 | 107 |
| #568 | «이름의 자는 «폴더 안이면 접두, 폴더 밖이면 접미»다 — schema/schema_in.py ↔ api/bc_error_schema.py.» | 890 | 486 |
| #572 | «bc_error_schema.py 에는 응답 본문 클래스 `<Bc>ErrorSchema` 와 오류 코드 `<Bc>ErrorCode` 가 함께 온다 — … 〔08-15 승인 예외〕 BC base 가 공통 스키마의 «식별자 field» 하나를 자기 `<Bc>ErrorCode` 로 정확히 좁히면서 공통의 default 를 잃어 required 가 되는 모양은 canon … 그 밖의 required/default 의미 변경은 계속 위반.» | 894 | 490 |
| #636 | «bc_error_schema.py 의 `<Bc>ErrorCode` 는 StrEnum 이다 — Literal·맨 문자열 상수 모음으로 대신하지 않는다.» | 1165 | 549 |

인접(소유 밖): #117 «BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다»(SPEC:447)는 **check-context-isolation
소유**(OWNER:108 — red 골든 #117×1 실재, `workspace/tools/findings_count_matrix.py:59`).

tree-slice 실방출(겹침 판단 재료 — v1 실측 유지): #114 부재 EC:4519·2개+ EC:4545 · #568 EC:4528·4538 ·
#572 부재 EC:4576·4583 · #636 EC:4592. tree 위반 시 anchor 미지정이면 code 레인 전 exit 2 선점(EC:4634–4635).

### 2.1 실측 개요

콜사이트 60곳 → category 55종(정적 46+동적 9) + blocker 3패턴(v1 실측 유지).
v2 분할(U8·U9·U10·U12): 행17 → 3술어 · 행23 → 3술어 · 행24 → 2술어 · 행30 → 2술어 · B1 → 2술어
⇒ **원자 술어 65**. Finding dataclass(EC:238–249) `symbol` 추가는 부속 A-1.

### 2.2 공통 모듈 군 (8종 · `_analyze_common` EC:2701–2962) — 전건 계약 · 리뷰 확정(L-U 20)

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 1 | `exactly one common FrameworkErrorSchema required` | EC:2726 | 계약 | 소유 4종 술어는 전부 BC 쪽 `bc_error_schema.py` 가 주어(SPEC:446·890·894·1165) — 공통 모듈 형태는 08-04 계약 고유(EC:4699) |
| 2 | `common FrameworkErrorSchema must directly inherit ninja.Schema` | EC:2731→2740 | 계약 | 동일 |
| 3 | `common FrameworkErrorSchema direct mutation/side effect forbidden` | EC:2763 | 계약 | 동일 |
| 4 | `common module Enum/public/derived class forbidden` | EC:2905 | 계약 | 동일 |
| 5 | `common module helper/function forbidden` | EC:2913 | 계약 | 동일 |
| 6 | `common module functional Enum forbidden` | EC:2917 | 계약 | 동일 |
| 7 | `common module public artifact forbidden` | EC:2930 | 계약 | 동일 |
| 8 | `common module helper/mutation/side effect forbidden` | EC:2936·2955 | 계약 | 동일 |

### 2.3 클래스 본문 공용 군 (14종 · `_class_member_findings` EC:2186–2410)

한 콜사이트 집합이 공통 클래스(EC:2841)·BC base(EC:3387)·concrete(EC:3556) 세 주체에 같은 category 로
발화한다. v1 의 «주체 혼합이므로 전 14종 계약» 처분 중 **행17 은 U8 이 뒤집었다** — 주체 분리
(common/base/concrete discriminant)를 적용하고, base 사건은 행36(#572)과 동일 사건이므로 **행36 finding
단독 방출**(행17 의 base 방출 제거 — rule=null 중복 소거). 나머지 13종은 계약 유지 · 리뷰 확정(L-U 20).

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 9 | `class decorator outside common FrameworkErrorSchema` | EC:2226 | 계약 | #572 문면(SPEC:894)의 술어는 동거·좁힘·required/default 뿐. **리뷰 확정(L-U 20)** |
| 10 | `class keyword config outside common FrameworkErrorSchema` | EC:2234 | 계약 | 동일 |
| 11 | `Pydantic hook override outside common FrameworkErrorSchema` | EC:2248·2325 | 계약 | 동일 |
| 12 | `model_config override outside common FrameworkErrorSchema` | EC:2258·2334 | 계약 | 동일 |
| 13 | `dynamic ClassVar assignment outside common FrameworkErrorSchema` | EC:2276 | 계약 | 동일 |
| 14 | `schema decorator proxy outside common FrameworkErrorSchema` | EC:2289·2347 | 계약 | 동일 |
| 15 | `dynamic private class assignment outside common FrameworkErrorSchema` | EC:2300·2360 | 계약 | 동일 |
| 16 | `duplicate public field` | EC:2309 | 계약 | 동일(allowed_fields 산식 — 공통 자기 본문 발화 가능) |
| 17 | `additional public field` | EC:2312 (base 주체 EC:2308·3387) | **분할(U8)** — ⓐ common = **계약** · ⓑ base = **#572 — 행36 finding 단독 방출(이 category 의 base 방출 제거)** · ⓒ concrete = **계약** | base 는 허용 field 하나만 전달돼(EC:3387) 추가 field 시 이 category(EC:2308)와 행36 `…must narrow exactly one…`(EC:3232)이 **같은 사건**을 이중 방출한다(L-U 8 실측) — 사건은 #572 하나이므로 base 주체에서 이 category 를 방출하지 않는다(주체 discriminant 분기·stdout 감소는 의도 변경 열거표 등재). common/concrete 는 소유 문면 밖 — 계약 |
| 18 | `complex class assignment outside common FrameworkErrorSchema` | EC:2316 | 계약 | 군 판단. **리뷰 확정(L-U 20)** |
| 19 | `public class assignment/helper` | EC:2342 | 계약 | 동일 |
| 20 | `validator/public helper` | EC:2379 | 계약 | 동일 |
| 21 | `public nested class/helper` | EC:2385 | 계약 | 동일 |
| 22 | `executable class-body statement outside common FrameworkErrorSchema` | EC:2404 | 계약 | 동일 |

### 2.4 BC error 모듈 잉여물 군 (2종 · `_bc_module_artifact_findings` EC:2431–2481)

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 23 | `BC error module extra class/helper forbidden` | EC:2445 (실발화 EC:2443) | **분할(U9)** — ⓐ 예상 밖 direct-common class = **#572 — 행35 finding 단독 방출(이 category 의 중복 방출 제거)** · ⓑ 두 번째 ErrorCode 컨테이너 = **#117 — EC 방출 억제(소유자 context-isolation 단독)** · ⓒ 기타 잉여물 = **계약** | ⓐ: 같은 사건이 행35 `second BC FrameworkErrorSchema base`(EC:3194)로 이미 #572 방출 — rule-null 중복 소거(L-U 9 실측). ⓑ: 술어가 #117(SPEC:447)과 축자 — 소유자 단독(OWNER:108). **U11 검증 의무 준용**: 적용 커밋에서 context-isolation 이 «bc_error_schema.py 안 두 번째 컨테이너» 사건 모양을 실발화함을 픽스처로 실증 후 제거(골든 #117×1 은 규칙 발화만 증명 — 이 사건 모양은 신규 실증). ⓒ: «함께 온다»(SPEC:894)는 닫힌 목록 명시가 없어(#437·#85 대조 — v1 논거) 잉여물 금지는 08-04 declarative-module 술어 |
| 24 | `BC error module helper/mutation/side effect forbidden` | EC:2475 (실발화 EC:2459) | **분할(U9)** — ⓐ functional Enum(두 번째 ErrorCode 성 할당) = **#117 — EC 방출 억제(소유자 단독)** · ⓑ 기타 helper/mutation = **계약** | ⓐ: 행31 과 같은 assignment 가 이 category 로도 잡힌다(L-U 9 — EC:2459) — #117 사건이므로 소유자 단독(검증 의무 행23ⓑ 와 동일). ⓑ: 08-04 계약 고유 |

### 2.5 ErrorCode enum 내부 군 (5종 · EC:3021–3099) — 전건 계약 · 리뷰 확정(L-U 20)

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 25 | `Enum public helper forbidden` | EC:3059·3063 | 계약 | #636(SPEC:1165)은 컨테이너 «타입»만 규정 — wire-code 규약은 08-04 고유(EC:4700) |
| 26 | `duplicate Enum member` | EC:3074 | 계약 | 동일 |
| 27 | `wire code must be snake_case` | EC:3090 | 계약 | 동일 |
| 28 | `ErrorCode requires a wire-code member` | EC:3092 | 계약 | 동일 |
| 29 | `duplicate wire code in Enum: {value}` (동적) | EC:3098 | 계약 | 동일 |

### 2.6 BC 컨테이너 존재·유일 군 (5종 · `_analyze_bc_module` EC:3102–3219) — U10 확정의 본체

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 30 | `exactly one <Bc>ErrorCode required` (동적 — EC:3132 산식) | EC:3142 (판정식 EC:3140 `len(enums)!=1`) | **분할(U10)** — ⓐ 0개(부재) = **#572** · ⓑ 2개 이상 = **#117 — EC 방출 억제(소유자 단독)** | ⓐ: 부재는 «`<Bc>ErrorCode` 가 함께 온다»(SPEC:894) 축자 위반 — category 분리 저작(`missing <Bc>ErrorCode`). tree #572(EC:4581–4587) 겹침은 §5 선점 억제. ⓑ: 복수는 «두 번째 ErrorCode 컨테이너 금지»(#117 — SPEC:447) 사건 — 소유자 단독(검증 의무 행23ⓑ 와 동일). **U10·U12 확정 — 불확실 소멸** |
| 31 | `second ErrorCode/StrEnum container` | EC:3153·3158 (실발화 EC:3149·3154) | **#117 사건 — EC 방출 억제(소유자 context-isolation 단독)** | 술어가 #117(SPEC:447)과 축자 · 소유자 OWNER:108 — 이 category 의 계약 방출 자체를 제거한다(**U10** — rule=null 로도 안 낸다: P#1 동형 이중 계수의 rule-null 판). **U11 검증 의무 준용**: 적용 커밋에서 context-isolation 실발화 픽스처 실증 후 제거 |
| 32 | `{enum_name} must directly inherit enum.StrEnum` (동적) | EC:3171→3180 | **#636** | «`<Bc>ErrorCode` 는 StrEnum 이다»(SPEC:1165) — 축자 포섭(EC:3171 — L-U 10 실측) · OWNER:549. tree #636(EC:4588–4596) 겹침은 §5 선점 억제 — «겹침 있음»은 승격 보류 사유가 아니다(**U10 확정**) |
| 33 | `exactly one {base_name} required` (동적 — `<Bc>ErrorSchema …`) | EC:3187 (판정식 EC:3184) | **#572** | `<Bc>ErrorSchema` 부재/복수는 «…와 …가 함께 온다»(SPEC:894)의 schema 동거 술어(L-U 10 실측) · OWNER:490. tree #572(EC:4574–4580) 겹침은 §5. **U10 확정** |
| 34 | `{base_name} must directly inherit common FrameworkErrorSchema` (동적) | EC:3210→3219 | **계약 (확정 — 불확실 소멸)** | 공통 직상속은 #572 승인 예외 절의 «전제»일 뿐 명시 술어가 아니다 — **U12 확정**(L-U 12: direct inheritance 전제는 문면에 없음) |

### 2.7 BC base 좁힘 군 (8종 · EC:3220–3395) — #572 승격의 본체

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 35 | `second BC FrameworkErrorSchema base` | EC:3198 (실발화 EC:3194) | **#572** | «…`<Bc>ErrorSchema` 와 …가 함께 온다»(SPEC:894 — 단수 동거) 위반 · L-P #3 축자 지목 · OWNER:490. **리뷰 확정(L-U 19)**. 행23ⓐ 의 중복 방출 제거로 이 finding 이 사건 단독 방출 |
| 36 | `BC FrameworkErrorSchema base must narrow exactly one common field to own ErrorCode` | EC:3233 (판정식 EC:3232) | **#572** | «식별자 field **하나**를 … **정확히** 좁히면서»(SPEC:894) · L-P #3 실증 · MED 채택. **리뷰 확정(L-U 19)**. 행17ⓑ 의 중복 방출 제거로 base additional-field 사건은 이 finding 단독 |
| 37 | `BC FrameworkErrorSchema discriminator must override common field` | EC:3260 | **#572** | 좁힘의 대상은 «공통 스키마의 식별자 field»(SPEC:894). **리뷰 확정(L-U 19)** |
| 38 | `BC base must preserve common annotation/nullability while narrowing str to own ErrorCode` | EC:3289 | **#572** | «**정확히** 좁히면서 … 그 밖의 … 의미 변경은 계속 위반»(SPEC:894). **리뷰 확정(L-U 19)** |
| 39 | `BC base field metadata must match common FrameworkErrorSchema` | EC:3303 | **계약 (확정 — 불확실 소멸)** | 문면이 명시한 «그 밖의» 변경은 «required/default 의미»다(SPEC:894) — metadata(alias 등) 확대는 축자 밖. **U12 확정** |
| 40 | `BC base must preserve common required/default semantics` | EC:3341 | **#572** | «그 밖의 **required/default 의미 변경**은 계속 위반»(SPEC:894) — 축자. **리뷰 확정(L-U 19)** |
| 41 | `raw string FrameworkErrorSchema discriminator` | EC:3352(base)·3522(concrete) | **계약 (확정 — 불확실 소멸)** | raw default/주체 혼합 — 대응 문면 없음(**U12 확정** — L-U 12). 주체 분리 없이 전 주체 계약 |
| 42 | `BC base discriminator default must be own ErrorCode member or None` | EC:3379 (판정식 EC:3365) | **계약 (v1 #572 취소 — U7)** | 승인 예외는 «공통 default 를 잃어 required 가 되는 모양»만 canon 으로 선언(SPEC:894) — «own member 또는 None 만 허용»은 문면에서 도출되지 않는다(`None` default 는 default 상실/required 가 아니다 — L-U 7 실측: 판정식은 required 아님·None 아님·member 아님 전부를 잡는다). #572 로 올리려면 규칙 문면 개정이 선행 — 현 문면 기준 계약 |

### 2.8 concrete 군 (9종 · EC:3397–3556) — 전건 계약 · 리뷰 확정(L-U 20)

소유 4종 문면의 주어는 파일·공통 pair·base 좁힘까지 — concrete 형태 술어는 없다(v1 논거 유지).

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 43 | `{node.name} must directly inherit {base_name}` (동적) | EC:3419→3428 | 계약 | «direct no-arg concrete/event-specific BC-base ErrorSchema»(REG:122) — 08-04 고유 |
| 44 | `concrete adds field outside common shape` | EC:3435 | 계약 | 동일 |
| 45 | `concrete field metadata must match common FrameworkErrorSchema` | EC:3450 | 계약 | 동일 |
| 46 | `concrete discriminator must preserve common annotation/nullability while using own ErrorCode` | EC:3464→3476 | 계약 | 동일 |
| 47 | `concrete field annotation/nullability must match common FrameworkErrorSchema` | EC:3474→3476 | 계약 | 동일 |
| 48 | `concrete field must have a no-arg default: {field_name}` (동적) | EC:3484 | 계약 | 동일(REG:109) |
| 49 | `concrete missing required default: {field_name}` (동적) | EC:3499 | 계약 | 동일 |
| 50 | `concrete discriminator default must use own ErrorCode member` | EC:3540 | 계약 | 동일 |
| 51 | `concrete discriminator requires own ErrorCode default` | EC:3549 | 계약 | 동일 |

### 2.9 raw 코드·전 프로젝트 군 (4종) — 전건 계약 · 리뷰 확정(L-U 20)

| # | category | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 52 | `raw string discriminator constructor argument` | EC:3913 | 계약 | 사용처 술어는 소유 4종 문면 밖 — #636 은 «정의»의 타입만(SPEC:1165) |
| 53 | `raw string one-step discriminator assignment` | EC:4079 | 계약 | 동일 |
| 54 | `concrete FrameworkErrorSchema outside canonical module` | EC:4108 | 계약 | 정본 모듈 밖 거주 술어는 소유 문면에 없음 — #117 은 ErrorCode 한정+타 소유(OWNER:108) |
| 55 | `duplicate project code wire value: {value}` (동적) | EC:4433 | 계약 | «project-wide unique wire code»는 08-04 계약 문면(EC:4700) |

### 2.10 blocker 3패턴 (list[str] — 방출 시 file="(code-profile)" EC:4680)

| # | blocker 문면 | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| B1 | `필수 canonical FrameworkErrorSchema artifact 부재: {path}` | EC:674 (path ∈ {공통 모듈} ∪ {BC별 `_bc_error_path(bc)`} — EC:670–674) | **분할 확정(U12 — 불확실 소멸)** — ⓐ BC `bc_error_schema.py` 경로 = **#114** · ⓑ 공통 모듈 경로 = **계약** | ⓐ: «BC 당 정확히 한 파일이고 **항상 있다**»(SPEC:446) 축자 · OWNER:107 · **리뷰 확정(L-U 19 — BC-path #114)**. tree #114(EC:4519 — 대상 집합: api/ 존재 BC 한정 EC:4511) 겹침은 §5 선점 억제. ⓑ: 공통 모듈 존재 요구는 소유 문면 밖(L-U 21 — 경로 재료 3패턴 전건 반증 실패). 분할 실현은 blocker 구조화(부속 A-2 — discriminant, V9)가 선행 |
| B2 | `필수 common artifact 부재: framework/ninja/__init__.py` | EC:4373 | 계약 | 공통 모듈 존재 술어는 소유 4종 밖. **리뷰 확정(L-U 20)** |
| B3 | `필수 common artifact 부재: framework/ninja/framework_error_schema.py` | EC:4375 | 계약 | 동일 |

blocker 의 file 실경로 복원(P#9·Q#4 채택)·구조화 discriminant(V9)는 부속 A-2.

---

## 3. check-composition-root.py — code-profile 10 category + DI 3 → 원자 술어 18

레인 선언: registry #16(REG:123). 소유 18종(OWNER:79–105·369–371·420–432).
현행 처분: code 레인(CR:1937–1944)·DI 레인(CR:620–685) 전부 `ContractFindings(rule=null)`.
실측 정정(v1 유지): «9 category»는 실측 **10**(정적 8+동적 2). v2 분할(U4·U5·U6): 행5 → 2술어 ·
행6 → 4술어 · 행10 → 2술어 ⇒ code 14 + DI 3 = **원자 술어 18**. `symbol` 추가는 부속 A-1.

### 3.0 관련 소유 규칙 문면

| # | 문면(축자) | SPEC | OWNER |
|---|---|---|---|
| #107 | «api/api_router.py 는 `def register_<bc>_api(api)` 등록 함수 하나만 갖는다.» | 439 | 100 |
| #108 | «api_router.py 는 전역 API 객체를 import 하지 않고 인자로 받는다 — BC 가 프로젝트를 import 하지 않는다.» | 440 | 101 |
| #109 | «등록은 register_<bc>_api(api) 함수 안에서만 하고 module top-level 에서 register_controllers 를 부르지 않는다(부작용 등록 금지).» | 441 | 102 |
| #111 | «api_router.py 가 하는 일은 자기 BC 의 컨트롤러를 import 해 api.register_controllers(...) 를 부르고 경로 접두사·태그를 정하는 것뿐이다.» | 443 | 104 |
| #437 | «`<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다 — … 닫힌 허용 목록…» (composition 자기 tree 레인 실소유 — CR:1844–1858) | 754 | 369 |
| #440 | «`<project>/urls.py` 는 라우터 «등록»만 한다 — 각 BC 의 register_<bc>_api(api) 를 명시적으로 부른다.» | 755 | 370 |
| #441 | «`<project>/urls.py` 는 BC 안의 심볼을 import 해서 쓰지 않는다 — 예외는 … 그 함수 import 하나뿐이다.» | 756 | 371 |
| #497 | «composition_root/ 는 파일이 아니라 폴더이고 «결선 하나 = 파일 하나»다 — 지금은 dependency_wiring.py 와 event_wiring.py 둘이다.» | 823 | 420 |
| #84 | «composition_root/ 는 BC 루트에 두고 네 층 폴더 어디에도 두지 않는다.» (인접) | 413 | 79 |

인접(소유 밖 — 억제 근거): #81 «BC 루트 바로 아래 일곱 가지만 — 여덟째는 없다»(SPEC:410 · OWNER:76)와
#488 «부모가 있으면 고정 이름 칸이 반드시 존재한다»(SPEC:814 · OWNER:411)는 **check-layer-skeleton
소유**(red 골든 #81×1 — `workspace/tools/findings_count_matrix.py:65`).

### 3.1 registrar/URLconf — code 원자 술어 14 (`_composition_semantics` CR:1557–1611)

| # | category(코드 문면 그대로) | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| 1 | `registrar imports selected project API` | CR:1387 | **#108** | «전역 API 객체를 import 하지 않고 인자로 받는다»(SPEC:440) — 축자(CR:1376–1387) · L-P #4 축 확정 · OWNER:101. **리뷰 확정(L-U 19)** |
| 2 | `additional public registrar function` | CR:1398 | **#107** | «등록 함수 **하나만** 갖는다»(SPEC:439) · OWNER:100. **리뷰 확정(L-U 19)** |
| 3 | `exactly one sync {spec.function_name} function required` (동적) | CR:1404 | **#107** | 같은 문면 — 부재·중복·async(CR:1402) 전부 «하나만» 위반. **리뷰 확정(L-U 19)** |
| 4 | `registrar signature must be one required positional parameter` | CR:1430 | **#107** | 문면이 시그니처를 축자로 적는다 — «`def register_<bc>_api(api)`»(SPEC:439). tree 도 arity 를 #107 로 낸다(CR:1799–1801). **리뷰 확정(L-U 19)** |
| 5 | `register_controllers outside canonical registrar owner` | CR:1467·1579·1598 | **분할(U4)** — ⓐ lexical owner 실제 함수 밖(module top-level 등록 — 세 파일 공용) = **#109** · ⓑ 함수 안 wrong receiver/parameter rebind = **계약** | ⓐ: «등록은 … 함수 **안에서만** 하고 module top-level 에서 … 부르지 않는다»(SPEC:441) · L-P #4 실증 · OWNER:102. ⓑ: 함수 안이어도 receiver 가 incoming parameter 아님/rebound 면 같은 category 로 방출된다(CR:1443·1466 — L-U 4 실측) — 그 술어는 #109 문면 밖이라 별도 category 저작(`registrar call on wrong receiver or rebound parameter`) 후 계약 유지 |
| 6 | `register_controllers decorator side effect` | CR:1471·1583·1602 (수집 CR:1334 — parent 무시) | **분할(U5 — 파일·lexical parent 별)** — ⓐ api_router 모듈층 = **#109** · ⓑ `<project>/api.py` = **#437** · ⓒ urls.py = **#440** · ⓓ 함수 내부 decorator = **계약** | ⓐ: «(부작용 등록 금지)»(SPEC:441). ⓑ: api.py 사건의 주어는 «닫힌 허용 목록»(SPEC:754 · OWNER:369 — composition 자기 tree 레인이 실소유 CR:1844–1858, 자기 검사기 내 귀속이라 교차 방출 아님. tree #437 과의 겹침은 §5 관찰 대상). ⓒ: URLconf 사건의 주어는 «라우터 등록만 한다»(SPEC:755 · OWNER:370). ⓓ: 중첩 함수 decorator 는 세 문면 어느 주어도 아님 — 계약(U5 확정 — L-U 5 의 «#111 또는 계약» 중 계약 채택). category 4분 저작 필요 |
| 7 | `canonical registrar has no direct register_controllers call` | CR:1475 | **#111** | «…를 **부르고** …뿐이다»(SPEC:443) — 직접 호출 부재는 «하는 일» 불이행 · L-P #4 실증 · OWNER:104. **리뷰 확정(L-U 19)** |
| 8 | `registrar call must be a module-level direct event` | CR:1527 | **#440** | «**명시적으로** 부른다»(SPEC:755) — 조건부·간접 호출(CR:1526) 위반 · OWNER:370. **리뷰 확정(L-U 19)** |
| 9 | `registrar URLconf call has wrong arity` | CR:1533 | **#440** | 호출 형태 «register_<bc>_api(**api**)» 축자(CR:1532). **리뷰 확정(L-U 19)** |
| 10 | `{spec.function_name} must be called exactly once (actual {count})` (동적 — 판정식 CR:1544 `count != 1`) | CR:1548 | **분할(U6·V6)** — ⓐ count==0(부재) = **#440** · ⓑ count≥2(중복) = **계약** | ⓐ: «**각 BC 의** register_<bc>_api(api) 를 명시적으로 부른다»(SPEC:755) — 0회는 축자 포섭 · L-P #4 축 계승. ⓑ: «정확히 한 번»은 #440 문면이 아니라 선행 계약 문면(CR:1950–1952)에만 있다(v1 자인 약점 2 를 U6 이 확정) — category 분리 저작: ⓐ `registrar call missing`(#440) · ⓑ `duplicate registrar call`(계약). 중복 호출을 #440 으로 만들려면 규칙 문면·owner-map 정식 개정이 선행(V6) |

#441 참고(v1 유지): 이 레인에 #441 대응 category 는 없다 — tree-slice(CR:1877) 단독 방출 · 관할 밖.

### 3.2 DI 레인 V1~V3 (`_filtered_di_findings` CR:620–685)

| # | 사건(코드 문면 요지) | 생성 지점 | 판정 | 근거 |
|---|---|---|---|---|
| V1 | `{local} — 단일 파일 composition_root.py 모양은 트리에 없다 — 정본은 BC 루트 «폴더» composition_root/(트리 2행)다` | CR:657–666 | **#497** | «composition_root/ 는 **파일이 아니라 폴더**이고 «결선 하나 = 파일 하나»다»(SPEC:823) — 축자 · L-Q #1 확정 실측(tree 는 폴더 부재 시 즉시 반환 CR:1712–1723 이라 이 사건에 못 닿는다) · OWNER:420 · MED 채택. **리뷰 확정(L-U 19)** |
| V2 | `composition/ 폴더에 배선 코드({파일들}) — DI 조립은 BC 루트 «폴더» composition_root/…가 소유한다` | CR:644–655 (검사 CR:643) | **#81 사건 — composition 방출 억제(소유자 layer-skeleton 단독)** | off-tree `composition/` 는 «BC 루트 바로 아래 일곱 가지만 — 여덟째는 없다»(#81 — SPEC:410 · OWNER:76)와 축자 대응(**U11** — L-U 11). composition 의 중복 검사를 제거해 소유자 단독 소유를 회복한다 — 계약(rule=null)으로도 안 낸다. **U11 검증 의무**: 적용 커밋에서 «이 사건 모양(`composition/` 여덟째 폴더)을 layer-skeleton 이 #81 로 실제 발화»함을 픽스처로 실증한 뒤에만 제거 — 발화 안 하면 소유자 쪽 보강이 선행 |
| V3 | `composition_root/ 부재 — application 로직…을 가진 BC는 DI 조립을 BC 루트 폴더 composition_root/…가 소유한다` | CR:668–682 | **#488 사건 — composition 방출 억제(소유자 layer-skeleton 단독)** | 고정 이름 칸 부재는 «부모가 있으면 고정 이름 칸이 반드시 존재한다»(#488 — SPEC:814 · OWNER:411)의 사건(**U11**). 제거 조건 동일 — **U11 검증 의무**(layer-skeleton 의 #488 실발화 픽스처 실증 후 제거) |

### 3.3 이중 방출 — §5 로 이관

v1 의 «(rule, where) 단위 레코드 dedupe 또는 EXPECTED 이중 계수 명시» 양자 택일은 **폐기**(U13 — code
locator 는 `rel:lineno`(CR:1314 조립)·tree #107 은 `rel` 뿐이라 키 불성립). composition 은 code·DI·tree
세 레인을 한 실행에서 전부 인쇄하므로(CR:1934–2005 — tree 선점 없음) 이중 #N 이 실재한다 — 처분은
§5 overlap 표(#107·#108·#109·#440)가 소유한다. 침묵 이중 계수 금지(P#1)는 유지.

---

## 4. 유지 확인란 — 현행 처분이 옳은 검사기 (v1 무변)

| 검사기 | 현행 처분 | 확인 근거 |
|---|---|---|
| `check-response-schema-bypass.py` | `ContractFindings("선행 계약(08-04 API-error)")` — rule=null | OWNER 소유 행 0건 + `workspace/tools/reverse_coverage.py:50` · OVERLAP:11 «안 겹침» · L-Q.md:21 «반증 실패» · REG:110 |
| 자유 출력 5종 — `check-app-container`·`check-choices-literal-consumption`·`check-idempotency-scope-creep`·`check-ninja-boundary-middleware`·`check-transient-overmapping` | 각 `ContractFindings(계약별 contract_ref)` — rule=null (커밋 95b34d1) | 5종 전부 OWNER 등재 0건(L-P.md:15 반증 실패) · OVERLAP 행별 «안 겹침/걷음» · 인접 #N 차용 오귀속은 adoption-log:105 확정 |
| `check-common-container.py` | `ContractFindings("선행 규약(D38 승격/강등 — 루트 framework/ 배치)")` — rule=null | OVERLAP:17 «보완 — 이중 발화 실측 0» · `workspace/tools/reverse_coverage.py:56` · REG:116 · F0:23(디렉터리 단위 — symbol=null 정당) |

---

## 5. 이중 방출 — incident 선점 억제 설계 (U13·U14·V4 — MED2 결정)

**기본 원칙**: dedupe 는 **message·occurrence 를 보존하는 multiset 이다 — 제거가 아니다**(V4·MED2).
`(rule, where)` 키 dedupe 는 전면 폐기한다 — 레인별 locator 가 애초에 다르고(아래 표), 같은 규칙·위치의
다른 message 를 지우면 실위반을 잃는다. 유일한 제거 형태는 아래 overlap 표에 열거된 조합의 **선점
억제**뿐이다: **정밀 레인(code-profile)이 활성인 대상에서, 그 대상에 대해 겹치는 tree 술어의 방출을
선점 억제한다**(더 정밀한 판정이 이긴다 — 대상 밖·anchor 미활성에서는 tree 단독 그대로). 구현은
`_emit` 즉시 방출이 아니라 두 레인 버퍼링 후 공용 ordered emitter 단계에서 억제를 적용한다(V1 —
판형·순서 골든은 포매터 계약 v2 소유). 억제로 사라지는 stdout 라인·레코드는 전건 «의도 변경
열거표»와 EXPECTED 사유에 등재한다(침묵 이중 계수 금지의 대칭 — 침묵 소거도 금지).

### overlap 표 — 어느 tree 사이트가 어느 code 술어와 겹치는가 (L-U 13·14 좌표)

| 검사기 | 규칙 | tree 사이트(locator) | code 사이트(locator) | 선점 억제 처분 |
|---|---|---|---|---|
| CR | #107 | CR:1796–1801 (`rel` — 파일 단위) | 행2·3·4 (`rel:lineno` — CR:1314 조립) | code-profile 활성 registrar 파일에서 tree #107 억제 |
| CR | #108 | CR:1817–1822 (`rel:lineno`) | 행1 (`rel:lineno`) | 동일 대상에서 tree #108 억제 |
| CR | #109 | CR:1809 (`rel:lineno`) | 행5ⓐ·행6ⓐ | 동일 대상에서 tree #109 억제 |
| CR | #440 | CR:1882–1886 (import 후 미호출) | 행8·9·행10ⓐ·행6ⓒ | code-profile 활성 URLconf 에서 tree #440 억제 |
| CR | #437 (관찰) | CR:1844–1858 (api.py 닫힌 목록) | 행6ⓑ (decorator@api.py) | 잠재 겹침 — 적용 커밋에서 픽스처 실측 후 같은 처분 적용 여부 확정(자인 약점 차순위) |
| API | #62 | API:6733–6736 (`rel:handler행`) | 행4·5 (handler 행) | code-profile 활성 controller 에서 tree #62 억제 |
| API | #474 | API:6737–6743 (**Name 참조 행** — 도메인 import 이름 ∧ Load) | 행7ⓐ (**handler 행** — API:3277) | locator 가 사건의 다른 좌표를 가리켜도 같은 incident — code 활성 대상에서 tree #474 억제 |
| API | #125 | API:6719 (**ⓓ info** 채널) | 행3·6 (violation) | code #125 확정 발화 대상 handler 에서 tree ⓓ#125 후보 억제(확정이 후보를 이긴다 — 자인 약점 1) |
| EC | #114 | EC:4519 (부재 — 대상: api/ 존재 BC 한정 EC:4511) | B1ⓐ (대상: config error_bcs) | 두 대상 집합의 교집합 BC 에서 tree #114 억제 |
| EC | #572 | EC:4574–4587 (**파일** locator) | 행30ⓐ·33·35~38·40 (**class/field 행** — EC:1959) | code-profile 활성 BC 에서 tree #572 억제 |
| EC | #636 | EC:4588–4596 (파일 locator) | 행32 (class 행) | 동일 대상에서 tree #636 억제 |
| OA | #63 (앵커 레인) | OA:3364(openapi_extra)·3358(override/monkeypatch) | code/repo — OA:2667·2905·2950 | `--anchor` 실행은 tree 뒤 return 없이 code 레인 지속(OA:3398·3406 — U14 실측: «다른 검사기엔 같은 축이 없다»는 v1 전제 반증) — code 레인 활성 operation 에서 tree #63 억제 |

선점 실현 조건 참고: API·EC 는 anchor 미지정 시 tree 위반이 code 레인 전에 exit 2 선점하므로
(API:6848–6850 · EC:4634–4635) 이중 방출은 `--anchor` 모드·대상 집합 차이에서만 실현된다(v1 실측 유지).
CR·OA 는 한 실행에서 양 레인이 함께 인쇄되므로 상시 실현된다.

---

## 부록 A. 필드·판형 정정 명세 (중재 채택분)

### A-1. symbol — 전건 null 처분 폐기 → `symbol` 필드 신설·확정 재료 채움 (U17·V10)

스키마 정의: symbol = «위반 심볼 이름(검사기가 아는 경우에만)»(F0:23). v1 의 «4종 전건 `symbol=None` +
재료 추가는 별도 개선» 처분은 **폐기** — 중재는 «아는 경우만 symbol·모르면 null»의 적극 실현을 이번
변경으로 채택했다(MED:24 · MED2 U17). 4종 Finding dataclass 에 `symbol: str | None = None` 필드를
추가하고 생성 지점이 확정 재료를 채운다.

**node 종별 채움 규칙**: `FunctionDef`/`AsyncFunctionDef`/`ClassDef` → `.name` ·
`AnnAssign`(target 이 `Name`) → `target.id` · OA `Operation` → `function.name` ·
`Call`/`Module`/`Assign` 등 안정 심볼이 없는 node → **null**. 심볼 유/무 픽스처를 각각 고정한다(V10).

| 검사기 | 확정 재료(실측 좌표 — L-U 17·V10) | 방출부 정정 |
|---|---|---|
| API | helper finding 이 이름 가진 `function.node` 를 직접 넘긴다(API:4302) — `_append_finding` 은 AST node 수취(API:2145) | API:6886(#59 레인)·6893(계약 레인): `symbol=finding.category` → `symbol=finding.symbol`(채워진 값 또는 null). msg `f"{category}: {shown}"`(API:6879) 무변 |
| EC | `ClassDef`(EC:3153)·field node(EC:3260) 등 보유 | EC:4687: `symbol=finding.symbol`. msg(EC:4686) 무변 |
| CR | 공개 `FunctionDef`(CR:1395) 등 보유 — `_append_finding` AST node 수취(CR:1307) | CR:1943: `symbol=finding.symbol`. msg(CR:1942) 무변 |
| OA | `Operation.function.name` 보유 — identity 에도 이름 포함(OA:164·2617) | OA:3294: `symbol=finding.symbol`. **msg 재확정(V8 — v1 의 «stdout 무변» 주장 폐기)**: `msg=f"{finding.category}: {finding.detail}"` 로 확정 — 공용 포매터 이행 후 라인은 `[{rule}] {where}: {msg}` 판형이라 stdout 에 category 가 **신설**된다. 이 문면 변경은 «의도 변경 열거표»(포매터 계약 v2)와 baseline/backstop/drift 갱신 사유에 등재 |

### A-2. error-central blocker 실경로·구조화 (P#9+Q#4 채택 — 재료는 리뷰 확정 L-U 21)

- 현행: blocker 는 `list[str]`(경로가 문면에 «접혀» 들어감) + `where="(code-profile)"` 고정(EC:4680) —
  regen `--filter-file` 침묵 제외(Q#4 실측). 경로 재료는 3패턴 전건 보유 — EC:674 f-string `{path}`,
  EC:4373/4375 상수 `COMMON_INIT`/`COMMON_ERROR`(**리뷰 확정 — L-U 21**).
- 정정: blocker 를 **dataclass/enum discriminant 구조**로 바꾼다(V9 — 문자열 prefix 분기 금지):
  `(kind: BC_ERROR|COMMON, relative_path: Path, reason: str)`. 방출은 `where=str(relative_path)`(부재
  파일 — lineno 없음)·`msg=reason`·파일별 1건 분해(P#9). `kind` 가 B1 의 ⓐ#114/ⓑ계약 분기(§2.10)를
  결정한다 — 구조화가 분할의 선행 조건. stdout 라인 순서는 수집 순 보존(V9 — ordered emitter 경유).
  «(code-profile)» 표지는 target 자리에서 폐기(provenance 필드는 T2-2 어댑터 몫 — v1 유지).

### A-3. ⓓ#511 튜플 확정 (U16·V7 — 현행 생성부 실측 2026-08-20)

- **현행 실측**(CR:1779–1784): `question` 변수 자체가 «물음: » 접두를 포함하고
  (CR:1782 — `"물음: 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 \`webhook/<provider>/\` 자리다"`),
  라인은 msg 없는 특수 판형 `  [ⓓ#511] {dir_rel}/ — {question}`(CR:1783), 레코드 message 도 question
  원문(접두 포함)이다. 그대로 공용 `Candidates` 판형(`[ⓓ{rule}] {where}: {msg} — 물음: {q}` —
  F0:153–156)에 넘기면 «물음: 물음:» 중복 또는 빈 msg 콜론 판형이 된다(V7 실측).
- **확정 튜플**:
  - `where` = `f"{dir_rel}/"` (유지 — 디렉터리 사건)
  - `msg` = `"외부 소유 계약 입구 후보(provider 성 디렉터리)"` (**신규 저작**)
  - `question` = `"이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 \`webhook/<provider>/\` 자리다"`
    (**«물음: » 접두 제거**)
  - `symbol` = null (디렉터리 사건 — 심볼 없음)
- **예상 골든**(공용 판형 적용 후 — 호출부 2-space 인쇄):
  - stdout: `  [ⓓ#511] <bc>/<driving>/api/<dir>/: 외부 소유 계약 입구 후보(provider 성 디렉터리) — 물음: 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 \`webhook/<provider>/\` 자리다`
  - record: `{rule:"#511", sentinel:null, contract_ref:null, file:"<dir_rel>/", symbol:null, severity:"info", message:"외부 소유 계약 입구 후보(provider 성 디렉터리) — 물음: 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 \`webhook/<provider>/\` 자리다"}`
  - 구→신 stdout diff: `…/ — 물음: …` → `…/: {msg} — 물음: …`(콜론+msg 신설 · record message 의
    «물음: » 접두 소멸) — «의도 변경 열거표» 등재.

### A-4. 행번호 오배치 11곳 — 재배치 (P#7 채택 · **리뷰 확정(L-U 22)**)

콜사이트 전수(리뷰가 11곳 전건 확정 — 이 외 같은 `msg=":N …"` 패턴 없음):
`check-synthetic-infra-exc.py` **193**(«합성» 센티널)·**195**(#129) · `check-public-surface-annotation.py`
**150·153·156·158**(#493)·**208**(#493)·**268**(#493)·**295**(#358)·**310·322**(#69 — Candidates·info).
제외: public-surface 303(#456)은 행번호 재료 없음(클래스 단위 — 대상 외).

정정: 각 지점을 `where=f"{rel}:{lineno}"`·msg=행번호 뗀 사유로 재배치. v1 의 «SliceFindings(line=…)
경유로 stdout byte 보존» 경로는 **폐기** — U15(전 표면 line 인자 제거·라인은 레코드 필드의 순수
함수)와 V3(대체 불변식)에 따라 공용 포매터가 라인을 생성하고, 문면 변경분은 «의도 변경 열거표»로
통제한다(판형 정본은 포매터 계약 v2 소유 — «합성» 센티널 격리는 F0:100–102 유지).

### A-5. #74 대상-0 가드 21지점 — 공용 helper (P#5 채택 · **리뷰 확정(L-U 23)**)

- 결함(v1 유지): 21개 검사기의 대상-0 가드가 print 후 공용 모듈보다 앞에서 `return 2` — 레코드 0건.
  `#74` 소유자는 `workspace/tools/checker_lint.py`(OWNER:69)라 target 검사기의 #74 레코드는 오귀속
  (MED P#5 — «#74 부여는 하지 않는다»). 21지점 전수 목록은 리뷰가 확정했다(**L-U 23** — registry 27종
  대비 직접 print+return 2 20종 + multiline 인 response-schema 1종·전부 findings import 보유):

| 검사기:행 | 검사기:행 | 검사기:행 |
|---|---|---|
| check-api-error-controller-contract.py:6833 | check-mechanism-ownership.py:315 | check-response-schema-bypass.py:997–1001 |
| check-context-isolation.py:913 | check-missable-entrance.py:402 | check-synthetic-infra-exc.py:178 |
| check-db-table.py:544 | check-naming.py:500 | check-test-config.py:436 |
| check-domain-model.py:823 | check-ninja-boundary-middleware.py:155 | check-transaction-boundary.py:503–504 ※문면 상이 |
| check-error-centralization.py:4623 | check-openapi-error-declaration.py:3392 | check-transient-overmapping.py:192 |
| check-event-publish.py:586 | check-port-adapter-pairing.py:825 | check-usecase-dto-placement.py:642 |
| check-idempotency-scope-creep.py:218 | check-public-surface-annotation.py:349 | check-layer-skeleton.py:319 |

- 설계 개정(U15 정합 — v1 의 `line` 인자 시그니처 폐기): `findings.py` 공용 helper
  `guard_zero_targets(where, msg, checker=None) -> int` — guard 판형은 **msg 원문**(U15: «guard=msg
  원문»)이라 기존 stdout 문면을 msg 로 그대로 이관하면 byte 무변. 레코드는 `rule=null + sentinel="대상0"`
  ·severity="violation"(exit 2 산입 정합) 1건. #74 는 달지 않는다(owner=checker_lint — rule-owner-map:69).
  호출부 치환: `print(<문면>)`+`return 2` → `return guard_zero_targets(where=<target 상대 경로 또는 ".">,
  msg=<기존 문면 그대로>)`. 대안 기각(v1 유지): «measurement-failure contract»는 contract_ref 의미
  오용 — 센티널 선례(«분석·합성·바인딩») 동형 채택.

### A-6. 배포 코드 주석 규율 (V26 채택)

배포 검사기(`dddjango/scripts/*`) 주석·docstring 에는 **로컬 절대 경로를 쓰지 않는다** — `workspace/`
는 개발 산출물로 설치 플러그인에 포함되지 않고 `/Users/…` 는 다른 clone 에서 무효다. 허용 표기는
안정적인 `#N` · 정본 문서명(예: «tree-revision-spec» · «rule-owner-map») · 규칙 문면 요약까지다.
상세 행 인용·중재 provenance 는 이 매핑표(workspace)가 소유하고, 필요 시 저장소 상대경로만 쓴다.
특히 API:34–39 의 «나머지 18 category 는 #N 대응 근거가 없어(실측)» 주석(L-P #2 가 거짓 실증)은
이 문서명 포인터로 교체하되 절대 경로 없이 교체한다.

---

## 부록 B. 계수 골든 영향 — rule 분포 이동 예상·신규 픽스처 레인 (U18·V16 재작성)

전제: 현행 EXPECTED 4행(api-error:52 · error-central:62 · composition:58 · openapi:70)은 red 픽스처가
tree-slice 레인만 발화시키므로 귀속 변경 «단독»으로 즉시 바뀌는 행은 없을 수 있다(v1 실측 유지).
변화는 **레인 단위 픽스처 신설 + (script,lane) 키 공간 확장**(V16 — 현행 `_LANE` 는 script 당 단일
pair, `workspace/tools/findings_count_matrix.py:40`)과 함께 온다. 수치는 적용 후 실측 — 아래는 방향과
사유의 사전 등재다(«의도 변경 열거표»·EXPECTED 갱신 사유와 1:1).

### B-1. 검사기별 rule 분포 이동 예상 (contract→#N · 억제로 인한 감소 포함)

| 검사기 | 이동 방향 |
|---|---|
| check-api-error-controller-contract.py | code 레인 contract:선행(08-04)×k → **#125×2(행3·6) · #62×2(행4·5) · #126×3+분할분(행15~17 + 행19ⓐ·20ⓐ) · #474×1(행7ⓐ)** 이동 · #59 는 유지 2 + 신규 계상(Q#6 — 현행 기대값에 #59 부재). 계약 잔존 = 분할 후 11 원자 술어. tree 억제(§5 — #62·#474·ⓓ#125)로 anchor 모드 tree 계수 **감소** |
| check-error-centralization.py | contract×k → **#572×7(행30ⓐ·33·35~38·40 — 행17ⓑ·23ⓐ 는 기존 #572 finding 단독이라 신규 방출 없음) · #636×1(행32) · #114(B1ⓐ — blocker 구조화 후)** 이동. **감소 4축**: #117 사건 4건(행23ⓑ·24ⓐ·30ⓑ·31)의 EC 방출 억제 + 자기 중복 2건(행17ⓑ·23ⓐ) 제거 + tree 억제(#114·#572·#636 — §5) + blocker 구조화(A-2)로 집계 1건 → 파일별 n건 재편 |
| check-composition-root.py | contract×k → **#107×3 · #108×1 · #109×2(행5ⓐ·6ⓐ) · #437×1(행6ⓑ) · #111×1 · #440×4(행8·9·10ⓐ·6ⓒ) · #497×1(V1)** 이동. **감소 2축**: V2·V3 방출 억제(#81/#488 — U11 실증 후 제거) + tree 억제(#107·#108·#109·#440 — §5, 상시 실현 검사기라 계수 직결). 계약 잔존 = 행5ⓑ·6ⓓ·10ⓑ 3 원자 술어 |
| check-openapi-error-declaration.py | 귀속 무변(이미 #63). 변동 2축: A-1 msg 재확정(category 신설 — stdout·record 문면 변경, 계수 무변)·앵커 레인 tree #63 억제(§5 — anchor 실행 계수 감소). violation_id→multiset fingerprint 정명(V17 — canonical tuple·직렬화는 포매터 계약 v2 소유) 겹치면 sha 전면 재계산 — 귀속과 독립 사유라 커밋 분리(v1 유지) |
| 대상-0 가드 21종(A-5) | 신규 레인 골든(exit 2·레코드 1·sentinel:대상0×1) 추가 — 현행 EXPECTED 에 없음 |
| 행번호 재배치 2종(A-4) | 계수 무변·where 문자열 변경 → fingerprint 재계산 사유 등재 |

### B-2. 신규 필요 픽스처 레인 — 위험 레인 4종 (MED:29 지정 · V16)

`(script, lane)` 키로 각 레인의 픽스처 경로·profile argv·기대 stdout/record/**rule 분포**를 EXPECTED 에
고정한다(신규 레인은 red 로 먼저 — V25 순서 ①). 분할 category 는 분할 양쪽 픽스처를 각 1건 이상 둔다
(U1: domain/application 각 1건 · U6: 0회/2회 각 1건).

| # | (script, lane) | 발화 목표 | 최소 픽스처 내용 |
|---|---|---|---|
| 1 | (api-error, **code-#59**) | `custom Ninja exception_handler` 계열이 code-profile 에서 #59 로 방출 | config 지정 controller + `api.exception_handler` decorator/`add_exception_handler` call — tree 무위반 상태로 code 레인 단독 발화 |
| 2 | (composition, **단일 composition_root.py**) | V1 → #497 방출(DI 레인) | `composition_root.py` 단일 파일 + application 로직 보유 BC(L-Q #1 픽스처 계승) — 폴더 부재라 tree 가 못 닿는 사건 |
| 3 | (openapi, **직접 선언 누락**) | 직접 선언 누락 사건의 code/repo 레인 #63 방출 | operation 이 오류 응답을 열되 `openapi_extra` 직접 선언 부재 — 앵커 레인 억제(§5) 검증 겸용 |
| 4 | (error-central, **code**) | base 좁힘 위반 → #572 code 레인 방출 | tree 4종 green 인 `bc_error_schema.py` + base 좁힘 위반(행36/38/40 축) — tree 선점(exit 2) 없이 code 레인 도달 |

부가 레인(채택분 착지 — 검증 계획 v2 와 공유): 대상-0 가드 레인(A-5) · U11 실증 레인(layer-skeleton 이
V2/V3 사건 모양을 #81/#488 로 발화 — 억제 제거의 선행 조건) · #117 실증 레인(context-isolation 이
행23ⓑ/24ⓐ/30ⓑ/31 사건 모양을 발화) · git 3레인·(exit,parsed_raw,normalized_unique,unparsed,synthetic)
확장 등 L-V 11~20 채택분은 검증 계획 문서(포매터 계약 v2) 소유 — 본 표는 rule 분포 열만 공급한다.

---

## 통계 (분할 후 원자 술어 기준 — U18 재산출)

계수 단위는 category 행이 아니라 **분할 후 원자 술어**다. 혼합 행(API7·19·20 · EC17·23·24·30 · B1 ·
CR5·6·10)은 술어 단위로 나눠 배타 계상했다.

| 구분 | 원자 술어 수 | 내역 |
|---|---|---|
| 전수 판정 대상 | **106** | api-error 23(20 category+분할 3) + error-central 65(55 category+blocker 3+분할 7) + composition 18(10 category+DI 3+분할 5) |
| **#N 귀속** | **36** | api-error 12(#125×2 · #62×2 · #126×5 · #474×1 · #59×2) + error-central 11(#572×9¹ · #636×1 · #114×1 · ¹그중 행17ⓑ·23ⓐ 2건은 기존 #572 finding 단독 방출로 자기 중복 제거 — 신규 방출 없음) + composition 13(#107×3 · #108×1 · #109×2 · #437×1 · #111×1 · #440×4 · #497×1) |
| **계약 유지** | **64** | api-error 11(행1·2·8~12·18 + 행7ⓑ·19ⓑ·20ⓑ) + error-central 50(공통 8 + 클래스 본문 13+행17ⓐⓒ 2 + 잉여물 기타 2 + enum 5 + 행34 + 좁힘 군 3(행39·41·42) + concrete 9 + raw 4 + blocker 3(B1ⓑ·B2·B3)) + composition 3(행5ⓑ·6ⓓ·10ⓑ) |
| **타 소유자 이관(방출 억제 — 소유자 단독)** | **6** | error-central 4 — #117=context-isolation(행23ⓑ·24ⓐ·30ⓑ·31) + composition 2 — #81·#488=layer-skeleton(V2·V3). 전건 U11 검증 의무(소유자 실발화 픽스처 실증 후 제거) 부가 |
| 불확실 표기 | **0** | v1 의 15행 전건 소멸(U12 최종 장부) — 판정 변경 10행 · 판정값 무변 확정 5행(API18 · EC34·39·41 · B1) |

v1 대비: 판정 대상 91행 → 원자 술어 106 · #N 26 → 36 · 계약 65 → 64 · 억제(신설 분류) 0 → 6 ·
불확실 15 → 0. v1 행 기준 판정 변경 18행 = 분할 6(API7·19·20 · CR5·6·10) + EC 주체/사건 분할 4(행17·
23·24·30) + 승격 4(API3·6=#125 · EC32=#636 · EC33=#572) + 강등 1(EC42 #572→계약) + 억제 이관 3(EC31 ·
V2 · V3).
