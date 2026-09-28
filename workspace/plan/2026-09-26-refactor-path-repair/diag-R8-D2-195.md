# 진단 R8-D2 — `check-transaction-boundary.py` #195 가 «컬렉션을 돌려주는 도메인 팩토리»의 원소를 팩토리 태생으로 보지 않는다

- 작성: 2026-09-28 · 진단만 했다. 저장소에서 수정한 파일은 0개이고 만든 파일은 이 문서 하나다. 커밋은 0이다. 리허설 사본은 읽기만 했다(`git show` 만 사용). Serena/Graphify 는 지시대로 쓰지 않았다.
- 결론: **결함은 실재한다.** 도메인이 생성을 소유할수록 red 가 되는 역전이 있다. 원인은 `_is_factory_call` 이 아니다. 반복 대상 판정 `_elements_factory_born` 이 **호출식 자체**를 원소 출처로 보지 않는 데 있다. 권고 수리안은 **P1z**(선언 증거 + 무인자)다. 반복 대상이 «같은 BC `domain_layer` 에서 import 한 클래스 C 의 `@classmethod`/`@staticmethod` 이고, 반환 애너테이션이 C(또는 `Self`)의 컬렉션이며, 인자 없이 호출된 것»이면 원소를 팩토리 태생으로 본다. 검사기 안의 국소 변경(약 35행)이고 규범 그래프·rulepack·LEDGER 는 바뀌지 않는다. 추정 약 3.5시간(적대 검토 포함).
- 표기: **[확인]** = 파일을 읽거나 명령을 돌려 확인한 사실 · **[추론]** = 판단.

## 1. 근본 원인 — `dddjango/scripts/check-transaction-boundary.py`(HEAD `1d712d87` · Codex 미러와 byte 동일 · sha256 앞 16자리 `0400895d29d9ba61`)

- [확인] 규칙 문면(9–11행): save/remove 인자는 «같은 함수 안에서 루트 메서드 호출을 받은» 객체여야 한다. 정직 기록(33–39행)에는 두 가지가 적혀 있다. «…또는 도메인 팩토리 호출로 태어났으면 통과». 반복 변수는 «원소식이 팩토리 호출인 컬렉션(`[F(..) for ..]`·`tuple(F(..) for ..)` 와 그 이름)을 돌 때만» 이를 물려받는다.
- [확인] **`_is_factory_call`(471–476행)은 «도메인 팩토리» 판정이 아니다.** 조건은 두 가지뿐이다. value 가 `Call` 이고 callee 가 `Name`/`Attribute` 일 것, 그리고 수신자(또는 속성 뿌리)가 리포지토리가 아닐 것(`_is_repo_recv` 464–469행 · `repo_names`). 도메인 층 여부도, 반환 타입도 보지 않는다. 그래서 `ActionKind.seed_catalog()` 도 이 함수에서는 **참**이다.
- [확인] 스칼라 수집(483–490행)은 `x = <Call>` 이면 `x` 를 `factory_born` 에 넣는다. 옛 형태 `kind: ActionKind = ActionKind(...)` 는 여기서 통과한다(489–490행).
- [확인] **반복 변수 전파는 `_elements_factory_born`(513–520행)이 판정하는데, 참이 되는 모양은 셋뿐이다.**
  - ① `ListComp/SetComp/GeneratorExp` 이면서 `elt` 가 `_is_factory_call` 인 것(514–515행)
  - ② 키워드 없는 단일 인자 `tuple|list|frozenset|set(<①>)`(516–519행)
  - ③ `element_factory` 에 든 이름(520행)
  - **반복 대상이 호출식 자체인 경우(`for k in C.m()`)는 어느 가지에도 들지 않아 거짓이 된다.** `_is_factory_call` 을 반복 대상에 적용하는 경로는 없다.
