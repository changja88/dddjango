# 수리 R8-D2 구현 기록 — `check-transaction-boundary.py` #195 도메인 컬렉션 팩토리 전파(P1z)

- 작성: 2026-09-28 · 격리 워크트리 `.claude/worktrees/agent-aff1131d91930e31b` 에서 구현했다. **커밋 0 · push 0** 이다. 변경은 워크트리에 미커밋으로 남겨 두고 메인 세션이 이식한다.
- 정본 명세: `workspace/plan/2026-09-26-refactor-path-repair/diag-R8-D2-195.md`(메인 체크아웃 · 미커밋). 권고안 **P1z**(선언 증거 + 무인자)를 구현했다.
- Serena/Graphify 는 지시대로 쓰지 않았다.
- 기준 커밋: 워크트리는 `acbfffda` 에서 시작했다. 진단 기준인 main `1d712d87` 의 조상이라 `git merge --ff-only 1d712d87` 로 브랜치 포인터만 앞당겼다(새 커밋 없음). 그래서 아래 diff 는 `1d712d87` 기준이다. 검사기 sha256 앞 16자리는 수리 전 `0400895d29d9ba61` 로 진단과 같다.
- 2026-09-29 독립 구현 리뷰(`scratchpad/review-D2/review-195-repair.md` · 수정 후 승인 · blocker 0 · major 1 · minor 2 · nit 4)를 반영했다. 처분과 결과는 **§8** 에 있다. 이 문서의 §1·§5·§6·§7 은 반영 후 최종 상태이고, §2~§4 는 리뷰 전 1차 구현(IMPL1 · `59f017b09fcaf958`)의 기록이다.
- 2026-09-29 재검토(`scratchpad/review-D2b/rereview-195-repair.md` · 수정 후 승인 · blocker 0 · major 1 · minor 1 · nit 2)를 반영했다(**§9** · IMPL3 `f5aa008b741f66ae`).
- 2026-09-29 조정자 추가 지시(순수 읽기 자리 확장 · §7 의 리스트 컴프리헨션 회귀 축소)를 반영했다(**§10**). 검사기 최종 sha 는 **`0cac462393f5e836`**(IMPL4)다.

## 1. 바뀐 것(리뷰 반영 후 최종)

| 파일 | 변화 |
|---|---|
| `dddjango/scripts/check-transaction-boundary.py` | 1차 구현:<br>- 상수 `COLLECTION_RETURNS` 추가<br>- 헬퍼 3개(`_domain_class_index`·`_returns_own_collection`·`_domain_collection_factories`)<br>- BC 당 도메인 색인 1회·모듈마다 표<br>- `_check_execute_body` 인자 `collection_factories`<br>- `_elements_factory_born` 가지 1개<br>리뷰 반영(§8):<br>- 헬퍼 `_module_rebound_names` 추가<br>- 색인 키를 대상 루트 기준으로 바꿈<br>- 반복 원소 채널을 결속·탈출 판정과 최소 고정점으로 재작성<br>- docstring «단순화(정직 기록)» 재작성<br>재검토 반영(§9):<br>- 불변 컬렉션 탈출 면제<br>- `match` 캡처·`locals()`/`vars()` 결속·탈출<br>- 상수 `MATCH_CAPTURES`·`MATCH_MAPPING`<br>- docstring 정정<br>추가 지시 반영(§10):<br>- 순수 읽기 자리 확장<br>- 상수 `PURE_COMPARE_OPS`<br>sha: `0400895d…` → `59f017b0…`(IMPL1) → `695fd0ea…`(IMPL2) → `f5aa008b…`(IMPL3) → **`0cac462393f5e836`**(IMPL4) |
| `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py` | byte 미러 |
| `dddjango/scripts/pregate_symbol_kinds.json` + Codex 미러 | 재소성. `source_sha` 1줄만 바뀐다(→ `0cac462393f5e836`). kinds 불변(`NO_BASE_MATERIAL`) |
| `…/good/…/domain_layer/order/order.py` | 클래스 끝에 `@classmethod seed_batch(cls) -> tuple["Order", ...]` 와 `@staticmethod ensure_distinct_ids(orders: tuple["Order", ...]) -> None`(재검토 반영 · 도메인 검증기) |
| `…/good/…/application_layer/order/seed_orders/` (신규 4) | `seed_orders_use_case.py`(인라인 루프 + 이름 경유 루프 · `execute(self, requested_by: str)`)와 빈 `_command/_query/_result.py` |
| `…/good/…/application_layer/order/register_orders/` (신규 4 · 재검토 M-1) | `orders: tuple[Order, ...] = tuple(Order.open_pending(i) for i in order_ids); Order.ensure_distinct_ids(orders); for order in orders: save(order)` + 빈 DTO 3개. 불변 컬렉션 면제 가드다 — 면제가 사라지면(IMPL2) exit 2 가 된다 |
| `…/good/…/application_layer/order/rank_orders/` (신규 4 · 추가 지시) | `orders: list[Order] = [Order.open_pending(i) for i in order_ids]; if orders == []: return; orders.reverse(); for order in orders: save(order)` + 빈 DTO 3개. 순수 읽기 자리 가드다 — 확장이 사라지면(IMPL3) exit 2 가 된다 |
| `…/bad_rules/…/domain_layer/order/order.py` | `from collections.abc import Sequence`, 끝에 `@staticmethod open_among(orders) -> tuple[Order, ...]`(선별 헬퍼)와 `@classmethod seed_batch(cls) -> tuple["Order", ...]`(리뷰 반영) |
| `…/bad_rules/…/order/select_orders/select_orders_use_case.py` (신규) | 인자 받는 선별 헬퍼로 조회를 돌린 뒤 필드 대입·save — «인자 허용»(P1) 회귀 가드 |
| `…/bad_rules/…/order/restock_orders/restock_orders_use_case.py` (신규 · 리뷰 M-1) | `orders = list(Order.seed_batch()); orders.extend(list_open()); for order in orders: 필드 대입·save` — 이름 단위 fail-closed 가드(IMPL1 에서 사라진다) |
| `…/bad_rules/…/order/replay_orders/replay_orders_use_case.py` (신규 · 리뷰 nit-4) + `…/bad_rules/…/driven_layer/persistence/order_record.py` (신규) | driven 의 동명 `Order.open_rows()`(무인자 · `tuple["Order", ...]` · ORM 조회)를 돌며 필드 대입·save — 도메인 출처 가드 |
| `workspace/tools/findings_count_matrix.py:134` | 최종 `(2, 22, 2, "#195×8,…", "9a82b5d48ac08380", "67a40e9a65ff7d03", "e34e0c9c727ef63f")`. HEAD 값은 `(2, 19, 2, "#195×5,…", d24236f0…, 75063fd1…, a0f21182…)`. `--emit-expected` 로 산출했고 이 키만 달랐다 |
| `workspace/tools/checker_baseline_matrix.py:261` | 최종 `(2, 22, 21, 3, False)`. HEAD 값은 `(2, 19, 18, 3, False)`. `--emit-expected` 로 산출했고 이 키만 달랐다 |
| 이 문서 | 신규 |

