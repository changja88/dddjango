# ① 문제 리뷰 — 리뷰어 A(기술 축 — 검사기·실행기·코드 형상) · 현장 보고 수리 2 (2026-09-04)

독립 리뷰. 재실행은 전부 `scratchpad/fr2/rv1A/` 아래 복제본(spring clone @ `d2eaafe` · 조사자 iso/snap 사본 재사용). 두 실서고는 `sed -n`·`find` 읽기만. 아래 «파일:줄» 은 dddjango 저장소 기준(`dddjango/scripts/…`)이 기본이고 실서고는 접두를 붙였다.

## 1. 판정 표

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| D 전제(«플러그인이 만든 모양 아님» · n=2/2저장소) | **검증됨** | 코퍼스 python 펜스 374/377 파싱 · def 862 → 항상-raise ∧ `-> None` **0**(항상-raise 6건은 전부 cleancode 의 `NotImplementedError` 스텁 — `-> Money`/무주석). `NoReturn` 언급 0파일. 조사자 스캔 재실행 jsonl **byte 동일**, 휴리스틱 밖 형상(NoReturn 도우미 호출 종단·`assert False`·`while True`) 보강 스캔 **0** → 누락 없음 |
| D 처방(문면 1줄 · 착지) | **MINOR** | 착지는 §4.4(graph-owned · 예외 우선 + «예외 발생 + 타입 힌트» 예제와 같은 주제)가 맞고 §1.2(Optional — `-> None` 의 뜻이 반대)는 부적합 · §15.1 은 산문 절이라 비용은 싸나 주제(try/except 기계)가 다르다. `sys.exit` 병기는 표준 트리에 CLI 칸이 없어(`standard_tree.py:70-71` cron_job 뿐) dddjango 산출물엔 과잉 — 괄호 부기 이상 두지 않는다 |
| E-1(시그니처 `Any` 0 실현 가능) | **검증됨** | `object` 프로브 재실행: 플러그인 미구성 판 3오류(var-annotated 소음·`unused-ignore`=object 통과·None 처리 arg-type) → **django-stubs 플러그인 구성 후 재실행**(settings.test) 소음 소거·override 호환 오류 **0** 유지 · `Any` 판도 같은 자리 `return-value` → 결론 불변 |
| E-2 소급 비용 «18건 red» | **MAJOR(과대 — 유리한 방향)** | ① `registry_gate._normalize`(:145-147)가 라인번호를 `:N` 으로 지우고 귀속은 N∖L 뿐(runB 헤더 «귀속 0 ≠ 전체 clean») → 기존 18건은 **legacy 잔존(L∩N)·차단 아님**, 브라운필드 레인이 그 시그니처를 다시 손댈 때만 귀속. ② 검사기는 `test/{factories,fake}` 도 검사(MATERIAL_DIRS :79)인데 조사자 집계가 test 플래그로 제외 → 시그니처 bare(별표 포함) 실계수 **spring 8+2 · kkebi 10+4 = 24**(변수까지 넓히면 +4/+15). ③ `fixtures/public_surface` 에 `Any` 0 → 기존 픽스처 red 0 |
| E-2 검사기 결정성(시그니처 무조건 · 변수 조건부) | **검증됨(조건부)** | 자리는 구조적으로 갈린다(시그니처 :211-226 / AnnAssign :265-268 / `self.x` :320-322) → «시그니처만 위반·변수는 ⓓ 후보(exit 불산입 · `findings.Candidates` :361)» 가 결정적. «프레임워크 미러 조건부 허용» 을 변수 자리에서 검사기가 가르려면 값 형상 화이트리스트(`request.user`)뿐 → 비권장 · 문면+ⓓ 로 |
| E 검사기 구현 사각 | **MINOR** | `_annotation_names`(:341-352)는 `_name_of` 라 `from typing import Any as _Any` 별칭 미해소 → `_module_bindings` 경유 필요 · bare 판정은 `Any | None`/`Optional[Any]`/`Union`/문자열 언랩 필요 · `typing.Any`/`t.Any` 는 `_name_of` Attribute 로 공짜 · `TYPE_CHECKING` 분기는 `_module_bindings` 가 `if` 를 걷어 해소 · `cast(Any, …)` 는 애너테이션이 아니라 표면 밖(문면) · `Callable[..., Any]` 데코레이터는 두 저장소 application prod 시그니처 nested 에 **0** (spring dict 39·tuple 1·list 1·ModelAdmin 1 / kkebi dict 12·list 12·tuple 2) — 실증 무영향 · ninja `Schema` 필드 `x: Any`(kkebi `product_observability/.../schema/schema_in.py:25 event_name: Any = Field(...)`)는 선언적 클래스 AnnAssign — «변수=ⓓ» 이면 권고로 남는다(계약 `Any` 를 위반으로 볼지는 ② 결정) |
| F-1(주입 callable ≡ Protocol · 1레인 특이) | **검증됨** | `wiring_audit.py` 재실행: 585c9c6 callable 42 = 일치 40·**불일치 1**(`dependency_wiring.py:48`)·판정불가 1 / 8244190 51 = 49·**1**(`:42`)·1 / HEAD 51 = 50·0·1 / kkebi 48 = 48·0·0. `#85`(`check-composition-root.py:1849-1875`)는 최상단 형태만 — 시그니처 무검사 확인 |
| F 검사기 승격 | **MINOR(승격 근거 박약)** | 표본 99지점 오탐 0 은 정밀하나 사각이 열거 가능(아래 §2 F) — 이 검사는 mypy `[arg-type]` 의 부분 재구현이고 B(mypy 프로젝트 소유) 기각과 정합하려면 문면 1줄이 적정. F-2 «실배선 테스트 1개» 는 약형(patch 인자 밖 `build_*()` 호출 존재)만 결정적이고 «최소 한 경로 실행·fake 경계» 는 판정 불가 → 문면만 |
| G(채널 전사 결손 · 예보/차단) | **검증됨** | runB 재확인 exit 2 · `#93`×2(`port.active_service_bundle.exception`·`port.relation_table.exception`)+`#96`×1. `_IMPORT_ROW_RE`(:171-172)는 행 종류 무제한 · `_parse_imports`(:495-521) → `render_stub`(:785-810) 원문 방출. 차단 모드에서 예보 red = «architect 반송 의무 · G1 배너·dispatch 근거 불가»(`commands/dddjango.md` pre-gate 절) → 블록에 적으면 **G1 에서 반송**되고 use case 번역(`app`→`port` 는 `check-context-isolation.py:243` 분기 · #92 는 driving 잎만)으로 재설계 → 행 제거 → green. **순환 없음(1회 종료)** · 조항 취지 = «적어라 — 그래야 G1 이 드러낸다» |
| G 무손실·효과 | **MINOR(효과 과대)** | 형식 red(exit 3)는 파싱 사유뿐이라 증가 0 · 예보 red 증가는 설계 위반일 때뿐(의도). **사각**: `_parse_imports` 는 `add` 소비자만 스텁 전사(`entry.tag != "add"` → 메모) → 브라운필드 `update` 잎은 행을 적어도 예보 안 됨 — kkebi tarot·billing(이관) 2레인은 조항이 있었어도 무효. 카탈로그 OHS 는 `add`(specA L308) → 실효 1(+리딩 P4 미확인). «5레인» 은 3이 블록 없는 구형 |
| H 재현(존재 5 / 부재 12 서로소) | **검증됨** | rv1A clone 재실행: `59d08c7` #219 2·#635 3·#488 0 / `99253ce` #218 2·#193 3·#576 2·**#488 5**. 캐스케이드 조건은 전부 파일 부재(`port-adapter:211-213` `is_file` · `usecase-dto:342-343` `slot_file is None` · `:1030-1046` rglob stem · `layer-skeleton:238-245`) — import 의존 아님 |
| H ⓐ(Coordinator «첫 슬라이스가 채운다») | **MAJOR(기각)** | 중간 상태 red 5 → 12 로 악화 · R-2499(`agents/coder.md:38`)·#488(houserules final.md:21 + 검사기 메시지 `:245` «비면 빈 파일로 만든다»)·R-3188(final.md:27) 3곳과 정면 충돌. pre-gate 는 격리 사본 스텁이라 저장소 충돌은 없으나 미계획 재등장 칸을 #488/#193/#218 로 예보(리딩 리포트) → architect 가 file-plan 에 올리고 coder 가 만들어야 하는 구조와 모순 |
| H ⓑ(#219/#635 빈 모듈 면제) | **MAJOR(누수 실증)** | 선례 있음 — `checker_target.skeleton_placeholder`(:32-50 · 판정 ④ 2026-08-25 · `plugin-revision-batch-plan.md:19,37` D4/W3)를 #256(domain-model:239)·#351 선언(port-adapter:641)·#114 가 쓴다 → 같은 술어 적용은 «일관» 이고 HEAD `_port.py`/`_use_case.py` 0바이트는 양 저장소 0·픽스처(port_adapter_pairing 0바이트 0 · usecase_dto 0바이트는 `_query.py`/api 뿐)라 검출 집합 변화 = 카탈로그 골격 상태 5→0 뿐. **그러나 누수는 이미 실물**: kkebi tarot 애그리거트 6+`_repository` 6 이 08-25 부터 0바이트인데 `check-domain-model` 을 kkebi 사본에 돌려 tarot 발화 **0**(#256 면제 경로) → 면제 뒤엔 어떤 규칙도 영구 빈 파일을 잡지 못한다(#218/#193/#576/#488 전부 «존재» 로 충족) |
| H ⓒ(골격 슬라이스 게이트 유예 문면) | **권고(무손실)** | registry 게이트는 Phase 2 step 6(G2 직전 · `dddjango.md:151-152,187`)만 규범이고 슬라이스별은 discipline-reviewer 경량(:107)·«수시 실행»(:154) — 슬라이스마다 registry green 을 요구하는 규범 **없음**. 카탈로그 슬라이스 0 red 는 자초(명세 L268 은 `check-layer-skeleton green` 만 요구). 검출 집합 무변 → 무손실은 구성상 성립 · 3레인(promotion-pricing·saju·reading)은 이미 이 방식 |
| H ⓓ(0바이트 한정 면제 + 잔존 규칙) | **MINOR(기각)** | «0바이트» 는 `skeleton_placeholder`(주석·docstring-only 포함)와 다른 제3의 빈-술어 → 판정 ④ 와 불일치. 잔존 규칙은 «아직 안 채움 / 버려짐» 을 시간 없이 못 가른다(형제 파일 내용 유무로 근사 가능하나 골격 슬라이스는 형제도 빈다) → ⓑ 누수로 환원 |
| ⓒ 효과 전체 | **MINOR(과대 — 항목별 §3)** | D 0~1건/저장소(문면 확률) · E 시그니처 bare ≈1/BC(그중 Django 미러 ≈0.7 → `object` 기계 치환) · 변수/nested ≈10/BC 는 문면+ⓓ 영역 · F 1/99 · G 실효 1(+1 미확인) 왕복 · H 1왕복 13m42s(타 3레인 비용 0) |

## 2. 항목별 상세

### D
- 코퍼스 AST(rv1A 실행 · `scan_de.terminates` 재사용): `fences 377 parsed 374 defs 862` → 항상-raise 6 = `discipline-cleancode/references/final.md:929 calculate_pay -> Money`, `:2075 fly`(무주석), `:2137-2140 process/validate/transform/serialize`(무주석) — 전부 `NotImplementedError` 형 인터페이스 스텁, `-> None` 0. 정규식 1차 스캔에서 걸린 4건(`architecture-ddd:502,526,782` · `cleancode:1267`)은 `if cond: raise` 가드(정상 경로 None 반환)라 항상-raise 아님.
- 재실행: `scan_de.py iso/{spring,kkebi} → rv1A/DE/` · `cmp` d/any jsonl 4개 **identical**. 보강 스캔(같은 모듈 NoReturn 도우미 호출 종단 · `assert False` · `while True` 무 break · `pytest.fail/self.fail/parser.error`) spring 0 · kkebi 0.
- 실물: kkebi `payment_processing_adapter.py:366 def _raise_transport_failure(...) -> Never:` · `:437 def _raise_provider_error(` · spring `service_runtime.py:642 def _fail(...) -> NoReturn:`(HEAD 수리됨).
- 착지 비교: §4.4(`implementation-python/references/final.md:629-650`, graph-owned, 경계 단서 «부재·거절은 답» 은 use case 결과 분기 얘기라 «항상 raise 하는 사설 도우미» 와 모순 없음) ⊃ §15.1(:1741-1755 · 산문 절 · try/except 기계) ⊃ §1.2(:33-58 · Optional — «None 반환 가능성 명시» 문맥에 «반환 안 함» 을 끼우면 혼선).

### E
- 재집계(`spring_any.jsonl`/`kkebi_any.jsonl` · application ∧ ¬test): spring 120 = sig-star bare 7 · sig-arg opt 1 · sig nested 42 · var 70(bare 37·nested 33) / kkebi 133 = sig bare 5 · opt 2 · star 3 · sig nested 26 · var 97(bare 61·nested 36). 시그니처 bare 목록 조사자와 동일(spring 8/8 Django 미러 · kkebi 5 미러+5 실질).
- MATERIAL_DIRS 누락분: spring `test/factories` 4(`character_model_factory.py:44`·`product_model_factory.py:29` `**kwargs: Any` + nested 2) · kkebi 15(billing factories `_create(*args, **kwargs)` 4 + fake var-class bare 11).
- 프로브: `rv1A/DE/mypy-obj/mypy_plugin.ini`(strict+plugin+`django_settings_module = spring_dream_server.settings.test`) → `probe.py` 2오류(`unused-ignore` ×1 = object 인자가 Any 매개변수에 통과 · `dict(super().clean())` None 처리 arg-type) · `probe_any.py` 1오류(같은 자리 return-value). 조사자의 «플러그인 미구성» 은 소음(`var-annotated`)만 더했고 결론을 흔들지 않는다.
- 게이트 의미: `registry_gate.py:145-147` `_normalize` = 경로 제거 + 라인번호 `:N` · 귀속 = N∖L. #493 은 auto 검사기라 Coordinator 판정 계열 «auto 위반 red = registry_gate 귀속 차분»(`dddjango.md:187`) → 신규 `Any` 만 차단.

### F
- 재실행 `wiring_audit.py`(rv1A/F/{s585,s8244,shead,khead}.out): callable 범위 판정 = 585c9c6 {일치 40·불일치 1·판정불가 1} · 8244190 {49·1·1} · HEAD {50·0·1} · kkebi {48}. 불일치 detail «주입 함수 필수 인자 미공급: data_root,embedder» · 판정불가 = chat_relay `:213` 팩토리 내부 지역 대입 `runtime.get_start_turn_persistence_factory()`.
- 검사기화 사각 열거: ① 런타임 값(팩토리 반환·인스턴스 메서드 — 1/51) ② `Callable[..., R]` 생략 부호(대조 불가) ③ `__call__` 없는 Protocol/클래스 수신에 함수 주입(스크립트는 불일치로 판정 — 인스턴스 주입과 구분 못 하면 오탐) ④ 중첩 `partial`·클로저·기본값 있는 lambda ⑤ 상속된 `__call__`·제네릭 Protocol·타 모듈 TypeAlias ⑥ 서드파티 구현(`rdflib`) 해소 불가 ⑦ `**kwargs` 수용 구현(무조건 일치 처리) ⑧ 시그니처를 바꾸는 데코레이터·`@overload` ⑨ 위치/키워드 사상. 전부 mypy 가 이미 다루는 영역 — 검사기 신설은 «고정밀·저-recall» 가족(`check-composition-root.py:1-40` 헤더) 안에서 recall 을 스스로 좁혀야 하고 n=1.
- F-2 약형 검사(patch 인자 밖 `build_*()` 호출 ≥1 · `test_audit.py` 판형): 기존 BC 는 앵커에도 부재라 legacy 잔존(귀속 0) · 신규 BC 만 귀속 → 소급 red 0. 그러나 «실행 1경로·LLM 만 fake» 는 판정 불가(자기 BC fake 포트 vs 전부 fake 를 못 가름 — #13/#385 로 타 BC OHS 대신 fake 를 쓰는 판형이 곧 «전부 fake» 와 형태가 같다) → 검사기는 형식적 충족(팩토리만 호출)을 막지 못한다.

### G
- `design_pregate.py:2` «차단 모드» · `:73` exit 2 = 예보 red · `:122 MODE = "enforce"` · `:1527-1528` S3 문면. Coordinator: «red 는 architect 반송 의무이며, red 인 최종본은 G1/G1′ 배너·무배너 재승인·Phase 2 슬라이스 dispatch 어느 것의 근거도 될 수 없다».
- 순환 검토: 조항 → architect 가 잎→port 행 기재 → pre-gate #93/#96 red → 반송 → use case 번역으로 재설계(use case→port 는 적법: `check-context-isolation.py:243` `loc in ("app","app_port")` 분기 · #92 는 `driving_layer/` 잎 주어) → 행 삭제 → green. 반대로 «적지 않음» 은 현재와 같음(S3 사각). 따라서 조항은 «허용» 이 아니라 «전사 의무» 로 써야 하고, 실효는 architect 가 잎 catch 를 설계할 때만.
- 사각(신규): `_parse_imports:517-519` `entry.tag != "add"` → 스텁 미전사(실존 판정만). 브라운필드 잎(`update`)은 조항이 있어도 예보 밖 — S3 문면에 «add 소비자만 전사» 를 같이 적어야 정직하다. 카탈로그 G1 OHS 는 `add`(`specA.md:308`).
- 실존 판정 부작용 0: runB «자기 add 해소 2» — 같은 명세가 add 하는 `port/**/exception.py` 라 결손 아님.

### H
- 재실행(`run_rules.py <commit> dddjango/scripts rv1A/H/spring rv1A/H/out` · `ONLY` 3종): `59d08c7 records=204 #219 2 #635 3 #218/#193/#576 0` · `99253ce records=211 #219/#635 0 #218 2 #193 3 #576 2` · `99253ce.log` `[#488]`∧fortune_catalog **5**. 조사자 표와 동일.
- 조건 코드: `check-port-adapter-pairing.py:211-213`(#218 `is_file`) · `:245-247`(#219 `len(classes) != 1`) · `:1030-1046`(#576 `decl_stems` rglob) · `check-usecase-dto-placement.py:342-343`(#193) · `:383-385`(#635) · `check-layer-skeleton.py:238-245`(#488) · `standard_tree.py:78,84` reappear. `registry_gate.py` 에 #487 조기 중단 grep 0.
- 선례·누수: `checker_target.skeleton_placeholder`(:32-50) 사용처 `check-domain-model.py:239`(#256) · `check-port-adapter-pairing.py:641`(#351 선언) · `check-error-centralization.py:717`(#114). kkebi 사본 `check-domain-model.py` 실행: exit 2 · 위반 2(tarot 무관) · tarot 0바이트 12파일(`domain_layer/tarot_{spread,prompt_definition,category,topic,prompt_backup,card}/{<agg>.py,<agg>_repository.py}`) 발화 **0**.
- 게이트 시점: `commands/dddjango.md:106-108`(슬라이스마다 coder · ≥3 이면 reviewer 경량) · `:151-152`(step 6 registry) · `:154`(«수시 실행» 은 재생성 루프 옵션 문맥) · `:187`(G2 직전 step 6 적용). `agents/coder.md:46-47`(래칫은 pytest BC 범위 · «좁힌 부분 실행 green 은 게이트 증거 아님»).

## 3. ⓒ 효과 — 항목별 관측 n · 과대 지적

| 항목 | 관측 n | 고치면 줄어드는 것 | 과대 여부 |
|---|---|---|---|
| D | 2(spring 1 · 사후 수리됨 / kkebi 1 · 같은 파일에 `-> Never` 공존) | 프로젝트 mypy 실행 시 `possibly-undefined` 증폭(13) — 플러그인 측은 0 | 문면 확률 · «지식 부재» 아님(정상 사용 7) |
| E | 시그니처 bare 8/11 BC · 10/10 BC ≈ 1/BC(미러 ≈0.7) · 변수/nested ≈10/BC | 시그니처 차단은 ≈1/BC · 실질 세탁(kkebi 5)은 잡힘 · 변수 `request.user`·JSON 순회는 ⓓ+문면 | «Any 0» 의 90% 는 검사기 밖(변수·nested) |
| F | 1/99 지점 · 실배선 부재 21/28 BC | 프로덕션 TypeError 1급 · 문면 효과 확률 | 검사기 승격 근거 n=1 |
| G | 명세 2(명시 1·암묵 1) · 발화 5레인(구형 3) | greenfield `add` 잎에서 Phase 2 왕복 1(카탈로그 S4) · 리딩 P4 부분 | `update` 잎·구형 3 은 무효 → 실효 1~2 |
| H | 삭제 왕복 1레인 13m42s · pre-content red 4런 | ⓒ 문면: 오독 레인의 14분 · ⓑ: +3런 소음 5~9행(누수 대가) | 3런은 비용 0 이었음 |

## 4. 범위 권고

- **D 유지(축소)** — §4.4 불릿 1줄(ttl 개정) 또는 §15.1 산문 1줄(LEDGER 재기준선) 중 택일 · `sys.exit` 는 괄호 부기까지만 · 검사기 없음.
- **E 유지(형상 확정)** — 검사기: **시그니처 bare `Any`(별표·`| None`·`Optional`·문자열·별칭 포함) = 위반** / **nested·변수 자리 = ⓓ 후보** · 선언적 클래스 필드 `Any` 는 ② 결정 · 문면은 `*args: object, **kwargs: object` 명시 · «소급 18» 은 legacy 잔존으로 정정(차단 0 · 실계수 24).
- **F 축소** — F-1 문면 1줄(implementation-django-ninja §2.3 · R-0719 계열) · F-2 문면 1줄(implementation-test) · 검사기 승격·약형 검사 **기각**.
- **G 유지(문면 정렬)** — R-3427 «경계» 정의를 «검사기(#92~#96)가 판정하는 층 경계 import — BC 내부 포함» 으로 정렬 + S3 에 «add 소비자만 전사» 병기 · 실행기 무접촉.
- **H ⓒ 채택 · ⓐ/ⓑ/ⓓ 기각** — Coordinator/coder 문면 «슬라이스 중간 #219/#635 는 pre-content 잔존(G2 전 해소) · 빈 파일 삭제로 해소 금지(#488)» · 검사기 무변. ⓑ 를 택한다면 `skeleton_placeholder` 재사용이 유일한 일관 형태이나 tarot 12파일 누수를 먼저 갚아야 한다.

## 5. 미확인

- 리딩 P4 잎(controller/OHS)의 file-plan 태그(`add`/`update`) — 조항 실효 1→2 판정에 필요(`919440c` 명세 미열람).
- ⓑ 채택 시 `fixture_matrix.py` EXPECTED 계수 변화(0바이트 `_port.py`/`_use_case.py` 픽스처는 없음을 확인했으나 골든 계수 파일은 미열람).
- kkebi `web/`·`scripts/` 의 #493 기준선 173 이 새 `Any` 규칙에서 legacy 로 남는 범위(레인 밖이라 미집계).
- F 검사기 사각 ③(무-`__call__` Protocol 수신 + 인스턴스 주입)의 실제 오탐 여부 — 표본에 해당 형상 0.
- E 문면(E-3 규범 정합·R-20·Knowledge Level 예제)은 B 축.
