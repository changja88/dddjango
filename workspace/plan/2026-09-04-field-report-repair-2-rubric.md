# 현장 보고 수리 2 — 제보 수정 단계(D·E·F 문면·G·H) 절차·적대 리뷰 루브릭 (2026-09-04 사용자 «착수»)

- 대상: `2026-09-03-field-report-spring-dream-typecheck.md` 처분 상태 블록의 미결 5건 — D(항상 raise 도우미 `-> NoReturn` 문면 · R-18) · E(`Any` 정책 — 하우스룰 §4 절 + 검사기 #493 확장 · R-19) · F-1/F-2(composition root 주입 callable ≡ Protocol · 실배선 테스트 규율 — 문면 2줄 · F 본체는 발주측 36258bb 자체 수리) · G(발견 ⑪ boundary-imports 블록에 예외 소비 import 기재 조항) · H(발견 ⑫ pre-content 골격 상충 — Coordinator 골격 규범 ⓐ vs 검사기 면제 ⓑ 택일). A·A3·4·B·C 는 파트 1 종결(main 88a65a0).
- 성격: 그래프 정본 문면 리비전(D·F·G·H 후보) + 검사기 확장(E 후보 — byte 미러·픽스처 동반). 실행기(`design_pregate.py`) 무접촉 예정. 판형 = 파트 1 루브릭(`2026-09-03-field-report-repair-rubric.md`) · 승격 루브릭(`2026-09-03-pregate-promotion-rubric.md`) 동일: ⓪ 증거 → ① 문제 리뷰 ×3 → ② 계획 → ③ 계획 리뷰 ×3 → ④ 구현 → ⑤ 구현 리뷰 ×3 → ⑥ 독립 감사·재검. 매회 독립 서브에이전트 3기(A 기술·B 규범·C 증거/표본 외) · 3축(코퍼스 정합·일반화·무손실) · 심각도(BLOCKER/MAJOR/MINOR/검증됨).
- 결정 게이트 2(사용자 09-04 확정): ① 뒤 «범위 확정»(E 범위 — 시그니처 `Any` 0 무조건 · 변수 주석의 프레임워크 미러 자리 조건부 허용 여부 / H 택일 ⓐ·ⓑ / 나머지 유지·축소) → ⑥ 뒤 «머지 진행». 릴리즈·push 없음(사용자 요청 시 `make release`).
- 브랜치: `fix/field-report-2`(main c7573b6 기점). 산출: `workspace/eval/field-report-2/`(⓪ `evidence/` · rv1 · rv3 · rv5 · rv6).

## ⓪ 조사자(코디) 검증 결과 (2026-09-04 — 리뷰어는 이 전제를 공격한다)

조사자 4기(D·E / F / G / H) 독립 실측 + 코디 직접 확인. 증거 원문 `workspace/eval/field-report-2/evidence/<항목>/summary.md`(스크립트·jsonl 동봉). 두 저장소 읽기 전용 · 검사기·mypy 는 rsync/`git archive` 격리 복제본에서 실행.

### D — 항상 raise 도우미 `-> None` (실측 2026-09-04)

- **재현 규모**: AST 전수(spring 2,918 · kkebi 3,952 파일). «항상 raise ∧ `-> None` ∧ 프로덕션 ∧ 도우미형» = **spring 0 · kkebi 1**(`application/billing/.../toss/payment_processing_adapter.py:437 _raise_provider_error`). 같은 파일 `:366 _raise_transport_failure -> Never` 가 이미 있음 → **지식 부재가 아니라 파일 내 일관성 문제**. 나머지 `-> None` 항상-raise 는 `__init__` 생성 차단 가드 3(mypy 가 `-> None` 강제 · 대상 아님)·테스트 fake 강제-실패 스텁 28.
- **보고서의 `_fail`**: spring `framework/.../service_runtime.py:642` 는 **이미 `-> NoReturn`**(발주측 `96e8719` mypy 빚 상환 커밋 · 레인 아님). 발생 당시(43e9628, 리딩 P3 레인 병행 framework 코드)에는 `-> None` 이었음 → 원 사건 1 + kkebi 1 = **n=2 / 2저장소**, 둘 다 레인 산출물(kkebi 는 `20260823-1637-billing-migration` 런 리뷰 md 가 파일 언급 · discipline 리뷰 언급 0).
- **정상 사용 실증**: `NoReturn/Never` 도우미 7(spring llm_access 슬라이스 0 커밋 `5431706` 3 · framework 2 · kkebi 2) → 레인이 쓸 줄 안다. 코퍼스 `NoReturn` 언급 0.
- **판단 재료**: 플러그인이 만든 모양 아님(코퍼스에 `-> None` raise 예제 없음) · 검사기 없음 · 반복 2레인(저장소 각 1). 현장 보고 기준 4 «검사가 못 잡는데 레인 두 곳 이상 반복 → 문면 후보» 에 **정확히 1건 차이로 걸침**(2레인·2저장소). 효과 = 문면 1줄(확률적) — mypy 결정 실행은 B 기각으로 없음.

### E — 명시 `Any` 정책 (실측 2026-09-04)

- **기준선(허용 상태의 자연 발생)**: 프로덕션 `Any` 사용 spring application **120**(bare 45 · 제네릭 안 75) · framework 633(RAG 런타임, 레인 밖) / kkebi application **133**(bare 71 · 안 62) · web 218(dddjango-web 응답 파서 사다리) · scripts 95. 보고서 «시그니처 `Any` 47 · application 0» 은 ANN401(bare 시그니처만·`*args/**kwargs` 면제) 기준의 수치 — **재집계: application 프로덕션 시그니처 bare `Any` = spring 8 · kkebi 10**. spring 8/8 은 Django 스텁 오버라이드 미러(Form `__init__(*args: Any, **kwargs: Any)` 6 · Model `update/delete` 2). kkebi 10 = 미러 5 + **실질 세탁 5**(`product_observability` 컨트롤러 도우미 `decision: Any` 2 · `saju` 도메인 서비스 JSON 순회 3).
- **막는 도구 부재 실증**: 두 저장소 `ruff.toml` 이 ANN401 을 select 후 ignore(순효과 비활성) · `allow-star-arg-any = true` · mypy 는 `disallow_any_explicit` 미설정 · pre-commit mypy 범위가 spring `application/` **미포함**·kkebi `web/` 미포함. → 현재 `Any` 를 막는 것은 아무것도 없다(레인 discipline reviewer 의 즉석 규칙만).
- **검사기 #493 자리**: `check-public-surface-annotation.py` 는 주석 «유무»만 보고(211~226·265~268·320~322) 내용은 #358 만 읽음(`_annotation_names` 341~352). «명시 `Any`» 규칙은 그 세 자리에 `_name_of(ann)=="Any"`(bare)·`"Any" in _annotation_names(ann)`(제네릭 안) 로 붙일 수 있고 `typing.Any`/`t.Any`/별칭은 기존 `_module_bindings` 로 해소. 현재 선언적 면제(`_is_declarative_class`)는 plain Assign 과 `self.x` 에만 걸려 있어 ninja `Schema` 필드 `x: Any`·Django 오버라이드 미러의 취급은 새 규칙이 정해야 함. 격리 실행 #493 기준선: application/* **0**(양 저장소) · 레인 밖 spring framework 3,078·kkebi web 등 173.
- **`object` 대체 가능성 프로브**(mypy 2.3.1 strict): Django 스텁 오버라이드 4형(`Form.__init__ *args/**kwargs` · `clean()` · `ModelAdmin.has_change_permission(obj)` · `Model.delete(using)`)을 `object` 로 바꿔도 **override 호환 오류 0**, `object` 값을 `Any` 매개변수에 넘기는 `super()` 호출도 통과. → «시그니처 `Any` 0» 은 프레임워크 미러 자리에서도 지킬 수 있다. 소급 비용 = 기존 레인 산출물 18건(미러 13 · 실질 5) 기계 치환.
- **코퍼스 정합 재료**: 하우스룰 §4 «예외 0» + «표준 문서군 예시는 적용 대상 아님» · R-3443(`object`/`Any` 입력은 경계가 좁힘) · implementation-python 1.12 TypeIs · 23.1 mypy strict 설정 블록(`disallow_any_generics`·`warn_return_any` 만 열거). architecture-ddd Knowledge Level 예제 `dict[str, Any]`·`value: Any` 는 예시 면제 대상이나 R-20(생성 모양 strict 준수)과의 관계는 ① 판정.

### F — composition root 주입 callable ≡ Protocol · 실배선 테스트 (실측 2026-09-04)

- **정적 대조 재현**: AST 로 `composition_root/dependency_wiring.py` 전수 → 생성자 키워드 인자의 callable 주입 지점(spring 51 · kkebi 48)을 수신 Protocol `__call__`/`Callable` 시그니처와 대조. 원 결함 커밋 `585c9c6`·수리 직전 `36258bb^` 에서 **불일치 1**(`fortune_reading/.../dependency_wiring.py:42` — Protocol 9키워드 vs 필수 `data_root,embedder` 미공급), HEAD 0. mypy strict 도 수리 전 그 줄을 `[arg-type]` 로 검출 — 그러나 pre-commit mypy 대상이 `spring_dream_server framework` 라 `application/` 미포함(레인·훅 모두 못 봄).
- **표본 외**: kkebi 12 BC · spring 나머지 15 BC 불일치 **0** → 시그니처 불일치는 **1레인 특이**. 보고서 grep(spring 159·kkebi 15 파일) 유사 사건 1(같은 어댑터의 테스트 fake 가 `content_roles` 미수용 — 방향 반대). «테스트 26곳» 은 미재현(실측 `build_*` patch 14 + llm_access 3).
- **실배선 테스트 부재는 기본 상태**: 진짜 `build_*()` 를 실행하는 테스트가 있는 BC = spring 5/16(리딩은 36258bb 신설) · kkebi 2/12. 신설 `test_composition_root_wiring.py` 의 fake 경계 = LLM ACL 어댑터·가중치 소재 2곳뿐.
- **문면 현황**: `implementation-django-ninja/references/final.md` §2.3(294~313 · graph-owned · R-0719/R-0722~0725)에 «주입 callable ≡ Protocol»·«partial» 문면 **없음**; «매요청 호출 … 테스트 오버라이드 회피»(312)는 있음. `implementation-test`·`discipline-tdd` 에 «composition root»·«실배선» 언급 **0**(보고서가 지목한 `discipline-test` 스킬은 **존재하지 않음** → F-2 착지는 implementation-test). design-review-api(49~58)·ddd(31~44) 관점 목록에 «주입 의존 공급처» 없음. 검사기 `check-composition-root.py` #85(1841~1875)는 «최상단은 import 와 build_* 뿐» 형태만 검사 — 주입 값·시그니처 무검사.
- **판단 재료**: F-1 은 «검사가 못 잡는 1레인 사건» 이지만 프로덕션 결함이었고 정적 검출 가능(AST·mypy) · F-2 는 «부재가 기본 상태»(n=21/28 BC) 라 문면 1줄의 소급 강제 여부가 쟁점. 미측정: 옛 배선의 런타임 TypeError 재현(테스트 미실행)·레인 당시 mypy 실행 범위.


### 코퍼스 좌표 (코디 직접 확인 · 2026-09-04)

- **D**: 코퍼스 전체에 `NoReturn` 언급 0건(skills refs·SKILL.md·agents·command 전수 grep). `implementation-python/references/final.md` §1 «타입 힌트와 타입 시스템»(1.1~1.14 · 대부분 graph-owned) · §4.4 «None 반환 대신 예외 발생»(graph-owned · ttl `implementation-python-final.ttl` ≈806) · §15 «예외 처리»(15.1 산문 · 15.2/15.3 graph-owned) · §23 «mypy/pyright 최신 기능»(graph-owned). `sys.exit` 는 L442 match 예제 1곳뿐. → 착지 후보 = §4.4 블록 추기(예외 우선 문단과 같은 주제) 또는 §1.2 Optional 블록.
- **E**: 하우스룰 `discipline-houserules/SKILL.md` §4(graph-owned · 섹션 `s007-4` · b1 = R-3148/R-3149/R-3150 «모든 이름 첫 대입에 타입 — 예외 0» · «문법이 없는 자리» 목록 · 프레임워크 선언 예외 · «표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다») · §4.1 «왜 전부인가». 코퍼스 `Any` 언급 4건 전부 `architecture-ddd/references/final.md`(L485 R-3443 문장 «`object`/`Any`/JSON 입력의 타입 좁히기는 경계가 담당» · L1585~1619 Knowledge Level 예제 `values: dict[str, Any]`·`value: Any`). `Mapping[str, object]` 관용구 언급 0건. 검사기 #493 = `check-public-surface-annotation.py`(`_annotation_names` L341 · 함수 시그니처 L357~ · AnnAssign L379~ 순회).
- **F·G·H**: 조사자 실측에 코퍼스 좌표 포함(F = implementation-django-ninja composition_root 절·implementation-test/discipline-test · G = architect boundary-imports 형식 규범·design_pregate 스텁 방출 · H = Coordinator 골격 문면·#219/#635/#218/#193/#576 조건).

### G — boundary-imports 블록의 잎→port 소비 import 결손 (실측 2026-09-04)

- **명세 7건 대조**(카탈로그·리딩은 수리 전 G1/P4 판본을 spring git `9ee721e`·`919440c` 에서 복원): 잎→`application_layer/port` 행이 블록에 있는 명세 **0/7**. 산문에서 잎이 port 예외를 소비한다고 적은 명세 = 카탈로그 G1(L167 명시 — 단 같은 명세 L57 은 «OHS 는 port 를 import 하지 않는다» → **명세 내부 모순**, 블록은 L57 쪽과 일치) · 리딩 P4(§5.10 암묵 — `failure.cause` 를 port 예외 타입으로 분기). notification-bc 는 use_case `__all__` 재수출 경유로 catch → 블록에 재수출 경로 행 있음(무영향). 나머지 4건 언급 없음.
- **코드 실측**: 현재 7 BC driving 잎의 `application_layer.port` import **0**, spring 전 ref 이력에도 0(카탈로그 S4·리딩 P4 위반 코드는 커밋 전 수리 — REPORT/STOP 만 증거).
- **#93 실발화 이력**: spring 3(openai-rag-generation 08-27 G1″ 블록 없음 · fortune-reading P4 09-02 STOP `#93·#96 6+6` 블록 있으나 port 행 0 · fortune-catalog Phase 2 S4 «설계 진화 3») + kkebi 2(tarot-reading 08-25 `#93(3)+#96(3)` · billing-payment-http 08-26) = **5 레인(블록 보유 2 + 블록 없는 3)**. pregate-report 의 `#93` 51회는 S3 사각 상용구(발화 아님).
- **실행기 격리 실측**(복제 @`e1294f5` · `--base HEAD`): 카탈로그 G1 원본 블록(해시 `6cf8e2ffdfc3` = 실제 4번째 런과 일치) → exit 0 green 재현. 블록에 OHS→port 예외 import 2행 추가 → **exit 2 · `#93`×2 + `#96`×1 예보**. «블록에 적혔다면 예보됐다» 성립(`_parse_imports` L495~521 → `render_stub` L806~810 원문 방출 · 행 종류 무제한). S3 문면 «산문에만 적힌 경계 import 는 표면 밖» 은 카탈로그 G1 이후(`2fbc111`) 추가.
- **규범 현황**: `design-architect.md` L90 = `s005/b36` → **R-3427 rev3**. 문면은 «검사기 판정에 관련되는 경계 import 전부» 라면서 열거는 타 BC·framework·서드파티·테스트뿐이고 «경계만 성문(그 밖은 구현 재량)» → 카탈로그 architect 는 **intra-BC 층 경계(잎→port)를 경계 아님으로 읽고 명세에 명문화**(현재 명세 L511). #93 은 `application_layer/port/**` 전체(예외 한정 아님 · checker L226~237 · 근거 하우스룰 #92). architecture-ddd 에 «use case 가 port 예외를 번역» 직접 성문 없음 — 설계 진화 3 은 #92/#93 귀결로 정합.
- **판단 재료**: 동형 결손 ≥2 레인 **성립** · 성격 = 실행기 사각 아님, **R-3427 «경계» 독법의 채널 전사 결손** + 카탈로그 G1 내부 모순. 처방 방향은 «예외 소비 import» 한정이 아니라 «잎→port 등 검사기(#92/#93/#96)가 보는 **BC 내부 층 경계 import 도 블록 대상**» 으로 넓혀야 정합. 무손실: 조항 추가 시 형식 red = 현재 판본 0 · 당시 판본 2(명시 1·암묵 1). 미측정: 리딩 P4 위반 코드 원문 · kkebi 블록 대조(구형 20건 전부 블록 0) · 조항 후 반송 증가율.

## ① 공격 질문 (항목마다 필답 · 판정 병기)

- D-1 «항상 raise 도우미 `-> None`» 이 플러그인이 만든 모양인가(코퍼스에 `-> None` raise 도우미 예제가 있는가) 아니면 코더 선택인가. 같은 저장소 다른 레인이 `NoReturn` 을 썼다면 «지식 부재» 가 아니라 «일관성» 문제 — 문면 1줄이 효과가 있는가(문면은 확률적 · B 기각으로 mypy 결정 실행은 없음). 표본 외(kkebi) 발생 유무.
- D-2 착지 자리(§4.4 vs §1.2 vs §15)와 문장이 기존 «예외 우선» 문단·OHS «부재·거절은 답» 경계 단서와 모순 없는가. `sys.exit` 까지 포함하는 문면이 dddjango 산출물(웹 서비스 · CLI 없음)에 과잉인가.
- E-1 «시그니처 `Any` 0 무조건» 이 실코드에서 지킬 수 있는가 — spring application `Any` 0 이 «레인이 이미 안 쓴다» 인지 «쓸 자리가 없었다» 인지. Django/ninja 프레임워크 미러(`clean() -> dict[str, Any]` · `request.user` · `**kwargs: Any` 오버라이드 · `Callable[..., Any]` 데코레이터)에서 `Any` 없이 mypy strict 를 통과하는 대체 형이 항상 존재하는가(`object` 로 바꾸면 상위 시그니처 호환 오류 나는 자리 열거).
- E-2 검사기 확장의 무손실: «명시 `Any`» 규칙이 현재 두 저장소 application 코드에서 몇 건 발화하는가(0 이 아니면 과거 산출물이 red 가 되는 소급 비용) · 제네릭 인자 안 `Any`(`dict[str, Any]`)를 위반으로 볼지 · 조건부 허용(프레임워크 미러)을 검사기가 결정적으로 구분할 수 있는가(못 하면 문면만 조건부·검사기는 시그니처만).
- E-3 규범 정합: §4 «예외 0» 취지 · R-3443 «`object`/`Any` 입력은 경계가 좁힘» · implementation-python 1.12 TypeIs · 12 pydantic strict · 23.1 mypy strict 설정 블록(`disallow_any_*` 언급?)과 새 절이 모순되는가. 아키텍처 예제(Knowledge Level `dict[str, Any]`)는 «예시 면제» 조항으로 커버되는가, 아니면 R-20(생성 모양은 strict 준수) 때문에 교체해야 하는가.
- F-1 «주입 callable ≡ Protocol 시그니처» 가 이미 #85·composition_root 절 문면에 함의돼 있는가(있다면 문면 추가는 중복 · 없다면 결손). 정적 대조로 검출 가능한 형상인가(검사기 후보로 승격할 근거) — 1레인 특이인지(표본 외 kkebi·spring 타 BC 불일치 0 이면 «문면 1줄» 이 적정).
- F-2 «BC 마다 실배선 테스트 1개» 가 implementation-test «매요청 호출 … 테스트 오버라이드 회피» 문면·#389(integration 은 실DB 자리)·#13/#385(타 BC OHS 계약 import 금지)와 정합한가. «1개» 강제가 기존 레인 산출물을 소급 red 로 만드는가(검사기 없음 → 감수자 판단 · 과적합 경계).
- G-1 «채널 전사 결손» 판정이 맞는가 — 블록에 적혔다면 pre-gate 가 #93 을 예보했을 것(실행기 스텁 방출 실측)인가, 아니면 애초 architect 가 «예외 소비 import» 를 블록 대상으로 인식할 문면이 없었는가(규범 문면 해석). 7건 명세 중 블록 밖 예외 소비 import 가 있는 명세 수(≥2 면 일반화).
- G-2 조항 추가의 무손실: 기존 명세 7건이 형식 red 가 되는가(소급 비용) · 예외 «소비」 import 를 블록에 넣으면 pre-gate 가 #93 을 **예보**하는 것이지 **막는** 것이 아니므로 설계 진화(use case 번역)가 그 시점에 일어나는 효과 = Phase 2 왕복 1회 절감 — 과대 추정 여부.
- H-1 캐스케이드 3종(#218/#193/#576)이 «빈 파일 삭제» 에서 결정적으로 발화하는가 — 아니면 카탈로그 레인의 특정 상태(다른 파일이 그 모듈을 import) 때문인가. ⓐ Coordinator 골격 규범이 «첫 슬라이스가 채운다» 로 바뀌면 슬라이스 0 골격 자체(디렉터리·`__init__.py`)와 pre-gate 스텁 실체화가 충돌하는가.
- H-2 ⓑ 검사기 면제는 «빈 모듈 영구 잔존» 을 허용하는가(0바이트 `.py` 실태) · 면제가 다른 규칙(#219 «하나»)의 취지를 약화하는가. ⓐ/ⓑ 외 제3안(빈 파일 대신 `raise NotImplementedError` 골격 / 골격 단계 검사기 스코프 제외)이 무손실인가.
- ⓒ 효과 전체: 5건을 고치면 무엇이 줄어드는가(레인당 왕복·분) — 각 항목의 관측 n(spring 런 · kkebi 런)과 «플러그인이 만든 모양 / 검사가 잡는 누락 / 반복 문면 후보» 분류(현장 보고 «판단 기준 4») 재확인.

## 3·5단계 3축 · 심각도

파트 1 루브릭 준용. 코퍼스 정합 = 건드리는 IRI·검사기·문법 성문 전수 열거(하우스룰 §4 절 신설 시 R-3148~3150 과 관계 명시 · 검사기 확장 시 docstring·registry·rulepack 5표면). 일반화 = Claude/Codex 동일·프로젝트 플래그 비의존·kkebi 대조. 무손실 = 검사기 검출 집합 변화는 «추가만»(E) · 게이트 강도 불변(G 는 예보 확대 · H 는 면제 추가 시 별도 증명).