**불변**(`git diff` 0줄로 확인): `dddjango/scripts/rulepack.json`·Codex 미러·`ontology/**`·`ontology/LEDGER.tsv`. fixture_matrix·checker_cross_matrix 의 EXPECTED 도 그대로다. cross 는 good 만 돌리고, good 은 IMPL1 이후 바뀌지 않았다.

### EXPECTED 갱신 사유(커밋 메시지용 · 두 표 공통)

`check-transaction-boundary.py` 기본 red 레인에서 violation 이 19 에서 22 로, `#195` 가 ×5 에서 ×8 로 늘었다. 새 bad_rules fixture 3개에서 참양성이 1건씩 났기 때문이다. 해시 3종은 이 3건이 늘어서 다시 나온 값이다.

- `select_orders_use_case.py:19`
  - 모양: 조회 결과를 **인자 받는** 도메인 선별 헬퍼 `Order.open_among(...)` 로 돌린 뒤 필드를 직접 대입하고 save 한다.
  - 가드: «인자 허용» 판(P1)에서 사라진다.
- `restock_orders_use_case.py:23`
  - 모양: 무인자 도메인 컬렉션 팩토리로 지은 컬렉션에 `extend` 로 조회 결과를 섞는다.
  - 가드: 이름 단위 fail-closed 가 없는 판(리뷰 전 IMPL1)에서 사라진다.
- `replay_orders_use_case.py:19`
  - 모양: driven 에서 들여온 동명 클래스의 무인자 컬렉션 호출을 돈다.
  - 가드: 도메인 출처 조건을 뗀 변이체에서 사라진다.

## 2. 구현 요지

- 반복 대상 판정 `_elements_factory_born` 에 가지를 하나 더했다. 반복 대상이 `Call(func=Attribute(Name(C), m))` 이고, 위치 인자와 키워드 인자가 모두 0이고, `m ∈ 표[C]` 이면 참이다. 컬렉션 이름 수집과 래퍼 재귀(`tuple(..)`·`list(..)`·`set(..)`·`frozenset(..)`)는 이 가지를 그대로 탄다. 이름 단위 fail-closed(`element_other`·`loop_other`·`scalar_other`)는 건드리지 않았다.
- 표를 만드는 방식은 다음과 같다.
  - BC 마다 `domain_layer/**.py` 의 최상위 `ClassDef` 를 한 번 파싱해 색인을 만든다. 색인 키는 `application/` 아래 BC 폴더부터의 모듈 경로다. 예: `("orders","domain_layer","order","order")`.
  - 유스케이스 모듈의 최상위 절대 `from X import C`(`level == 0`)에서 X 의 끝이 색인 키와 일치할 때만 해소한다.
  - 해소한 클래스에서 `@classmethod`/`@staticmethod` 이면서 동기 `def` 이고, 반환 애너테이션의 바깥이 `COLLECTION_RETURNS` 에 들고, 원소 이름 집합이 `{C}` 또는 `{Self}` 인 메서드만 표에 올린다. 문자열 전방 참조도 해석한다.

## 3. 진단과 다른 점

1. **«같은 BC» 를 문면 그대로 적용했다.** 시제품은 색인 키를 BC 내부 경로(`domain_layer/…`)로 잡았다. 그래서 다른 BC 에 같은 경로의 클래스가 있으면 그 클래스를 import 해도 이 BC 클래스 정의를 증거로 빌렸다. 본 구현은 키에 BC 폴더 이름을 넣었다.
   - 탐침 q: 시제품 green, 본 구현 red(fail-closed).
2. **상대 import(`from ....domain_layer… import C`)는 해소하지 않는다(fail-closed).** 시제품은 접미 대조로 이를 인정했다.
   - 탐침 t: 시제품 green, 본 구현 red.
   - 현장 사본(`field-s4`·`field-copy`)의 유스케이스는 `domain_layer` import 가 **전부 절대 import** 다(field-s4 기준 절대 1737줄, 두 사본 합쳐 상대 0줄). 그래서 현장 판정은 달라지지 않는다.
   - 실례가 나오면 파일 경로 기준으로 해소를 더한다(원칙 05 — 지금은 만들지 않았다).
3. **async 메서드는 제외했다.** 표에 올리는 것은 동기 `ast.FunctionDef` 만이다. 시제품은 `AsyncFunctionDef` 도 받았다. async 메서드를 `C.m()` 로 부르면 컬렉션이 아니라 코루틴이 나온다.
4. **도메인 색인은 BC 당 1회 파싱한다.** 진단 §5 가 요구한 대로다. 시제품은 모듈마다 다시 파싱했다.
5. **docstring 정직 기록에 두 가지를 더 적었다.** 하나는 진단 §4 «남는 것» ②의 가정 밖 조건(클래스 속성·모듈 전역에 받은 인스턴스를 쌓아 두는 도메인)이다. 다른 하나는 해소하지 않는 import 모양 목록(상대·모듈 경유·최상위 밖·`__init__` 재수출)이다.
6. **이 워크트리에서 하지 않은 것**(메인 세션 몫):
   - `workspace/design/ontology-adoption-map.html` 행 추가와 `progress.md`·`step8-rehearsal.md` 기록. 셋 다 메인 체크아웃에서 수정 중이거나 미추적 파일이라, 여기서 고치면 이식할 때 충돌한다.
   - 봉인 chore 커밋.
   - 적대 검토.
