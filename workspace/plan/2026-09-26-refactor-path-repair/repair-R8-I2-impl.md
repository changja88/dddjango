# 수리 R8-I2 구현 기록 — `check-transaction-boundary.py` #195 인자 받는 도메인 컬렉션 팩토리 «본문 증명»(B + 리뷰 수리)

> **최종 상태는 §8 + §9 다(검사기 `382f76c2d4e98d03`).** §0–§7 은 구현 리뷰 전 1차 구현(B + Bfix2 + Ball · 검사기 `d71fb8cb060510ac`)의 기록이다. 2026-09-29 구현 리뷰(`scratchpad/review-I2/review-I2-impl.md` · 수정 후 승인)를 받아 운영 세션이 **Ball 을 제외**했다. 무인자 호출은 R8-D2 의 선언 전파(P1z) 그대로 두고, 인자 있는 호출만 본문 증명을 요구한다. 최종 검사기 sha 는 **`cbb15e805364d24e`** 다. §0–§7 의 Ball 서술(무인자 통일 · 표→집합 · k·L6 red · MUT-P1z · `make_ball_probes.py`)은 §8 에서 되돌렸다.

- 작성: 2026-09-29 · 격리 워크트리 `.claude/worktrees/agent-a48c48a23f40de0e5` 에서 구현했다. **커밋 0 · push 0** 이다. 변경은 워크트리에 미커밋으로 남겨 두고 메인 세션이 이식한다.
- 입력
  - 진단·설계: `diag-R8-I2-arg-factory.md`(메인 체크아웃 · 미추적) · 패치 `scratchpad/diag-I2/I2-B.patch`(14 파일)
  - 적대 리뷰: `scratchpad/review-I2/review-I2.md`(수정 후 승인 · major 2 · minor 3 · nit 4) · 수리 시제품 `review-I2/proto/Bfix2`(`10c5ea0243562b53`)
  - 운영 세션 처분: Ball(무인자도 본문 증명) 포함
- 기준 커밋: 워크트리는 `acbfffda` 에서 시작했다. main `fcf051fd` 의 조상(13 커밋 뒤)이라 `git merge --ff-only main` 으로 포인터만 앞당겼다(새 커밋 없음). 아래 diff 는 `fcf051fd` 기준이다.
- 검사기 sha256 앞 16자리: 수리 전 `0cac462393f5e836` → B `5034a76e0fc4dacb` → Bfix2 `10c5ea0243562b53` → **최종 `d71fb8cb060510ac`**
- Serena·Graphify 는 쓰지 않았다. `make verify` 용 `.venv` 심링크(→ 메인 `.venv`)는 인계 전에 지웠다.

## 0. 요약

- `I2-B.patch` 를 적용하고, 리뷰 M-1·M-2·m-1 수리(`Bfix2-vs-B.diff`)와 Ball(무인자 호출도 본문 증명 요구)을 합쳤다.
- Ball 을 넣으니 호출 지점의 «선언만 있고 증명 안 된 메서드» 구분을 읽는 곳이 없어졌다. 그래서 B 가 도입한 `{메서드: 증명 여부}` 표를 HEAD 의 `{메서드}` 집합으로 되돌렸다. 집합에는 «선언 + 본문 증명» 메서드만 담긴다. 이제 `_check_execute_body` 서명은 HEAD 그대로다. 호출 지점도 HEAD 에서 무인자 조건 한 줄만 빠진 모양이다. 합친 시제품(Bfix2 + Ball 1행)과 338 대상 출력이 byte 동일한 것을 확인했다.
- docstring 정직 기록을 고쳤다(m-2 전부 + 운영 지시 5항).
- 변이 가드를 저장소에 보존했다(`evidence/i2-mutants/` · 변이체 18종 전부 잡힘). bad_rules fixture 에 `list(orders)` 로 시작하는 누적 `followup_orders` 를 더했다.
- 검증 결과
  - 행렬: fixture 104/104 · count 73/73 · baseline 73/73 · cross 347 차이 0 · drift 8/8 · checker_lint 0 · spec_lint 0 · pregate in-sync
  - 미러 무차이 · `make verify-mutation` green · `claude plugin validate dddjango --strict` 통과
  - `make verify` 는 봉인 드리프트로만 RED 다(§4.5).

## 1. 바뀐 파일

| 파일 | 변화 |
|---|---|
| `dddjango/scripts/check-transaction-boundary.py` | +290/−26(HEAD 대비). 아래 세 층을 합쳤다.<br>- B(진단 패치): 상수 2 · 새 함수 3(`_module_bound_names`·`_built_collection_factories`·`_proves_fresh`) · `_domain_class_index` 값에 증명 표<br>- Bfix2(리뷰 M-1·M-2·m-1): 클래스 본문 결속 스택 스캔 · `plain = "__new__" not in counts` · 중첩 범위 대입 fail-closed · `+` 상대 검사<br>- Ball: `_domain_collection_factories` 가 «선언 + 본문 증명» 메서드 집합을 돌려준다(HEAD 모양). 호출 지점은 무인자 조건을 뗐다<br>- docstring: 모듈 «단순화(정직 기록)» ② 재작성 · `_built_collection_factories`·`_proves_fresh`·`_domain_collection_factories` 문면 정정 · 120자 줄 1개 정리(최대 119자 = HEAD 와 같다) |
| `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py` | byte 미러 |
| `dddjango/scripts/pregate_symbol_kinds.json` + Codex 미러 | `gen_pregate_symbol_kinds.py` 재소성. `source_sha` 1줄(`0cac462393f5e836` → `d71fb8cb060510ac`)만 바뀐다. kinds 불변 |
| `…/good/…/domain_layer/order/order.py` | 진단 패치 그대로: `@classmethod open_batch(cls, order_ids)` — 빈 리스트에 `cls.open_pending(..)` append 뒤 `tuple(orders)` |
| `…/good/…/order/open_batch_orders/` (신규 4) | 진단 패치 그대로: `for order in Order.open_batch(order_ids): save(order)` + 빈 DTO 3 |
| `…/bad_rules/…/domain_layer/order/order.py` | 진단 패치(`kept`·`retouched`·`merged_with`) + **m-3(나)** `@classmethod with_followup(cls, orders)` — `batch: list[Order] = list(orders); batch.append(cls()); return batch` |
| `…/bad_rules/…/order/retouch_orders/`·`merge_orders/` (신규) | 진단 패치 그대로 — 참양성 1건씩 |
| `…/bad_rules/…/order/followup_orders/followup_orders_use_case.py` (신규 · m-3(나)) | 조회 결과를 `Order.with_followup(..)` 로 돌린 뒤 필드 대입·save — 참양성 1건. MUT-noinitcheck 에서 사라진다 |
| `workspace/tools/findings_count_matrix.py:134` | `(2, 25, 2, "#195×11,#197×3,#200×1,#282×1,#283×1,#285×1,#287×2,#355×2,#4×1,#597×1,#599×3", "2277f033009f70d2", "6b47459909f89ac6", "a5eed362b37c3616")` — `--emit-expected` 산출. 73 키 가운데 이 키만 달랐다 |
| `workspace/tools/checker_baseline_matrix.py:261` | `(2, 25, 24, 3, False)` — 같은 방식. 이 키만 달랐다 |
| `workspace/plan/2026-09-26-refactor-path-repair/evidence/i2-mutants/` (신규 7) | m-3(가): README · `base_tree.json` · 생성기 3 · `run_mutants.py` · `expected.md`(§4.3) |
| 이 문서 | 신규 |

