# rv1-C — ① 문제 리뷰 · 리뷰어 C(증거·표본 외 축 — 수치 재검증·일반화·효과·소급 비용) · 2026-09-04

독립 재계산. 실서고 두 곳은 읽지 않았고 격리 사본 `$S/fr3/{spring(7bfe1aa)·spring-d2eaafe·spring-c20f525·spring-f5ee428·kkebi(6608fb0)}` 에서만 실행했다. 조사자 스크립트(`inventory.py`·`proto_647.py`·`proto_ninja3.py`)는 쓰지 않고 자체 스크립트 3종(`$S/rv1C/s1_count.py`·`s4_647.py`·`s5_count.py` — import 바인딩 → dotted 복원 · TYPE_CHECKING 분기 별칭/중간 ClassDef 추적 · 주석 Subscript 값 자리 판정 · `Status` 항 계수)으로 재계수했다. mypy 는 spring venv 인터프리터를 사본 cwd 로(c20f525 훅 범위 1회 33s · kkebi 상자 둘 BC 1회 10s), 검사기·`registry_gate` 는 dddjango 저장소의 dev 스크립트를 사본 클론(`$S/rv1C/spring-gate`)에서. 산출은 전부 `$S/rv1C/`(jsonl·txt). Serena: skipped — 리서치·재계산 작업(코드 수정 없음).

## 1. 판정 표