7. 과제 문면의 «18 세탁 탐침»은 진단 scratch 트리 **19개**(a~p + c4)로 읽었다. 그 19개 전부와 추가 탐침 8개를 돌렸다.
8. `make verify` 를 돌리려고 워크트리에 `.venv` 심링크(→ 메인 `.venv`)를 잠시 만들었다. 인계 전에 지웠다.

## 4. 전후 결과

실행 판형은 fixture_matrix 와 같다. 임시 사본(비-git)에서 돌리고, `DJR_FINDINGS_JSON` 은 제거하고, cwd 는 워크트리 루트다. 판은 셋이다.

- HEAD: 수리 전 `dddjango/scripts` 스냅숏
- IMPL: 본 구현
- P1z: 진단 시제품

칸은 `exit/#195 줄 수/발견 줄 수` 이고, ✗ 는 기대와 다르다는 뜻이다. 실행기는 scratch `impl-D2/run_impl.py` 다.

### 4.1 요청된 4형

| 케이스 | 기대 | HEAD | IMPL |
|---|---|---|---|
| (a) `a_old_ctor` 옛 형태(생성자) | green | 0/0/0 | 0/0/0 |
| (b) `b_listcomp` · `b2_tuple_genexpr_inline` | green | 0/0/0 · 0/0/0 | 0/0/0 · 0/0/0 |
| (c) `c_domain_seed_inline` · `c2_…_named` · `c3_…_tuple_wrapped` · `c4_field_frozen_literal` | green | **2/1/1✗** ×4 | **0/0/0** ×4 |
| (d) `d_tp_repo_loop` 조회 루프 + 필드 대입(참양성) | red | 2/2/2 | 2/2/2(출력 byte = HEAD) |

### 4.2 진단 트리 19개 전부

- IMPL 출력은 19개 모두 **P1z 와 byte 동일**하다.
- 기대와 다른 칸은 두 개이고, 둘 다 진단이 예고한 것이다.
  - **h**(인자 받는 컬렉션 팩토리): HEAD 와 같은 red 로 남는다. 미해결이지 회귀가 아니다.
  - **p**(`next(iter(조회))` 스칼라 세탁): HEAD 부터 green 이다. 범위 밖의 별도 백로그다.
- 세탁 탐침 e·f·g·i·m·n·o 와 d 는 모두 red 를 유지한다. 출력도 HEAD 와 byte 동일하다.
- HEAD 에서 오탐이던 c·c2·c3·c4·k·l 은 green 이 됐다.

| 케이스 | 기대 | HEAD | IMPL |
|---|---|---|---|
| e sorted(조회) | red | 2/2/2 | 2/2/2 |
| f 선별 헬퍼(인자) | red | 2/1/1 | 2/1/1 |
| g 이름 공용 | red | 2/2/2 | 2/2/2 |
| h 인자 받는 팩토리 | green | 2/1/1✗ | 2/1/1✗(미해결 유지) |
| i list(조회) 인라인 | red | 2/2/2 | 2/2/2 |
| k 무인자 · 모듈 상수 | green | 2/1/1✗ | 0/0/0 |
| l 무인자 · append | green | 2/1/1✗ | 0/0/0 |
| m 항등 헬퍼 세탁 | red | 2/1/1 | 2/1/1 |
| n seed 이름을 조회로 재대입 | red | 2/1/1 | 2/1/1 |
| o 스칼라 조회 + 대입 | red | 2/2/2 | 2/2/2 |
| p `next(iter(조회))` | red | 0/0/0✗ | 0/0/0✗(범위 밖) |

### 4.3 추가 탐침(식별 경계 · scratch `impl-D2/make_extra.py`)

| 케이스 | 기대 | HEAD | IMPL | P1z |
|---|---|---|---|---|
| q 다른 BC 의 같은 경로 클래스 import | red | 2/1/1 | 2/1/1 | 0/0/0✗ |
| r 별칭 import(`as Kind`) | green | 2/1/1✗ | 0/0/0 | 0/0/0 |
| s 모듈 경유(`ak_mod.ActionKind.seed_catalog()`) | red | 2/2/2 | 2/2/2 | 2/2/2 |
| t 상대 import | red | 2/1/1 | 2/1/1 | 0/0/0✗ |
| u 무인자지만 `tuple[str, ...]` 반환 | red | 2/1/1 | 2/1/1 | 2/1/1 |
| w 키워드 인자 팩토리 `open_many(codes=…)` | red | 2/1/1 | 2/1/1 | 2/1/1 |
| y 모듈 함수 `seed_catalog()` | red | 2/2/2 | 2/2/2 | 2/2/2 |
| z seed 루프 뒤 같은 변수로 조회 루프 | red | 2/2/2 | 2/2/2 | 2/2/2 |

### 4.4 현장 사본과 fixture

| 대상 | HEAD | IMPL | 비고 |
|---|---|---|---|
| `field-copy`(현 클론 전 BC) | 0/0/0 | 0/0/0 | 출력 byte = HEAD |
| `field-s4`(리허설 S4 재구성) | **2/2/2** | **0/0/0** | IMPL 출력 = `field-copy` 출력(byte) — 카탈로그 외 판정 변화 0 |
| fixture good(수리 전 문면) | 0/0/0 | 0/0/0 | byte = HEAD |
| fixture bad_rules(수리 전 문면) | 2/5/19 | 2/5/19 | byte = HEAD |
| fixture good(새 문면 · seed_orders) | **2/2/2**(수리 전 red 증명 · `seed_orders_use_case.py:19`·`:23`) | 0/0/0 | |
| fixture bad_rules(새 문면 · select_orders) | 2/6/20 | 2/6/20 | P1 시제품은 19(select_orders 0) — 가드가 문다 |

## 5. 검증 명령과 결과(마지막 실행 기준 — 추가 지시 반영 후 · 검사기 `0cac462393f5e836`)

모든 명령은 워크트리 루트에서 돌렸다.
- 1·2 는 리뷰 전 1차 구현의 기록이다.
- 전 대상 재실행은 리뷰 반영 후가 §8.3, 재검토 반영 후가 §9.3, 추가 지시 반영 후가 §10.3 이다.
- 3~9 의 수치는 마지막 실행(`verify5.log`)과 같다.