**불변**(`git diff` 0줄): `rulepack.json`·`ontology/**`·`LEDGER.tsv`·graph-owned md·`fixture_matrix.py`·`checker_cross_matrix.py`·`construct_drift_report.py`. 진단 §5 대로 #195 는 alias 가 없고 이름으로만 결속된다.

### EXPECTED 갱신 사유(커밋 메시지용 · 두 표 공통)

`check-transaction-boundary.py` 기본 red 레인에서 violation 이 22 에서 25 로, `#195` 가 ×8 에서 ×11 로 늘었다. 새 bad_rules fixture 3개에서 참양성이 1건씩 났다. 해시 3종은 이 3건 때문에 다시 나온 값이다.

- `retouch_orders_use_case.py:19`
  - 모양: 받은 인스턴스를 그대로 돌려주는 단일 메서드(`cls.kept`)로 원소를 감싼다.
  - 가드: MUT-P1·MUT-anyclscall 에서 사라진다.
- `merge_orders_use_case.py:19`
  - 모양: 새 원소로 시작한 누적 리스트에 받은 컬렉션을 `extend` 한다.
  - 가드: MUT-P1·MUT-noreadcheck 에서 사라진다.
- `followup_orders_use_case.py:19`
  - 모양: 누적 리스트가 받은 컬렉션의 복사(`list(orders)`)로 시작한다.
  - 가드: MUT-P1·MUT-noinitcheck 에서 사라진다.

## 2. 반영 처분

| 지적 | 처분 | 결과 |
|---|---|---|
| **M-1** 클래스 본문 결속 스캔이 최상위 def 만 본다 | Bfix2 첫 hunk 반영. 클래스 본문 범위를 메서드 본문 밖까지 스택으로 훑는다. def·class 이름, import 별칭, Load 가 아닌 Name 을 센다. `plain = "__new__" not in counts` | RK1·RK2·RK3·RK4 red. 변이 MUT-noclassscan(RK1·RK3·RK4·B61)·MUT-noclassimport(RK2)가 무다 |
| **M-2** 중첩 범위 대입을 바깥 지역 대입으로 합친다 | Bfix2 둘째·셋째 hunk 반영. 중첩 def·class·lambda 안의 대입은 단순 대입으로 세지 않는다(그 target 은 «그 밖의 결속» → fail-closed) | RA11·RA12 red. MUT-nonestedscope 가 무다 |
| **m-1** `+` 피연산자 읽기를 상대와 무관하게 허용 | Bfix2 넷째 hunk 반영. 상대가 같은 이름이거나 새 컬렉션일 때만 허용한다 | RA9 red. MUT-raddany 가 무다. RA10(`__eq__`)은 가정으로 docstring 에 적었다 |
| **m-2** docstring 정정 | 반영. (1) 클래스 본문 범위에서 한 번만 묶임 (2) `__new__` 가 본문 범위 어디서도 묶이지 않을 때만 (3) 중첩 def·class·lambda 대입 (4) 가정 밖: 베이스 `__new__`·metaclass, 비교 상대의 사용자 정의 `__eq__` 등 (5) 누적 읽기 자리에 별표 풀기·`+` 피연산자(상대도 새 컬렉션) (6) 복제 문면에 `cls(**vars(k))`·`cls(**asdict(k))`·`__dict__` 대입 상태 공유 (7) 비전파 목록에 도메인 본문의 dict 값·sorted·map·reversed·`.copy()` | §3 문면 |
| **m-3** 변이 가드가 scratch 에만 있다 | (가) `evidence/i2-mutants/` 에 보존했다. 바탕 트리 번들 + 생성기 3 + 실행기 + 기대 결과를 두었고 README 에 재실행 방법을 적었다. (나) bad_rules `followup_orders` 를 추가했다 | §4.3 · 변이체 18종 전부 잡힘 · fixture 가 무는 변이 4종(P1·anyclscall·noreadcheck·noinitcheck) |
| **n-1** 고정점 O(n²) | 보류(현장 무관). §5 참고 | — |
| **n-2** `_module_bound_names`·결속 수집이 D2 코드와 중복 | 보류. 원칙 08 — D2 코드를 건드리는 리팩터라 별도 작업으로 둔다 | — |
| **n-3** 120자 줄 | 정리. 새 줄 최대 119자로 HEAD 와 같다 | — |
| **n-4** G07(증명된 컬렉션을 돌며 반복 변수를 조건부 append) fc | 보류(원칙 05 — 현장 실례가 나오면 연다) | G07 은 fc 그대로다 |
| 운영 지시 3 **Ball 포함** | 반영(§3) | 가정 밖 세탁 9개 red · k·L6 red |
| 운영 지시 4 docstring 보강 | 반영. RK5(베이스 metaclass) · RC6(`__dict__` 공유) · 복제 팩토리 한계 · 도메인 `__eq__`(RA10) 가정 · Ball 로 닫힌 것과 k·L6 이 red 인 이유 | §3 |
| (구현 판단) 증명 여부 표 → 집합 | Ball 뒤에는 `False` 항목을 읽는 곳이 없다. 그래서 `{메서드: bool}` 대신 «선언 + 증명» 집합으로 바꿨다(원칙 07). `_check_execute_body` 서명·호출 지점 판별식은 HEAD 모양으로 돌아왔다 | 합친 시제품과 338 대상 출력 byte 동일 |

