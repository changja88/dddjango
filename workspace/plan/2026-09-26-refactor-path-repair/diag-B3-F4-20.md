# 진단 B3 — F4-20 (`check-transaction-boundary.py` #195 반복 원소 출처 미전파)

- 작성: 2026-09-26 · 진단만(저장소 파일 수정 0 · 커밋 0) · Serena/Graphify 미사용(지시).
- 결론 한 줄: **결함 실재. 캠페인 빚 «#195 1건»(fortune_library)은 이 오탐 그 자체다.** 수리는 `_check_execute_body` 안에서만 끝나는 국소 변경이다. 단, 보고서가 먼저 제시한 «factory_born 이름을 도는 for 변수 전파»를 그대로 옮기면 참양성을 놓친다(아래 §4 실측).
- 표기: **[확인]** = 파일을 읽거나 명령을 돌려 확인한 사실 · **[추론]** = 판단.

## 1. 근본 원인 — `dddjango/scripts/check-transaction-boundary.py`

- [확인] 규칙 문면: docstring 9–11행 «save/remove 인자는 같은 함수 안에서 루트 메서드 호출을 받은 객체여야». 정직 기록 33–35행에는 «…또는 도메인 팩토리 호출로 태어났으면 통과»라고 적혀 있다.
- [확인] 판정 함수는 `_check_execute_body`(452–518행)다. 공개 메서드마다 호출된다(446–449행 · `_` 로 시작하는 헬퍼는 대상이 아니다). 이 함수는 `ast.walk(fn)` 한 번(472–497행)으로 세 집합을 모은다.
  - `factory_born`(468행): 473–485행에서 **`Assign/AnnAssign` 이고 target 이 `ast.Name` 이며 value 가 `ast.Call` 일 때만** target 이름을 넣는다(478행 조건). callee 가 리포지토리가 아니면(483–484행) 모두 여기에 든다.
  - `method_called`(467행): 490–497행에서 `Name.method(...)` 호출의 수신자 이름을 모은다. 리포지토리 수신자는 쓰기 수집(492–495행)으로 빠진다.
  - `writes`(470행): 리포지토리의 `save*/remove*` 호출이다. 첫 인자가 `Name` 이면 그 이름을 기록한다(495행).
- [확인] 판정은 506–515행이다. 쓰기 인자 이름이 `method_called ∪ factory_born` 에 없으면 #195 를 낸다.
- [확인] **이름을 새로 만드는 구문 가운데 `ast.For/AsyncFor` 의 target 과 `ast.comprehension` 의 target 은 어떤 수집 분기에도 없다.** 그래서 `x = Factory(...)` 로 태어난 원소는 통과하지만, 같은 원소가 `tuple(Factory(...) for …)` 컬렉션을 도는 `for x in …` 변수로 나타나면 출처를 잃는다. 컬렉션 이름(`mappings`)은 `tuple(...)` 이 Call 이라서 factory_born 에 들어간다(478행). 하지만 반복 변수(`mapping`)로 넘겨주는 단계가 없다. 리스트 컴프리헨션(`orders = [F(...) for …]`)은 value 가 Call 이 아니어서 컬렉션 이름조차 수집되지 않는다.
- [확인] 도메인 서비스 호출 `self._reference_policy.validate(mapping, …)` 는 수신자가 `Attribute` 라 496행 분기(`isinstance(recv, ast.Name)`)에 들지 않는다. 루트 메서드가 아니므로 의도된 동작이다(보고서 기술과 일치).

## 2. 재현 — scratch `…/scratchpad/f4-20/`

실행(모든 run 공통): `env -u DJR_FINDINGS_JSON DJR_VIOLATIONS_DIR=<f4-20>/violations PYTHONUTF8=1 .venv/bin/python -B dddjango/scripts/check-transaction-boundary.py <대상>` · cwd = 저장소 루트. fixture_matrix.py:212 도 같은 방식으로 subprocess 를 호출한다.

- [확인] `f4-20/root` = `workspace/eval/fixtures/transaction_boundary/good` 사본에 유스케이스 5개를 더한 것(원본 good 은 exit 0).

| 케이스 | 모양 | HEAD 결과 | 기대 |
|---|---|---|---|
| `import_orders` | 현장 판형: `orders: tuple[Order, ...] = tuple(Order.open_pending(i) for i in ids)` → `for order in orders: policy.validate(order)` → `for order in orders: if repo.get(..) is None: repo.save(order)` | **#195 :24** | green(오탐) |
| `import_orders_listcomp` | `orders = [Order.open_pending(i) for i in ids]` → `for order in orders: save(order)` | **#195 :18** | green(오탐) |
| `import_orders_inline` | `for order in (Order.open_pending(i) for i in ids): save(order)` | **#195 :17** | green(오탐) |
| `tp_loaded_loop` | `orders = repo.list_open()` → `for order in orders: order.status = …; save(order)` | #195 :18 + UoW 루트 호출 0 :13 | red 유지 |
| `tp_list_wrapped` | `orders = list(repo.list_open())` → 위와 같은 루프 | #195 :19 | red 유지 |