| # | 명령 | 결과 |
|---|---|---|
| 1 | (리뷰 전) `python3 <scratch>/impl-D2/run_impl.py HEAD IMPL P1z` | §4 표. 진단 트리 19개에서 IMPL = P1z(byte). 추가 탐침 8/8 기대와 일치. field-s4 2→0 |
| 2 | (리뷰 반영) `python3 <scratch>/impl-D2/run_v2.py` · `guards_v2.py` | §8.3·§8.4 |
| 3 | `PYTHONUTF8=1 python3 workspace/tools/fixture_matrix.py` | 케이스 104 · 일치 104 · 불일치 0 |
| 4 | `…/findings_count_matrix.py --emit-expected` → 표 갱신 → 무인자 재실행 | 레인 73 · 일치 73 · 불일치 0 |
| 5 | `…/checker_baseline_matrix.py --emit-expected` → 표 갱신 → 무인자 재실행 | 레인 73 · 일치 73 · 불일치 0 |
| 6 | `…/checker_cross_matrix.py`(verify-base-cross 안) | census 347 행 · EXPECTED 347 행 · 차이 0건 |
| 7 | `…/gen_pregate_symbol_kinds.py` → `--check` | in-sync(종류 56 · 검사기 27종 · 양쪽 미러 일치) |
| 8 | `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__` | 무차이 |
| 9 | `make verify VERBOSE=1` | 아래 목록 |

`make verify` 타깃별 결과는 다음과 같다.

- **verify-ontology: green**
- **verify-base-cross: green**
- **verify-base-backstop: green**
- **verify-base-regen: green**(pregate-kinds 포함)
- **verify-base-core: RED**
  - 원인은 `manifest_seal.py --check --draft` 하나다. 지적 8건이 모두 봉인 드리프트다.
    - `봉인 후 변경` 3건: 검사기 · `pregate_symbol_kinds.json` · `findings_count_matrix.py`
    - `tree_sha256` 3건
    - `script_trees` 2건
  - 봉인 재발행 전에는 예상되는 red 다.
  - 이 단계 앞의 corpus·spec·checker_lint·tree·coverage·fixture·baseline·count·findings-smoke·drift·anchor·bounce·paths·rulepack(`정합 — 팩 == render(그래프)`)는 모두 통과했다.
- set -e 때문에 core 에서 봉인 단 뒤의 단계는 돌지 않았다. 그래서 따로 돌렸다.
  - `manifest_seal.py --self-test`: 변이 8종은 모두 red 로 잡혔다. M0(무변이 대조 = `--check --draft`)만 같은 봉인 드리프트로 red 다.
  - `ab_score.py --self-test`: 단언 5 · 실패 0
  - 미러 `diff -rq`: 무차이
  - REQUEST_GUIDE `cmp`: 일치
  - `request_guide_contract.py --self-test`: rc 0
  - `request_guide_contract.py`: rc 0

## 6. 메인 세션에 남는 일

1. 이 diff 를 이식한다. 신규 미추적 파일 17개가 포함된다(good 12 · bad_rules 4 · 이 문서).
2. `make verify` 를 다시 돌린다. 봉인 드리프트 외에는 green 이어야 한다.
3. 수리 커밋을 만든다. 메시지에 §1 의 EXPECTED 사유를 적는다.
4. 별도 chore 커밋으로 `manifest_seal.py --write` 를 한다(DEVELOPMENT.md §4·§6).
5. 조감도 행, `progress.md`, `step8-rehearsal.md` 에 D2 결과를 기록한다.
6. 재검토 반영분(§9)이 재검토 시제품 PROTO2b 와 byte 동일한지 확인한다. 163 대상에서 차이 0 이다.

## 7. 위험

- 전파 조건은 «선언(반환 애너테이션) + 무인자» 뿐이다. 도메인이 클래스 속성·모듈 전역·기본값 인자에 상태를 두거나 `importlib` 로 우회하면 세탁 통로가 된다(리뷰 L1·L2·L5·L7·L8·L14 · 이 수리 뒤에도 green).
  - 서비스 로케이터와 가변 레지스트리는 DDD 규범 위반이지만, 27종 어느 검사기도 애그리거트 모듈에서 이를 막지 않는다.
  - docstring «가정 밖» 에 적었다.
- 스칼라 채널 세탁(p·P·P3)과 클래스 수신자가 `method_called` 에 드는 약점은 이번 수리 범위 밖이다. HEAD 와 같다.
- 탈출 판정의 fail-closed 비용(재검토 M-1 로 정정 · §10 으로 축소): **가변** 컬렉션(list·set) 이름이 **호출 인자**(로깅·도메인 검증기·결과 DTO 등)·별칭·그 밖의 메서드 수신처럼 허용 자리 밖에서 읽히면 그 이름을 도는 루프는 전파를 잃는다. 순수 읽기(비교·`isinstance`/`len`/`bool`·`sort()`/`reverse()`·이 함수의 `return x`)는 §10 부터 허용한다.
  - 리스트 컴프리헨션 원천에서 HEAD green 이던 모양은 재검토 시점에 9종이 red 였다(F1h·F3h·F5h·F7h·F16h·F18h·F19h·F20h·F28h). 추가 지시(§10)로 순수 읽기 자리를 넓혀 6종(F1h `return x`·F5h `return tuple(x)`·F18h `==`·F19h `isinstance`·F20h `in`·F28h `sort()`)을 green 으로 되돌렸다.
  - **남는 회귀는 호출 인자 3종이다**: F3h 로깅 인자·F7h 도메인 검증기 인자·F16h 결과 DTO(`dict(items=x)`) 인자. 피호출자가 원소를 넣을 수 있어 fail-closed 로 둔다. 같은 부류로 v4 탐침 C1(`print(x)`)·C2(검증기 인자)도 red 다. docstring 에 적었다.
  - 불변 컬렉션(`tuple(..)`·`frozenset(..)`·제너레이터 식) 원천은 면제되므로 F4-20 현장 판형(`tuple(<genexpr>)`)은 회귀하지 않는다.
  - G3(`print(batch)`)은 새 원천 모양이라 HEAD 에서도 red 였다. 회귀가 아니다(앞선 서술 정정).
  - 현장 코퍼스 5종과 fixture 에서 이 경로로 판정이 바뀐 곳은 0곳이다.