## 3. Ball 포함 — 근거와 실측

- **바뀐 규칙**: 도메인 컬렉션 팩토리 호출 `C.m(..)` 은 인자 유무와 무관하게 본문 증명이 설 때만 반복 원소에 «팩토리 태생»을 물려준다. R8-D2 의 «무인자면 선언만으로»(P1z)를 본문 증명 하나로 통일했다.
- **근거**(운영 세션 설계 판단 · 진단 §6 참고 · 리뷰 §6)
  - 입력 없는 도메인 호출도 클래스 속성·모듈 전역(기본값 인자 포함)·지연 import·`importlib`·제너레이터·공유 가변 list 에 담아 둔 조회 인스턴스를 돌려줄 수 있다. P1z 는 이 9개(L1–L5·L7·L8·L14·A40)를 green 으로 통과시켰다.
  - 규칙이 한 문장이 된다: «원소는 호출마다 도메인 본문에서 새로 태어나야 한다».
- **대가 k·L6 은 red 가 맞다**(리뷰 §6 동의)
  - k 는 모듈 상수로 미리 지은 인스턴스를 돌려준다. L6 은 `functools.cache` 로 호출 사이에 같은 인스턴스를 돌려준다.
  - 둘 다 «호출마다 새로 태어남»이 아니다. 같은 인스턴스를 두 유스케이스가 저장하면 필드 대입 세탁과 같은 효과가 난다. 그래서 이상(ideal)을 red 로 고쳐 읽는다.
- **실측**(`scratchpad/impl-I2/run_impl.py` → `matrix_impl.md`)
  - 대상 338: 진단 268 + 리뷰 67 + 현장 field-now + 워크트리 fixture 2
  - 판 5: HEAD · B · Bfix2 · Ball · Impl(워크트리)
  - stderr·exit 1 은 0건이다.

| 비교 | 출력이 다른 대상 | 내용 |
|---|---|---|
| Impl vs Bfix2 | **11** | 정확히 Ball 몫이다. 가정 밖 세탁 9개(L1–L5·L7·L8·L14·A40) green→red, k·L6 green→red |
| Impl vs Ball | **7** | 정확히 리뷰 수리 몫이다. RA9·RA11·RA12·RK1–RK4 green→red |
| Impl vs B | 18 | 위 11 + 7. 겹침·상호작용 0 |
| Impl vs HEAD | 62 | 진단 의도 차이 29(B 와 같다) + 리뷰 탐침 21(G 계열 green 13 · lim 7 · RA10) + Ball 11 + 워크트리 good fixture 1. 현장 코퍼스는 FH1·FH2(의도한 green)만 다르다 |

- 현장·fixture 영향은 0 이다.
  - 현장 코퍼스 7종(구현 리뷰 m-2 정정 — 처음에 «8종»이라 잘못 셌다 · sds@25d70b636 26 BC · field-now@2bb9c4edc 26 BC · sds-main · sdsR · kkebi · field-copy · field-s4)은 HEAD 와 byte 동일하다.
  - 기존 fixture 8판(fcf051fd·HEAD-D2·IMPL1·IMPL3 × good/bad_rules)도 HEAD 와 byte 동일하다.
  - 현장에는 무인자 자기 컬렉션 팩토리가 0개다(`survey2.py` — 자기 컬렉션 팩토리 2 · 인자 받음 2 · 증명 2).
  - fixture 의 무인자 팩토리 `seed_batch`(`(cls(), cls())`)는 증명된다.
- 변이 MUT-P1z(Ball 되돌림)를 Z1–Z5 탐침(`make_ball_probes.py`)이 문다(§4.3).

## 4. 검증

### 4.1 이상 대비(Impl · 338 대상)

- 이상 불일치 ✗ 수: HEAD 77 · B 44 · Bfix2 37 · Ball 37 · **Impl 30**
- Impl 의 30개는 다음과 같다.
  - HEAD 부터 있던 27개
    - 스칼라 채널(범위 밖): p·P·P3
    - 유스케이스 쪽 identity 헬퍼: K11
    - D2 fail-open 한계: A1·A2·A9·A34·A35(+h)
    - fail-closed 오탐: L9·L10·L13a·L13b·G3·F3·F7·F16(+h)·C1·C2
  - Ball 로 이상을 red 로 고쳐 읽는 2개: k·L6
  - 문서화한 가정 1개: RA10(`__eq__`)
- 새 오탐(HEAD green·이상 green → Impl red)은 k·L6 뿐이다(§3). **[정정 — 구현 리뷰 M-1] 338 대상에 무인자 fail-closed 모양이 없어서 드러나지 않았다. 실제로는 무인자 도메인 팩토리가 증명 문법 밖(sorted·map·dict 값·모듈 헬퍼·중첩 헬퍼·replace·reversed)으로 새로 지으면 P1z green → red 였다(7개 · 그중 모듈·중첩 헬퍼 2개는 D2 가 고친 역전을 다시 연다). 이것이 Ball 제외 근거다(§8).**

### 4.2 행렬·lint(워크트리)

| 도구 | 결과 |
|---|---|
| `fixture_matrix.py` | 케이스 104 · 일치 104 |
| `findings_count_matrix.py` | 레인 73 · 일치 73(EXPECTED 갱신 뒤) |
| `checker_baseline_matrix.py` | 레인 73 · 일치 73(EXPECTED 갱신 뒤) |
| `checker_cross_matrix.py` | census 347 · EXPECTED 347 · 차이 0(새 fixture 의 타 검사기 발자국 0) |
| `construct_drift_report.py` | 대표 8종 byte 골든 일치 8 |
| `checker_lint.py` · `spec_lint.py` | 위반 0 · 위반 0 |
| `gen_pregate_symbol_kinds.py --check` | in-sync(양쪽 미러) |
| `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts` | 무차이 |
| `make verify-mutation` | 변이 12종 전건 red |
| `claude plugin validate dddjango --strict` | 통과 |

### 4.3 변이 가드(`evidence/i2-mutants/run_mutants.py --check` · 약 30초)

