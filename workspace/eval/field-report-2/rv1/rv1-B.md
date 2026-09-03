# 현장 보고 수리 2 — ① 문제 리뷰 · 리뷰어 B(규범 축 — 코퍼스 정합·중복/결손·미끄럼길·과적합) (2026-09-04)

독립 리뷰. 읽은 것: 루브릭 ⓪·① → 현장 보고(처분 블록·«수정 우선순위·판단 기준»·D~H) → 증거 `evidence/{DE,F,G,H}/summary.md` → 규범 정본(`ontology/rules/*.ttl`)·투영물(skills/agents/command md)·`rulepack.json`·검사기 소스 → authoring §13·DEVELOPMENT §3. 저장소 무수정(이 파일만 신규). spring/kkebi 는 카탈로그 `design-spec.md` §10 한 절만 읽었다(리뷰 md 는 범위 밖 — 증거 요약 인용).

## 1. 항목별 판정 표

| 항목 | 판정 | 핵심 근거(규범 축) |
|---|---|---|
| D 결손 성립 | **검증됨(소)** | 코퍼스 `NoReturn`/`Never` 언급 0(grep 전수 · `sys.exit` 는 §? L442 match 예제 1곳) — 참조 지식 공백은 실재. 단 «판단 기준 4» 는 n=2 중 1건이 «레인 병행 framework 코드로 **추정**»(DE §D.5)이라 확정 2레인이 아님 → 걸침 |
| D 착지·문면 | **MINOR** | 착지 = §4.4(`s032-4.4`) 새 블록 b3 — 절 주제(«None 반환 대신 예외 발생»)의 직접 따름정리. §1.2(R-2712/R-2713 = Optional·strict-optional)·§15(15.1 산문 try/except·15.2 계층)·§23.1(설정 블록)은 주제 이탈. R-2720(경계 단서 — 유형 `djr:Exception`)과 무모순(문면을 «조건문»으로 쓰면). `sys.exit` 포함은 과잉(dddjango 산출물에 CLI 없음) — 삭제 권고 |
| E 결손 성립 | **검증됨** | §4 b1 R-3148(«첫 대입에 타입 — 예외 0»)은 «주석의 존재» 규범 — `x: Any` 로 충족됨. 코퍼스 `Any` 정책 0(R-3443 은 «좁히기 위치» 만). 사용자 결정 09-03 |
| E 조건부 허용형 | **MAJOR(자기모순)** | «변수 주석의 프레임워크 미러 자리 조건부 허용» 은 R-3150(«조건부 면제 금지 — 매 실행 흔들리는 암묵 판단»)과 정면 충돌하고, R-3154 의 면제 근거(«문법이 없는 자리 = 불가능»)와 달리 `object` 대체가 가능함이 실측됨(DE 추기 2 override 오류 0) → «불가능» 이 아니라 «판단» 면제. 검사기도 결정적 구분 불가. **무조건형**(시그니처·변수 주석·`*args/**kwargs` 전부 `Any` 0) 만 정합 |
| E 착지·채번 | **MINOR** | 별도 §4.2 신설(새 Section 키 `s013-4.2`·LEDGER 행) 보다 `s007-4` 새 블록 b7(b6 R-3155/R-3156 뒤) 이 작다. 신규 Work 2(Prohibition «명시 `Any` 금지» · Obligation «경계 입력은 `object`/정확 타입으로 받아 즉시 좁힘 — 위치는 R-3443») = R-3446·R-3447(ISSUED 끝 R-3445). `#N` 은 신설 권고(원장 `2026-08-08-tree-revision-spec.md` 최대 #643) |
| E 인접 규범 | **검증됨(무모순)** + MINOR 1 | R-3443·1.12 TypeIs·12.0 pydantic boundary·23.1 strict 블록과 모순 없음. 23.1 에 `disallow_any_explicit` 추가는 **금지**(프로젝트 설정 = B 기각 영역). Knowledge Level `s040-5.5/b10`(kind-code · Work 0)은 R-3156 «예시 면제» 로 남길 수 있으나 A 선례(예제 답습)상 `object` 치환 권고(선택). R-3158 «mypy strict 는 시그니처만 강제» 는 clarification 후보(선택) |
| E 검사기 5표면 | **MINOR(표면 7)** | docstring(#N 등재) · `checker_registry.py`(**무변경** — 이름·auto 플래그뿐) · rulepack `by_checker`(wiring `enforcedBy` 신설 → `make rulepack`) · Coordinator R-0345(`command-dddjango s007/b28` — 새 #N 이면 amendment) · 하우스룰 b7 · **+ 픽스처** `fixtures/public_surface/{good,bad_rules}` + `fixture_matrix`/`checker_cross_matrix` 기대표 · **+ codex byte 미러** |
| F-1 결손 성립 | **MINOR(과적합 경계)** | 1레인·1저장소(표본 외 0/27 BC) → «판단 기준 4» 미충족. 코퍼스에 «주입 callable ≡ Protocol» 문면 없음은 사실(§2.3 R-0719·R-0722~0725 어디에도 없음)이나 프로덕션 결함이라는 이유만으로 규범화하면 1레인 규범화. 채택 시 R-0719 따름정리 1문장으로 축소 |
| F-1 #85 정합 | **MAJOR(문면 조건)** | `check-composition-root.py:1841~1880` — 모듈 최상단의 import·docstring·`build_*` 외 **모든 문장**(`Assign` 포함)이 #85 → 모듈 수준 `_run = partial(...)` 은 #85 red. 문면은 반드시 «`build_*()` **본문 안에서** partial/클로저» 로 써야 한다(발주측 36258bb 도 «#85 인라인 유지»). 이 조건 없으면 R-0725(모듈 전역 인스턴스 금지)와도 충돌 |
| F-2 «BC 마다 1개 강제» | **MAJOR(기각)** | discipline-tdd §5.5(`s025-5.5`) 입장 심사 모델과 정면 충돌 — «quota·coverage·피라미드 비율…만을 이유로 한 테스트 복제» 는 비자격(L445) · design-review-api b(L58) «decision 없이 테스트를 의무화하지 않는다» · coder «구조 규칙만으로 test file 을 만들지 않는다»(coder.md:37). «부재가 기본 상태(21/28)» 는 규범 필요의 근거가 아니라 quota 형이 21건의 근거 없는 add 를 만든다는 경고 |
| F-2 착지 | **MAJOR(소유자 오류)** | 조사자 «착지 = implementation-test» 는 소유 경계 위반 — 무엇을/왜 보호하는가는 discipline-tdd 소유(implementation-test §1.4 L106 «무엇을 만들고 … 는 `discipline-tdd` §5.5 가 소유»). 축소형(«실배선 정합은 인정되는 unique production failure 유형 — 팩토리 monkeypatch 는 그 보호가 아니다» 1항)은 §5.5 «보호할 수 있는 대상» 목록 항으로 착지 |
| F design-review 항목 추가 | **MINOR(기각)** | «주입 의존 공급처» 는 API 계약 lens(design-review-api)도 도메인 lens(design-review-ddd)도 아님 — 구조/배선은 discipline-reviewer(Phase 1 경량 점검 모드) 소유. 두 리뷰어 목록에 넣으면 «한 주제 한 소유자» 위반 |
| G 결손 성립 | **검증됨** | R-3427 rev3(`s005/b36`) 원문: «검사기 판정에 관련되는 **경계 import 전부** … 타 BC OHS/contract·framework 공통만이 아니라 … 서드파티 … 테스트 파일의 경계 import 전부 … **경계만 성문한다(그 밖의 import 는 구현 재량)**» — «경계» 미정의·열거 전부 BC 밖 → 잎→port 는 문면상 **배제로 읽히는 쪽이 자연스럽다**(실전 2/2 ⓑ 독법). 결손 = «경계» 정의 부재 |
| G 조항 형태 | **MAJOR(범위)** | (i) «예외 소비 import 기재»(현장 보고) = 부정합 — #93 은 `port/**` 전체(exception 한정 아님 · `check-context-isolation.py:226~237`)·#96 은 port 선언 → 예외 한정 조항은 잎→port DTO import 를 놓친다. (ii) «BC 내부 층 경계 import 도 블록 대상»(조사자) = 과광 — 잎→use case/command 정상 import 까지 포함되면 «파일별 전체 import 강제 아님» 과 충돌. 정합형 = «층 규율 검사기(#92~#96)의 **금지·예외 항목**에 해당하는 import» 로 한정한 R-3427 clarification |
| G 설계 규범 결손 | **검증됨(별도 결손)** | «port 예외의 번역 책임은 use case» 성문 0(skills·agents grep 0). #92(R-3206)/#93 귀결로 유도 가능하나 ≥4레인(kkebi identity·spring service-policy·openai-rag·catalog)이 **각자 재유도** → 코퍼스 결손 보충 요건 충족. 소유 = architecture-ddd(설계 시점·design-review-ddd 위임). 문면은 «번역» 으로 쓰고 «재수출» 은 인정하지 않는다(notification-bc `__all__` 우회·openai-rag loopback «alias 금지» 긴장) |
| H 규범 간 모순 | **MAJOR(전제 과장)** | «빈 파일 실현»(R-2499·R-3181·R-3188/3189)과 «하나»(#219/#635)는 **시점 차이**로 양립 — 골격 시점 vs 개념 실현 후. 게다가 «하나» 는 **그래프 Work 0**(rulepack `by_alias` 없음·houserules final.md 본문 없음 — 검사기 docstring·원장뿐) → 그래프 규범끼리의 모순이 아니라 «검사기-only 규칙의 시점 미성문». 조사자의 «상충 확정» 은 그래프 위계를 빠뜨림 |
| H Coordinator 골격 문면 0 | **검증됨(결손)** + 선례 발견 | Coordinator 골격 문면 0 은 사실. 그러나 R-0319(`command-dddjango s007/b14`, L117)가 이미 «내용 없는 골격 파일(빈 모듈)은 … 내용이 생긴 뒤부터 검사한다 · 검사기도 빈 골격의 union 부재를 분석 오류로 세지 않는다» 를 registry #2 한정으로 성문 → **pre-content 검사 유예의 선례가 코퍼스에 있다**. #219/#635 는 이 선례를 따르지 않는다. promotion-pricing·saju 의 «time-phased» red 수용은 근거 문면 0 → 그 자체가 결손 |
| H 처방 | **ⓓ 권고(ⓐ 기각·ⓑ 조건부)** | ⓐ는 R-2499·R-3181·R-3188·#488 메시지 4곳 redefinition + R-3425 `empty` 태그(새 빈 파일 = 적법 계획)와 충돌 → 최대 개정. ⓒ는 절차 문면만으로 pre-gate 스텁(빈 파일 예보 red)·슬라이스 게이트를 못 막음. **ⓓ** = #219/#635 를 «내용 없는 골격 파일»(R-0319 와 같은 정의)에 한해 유예 + 형제 파일에 내용이 생기면 발화(결정적 시점 대리) — 그래프 측 최소 개정은 R-3181(#488) **clarification 1문장**(«빈 파일 실현 상태의 내용 규칙은 내용이 생긴 뒤 선다») 또는 R-0319 amendment(#2 한정 → 일반) |
| ⓒ 과적합/결손 분류 | 표 §3 | D 결손(소)·E 결손·F-1 과적합 경계·F-2 과적합·G 결손 2건·H 결손(시점) |

## 2. 항목별 상세

### D — `-> NoReturn`

- 좌표: `implementation-python/references/final.md` §4.4 = `s032-4.4`(graph · `implementation-python-final.ttl:805~823`). b1 = R-2720(유형 `djr:Exception` · «OHS 계약의 결과 분기·조회 use case 의 `None` 답·그 밖 use case 실패는 예외(#571)» · enforcedBy check-context-isolation · delegatedTo discipline-reviewer) · b2 = kind-code(`careful_divide` — 한 경로 raise·한 경로 return). §4.4 에 «예외 우선» 자체를 말하는 Work 는 없고, 그 요약은 SKILL.md `s004/b8` R-3000(«…None 반환 대신 예외 발생 (§15)» — **§15 를 가리키나 실제 절은 §4.4** — 포인터 드리프트 · 범위 밖 MINOR).
- §1.2 = R-2712(Optional 명시)·R-2713(strict-optional) — None «값» 처리. NoReturn 은 «반환 경로 없음» 이라 주제 불일치. §15.1 은 **산문**(마커 없음 · try/except 블록) · 15.2 최상위 예외 계층 · 15.3 deprecated — 예외 «설계» 지 어노테이션 아님. §23.1 은 설정 블록(kind-code). §23.3 `assert_never` 는 exhaustiveness — 인접하나 «Never 반환형» 과 다름.
- 문장 해상도(authoring §13): 새 문장 = 새 Work. 권고 = `s032-4.4` b3(kind-norm) 신설 · R-3446(Obligation) · delegatedTo discipline-reviewer(위임 기본값 표 implementation-*). 문면 형식은 **조건문**으로: «본문의 모든 경로가 `raise` 로 끝나 정상 반환이 없는 함수는 `-> None` 이 아니라 `-> NoReturn` 으로 선언한다 — `-> None` 이면 호출부의 흐름 분석(도달 불가·미정의 가능)이 깨진다.» R-2720 과의 관계: OHS 결과 분기·조회 `None` 은 «반환 경로 있음» 이라 대상 밖 — 문면이 «raise 도우미를 만들라» 로 읽히지 않게 조건문 유지. `sys.exit` 는 dddjango 산출물(BC 코드)에 없고 코퍼스 관용 0 → 삭제(MINOR).
- 판단 기준 4: DE §D.5 — spring `_fail` 은 `framework/` 경로·`dddjango(...)` 표식 없음·«레인 병행 작성으로 **추정**» / kkebi `_raise_provider_error` 는 레인 확정이나 같은 파일 `:366 -> Never` 존재. 확정 레인 1 + 추정 1 → 기준 «두 곳 이상» 은 **걸침(미충족에 가까움)**. 다만 «코퍼스 언급 0» 이라는 결손은 독립 사실이므로 «결손 보충(소)» 으로 분류 — 비용(블록 1·Work 1) 대비 채택 가능.

### E — `Any` 정책

- 구조: `s007-4` b1 R-3148·R-3149·R-3150 / b2 R-3151 / b3 R-3152 / b4 R-3153 / b5 R-3154 / b6 R-3155·R-3156 ; `s008-4.1` R-3157·R-3158. 절 키 현황 `s001,s003,s004-1,…,s012-6.2` → 새 절이면 `s013`.
- (a) 존재 vs 내용: §4 제목은 «타입 어노테이션» 이라 내용 규범도 같은 절 범위. b1 은 존재(R-3148)·범위(R-3149)·조건부 면제 금지(R-3150)의 3 Work 블록. `Any` 금지는 «R-3148 의 «타입» 에 `Any` 는 들지 않는다» 는 R-3148 의 범위 축소(amendment 성격)이나, 검사기 배선(enforcedBy)·rulepack 조인·픽스처 계수를 위해 **독립 Prohibition Work** 가 깔끔하다. → b7 신설(b6 뒤) · R-3446 Prohibition + R-3447 Obligation. §4.2 신설은 Section 노드·headingSnapshot·LEDGER 행이 늘어 크다 — 정책이 3문장 이상·독자 근거절이 필요해질 때만.
- (b) 조건부 vs 무조건: R-3150 원문 «「자명하니까 면제」를 두지 않는다 — 조건부 면제는 매 실행 흔들리는 암묵 판단으로 돌아온다». R-3151~3154 의 면제는 «문법이 없는 자리(면제가 아니라 불가능)» 로 정당화된다. 프레임워크 미러 `Any` 는 `object` 로 대체 가능(DE 추기 2: `Form.__init__(*args: object, **kwargs: object)`·`clean() -> dict[str, object]`·`has_change_permission(obj: object | None)`·`delete(using: object = None)` override 오류 0) → «불가능» 아님 → 조건부 허용은 R-3150 의 «암묵 판단» 그 자체. 검사기가 «미러 자리» 를 결정적으로 못 가른다는 점(DE E.6)도 같은 결론. **무조건형** 확정 권고. 문면에 `*args/**kwargs` 포함 명시(ruff `allow-star-arg-any` 관례와 다름 — R-3157 «주류와 다른 선택임을 숨기지 않는다» 와 정합). 적용 대상 절은 R-3443 선례(«신규 값 객체·손대는 줄 — 기존 정리는 발주 소관»)와 같은 형으로 두되, 검사기의 «전 파일 fail-closed(기존 코드도 빚)» 계약과의 긴장은 #493 이 이미 안고 있는 구조라 새 모순 아님(귀속 처리는 A/C 축).
- (c) 인접: R-3443(`s016-3.1` — «`object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 전 경계가 담당») 은 «어디서» · 새 R-3447 은 «경계가 무엇으로 받는가(`object`/정확 타입 · JSON 은 `Mapping[str, object]`) + 즉시 좁힘(TypeIs/isinstance/`type() is`)» — 인접하나 별개. 문면에 «(좁히기 위치는 R-3443 · 메커니즘은 implementation-python 1.12)» 참조로 중복 회피. 12.0 pydantic boundary(«shape 명시») 와 정합 — ninja `Schema` 필드 `x: Any`(kkebi `schema_in.py:25`) 가 red 되는 것은 R-3155 «`x: T` 필수» 의 정상 귀결. 23.1 strict 설정 블록은 손대지 않는다(`disallow_any_explicit` 추가 = 프로젝트 설정 강제 = B 기각 재개봉). R-3158 «mypy strict 는 시그니처만 강제 — 나머지는 백스톱과 감수자» 에 «명시 `Any` 도 strict 가 막지 않는다» clarification 은 선택.
- (d) Knowledge Level `s040-5.5/b10`(kind-code · statesNorm 0 · `values: dict[str, Any]`·`value: Any`): R-3156 «표준 문서군의 코드 예시는 적용 대상 밖» 이 문면상 덮는다. R-20 은 로드맵의 «점검 원칙»(그래프 Work 아님)이고 mypy strict 는 명시 `Any` 를 막지 않으므로 R-20 이 교체를 강제하지 않는다. 그러나 파트 1 A(레인이 예제를 답습)의 실증상 «규범이 금지하는 모양을 예제가 보이는» 내부 불일치는 미끄럼길 → `dict[str, object]`·`object` 로 치환 권고(선택 · 블록 리터럴만 · Work 무변 · 렌더 재투영).
- (e) 표면: ① 검사기 docstring 규칙 목록(#N 추가·검출 한계) ② `checker_registry.py` **무변경**(이름·auto 플래그만) ③ rulepack `by_checker` — 새 Work 에 `djr:enforcedBy c/check-public-surface-annotation.py` wiring 저작(authoring §16 4원 근거 검수표) → `make rulepack` ④ Coordinator registry #11 = R-0345(`s007/b28` «타입 전면(#493)·Thin Read(#358)·계약 검증 토큰(#456)») — 새 #N 이면 amendment(«명시 `Any`(#N)» 병기) ⑤ 하우스룰 b7. **누락 2**: ⑥ 픽스처 `workspace/eval/fixtures/public_surface/{good,bad_rules}` + `fixture_matrix.py` EXPECTED + `checker_cross_matrix.py`(public_surface 픽스처에 대한 타 검사기 기대 — 파일 추가 시 재실측) ⑦ `codex-dddjango/skills/dddjango/scripts/` byte 미러.
- (f) 채번: R-3446·R-3447(ISSUED 끝 R-3445 · rules 경로 `rules/discipline-houserules-skill.ttl`). `#N`: #493 재사용(«`Any` 는 타입 부착으로 인정하지 않는다» 독법)도 가능하나 존재/내용 계수가 섞여 픽스처 기대표·baseline 텔레메트리가 흐려진다 → **신설 권고**(원장 `workspace/design/2026-08-08-tree-revision-spec.md` 538 규칙·최대 #643 → #644 후보 · 검사기 docstring 전수 대조는 미확인).

### F-1 / F-2

- §2.3 `s010-2.3` graph(LEDGER owner=graph 확인). R-0719(b18 «DI 조립 소유·build_<uc>() 매요청 호출») · R-0722~R-0725(b20/b21). «주입 callable ≡ Protocol»·«partial» 문면 0(재확인). «만들기와 꽂기» 는 `check-composition-root.py:1863` 메시지에만 있고 final.md 에 없다 · #85 R-ID 없음(rulepack by_alias 0 · Coordinator R-0350 registry #16 소개만).
- #85 코드(`:1849~1880`): `mod.body` 순회 — Import/ImportFrom·docstring·`build_*` FunctionDef 외 **모든 노드**가 #85(`Assign`·비-build 함수 포함). 따라서 «composition root 가 partial 로 묶는다» 만 쓰면 레인이 모듈 수준 `_run = partial(...)` 을 만들어 #85 red 를 맞는다 → 문면에 «`build_*()` 본문 안에서» 필수. 이렇게 쓰면 R-0719 «매요청 조립»(partial 도 매요청 생성)·R-0725(전역 인스턴스 금지)·b21 «테스트 오버라이드 회피» 와 정합.
- F-1 판정: 1레인·표본 외 0(spring 15 BC·kkebi 12 BC 불일치 0) → 기준 4 미충족 · 정적 검출(mypy arg-type)이 있음(B 기각 영역). 채택하더라도 «R-0719 의 따름정리 1문장(꽂기 = 시그니처 동일 · 부족 인자는 build_* 본문 안 partial/클로저)» 로 축소. 검사기 승격 근거 없음.
- F-2: 코퍼스 «composition root»·«실배선» 언급 0 은 사실. 그러나 «BC 마다 1개» 는 quota 형 — discipline-tdd §5.5 «영구 test artifact 를 add 하기 전에 [candidate | protected contract | unique production failure | existing coverage | decision] 행을 확정한다 · 후보 목록·피라미드·coverage 는 이 행을 건너뛸 근거가 아니다» 와 «quota·coverage·피라미드 비율·디버깅 편의만을 이유로 한 테스트 복제(비자격)» 에 저촉. design-review-api L58 «decision 없이 테스트를 의무화하지 않는다». coder.md:37 «구조 규칙만으로 test file … 빈 test package 를 만들지 않는다». 세 문면과 동시에 모순되는 조항은 채택 불가. «부재가 기본 상태 21/28» 은 그 21 BC 에 실배선 unique failure 가 있었다는 증거가 아니다(불일치 0). 축소형 착지: §5.5 «영구 테스트가 보호할 수 있는 대상» 목록에 1항 «composition root 실배선 정합(진짜 `build_*()` → 실 어댑터 → 최소 1경로) — 팩토리 monkeypatch 는 이 failure 를 보호하지 않는다» 신설(Work 1 · delegatedTo discipline-reviewer). #389(integration=실DB)·#385/#13(타 BC import 금지)은 검사기 docstring 에만 성문(houserules final.md 본문 0 — 미확인 항목)이라 문면은 «외부 경계는 자기 BC fake(#385) · DB 필요 시 integration(#389)» 정도로 일반화 — «LLM 만 fake·데이터 루트 fixture» 는 RAG 특이 → 과적합.
- design-review 항목: 소유 위계상 기각(위 표).

### G — boundary-imports «경계»

- R-3427 rev3 원문(`design-architect.md:90` = `s005/b36` · rev1 09-01 → rev2 09-03 amendment(3단 실존) → rev3 09-03b amendment(승격 예외 ⑴)): «검사기 판정에 관련되는 **경계 import 전부**를 … 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계만 성문한다(그 밖의 import 는 구현 재량)**.» → «경계» 정의 없음 · 열거 4종 전부 BC 밖·서드파티 · «그 밖은 재량» 으로 닫힘. 머리절 «검사기 판정에 관련되는» 만이 ⓐ 독법의 근거인데 #93 은 «판정» 검사기라 ⓐ도 문면상 가능 → **양립 가능한 두 독법 = 결손**. 실전 2/2 가 ⓑ(카탈로그 명세 L511 명문화·리딩 P4 port 행 0).
- 조항 형태: (i) 예외 한정은 #93 정의(`app_port` = `application_layer/port/**` 전체)·#96(port 선언)과 어긋나 잎→port DTO/선언 import 를 놓침 → 기각. (ii) «BC 내부 층 경계 import 도 블록 대상» 은 잎→`<area>/<use_case>` 정상 import 까지 포괄되어 «파일별 전체 import 강제 아님» 과 충돌·블록 비대(fortune-record 27행) → 한정 필요. 정합형: R-3427 clarification «경계 = ① 저장소 밖(서드파티) ② 타 BC·framework ③ **층 규율 검사기(#92~#96)가 금지 또는 예외 항목으로 판정하는 BC 내부 층 횡단**(driving 잎→`application_layer/port/**`·`driven_layer/**`·`domain_layer` 비-exception/VO 등)». R-3425 태그 의미론과 무관(행은 소비자 태그를 바꾸지 않음) · 3단 실존 판정은 자기 add 자기 해소(symbols) 그대로 · S3 문면(«블록 기재 경계 import 는 예보됨») 과 정합 — S3 는 보고 정직화이지 architect 의무가 아니므로 대체 불가.
- (iii) 설계 규범: architecture-ddd 에 «port 예외의 번역 책임 = use case(application_layer)» 0(grep). #92(R-3206)+R-2720 으로 유도 가능하나 ≥4레인 재유도(kkebi identity-bc L255·spring service-policy L642·openai-rag loopback·catalog 진화 3) = 결손 보충 요건 충족(기준 4: 검사기가 잡되 **Phase 2 에서** 잡음 = 설계 시점 결손). 착지 = architecture-ddd 응용 서비스/포트 절(delegatedTo design-review-ddd) 새 Work 1. «재수출 경유 catch» 를 정당화하지 않도록 «번역» 으로 성문.

### H — pre-content 골격

- 성문 위치: R-2499(`agent-coder s004/b2` · delegatedTo command-dddjango · enforcedBy app-container·layer-skeleton) «고정·재등장 칸은 내용이 없어도 … 파일은 빈 파일로 만든다(#488)» · R-3181(`houserules-final s003-0/b3` = #488) «파일도 비면 «빈 파일»로 … 빈 칸 실현의 정본 형태는 여전히 «빈 파일»» · R-3188/R-3189(`s003-0/b8`) «coder 가 … 빈 채로라도 실현 · 위반은 check-layer-skeleton» · R-3186(#491 «조건부 없음» — 주어는 칸의 **존재**). #219(`check-port-adapter-pairing.py:245`)·#635(`check-usecase-dto-placement.py:383`) «하나» 는 **Work 없음**(rulepack by_alias·aliases.ttl·houserules final.md 본문 전부 0 — docstring·`tree-revision-spec` 원장뿐) · Coordinator registry #19/#22 소개행(L141/L144)에도 «하나» 언급 없음.
- 모순인가: 그래프 규범은 «빈 파일 실현»(골격 시점)만 말하고 «내용» 은 말하지 않는다 · «하나» 는 내용 규칙. 시점 차이로 양립. 결손은 «빈 파일 실현 상태에서 내용 규칙이 언제 서는가» 미성문. 게다가 R-0319(`command-dddjango s007/b14` L117) «내용 없는 골격 파일(빈 모듈)은 inventory 에서 제외 — 골격 실현 의무로 만든 빈 칸은 **내용이 생긴 뒤부터 검사** · 검사기도 빈 골격의 union 부재를 분석 오류로 세지 않는다(2026-08-15)» 가 registry #2 한정으로 이미 이 시점 규칙을 성문 → #219/#635 는 코퍼스 선례를 따르지 않는 검사기. R-3425 `empty` 태그(«새 빈 파일» = 적법 계획 · 09-04 ⑥ MAJOR-1 반영)가 있는데 pre-gate 스텁이 그 빈 파일을 #219/#635 로 예보 red 하는 것(fortune-reading pregate-report #219×1·#635×1)도 같은 불일치.
- 처방 위계: ⓐ = R-2499·R-3181·R-3188 redefinition + #488 메시지 + R-3425 `empty` 의미 재정의 → 최대. ⓑ 순수 면제 = 영구 잔존 위험(kkebi tarot 애그리거트 12 파일 10일 — 단 그 칸엔 «하나» 규칙 자체가 없음). ⓒ 절차 문면 = 검사기·pre-gate 스텁을 못 막음. **ⓓ** = #219/#635 를 «내용 없는 골격 파일»(R-0319/`_skeleton_placeholder_module` 과 같은 정의 — 0바이트 또는 docstring 만) 에 한해 유예 + «같은 칸 형제 파일(`_command/_result`·adapter·fake)에 내용이 있으면 발화»(결정적 시점 대리 — Coordinator 판단 불요). 그래프 최소 개정 = R-3181 **clarification** 1문장(«빈 파일로 실현된 칸의 내용 규칙(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다 — R-0319 와 같은 시점») 또는 R-0319 amendment(#2 한정 → 일반). 검사기 변경은 면제 «추가» 라 ⑤ 에서 무손실 증명(pre-content 집합만 제외 · 형제-내용 조건으로 잔존 차단) 필요.
- «time-phased skeleton» 수용 근거: Coordinator·houserules·R-0319(#2 한정) 어디에도 «골격 슬라이스 red 는 수용» 문면 없음 → 무근거(결손 그 자체). 원문(리뷰 md)은 읽기 범위 밖 — 증거 H §4 인용.

## 3. ⓒ 효과·미끄럼길 — «판단 기준 4» 적용 표

| 항목 | 검사가 잡나 | 반복(레인/저장소) | 분류 | 판정 |
|---|---|---|---|---|
| D | 플러그인 검사기 ✗ · mypy(프로젝트) ✓ | 1 확정 + 1 추정 / 2 | 코퍼스 결손 보충(소) | 걸침 — 저비용 채택 가능 |
| E | ✗(검사기 확장 대상) | 정책 부재 자체(사용자 결정) | 코퍼스 결손 보충 | 무조건형만 채택 |
| F-1 | mypy ✓(프로젝트) · 플러그인 ✗ | 1/1 | 1레인 규범화(과적합 경계) | 축소 1문장 또는 보류 |
| F-2 «1개» | 실배선 테스트 ✓ | 1/1(부재 21/28 은 결함 아님) | 과적합 + §5.5 모순 | 기각 → 보호 대상 유형 1항 |
| G (ii) | pre-gate ✓(블록 기재 시) · Phase 2 #93 ✓ | 2 블록 보유 + 3 블록 없음 / 2 | 결손 보충(«경계» 정의) | 한정형 채택 |
| G (iii) | Phase 2 #93 ✓(늦음) | ≥4 / 2 | 결손 보충(설계 규범) | 채택 |
| H | 검사기가 오히려 발화 | 4 / 2 | 결손 보충(시점 규범) | ⓓ + clarification |

## 4. 범위 권고(유지/축소/기각 · 착지 Work · 개정 종류)

- **D 유지(축소)**: `s032-4.4` b3 신설 · R-3446 Obligation · 조건문 형식 · `sys.exit` 삭제 · delegatedTo discipline-reviewer. (부수: SKILL R-3000 «(§15)» 포인터 → «(§4.4)» clarification 은 범위 밖 기록.)
- **E 유지(무조건형 확정)**: `s007-4` b7 신설 · R-3446/R-3447(D 와 채번 순서는 계획이 확정) · 검사기 #N 신설(#644 후보) + docstring·픽스처·cross matrix·codex 미러·wiring enforcedBy·rulepack·Coordinator R-0345 amendment. 23.1 무접촉. Knowledge Level `object` 치환·R-3158 clarification 은 선택.
- **F-1 축소**: R-0719 따름정리 1문장(«`build_*()` 본문 안 partial/클로저» 명시) — 새 Work 1(`s010-2.3` b18 또는 b20 불릿) · 검사기 승격 없음. 보류도 정당(기준 4 미충족).
- **F-2 기각 → 축소형**: «BC 마다 1개» 폐기 · discipline-tdd `s025-5.5` «보호할 수 있는 대상» 목록에 1항 신설(Work 1 · delegatedTo discipline-reviewer) · implementation-test 착지 철회 · design-review 항목 기각.
- **G 유지(재형식화)**: R-3427 **clarification**(«경계» 3분류 — 층 규율 검사기의 금지·예외 항목 포함) + architecture-ddd 새 Work 1(«port 실패 번역은 use case 소유 — 재수출 아님» · delegatedTo design-review-ddd). 현장 보고 (i) 형은 기각.
- **H ⓓ**: #219/#635 pre-content 유예 + 형제-내용 발화 조건(검사기·docstring·픽스처·미러) + R-3181 clarification 1문장(또는 R-0319 amendment). ⓐ 기각 · ⓒ 단독 기각 · Coordinator 신규 절차 문면 불요.

## 5. 미확인

- D: spring `_fail`(`43e9628`) 이 dddjango 레인 산출물인지(«추정» — 표식 없음) · kkebi `payment_processing_adapter` 의 두 도우미가 같은 슬라이스에서 나왔는지.
- E: `#644` 가 검사기 docstring·설계 문서 어디에도 미사용인지(원장 최대 #643 만 확인) · 검사기 귀속(registry_gate)이 기존 `Any` 18+100 건을 touched 밖으로 걸러 주는지(A/C 축).
- F: #385/#389/#13 의 그래프 Work 유무(houserules final.md 본문 grep 0 — 검사기 docstring·Coordinator registry #12/#6 소개행뿐으로 보임) · «26곳» 집계 기준.
- G: R-3427 rev1→rev3 사이 «경계» 문구 변동 여부(블록 리터럴은 현행만 보존 · 개정 사유는 rev2 3단 실존·rev3 승격 예외로 «경계» 정의와 무관) · kkebi 구형 명세 5건의 블록 대조.
- H: promotion-pricing·saju 의 «time-phased» 수용 원문(리뷰 md — 읽기 범위 밖) · pre-gate 스텁이 `empty` 태그 파일에 #219/#635 를 예보하는지 실측(fortune-reading pregate-report 인용만).

Serena: skipped — 읽기 전용 규범 리뷰(코드 편집 없음)라 기본 도구로 충분.