- 결속 판정의 잔여 통로(docstring 한계 · fail-open)는 다음과 같다. 모두 의도하지 않고는 쓰기 어렵다.
  - 중첩 def·lambda 동명 파라미터(재검토 A1·A2·A34·A35)
  - 함수 안 `list = …` 로 복사 래퍼 가림(A9)
  - 도메인이 공유 가변 list 를 그대로 반환(A40 · 가정 밖)

## 8. 리뷰 반영(2026-09-29)

리뷰 원문은 `scratchpad/review-D2/review-195-repair.md`, 시제품은 `review-D2/proto-hardening.diff`(M-1·m-1)다.

### 8.1 처분표

| # | 등급 | 지적 | 처분 | 근거(탐침) |
|---|---|---|---|---|
| M-1 | major | 새 경로가 이름 단위 fail-closed 빈틈을 물려받는다 — `extend`·`+=`·`:=`·for target 재결속·파라미터 동명·언패킹 6모양이 HEAD red → IMPL1 green. 컴프리헨션 원천(N1h–N6h)은 HEAD 부터 green | **코드로 막음**(시제품 의미 + 확장 · §8.2)<br>fixture `restock_orders` 추가 · EXPECTED 재산출 | N1–N6 · N1h–N6h 12개 모두 red(HEAD 부터 열려 있던 h 6개 포함). 대조군 c0·L6·L11, 참양성 N7–N11 유지 |
| m-1 | minor | 클래스 이름 가림(최상위 재 import · 함수 안 재결속)으로 green | **코드로 막음**<br>- 모듈 범위(`if`·`try` 안 포함)에서 두 번 이상 묶이거나 `global` 로 선언된 이름은 표에서 뺀다<br>- 함수 안 결속·파라미터로 가린 이름은 수신자로 인정하지 않는다 | L12b·L12c red. 추가 V5(`try` 안 재 import)·V6(다른 메서드의 `global`) red — 시제품은 green |
| m-2 | minor | «가정 밖» 문면이 좁다 | **docstring 확장**: 클래스 속성·모듈 전역(기본값 인자 포함)의 상태, 곧 받은 인스턴스·자기 등록 레지스트리·주입된 로더/리포지토리·그것을 내놓는 제너레이터와 `importlib` 우회. 어느 검사기도 막지 않는다는 점과 스칼라 채널도 같은 부류라는 점도 적었다 | L1·L2·L5·L7·L8·L14 는 여전히 green(문서화된 가정 · 리뷰 판단과 같음) |
| nit-1 | nit | `#8` 근거 표기 · `importlib` 우회 | docstring·주석을 «#8·#1 — import 문 기준» 으로 고치고, `importlib` 을 가정 밖에 넣었다 | — |
| nit-2 | nit | 둘째 `application` 루트에서 «같은 BC» 접미 대조가 속는다 | **코드로 고침**. 색인 키를 대상 루트 기준 모듈 경로로 바꿨다. import 경로는 그 **접미**이면서 BC 한 칸 위(`application`)까지 담아야 한다 | X1 red(시제품 green). 현장 사본 byte 불변 |
| nit-3 | nit | docstring 누락 조건 | 동기 def 만 · 상속 메서드 미해소 · `list[C] \| None`·`Optional` 미인정 · 대상 루트 접미 조건을 적었다 | L9·L13a·L13b 는 red 유지(fail-closed) |
| nit-4 | nit | fixture 가드가 «인자 허용» 회귀만 문다 | 도메인 출처 가드 fixture `replay_orders`(+ driven `order_record.py`)를 추가했다. 애너테이션 조건 가드는 넣지 않았다 — 무인자 도메인 호출은 원리상 참양성을 만들 수 없어 규칙 문면 가드밖에 안 된다. 진단 탐침 u·y 와 리뷰 L13 이 대신 잡는다 | 변이체 MUT-origin(도메인 출처 조건 탈락)이 replay 1건을 놓친다 → EXPECTED 불일치. MUT-annot 은 fixture 로 잡히지 않는다(§8.4) |

### 8.2 구현 — 시제품과 다른 점(리뷰 밖 확장 · 재검토 권장)

시제품은 다음 두 규칙을 쓴다.
- 비단순 결속 → `element_other`
- **닫힌 목록**(`append`·`extend`·`insert`·`add`·`update`·`__iadd__`)의 변경 메서드 수신자와 첨자 대입 → `element_other`

본 구현은 같은 결속 판정 위에 규칙을 세 가지 더했다.

1. **탈출 판정**
   - 규칙: 컬렉션 이름은 다음 자리에서만 읽혀야 원소 출처를 물려준다.
     - 반복 원천
     - 복사 래퍼(`tuple/list/set/frozenset(x)`) 인자
     - 읽기 전용 자리(`len(x)`·`if/while/assert x`·`… if x else …`·`not x`)
   - 그 밖의 읽기(별칭 `a = x`·호출 인자·메서드 수신·속성/첨자 저장·`print`·`return`)가 하나라도 있으면 물려주지 않는다.
   - 효과: 닫힌 목록 밖의 변경 경로가 모두 닫힌다. 시제품은 이 경로들에서 green 이다.
     - 별칭 뒤 변경(V1·V1h)
     - 헬퍼 인자로 넘겨 채움(V2)
     - 속성으로 새어 채움(V3)
     - `appendleft`(V7)
2. **최소 고정점** — 컬렉션 값이 가리키는 이름도 같은 조건을 만족해야 한다. 대입 순서와 무관하다.
   - 효과: 복사 뒤 재대입(V4·V4h) 세탁이 닫힌다. 이 모양은 HEAD 부터 walk 순서 탓에 green 이었다.
3. **모듈 범위 가림을 `try`/`if` 안과 `global` 까지 본다**(시제품은 `mod.body` 최상위 문만 본다).
   - 효과: V5·V6 이 닫힌다.

비용: G3(`print(batch)` 뒤 루프)이 red 가 된다. 이상적으로는 green 이어야 하므로 fail-closed 오탐이다. G1(`len`)·G2(`if not`)는 green 이다. 현장 사본과 fixture 에서 바뀐 판정은 0곳이다.