- 대상 157(i2 81 · review 67 · ball 7 · fixture 2) × 판 19(구현 + 변이체 18)
- 탐침 트리는 저장소 번들에서 새로 만든다. 새로 만든 트리가 scratch 원본 트리(`diag-I2/trees_i2`·`review-I2/trees_r`·바탕)와 byte 동일함을 확인했다.
- 결과: **잡히지 않은 변이체 0**. 두 번 돌려 출력이 같다(`expected.md` 대조 일치).

| 변이체 | 판정이 바뀐 탐침(요지) | bad_rules(25) |
|---|---|---|
| MUT-P1 본문 증명 요구 탈락 | 세탁 공격 전부 + Z1–Z5 | 21 — select·retouch·merge·followup 소실 |
| MUT-P1z 무인자 선언 전파(Ball 되돌림) | Z1–Z5 | 25 |
| MUT-anyclscall | B4·B50·B23·B63·RE3·RI1·RK1·RK2 | 24 — retouch 소실 |
| MUT-noreadcheck | B 계열 17 · RA 계열 8 · G07 | 24 — merge 소실 |
| MUT-noinitcheck | B1 | **24 — followup 소실(m-3 나)** |
| MUT-raddany(m-1 되돌림) | RA9 | 25 |
| MUT-nonestedscope(M-2 되돌림) | RA11·RA12 | 25 |
| MUT-noclassscan(M-1 되돌림) | B61·RK1·RK3·RK4 | 25 |
| MUT-noclassimport(M-1 되돌림) | RK2 | 25 |
| MUT-nodeco · nonew · nometa · nofirst · noyield · nonamevars · nobuiltin · nodup · nodecoshadow | 각 1–4개(B12·Z5 / B57·B63·RK3·RK4 / B58 / B8·B8b / B13b·GU3 / B20·RE5 / B56a·B56b·B62 / B61·RK1·RK2 / B65) | 25 |

### 4.4 현장

- field-now@2bb9c4edc(26 BC)
  - 출력: exit 0 · #195 0건 · HEAD 와 byte 동일
  - 도메인 전수 증명 표(`survey2.py`)는 Bfix2 와 byte 동일하다: 단일 팩토리 162 중 미증명 5 · 자기 컬렉션 팩토리 2(모두 인자 받음 · 모두 증명)
- 현장 변형 FH1·FH2(teller 반복 저장)는 HEAD red → Impl green 이다(의도).
- 실행 시간(field-now · 7회 평균, 같은 기계에서 번갈아 돌림)
  - HEAD 1.97s · B 2.43s · Bfix2 2.49s · Impl 2.34s
  - 중앙값: HEAD 1.81s · Impl 2.35s. 본문 증명 비용 약 +0.4–0.5s 다(B 부터 같다 · Ball 무관)
  - 리뷰 측정(B 2.11s vs HEAD 2.01s)보다 차이가 크다. 기계 부하 차이일 수 있다

### 4.5 `make verify`(VERBOSE=1 · 원문 scratch `impl-I2/make_verify.log`)

- verify-ontology · verify-base-cross · verify-base-backstop · verify-base-regen: **green**
  - cross: 차이 0
  - backstop: 714 통과
  - regen: pregate in-sync · behavior-guard·refactor-audit 일치
- verify-base-core: **RED — 봉인 드리프트 8건뿐**
  - 봉인 단 앞(corpus·lint·fixture·baseline·count·smoke·drift·paths·rulepack «팩 == render(그래프)»)은 모두 통과했다.
  - `manifest_seal.py --check --draft` 가 짚은 것:
    - scorer: 봉인 후 변경 `dddjango/scripts/check-transaction-boundary.py` · tree_sha256
    - packs: 봉인 후 변경 `dddjango/scripts/pregate_symbol_kinds.json` · tree_sha256
    - harness: 봉인 후 변경 `workspace/tools/findings_count_matrix.py` · tree_sha256
    - script_trees[source-claude]·[source-codex]: 봉인 `7976f52d956057bc` ≠ 실측 `7870a6712ce2d78a`
  - 지시대로 `manifest_seal.py --write` 는 돌리지 않았다. D2 선례대로 수리 커밋 뒤 별도 chore 봉인 커밋으로 푼다.
  - 봉인 단 뒤 단계는 따로 돌렸다.
    - `manifest_seal.py --self-test`: 변이 9 가운데 M0(무변이 대조)만 같은 드리프트로 red(진단 때와 같다)
    - `ab_score.py --self-test`: 5/5
    - REQUEST_GUIDE byte 미러 일치
    - `request_guide_contract.py --self-test` 157/157 · 본 검사 PASS

## 5. 남는 한계(정직 기록 · docstring 에 반영)

| 부류 | 모양 | 판정 | 비고 |
|---|---|---|---|
| 가정 밖(green) | 복제 팩토리 `cls(code=k.code, …)`·`cls(**vars(k))`·`cls(**asdict(k))`·새 인스턴스에 `__dict__` 대입(RC6 — 상태 공유) | green | 현장 0개. 필드 출처를 막으면 `after`(받은 값을 읽어 새로 지음)와 가를 수 없다 |
| 가정 밖(green) | 베이스 클래스 `__new__`·metaclass(RK5·RK6)·클래스 데코레이터(RK7)·클래스 본문 밖 메서드 바꿔 끼우기(H23) | green | 현장 metaclass 키워드 0 |
| 가정 밖(green) | 누적 이름과 비교되는 상대의 사용자 정의 `__eq__` 등이 원소를 들임(RA10) | green | 유스케이스 쪽 D2 가정과 같다 |
| fail-closed 오탐 | 재귀(H16)·상속 메서드(H17·L9)·dict 값(H18·G03)·sorted·map·reversed·`.copy()`·지역 별칭(G18)·`super()`(GU2)·중첩 제너레이터 헬퍼(GU3)·증명된 컬렉션 반복 변수 조건부 append(G07) | red | 인자 받는 팩토리에 한해 HEAD 에서도 red(무인자는 Ball 판에서만 red 였다 — 구현 리뷰 M-1 정정 · §8 에서 Ball 제외). 실례가 나오면 허용 목록에 한 줄씩 더한다(원칙 05) |
| Ball 로 red | 모듈 상수로 미리 지은 인스턴스(k)·`functools.cache` 등 데코레이터를 더 단 메서드(L6) | red | 호출 사이 같은 인스턴스 — red 가 맞다 |
| 범위 밖(HEAD 와 같음) | 스칼라 채널 `next(iter(조회))`(p·P·P3) · 유스케이스 identity 헬퍼(K11) · `save_items((item,))`(이름 아닌 save 인자) | green | 백로그 ④p |
| 성능 | 고정점 역순 의존 O(n²)(n-1) · 현장 +0.4–0.5s | — | 클래스마다 «선언된 자기 컬렉션 팩토리가 없으면 증명 생략» 같은 가지치기로 줄일 수 있다(행동 불변). 이번에는 하지 않았다 |
| 중복 | `_module_bound_names` ≈ `_module_rebound_names` · 결속 수집 ≈ `_check_execute_body`(n-2) | — | 원칙 08 — 별도 리팩터 |