- [확인] HEAD 출력은 exit 2 에 #195 6줄이다. 오탐 3건(24·17·18행)과 참양성 3줄이 함께 나온다.
- [확인] 현장 파일(`spring_dream_server` 508a841a8 판)을 `git show` 로 `f4-20/field/` 에 뽑아 같은 명령을 돌렸다. `:82: save/remove 인자 \`mapping\`` 한 줄이 나오고, 캠페인 증거 `evidence/root-run-508a841a8/check-transaction-boundary.py.txt:13` 과 **byte 동일**하다(`diff` 무차이).

## 3. 규칙 문면 대조 — 정당한 코드인가

- [확인] #195 는 ontology 에 alias 가 없는 rule-owner-map 번호다(`workspace/eval/ab/T0-rule-owner-map-snapshot.md:192` · 별칭 대장 `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md:61` 이 «R-0108 합성 Work 의 실호출 축 · 미등재»로 확정). houserules final.md 에는 없다. 문면 정본은 검사기 docstring 9–11·33–35행이다. 상위 규범은 R-0108(`dddjango/skills/architecture-ddd/references/final.md:644`)이다: «판정은 도메인 애그리거트(안 담기면 도메인 서비스)가 소유하고, 응용은 조회 → 도메인 기능 실행 → 영속화 순서로 실제 호출한다».
- [확인] 현장 코드(508a841a8 · HEAD 12d876dcc 와 무변경)의 흐름은 다음과 같다.
  - 59–71행: 애그리거트 팩토리 `SearchTermMapping.create_pending`(`search_term_mapping.py:84–85` `@classmethod`)로 전량을 생성한다.
  - 73–78행: 도메인 서비스 `SearchTermMappingReferencePolicy.validate`(`search_term_mapping_reference_policy.py:16` · 위반 시 도메인 예외 21·27·30행)로 전량을 검증한다.
  - 80–83행: `load_by_identity(...) is None` 이면 `save_new(mapping)` 을 호출한다.
  - 저장되는 객체는 **모두 도메인 팩토리에서 태어난 애그리거트**다. 정직 기록 34행의 통과 조건과 같은 의미다. 판정도 도메인 서비스가 소유한다.
- [추론] 따라서 #195 문면으로는 정당하다. 위반이 아니라 AST 수집 채널의 결손이다. 부재 검사 후 저장(`is None → save_new`)이 R-0108 의 «판정 대신 내리기»에 해당하는지는 #195 가 아니라 discipline-reviewer 소관의 별개 물음이다. 명세가 요구한 멱등 반입이라 이 진단에서는 문제 삼지 않는다.

## 4. 수리 설계(최소)

- [확인] **순진한 전파(보고서 기대 전단: «`for t in <factory_born 이름>` → t 를 factory_born»)는 쓰면 안 된다.** 478–485행의 factory_born 조건은 리포지토리가 아닌 모든 Call 을 포함한다. 그래서 `orders = list(repo.list_open())` 도 factory_born 이 된다. 이를 scratch 시제품 A(`f4-20/proto/A`)로 실측했다.
  - `tp_list_wrapped` 참양성이 **소멸**한다(눈가림).
  - 리스트 컴프리헨션과 inline 오탐은 **남는다**.
- [확인] **시제품 B(`f4-20/proto/B` · 권장 설계)의 원리: 원소식에 스칼라 대입과 같은 판정을 적용한다.** 반복 변수 `x` 를 «`x = <원소식>` 이라고 쓴 것»과 같게 본다. 스칼라 판정보다 넓어지지 않으므로 새 사각지대가 생기지 않는다.
  - 478–485행 조건을 지역 함수 `_is_factory_call(value)` 로 뽑는다. 스칼라 수집과 원소 판정이 한 출처를 쓰게 된다.
  - `_elements_factory_born(it)` 가 참인 경우는 셋이다. ① `ListComp/SetComp/GeneratorExp` 인데 `elt` 가 `_is_factory_call` 인 경우 ② `tuple|list|frozenset|set(<①>)` 처럼 단일 인자에 키워드가 없는 경우 ③ `element_factory` 이름.
  - walk 1회로 `Assign/AnnAssign(Name ← ①②)` 를 `element_factory` 에 모은다. 이어서 walk 1회로 `For/AsyncFor/comprehension` 의 `Name` target 이면서 `_elements_factory_born(iter)` 인 경우 `factory_born` 에 넣는다. 두 단계로 나눈 이유는 `ast.walk` 순서에 기대지 않기 위해서다. 판정(506행~)보다 앞에 둔다.
- [확인] 시제품 B 실측 결과:
  - scratch root: 오탐 3건 소멸, 참양성 3줄 유지(`tp_list_wrapped` 포함).
  - 현장 사본: exit 2 → **0**.
  - `transaction_boundary/good`·`bad_rules` 사본: HEAD 와 **출력 byte 동일**(0 / 15건).