> **정정(재검토 M-1)**: 위 «비용: G3» 서술은 불완전했다.
> - G3 은 새 원천 모양이라 HEAD 에서도 red 였다. 따라서 회귀가 아니다.
> - 실제 비용은 따로 있었다. 탈출 판정이 기존 F4-20 원천(컴프리헨션·`tuple(genexpr)`)에도 걸려 HEAD green 이던 모양이 red 가 됐다.
> - §9 에서 불변 컬렉션을 면제해 tuple·genexp 원천은 회복했다. 남는 리스트 컴프리헨션 쪽 비용은 §7 에 적었다.

### 8.3 전 대상 재실행(`scratch/impl-D2/run_v2.py` · 89 대상)

판은 넷이다.
- HEAD: 수리 전
- IMPL1: 리뷰 전 `59f017b0`
- PROTO: 리뷰 시제품
- IMPL2: 최종

| 묶음 | 대상 수 | IMPL2 결과 | IMPL2 ≠ IMPL1(byte) | IMPL2 ≠ PROTO(byte) |
|---|---|---|---|---|
| 진단 트리 | 19 | 기대 불일치 2(h·p — 진단 예고) | 0 | 0 |
| 구현 추가 탐침 q~z | 8 | 불일치 0 | 0 | 0 |
| 리뷰 탐침 + X1 | 42 | 불일치 16(L1·L2·L3·L4·L5·L7·L8·L14 = 가정 밖, L9·L10·L13a·L13b·L15a·L15b = fail-closed 오탐, P·P3 = 스칼라 · 모두 리뷰가 예측한 판정과 같다) | 15(L12b·L12c·N1–N6·N1h–N6h·X1 → 전부 red 로) | 1(X1) |
| 반영 새 탐침 V1–V7·G1–G3 | 12 | 불일치 1(G3 · §8.2 비용) | 10 | 10 |
| 현장 사본 field-copy·field-s4 | 2 | 0/0/0 · 0/0/0 | 0 | 0 |
| fixture(HEAD 판 · IMPL1 판 good/bad) | 4 | 기대대로 | 0 | 0 |
| fixture(WT good/bad) | 2 | 0/0/0 · 2/8/22 | 1(bad_rules — 새 fixture 2건) | 0 |

- 리뷰 권고의 byte 중립 31 대상은 IMPL2 에서도 IMPL1 과 byte 동일하다. 31 = 진단 19 + 구현 탐침 8 + 현장 2 + fixture 2.
- **판정이 바뀐 기존 fixture·현장 사본 출력은 0건이다.**
- stderr 가 나오거나 exit 1 로 끝난 경우는 0건이다.

### 8.4 fixture 가드 증명(`scratch/impl-D2/guards_v2.py` · 새 bad_rules)

| 판 | 발견 | select | restock | replay |
|---|---|---|---|---|
| HEAD | 22 | 1 | 1 | 1 |
| P1(인자 허용) | **20** | **0** | **0** | 1 |
| IMPL1(M-1 빈틈) | **21** | 1 | **0** | 1 |
| MUT-origin(도메인 출처 탈락) | **21** | 1 | 1 | **0** |
| MUT-annot(애너테이션 탈락) | 22 | 1 | 1 | 1 — fixture 로는 못 잡는다(탐침 u·L13 소관) |
| IMPL2 | 22 | 1 | 1 | 1 |