## 6. `git diff --stat`(1차 구현 시점 · `fcf051fd` 기준 — 최종은 §8.6)

```
 .../dddjango/scripts/check-transaction-boundary.py | 316 +++++++++++++++++++--
 .../dddjango/scripts/pregate_symbol_kinds.json     |   2 +-
 dddjango/scripts/check-transaction-boundary.py     | 316 +++++++++++++++++++--
 dddjango/scripts/pregate_symbol_kinds.json         |   2 +-
 .../application/orders/domain_layer/order/order.py |  20 ++   (bad_rules)
 .../application/orders/domain_layer/order/order.py |   8 +    (good)
 workspace/tools/checker_baseline_matrix.py         |   2 +-
 workspace/tools/findings_count_matrix.py           |   2 +-
 8 files changed, 612 insertions(+), 56 deletions(-)
```

미추적(신규):

| 경로 | 줄 |
|---|---|
| `…/bad_rules/…/order/followup_orders/followup_orders_use_case.py` | 19 |
| `…/bad_rules/…/order/merge_orders/merge_orders_use_case.py` | 19 |
| `…/bad_rules/…/order/retouch_orders/retouch_orders_use_case.py` | 20 |
| `…/good/…/order/open_batch_orders/`(use_case 19 + 빈 DTO 3) | 19 |
| `workspace/plan/2026-09-26-refactor-path-repair/evidence/i2-mutants/`(README 49 · `base_tree.json` 21 · `make_probes_i2.py` 829 · `make_attacks.py` 790 · `make_ball_probes.py` 121 · `run_mutants.py` 240 · `expected.md` 60) | 2110 |
| 이 문서 | — |

## 7. 재실행 경로

- 저장소: `workspace/plan/2026-09-26-refactor-path-repair/evidence/i2-mutants/`(README 참고)
- scratch `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/impl-I2/`

| 파일 | 역할 |
|---|---|
| `run_impl.py [워크트리]` → `matrix_impl.md` · `out/` | 338 대상 × 5 판(HEAD·B·Bfix2·Ball·Impl) |
| `out_merged/` · `matrix_impl_merged.md` | 표→집합 단순화 전(Bfix2 + Ball 1행 합본) Impl 출력 — 단순화 뒤와 byte 대조 |
| `fcm_emit.txt` · `cbm_emit.txt` | `--emit-expected` 산출 |
| `v_*.out` · `make_verify.log` · `verify_mutation.log` | 행렬·lint·verify 원문 |
| `survey_impl.txt` | 현장 전수 증명 표(Impl) |
| `time_field.py` | 실행 시간 |
| `make_evidence.py` | scratch 생성기 → 저장소 evidence 사본 변환 |

## 8. 구현 리뷰 반영(2026-09-29 · 최종은 §9)

- 리뷰: `scratchpad/review-I2/review-I2-impl.md`(수정 후 승인 · blocker 0 · major 2 · minor 2 · nit 3) · 재현 `scratchpad/review-I2-impl/`
- 운영 세션 처분: **M-1 → Ball 제외**(무인자 = P1z 그대로 · 인자 있는 호출만 본문 증명) · M-2 수용 · 선택 sorted/reversed(조건부) · m-1·m-2·nit
- 최종 검사기 sha256 앞 16자리: **`cbb15e805364d24e`**(1차 `d71fb8cb060510ac` 에서 바꿈)

### 8.1 처분 표

| 지적 | 처분 | 결과 |
|---|---|---|
| **M-1** Ball 의 대가 과소 기재 | **Ball 제외**(운영 세션이 판단을 번복했다). 호출 지점·`_domain_collection_factories`·`_check_execute_body` 서명을 Bfix2 모양(`{메서드: 증명 여부}` · `(not (it.args or it.keywords) or 증명)`)으로 되돌렸다. docstring 에서 «무인자 통일 · Ball 로 닫힌 것 · k·L6 red 이유» 를 지우고, R8-D2 의 «이 가정 밖» 문단을 되살렸다. 이 문단은 무인자 경로의 클래스·모듈 상태 세탁(탐침 L1–L8·L14·A40·k·L6)이 HEAD 와 같이 가정 밖이라고 적는다. 1차 기록 §3·§4.1·§5 의 틀린 문장에는 정정 표시를 달았다 | 무인자 경로가 HEAD 와 byte 동일하다(§8.3) |
| **M-2** 클래스 본문 데코레이터 이름 가림(`classmethod = _launder`) | 수용. `cands` 조건에 `and m.decorator_list[0].id not in counts` 를 더했다(리뷰 1행 수리). docstring «데코레이터가 모듈·클래스 본문 어디서도 가려지지 않은» | X1 HEAD red · Bfix2 green → **Impl red**. 탐침 D1 · 변이 MUT-noclassdeco 추가 · MUT-nodecoshadow 치환 원문 갱신 |
| 선택 sorted/reversed | **넣었다**(조건을 모두 채웠다). 인자 경로 증명 문법에 `sorted(<새 컬렉션>[, key=][, reverse=])`·`reversed(<새 컬렉션>)` 를 새 컬렉션으로 인정한다. 누적 이름의 읽기 자리에도 sorted·reversed 인자를 더했다. 검사기 +6줄 · 1줄 수정 | 370 대상 중 R1(M-2 까지) 대비 바뀐 것은 G04·G12(fc→green) 둘뿐이다. 세탁 탐침은 전부 red 를 유지한다(B40 `sorted(kinds)` 포함). 현장·fixture·seed·appside 는 byte 불변이다. 표적 공격 S4·S5·S6·S8 은 red, S7(`**opts`)은 fc 다 |
| **m-1** 변이 목록·기대값 재기록 | `make_ball_probes.py` 를 지우고 `make_impl_probes.py`(18개: N 무인자 9 · D1 · S 8)로 바꿨다. MUT-P1z 를 지웠다. MUT-P1 을 호출 지점 치환으로 되돌렸고, MUT-noargproof(Ball)·MUT-noclassdeco(M-2)·MUT-sortedany 를 더했다. `expected.md` 는 `--write` 로 다시 썼다 | 대상 168 · 변이체 20 · **잡히지 않은 변이체 0** · `--check` 일치 |
| **m-2** 기록 부정확 | §4 «현장 코퍼스 8종» → 7종 · §4.1 «새 오탐 k·L6 뿐» · §5 fc 행 «HEAD 에서도 red» 에 정정 표시 | — |
| n-1 README 시간 기준 | «16코어 벽시계 약 30초(CPU 약 370초) · 코어가 적으면 길어진다» | — |
| n-2 가지치기 | 보류(행동 불변 최적화 · §5 그대로) | — |
| n-3 표→집합 동치 근거 | Ball 을 빼면서 표→집합 단순화도 되돌렸다(Bfix2 의 `{메서드: bool}` 표가 필요하다). 참고로 리뷰 §1.2 가 확인한 동치 근거는 이렇다: 같은 지역 이름의 이중 해소는 `_module_rebound_names` 가 제외하고, BC 안 `domain_layer` 중첩은 `bc_len < len(mparts)` 로 걸린다 | — |