- [추론] 수리 뒤에도 남는 오탐(fail-closed · 누락 위험 없음): 튜플 언패킹 target(`for i, m in enumerate(..)`), 필터 체인(`[m for m in ms if …]` 처럼 elt 가 Name), 리터럴 `[F(), G()]`, `sorted/map/zip`. 정직 기록 33–35행에 «반복 원소는 원소식이 팩토리 호출인 컬렉션만 전파»로 명시한다.
- [확인] 기존 약점(F4-20 밖 · 이번 범위 아님): 위 factory_born 조건의 과포섭, 그리고 496–497행이 `SearchTermMapping.create_pending`·`datetime.now` 같은 클래스·모듈 수신자까지 `method_called` 에 넣는 문제다. 이 때문에 516행의 «UoW 루트 호출 0» 검사가 약해져 있다. 실측으로 `tp_list_wrapped` 는 그 줄을 내지 않았고 `tp_loaded_loop` 는 냈다.

### 동반 갱신 목록

| 대상 | 변화 | 근거 |
|---|---|---|
| `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py` | byte 미러 동시 갱신(현재 `cmp` 동일 확인) | Makefile:171 `diff -rq` |
| `workspace/eval/fixtures/transaction_boundary/good/…/order/import_orders/` | 새 good 케이스: `import_orders_use_case.py`(tuple genexpr → for → save) + 빈 `_command/_query/_result.py` 3개(51a0a531 선례 골격). **[확인] HEAD 에서 red(재현 증명) · B 에서 green · 다른 검사기 26종 발자국 0**(scratch `xgood_new` 로 27종 exit·규칙 ID 대조) → cross-matrix 불변 | checker_cross_matrix.py:61 (good 레인만) |
| `…/transaction_boundary/bad_rules/…/order/close_orders/close_orders_use_case.py` | 판별 음성 경계: `list(repo.list_open())` 루프 + 필드 대입 → #195. **[확인] HEAD 16건·B 16건·A 15건** — 순진 전파를 red 로 잡는 가드 | — |
| `workspace/tools/findings_count_matrix.py:134` | `(2, 15→16, 2, "#195×1→×2,…", 해시 3종 재생성)` — `--emit-expected` 로 갱신하고 사유 기재 | 같은 파일 44–45행 규율 |
| `workspace/tools/checker_baseline_matrix.py:261` | `(2, 15→16, 15→16, 3, False)` | 같은 파일 규율 |
| `checker_cross_matrix.py` · `fixture_matrix.py:50` | 불변 예상(good 발자국 0 · bad 는 이미 exit 2) | 위 실측 |
| `dddjango/scripts/pregate_symbol_kinds.json:28` + Codex 미러 | `source_sha` 가 검사기 byte 해시라 재소성 필요(`gen_pregate_symbol_kinds.py` 무인자 실행) | gen_pregate_symbol_kinds.py:476 · Makefile:198 `--check` |
| `workspace/eval/ab/T2-0b-manifest.json` | 봉인 대상 글롭 `dddjango/scripts/check-*.py`(manifest_seal.py:56) — 수리 커밋 **뒤** 별도 chore 커밋으로 재발행 | DEVELOPMENT.md:128·154 |
| 규범 그래프·rulepack·LEDGER | 불변(검사기 구현 수리 · 규범 문면 무변경) | — |
| `ontology-adoption-map.html` | 51a0a531 선례·사용자 상시 지침에 따라 행 추가 | 메모리 «조감도 상시 갱신» |

## 5. 현장 영향 — 캠페인 «#195 1건»

- [확인] `evidence/bc-scan-root-508a841a8.json:53–58`: `fortune_library total 1 = transaction-boundary 1`. 같은 run 원문(`root-run-508a841a8/check-transaction-boundary.py.txt:13`)의 유일한 #195 는 `import_search_term_candidates_use_case.py:82 · mapping` 이다. 위 §2 의 scratch 재현과 byte 동일하다.
- [확인] 원천 파일은 508a841a8 ↔ HEAD 12d876dcc 사이 무변경이다(`git diff --stat` 공백 · 마지막 변경 fbf0b46b2). F4-20 보고의 실물(보고서 18–23행 · A5 STOP-03)과 같은 코드다.
- [추론] **그 1건은 빚이 아니라 이 오탐이다.** 수리 릴리즈 후 재측정하면 plan-v2.md:8 의 «BC 경로 빚 168건» 가운데 `#195 1` 이 빠져 167건이 되고, fortune_library 는 빚 0 BC 가 된다(다른 변화가 없다는 전제). 현장의 A5 waiver 레코드 1(보고서 23행)은 설치본 갱신 뒤 회수할 대상이다. spring_dream_server 에서는 `git show`·읽기만 했고 검사기는 scratch 사본에서만 돌렸다.

## 6. scratch 산출물(재실행용)

`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/f4-20/`
- `root/`: 재현 트리(§2 표 5개 케이스)
- `field/`: 현장 파일 사본
- `proto/make.py`: 시제품 생성기(HEAD 검사기에 A/B 블록 삽입). 산출물은 `proto/{A,B}/check-transaction-boundary.py`
- `xgood_new/`, `xbad_new/`: 제안 fixture 사본
- `violations/`: 레코드 sink