- [확인] 컬렉션 이름 수집(522–532행)에서 `catalog = ActionKind.seed_catalog()` 는 value 가 컴프리헨션이 아니다. 그래서 `element_other` 에 들어간다(529행). `_is_factory_call(value)` 가 참이므로 `scalar_other` 에는 들지 않는다(530–531행). 결과적으로 이름 `catalog` 는 스칼라로는 factory_born 이지만, 원소 출처로는 물려주지 않는다.
- [확인] 반복 전파(533–536행)에서 `for kind in ActionKind.seed_catalog()` 와 `for kind in catalog` 는 둘 다 `loop_other` 로 간다. 판정(545–554행)에서 `kind ∉ method_called ∪ factory_born` 이므로 «같은 함수 안에서 루트 메서드 호출을 받은 적이 없다» #195 가 난다.
  - 555–557행의 «UoW 루트 호출 0» 줄은 나오지 않는다. 501–502행이 클래스 수신자 `ActionKind` 를 `method_called` 에 넣기 때문이다(diag-B3 §4 가 이미 기록한 약점).
- [추론] **역전의 구조.** 같은 저장 원소가 어디서 보이느냐에 따라 결과가 갈린다.
  - 응용이 생성자를 직접 부르면(스칼라 489행) green 이다.
  - 응용이 컴프리헨션으로 지으면(514행) green 이다.
  - 도메인이 컬렉션으로 지어 돌려주면 원소식이 함수 밖으로 숨어 red 가 된다.
  - 이는 R-0108(`architecture-ddd` §3.3 «판정·불변식은 도메인이 소유»)이 미는 방향과 반대다.
  - F4-20 수리의 원리(«원소식에 스칼라와 같은 판정»)는 원소식이 **함수 안에 문법으로 보일 때만** 작동한다. 이번 사례는 그 범위의 사각이다.
  - 정직 기록 36–38행이 나열한 비전파 모양(튜플 언패킹·필터 체인·리터럴 목록·sorted/map/zip)에는 «컬렉션을 돌려주는 호출»이 **없다**. 리허설이 이를 «단순화»로 읽은 것은 추론이었다. 정직 기록 불비로, review-D M-3 과 같은 부류다.

## 2. 최소 재현 — 실행함