### 8.2 Ball 제외 근거(운영 세션 판단 · 리뷰 §2.3)

- Ball 은 무인자 도메인 컬렉션 팩토리가 증명 문법 밖으로 **새로 지어도** red 로 바꾼다. 해당 모양은 7개다: sorted·map·dict 값·모듈 헬퍼·중첩 헬퍼·`replace`·reversed. HEAD(P1z)에서는 green 이었다.
- 그중 모듈 헬퍼·중첩 헬퍼 둘은 D2 가 고친 «응용이 지으면 green · 도메인이 지으면 red» 역전을 다시 연다.
- 이번 배치의 목적은 캠페인 멈춤을 줄이는 것이다. 리팩토링은 생성을 도메인으로 옮기는 쪽으로 간다. 그래서 대가(현실 모양 red)가 이득(의도적 속임 9모양 봉쇄)보다 크다고 판단했다.
- 무인자 경로의 세탁 9모양(L1–L5·L7·L8·L14·A40)과 k·L6 은 R8-D2 때처럼 가정 밖(green)으로 둔다. docstring 에 적었다.

### 8.3 재실측(`scratchpad/impl-I2/run_impl2.py` → `matrix_impl2_final.md` · `out2/`)

- 대상 370: 1차 338 + 구현 리뷰 xprobe 2(X1·X2) + seed 22(R8-R M8 원형·변형 · `make_seed_probes.py` 로 다시 만듦) + appside 8
- 판
  - HEAD
  - Bfix2
  - R1: Bfix2 + M-2 · Ball 제외 · scratch 스냅숏
  - R2: R1 + sorted/reversed
  - Impl: 워크트리
- stderr·exit 1 은 0건이다.

| 비교 | 출력이 다른 대상 | 내용 |
|---|---|---|
| R1 vs Bfix2 | **1** | X1(M-2 수리 · green→red) |
| Impl vs R2 | **0** | 워크트리 = 시제품 R2 |
| Impl vs Bfix2 | 3 | X1(M-2) · G04_sorted_fresh·G12_reversed(fc→green · sorted/reversed) |
| Impl vs HEAD | 53 | 인자 경로 몫뿐이다: 진단 의도 29 + 리뷰 탐침 21(G green 13 · lim 7 · RA10) + 워크트리 good 1 + G04·G12 |

- **무인자 경로는 HEAD 와 byte 동일하다.** Impl vs HEAD 목록에 들어 있지 않은 것:
  - 무인자 탐침: k·L1–L8·L14·A40·c0·l
  - seed 22: M8 원형 S0x 와 F1–F7·K1–K3 — 모두 HEAD 와 같이 green
  - appside 8
  - 현장 코퍼스 7종: field-now@2bb9c4edc · sds@25d70b636 · sds-main · sdsR · kkebi · field-copy · field-s4
  - 기존 fixture 8판
- 현장에서 바뀐 것은 FH1·FH2(teller 반복 저장 · 인자 경로 · 의도한 green) 뿐이다.
- 이상 불일치 ✗: HEAD 77 · Bfix2 38 · **Impl 37**
  - 36개는 HEAD 부터 있던 것이다. 무인자 가정 밖 L1–L5·L7·L8·L14·A40, 스칼라 p/P/P3, K11, D2 fail-open A 계열, fail-closed L9·L10·L13a/b·G3·F·C 가 여기 든다.
  - 나머지 1개는 RA10(문서화한 `__eq__` 가정)이다.
- 현장 전수 증명 표(field-now · `survey2.py`)는 Bfix2 와 byte 동일하다: 단일 162 중 미증명 5 · 자기 컬렉션 2(모두 인자 · 모두 증명).
- EXPECTED: `--emit-expected` 를 다시 돌렸다. 73 키 모두 워크트리 값과 같다(fixture 출력 불변 → 스플라이스 불필요).

### 8.4 검증(최종 · 워크트리 · `.venv` 심링크는 끝나고 지웠다)

| 항목 | 결과 |
|---|---|
| `make verify VERBOSE=1` | ontology·cross(347 차이 0)·backstop(714)·regen(pregate in-sync) green · core **RED 는 봉인 드리프트 8건뿐**(scorer 검사기+tree · packs pregate+tree · harness `findings_count_matrix.py`+tree · script_trees ×2 봉인 `7976f52d956057bc` ≠ 실측 `259f349bc0f47ff7`) · `--write` 는 돌리지 않았다 |
| 봉인 단 앞(core) | corpus·lint 3·tree·coverage·fixture 104/104·baseline 73/73·count 73/73·findings-smoke·drift 8/8·anchor·bounce·paths·rulepack «팩 == render(그래프)» 통과 |
| 봉인 단 뒤(따로) | seal self-test M0 만 같은 드리프트로 red · ab_score 5/5 · 미러 무차이 · REQUEST_GUIDE cmp 일치 · request_guide self-test 157/157 + PASS |
| `make verify-mutation` | 12/12 red |
| `evidence/i2-mutants/run_mutants.py --check` | `expected.md` 와 일치(대상 168 · 변이체 20 · 잡히지 않은 변이체 0) |
| checker_lint · spec_lint | 0 · 0 |
| pregate `source_sha` | 양 런타임 `cbb15e805364d24e` · `--check` in-sync |
| Codex byte 미러 | `diff -rq` 무차이 |
| `claude plugin validate dddjango --strict` | 통과 |