good: HEAD exit 2(#195 ×2) → IMPL2 exit 0.

### 8.5 재산출·재검증

- EXPECTED:
  - findings_count `(2, 22, 2, #195×8, 9a82b5d48ac08380 · 67a40e9a65ff7d03 · e34e0c9c727ef63f)`
  - baseline `(2, 22, 21, 3, False)`
  - 두 표 모두 `--emit-expected` 로 산출했고, 이 키만 달랐다.
- pregate 재소성 `--check` in-sync, Codex 미러 `diff -rq` 무차이.
- `make verify VERBOSE=1`:
  - ontology·cross(347 · 차이 0)·backstop·regen green.
  - core 는 봉인 드리프트 8건으로만 RED 다. 봉인 단 앞의 fixture 104/104 · count 73/73 · baseline 73/73 · checker_lint 위반 0 은 통과했다.
  - 봉인 뒤 단계는 따로 돌렸다: seal self-test 는 M0 만 드리프트로 red, ab_score 5/5, 미러·가이드 rc 0.
- 패치 `scratch/impl-D2/r8-d2.patch` 를 새로 뽑았고, `1d712d87` 기준 `git apply --cached --check` 가 통과했다.

## 9. 재검토 반영(2026-09-29)

재검토 원문은 `scratchpad/review-D2b/rereview-195-repair.md`, 시제품은 `review-D2b/proto2b.diff` 다. 탐침은 71개다.

### 9.1 처분표(재검토 행)

| # | 등급 | 지적 | 처분 | 근거(탐침) |
|---|---|---|---|---|
| 재 M-1 | major | 탈출 판정이 기존 F4-20 원천(컴프리헨션·`tuple(genexpr)`)에도 걸린다. HEAD green 이던 정상 모양 8종이 red 가 된다. 또 G3 을 «비용» 으로 든 서술이 틀렸다 | **코드로 고침**<br>- 모든 값이 불변 컬렉션(함수 안에서 가려지지 않은 `tuple(..)`·`frozenset(..)`·제너레이터 식)인 이름은 탈출 판정에서 면제(`_immutable` · 시제품과 같은 의미)<br>- good fixture `register_orders`(`tuple(<genexpr>)` 를 도메인 검증기 `Order.ensure_distinct_ids` 에 넘긴 뒤 도는 루프) 추가<br>- EXPECTED 재산출<br>- G3 서술 정정(§7·§8.2) | F1t·F7t·F16t·F19t·F1tn·F7tn·F16tn·F19tn·T1·T2 green 회복. T3·T4·K1–K10 은 red 유지.<br>가드: 새 good 에 IMPL2 → exit 2(`register_orders_use_case.py:21`), IMPL3 → exit 0, HEAD → register 는 green.<br>리스트 컴프리헨션 쪽 잔여 오탐 9종(F*h)은 docstring·§7 에 회귀로 적었다 |
| 재 m-1 | minor | 결속 판정의 잔여 통로 5종과 docstring «파라미터 … 하나라도» 과장 | **`match` 캡처·`locals()`/`vars()` 는 코드로 닫음**(시제품 7줄과 같은 의미).<br>나머지는 docstring 한계(fail-open)로 적었다: 중첩 def·lambda 동명 파라미터·함수 안 `list` 가림·도메인 공유 가변 list 반환(가정 밖).<br>«이 함수의 파라미터» 로 정정했다 | A3·A4·A5·A12(+h) red.<br>A1·A2·A34·A35(+h)·A9(+h)·A40 은 green 유지(문서화) |
| 재 nit-1 | nit | docstring «복사 래퍼 인자» 가 실제 허용 자리보다 넓다 | docstring·주석을 «반복 원천이나 단순 대입 우변에 놓인 복사 래퍼 인자» 로 좁혔다 | F5·F5h(`return tuple(x)`) red — 문면과 같다 |
| 재 nit-2 | nit | `_check_execute_body` 비대 · 헬퍼 분리 | **이번엔 하지 않음**(조정자 지시) | — |

시제품과 다른 점은 표기뿐이다.
- `ast.MatchAs`·`MatchStar`·`MatchMapping` 을 모듈 상수 `getattr(ast, …, None)` 로 받는다(`check-api-error-controller-contract.py:116-119` 선례 · 3.10 아래 파이썬 호환).
- 판정은 byte 동일하다(§9.3).

### 9.2 good fixture 추가의 발자국(`scratch/impl-D2/footprint_v3.py`)

- 검사기 26종(자기 제외)에 이전 good 과 새 good 을 돌려 stdout+exit 가 다른 것을 셌다. **0종**이다.
  - 그래서 cross 가 불변이고(347 · 차이 0), findings_count·baseline EXPECTED 도 불변이다.
  - `--emit-expected` 로 다시 산출해도 73행이 모두 기존 표와 같다.
- `ensure_distinct_ids` 는 클래스 **끝에** 붙였다. 새 import 는 없다.

### 9.3 전 대상 재실행(`scratch/impl-D2/run_v3.py` · 163 대상)

판은 넷이다.
- HEAD
- IMPL2: 재검토 전 `695fd0ea`
- PROTO2b: 재검토 시제품
- IMPL3: 최종 `f5aa008b`

| 묶음 | 대상 | IMPL3 기대 불일치 | IMPL3 ≠ IMPL2 | IMPL3 ≠ PROTO2b |
|---|---|---|---|---|
| 진단 트리 | 19 | 2(h·p) | 0 | 0 |
| 구현 탐침 q~z | 8 | 0 | 0 | 0 |
| 리뷰 탐침 + X1 | 42 | 16(§8.3 과 같음) | 0 | 0 |
| v2 탐침 | 12 | 1(G3 · HEAD 부터 red) | 0 | 0 |
| **재검토 탐침** | **71** | 29 | 18 | **0** |
| 현장 코퍼스(sds-main·sdsR·kkebi·field-copy·field-s4) | 5 | 0 | 0 | 0 |
| fixture(HEAD·IMPL1·WT 판 good/bad) | 6 | 0 | 1(good@WT — register_orders 가드) | 0 |

- 재검토 탐침에서 IMPL3 과 IMPL2 가 다른 18개는 다음과 같다.
  - red 로 돌아온 8개: A3·A4·A5·A12(+h)
  - green 으로 돌아온 10개: F1t·F7t·F16t·F19t·F1tn·F7tn·F16tn·F19tn·T1·T2
- 재검토 탐침의 기대 불일치 29개는 재검토가 예측한 판정과 모두 같다.
  - 문서화한 통로 11: A1·A2·A34·A35(+h)·A9(+h)·A40
  - 범위 밖 1: K11(HEAD 부터)
  - 새 원천 가변 list 의 탈출 8: F1·F3·F5·F7·F16·F18·F19·F20 · HEAD 에서도 red
  - 리스트 컴프리헨션 회귀 9: F*h
- **163 대상 전부 IMPL3 과 PROTO2b 가 byte 동일하다.** 현장 코퍼스 5종은 IMPL2 와도 byte 동일하다. stderr 나 exit 1 은 0건이다.

### 9.4 재검증

- fixture_matrix 104/104, count 73/73, baseline 73/73, cross 347 · 차이 0, checker_lint 위반 0, spec_lint 위반 0
- pregate 재소성(`source_sha` → `f5aa008b741f66ae`) `--check` in-sync, Codex 미러 `diff -rq` 무차이
- `make verify VERBOSE=1`(`verify4.log`)
  - ontology·cross·backstop·regen green
  - core 는 봉인 드리프트 8건으로만 RED
  - 봉인 뒤 단계는 따로 돌렸다: seal self-test 는 M0 만 드리프트로 red, ab_score 5/5, 미러·가이드 rc 0
- 가드(`guards_v2.py` 재실행): bad_rules 는 HEAD 22 · P1 20 · IMPL1 21 · MUT-origin 21 · WT 22 로 불변이고, good 은 WT exit 0 이다.
- 패치 `scratch/impl-D2/r8-d2.patch` 를 새로 뽑았고, `1d712d87` 기준 `git apply --cached --check` 가 통과했다.

## 10. 추가 지시 반영 — 순수 읽기 자리 확장(2026-09-29)

지시: 가변 컬렉션 이름이라도 원소를 들이지 못하는 순수 읽기 자리는 탈출로 보지 않는다. 호출 인자는 그대로 탈출이다.

### 10.1 처분표(추가 지시 행)

| # | 지시 | 처분 | 근거 |
|---|---|---|---|
| 추-1 | 비교 피연산자(`==`·`!=`·`in`·`not in`·`is`)·`isinstance(x, …)`/`len(x)`/`bool(x)` 인자·`x.sort(..)`/`x.reverse()`·`return x` 를 탈출에서 뺀다 | **코드로 반영**<br>- 상수 `PURE_COMPARE_OPS`(`is not` 포함)<br>- `return` 은 **이 함수 자신의** `return` 만 인정한다. 중첩 def 의 `return x` 는 그 def 를 부른 쪽으로 새므로 탈출로 둔다(E1). `lambda: x` 도 탈출이다(E4)<br>- `return tuple(x)`·`return list(x)` 처럼 복사 래퍼 인자로 돌려주는 것도 허용한다 | F1h·F5h·F18h·F19h·F20h·F28h green 회복. v4 Q1–Q6 green |
| 추-2 | 호출 인자 자리는 그대로 탈출(회귀로 남긴다) | 유지 | F3h·F7h·F16h red(HEAD green → 남는 회귀 3종). v4 C1·C2 도 같은 부류로 red |
| 추-3 | `extend`·`append`·`+=`·`[:] =`·`insert` 등 원소를 들이는 변경은 red | 확인 | v4 R1–R5 · 재검토 K1–K10 · 리뷰 N1h–N6h · v2 V1h·V4h 모두 red |
| 추-4 | 「루프 뒤 return 은 판정과 무관한지」 확인 | 확인 | `return x` 는 함수를 떠난다. 탈출해도 이 함수 안의 뒤 루프는 돌지 않는다. 그래서 허용해도 세탁 통로가 되지 않는다.<br>`try/finally` 의 finally 루프는 반환값이 호출자에 닿기 **전에** 돈다. 호출자가 원소를 넣을 틈이 없다.<br>중첩 def 의 `return` 과 `lambda` 는 제외했다(E1·E4 red) |
| 추-5 | good fixture 순수 읽기 가드 · EXPECTED 재산출 · docstring · 처분표 | 반영 | `rank_orders`(컴프리헨션 → `==` → `reverse()` → 루프).<br>IMPL3 → exit 2(`rank_orders_use_case.py:23`), IMPL4 → exit 0, HEAD 에서 rank 는 green.<br>타 검사기 발자국 26종 중 0.<br>EXPECTED 재산출 결과 불변(73행 동일) |

v4 탐침(`scratch/impl-D2/make_v4.py` · 리스트 컴프리헨션 원천 17개):
- Q1–Q6: 순수 읽기 — `bool`·`reverse`·`!=`·`is not None`·`not in`·`return list(x)`
- R1–R5: 원소 유입 — `append`·`insert`·`[:] =`·`[0] =`·`__iadd__`
- E1–E4: 순수 읽기 허용을 노린 탈출 — 중첩 def `return`·sort key 안 `append`·비교 뒤 `extend`·`lambda: x`
- C1–C2: 호출 인자

### 10.2 F 계열(재검토 탐침) 결과

칸 = exit/#195 줄 수/발견 줄 수 · ✗ = 이상과 다름.

| 모양 | 리스트 컴프리헨션(h) HEAD → IMPL3 → IMPL4 | 새 원천(`seed_list`) HEAD → IMPL3 → IMPL4 |
|---|---|---|
| `return batch`(F1) | 0 → 2✗ → **0** | 2✗ → 2✗ → **0** |
| `return tuple(batch)`(F5) | 0 → 2✗ → **0** | 2✗ → 2✗ → **0** |
| `==`(F18) | 0 → 2✗ → **0** | 2✗ → 2✗ → **0** |
| `isinstance`(F19) | 0 → 2✗ → **0** | 2✗ → 2✗ → **0** |
| `in`(F20) | 0 → 2✗ → **0** | 2✗ → 2✗ → **0** |
| `sort()`(F28h) | 0 → 2✗ → **0** | — |
| 로깅 인자(F3) | 0 → 2✗ → **2✗** | 2✗ → 2✗ → 2✗ |
| 도메인 검증기 인자(F7) | 0 → 2✗ → **2✗** | 2✗ → 2✗ → 2✗ |
| 결과 DTO 인자(F16) | 0 → 2✗ → **2✗** | 2✗ → 2✗ → 2✗ |

- 세탁 탐침 K1–K10·T3·T4 는 IMPL4 에서 모두 red 이고, IMPL3 과 byte 동일하다.
- T1·T2(tuple 원천)는 green 이다.
- K11 은 HEAD 부터 범위 밖이다.

### 10.3 전 대상 재실행(`scratch/impl-D2/run_v4.py` · 182 대상)

판은 셋이다.
- HEAD
- IMPL3: `f5aa008b` 스냅숏
- IMPL4: 최종 `0cac4623`

| 묶음 | 대상 | IMPL4 기대 불일치 | IMPL4 ≠ IMPL3 |
|---|---|---|---|
| 진단 19 · 구현 8 · 리뷰 42 · v2 12 | 81 | 19(§9.3 과 같음) | 0 |
| 재검토 71 | 71 | 18(문서화 11 · K11 1 · F3·F7·F16·F3h·F7h·F16h 6) | 11 · F1·F5·F18·F19·F20(+h)·F28h → green |
| v4 17 | 17 | 2(C1·C2 · 호출 인자 비용) | 6 · Q1–Q6 → green |
| 현장 코퍼스 5 | 5 | 0 | **0** |
| fixture(HEAD·IMPL1·IMPL3·WT 판 good/bad) | 8 | 0 | 1 · good@WT, rank_orders 가드 |

- HEAD green → IMPL4 red 는 모두 28개다.
  - 23개는 세탁 봉쇄다(이상 red): N1h–N6h, V1h, V4h, A3h, A4h, A5h, A12h, T3, T4, R1–R5, E1–E4.
  - **5개는 호출 인자 오탐이다**: F3h, F7h, F16h, C1, C2.
- 재검토 탐침 기준으로 남는 회귀 모양은 **3종**(F3h·F7h·F16h)이다.
- stderr 나 exit 1 은 0건이다.

### 10.4 재검증

- fixture_matrix 104/104 · count 73/73 · baseline 73/73(두 표 `--emit-expected` 재산출 불변) · cross 347 차이 0 · checker_lint 0 · spec_lint 0
- pregate 재소성(`source_sha` → `0cac462393f5e836`) in-sync · Codex 미러 `diff -rq` 무차이
- `make verify VERBOSE=1`(`verify5.log`)
  - ontology·cross·backstop·regen green
  - core 는 봉인 드리프트 8건으로만 RED
  - 봉인 뒤 단계는 따로 돌렸다: seal self-test 는 M0 만 드리프트로 red, ab_score 5/5, 미러·가이드 rc 0
- bad_rules 가드(`guards_v2.py`)는 22 · P1 20 · IMPL1 21 · MUT-origin 21 로 불변이다.
- 패치 `scratch/impl-D2/r8-d2.patch` 를 새로 뽑았고, `1d712d87` 기준 `git apply --cached --check` 가 통과했다.
