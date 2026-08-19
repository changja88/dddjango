# T2-1 보강 — category→규칙 귀속 매핑표 (설계 정본)

> **지위**: T2-1 적대 검증 중재([MEDIATION.md](2026-08-19-ontology-t2-1-adversarial/MEDIATION.md) — P#2·3·4+Q#1 «채택(가장 무거운 발견)»)가 명령한 처분 —
> «category→rule 매핑표를 검사기별로 저작해 해당 category를 `SliceFindings(rule)`로 승격. 매핑 근거는
> 규칙 문면(tree-revision-spec)+owner-map 행을 전건 인용. 진짜 계약 전용 category만 `ContractFindings` 존치» — 의 **적용 전 설계 정본**이다.
> 코드 수정 전에 적대 리뷰 2레인을 받는다. 2026-08-19 중재의 이행분 · 작성 2026-08-20.
>
> **판정 기준**(리뷰가 세운 것 — L-Q #1·MEDIATION 표): «규칙 ID가 tree-slice에 등장하는가»가 아니라
> **«이 category가 잡는 사건이 어느 규칙 문면의 술어에 포함되는가»**다. ID 존재와 술어의 전 사건 커버리지를
> 혼동한 것이 원 결함의 뿌리다([L-Q.md](2026-08-19-ontology-t2-1-adversarial/L-Q.md):3).
>
> **표면 전제**: 이 표는 category→rule «귀속 판단»만 정한다. 방출 표면(`SliceFindings` 유지 = 동결 개정 5 갈래 가 /
> 공용 포매터 재저작 = 갈래 나)이 어느 쪽으로 결정되든 귀속 자체는 그대로 이월된다 — 판단은 표면 선택과 독립이다.
>
> **적용 시 동반 의무**(중재 문면): ① 매핑 근거를 코드 주석에 전건 인용(특히 [API:34–39](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py)의
> «나머지 18 category 는 #N 대응 근거가 없어(실측)» 주석은 L-P #2가 거짓으로 실증 — 이 문서 포인터로 교체)
> ② 계수 골든 EXPECTED 갱신은 검사기별 사유와 함께(부록 B).

## 출처 핸들

| 핸들 | 실경로 |
|---|---|
| SPEC | `/Users/hyun/Desktop/dddjango/workspace/design/2026-08-08-tree-revision-spec.md` (규칙 문면 정본) |
| OWNER | `/Users/hyun/Desktop/dddjango/workspace/plan/2026-08-11-rule-owner-map.md` (소유 정본) |
| OVERLAP | `/Users/hyun/Desktop/dddjango/workspace/design/2026-08-12-prior-contract-overlap-review.md` (겹침 처분) |
| REG | `/Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md` (registry 레인 선언) |
| API | `/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py` |
| EC | `/Users/hyun/Desktop/dddjango/dddjango/scripts/check-error-centralization.py` |
| CR | `/Users/hyun/Desktop/dddjango/dddjango/scripts/check-composition-root.py` |
| OA | `/Users/hyun/Desktop/dddjango/dddjango/scripts/check-openapi-error-declaration.py` |
| F0 | `/Users/hyun/Desktop/dddjango/dddjango/scripts/findings.py` (findings/0) |
| L-P·L-Q·MED | `workspace/design/2026-08-19-ontology-t2-1-adversarial/{L-P,L-Q,MEDIATION}.md` |

## 저자 판단 요약

1. **포섭이 축자로 확인될 때만 #N**: category가 잡는 «모든» 사건이 규칙 문면의 술어에 들어갈 때만 귀속했다.
   사건의 일부만 포섭되는 category(주체 혼합·과포섭)는 계약 유지로 보수 처분하고 사유를 «불확실» 열에 남겼다.
2. **소유 경계는 owner-map이 이긴다**: 문면상 포섭돼도 소유자가 타 검사기인 규칙(#117=context-isolation ·
   #63=openapi · #81=skeleton 축 · #129=synthetic-infra-exc)은 귀속하지 않았다 — P#1(#393/#395 이중 방출)과 같은
   모양의 오귀속을 새로 만들지 않기 위해서다.
3. **이중 방출은 별도 축**: 같은 검사기의 tree-slice가 이미 같은 사건을 #N으로 방출하는 category는, 문면 포섭이
   명확해도 승격을 보류(계약 유지)하거나 dedupe 조건을 달았다 — 위반 그래프 이중 계수는 P#1이 지목한 실해다.
4. **리뷰 실증분은 그대로 계승**: L-P #2(#62·#126) · L-P #3(#572) · L-P #4(#107/#108/#109/#111/#440) ·
   L-Q #1(#497)이 실측으로 세운 귀속은 문면 재대조 후 전건 채택했다.
5. **수치는 실측이 계획을 이긴다**: category 전수를 코드 AST에서 재추출했다 — api-error 20(정적 18+동적 2) ✓,
   error-centralization **55**(«약 55» 확정: 정적 46+동적 9, 콜사이트 60) + blocker 3패턴, composition **10**
   (과제 문면의 «9»를 정정: 정적 8+동적 2) + DI 3.

## 자인 약점 (가장 자신 없는 판정 3)

1. **§1 행7 `caught exception forwarding forbidden` → #474**: #474 문면의 주어는 «도메인 예외»인데
   managed catch는 자기 BC «응용» 예외도 허용한다(§1 행5 문면). 응용 예외를 전달한 사건이 #474 술어 밖일 수 있다.
   또 tree-slice #474([API:6742](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py))와 부분 겹침(§1.3).
2. **§3 행10 `register_<bc>_api must be called exactly once (actual N)` → #440**: 0회(부재) 사건은 «명시적으로
   부른다» 위반이 명확하나, 2회 이상 사건의 «정확히 한 번»은 #440 문면이 아니라 선행 계약 문면(«선택 API object를 각
   registrar에 정확히 한 번 전달» — [CR:1950–1952](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-composition-root.py))에서 온다. L-P #4의 «URLconf 계열 → #440/#441 축» 지시를 따라 귀속했다.
3. **§2.6의 #572 확장 4종**(행32·33·35·37): 리뷰가 실증한 것은 행30·31 두 category뿐이고, 나머지는 #572의
   08-15 승인 예외 문면(«정확히 좁히면서 … 그 밖의 required/default 의미 변경은 계속 위반» — [SPEC:894](/Users/hyun/Desktop/dddjango/workspace/design/2026-08-08-tree-revision-spec.md))의
   «정확히»·«그 밖의» 절 해석에 의존한다.

(차순위 약점 — §1 행18 model config mutation: #63 «사후 변형» 인접이나 #63 소유자가 OA라 교차 검사기 배제로 계약 유지 처분.)

---

## 1. check-api-error-controller-contract.py — code-profile 20 category

레인 선언: registry #15([REG:122](/Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md)) — 08-04 API-error 선행 계약 레인 + 표준 트리 슬라이스(#120~#132·#474·#62).
현행 처분: `HANDLER_CATEGORIES` 2종만 `SliceFindings("#59")`, 나머지 18종 전부 `ContractFindings(rule=null)`
([API:34–46](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py), 방출부 [API:6875–6894](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py)).

### 1.0 소유 규칙 11종 문면 (SPEC 정본 · OWNER 소유 행)

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

인접(소유 밖 — 귀속 금지 근거): #129 «예외 번역은 알려진 구체 예외의 전수 명시 매핑으로 한다»(SPEC:457)는
**check-synthetic-infra-exc 소유**(OWNER:118·실방출 [synthetic:195]) · #63(SPEC:387)은 **OA 소유**(OWNER:61).

### 1.1 category 실측 — 20종 확정

`_append_finding` 콜사이트 20곳 AST 전수 추출: **정적 문자열 18** + **동적 2**(공유 방출 지점
[API:3087](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py)·[API:3134](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py) —
`_validate_mapping_body(category=…)` 인자를 호출부 [API:3285→3294](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py)·[API:3555→3564](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py)가 지정) = **20**. 과제 문면과 일치.
Finding dataclass([API:198–204]): `path·lineno·category·shown` — **심볼 재료 없음**(부록 A-1).

### 1.2 매핑표

| # | category(코드 문면 그대로) | 생성 지점 | 판정 | 근거(규칙 문면 인용+출처) | 불확실 |
|---|---|---|---|---|---|
| 1 | `managed try cannot have else/finally` | API:3229 | 계약 | 소유 11종 어느 문면에도 try 문 형태(else/finally) 술어가 없다. 인접 검토: #62(SPEC:386)는 catch «타입»만 규정 · #125(SPEC:454)는 ⓓ 후보(광의 «입구 로직»)로 tree-slice가 이미 info 방출([API:6719]) — blocker 승격은 severity 의미 변경. managed-try 형태는 08-04 계약 고유(«narrow one-call try» — REG:122) | |
| 2 | `managed try body must be one root-call statement` | API:3237 | 계약 | 동일 — «one-call try» 형태는 08-04 계약 문면(REG:122)이 소유. #125의 «유스케이스 1회 호출»은 메서드 수준·ⓓ 채널이라 술어·severity 둘 다 다르다 | |
| 3 | `raise inside managed try` | API:3245 | 계약 | raise 배치 술어는 소유 11종 문면에 없음. #474(SPEC:771)는 «as e 이름 참조»만 문다 | |
| 4 | `bare catch forbidden` | API:3251 | **#62** | «except Exception 을 쓰지 않고 … base 단위 catch 로 한정한다»(SPEC:386) — bare `except:`는 catch-all의 극단형으로 «한정» 위반. **L-P #2 실증**(공식 backstop case `controller-bare-catch`가 rule=null로 나감을 실측) · OWNER:60 | 이중 방출 주의 §1.3-a |
| 5 | `catch must be direct own-BC application/domain exception` | API:3263 | **#62** | «폴백을 둘 경우 도메인·응용 base 단위 catch 로 한정한다»(SPEC:386) — 자기 BC 도메인·응용 예외 밖의 catch = «한정» 위반. **L-P #2 실증** · OWNER:60 | |
| 6 | `raise inside managed catch` | API:3274 | 계약 | catch 안 raise 금지 술어는 소유 문면에 없음(#126은 매핑 «위치»만) — 08-04 managed catch 형태 고유 | |
| 7 | `caught exception forwarding forbidden` | API:3278 | **#474** | «`except … as e` 로 묶은 이름을 그 파일 안에서 참조하면 위반이다»(SPEC:771) — 판정 함수 `_caught_exception_forwarded`([API:3191–3208])는 묶인 이름을 «호출 인자로 전달»할 때 발화 = 참조의 부분집합 · OWNER:399 | **자인 약점 1** — 문면 주어는 «도메인 예외»인데 managed catch는 응용 예외도 허용(행5). tree #474([API:6742])와 부분 겹침 §1.3-b |
| 8 | `same call cannot use exception and Result mapping` | API:3585 | 계약 | Result 매핑 채널은 08-04 계약 고유 개념 — 소유 11종 문면에 Result 술어가 없다 | |
| 9 | `orphan/pre-call error mapping is not causally owned by an application call` | API:3597 | 계약 | «호출 인과 소유» 술어는 08-04 고유. 인접 #126(SPEC:455)은 매핑의 «장소»(컨트롤러 안 vs helper)만 문다 — 이 사건은 컨트롤러 «안»에서 난다 | |
| 10 | `Result/error mapping must immediately follow its try-free call assignment` | API:3610 | 계약 | 인접 배치(immediately follow) 술어는 08-04 고유 | |
| 11 | `FrameworkErrorSchema construction is not owned by an approved catch/Result arm` | API:3633 | 계약 | 승인 arm 밖 «생성» — 컨트롤러 안 사건이라 #126의 «옮기지 않는다» 밖. arm 소유 개념은 08-04 고유 | |
| 12 | `error Status mapping is not owned by an approved catch/Result arm` | API:3645 | 계약 | 행11과 동일 논거 | |
| 13 | `custom Ninja exception_handler forbidden` | API:4006 | **#59 (현행 유지)** | «전역 예외 핸들러 … 로 오류를 가로채지 않는다»(SPEC:385) · OWNER:59. **L-P #59 집중 검증 «반증 실패»**(L-P.md:13) — decorator 형은 tree #126([API:6707])·framework 인스턴스 call 형은 code #59로 분리 실측 | |
| 14 | `custom Ninja add_exception_handler forbidden` | API:4014 | **#59 (현행 유지)** | 행13과 동일 | |
| 15 | `prepared FrameworkErrorSchema factory/helper forbidden` | API:4302 | **#126** | «helper·factory·…로 옮기지 않는다»(SPEC:455) — 축자. **L-P #2 실증**(`controller-one-hop-nested-prepared-factory`가 rule=null로 나감) · OWNER:116 | |
| 16 | `FrameworkErrorSchema raw HTTP serializer helper forbidden` | API:4310 | **#126** | «…serializer…로 옮기지 않는다»(SPEC:455) — 축자 · OWNER:116 | |
| 17 | `exception-to-FrameworkErrorSchema mapping helper forbidden` | API:4318 | **#126** | «도메인 예외를 ErrorSchema·상태 코드로 바꾸는 매핑을 … helper…로 옮기지 않는다»(SPEC:455) — 축자(판정 재료도 `has_exception_test ∧ has_error_constructor` [API:4317]) · OWNER:116 | |
| 18 | `FrameworkErrorSchema/model config mutation in controller forbidden` | API:6534 | 계약 | 오류 스키마 model config 런타임 변형([API:4352–4439] — `model_config` dict 변형·setattr·rebuild). 인접 #63 «monkeypatch…사후 변형»(SPEC:387)에 닿으나 **#63 소유자는 OA**(OWNER:61) — 여기서 #63 방출은 P#1 동형 교차 방출. 소유 11종 문면에는 대응 술어 없음 | 차순위 약점 — #63 술어 재획정(OA와의 사건 경계)은 리뷰 재판정 대상 |
| 19 | `managed catch must directly construct FrameworkErrorSchema and return Status` | 동적 — API:3294 지정·3087/3134 방출 | 계약 | 사건의 일부(helper 위임)는 #126 «직접 쓴다» 위반이나, 같은 category가 형태 위반(본문 2문 미만·비정형 구성·비직접 반환 [API:3084–3141])도 함께 잡는다 — category 단위 #126 귀속은 과포섭 | **불확실** — 위임/형태 사건을 콜사이트 분리하면 위임분은 #126 승격 가능(리뷰 재판정) |
| 20 | `Result arm must directly construct FrameworkErrorSchema and return Status` | 동적 — API:3564 지정·3087/3134 방출 | 계약 | 행19와 동일 구조(같은 방출 지점 공유) | **불확실** — 행19와 동일 |

### 1.3 이중 방출 주의 (승격 적용 조건)

tree-slice는 **프로필 무관 선행**이고, tree 위반 발견 시 anchor 미지정이면 code-profile 전에 **exit 2 선점**한다
([API:6848–6850]). 따라서 이중 방출은 ① `--anchor` 모드(양 레인 계속) ② 두 레인의 대상 집합 차이(tree=채택 신호 BC의
driving 파일 · code=config 지정 controller)에서만 실현된다. 승격 시 다음 겹침을 처리한다:

- **(a) 행4 vs tree #62**: tree도 bare/`except Exception` catch에 #62를 방출([API:6733–6736]) — 같은 사건·같은
  `where`(rel:handler행) 이중 #62 가능. 처분: 승격과 동시에 (rule, where) 단위 레코드 dedupe 또는 anchor 모드 한정
  중복임을 하네스 단언에 명시.
- **(b) 행7 vs tree #474**: tree는 «도메인 import 이름 ∧ Load 참조»([API:6737–6743]), code는 «호출 인자 전달» —
  교집합(도메인 예외+인자 전달)에서 이중 #474 가능. 처분 동일.
- (c) 행15~17의 #126은 tree #126([API:6707] — decorator 형)과 **사건이 다르다**(helper 정의 형) — 겹침 없음.

### 1.4 #59 현행 유지 확인

`HANDLER_CATEGORIES` 2종([API:41–46])의 `SliceFindings("#59")` 방출([API:6880–6887])은 옳다 — OWNER:59 +
SPEC:385 + L-P «#59 집중 검증 — 반증 실패»(L-P.md:13). 단 `symbol=finding.category` 오입력은 부록 A-1 대상.

---

## 2. check-error-centralization.py — code-profile 55 category + blocker 3패턴

레인 선언: registry #2([REG:109](/Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md)) — common/BC ErrorSchema shape·inventory 계약 + 트리 슬라이스(#114·#568·#572·#636).
현행 처분: code-profile 전건 `ContractFindings(rule=null)`([EC:4677–4688](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-error-centralization.py)) — L-P #3이 #572 폐기를 실증.

### 2.0 소유 규칙 4종 문면

| # | 문면(축자) | SPEC | OWNER |
|---|---|---|---|
| #114 | «driving_layer/api/bc_error_schema.py 는 BC 당 정확히 한 파일이고 **항상 있다** — HTTP 오류를 아직 안 여는 BC 에도 «빈 파일»로 있다.» | 446 | 107 |
| #568 | «이름의 자는 «폴더 안이면 접두, 폴더 밖이면 접미»다 — schema/schema_in.py ↔ api/bc_error_schema.py.» | 890 | 486 |
| #572 | «bc_error_schema.py 에는 응답 본문 클래스 `<Bc>ErrorSchema` 와 오류 코드 `<Bc>ErrorCode` 가 함께 온다 — 코드는 스키마의 code 필드 «타입»이라 떼면 둘이 따로 늘어난다. 〔08-15 승인 예외〕 BC base 가 공통 스키마의 «식별자 field» 하나를 자기 `<Bc>ErrorCode` 로 정확히 좁히면서 공통의 default 를 잃어 required 가 되는 모양은 canon … 그 밖의 required/default 의미 변경은 계속 위반.» | 894 | 490 |
| #636 | «bc_error_schema.py 의 `<Bc>ErrorCode` 는 StrEnum 이다 — Literal·맨 문자열 상수 모음으로 대신하지 않는다.» | 1165 | 549 |

인접(소유 밖): #117 «BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다»(SPEC:447)는 **check-context-isolation
소유**(OWNER:108 — context-isolation red 골든에 #117×1 실재, `findings_count_matrix.py:59`).

tree-slice 실방출(이중 방출 판단 재료): #114 부재 [EC:4519]·2개+ [EC:4545] · #568 [EC:4528·4538] ·
#572 `<Bc>ErrorSchema` 부재 [EC:4576]·`<Bc>ErrorCode` 부재 [EC:4583](비어 있지 않은 파일 한정 — [EC:4570] 빈 파일 skip) ·
#636 [EC:4592](이름 `*ErrorCode` 클래스 전수). tree 위반 시 anchor 미지정이면 code 레인 전 **exit 2 선점**([EC:4634–4635]).

### 2.1 실측 개요

`_append_finding` 콜사이트 60곳 AST 전수 추출 → **중복 제거 category 55종**(정적 46 + 동적 패턴 9) +
blocker 문면 3패턴([EC:674·4373·4375]). 주체(무엇을 스캔하나) 기준 9군으로 나눠 판정한다.
Finding dataclass([EC:238–249]): `relative_path·lineno·category·shown·requires_static_error_shape` — 심볼 재료 없음.

### 2.2 공통 모듈 군 — `framework/ninja/framework_error_schema.py` (8종 · `_analyze_common` EC:2701–2962)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 1 | `exactly one common FrameworkErrorSchema required` | EC:2726 | 계약 | 소유 4종 술어는 전부 BC 쪽 `bc_error_schema.py`가 주어다(SPEC:446·890·894·1165). 공통 모듈의 형태는 08-04 계약 고유(«common FrameworkErrorSchema는 … exact wire shape의 단일 기반» — 방출부 근거문 [EC:4699]) | |
| 2 | `common FrameworkErrorSchema must directly inherit ninja.Schema` | EC:2731→2740 (`_base_contract` 경유·방출 EC:1992/2001) | 계약 | 동일 — 공통 모듈 술어는 소유 밖 | |
| 3 | `common FrameworkErrorSchema direct mutation/side effect forbidden` | EC:2763 | 계약 | 동일 | |
| 4 | `common module Enum/public/derived class forbidden` | EC:2905 | 계약 | 동일 | |
| 5 | `common module helper/function forbidden` | EC:2913 | 계약 | 동일 | |
| 6 | `common module functional Enum forbidden` | EC:2917 | 계약 | 동일 | |
| 7 | `common module public artifact forbidden` | EC:2930 | 계약 | 동일 | |
| 8 | `common module helper/mutation/side effect forbidden` | EC:2936·2955 | 계약 | 동일 | |

### 2.3 클래스 본문 공용 군 — 주체 3종 혼합 (14종 · `_class_member_findings` EC:2186–2410)

한 콜사이트 집합이 **공통 클래스([EC:2841] · allow 플래그 True)·BC base([EC:3387])·concrete([EC:3556])** 세 주체에
같은 category 문자열로 발화한다. BC base에서 난 사건 일부는 #572 승인 예외 절(«그 밖의 … 의미 변경은 계속 위반»)에
인접하지만, 같은 category가 공통·concrete 사건도 담으므로 **category 단위 #N 부여는 과포섭**이다 — 전 14종 계약 유지.
(적용 단계에서 주체별 category 분할(문자열 분리)을 하면 base분에 한해 #572 재론 가능 — 리뷰 판단에 맡긴다.)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 9 | `class decorator outside common FrameworkErrorSchema` | EC:2226 | 계약 | 위 군 판단(주체 혼합) — #572 문면(SPEC:894)의 술어는 동거·좁힘·required/default뿐 | |
| 10 | `class keyword config outside common FrameworkErrorSchema` | EC:2234 | 계약 | 동일 | |
| 11 | `Pydantic hook override outside common FrameworkErrorSchema` | EC:2248·2325 | 계약 | 동일 | |
| 12 | `model_config override outside common FrameworkErrorSchema` | EC:2258·2334 | 계약 | 동일 | |
| 13 | `dynamic ClassVar assignment outside common FrameworkErrorSchema` | EC:2276 | 계약 | 동일 | |
| 14 | `schema decorator proxy outside common FrameworkErrorSchema` | EC:2289·2347 | 계약 | 동일 | |
| 15 | `dynamic private class assignment outside common FrameworkErrorSchema` | EC:2300·2360 | 계약 | 동일 | |
| 16 | `duplicate public field` | EC:2309 | 계약 | 동일(공통 클래스 자기 본문에도 발화 가능 — allowed_fields 산식) | |
| 17 | `additional public field` | EC:2312 | 계약 | 동일. base 사건(허용 field={식별자} [EC:3391])은 #572 «하나를 정확히» 축에 인접하나 같은 사건을 행31이 이미 #572로 잡는다(len(fields)!=1 [EC:3232]) — 여기서 중복 부여하지 않는다 | |
| 18 | `complex class assignment outside common FrameworkErrorSchema` | EC:2316 | 계약 | 군 판단 | |
| 19 | `public class assignment/helper` | EC:2342 | 계약 | 동일 | |
| 20 | `validator/public helper` | EC:2379 | 계약 | 동일 | |
| 21 | `public nested class/helper` | EC:2385 | 계약 | 동일 | |
| 22 | `executable class-body statement outside common FrameworkErrorSchema` | EC:2404 | 계약 | 동일 | |

### 2.4 BC error 모듈 잉여물 군 (2종 · `_bc_module_artifact_findings` EC:2431–2481)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 23 | `BC error module extra class/helper forbidden` | EC:2445 | 계약 | #572 문면 «…가 함께 온다»(SPEC:894)는 동거 «필수»를 정하나 **닫힌 목록임을 명시하지 않는다**(#437 «닫힌 허용 목록» SPEC:754와 대조·#85 «…만 온다 — 둘뿐» SPEC:414와 대조). 잉여물 금지는 08-04 계약의 declarative-module 술어 | **불확실** — «온다» 열거를 닫힌 것으로 읽으면 #572 포섭. 보수 처분·리뷰 재판정 |
| 24 | `BC error module helper/mutation/side effect forbidden` | EC:2475 | 계약 | 행23과 동일 | **불확실** — 동일 |

### 2.5 ErrorCode enum 내부 군 (5종 · `_enum_members` EC:3021–3099 — 주체는 BC `<Bc>ErrorCode` 본문)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 25 | `Enum public helper forbidden` | EC:3059·3063 | 계약 | #636(SPEC:1165)은 컨테이너 «타입»(StrEnum)만 규정 — 멤버·헬퍼 술어 없음. wire-code 규약은 08-04 고유(«project-wide unique wire code» [EC:4700]) | |
| 26 | `duplicate Enum member` | EC:3074 | 계약 | 동일 | |
| 27 | `wire code must be snake_case` | EC:3090 | 계약 | 동일 — 소유 4종에 wire 표기 술어 없음 | |
| 28 | `ErrorCode requires a wire-code member` | EC:3092 | 계약 | 동일 | |
| 29 | `duplicate wire code in Enum: {value}` (동적) | EC:3098 | 계약 | 동일 | |

### 2.6 BC 컨테이너 존재·유일 군 (5종 · `_analyze_bc_module` EC:3102–3219)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 30 | `exactly one <Bc>ErrorCode required` (동적 — EC:3132 산식) | EC:3142 | 계약 | 부재 사건은 #572 «함께 온다» 포섭이나 **tree-slice가 같은 사건을 이미 #572로 방출**([EC:4581–4587]). 잔여 사건(빈 파일·config 지정 BC)의 «이 BC 는 오류를 연다»는 전제는 선행 계약(config error_bcs)이 정한다 — #114·#572 문면은 빈 파일을 canon으로 인정(SPEC:446) | **불확실** — tree/code 대상 집합 차이(채택 신호 BC×api/ 존재 vs config error_bcs) 실측 후, 비겹침분 한정 #572 승격 재론 |
| 31 | `second ErrorCode/StrEnum container` | EC:3153·3158 | 계약 | 술어는 #117(SPEC:447)과 축자 일치하나 **#117 소유자는 check-context-isolation**(OWNER:108) — 여기서 #117 방출은 P#1(#393/#395) 동형 이중 계수. 소유 4종 문면에는 «두 번째 컨테이너» 술어 없음 | **불확실** — 소유 경계 자체의 재조정(#117 사건 분할)은 별도 트랙(MED 범위 밖 등재 P#1 참조) |
| 32 | `{enum_name} must directly inherit enum.StrEnum` (동적 — `<Bc>ErrorCode …`) | EC:3171→3180 (방출 EC:1992/2001) | 계약 | 사건은 #636(SPEC:1165) 축자 포섭이나 **tree-slice #636([EC:4588–4596])이 같은 사건을 이미 방출**(`*ErrorCode` 전수×StrEnum base 검사) — 승격 시 같은 실행(anchor 모드)·같은 파일 이중 #636 | **불확실** — 겹침 해소(한쪽 제거 또는 dedupe)와 동시에만 #636 승격 |
| 33 | `exactly one {base_name} required` (동적 — `<Bc>ErrorSchema …`) | EC:3187 | 계약 | 부재 사건이 tree-slice #572([EC:4574–4580])와 겹침 — 행30과 동일 구조 | **불확실** — 행30과 동일 |
| 34 | `{base_name} must directly inherit common FrameworkErrorSchema` (동적) | EC:3210→3219 | 계약 | #572 승인 예외 절의 «공통 스키마의 식별자 field 를 좁힌다»가 공통 상속을 «전제»하나 명시 술어는 아니다 — 전제 위반의 포섭은 해석 의존 | **불확실** — 리뷰 재판정(전제 포섭 인정 시 #572) |

### 2.7 BC base 좁힘 군 (8종 · EC:3220–3395) — #572 승격의 본체

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 35 | `second BC FrameworkErrorSchema base` | EC:3198 | **#572** | «응답 본문 클래스 `<Bc>ErrorSchema` 와 … 가 함께 온다»(SPEC:894 — 단수 동거)의 위반(공통 직상속 두 번째 base [EC:3196–3198]). **L-P #3 수정 제안이 축자 지목**(«'second BC FrameworkErrorSchema base' 등 #572 문면에 포함되는 판정은 SliceFindings("#572")로») · OWNER:490. tree-slice 겹침 없음(tree는 존재만 검사) | |
| 36 | `BC FrameworkErrorSchema base must narrow exactly one common field to own ErrorCode` | EC:3233 | **#572** | 08-15 승인 예외 문면 «BC base 가 공통 스키마의 «식별자 field» **하나**를 자기 `<Bc>ErrorCode` 로 **정확히** 좁히면서…»(SPEC:894). **L-P #3 실증**(두 번째 field 추가 fixture → stdout 이 category·JSONL rule=null 실측) · MED 채택 | |
| 37 | `BC FrameworkErrorSchema discriminator must override common field` | EC:3260 | **#572** | 같은 절 — 좁힘의 대상은 «공통 스키마의 식별자 field»여야 한다(SPEC:894). 비공통 field 를 discriminator 로 세우면 그 술어 위반 | 자인 약점 3(확장분) |
| 38 | `BC base must preserve common annotation/nullability while narrowing str to own ErrorCode` | EC:3289 | **#572** | «**정확히** 좁히면서 … 그 밖의 … 의미 변경은 계속 위반»(SPEC:894) — 좁힘 외 annotation/nullability 변경은 «그 밖의 의미 변경» | 자인 약점 3 |
| 39 | `BC base field metadata must match common FrameworkErrorSchema` | EC:3303 | 계약 | 문면이 명시한 «그 밖의» 변경은 «required/default 의미»다(SPEC:894) — metadata(alias 등)까지의 확대는 축자 밖 | **불확실** — «정확히 좁히면서»를 넓게 읽으면 #572. 보수 처분 |
| 40 | `BC base must preserve common required/default semantics` | EC:3341 | **#572** | «그 밖의 **required/default 의미 변경**은 계속 위반»(SPEC:894) — 축자 | 자인 약점 3 |
| 41 | `raw string FrameworkErrorSchema discriminator` | EC:3352(base)·3522(concrete) | 계약 | **주체 혼합** — base 사건은 #572 «코드는 스키마의 code 필드 «타입»» 축 위반으로 읽히나, 같은 category 가 concrete 사건(3522)도 담고 concrete 는 소유 문면 밖(§2.8) — category 단위 과포섭 | **불확실** — 콜사이트 분리 시 base분 #572 재론 |
| 42 | `BC base discriminator default must be own ErrorCode member or None` | EC:3379 | **#572** | «자기 `<Bc>ErrorCode` 로 정확히 좁히면서 **공통의 default 를 잃어 required 가 되는 모양은 canon**»(SPEC:894) — default 는 자기 ErrorCode member 또는 상실(→None/required)만 canon | 자인 약점 3 |

### 2.8 concrete 군 (9종 · EC:3397–3556) — 08-04 계약 고유

소유 4종 문면의 주어는 파일·공통 pair·base 좁힘까지다 — **concrete 오류 스키마의 형태 술어는 없다**(#572 승인 예외
절도 주어가 «BC base»다). 전 9종 계약 유지.

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 43 | `{node.name} must directly inherit {base_name}` (동적) | EC:3419→3428 | 계약 | 상단 군 판단 — concrete 상속 술어는 08-04 고유(«direct no-arg concrete/event-specific BC-base ErrorSchema» — REG:122) | |
| 44 | `concrete adds field outside common shape` | EC:3435 | 계약 | 동일 | |
| 45 | `concrete field metadata must match common FrameworkErrorSchema` | EC:3450 | 계약 | 동일 | |
| 46 | `concrete discriminator must preserve common annotation/nullability while using own ErrorCode` | EC:3464→3476 | 계약 | 동일 | |
| 47 | `concrete field annotation/nullability must match common FrameworkErrorSchema` | EC:3474→3476 | 계약 | 동일 | |
| 48 | `concrete field must have a no-arg default: {field_name}` (동적) | EC:3484 | 계약 | 동일(«no-arg source contract» — REG:109) | |
| 49 | `concrete missing required default: {field_name}` (동적) | EC:3499 | 계약 | 동일 | |
| 50 | `concrete discriminator default must use own ErrorCode member` | EC:3540 | 계약 | 동일 | |
| 51 | `concrete discriminator requires own ErrorCode default` | EC:3549 | 계약 | 동일 | |

### 2.9 raw 코드·전 프로젝트 군 (4종 · EC:3765–3946 / 4017–4310 / 4354–4461)

| # | category | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 52 | `raw string discriminator constructor argument` | EC:3913 | 계약 | 사용처(생성 호출 인자) 술어는 소유 4종 문면 밖 — #636은 컨테이너 «정의»의 타입만 문다(SPEC:1165) | |
| 53 | `raw string one-step discriminator assignment` | EC:4079 | 계약 | 동일 | |
| 54 | `concrete FrameworkErrorSchema outside canonical module` | EC:4108 | 계약 | «스키마가 정본 모듈 밖에 산다» 술어는 소유 문면에 없음 — #572는 파일 «안 내용»을, #114는 파일 «존재»를 문다. 인접 #117은 ErrorCode 한정+타 검사기 소유(OWNER:108) | |
| 55 | `duplicate project code wire value: {value}` (동적) | EC:4433 | 계약 | «project-wide unique wire code»는 08-04 계약 문면([EC:4700]) — 소유 4종 술어 밖 | |

### 2.10 blocker 3패턴 (list[str] — 방출 시 file="(code-profile)" [EC:4680])

| # | blocker 문면 | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| B1 | `필수 canonical FrameworkErrorSchema artifact 부재: {path}` | EC:674 (path ∈ {공통 모듈} ∪ {BC별 `_bc_error_path(bc)`} — EC:670–674) | **사건 분할: path가 BC `bc_error_schema.py` → #114 · path가 공통 모듈 → 계약** | «BC 당 정확히 한 파일이고 **항상 있다**»(SPEC:446) — BC 경로 부재는 축자 포섭 · OWNER:107. 공통 모듈 존재 요구는 소유 문면 밖(코드 주석의 #417·#414는 business-vocabulary 소유 — OWNER:352·355) | **불확실(#114 분)** — tree-slice #114([EC:4519])가 같은 부재를 방출(단 api/ 디렉터리 존재 BC 한정 [EC:4511] — 대상 집합 상이). 승격은 겹침 실측·dedupe 와 동시에 |
| B2 | `필수 common artifact 부재: framework/ninja/__init__.py` | EC:4373 | 계약 | 공통 모듈 존재 술어는 소유 4종 밖(B1 논거) | |
| B3 | `필수 common artifact 부재: framework/ninja/framework_error_schema.py` | EC:4375 | 계약 | 동일 | |

blocker 의 file 실경로 복원(P#9·Q#4 채택)은 부록 A-2.

---

## 3. check-composition-root.py — code-profile 10 category + DI 3

레인 선언: registry #16([REG:123](/Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md)). 소유 18종(OWNER:79–105·369–371·420–432).
현행 처분: code 레인([CR:1937–1944])·DI 레인([CR:620–685]) 전부 `ContractFindings(rule=null)`.
**실측 정정**: 과제 문면의 «9 category»는 실측 **10**이다(정적 8 + 동적 2 — `_append_finding` 콜사이트 15곳 AST 전수).
Finding dataclass([CR:143–150]): `relative_path·lineno·category·shown` — 심볼 재료 없음.

### 3.0 관련 소유 규칙 문면

| # | 문면(축자) | SPEC | OWNER |
|---|---|---|---|
| #107 | «api/api_router.py 는 `def register_<bc>_api(api)` 등록 함수 하나만 갖는다.» | 439 | 100 |
| #108 | «api_router.py 는 전역 API 객체를 import 하지 않고 인자로 받는다 — BC 가 프로젝트를 import 하지 않는다.» | 440 | 101 |
| #109 | «등록은 register_<bc>_api(api) 함수 안에서만 하고 module top-level 에서 register_controllers 를 부르지 않는다(부작용 등록 금지).» | 441 | 102 |
| #111 | «api_router.py 가 하는 일은 자기 BC 의 컨트롤러를 import 해 api.register_controllers(...) 를 부르고 경로 접두사·태그를 정하는 것뿐이다.» | 443 | 104 |
| #440 | «`<project>/urls.py` 는 라우터 «등록»만 한다 — 각 BC 의 register_<bc>_api(api) 를 명시적으로 부른다.» | 755 | 370 |
| #441 | «`<project>/urls.py` 는 BC 안의 심볼을 import 해서 쓰지 않는다 — 예외는 #440 의 register_<bc>_api 명시 호출을 위한 그 함수 import 하나뿐이다.» | 756 | 371 |
| #497 | «composition_root/ 는 파일이 아니라 폴더이고 «결선 하나 = 파일 하나»다 — 지금은 dependency_wiring.py 와 event_wiring.py 둘이다.» | 823 | 420 |
| #437 | «`<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다 — … 닫힌 허용 목록…» (인접) | 754 | 369 |
| #84 | «composition_root/ 는 BC 루트에 두고 네 층 폴더 어디에도 두지 않는다.» (인접) | 413 | 79 |

### 3.1 registrar/URLconf 10 category (`_composition_semantics` CR:1557–1611)

| # | category(코드 문면 그대로) | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| 1 | `registrar imports selected project API` | CR:1387 | **#108** | «전역 API 객체를 import 하지 않고 인자로 받는다 — BC 가 프로젝트를 import 하지 않는다»(SPEC:440) — 축자(선택 api 모듈 import 검출 [CR:1376–1387]). **L-P #4 축 확정** · OWNER:101 | |
| 2 | `additional public registrar function` | CR:1398 | **#107** | «등록 함수 **하나만** 갖는다»(SPEC:439) — 공개 함수 추가 = «하나만» 위반 · OWNER:100 | |
| 3 | `exactly one sync {spec.function_name} function required` (동적 — `register_<bc>_api`) | CR:1404 | **#107** | 같은 문면 — 부재·중복·async([CR:1402]) 전부 «def register_<bc>_api(api) … 하나만» 위반 | |
| 4 | `registrar signature must be one required positional parameter` | CR:1430 | **#107** | 문면이 시그니처를 축자로 적는다 — «`def register_<bc>_api(api)`»(SPEC:439). #108 «인자로 받는다»(SPEC:440)와 동근이나 형태 술어의 자리는 #107 (tree 도 arity 를 #107로 낸다 [CR:1799–1801] — 정합) | |
| 5 | `register_controllers outside canonical registrar owner` | CR:1467·1579·1598 | **#109** | «등록은 register_<bc>_api(api) 함수 **안에서만** 하고 module top-level 에서 register_controllers 를 부르지 않는다»(SPEC:441) — api_router 함수 밖([CR:1467])·`<project>/api.py`([CR:1579])·urls.py([CR:1598]) 세 지점 전부 «함수 밖 등록». **L-P #4 실증**(`composition-registrar-rebinds-api-parameter` fixture 가 rule=null 실측) · OWNER:102. 인접: api.py 사건은 #437(SPEC:754)에도 포섭되나 category 는 세 파일 공용이라 공통 술어 #109 로 귀속(#437 은 tree 레인이 이미 소유 [CR:1844–1858]) | |
| 6 | `register_controllers decorator side effect` | CR:1471·1583·1602 | **#109** | «(부작용 등록 금지)»(SPEC:441) — decorator 등록은 부작용 등록의 축자 사례(인접 #431 SPEC:748 도 동문이나 주어가 `# noqa` import 등록) | |
| 7 | `canonical registrar has no direct register_controllers call` | CR:1475 | **#111** | «api_router.py 가 하는 일은 … api.register_controllers(...) 를 **부르고** …뿐이다»(SPEC:443) — 직접 호출 부재는 그 «하는 일»의 불이행. **L-P #4 실증** · OWNER:104 | |
| 8 | `registrar call must be a module-level direct event` | CR:1527 | **#440** | «각 BC 의 register_<bc>_api(api) 를 **명시적으로** 부른다»(SPEC:755) — 조건부·간접 호출([CR:1526])은 명시 호출 위반. **L-P #4 축 확정** · OWNER:370 | |
| 9 | `registrar URLconf call has wrong arity` | CR:1533 | **#440** | 같은 문면 — 호출 형태 «register_<bc>_api(**api**)» 축자(인자 1·키워드/星 금지 [CR:1532]) | |
| 10 | `{spec.function_name} must be called exactly once (actual {count})` (동적) | CR:1548 | **#440** | «**각 BC 의** register_<bc>_api(api) 를 명시적으로 부른다»(SPEC:755) — 0회(부재)는 축자 포섭. L-P #4 «URLconf 계열 → #440/#441 축» 지시 계승 | **자인 약점 2** — 2회 이상 사건의 «정확히 한 번»은 선행 계약 문면([CR:1950–1952]) 소지 |

#441 참고: 이 레인에 #441 대응 category 는 **없다** — urls.py import 술어는 analysis(분석 불능) 채널만 있다
([CR:1507]). #441 은 tree-slice([CR:1877])가 단독 방출 — 매핑표 관할 밖(현행 유지).

### 3.2 DI 레인 V1~V3 (`_filtered_di_findings` CR:620–685 — 현행 `ContractFindings` 직생성)

| # | 사건(코드 문면 요지) | 생성 지점 | 판정 | 근거 | 불확실 |
|---|---|---|---|---|---|
| V1 | `{local} — 단일 파일 composition_root.py 모양은 트리에 없다 — 정본은 BC 루트 «폴더» composition_root/(트리 2행)다` | CR:657–666 (COMPOSITION_FILE="composition_root.py" CR:102) | **#497** | «composition_root/ 는 **파일이 아니라 폴더**이고 «결선 하나 = 파일 하나»다»(SPEC:823) — 축자. **L-Q #1 확정 실측**(`composition_root.py`+application 로직 fixture → exit 2·contract 레코드 2·#497 레코드 0 — tree 는 폴더 부재 시 즉시 반환 [CR:1712–1723]이라 이 사건에 못 닿는다) · OWNER:420 · MED 채택 | |
| V2 | `composition/ 폴더에 배선 코드({파일들}) — DI 조립은 BC 루트 «폴더» composition_root/…가 소유한다` | CR:644–655 (COMPOSITION_DIR="composition" CR:103) | 계약 | off-tree `composition/` 디렉터리 술어는 소유 18종 문면에 없다. 인접: #81 «BC 루트 바로 아래 일곱 가지만 — 여덟째는 없다»(SPEC:410)가 포섭하나 **#81 소유자는 check-layer-skeleton**(skeleton red 골든 #81×1 — `findings_count_matrix.py:65`) — 교차 방출 금지. #84(SPEC:413)는 «네 층 폴더 안 금지»라 주어가 다름 | **불확실** — #81 소유 경계 재론 시 재판정 |
| V3 | `composition_root/ 부재 — application 로직…을 가진 BC는 DI 조립을 BC 루트 폴더 composition_root/…가 소유한다` | CR:668–682 | 계약 | «폴더 부재» 사건은 #497 «파일이 아니라 폴더» 문면 밖(폴더가 있을 때의 내용 규율이 #497 tree 방출 [CR:1724–1734]). 골격 완비(필수 칸 존재) 술어는 skeleton 축(#488 등) — 소유 18종 밖 | **불확실** — L-Q #1 도 «#497 또는 정확한 owner 규칙»으로 열어 둠. 보수 처분·리뷰 재판정 |

### 3.3 이중 방출 주의 — composition 은 선점이 없다

api-error·error-central 과 달리 composition 은 **code·DI·tree 세 레인을 한 실행에서 전부 인쇄**하고 마지막에 exit 를
정한다([CR:1934–2005] — tree 선점 없음). 승격 시 같은 실행 이중 #N 이 실재한다:

- 행5 vs tree #109([CR:1809] — module top-level `register_controllers`/`add_router`): 같은 사건·같은 where 포맷.
- 행2·3·4 vs tree #107([CR:1796–1801] — 함수 수·arity).
- 행1 vs tree #108([CR:1817–1822] — allowlist 밖 import).
- 행10(0회) vs tree #440([CR:1882–1886] — import 후 미호출).

처분: 승격과 동시에 **(rule, where) 단위 레코드 dedupe** 를 넣거나, tree/code 술어 경계(발견 기반 vs config 지정)를
하네스 레인 픽스처로 고정해 이중 계수를 EXPECTED 에 명시적으로 반영한다(부록 B). 어느 쪽인지는 적용 커밋이 정하되
**침묵 이중 계수는 금지**(P#1 이 지목한 실해).

---

## 4. 유지 확인란 — 현행 처분이 옳은 검사기

| 검사기 | 현행 처분 | 확인 근거 |
|---|---|---|
| `check-response-schema-bypass.py` | `ContractFindings("선행 계약(08-04 API-error)")` — rule=null | OWNER 소유 행 0건 + `reverse_coverage.py:50`(PRIOR_CONTRACT_SCRIPTS 고정 — L-P.md:15 «반증 실패») · OVERLAP:11 «**안 겹침** — JSON 성공 응답 형태는 트리 규칙 관할 밖(성공 lane)» · L-Q.md:21 «owner 규칙과 tree-slice 모두 0건 … 반증 실패» · REG:110 «error helper 계약은 registry #15 소유» |
| 자유 출력 5종 — `check-app-container`·`check-choices-literal-consumption`·`check-idempotency-scope-creep`·`check-ninja-boundary-middleware`·`check-transient-overmapping` | 각 `ContractFindings(계약별 contract_ref)` — rule=null (커밋 95b34d1) | 5종 전부 OWNER 등재 0건(L-P.md:15 — 반증 실패·`reverse_coverage.py:51–55` 고정). OVERLAP 행별: app-container:16 «안 겹침(유일 실체)» · choices-literal:14 «안 겹침 — 다른 지식» · idempotency:15 «안 겹침 — 경계 명문화(§13 과 #181 은 다른 층위)» · ninja-boundary:18 «겹침 1건 → #433 쪽 면제로 걷음 — 실체는 이 검사기» · transient-overmapping:12 «안 겹침 — 대응 술어 없음». 인접 #N 차용(#486/#565/#181/#433)이 오귀속임은 adoption-log:105 가 확정 |
| `check-common-container.py` | `ContractFindings("선행 규약(D38 승격/강등 — 루트 framework/ 배치)")` — rule=null | OVERLAP:17 «**보완**(같은 표면·다른 술어) — 실체는 이 검사기·이중 발화 실측 0» · `reverse_coverage.py:56` · REG:116. v0 대표 2종의 하나(F0:23 — 위치 단위가 디렉터리라 symbol=null 도 정당) |

---

## 부록 A. 필드 정정 명세 (중재 채택분 — 이 문서와 함께 리뷰받는다)

### A-1. symbol 오입력 4종 (P#8+Q#4 채택: «category 는 message 로만 · 심볼 아는 경우만 symbol · 모르면 null»)

스키마 정의: symbol = «위반 심볼 이름(검사기가 아는 경우에만)»(F0:23).

| 검사기 | 오입력 지점 | 현행 symbol | dataclass 심볼 재료 실측 | 정정 |
|---|---|---|---|---|
| API | 6886(#59 레인)·6893(계약 레인) | `finding.category` | Finding(path·lineno·category·shown — API:198–204) — **없음** | `symbol=None`. msg 는 이미 `f"{category}: {shown}"`(API:6879)라 category 보존 무변 |
| EC | 4687 | `finding.category` | Finding(relative_path·lineno·category·shown·requires_static_error_shape — EC:238–249) — **없음** | `symbol=None`. msg `f"{category}: {shown}"`(EC:4686) 무변 |
| CR | 1943 | `finding.category` | Finding(relative_path·lineno·category·shown — CR:143–150) — **없음** | `symbol=None`. msg `f"{category} — {shown}"`(CR:1942) 무변 |
| OA | 3294 | `finding.category` (실측값 예 `"openapi-postprocess"`) | Finding(relative_path·lineno·category·detail — OA:180–186) — **없음** | `symbol=None`. **단 OA 는 msg=`finding.detail`(OA:3293)라 category 가 message 에 없다** → `msg=f"{finding.category}: {finding.detail}"` 로 승계(레코드 채널만 변경·stdout 무변) |

4종 모두 생성 지점 다수가 AST 노드(FunctionDef·ClassDef 등)를 쥐고 있어 **재료 추가는 가능**하나, 이 보강의 범위는
«모르면 null»까지다 — dataclass 에 `symbol: str | None` 필드를 새로 채우는 작업은 별도 개선으로 등재(중재 문면
«심볼을 아는 경우만»의 적극 실현).

### A-2. error-central blocker 의 file="(code-profile)" → 실경로 (P#9+Q#4 채택)

- 현행: blocker 는 `list[str]`(문면에 경로가 «접혀» 들어감)이고 방출부가 `where="(code-profile)"` 고정([EC:4680]).
  regen `--filter-file` 부분 일치에서 침묵 제외됨을 Q#4 가 실측.
- 경로 재료 실측: **3패턴 전부 보유** — EC:674 는 f-string 에 `{path}`(Path 객체 — `COMMON_ERROR` 또는
  `_bc_error_path(bc)`), EC:4373/4375 는 상수 `COMMON_INIT`/`COMMON_ERROR`.
- 정정: blocker 를 `(relative_path: Path, reason: str)` 구조(경량 tuple 또는 dataclass)로 바꾸고 방출을
  `where=str(relative_path)`(부재 파일이라 lineno 없음 — 경로만)·`msg=reason` 으로. 집계 1건이 파일별 1건이 되도록
  분해(P#9 «파일·행 단위 레코드로 분해»). stdout 문면(`  - {blocker}`)은 byte 보존 — 라인 조립만 구조에서 복원.
  «(code-profile)» 분류 표지는 target 자리에서 폐기(별도 provenance 필드는 T2-2 어댑터 몫 — Q#4 의 `target_precision`
  제안은 이 보강 범위 밖 등재).
- §2.10 B1 의 사건 분할(#114/계약)은 이 구조화가 선행되어야 실현 가능하다(경로가 문자열에 접혀 있으면 분기 불가).

### A-3. 행번호 재배치 2종 (P#7 채택: where=`rel:lineno` · msg 에서 `:N` 제거)

현행: 두 검사기가 `Findings/Candidates.add(rule, rel, ":N …")` 로 행번호를 msg 선두에 넣어 stdout 이 `경로: :N`,
레코드 file 이 파일까지만이다.

- 콜사이트 전수(실측): `check-synthetic-infra-exc.py` **193**(«합성» 센티널)·**195**(#129) ·
  `check-public-surface-annotation.py` **150·153·156·158**(#493 매개변수/반환)·**208**(#493 첫 대입)·**268**(#493 속성)·
  **295**(#358)·**310·322**(#69 — Candidates·info). L-P #7 이 예시한 150·208·268 외 6곳이 더 있다.
  제외: public-surface **303**(#456)은 행번호 재료 자체가 없다(클래스 단위) — 대상 외.
- 정정: 각 지점을 `where=f"{rel}:{lineno}"`·msg=행번호 뗀 사유로 재배치. **stdout byte 보존이 규율이므로**
  `Findings/Candidates`(모듈이 라인을 조립 — where 변경이 곧 stdout 변경)를 그대로 쓸 수 없다 → L-P #7 대안대로
  `SliceFindings(rule, line=<기존 조립 결과와 동일 문자열>, where=<정상 locator>, msg=<정상 사유>[, severity="info"])`
  경유(«합성» 은 rule 인자 그대로 — F0:100–102 의 sentinel 격리가 rule=null+sentinel 로 변환). 판형 주의: 이는 규약군
  →`SliceFindings` 강등이라 동결 개정 5(E8) 결론에 종속 — 갈래 나(공용 포매터 재저작) 채택 시 이 두 검사기는 stdout
  재저작(기준선 SHA 갱신) 쪽으로 함께 간다.

### A-4. #74 대상-0 가드 21종 — 공용 helper + 비수치 센티널 (P#5 채택)

- 결함: 21개 검사기의 대상-0 가드가 stdout print 후 **공용 모듈보다 앞에서** `return 2` — 레코드 0건. 또 `#74` 의
  소유자는 target 검사기가 아니라 `workspace/tools/checker_lint.py`(OWNER:69)라 **target 검사기가 #74 레코드를 내는
  것 자체가 오귀속**(MED P#5: «#74 부여는 하지 않는다»).
- 현행 print+return 2 지점 전수(21 — print 문 기준·`return 2` 직후 행):

| 검사기:행 | 검사기:행 | 검사기:행 |
|---|---|---|
| check-api-error-controller-contract.py:6833 | check-mechanism-ownership.py:315 | check-response-schema-bypass.py:997–1001 |
| check-context-isolation.py:913 | check-missable-entrance.py:402 | check-synthetic-infra-exc.py:178 |
| check-db-table.py:544 | check-naming.py:500 | check-test-config.py:436 |
| check-domain-model.py:823 | check-ninja-boundary-middleware.py:155 | check-transaction-boundary.py:503–504 ※문면 상이(«경로 계약 불일치 — #74») |
| check-error-centralization.py:4623 | check-openapi-error-declaration.py:3392 | check-transient-overmapping.py:192 |
| check-event-publish.py:586 | check-port-adapter-pairing.py:825 | check-usecase-dto-placement.py:642 |
| check-idempotency-scope-creep.py:218 | check-public-surface-annotation.py:349 | check-layer-skeleton.py:319 |

- 설계 — `findings.py` 에 공용 helper 신설(21종이 이미 이 모듈을 import):

  ```python
  def guard_zero_targets(line: str, where: "str | Path", msg: str,
                         checker: "str | None" = None) -> int:
      """대상-0 가드 공용화 — stdout 문면은 호출자 소유 그대로(byte 보존),
      레코드는 rule="대상0" 센티널(_emit 이 rule=null+sentinel 로 격리 — findings.py:100–102)
      severity="violation"(exit 2 산입 의미와 정합 — findings/0 정의) 1건. #74 는 달지 않는다
      (owner=workspace/tools/checker_lint.py — rule-owner-map:69 · 오귀속 회피)."""
      print(line)
      _emit(checker or _default_checker(), "대상0", str(where), None, "violation", msg)
      return 2
  ```

  호출부 치환 규칙: 각 지점의 `print(<기존 문면>)` + `return 2` →
  `return guard_zero_targets(<기존 문면 그대로>, where=<target 상대 경로 또는 ".">, msg=<문면에서 label 장식을 뗀 사유>)`.
  stdout·exit 무변, 레코드 1건 신규(`rule=null, sentinel="대상0"`). L-P #5 의 «where 에 target 경로·msg 에 대상-0
  사유» 지시 그대로.
- 대안 기각: «별도 measurement-failure contract»(L-P #5 후단)는 contract_ref 의미(«선행 계약 소유» — F0:16)를
  측정 실패에 오용하므로 센티널 쪽을 채택(기존 «분석·합성·바인딩» 센티널 격리 선례와 동형 — L-P.md:19).

## 부록 B. 계수 골든 영향 예고 (`workspace/tools/findings_count_matrix.py` EXPECTED)

현행 EXPECTED 4행(api-error:52 · error-central:62 · composition:58 · openapi:70)은 **red 픽스처가 tree-slice 레인만
발화**시키므로(계약 레코드 0 — 행에 contract:× 항목 없음), 귀속 변경 «단독»으로 즉시 바뀌는 행은 없을 수 있다.
변화는 Q#6+S#2 채택분(레인 단위 픽스처 신설)과 함께 온다 — 방향(수치는 적용 후 실측):

| 검사기 | 예상 방향 |
|---|---|
| check-api-error-controller-contract.py | code-profile 레인 픽스처에서 contract:선행(08-04)×k → **#62·#126·#474 이동**, #59 신규 계상(Q#6 지적 — 현행 기대값에 #59 부재), 계약 잔존 12종은 contract 유지 |
| check-error-centralization.py | contract×k → **#572 이동**(§2.7 의 6종), blocker 구조화(A-2)로 집계 1건 → 파일별 n건 **레코드 수 자체 변동**, B1 의 #114 분할 반영 |
| check-composition-root.py | contract×k → **#107×3·#108×1·#109×2·#111×1·#440×3 및 DI V1 → #497 이동**, V2·V3 은 contract 유지. §3.3 이중 방출 처분(dedupe 여부)이 계수에 직결 — EXPECTED 갱신 사유에 명기 |
| check-openapi-error-declaration.py | 귀속 무변(이미 #63) — A-1 의 msg 확장만 레코드 문면 변경(계수 무변·violation_id 산식이 message 를 포함하게 되면(S#3 정명) sha 재계산) |
| 대상-0 가드 21종(A-4) | 대상-0 레인은 현행 EXPECTED 에 없음 → **신규 레인 골든**(exit 2·레코드 1·sentinel:대상0×1) 추가 |
| 행번호 재배치 2종(A-3) | synthetic-infra-exc:74 행 `sentinel:합성×1`·public-surface:72 행 등 **계수 무변·where 문자열 변경** → violation_id/fingerprint sha 재계산 |

공통: S#3 채택(violation_id → multiset fingerprint 정명·message 포함 occurrence 축)이 겹치면 sha16 열은 전면
재계산된다 — 귀속 변경과 독립 사유이므로 커밋을 분리한다.

## 통계 (전수 판정)

| 구분 | 행수 |
|---|---|
| 전수 판정 대상 | **91** = api-error 20 + error-central 55 category + error-central blocker 3패턴 + composition 10 + DI 3 |
| #N 귀속 | **26** = api-error 8(#62×2 · #126×3 · #474×1 · #59 유지×2) + error-central 6(#572×6) + blocker 조건부 1(#114 — B1 의 BC 경로 사건 한정) + composition 11(#107×3 · #108×1 · #109×2 · #111×1 · #440×3 · #497×1) |
| 계약 유지 | **65** = api-error 12 + error-central 49 + blocker 2 + composition DI 2 |
| 불확실 표기(보수 처분 포함) | **15** — api-error 3(행18·19·20) · error-central 9(행23·24·30·31·32·33·34·39·41) · blocker 1(B1 의 #114 분) · composition 2(V2·V3) |