| # | 조사자·확정 방향의 주장 | 판정 | 재계산 근거(요약) |
|---|---|---|---|
| C-1 | S-1-1 수치: spring d2eaafe 39클래스(맨몸 13·ignore 17+속성 1·별칭 9) · HEAD 0/17/22 · kkebi 67(ignore 21·별칭 31·TC 중간 ClassDef 15) · BC 10 · CBV 0 | **검증됨** | `s1_count.py` 독립 재계수 전항 일치(§2 표). 기저별 spring ModelAdmin 18·ModelForm 15·TabularInline 4·StackedInline 1·BaseInlineFormSet 1 ✓ · kkebi ModelAdmin 48(+TC 15)·ModelForm 3·TabularInline 1 ✓. CBV(`--cbv` · application+framework+web) 양 저장소 0 ✓. code 없는 `# type: ignore` 헤더 0 |
| C-2 | S-1-1 «플러그인이 만든 모양»(django-web :208 맨몸 예시 → 레인 ①) | **MINOR(근거 «중간» — 예시 모양 일치 + §6 열람 흔적, 예시 참조 흔적 없음)** | `$S/spring/.dddjango/20260830-0029-fortune-character/design-spec.md:362` 가 «implementation-django-web §6 검증 순서·§11 «출처 분류»» 를 인용 — 스킬 로드·**§6(예시 :208 이 있는 절) 열람 흔적 ✓** · `ArticleForm`/`:208` 참조 ✗ · lane-report·slice-plan 에 스킬 언급 0. 같은 날·같은 런타임(Claude — 두 레인 md 모두 `.claude/plugins` 1·`.codex` 0)의 service_policy 레인은 ③ → 예시가 모양을 «결정»했다는 증거는 없다. ② ignore 17(8 BC)은 예시 모양이 아니라 mypy 메시지 대응 모양이라 «검사가 못 잡는 반복»이 정확한 분류(§5 재분류표) |
| C-3 | S-1 소급: #646 수정 1(별칭 3모양 통과·클래스당 1건) 기준 legacy spring 17·kkebi 21 · 앵커 차분으로 격리 · 브라운필드 귀속 비용 | **검증됨(격리) · MINOR(브라운필드 «0» 은 메시지 문구 설계에 달림)** | 수정 1 기준 발화 spring **18**(17 클래스 + accounts panel.py:83 속성줄 1)/16 파일/8 BC · kkebi **21**/21 파일/4 BC(`s1_*.jsonl`). `registry_gate` 4회(§4): run1 anchor HEAD~1 → 귀속 0·legacy 2,676 · run2 legacy 위반 파일 첫 줄에 주석 삽입(줄 밀림) → 귀속 0 · run4 legacy 위반 심볼 개명(`view_box`→`view_box_rv1c`) → **귀속 1**(`[#493] …:N: 지역 변수 \`view_box_rv1c\` …`)·해소 2·exit 2 — 메시지 문구에 이름이 들어가면 개명이 곧 귀속. 브라운필드 실측: spring ignore 파일 16 중 **9 파일이 생성 후 5일 안에 11 커밋으로 수정**(레인 커밋 3: `f750454` accounts-1 S1 · `a4275f7` fortune-intent · `193e82c` promotion S5 · 나머지는 ruff format·docs·mypy 상환) · kkebi 0(저장소 휴면 08-26 이후). 귀속은 클래스 헤더 문구(클래스명·기저)가 바뀔 때만 — run4 실증 |
| C-4 | S-4-1 수치 1,110/828/281 · mypy 124(P1 61+P2 9=70) | **검증됨** | 보고자 grep 그대로 재실행 1,110/828/281 · BC 분포 16 BC 일치 · kkebi 431(object 399 : Any 55 줄) · `mypy application framework spring_dream_server`(c20f525 · 33s) 124 errors/25 files · 코드별 arg-type 29·misc 21·attr-defined 20·call-overload 16·no-any-return 9 ✓(`mypy_c20f525.txt`) |
| C-5 | S-4-1 «P1 뿌리 = 속성·반환 누수»(수정 1 «선»의 근거) | **MAJOR(부분 참 — 61건 중 #647 차단 18(+상류 4) · ⓓ 13 · #647 표면 밖 30)** | §3 표. 즉시 뿌리 (a) 클래스 속성 16 · (b) 함수 반환 21 · (c) 매개변수 5 · (d) 지역 변수 19. 그러나 반환 21 중 **19 가 `_load_controls(...) -> tuple[object, object, object]`**(cli.py:44 · `plan.rag_id`·`run_c0N(profile=…)` 19건)라 dict/Mapping 만 보는 #647 표면 밖이고, (d) 19 중 10 은 **무주석 dict 리터럴 추론**(mypy 만 본다). 결정표 6행(«자리표시 `object` 금지»)은 검사기 없이 문면만 남는다 — «선» 자체는 맞되 «P1 뿌리를 차단으로 잡는다»는 36% 명제 |
| C-6 | S-4 ⓒ 효과 «mypy 빚 70 감소» | **MAJOR(효과 과대 — 레인 귀속 3/70)** | P1 61+P2 9 의 파일 영역: `framework/technology/rag/runtime` **67**(P1 58·P2 9) · application 2(rfc8785_adapter 74·99) · framework/pydantic 1(cited_answer_schema 71) — 뒤 3건은 fortune-reading 레인 `8216c78`. RAG 런타임은 레인 산출이 아니다: 커밋 85 중 dddjango 표식 0 · openai-rag 레인 `introduced.json` 에 rag runtime 경로 0 · 그 레인 design-spec:18 «`framework/technology/rag/runtime/`는 … 기술 영역 … 이 기술 루트에 넣으면 변경 이유가 섞인다». 발주측 상환 모양(TypedDict 2→19·TypeAdapter 0→5·JsonValue 38→67 · git grep 재확인)도 발주측 RAG 작업 |
| C-7 | S-4 소급 #647(수정 1) 건수·BC별·«정당해 보이는 반환/속성» 대체 주석 | **검증됨(수치 −5% · 테스트 factories 제외 차) · MINOR(대체 «주석»은 전부 있으나 좁히기 도우미 19곳은 «재구성»)** | `s4_647.py`: spring HEAD 차단 **702줄**(Any 631·object 반환 57·속성 14 — app 136·fw 566) · ⓓ 272(app 111·fw 161) · kkebi app+fw 차단 165(Any 54·반환 59·속성 52)·ⓓ 264 · `Form.clean -> dict[str, Any]` spring 15·kkebi 3(수정 1 면제는 `object` 만 — 이 15 는 차단(Any) legacy) · union 값 변종 kkebi 2. 표본 12(§4-b): TypedDict 대체 6 · `JsonValue`/`Mapping[str, JsonValue]` 4 · Protocol 미러 2(`dict[str, Any]` 구현과 호환) — 대체 없음 0. 단 «좁히기 도우미 반환»(`_mapping(value: object) -> dict[str, object]` 류) spring 6·kkebi 13 은 주석 교체가 아니라 `TypeIs` 반환(면제)+호출부 ⓓ 또는 `TypeAdapter` 로 재구성해야 한다 |
| C-8 | S-4 kkebi 일반화 — R-3448 형상 지배 저장소에서 수정 1 의 «ⓓ 잡음» | **MAJOR(ⓓ 채널에 앵커 격리가 없다 — 설계 미정)** | kkebi ⓓ(object 매개변수·변수) **264줄**(billing 127·product_observability 30·tarot 27·identity 26·saju 21·notification 13·daily 12) · web/scripts 포함 446. `registry_gate._FINDING_RE = ^\s*(\[#\d+\].*)$` 는 `[ⓓ#…]` 를 파싱하지 않아 ⓓ 는 N∖L 밖 → R-0284 «해당 범위 실행분» 동봉이 루트 실행이면 billing 갱신 레인 감수자가 127건을 매번 본다(spring llm_access 37·fortune_reading 25) |
| C-9 | S-5-1 상자 둘 13·RootModel 단독·#63 red·«08-25 이후 4레인 반복»·리딩 G2 auto | **검증됨** | `s5_count.py`: 상자 둘 f5ee428 8(accounts 6·fortune_record 1·fortune_reading 1)·HEAD 7·kkebi 6(identity 2·review 2·saju 2) ✓ · RootModel 단독 spring fortune_intent ACL 4(+HEAD schema_out 1)·kkebi tarot `TarotCardOut` 1 ✓ · Schema+RootModel f5ee428 1/HEAD 0/kkebi 0 ✓. `check-openapi-error-declaration.py --error-profile dddjango-code-json --scope-bc fortune_reading --error-bc fortune_reading …` f5ee428·HEAD **exit 2 · #63 2건**(400·503) · `auto` exit 0·0건 ✓. `refactor-scope.md` 5행 «Error profile: `auto`» · 15행 registry 5 `… --error-profile auto` exit 0 ✓. 도입 커밋(`git log -S'] | Status['`): spring accounts `06346ff`(08-30)·fortune_record `eda6b96`(08-30)·fortune_reading `585c9c6`(09-03) · kkebi review `fb14fa2`(08-25)·saju `65c1ffd`(08-26)·identity `cb3f4ad`(08-24)·web_session `c2b2bfd`(08-25) → 08-25 이후 **5 레인**(조사자 «4 이상» ✓). 런타임: Claude 4(accounts·fortune_record·review·saju)·Codex 2(fortune_reading·identity)·미상 1 — 런타임 무관. kkebi 상자 둘 BC mypy 재실행 **Success 338 files** ✓ |
| C-10 | ⓒ 효과 전체(레인당 왕복·mypy 빚·ⓓ 처리) | **MINOR(왕복 절감 0 · mypy 절감은 S-1 26/1레인·S-5 9/1레인·S-4 3/70 — «예방» 으로 정직화)** | §5 |

## 2. 수치 재검증 표 (조사자 vs C)

| 항목 | 조사자 | C 독립 재계수 | 일치 | 방법 |
|---|---|---|---|---|
| S-1 spring d2eaafe 클래스 · ①/②/③/④ | 39 · 13/17/9/0 · 속성줄 1 | **39 · 13/17/9/0 · 속성줄 1** | ✓ | `s1_count.py spring-d2eaafe` |
| S-1 spring HEAD | 39 · 0/17/22/0 | **39 · 0/17/22/0** | ✓ | 〃 |
| S-1 kkebi | 67 = 21 ignore·31 alias·15 TC | **52 런타임(0/21/31/0) + TC 중간 ClassDef 15 = 67** | ✓ | 〃(TC 중간 클래스를 런타임 표에서 분리) |
| S-1 BC 수 · 위반 파일 | 10 · — | 10 · spring 위반 파일 d2eaafe 25 → HEAD 16 · kkebi 21 | ✓ | 〃 |
| S-1 CBV 상속 | 0 | 0(application·framework·web · `View`/`TemplateView`/`RedirectView` 제외) | ✓ | `--cbv` |
| S-1 monkeypatch·별칭 블록 규모 | (파일당 8줄) | 별칭 블록 6줄/기저(service_policy panel.py:35~40) · `if TYPE_CHECKING:` 파일 spring admin 18·kkebi admin 30 | — | grep |
| S-4 grep 1,110/828/281 · BC 분포 | 1,110/828/281 | **1,110/828/281** · fortune_reading 59…accounts 1 전 BC 일치 | ✓ | 보고자 명령 |
| S-4 kkebi grep | 431 | **431**(object 399 : Any 55 줄) | ✓ | 〃 |
| S-4 mypy c20f525 훅 범위 | 124 · P1 61·P2 9 | **124 · 25 files** · 대장 P1a 17·b 18·c 11·d 11·e 4·P2 9 = 70 좌표 전부 소스와 대응 | ✓ | mypy 1회 · `p1_ctx.py` |
| S-4 #647 시제품 exact 히트(spring HEAD) | 1,061 히트/848 줄 · object 395 : Any 666 · class-attr 44 | **1,011 히트/968 줄** · object 347 : Any 664 · attr 40(object 14·Any 26) | ≈(−5% · C 는 test/factories·fake·scripts 제외) | `s4_647.py` |
| S-4 #647 kkebi(app+fw) | 759/723(전 루트) | app+fw **435/422** · 전 루트 **760/740** | ✓ | 〃 `--roots` |
| S-4 `Mapping[str, object]` 최상위 매개변수 | spring 34 · kkebi 69 | param·object spring 99(top+nested) · kkebi 70 | ≈(집계 기준 차) | 〃 |
| S-4 `clean() -> dict[str, Any]` | spring 15 · kkebi 7(web 2 포함) | spring 15 · kkebi app 3(+`object` 1) | ✓(web 제외) | 〃 |
| S-4 HEAD 상환 도구 | TypedDict 2→19 · TypeAdapter 0→5 · JsonValue 38→67 | **동일** | ✓ | `git grep -c` |
| S-5 상자 둘 | f5ee428 8 · HEAD 7 · kkebi 6 | **8 · 7 · 6** | ✓ | `s5_count.py` |
| S-5 RootModel 단독 / Schema+RootModel | spring 4(+HEAD 1) · kkebi 1 / 1·0·0 | **동일** | ✓ | 〃 |
| S-5 #63 code-json | f5ee428·HEAD exit 2 · 2건 | **exit 2 · 2건** 양쪽 · auto exit 0 | ✓ | 검사기 재실행 |
| S-5 mypy kkebi 상자 둘 BC | 0(338 files) | **0(338 files)** | ✓ | kkebi venv mypy |
| S-5 도입 레인 | 08-25 이후 4 이상 | **5**(+08-24 identity 1) | ✓ | `git log -S` |

## 3. P1 61건 뿌리 자리 분류 (c20f525 · 대장 좌표 → 소스 판독 · `p1_ctx.txt`)

| 뿌리(즉시) | 오류 좌표 | 건수 | 뿌리 종류 | #647 수정 1 판정 |
|---|---|---|---|---|
| `SourceBlock.coordinate: Mapping[str, object]`(source_adapter.py:19 dataclass 필드) — `block.coordinate[...]`·`first/last = blocks[i].coordinate`·`coordinate = block.coordinate`·`dict(block.coordinate)` | coordinates 144·146·152·153·155·156·168·172·356·357·372·116 · crosswalk 111·112 · steps 464·1862 | **16** | (a) 클래스 속성 | **차단**(object 속성) |
| `_load_controls(...) -> tuple[object, object, object]`(cli.py:44) — `plan.rag_id` 10 · `run_c04/05/06(profile=, plan=, evaluation_pack=)` 9 | cli 134·135·138·149·152·163·190·214·259·282 · 170·171·172·203·204·205·246·247·248 | **19** | (b) 함수 반환 — **`tuple[object, …]`** | **표면 밖**(dict/Mapping 아님 · 결정표 6행 «자리표시 object») |
| `_item_value(...) -> dict[str, object]` · `_materialize_…_case_report -> Mapping[str, object]` 선언 vs 추론 dict | rfc8785_adapter 74 · ontology_c11 1447 | 2 | (b) 함수 반환 | 차단(object 반환) |
| 매개변수 `base_ref: dict[str, object]` ← 상류 `_terminal_bundle_base_ref -> dict[str, object]`(:133) | ontology_c11 1976·2003 | 2 | (c) 매개변수(상류 b) | ⓓ · 상류 반환은 차단 |
| 매개변수 `expected_files: list[object]` | model_snapshot 154 | 1 | (c) — `list[object]` | 표면 밖 |
| 콜백 매개변수 `schema: dict[str, object]` vs pydantic `JsonDict` · 매개변수 `list[dict[str, object]]`(:600) vs 인자 `list[dict[str, str]]` | cited_answer_schema 71 · ontology_c11 3193 | 2 | (c) 매개변수 | ⓓ |
| 지역 주석 `descriptor: dict[str, object] = load_json_object(...)`(:279) · `rag_refs: list[dict[str, object]]`(:302 ← `_require_sorted_unique_refs -> list[dict[str, Any]]`) · `activation_record: dict[str, object]`(:625) · `retrieval_request: dict[str, object] = cast(...)`(:985) · `document_by_id: dict[str, Mapping[str, object]]`(:889 ← `_objects -> tuple[Mapping[str, object], ...]`) · `values: list[dict[str, object]]`(rfc8785:85) | service_runtime 314·315·316·352·635·636·909 · ontology_c11 1032 · rfc8785_adapter 99 | 9 | (d) 지역 변수(주석) | ⓓ(변수) · 상류 반환 2건(`_objects`·`_require_sorted_unique_refs`=Any)은 차단 |
| **무주석 dict 리터럴**(`descriptor = {…}` 880·`manifest = {…}` 912·`current = {…}` 1511/registry_snapshot 712·`pointer`·`loss_rows = [...]` 92·`seed_payload = {…}` 279·`gate_results_payload = {…}` 3450·`expected = spec["expected"]`) — mypy 추론 `dict[str, object]`/`Collection[...]` | release_store 906·935·941·1528·1585 · registry_snapshot 725 · authoring 104 · passage 288 · steps 3516 · ontology_control 3477 | 10 | (d) 지역 변수(추론) | 표면 밖(주석 없음 — mypy 만 본다) |
| **합** | | **61** | (a) 16 · (b) 21 · (c) 5 · (d) 19 | **차단 18(+상류 4 = 22) · ⓓ 13 · 표면 밖 30** |

판독: «반환값·클래스 속성에 `object` 가 남으면 차단» 선은 `coordinate` 계열(16)과 반환 2를 정확히 잡는다 — 이 18건은 실제로 발주측이 `CitationCoordinate` TypedDict union 으로 갚은 자리와 일치한다. 그러나 (i) 단일 최대 뿌리 `tuple[object, object, object]` 반환 19건은 dict/Mapping 표면 밖이고 (ii) 무주석 추론 10건은 어떤 주석 검사기도 못 본다(mypy 몫). «선» 은 맞지만 «P1 뿌리 = 속성·반환 누수 → #647 차단» 명제는 22/61 이다. 결정표 6행(«타입 있는 값 → 실제 클래스 · 자리표시 `object` 금지»)에 대응하는 검사 자리를 ②가 정해야 한다(반환 주석 `tuple/list/Sequence[object…]` 포함 여부 · 또는 «6행은 mypy 몫» 명시).

## 4. 소급 비용 표

### 4-a. legacy 격리·브라운필드 귀속

| 규칙 | spring HEAD legacy | kkebi HEAD legacy | 앵커 격리 실증 | 브라운필드 update 잎 귀속 조건·비용 |
|---|---|---|---|---|
| #646(수정 1) | **18 발화**(클래스 17 + 속성줄 1)/16 파일/8 BC | **21**/21 파일/4 BC | run1~run4(아래) — 라인번호 정규화로 줄 밀림은 legacy 유지 | 헤더 문구(클래스명·기저) 변경 시에만 귀속. 실측: spring 16 파일 중 9 가 생성 후 5일 내 수정(11 커밋 · 레인 3) — 전부 본문·속성 수정(예: `f750454` accounts-1 S1 이 `_PROFILE_VIEW_FIELDS` 튜플만 변경) → 귀속 0. 단 update 잎이 기저를 별칭으로 «고치면» 그 클래스의 #493 첫 대입 위반이 legacy→귀속으로 바뀐다(발주측 `1288e4a` 메시지가 그 비용을 명기 · 11 파일 +131/−47) |
| #647 차단(Any 전 자리 + object 반환/속성) | **702줄**(app 136 · fw 566) | **165**(app) · 루트 필터 없으면 +web 104 · scripts 39 = **308** | 앵커(라인 정규화) | 함수/클래스 이름·파일 경로가 메시지에 들어가면 rename·이동 시 귀속 |
| #647 ⓓ(object 매개변수·변수) | **272**(app 111 · fw 161) | **264**(app) · +scripts 174 = **446** | **격리 없음** — `_FINDING_RE` 가 `[ⓓ#…]` 미파싱 | 매 레인 «해당 범위 실행분» 재동봉(billing 127 · llm_access 37 · fortune_reading 25) |
| #648 상자 둘 | 7 함수(accounts 6 · fortune_record 1) | 6 | 앵커 | 컨트롤러 함수명 불변이면 0 |
| #649 Schema+RootModel | 0 | 0 | — | — |
| #63(기존 · code-json 만) | 2(fortune_reading 400·503 · HEAD 잔존) | 31(identity 16 · saju 9 · review 5 · image 1) | 이미 legacy | 프로필을 code-json 으로 바꾸는 순간 L 도 code-json 으로 잡히므로 귀속 0 |
| 픽스처 | `public_surface/good/order_form.py` 3줄 red(#647 · :9 TypeIs nested 는 면제 · :20 `clean -> dict[str, object]` 면제 · :21 변수 → ⓓ → 수정 1 기준 **good red 0** — 단 :21 은 ⓓ 인쇄) · `naming/bad_rules` admin 3클래스(#646 교차 매트릭스) · 87 루트 S-5 0 | | | 정리는 «새 규칙 때문에만» 성립 |

`registry_gate` 실측(`$S/rv1C/spring-gate` · 클린 클론 · 각 68~71s · 27종 2회 실행):
- run1 `--anchor HEAD~1`(docs 1파일 diff): **귀속 0** · legacy 2,676(public-surface 2,662 · domain-model 5 · layer-skeleton 4 · test-config 2 · business-vocabulary 2 · context-isolation 1) · 해소 1 · exit 0.
- run2 `--anchor HEAD` + legacy #493 위반 파일(`docs/official/resource/build_fortune_overview.py`) 첫 줄에 주석 삽입(줄 밀림 +1): **귀속 0** · legacy 2,676 · exit 0 — 라인 정규화 확인.
- run4 같은 파일에서 위반 심볼 `view_box` → `view_box_rv1c` 개명(3줄 변경): **귀속 1** `check-public-surface-annotation.py :: [#493] docs/official/resource/build_fortune_overview.py:N: 지역 변수 \`view_box_rv1c\` 의 첫 대입에 타입이 없다` · legacy 2,675 · 해소 2 · **exit 2** — 라인번호는 정규화되지만 메시지 본문의 심볼 이름은 그대로 대조된다. #646 메시지에 클래스명이 들어가면 update 잎의 클래스 개명·기저 교체가 귀속이 되고, 파일 경로만 들어가면 파일 이동만 귀속이 된다(②에서 문구 결정).
- (run3 은 BSD sed `\b` 미지원으로 개명이 적용되지 않은 run2 반복 — 귀속 0 · 폐기.)

### 4-b. «정당해 보이는 반환/속성 `object`» 표본 12 (spring HEAD · `s4_spring_object_block.txt`)

| # | 자리 | 대체 | 판정 |
|---|---|---|---|
| 1 | `chat_relay/domain_layer/turn/value_object/turn_widget.py:19 item: Mapping[str, object]`(VO 속성 · 위젯 JSON) | `Mapping[str, JsonValue]`(결정표 5행) | 대체 있음 |
| 2 | `chat_relay/…/turn/schema/schema_out.py:76 delta(...) -> dict[str, object]`(SSE 이벤트 · 키 고정) | TypedDict | 있음 |
| 3 | `fortune_character/…/schema_out.py:16 build_list_body -> dict[str, object]`(API 본문 · 키 고정) | ninja Schema/TypedDict | 있음 |
| 4 | `fortune_catalog/…/rag_runtime_adapter.py:19 Protocol __call__(path) -> dict[str, object]`(JSON 로더) — 구현 `load_json_object -> dict[str, Any]` | `dict[str, JsonValue]`(Any 구현과 호환) | 있음 |
| 5 | `fortune_catalog/…/rag_runtime_adapter.py:33 _mapping(value: object, field) -> dict[str, object]`(좁히기 도우미) | `TypeIs[Mapping[str, object]]`(면제) + 호출부 ⓓ · 또는 `TypeAdapter(TD).validate_python` | **재구성 필요**(주석 교체 아님) |
| 6 | `llm_access/…/serialized_audit_payload.py:165 _require_object(value: object, …) -> Mapping[str, object]` | 5 와 동일 | 재구성 |
| 7 | `llm_access/…/openai/generation_adapter.py:70 Protocol model_dump(mode="json") -> Mapping[str, object]`(pydantic `dict[str, Any]` 미러) | `Mapping[str, JsonValue]` | 있음 |
| 8 | `fortune_record/…/save_fortune_record_command.py:28 answer_json: Mapping[str, object]`(커맨드 속성 · LLM 답 JSON) | `Mapping[str, JsonValue]` 또는 답 TypedDict | 있음 |
| 9 | `fortune_reading/…/schema_in.py:36 calculation_output: dict[str, object] \| None`(ninja Schema 요청 필드 · 통과 JSON) | `dict[str, JsonValue]`(pydantic 검증) | 있음 |
| 10 | `framework/…/service_runtime.py:685 _object(value: object, *, label) -> Mapping[str, object]` | 5 와 동일 | 재구성 |
| 11 | `promotion/…/campaign_repository.py:145 _discount_columns -> dict[str, object]`(ORM 컬럼 dict · 키 고정) | TypedDict | 있음 |
| 12 | `fortune_character/…/character_repository.py:180 _time_rule_to_columns -> dict[str, object]` | TypedDict | 있음 |

형상별 계수(반환 object · 줄): spring 57 = 좁히기 도우미형 6 · Protocol 미러 7 · 직렬화/컬럼/wire 빌더형 11 · 기타 33 / kkebi 59 = 도우미 13 · 빌더 32 · 기타 14. 대체 «주석» 이 없는 자리 0 → MAJOR 기준 미달. 단 도우미 19곳(spring 6·kkebi 13)은 «면제 `TypeIs` + 호출부 ⓓ» 또는 «TypeAdapter» 라는 형태 지침이 문면에 있어야 새 레인이 같은 모양을 반복하지 않는다(MINOR).

## 5. 효과 추정 (레인당 · 관측 n · 소급 총합 · 재분류)

| 항목 | 관측 n | 레인당 절감(왕복·mypy·감수자) | 과대 여부 | 정직한 서술 |
|---|---|---|---|---|
| S-1 | 레인 10 · ① 1(Claude fortune_character) · ② 8 · ③ 1(Claude service_policy) · 관측 왕복 **0**(전 레인 G2 통과) | mypy 26/레인 × 1/10 (발주측 상환 `1288e4a` 1 커밋 11 파일 +131/−47 · 훅 152→124) · 은폐 빚 18줄/8레인 미상환 · 별칭 블록 비용 6줄/기저(spring 18·kkebi 30 파일 이미 채택) | «왕복 절감» 없음 | «1/10 레인 mypy 26 · 8/10 레인 은폐 18줄 예방 · 왕복 0» |
| S-4 | BC 281줄(레인 산출) · mypy 70 중 레인 3 | Any 누수 예방 app 93 히트/16 BC ≈ **6/레인**(fortune_calculation 26·fortune_character 19·promotion 13) · object 반환/속성 차단 app 46/16 ≈ **3/레인** · 감수자 ⓓ app 111/16 ≈ **7/BC**(llm_access 37 · fortune_reading 25 · chat_relay 17) · kkebi ⓓ 264/11 ≈ 24/BC(billing 127) · mypy 절감 ≈ 0.2/레인 | **과대**: «mypy 빚 70» 의 67 은 비레인 RAG 런타임 | «레인당 Any 누수 ≈6·object 반환/속성 ≈3 예방 · mypy 빚은 발주측 RAG 67/70 · ⓓ 감수 ≈7/BC(kkebi ≈24)» |
| S-5 | 상자 둘 레인 7(Claude 4·Codex 2·미상 1) · mypy red 1/7(리딩 · concrete 값 직접 반환) · mypy-clean 13 함수 · 관측 왕복 0 | ⓐ: mypy 9 × 1/7 레인 예방 + 형태 통일 · ⓒ: 1 레인 1건 · ⓑ 철회 → #63 code-json 안내(리딩 2건 HEAD 잔존 · kkebi 31 legacy) | «상자 둘 = mypy strict 차단» 문장은 과대(수정 1 이 이미 정정) | «형태 통일 규칙 · mypy 효과는 1/7 레인» |
| 소급 총합 | — | legacy 격리 라인 spring 18+702+7 = **727** · kkebi 21+165+6 = **192**(+web/scripts 143) · ⓓ 반복 동봉 spring 272·kkebi 264 · 픽스처: good red 0(수정 1)·naming 교차 3·신설 good/bad 4쌍 | — | — |

### 판단 기준 4 재분류표

| 항목 | 플러그인이 만든 모양 | 검사가 못 잡는데 ≥2레인 반복 | 발주측 | C 판정 |
|---|---|---|---|---|
| S-1 ① 맨몸(1 레인) | django-web :208 예시 모양 일치 · §6 열람 흔적(design-spec:362) · 같은 런타임 다른 레인은 ③ | mypy 가 잡는다(레인이 자기 BC 를 안 돌림 = S-3) | S-3 | 문면 정정(예시 4줄) — 근거 «중간» |
| S-1 ② ignore(8 레인) | 예시 모양 아님(mypy 메시지 대응) | **✓** mypy `ignore-without-code` 통과 · 8 BC | — | #646ⓑ 정당(가장 강한 근거) |
| S-1 monkeypatch 전제 | — | — | dev 전이 의존성 → 운영 의존성 결정(R-12) | 발주측 |
| S-3 | — | — | ✓ | 발주측 |
| S-4 `dict[str, Any]`(app 93 히트) | ddd:1618 예시 1줄 · #645 ⓓ 후보라 반복 | ✓(차단 아님) | — | 문면 + #647 |
| S-4 `Mapping[str, object]` 형상(chat_relay·llm_access·fortune_reading·fortune_record) | R-3448 은 09-04 신설 → 8/27~9/3 레인 산출의 원인이 아님 · 레인 자체 선택 | mypy 통과(즉시 좁힘) | — | 문면(결정표·도우미 형태) · ⓓ |
| S-4 mypy 70 | 3/70(fortune_reading 레인) | — | **67/70 framework RAG(비레인)** | 발주측 재분류 |
| S-5 ⓐ 상자 둘 | 예시 모순 없음 · 산문 부재 | **✓** 7 레인 · 13 함수 mypy-clean | — | 문면 + #648 |
| S-5 ⓒ Schema+RootModel | RootModel 문면 0 | 1 레인 1건(Codex) | — | 문면 + #649(AST 만 · 싸다) |
| S-5 ⓑ base 뭉뚱그림 | — | 검사가 잡는다(#63 code-json) | 레인 G2 auto 운용(Coordinator :119 «Error response 와 무관한 G2 는 auto» 해석 — B 축) | #63 안내 · openapi 문면 stale 수리 |

## 6. «② 계획에 넣을 것»

1. **#647 표면 vs 결정표 6행**: «자리표시 `object`» 는 P1 최대 단일 뿌리(`-> tuple[object, object, object]` 19건)인데 dict/Mapping 표면 밖이다. 반환 주석의 `tuple/list/Sequence[…object…]`·bare `-> object` 를 #647(또는 #645 옆 별도 번호)에 넣을지, 아니면 «6행은 mypy 몫(R-20)» 을 문면에 명시할지 택일. 무주석 추론 10건은 어느 쪽도 못 본다 — 문면에 «dict 리터럴은 첫 대입에 TypedDict 주석»(#493 이 이미 요구)로 걸린다는 점만 적는다.
2. **ⓓ 채널 앵커 격리**: `[ⓓ#…]` 라인은 `registry_gate` 차분 밖 → kkebi billing 127·spring llm_access 37 이 매 레인 재동봉. R-0284 «해당 범위 실행분» 을 «변경 파일/BC 범위» 로 못 박거나 `_FINDING_RE` 를 ⓓ 까지 넓혀 N∖L 로 접는다. 그렇지 않으면 수정 1 의 ⓓ 는 감수자 잡음이다.
3. **#647 루트 필터**: kkebi `web/`(dddjango-web 산출 · 차단 104)·`scripts/`(차단 39·ⓓ 174) 포함 여부 — 자매 플러그인 경계와 «BC 산출물만» 취지에 맞게 `application/`·`framework/` 로 제한할지 결정(#493 과 같은 기존 동작이라는 이월 MINOR 는 #647 도입으로 규모가 3배가 된다).
4. **좁히기 도우미 반환 형태**를 문면에: `_mapping(value: object) -> dict[str, object]`(spring 6·kkebi 13)은 «`TypeIs[...]` 반환(면제) + 호출부 지역 변수 ⓓ» 또는 «`TypeAdapter(TD).validate_python`» 두 형태만 — 그렇지 않으면 새 레인이 같은 모양을 쓰고 #647 차단에 걸린다.
5. **#646 메시지 문구**: 클래스명·기저명을 메시지에 넣을지 결정(넣으면 update 잎의 클래스 개명 시 귀속 — run4 실증). 권장 = 넣는다(개명·재작성 시점에 갚게) · 단 «기저를 별칭으로 고치면 #493 첫 대입 위반이 귀속으로 바뀐다» 는 발주측 비용을 회신 3 에 명기(1288e4a 선례).
6. **효과 서술 정직화(회신 3)**: S-1 «왕복 절감» 이 아니라 «1/10 레인 mypy 26 + 8/10 레인 은폐 18줄 예방» · S-4 «mypy 빚 70» 이 아니라 «레인당 Any 누수 ≈6·object 반환/속성 ≈3 예방 · 70 중 67 은 발주측 RAG 런타임» · S-5 «상자 둘 = mypy 차단» 이 아니라 «형태 통일 · mypy 효과 1/7 레인».
7. **S-1 «플러그인이 만든 모양» 근거 표기**: ①(1 레인)은 «예시 모양 일치 + §6 열람 흔적» 까지, ②(8 레인)은 «검사가 못 잡는 반복» 으로 — 예시 정정 4줄과 #646ⓑ 의 근거를 섞지 않는다.
8. **Form.clean 면제 문면**: 면제는 `-> dict[str, object]` 만 · 현장 `-> dict[str, Any]` spring 15·kkebi 3 은 #647 차단(Any) legacy → 새 레인 지침에 «`Any` 아님» 을 명시.
9. **#63 안내 문구(회신 3)**: kkebi 31 자리(identity 16·saju 9·review 5·image 1)도 code-json 으로 돌리면 전부 red — «오류 응답을 선언한 컨트롤러 G2 는 code-json» 안내에 legacy 규모를 함께 적는다.
10. **picture 단위 비용**: `registry_gate` 1회 ≈70s(spring 2,555 파일 · 27종 ×2) — #646·#647·#648·#649 추가로 검사기 1종당 실행 시간이 늘어나는 규모는 ④에서 실측.

## 7. 사각 · 미확인

1. `registry_gate` 실증은 #646/#647 이 없는 사본에서 기존 #493 위반으로 «메커니즘» 만 확인했다 — 실제 귀속 여부는 ②에서 정할 메시지 문구(클래스명 포함 여부)에 달린다.
2. ⓓ 채널 «해당 범위 실행분»(dddjango.md:108)의 실제 실행 범위(루트 전체 vs BC)는 Coordinator 실행 경로에서 확인하지 않았다 — 문면 판독.
3. P1 뿌리 분류는 «즉시 뿌리» 소스 판독이다(mypy `reveal_type` 미실행) · `tuple[object,object,object]` 19건이 한 함수(`_load_controls`)에서 나온다는 점은 정확하나, 발주측이 그것을 어떤 도구로 갚았는지(HEAD `cli.py`)는 열지 않았다.
4. kkebi `web/` 가 dddjango-web 산출이라는 것은 S1 summary 진술에 의존(커밋 표식 미확인).
5. S-1 «§6 열람 흔적» 은 design-spec 1줄(architect 산출)이다 — coder 가 :208 예시를 봤는지는 Claude 런타임 로그가 없어 알 수 없다.
6. kkebi identity `web_session_controller.py`(c2b2bfd) 의 상자 둘은 레인 디렉터리를 특정하지 못했다(«미상 1»).
7. `registry_gate` 모든 run 에서 «해소(L∖N) 1건» 이 상존 — 앵커 스냅숏 vs working tree 의 상시 차이 1건(정체 미확인 · 귀속엔 무영향).
8. #647 시제품 수치 차(조사자 1,061 vs C 1,011)는 test/factories·fake·scripts 포함 여부로 설명되나 줄 단위 대조는 하지 않았다.