### 8.5 남는 한계(재검토 반영 · 최종은 §9 까지 포함)

- 인자 경로 가정 밖(green): 복제 팩토리·`__dict__` 공유 · 베이스 `__new__`·metaclass · 클래스 데코레이터 · 본문 밖 바꿔 끼우기 · RA10 `__eq__` · `builtins.X = …`·`globals()['X'] = …` 로 내장 바꿔 끼우기 · `gc.get_objects()`·`gc.get_referents()` 로 객체를 찾아 고치기(재검토 m-1).
- 무인자 경로 가정 밖(green · HEAD 와 같다): 클래스 속성·모듈 전역·기본값 인자·지연 import·`importlib`·제너레이터·공유 list 세탁(L1–L8·L14·A40) · 모듈 상수 인스턴스(k) · `functools.cache`(L6).
- fail-closed(red · 인자 경로): 재귀 · 상속 · dict 값 · map · `.copy()` · 지역 별칭 · `super()` · 중첩 제너레이터 · G07 · `sorted(.., **opts)` · 누적 이름끼리의 `+`(`tuple(out + items)` · 재검토 n-1) · 이름에 담은 역순 반복자 `r = reversed(items)`(재검토 F-1 대가).
- 범위 밖: 스칼라 p/P/P3 · K11 · `save_items((item,))`.
- 성능(n-2): 본문 증명 비용 약 +0.3–0.5s(field-now). 행동 불변 가지치기 후보는 §5 그대로다.

### 8.6 `git diff --stat`(최종 · `fcf051fd` 기준)

```
 .../dddjango/scripts/check-transaction-boundary.py | 338 +++++++++++++++++++--
 .../dddjango/scripts/pregate_symbol_kinds.json     |   2 +-
 dddjango/scripts/check-transaction-boundary.py     | 338 +++++++++++++++++++--
 dddjango/scripts/pregate_symbol_kinds.json         |   2 +-
 .../application/orders/domain_layer/order/order.py |  20 ++   (bad_rules)
 .../application/orders/domain_layer/order/order.py |   8 +    (good)
 workspace/tools/checker_baseline_matrix.py         |   2 +-
 workspace/tools/findings_count_matrix.py           |   2 +-
 8 files changed, 644 insertions(+), 68 deletions(-)
```

미추적(신규): bad_rules `followup_orders/`·`merge_orders/`·`retouch_orders/` · good `open_batch_orders/` · `evidence/i2-mutants/`(README 56 · `base_tree.json` 21 · `make_probes_i2.py` 829 · `make_attacks.py` 790 · `make_impl_probes.py` 233 · `run_mutants.py` 239 · `expected.md` 66) · 이 문서.

scratch 재실행 경로(`impl-I2/`): `run_impl2.py [판…]` · `make_seed_probes.py`(→ `seed_trees/`) · `make_r2.py`(R1 → R2 시제품) · `r1/`·`r2/` 스냅숏 · `matrix_impl2_{r1,r2,final}.md` · `make_verify2.log` · `fcm_emit2.txt`·`cbm_emit2.txt` · `cmp_emit.py` · `survey_final.txt`.

## 9. 최종 재검토 반영(2026-09-29 · 최종)

- 재검토: `scratchpad/review-I2/rereview-I2-final.md`(수정 후 승인 · blocker 0 · major 2 · minor 1 · nit 3) · 원문 `scratchpad/rereview-I2/`(수리 합본 `fixrev/scripts/` · `fixrev.diff` · 공격 `make_sr_attacks.py`)
- 최종 검사기 sha256 앞 16자리: **`382f76c2d4e98d03`**(§8 `cbb15e805364d24e` 에서 바꿈 · 양 런타임 byte 동일)
- 코드는 `fixrev.diff` 를 그대로 적용했다(+8줄 · 1줄 수정). docstring 을 뺀 AST 가 `fixrev/scripts/` 시제품과 **완전히 같다**(`impl-I2/astcmp_nodoc.py` — 다른 최상위 정의 없음 · 최상위 문장 동일). 시제품과는 docstring 만 다르다.

### 9.1 처분 표

| 지적 | 처분 | 결과 |
|---|---|---|
| **F-1** `reversed(acc)` 읽기 인정이 원본 별칭을 샌다 | 수용. 복사 래퍼 튜플에서 `"reversed"` 를 뺐다. `reversed(acc)` 가 **바로 소비되는 자리**에 있을 때만 읽기로 인정한다: 가려지지 않은 `tuple/list/set/frozenset/sorted` 의 유일 인자, for·컴프리헨션 반복 원천, 이 메서드의 return. docstring 에 대가를 적었다: `r = reversed(x)` 처럼 이름에 담으면 fail-closed | t05·t05b·t05c·t05d·t05e green→**red**. 대가 t13b green→fc. 탐침 R1(helper 누출)·R2(`__reduce__` 인라인) red · R3(for 읽기) green · R4(이름 경유 재사용) fc · 변이 MUT-reversedany 추가 |
| **F-2** 모듈 함수 `global` 로 내장을 다시 묶으면 가림 판정을 빠져나간다 | 수용. `_module_bound_names` 에 1줄: `bound \|= {n for g in ast.walk(node) if isinstance(g, ast.Global) for n in g.names}`. docstring «함수·클래스 본문이 `global` 로 선언한 이름» | S_global_fn_sorted·S_global_fn_tuple green→**red** · 탐침 G1 red · 변이 MUT-noglobalbuiltin 추가 |
| **m-1** 가정 밖 목록 누락 | 수용. 모듈 docstring «본문 밖 바꿔 끼우기» 문장에 더했다: `builtins.X = …`·`globals()['X'] = …` 로 내장을 바꿔 끼우는 코드, `gc`(`get_objects`·`get_referents`)로 객체를 찾아 고치는 코드. 기록 §8.5 도 고쳤다 | — |
| n-1 누적 둘의 `+` fc | docstring(모듈·`_built_collection_factories`)의 `+` 피연산자 문구에 «누적 이름끼리는 fail-closed» 를 넣었다. 기록 §8.5 fc 목록에도 넣었다 | t16b·t20·t23 fc 그대로(R1 부터 같다) |
| n-2 71행 한정어 | «유스케이스 반복 원천의 튜플 언패킹·필터 체인·리터럴 목록·sorted/map/zip» | — |
| n-3 R2 와 워크트리 docstring 차이 | 조치 없음. §8.3 «Impl vs R2 차이 0» 은 출력 기준이다 | — |
| evidence | `make_impl_probes.py` 에 R1–R4·G1(5개)과 `global_shadow_kind.py` 측면 모듈을 더했다. `run_mutants.py` 에 MUT-reversedany·MUT-noglobalbuiltin 을 더했다. `expected.md` 는 `--write` 로 다시 썼다. README 수치도 고쳤다 | 대상 173(i2 81 · review 67 · impl 23 · fixture 2) · 변이체 22 · **잡히지 않은 변이체 0** · `--check` 일치 |
| pregate·미러·EXPECTED | pregate `source_sha` 를 양 런타임에서 `382f76c2d4e98d03` 로 재소성했다. Codex byte 미러를 맞췄다. `--emit-expected` 를 다시 돌려 73 키 모두 같았다(fixture 출력 불변) | — |