scratch: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag-D2/`

- 트리(`make_trees.py`): 케이스마다 트리를 따로 만든다. 각 트리는 `workspace/eval/fixtures/transaction_boundary/good` 사본에 다음을 더한 것이다.
  - 애그리거트 `domain_layer/action_kind/{action_kind.py, action_kind_repository.py}`
  - 유스케이스 1개 `application_layer/action_kind/<case>/<case>_use_case.py`
  - 도메인 `ActionKind.seed_catalog(cls) -> tuple["ActionKind", ...]` 는 부를 때마다 `cls(..)` 로 새로 짓는다. 리허설 원형은 별도 트리 `c4_field_frozen_literal` 로 뒀다(frozen dataclass · 코드 VO · 튜플 리터럴 `cls(..)` · `SuspensionReason`).
- 실행(`run.py` · fixture_matrix.py:201–214 와 같은 판형):
  - 임시 사본(비-git)에서 실행한다.
  - `DJR_FINDINGS_JSON` 은 제거한다.
  - cwd = 저장소 루트
  - `.venv/bin/python -B <scripts>/check-transaction-boundary.py <사본>`
  - 원문은 `out/<판>__<케이스>.txt` 에 남는다.

### 2.1 요청된 4형(HEAD)

| 케이스 | 모양 | exit | 발견 |
|---|---|---|---|
| (a) `a_old_ctor` | `for code, name in _SEEDS: … kind: ActionKind = ActionKind(code=…, name=…); save(kind)` | **0** | 없음 |
| (b) `b_listcomp` | `kinds: list[ActionKind] = [ActionKind(…) for …]; for kind in kinds: … save(kind)` | **0** | 없음 (b2 `for kind in tuple(ActionKind(…) for …)` 도 0) |
| (c) `c_domain_seed_inline` | `for kind in ActionKind.seed_catalog(): if find_by_code(kind.code) is not None: continue; save(kind)` | **2** | `[#195] …/c_domain_seed_inline_use_case.py:20: save/remove 인자 \`kind\` — 같은 함수 안에서 루트 메서드 호출을 받은 적이 없다. …` |
| (c2) `c2_domain_seed_named` | `catalog: tuple[ActionKind, ...] = ActionKind.seed_catalog(); for kind in catalog: …` | **2** | `[#195] …/c2_domain_seed_named_use_case.py:21: …받은 적이 없다…` (c3 `tuple(ActionKind.seed_catalog())` 도 2) |
| (d) `d_tp_repo_loop` | `for kind in self._repository.list_all(): kind.is_enabled = False; save(kind)` | **2** | `[#195] …:19: save/remove 인자 \`kind\` — 루트 메서드 호출 없이 필드 직접 대입만 받았다…` + `[#195] …:15: \`execute\` 이 UnitOfWork 로 쓰기를 하는데 루트 메서드 호출이 0 이다` |

### 2.2 현장 원형 재구성 — 리허설 출력과 byte 동일

- [확인] 카탈로그 코드는 커밋된 적이 없어 클론 git 이력에 없다(`git log -S"def seed_catalog"` 공백). 클론 HEAD 도 그 뒤 `386d7e7ad` 로 움직였다.
  - 대신 리허설 전사 `8-rehearsal/R8-R.t04.jsonl` 에서 S4 코더의 diff(4 파일)를 뽑았다(`diag-D2/s4_transcript_blob.txt`).
  - 클론의 `application/`·`pyproject.toml` 사본(`field-copy/`)을 만들고, 4 파일만 `git show 168bd3847:<경로>` 로 되돌린 뒤 `patch -p1` 로 적용했다(`field-s4/`).
- [확인] HEAD 검사기로 `field-s4` 를 돌리면 exit 2 에 #195 가 2줄 나온다. 위치는 `seed_action_kind_catalog_use_case.py:39`(`kind`)와 `seed_suspension_reason_catalog_use_case.py:43`(`reason`)이다.
  - 리허설 원문 `runs/S4-check-transaction-boundary.txt` 와 비교하면 #195·blocker 줄이 **byte 동일**하다(`diff` 무차이). ⓓ 후보 줄은 클론이 그 뒤 진행돼 대조하지 않았다.
- [확인] 시제품 P1z·P2 로 돌리면 `field-s4` 는 exit 0 이다. 그 출력은 카탈로그를 철회한 현 클론 사본(`field-copy`)의 출력과 byte 동일하다.
  - `field-copy` 에서는 HEAD·P1z·P2 세 판의 출력이 서로 byte 동일하다(exit 0 · #195 0). 현장 전 BC 에서 다른 판정 변화는 0건이다.

## 3. 수리안(시제품 실측)

시제품: `diag-D2/make_protos.py` 가 HEAD 검사기 사본에 블록을 끼워 `proto/<판>/scripts/` 에 만든다. 원본은 무변경이다.

- 공통 식별(P1·P1z·P2): 유스케이스 모듈의 최상위 `from …domain_layer… import C` 를 같은 BC `domain_layer/**.py` 의 모듈 경로 접미와 맞춰 `ClassDef` 로 해소한다. 거기서 다음 조건을 모두 갖춘 메서드를 «도메인 컬렉션 팩토리»로 표에 올린다.
  - `@classmethod`/`@staticmethod` 일 것
  - 반환 애너테이션의 바깥이 `tuple|Tuple|list|List|Sequence|frozenset|FrozenSet|set|Set|Iterable|Iterator|Collection` 일 것
  - 원소 이름 집합이 `{C}` 또는 `{Self}` 일 것(문자열 전방 참조 해석 포함)
- `_elements_factory_born` 에 가지 하나를 더한다. `Call(func=Attribute(Name(C), m))` 이고 `m ∈ 표[C]` 이면 참이다. 스칼라 컬렉션 이름(522–532행)과 래퍼 재귀(516–519행)는 이 가지를 그대로 탄다. 이름 단위 fail-closed(`element_other`·`loop_other`·`scalar_other`)는 손대지 않는다.

| 판 | 추가 조건 |
|---|---|
| **P1** 선언 증거 | 없음(인자 허용) |
| **P1z** 선언 증거 + 무인자 | 호출 인자 0(위치·키워드) |
| **P2** 선언 + 본문 증거 | 메서드 본문의 모든 `return` 이 `cls(..)`/`C(..)`/`cls.<m>(..)` 원소로 **새로 짓는** 컬렉션(컴프리헨션 · 래퍼 · 튜플/리스트 리터럴)일 것 · 인자 허용 |
| **P3** 대칭(순진) | 반복 대상이 `_is_factory_call` 이면 전파(대조용 — diag-B3 시제품 A 와 같은 계열) |

실측 매트릭스(`out/matrix.md` · 칸 = exit/#195 줄 수 · ✗ = 기대와 다름):

| 케이스 | 기대 | HEAD | P1 | P1z | P2 | P3 |
|---|---|---|---|---|---|---|
| a 옛 형태(생성자) | green | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| b 리스트 컴프리헨션 · b2 tuple(genexpr) 인라인 | green | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| c 도메인 seed 인라인 · c2 이름 경유 · c3 `tuple(C.seed())` | green | 2/1✗ | 0/0 | 0/0 | 0/0 | 0/0 |
| c4 현장 원형(frozen · 튜플 리터럴) | green | 2/1✗ | 0/0 | 0/0 | 0/0 | 0/0 |
| d 조회 루프 + 필드 대입(참양성) | red | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| e `sorted(repo.list_all())` 루프(참양성) | red | 2/2 | 2/2 | 2/2 | 2/2 | **0/0✗** |
| f `C.enabled_among(repo.list_all())` 선별 헬퍼 루프(참양성) | red | 2/1 | **0/0✗** | 2/1 | 2/1 | **0/0✗** |
| g 같은 이름을 seed 루프·조회 루프에 공용(참양성 · review-D 이름 단위) | red | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| h 인자 받는 컬렉션 팩토리 `C.open_many(codes)` | green | 2/1✗ | 0/0 | 2/1✗ | 0/0 | 0/0 |
| i `list(repo.list_all())` 인라인(참양성) | red | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| k 무인자 · 모듈 상수의 기성 인스턴스 반환 | green | 2/1✗ | 0/0 | 0/0 | 2/1✗ | 0/0 |
| l 무인자 · append 루프로 지음 | green | 2/1✗ | 0/0 | 0/0 | 2/1✗ | 0/0 |
| m `C.touched(repo.list_all())` = `tuple(cls.identity(k) for k in …)` 세탁 탐침(참양성) | red | 2/1 | **0/0✗** | 2/1 | **0/0✗** | **0/0✗** |
| n seed 컬렉션 이름을 조회 결과로 재대입(참양성) | red | 2/1 | 2/1 | 2/1 | 2/1 | 2/1 |
| o 스칼라 조회 + 필드 대입(참양성) | red | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| p `next(iter(repo.list_all()))` 스칼라 세탁(참양성 · §6 ③) | red | **0/0✗** | 0/0✗ | 0/0✗ | 0/0✗ | 0/0✗ |
| fixture `good` | green | 0/0 | = HEAD | = HEAD | = HEAD | = HEAD |
| fixture `bad_rules` | red | 2/19 | = HEAD | = HEAD | = HEAD | = HEAD |

(fixture 행의 «= HEAD» 는 출력 byte 동일이다. d·e·g·i·o 는 P1z·P2 출력이 HEAD 와 byte 동일하다.)

- **P1**: 인자를 받는 도메인 선별 헬퍼가 조회 결과를 그대로 돌려주면 세탁 통로가 된다(f·m green). → 기각.
- **P3**: `sorted(조회)`·선별 헬퍼를 세탁한다(e·f·m). F4-20 에서 기각한 순진 전파와 같은 결함이다. → 기각.
- **P2**: 인자 받는 팩토리(h)를 살린다. 대신 본문 모양에 민감하다. append 루프(l)·기성 상수(k)·지역 변수 경유·다른 헬퍼 위임은 red 로 남는다(fail-closed). `cls.<m>(..)` 을 생성으로 인정하면 항등 헬퍼 세탁(m)이 뚫린다. 막으려고 `cls(..)`/`C(..)` 만 인정하면 `tuple(cls.create(..) for ..)` 같은 위임 팩토리가 red 가 된다. 조건 문면도 길어져 코더가 예측하기 어렵다.
- **P1z**: 기대와 다른 칸은 h 하나다. h 는 HEAD 와 같은 red 라 **회귀가 아니라 미해결로 남는 것**이다. 세탁 탐침(e·f·m·n·i·g)은 전부 red 를 유지한다.
- (명명 관례안 — `seed_*`·`create_*` 등 이름으로 인정: 시제품 없음.) 이름 목록은 어느 규범에도 없는 재량 어휘다. `find_*` 같은 이름이 도메인에 생기면 곧바로 세탁 통로가 된다. → 기각.

## 4. 권고 — P1z(선언 증거 + 무인자)

- [추론] **근거가 원리에서 나온다.** `domain_layer` 는 밖으로 import 할 수 없다(#8 · `check-domain-model.py:5`). 그래서 **입력이 없는 도메인 클래스 호출은 조회된 애그리거트를 손에 쥘 길이 없다.** 그 원소는 도메인 안에서 태어났다는 뜻이다. 인자가 있으면 받은 인스턴스를 돌려줄 수 있으니 증거가 없다고 보고 전파하지 않는다(fail-closed). 이 한 줄이 판정 전체라서 코더가 결과를 예측할 수 있다.
- [확인] 본문 모양과 무관하다. 리터럴·컴프리헨션·append·상수(c4·c·k·l)가 모두 green 이다. 요구하는 것은 자기 타입 컬렉션 반환 애너테이션 하나뿐이다. 이는 하우스룰(모든 이름·공개 표면 애너테이션 필수)이 이미 요구하는 것이다.
- [확인] 기존 동작을 보존한다.
  - fixture good·bad_rules 출력이 HEAD 와 byte 동일하다.
  - 현장 전 BC 사본의 출력도 byte 동일하다.
  - review-D 의 이름 단위 fail-closed(g·n)와 F4-20 음성 경계(i · `close_orders`)가 유지된다.
- 남는 것(정직 기록에 적을 것):
  - ① 인자를 받는 컬렉션 팩토리(h)는 여전히 red 다. 현장에서 실례가 나오면 P2 의 본문 증거를 «인자 있음» 쪽에 OR 로 더한다. 원칙 05 에 따라 지금은 만들지 않는다.
  - ② 클래스 속성·모듈 전역에 조회 결과를 주입하는 도메인은 가정 밖이다(#8 과 서비스 로케이터 금지 아래서는 성립하지 않는 코드).
  - ③ 최상위가 아닌 import(`if TYPE_CHECKING:` 안)·모듈 import(`import …domain_layer… as m; m.C.seed()`)는 해소하지 않는다(fail-closed).
- 구현 윤곽(국소 · 다른 규칙 무영향):
  - `_check_use_case_writes`(413행~)에서 BC 마다 `domain_layer` 클래스 색인을 한 번 파싱한다.
  - 모듈마다(427행 부근) `{지역 클래스 이름: {메서드}}` 표를 만들어 `_check_execute_body`(456–459행 서명 · 453행 호출)에 넘긴다.
  - `_elements_factory_born`(513–520행) 끝의 520행 앞에 다음 한 가지를 더한다.

```python
        if (isinstance(it, ast.Call) and not it.args and not it.keywords
                and isinstance(it.func, ast.Attribute) and isinstance(it.func.value, ast.Name)
                and it.func.attr in collection_factories.get(it.func.value.id, ())):
            return True
```

## 5. 변경 면과 검증

| 대상 | 변화 | 근거·실측 |
|---|---|---|
| `dddjango/scripts/check-transaction-boundary.py` | §4 블록(헬퍼 2~3개 + 가지 1개 + 인자 전달) | 시제품 `diag-D2/proto/P1z/scripts/check-transaction-boundary.py`(단 시제품은 모듈마다 도메인을 다시 파싱한다 — 본 구현은 BC 당 1회) |
| 같은 파일 docstring 정직 기록 33–39행 | «…또는 인자 없는 도메인 컬렉션 팩토리 — 같은 BC domain_layer 에서 import 한 클래스 C 의 @classmethod/@staticmethod 로 반환 애너테이션이 C(또는 Self)의 컬렉션(`tuple[C, ...]`·`list[C]`·`Sequence[C]` 등)인 것 — 의 호출과 그 이름을 돌 때도 물려받는다(도메인은 조회를 못 하므로 — #8). 인자를 받는 컬렉션 팩토리·선별 헬퍼·(기존 목록)은 전파하지 않는다» 로 고치고, «컬렉션을 돌려주는 호출» 비전파를 명시한다 | §1 정직 기록 불비 |
| `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py` | byte 미러 | Makefile:176 `diff -rq` |
| fixture good: `…/good/application/orders/domain_layer/order/order.py` + `…/application_layer/order/seed_orders/` | `Order.seed_batch(cls) -> tuple["Order", ...]` 를 클래스 **끝에** 붙인다. `seed_orders_use_case.py`(인라인 루프 + 이름 경유 루프 · `execute(self, requested_by: str)` 1인자)와 빈 `_command/_query/_result.py` 3개를 둔다(import_orders 선례) | [확인] scratch `xgood`: **HEAD red 2줄(재현 증명) · P1z 0.** 검사기 27종 중 출력이 달라지는 것은 자기 검사기 1종뿐이다. 발자국 0 → cross-matrix 불변(처음 판은 메서드를 `place` 앞에 넣어 domain-model ⓓ 행 번호가 밀렸고, 0인자 `execute` 는 dto-placement #635 를 +1 했다 — 둘 다 위 모양으로 해소) |
| fixture bad_rules: `…/bad_rules/…/order/order.py` + `…/order/select_orders/` | `Order.open_among(orders: Sequence[Order]) -> tuple[Order, ...]`(staticmethod 선별 헬퍼 · 끝에 추가)와 `select_orders_use_case.py`(`for order in Order.open_among(self._repository.list_open()): order.status = …; save(order)`) | [확인] scratch `xbad`: HEAD 20 · **P1z 20 · P2 20 · P1 19**. «인자 허용» 회귀(P1)를 EXPECTED 불일치로 잡는 가드다 |
| `workspace/tools/findings_count_matrix.py:134` | `(2, 19→20, 2, "#195×5→×6,…", 해시 3종 재생성)` — `--emit-expected` 로 갱신하고 사유를 커밋 메시지에 적는다(같은 파일 36–37행 규율) | [확인] scratch fixtures-x + P1z 실행: 불일치 1(이 키뿐) · 시제품 해시 `8d7ea0dd27f3ada0`/`4a1af605c7102923`/`92c83e9c1a600852`(fixture 문면이 확정되면 다시 산출) |
| `workspace/tools/checker_baseline_matrix.py:261` | `(2, 19→20, 18→19, 3, False)` | [확인] 같은 실행: 불일치 1(이 키뿐) |
| `fixture_matrix.py` · `checker_cross_matrix.py` | 불변(good exit 0 · bad exit 2 · 발자국 0) | 위 실측 |
| `dddjango/scripts/pregate_symbol_kinds.json:28` + Codex 미러 | `source_sha` 재소성(`gen_pregate_symbol_kinds.py` 무인자). 이 검사기는 `NO_BASE_MATERIAL`(생성기 86–99행)이라 kinds 는 불변이고 sha 1줄만 바뀐다 | Makefile:203 `--check` |
| `dddjango/scripts/rulepack.json` · `ontology/**` · `LEDGER.tsv` | **불변.** #195 는 그래프 alias 가 없다(`ontology/wiring/aliases.ttl` 무등재 · diag-B3 §3). rulepack 은 검사기를 이름으로만 가리키고(45회) 해시를 싣지 않는다. 문면은 검사기 docstring 과 `spec_lint.py:443` 매핑뿐이고 매핑은 불변이다. graph-owned 절과 md 산문은 무변이다 | grep 실측 |
| `workspace/eval/ab/T2-0b-manifest.json:932`(봉인) | 검사기 sha 가 바뀐다. 수리 커밋 **뒤** 별도 chore 커밋으로 `manifest_seal.py --write` 한다 | DEVELOPMENT.md:128–129·156 |
| `workspace/design/ontology-adoption-map.html` | 행을 추가한다(사용자 상시 지침) | 메모리 «조감도 상시 갱신» |
| 기록 | `progress.md` 행 · `step8-rehearsal.md` 에 D2 결과 · 리허설 M8 카탈로그 부분은 수리 릴리즈 뒤 재상정할 수 있다(현재 «검사기 수리 대기 · legacy 보고») | refactor-scope.md «ⓐ 재상정 20260928-2127» |

검증 명령(모두 저장소 루트):
1. 수리 전 red 증명: 새 good 사본에 HEAD 검사기를 돌려 exit 2 · #195 2줄을 확인한다(scratch `fixture_probe.py` 판형).
2. `PYTHONUTF8=1 python3 workspace/tools/fixture_matrix.py` → 전부 일치.
3. `PYTHONUTF8=1 python3 workspace/tools/findings_count_matrix.py --emit-expected`·`checker_baseline_matrix.py --emit-expected` 로 갱신한 뒤, 무인자 재실행으로 일치를 확인한다.
4. `PYTHONUTF8=1 python3 workspace/tools/checker_cross_matrix.py` → 불변 일치.
5. `PYTHONUTF8=1 python3 workspace/tools/gen_pregate_symbol_kinds.py` 로 재소성하고 `--check` 로 확인한다.
6. `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__` → 무차이.
7. 재현 매트릭스 재실행: `python3 <scratch>/diag-D2/run.py HEAD` 에 본 구현 검사기를 넣고 돌린다. h·p 를 뺀 전 케이스가 기대와 일치하고 fixture 출력이 = HEAD 여야 한다. `field-s4` 도 exit 0 이어야 한다.
8. `make verify` green → 커밋 → `manifest_seal.py --write` chore 커밋.

## 6. 설명과 어긋나거나 설명에 없는 점

- ① **«도메인 팩토리 판정 = `_is_factory_call`» 은 사실이 아니다.** 이 함수는 «리포지토리 수신자가 아닌 모든 호출»을 참으로 본다(471–476행). `ActionKind.seed_catalog()` 도 참이다. 원인은 반복 대상 판정 `_elements_factory_born`(513–520행)이 호출식 자체를 보지 않는 데 있다. 이름 경유(c2)는 `element_other`(529행) 때문에 막힌다.
- ② **인자를 받는 도메인 컬렉션 팩토리(h `C.open_many(ids)`)도 HEAD 에서 같은 오탐이다.** 권고안 P1z 는 이것을 고치지 않는다(fail-closed 유지 · §4 남는 것 ①).
- ③ **스칼라 채널에는 이미 세탁 통로가 있다(범위 밖 · 별도 백로그).** `kind = next(iter(self._repository.list_all())); kind.is_enabled = False; save(kind)` 가 HEAD 에서 **green** 이다(p). 스칼라 판정이 «비리포지토리 호출 전부»라 `next(...)`·`max(...)`·`self._query.find()` 도 팩토리가 된다. 설명의 «도메인 팩토리 호출로 태어났으면» 보다 실제 문턱이 훨씬 낮다. 클래스 수신자가 `method_called` 에 드는 약점(501–502행 · f 의 «UoW 루트 호출 0» 줄 소실)도 diag-B3 §4 이래 그대로다.
- ④ 정직 기록 36–38행은 «컬렉션을 돌려주는 호출»을 비전파 목록에 적지 않았다. 코더·코디네이터가 «단순화»라고 부른 것은 문면이 아니라 추론이었다.
- ⑤ 증거 원형은 클론 git 이력이 아니라 **리허설 전사**(`R8-R.t02/t04.jsonl`)에서 복원했다. 카탈로그 변경은 미커밋 상태에서 철회됐고, 클론 HEAD 는 `386d7e7ad` 로 진행했다. 복원본의 #195 출력은 리허설 원문과 byte 동일하다(§2.2).

## 7. 추정

| 일 | 시간 |
|---|---|
| 검사기 구현(색인·표·가지 약 35행) + docstring 정직 기록 | 1.0h |
| fixture 2건(good `seed_orders` · bad `select_orders`) + HEAD-red·P1-red 가드 증명 | 0.5h |
| EXPECTED 2표 재산출 · pregate 재소성 · Codex 미러 · 조감도·기록 | 0.5h |
| `make verify` 1회 + 봉인 chore 커밋 | 0.5h |
| 프로젝트 관례상 적대 검토와 반영 | 1.0h |
| **합계** | **약 3.5h**(검토 제외 2.5h) |

## 8. scratch 산출물(재실행용)

`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag-D2/`
- `make_trees.py` → `trees/<케이스>/`(19 트리) · `cases.tsv`(기대)
- `make_protos.py` → `proto/{P1,P1z,P2,P3}/scripts/`
- `run.py [판…]` → 매트릭스 표 · `out/<판>__<케이스>.txt` 원문 · `out/matrix.md`
- `fixture_probe.py` → `xgood/`·`xbad/`(제안 fixture 사본) · 검사기 27종 발자국 대조
- `fixtures-x/`(제안 fixture 를 끼운 전체 fixtures 사본 — `findings_count_matrix.py`/`checker_baseline_matrix.py --scripts-dir proto/P1z/scripts --fixtures-dir fixtures-x` 산출은 `out/fcm_P1z.txt`·`out/cbm_P1z.txt`)
- `s4_transcript_blob.txt`(리허설 S4 diff 복원본) · `field-copy/`(현 클론 사본) · `field-s4/`(S4 재구성) · `out/field*__*.txt`
