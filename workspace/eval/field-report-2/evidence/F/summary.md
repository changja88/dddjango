# F 항목 실측 — composition root 주입 callable 시그니처 불일치 · 실배선 테스트 부재

측정일 2026-09-04 · spring HEAD `d2eaafe` · kkebi HEAD `6608fb0` · 두 저장소 읽기 전용(스냅숏은 `git archive`로 scratchpad에 추출).
산출물: `wiring_audit.py`(AST 정적 대조) · `test_audit.py`(테스트 실태) · `injection_table.md`(주입 지점 150행 전수표) · `summary_wiring.txt` · `mypy_pre.txt`/`mypy_head.txt` · `keyword_grep_reports.txt`.

## 1. 측정 방법

- **composition root 전수**: `application/*/composition_root/dependency_wiring.py` glob. spring 16 BC · kkebi 12 BC(전부 `composition_root/{__init__,dependency_wiring,event_wiring}.py` 3파일 골격).
- **주입 지점 추출**(`wiring_audit.py`): 각 `build_*` 함수 안 모든 `Call`의 키워드 인자 중 값이 Name·Attribute·`partial(...)`·Lambda 인 것. 수신 클래스→`__init__`(또는 dataclass 필드·1단계 base) 매개변수 주석 → Protocol `__call__` / `Callable[[…],R]` / `type X = Callable[...]` 별칭까지 해석. 주입식은 import 추적·팩토리 내부 지역 def/대입(`cast(...)` 포함)·`X().method`·stdlib(`inspect`)까지 해석. `partial`은 바인딩 kw/pos 제외 뒤 대조. 판정 = 주입 함수의 **필수 인자 중 Protocol이 안 주는 것**(불일치) · Protocol이 주는 인자를 주입 함수가 **못 받는 것**(불일치, `**kw` 예외) · 그 외 일치. 값 주입(settings·int·인스턴스)은 «value 범위»로 표에서 제외.
- **자체 검증**: 같은 스크립트를 spring `36258bb^`(=8244190, 수리 직전)와 `585c9c6`(결함 도입 커밋) 스냅숏에 적용해 원 결함 검출 여부 확인.
- **테스트 실태**(`test_audit.py`): `monkeypatch.setattr / patch / patch.object` 인자에 `build_*` 문자열·속성이 있는 호출(다줄 포함) vs 같은 파일에서 patch 안 된 이름으로 `build_*use_case()`를 직접 호출하는 지점.
- **mypy 교차 검증**: 스냅숏 디렉터리에 `spring_dream_server`·`pyproject.toml`·`.venv` 등을 symlink 후 `mypy --cache-dir <scratch>` 단일 파일 실행(저장소 무변경).

## 2. 표

### 2.1 정적 시그니처 대조 (callable 범위만)

| 스냅숏 | 주입 지점(전체) | callable 범위 | 일치 | 불일치 | 판정 불가 | callable 주입 있는 BC |
|---|---|---|---|---|---|---|
| spring 585c9c6 (결함 도입) | 286 | 42 | 40 | **1** | 1 | accounts·chat_relay·fortune_reading·llm_access |
| spring 36258bb^ (수리 직전) | 304 | 51 | 49 | **1** | 1 | + fortune_catalog |
| spring HEAD (수리 후) | 304 | 51 | 50 | 0 | 1 | 5 BC |
| kkebi HEAD | 143 | 48 | 48 | 0 | 0 | billing 34·product_observability 11·share 3 |