### 9.2 실측 — 재검토 전 워크트리(Prev `cbb15e805364d24e` · `fixrev.diff` 역적용으로 복원·sha 확인) 대비

- 원문: `impl-I2/run_impl3.py` → `matrix_impl3_370.md`(370 대상) · `matrix_impl3_sr55.md`(sr 공격 55) · `out3/`
- 판: Prev · FixRev(재검토 시제품) · Final(워크트리 스냅숏)
- stderr·exit 1 은 0건이다.

| 대상 묶음 | Final vs Prev | Final vs FixRev | 차이 내용 |
|---|---|---|---|
| 370(1차 338 + xprobe 2 + seed 22 + appside 8) | **0** | 0 | — |
| sr 공격 55(t 41 · S 10 · D 4) | **8** | 0 | F-1: t05·t05b·t05c·t05d·t05e(green→red) · F-1 대가: t13b(green→fc) · F-2: S_global_fn_sorted·S_global_fn_tuple(green→red) |

- 차이는 두 구멍 몫뿐이다.
- sr 55 의 이상 불일치 ✗ 는 Prev 10 → Final 4 이다. 남는 4개는 t13b(F-1 대가) · t16b·t20·t23(R1 부터 있던 fc · n-1)이다.
- 370 대상의 이상 불일치는 §8.3 과 같다(Impl 37).

### 9.3 검증(최종 · 워크트리 · `.venv` 심링크는 끝나고 지웠다)

| 항목 | 결과 |
|---|---|
| `make verify VERBOSE=1` | ontology·cross(347 차이 0)·backstop(714)·regen(pregate in-sync) green · core **RED 는 봉인 드리프트 8건뿐**(scorer 검사기+tree · packs pregate+tree · harness `findings_count_matrix.py`+tree · script_trees ×2 봉인 `7976f52d956057bc` ≠ 실측 `d655d88f758e1e64`) · `--write` 는 돌리지 않았다 |
| 봉인 단 앞(core) | fixture 104/104 · baseline 73/73 · count 73/73 · drift 8/8 · lint·corpus·paths·rulepack 통과 |
| 봉인 단 뒤(따로) | seal self-test M0 만 같은 드리프트로 red · ab_score 5/5 · 미러 무차이 · REQUEST_GUIDE cmp 일치 · request_guide 157/157 + PASS |
| `make verify-mutation` | 12/12 red |
| `evidence/i2-mutants/run_mutants.py --check` | 일치(대상 173 · 변이체 22 · 잡히지 않은 변이체 0) |
| checker_lint · spec_lint | 0 · 0 |
| `claude plugin validate dddjango --strict` | 통과 |

### 9.4 `git diff --stat`(최종 · `fcf051fd` 기준)

```
 .../dddjango/scripts/check-transaction-boundary.py | 353 +++++++++++++++++++--
 .../dddjango/scripts/pregate_symbol_kinds.json     |   2 +-
 dddjango/scripts/check-transaction-boundary.py     | 353 +++++++++++++++++++--
 dddjango/scripts/pregate_symbol_kinds.json         |   2 +-
 .../application/orders/domain_layer/order/order.py |  20 ++   (bad_rules)
 .../application/orders/domain_layer/order/order.py |   8 +    (good)
 workspace/tools/checker_baseline_matrix.py         |   2 +-
 workspace/tools/findings_count_matrix.py           |   2 +-
 8 files changed, 674 insertions(+), 68 deletions(-)
```

미추적(신규): bad_rules `followup_orders/`·`merge_orders/`·`retouch_orders/` · good `open_batch_orders/` · `evidence/i2-mutants/`(README 56 · `base_tree.json` 21 · `make_probes_i2.py` 829 · `make_attacks.py` 790 · `make_impl_probes.py` 311 · `run_mutants.py` 248 · `expected.md` 69) · 이 문서.

### 9.5 남는 한계(최종)

§8.5 가 최종이다(m-1·n-1·F-1 대가를 반영했다). 요약:
- 인자 경로 가정 밖(green): 복제 팩토리 · `__dict__` 공유 · 베이스 `__new__`·metaclass · 클래스 데코레이터 · 본문 밖 바꿔 끼우기 · `builtins`·`globals()` 내장 교체 · `gc` 탐색 · RA10 `__eq__`
- 무인자 경로 가정 밖(green · HEAD 와 같다): L1–L8·L14·A40·k·L6
- fail-closed(인자 경로): 재귀 · 상속 · dict 값 · map · `.copy()` · 지역 별칭 · `super()` · 중첩 제너레이터 · G07 · `sorted(.., **opts)` · 누적 이름끼리의 `+` · 이름에 담은 역순 반복자
- 범위 밖: 스칼라 p/P/P3 · K11 · `save_items((item,))`
