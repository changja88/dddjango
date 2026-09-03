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

### H — pre-content 골격 «빈 파일 실체화» vs «클래스 하나» 상충 (실측 2026-09-04)

- **검사기 조건**(dev main = 설치본 2.17.16 byte 동일 · `7f695bb` 08-12 이후 무변경): 빈 파일 **존재** 시 발화 = #219(`check-port-adapter-pairing.py:245~247` 공개 클래스 ≠1) · #635(`check-usecase-dto-placement.py:383~385`). 파일 **부재** 시 발화 = #218(port-adapter 211~213) · #193(usecase-dto 342~343) · #576(port-adapter 1030~1046 fake stem) · **추가 발견 #488**(`check-layer-skeleton.py:238~245` — `_use_case.py`·`_port.py` 는 `standard_tree` reappear(고정) 칸이라 부재 시 «비면 빈 파일로 만든다» 메시지).
- **결정적 재현**(격리 복제본 · 카탈로그 BC 귀속 · dev/설치본 차이 0): `59d08c7` 빈 5파일 → #219 2·#635 3(계 5) / `99253ce` 제거 → #218 2·#193 3·#576 2·#488 5(계 12) / `9c8814e` 복원 → 5. 수동 rm·빈 재생성·`# placeholder` 1줄 도 동일하게 갈림. **두 집합은 서로소이고 위반 0 상태는 «클래스 하나가 든 파일» 뿐** → pre-content 골격은 어떤 상태로도 green 이 될 수 없다(플러그인 규칙 간 상충 확정). 왕복 비용 13:55:30 → 14:05:40 → 14:09:12 = **13분 42초** ✓.
- **표본 외**: «0바이트 add→delete→add» 왕복은 spring 5경로(전부 카탈로그) · kkebi 0 → **삭제 왕복은 1레인 유일**. 그러나 pre-content #219/#635 발화 자체는 **4레인/2저장소 반복**: spring promotion-pricing(08-31 review-s2-r2 #219×2·#635×4 — «time-phased skeleton» 으로 수용) · spring fortune-reading(pre-gate 예보 #219·#576×3·#635·#488×2·#193 → 설계 교정) · kkebi saju-chart-engine(08-23 S1 조기 red #219×2+#635×3 — 잔존 허용 후 S2 해소) · 카탈로그.
- **규범 문면**: Coordinator `commands/dddjango.md` 에 골격 실체화·빈 파일·pre-content 문면 **0건**(105행 «슬라이스 0» 은 리팩터링 빚 슬라이스). 빈 파일의 근거 = `agents/coder.md:38`(graph-owned) **R-2499** «고정·재등장 칸은 내용이 없어도 … 빈 파일로 만든다(#488)» · 하우스룰 final.md 21·24·27 #488·#491·**R-3188/R-3189** «빈 채로라도 실현». 카탈로그의 빈 파일은 architect 명세 L268 «슬라이스 0 — 골격 … 빈 파일 … check-layer-skeleton green» → coder R-2499 집행(pre-gate 스텁 아님).
- **ⓐ/ⓑ 재료**: ⓐ(Coordinator «첫 슬라이스가 채운다»)는 부재 상태에서 #488×5+#218×2+#193×3+#576×2 가 결정 발화 → Coordinator 문면만이 아니라 **R-2499·R-3188·#488 코드 메시지와 정면 충돌(3곳 동시 개정)**. ⓑ(#219/#635 빈 모듈 면제)의 위험 = «하나» 검사가 없는 칸은 실제로 비어 남는다: HEAD 0바이트 `.py`(`__init__` 제외) spring 113(허용 칸 112 + `translation_controller.py` 1) · kkebi 168(허용 칸 151 + **tarot domain 12 — 애그리거트 6·`_repository` 6, 08-25 부터 10일째** + controller 4). `registry_gate.py` 에 #487 조기 중단 없음(27종 전수 실행).
- **판단 재료**: 상충은 플러그인 내부 규칙 간 모순(«빈 채로라도 실현» ↔ «있으면 하나»)으로 확정, 재현 결정적. 문제의 본질은 «pre-content 상태를 게이트가 언제 보는가» — promotion-pricing·saju 레인은 red 를 «time-phased» 로 수용했고 카탈로그만 삭제로 대응. 처방은 ⓐ/ⓑ 외에 ⓒ «골격 슬라이스는 게이트 대상 아님(첫 내용 슬라이스와 함께 판정)» 문면·ⓓ #219/#635 를 0바이트 한정 면제 + 잔존 빈 파일은 별도 규칙(#488 반대 방향)으로 잡기 등을 ① 이 비교해야 한다. 미측정: «lane 6» 정의(발주서에 없음 — ledger 는 레인 4) · 각 레인의 red 수용이 게이트 통과에 어떻게 기록됐는지.

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

## 1단계 결과 (2026-09-04 — 적대 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-2/rv1/`)

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| D 결손 | **검증됨(소)** | 코퍼스 `NoReturn` 0 · `-> None` raise 예제 0(펜스 374·def 862 재검). 형상 n=2/2저장소이나 **효과 n=1**(kkebi 건은 호출부 문장 위치라 mypy 증폭 0) · 두 레인 모두 Codex·동일 작성자·1건은 framework 경로(표식 없음) → 기준 4 «≥2레인» 에 걸침(C MAJOR: 독립성 약함) |
| D 처방 | MINOR | 착지 implementation-python §4.4(`s032-4.4`) 새 블록 b3 · Obligation 1문장 · `sys.exit` 삭제(트리에 CLI 칸 없음 — 과잉). 우선순위 최하 |
| E 결손 | **검증됨** | R-3148 은 «주석 존재» 규범 → `x: Any` 로 충족. 막는 도구 부재(ANN401 무효·`disallow_any_explicit` 없음·mypy 범위 `application/` 제외) 실증 |
| E 조건부형 | **MAJOR(자기모순)** | «프레임워크 미러 자리 조건부 허용» 은 R-3150(조건부 면제 금지)과 충돌 · `object` 대체 프로브(django-stubs 플러그인 구성 후 재실행 · override 오류 0) → «불가능» 이 아니므로 **문면은 무조건형만 정합** |
| E 검사기 형상 | **검증됨(조건부)** | 자리가 구조적으로 갈림(시그니처 211~226 / AnnAssign 265~268 / `self.x` 320~322) → **시그니처 bare `Any`(별표·`\| None`·`Optional`·문자열·별칭 포함) = 위반(exit 2) · 변수·제네릭 안 = ⓓ 후보(exit 불산입)** 가 결정적. 변수 자리의 «미러» 구분은 값 형상 화이트리스트뿐이라 비권장 → 문면+ⓓ. 사각 정정: `_annotation_names` 는 별칭 미해소 → `_module_bindings` 경유 · ninja `Schema` 필드 `x: Any` 취급은 ② 결정 |
| E 소급 «18 red» | **MAJOR(과대)** | `registry_gate` 는 N∖L 귀속이라 legacy 잔존 차단 0 · 검사기가 `test/{factories,fake}` 도 보므로 실계수 24. 강도표(C · application 프로덕션): ① 시그니처 bare 0 = spring 8/kkebi 10(전부 치환 가능) · ② +변수 = 45/71(ninja Schema 필드 3 면제 결정 필요) · ③ +제네릭 안 = 120/133(Django `clean()` 미러 다수) → **① 채택 · ② 문면+ⓓ · ③ 기각** |
| E 착지·표면 | MINOR | §4.2 신설보다 `s007-4` 새 블록 b7 · Work 2(R-3446 정책·R-3447 검사기 규칙) · `#644` 규칙 번호 후보 · 표면 7(검사기 docstring·registry 소개·rulepack·하우스룰 문면·픽스처 good/bad·codex 미러·Coordinator 133행) · 23.1 mypy 블록 무접촉 · Knowledge Level 예제 치환은 선택 |
| F-1 | MINOR(문면 조건) | 1레인·기준 4 미충족이나 정적 검출 실증(불일치 1→0). #85 는 **최상단 `Assign` 도 red** → 문면은 «`build_*()` 본문 안에서 `partial`/클로저» 명시 필수. 검사기 승격 기각(사각 9종·mypy arg-type 부분 재구현·n=1) → R-0719 따름정리 **1문장** |
| F-2 «BC 마다 1개» | **MAJOR(기각→축소형)** | discipline-tdd §5.5 quota 비자격·design-review-api «decision 없이 의무화 금지»·coder :37 과 3중 모순 · 착지 implementation-test 는 소유 오류(§5.5 소유) · 실배선 있는 BC 는 엄격 기준 3/16(+부분 1) · «26곳» 미재현(후보 11/16/21/22 모두 아님) → **discipline-tdd §5.5 «보호 대상» 1항**(composition root 실배선 1경로 = 보호 대상 후보 · 강제·소급 없음) · design-review 항목 추가 기각 |
| G 결손 | **검증됨** | R-3427 «경계» 미정의·열거 전부 BC 밖 → «잎→port 는 경계 아님» 독법 자연. 잎→port 행 블록 0/7 · #93 실발화 5레인(블록 보유 2 = 조항 실효 n, 블록 없는 3 = 패턴 n) · 실행기 예보 성립(runB exit 2 재확인) · 차단 모드 red = G1 반송 → 1회 재설계로 종료(순환 없음) |
| G 형태 | **MAJOR(범위)** | «예외 소비 import» 한정 = #93 정의(`port/**` 전체)와 부정합 · «층 경계 전부» = 과광 → 정합형 = **R-3427 clarification(경계 3분류: BC 밖 / BC 내부 층 경계 중 #92~#96 판정 대상 = 블록 의무 / 그 밖 재량)** + **architecture-ddd «port 예외 번역 책임 = use case» Work 1 신설**(≥4레인 재유도 방지) + S3 «add 소비자만 전사(브라운필드 update 잎 무효)» 병기 |
| G 효과 | MINOR(과대) | «Phase 2 왕복 1회 절감» 아님 — 카탈로그 STOP 0·리딩 STOP-149 중 12/149 → **«예보 시점이 Phase 2 → G1 로 이동»** 으로 정직화. 실효 1~2레인 |
| H 재현 | **검증됨** | 존재 5행 / 부재 12행 서로소(A·C 재실행 동일) · 13:42(게이트 red 2회 = 파일 왕복 1회) |
| H «모순» 전제 | **MAJOR(과장)** | «하나»(#219/#635)는 **Work 0**(검사기 docstring·원장뿐) · 그래프 규범은 «빈 파일 실현» 만 말함 → 시점 차이로 양립. 진짜 결손 = «빈 파일 실현 상태에서 내용 규칙이 언제 서는가» 미성문. **R-0319 가 registry #2 한정으로 이미 pre-content 유예 선례** · R-3425 `empty` 태그(적법 계획)인데 pre-gate 스텁이 #219/#635 예보 red(리딩 pregate-report) = 같은 불일치 |
| H ⓐ | **MAJOR(기각)** | 부재 상태 red 5→12 · R-2499·R-3181·R-3188 redefinition + #488 메시지 + `empty` 의미 재정의(최대) |
| H ⓑ | **MAJOR(누수)** | `skeleton_placeholder` 선례(판정 ④)와 일관하나 순수 면제는 영구 잔존을 못 잡음. 단 C 정정: kkebi tarot «10일째» 는 과대(저장소 마지막 커밋 08-26 → ≈27h) · 그 칸엔 «하나» 규칙 자체가 없음 → ⓑ 기각 근거로 부적합 |
| H ⓒ(골격 슬라이스 유예 문면) | A 권고 / B «단독 부족» | 슬라이스별 registry green 규범 없음(G2 step 6 만) · 3레인(promotion-pricing·saju·reading)이 이미 이 방식 · 검출 집합 무변. 그러나 문면만으로는 검사기·pre-gate 스텁의 red 를 못 막음(`empty` 계획이 매번 귀속 red → 처분 필요) |
| H ⓓ(검사기 유예 + 형제-내용 조건 + R-3181 clarification) | B 권고 / A «0바이트 술어» 기각 | A 의 기각 사유(제3의 빈-술어)는 **`skeleton_placeholder` 재사용으로 해소** · «잔존은 시간 비인지» 는 «같은 칸 형제 파일에 내용이 있으면 발화» 가 결정적 대리 · 검출 집합 변화 = pre-content 상태만(HEAD 양 저장소 0바이트 `_port/_use_case` 0 · 픽스처 0 · 카탈로그 골격 5→0) → ⑤ 무손실 증명 가능 |
| ⓒ 효과 전체 | MINOR(과대) | D 0~1건/저장소(확률) · E 시그니처 ≈1/BC(실질 세탁 kkebi 5 검출) · F 1/99 · G 실효 1~2 · H 1왕복 13m42s(타 3레인 비용 0) |

### ① 결론 (결정 게이트 «범위 확정» 상신)

- 합의(사용자 결정 불요): **D** 유지·축소(§4.4 b3 1문장 · `sys.exit` 삭제) · **F-1** 축소(R-0719 따름정리 1문장 · «`build_*()` 본문 안 partial») · **F-2** 축소형(discipline-tdd §5.5 보호 대상 1항 · 강제·소급 없음 · implementation-test 착지 철회) · **G** 재형식화(R-3427 clarification 경계 3분류 + architecture-ddd 번역 책임 Work 1 + S3 병기) · 현장 보고 «수정 우선순위» 문면(`discipline-test` 스킬 부재·«26곳»·«13건»·«47/0») 정정 추기.
- 갈림 1 — **E 검사기 차단 범위**: ① 시그니처 bare `Any` 만 차단 + 변수·제네릭 안은 ⓓ 후보(리뷰 3기 공통 권고) / ② 문면만 / ③ 변수까지 차단(소급 45/71 · 기각).
- 갈림 2 — **H 처방**: ⓒ 문면만(A) / ⓓ 검사기 유예(`skeleton_placeholder` 한정 · 형제-내용 발화 · R-3181 clarification · B) / ⓒ+ⓓ 병행(코디 추천 — 문면은 «삭제로 해소 금지», 검사기는 내용 생길 때까지 침묵).