- 유일한 불일치 = `application/fortune_reading/composition_root/dependency_wiring.py:42`(585c9c6에서는 :48) `RagRuntimeEvidenceRetrievalAdapter(run_retrieval=service_runtime.retrieve_release_evidence)` — Protocol `_RunRetrieval.__call__` 키워드 9개 vs 주입 함수 필수 `data_root, embedder` 추가 → «주입 함수 필수 인자 미공급: data_root,embedder». HEAD는 `partial(retrieve_release_evidence_with_local_embedder, data_root=data_root)` → 일치. **방법이 원 결함을 잡고, 수리 후 소거됨을 확인.**
- 판정 불가 1건(spring chat_relay:213)은 `runtime.get_start_turn_persistence_factory()` 호출 결과의 메서드 — 런타임 값이라 정적 해석 밖.
- kinds: spring name 38·attr 9·lambda 3·partial 1 / kkebi name 43·attr 3·lambda 2. 수신 계약 종류: spring Protocol-`__call__` 10·`Callable[...]` 41 / kkebi 2·46. **Protocol 수신은 fortune_reading(4)·fortune_catalog·accounts에 집중** — kkebi는 거의 전부 `Callable[[], UoW]` 팩토리 주입.
- mypy strict(spring `pyproject [tool.mypy] strict=true`): 36258bb^ 스냅숏에서 `dependency_wiring.py:42: error: Argument "run_retrieval" ... has incompatible type "def retrieve_release_evidence(*, data_root: Path, embedder: Embedder, ...)"; expected "_RunRetrieval"  [arg-type]` **검출됨**; HEAD는 그 줄 오류 없음(`mypy_pre.txt`/`mypy_head.txt`). 그러나 `.pre-commit-config.yaml:70` mypy 훅 대상은 `uv run mypy spring_dream_server framework` — **`application/` 미포함**. 레인 STOP 문서의 mypy 실행은 «checked 1 source file» 식 focused 실행. 즉 기존 툴체인으로 정적 검출 가능했으나 검사 범위 밖이었다.

### 2.2 테스트 실태

| 저장소 | 테스트 파일 | `build_*` patch 지점 | 실 `build_*()` 호출·실행(patch 안 함) |
|---|---|---|---|
| spring HEAD | 488 | 49 지점 / 16 파일 (fortune_reading 14/5 · fortune_intent 11/5 · query_translation 7/1 · chat_relay 6/1 · llm_access 6/1 · tests/ 3 · promotion 2/2) | 21 지점 / 7 파일 — media_library 6·service_policy 7(3파일)·fortune_character 1·**fortune_reading 1(신설 실배선)**·chat_relay 6(fake runtime 헬퍼, execute 없음) |
| spring 36258bb^ | 447 | fortune_reading **14 지점 / 5 파일**, 실 호출 **0** | — |
| kkebi HEAD | 510 | 21 지점 / 11 파일 (identity 16/8 · product_observability 2 · tarot 2 · tests/ 1) | 23 지점 / 7 파일 — billing 21(5파일, 전부 `build_import_legacy_billing_use_case` 계열) · tarot 2 |

- 현장 보고의 «26곳»은 미재현 — 실측은 BC 내 14 지점(5 파일; 팩토리명별 `build_prepare_fortune_evidence_use_case` 11 · `build_validate_citations_use_case` 2 · `build_generate_use_case` 1) + llm_access 측 `build_generate_use_case` 3. 집계 기준 차이로 추정(미확인).
- spring `application/fortune_reading/test/unit/test_composition_root_wiring.py`(157줄, 36258bb 추가) fake 경계: ① `monkeypatch.setattr(dependency_wiring, "QueryTranslationAdapter", _FakeQueryTranslationAdapter)` — LLM 경계 ACL 어댑터 자리를 생성자 키워드만 같은 fake로 교체, ② `service_runtime.verify_model_snapshot_ref`·`load_local_embedder`를 인덱스 pin과 identity가 같은 결정적 `_PinnedEmbedder`로 교체(가중치 파일 없이 실행). 그 외(active Bundle 고정·검색 어댑터·검색 런타임·Release 산출물·digest 어댑터)는 실물. `dependency_wiring.build_prepare_fortune_evidence_use_case()` → `execute()` 1경로.
- BC별 실배선 테스트 유무(진짜 팩토리→execute): spring 16 BC 중 **5**(media_library·service_policy·fortune_character·fortune_reading·[chat_relay는 fake runtime 경유 헬퍼라 불확실]) · kkebi 12 BC 중 **2**(billing·tarot). 나머지는 0(미측정 아님 — 검출 0).

### 2.3 표본 외 재현 · 유사 사건

- 정적 대조: kkebi 12 BC 전부 불일치 0 · spring 다른 15 BC 불일치 0(위 표). **1레인(fortune_reading P4) 특이.**
- 키워드 grep(`lane-report.md`·`STOP-*.md`·`REPORT*.md`·`report.md`, violations 제외 — spring 159 파일·kkebi 15 파일; kkebi에는 `lane-report.md`가 0개): `TypeError|arg-type|시그니처` 히트 spring 17줄·kkebi 2줄. 유사 사건 1건 — spring `docs/superpowers/orders/lane/STOP-fortune-reading-l2-t16-runner-content-roles.md:24` «`TypeError: _ProjectionBackedRunner.__call__() got an unexpected keyword argument 'content_roles'`»: 같은 어댑터(`RagRuntimeEvidenceRetrievalAdapter`)의 **테스트 fake runner**가 Protocol 9번째 키워드를 못 받아 실패(방향 반대 — 실물이 아니라 fake 쪽 시그니처 drift). `wiring|배선`+`오류|결함|불일치|TypeError` 동시 히트는 양 저장소 0(kkebi 1줄은 «실배선» 단어 우연 일치, 결함 아님).

## 3. 판단 재료

1. **1레인 특이인가** — 예. 양 저장소 composition root 28개·callable 주입 99지점 중 불일치는 fortune_reading 1지점뿐, 같은 날(09-03) 도입→수리. 단 «실배선 테스트 부재»는 특이가 아니라 **기본 상태**(spring 11/16 BC · kkebi 10/12 BC에 실 팩토리 실행 테스트 0; 팩토리 patch 지점 spring 49·kkebi 21).
2. **정적 대조로 검출 가능한가** — 예, 두 경로 모두. (a) AST 대조 스크립트가 pre/post를 정확히 가름(오탐 0, 미판정 1). (b) 기존 mypy strict가 `[arg-type]`로 이미 잡고 있었으나 pre-commit 훅 대상이 `spring_dream_server framework`라 `application/`이 빠져 있었다 — 규범이 «mypy 대상에 `application/` 포함»을 요구하는지가 별도 쟁점(미조사).
3. **문면 위치와 graph-owned 여부**
   - `dddjango/skills/implementation-django-ninja/references/final.md` §2.3 «컴포지션 루트(배선)» 문단 :294–313(«`build_<use_case>()` 팩토리 … 호출만(매요청 조립)» :294 · «**매요청 호출** … 테스트 오버라이드 회피» :312 · «BC 격리» :313). 마커 :205(§2.3 시작)~:331(§3.1) — **graph-owned**(LEDGER `implementation-django-ninja-final s010-2.3 graph` :1508). 그래프 정본 `ontology/rules/implementation-django-ninja-final.ttl` R-0719(:1444 «DI 조립의 composition_root/dependency_wiring.py 소유·build_<uc>() 매요청 호출») · R-0722~R-0725(:1467–1492, 블록 b20/b21 :2740–2749). «주입 callable ≡ Protocol 시그니처»·«partial/클로저» 문면은 **없음**. «만들기와 꽂기»는 final.md에 없고 검사기 문구에만 있음. `#85`는 final.md에 언급 없음.
   - `discipline-houserules/references/final.md` :194–206 #81·#10·#92·#97(«`composition_root` 의 `build_`») — graph-owned 절.
   - 테스트 측: `implementation-test/references/final.md`에 «composition root»·«실배선» 0건(monkeypatch는 §3.8 :311–321 환경변수·:1342 datetime 비권장만); `discipline-tdd/references/final.md`도 0건(:443 «monkeypatch seam만 확인하는 assertion» 금지 목록). 두 SKILL.md에도 0건. dddjango에 `discipline-test` 스킬은 **없음**(dddart 전용).
   - 에이전트: `design-review-api.md` :49–58·`design-review-ddd.md` :31–44 점검 항목(모두 graph-owned)에 «주입 의존 공급처» 항목 **없음**. `discipline-reviewer.md` :93 «API instance·registrar·composition 규율»은 registrar/DI-only 분리만 다룸. `coder.md`·`acceptance-tester.md`에 주입 시그니처 언급 0.
4. **검사기**: `dddjango/scripts/check-composition-root.py` `_check_dependency_wiring` :1841–1875 — #85 조건은 «dependency_wiring.py 최상단에는 import와 `build_*` 팩토리만 온다 / 비-`build_` 함수 → #85 finding / 함수 안 `if` → #86 후보». 주입 값·시그니처는 보지 않는다(헤더 :1–40 명시 «고정밀·저-recall … 형태만»). `check-event-publish.py`·`check-missable-entrance.py`는 #85 짝(`build_X ↔ X_use_case.py`)만 해소에 사용.
5. **미측정**: 36258bb의 «옛 배선으로 되돌리면 TypeError» 런타임 재현(테스트 실행 안 함 — 커밋 메시지 인용만) · «26곳»의 집계 기준 · 레인 당시 mypy 실제 실행 범위(문서에 count 미기재).
