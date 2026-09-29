# 진단·설계 R8-I2 — #195 인자 받는 도메인 컬렉션 팩토리(④h) 오탐 수리

- 작성: 2026-09-29 · 진단·설계만 했다. 저장소에서 만든 파일은 이 문서 하나이고, 수정한 파일은 0개, 커밋은 0이다. 현장 원본(`spring_dream_server`)은 `git` 읽기 명령으로만 봤고, 검사기는 `git clone --shared` 사본에서 돌렸다. Serena·Graphify 는 쓰지 않았다.
- 기준: 검사기 HEAD `fcf051fd`(`check-transaction-boundary.py` sha256 앞 16자리 `0cac462393f5e836` · Codex 미러 byte 동일).
- 현장 원본 main 은 조사 중에도 커밋이 이어졌다(`74625fdaf` → `25d70b636` → `d3260f257`). 사본은 `25d70b636` 이다. [확인] `25d70b636..d3260f257` 사이에 `application/` 변경은 0이고, `74625fdaf..25d70b636` 사이에 두 팩토리와 호출처 파일 변경도 0이다.
- 표기: **[확인]** = 파일을 읽거나 명령을 돌려 확인한 사실 · **[추론]** = 판단.

## 0. 결론

- **현장 두 형태는 HEAD 에서 지금 red 가 아니다.** [확인] 현장 사본 26 BC 전체에서 exit 0 이고 #195 는 0건이다.
  - `teller_items` 는 유스케이스가 컬렉션을 통째로 `save_items(teller_items)` 한다. 이 이름은 스칼라 채널에서 factory-born 이 된다(비리포지토리 호출 = 팩토리).
  - `DisplayOrder.after` 는 도메인 서비스 두 곳에서만 불린다. VO 이고, 스캔 대상인 `_use_case.py` 밖이다.
  - 그러나 호출처를 **반복 저장**(`for item in C.m(..): save(item)`)으로 바꾸면 HEAD 가 red 다(현장 변형 FH1·FH2). 리팩토링이 생성을 도메인으로 옮길수록 이 모양이 늘어난다. 그래서 ④h 는 **잠재 오탐**이다.
- **권장안 B — 본문 증명.** 무인자 호출은 지금처럼 선언만 본다(P1z 그대로). 인자 있는 호출은 도메인 메서드 본문이 «원소를 모두 이 본문에서 새로 짓는다»는 것을 AST 로 보일 때만 전파한다.
  - 새 원소로 인정하는 것: `cls(..)`·`C(..)`·`object.__new__(cls)`, 그리고 같은 규칙으로 증명된 같은 클래스 팩토리.
  - 컬렉션 모양: 그런 원소만 담은 컴프리헨션·리터럴·복사 래퍼, 또는 그런 원소만 들인 지역 누적 리스트.
  - 판별 기준이 «인자의 출처»가 아니라 «원소의 출생지»다. 그래서 `after(existing=조회 결과)` 도 통과한다.
- **실측(268 대상 × 8 판).**
  - B 의 출력이 HEAD 와 다른 대상은 29개다. 의도한 green 회복 27개(h·w·L15a·L15b, 새 h 계열 20, 현장 변형 2, 제안 good fixture)와 문서화한 한계 2개(H19·H23)다.
  - **나머지 239 대상은 HEAD 와 byte 동일하다.** 기존 세탁 탐침 75개는 모두 red 를 유지한다. 새 세탁 공격 55개도 B 에서 모두 red 다.
  - 현장 코퍼스 6종(26 BC 사본 포함)과 기존 fixture 8판은 byte 불변이다.
  - 행렬: fixture_matrix 104/104 · count 73/73 · baseline 73/73(각 표에서 이 검사기 키 1개만 새 fixture 몫으로 갱신) · cross 347행 차이 0 · checker_lint 0 · spec_lint 0 · pregate `--check` in-sync.
  - `make verify` 는 봉인 드리프트 8건으로만 red 다(D2 와 같은 예상 red).
- **(나) 인자 출처·(다) 매개변수 타입은 기각한다.** 현장 두 형태 가운데 적어도 하나를 막고(오탐), 새 세탁 공격 10~12개를 연다(§3).
- **남는 한계**는 §6 에 있다. fail-closed 오탐으로 재귀·상속·dict 누적이 남는다. 가정 밖으로는 복제 팩토리·클래스 밖 메서드 바꿔 끼우기·베이스 `__new__` 가 있다. 스칼라 채널 p 는 범위 밖이다.

## 1. 현장 두 팩토리

| 항목 | chat_relay `ConversationItem.teller_items` | showcase `DisplayOrder.after` |
|---|---|---|
| 위치 | `application/chat_relay/domain_layer/conversation_item/conversation_item.py:277` | `application/showcase/domain_layer/shared_value_object/display_order.py:19` |
| 서명 | `@classmethod (cls, *, room_id, turn_id, sequence_range, teller_text, widgets=(), created_at) -> tuple[ConversationItem, ...]` | `@classmethod (cls, existing: tuple[DisplayOrder, ...], count: int) -> tuple[DisplayOrder, ...]` |
| 본문 | `items: list[ConversationItem] = []` 에 `cls.for_message(..)`·`cls.for_recorded_marker(..)`·`cls.for_turn_widget(..)` 만 append 하고 `return tuple(items)`. 세 단일 팩토리는 모두 `return cls(..)` 다 | `start = max((order.value for order in existing), default=-1) + 1` · `return tuple(cls(value=start + offset) for offset in range(count))` — `existing` 은 읽기만 한다 |
| 호출처 | `commit_turn_terminal_use_case.py:96` 에서 `teller_items = ConversationItem.teller_items(...)` 한 뒤 `:104` 에서 `self._item_repository.save_items(teller_items)` | `plan_content_card_placements.py:22`·`plan_fortune_type_tab_placements.py:27`(둘 다 domain_service). 인자 `existing` 은 조회된 애그리거트에서 뽑은 차례들이다 |
| HEAD 판정(현장 사본) | [확인] green. `save_items` 인자가 이름이고, 그 이름은 스칼라 «팩토리 호출»로 factory-born 이다(반복 전파 경로를 타지 않는다) | [확인] 스캔 밖. VO 라 저장하지 않고, 유스케이스도 아니다 |
| 반복 저장으로 바꾼 현장 변형 | FH1 인라인 `for item in ConversationItem.teller_items(..): save_item(item)` → HEAD **exit 2**(`:105` #195 «루트 메서드 호출을 받은 적이 없다») · FH2 이름 경유 → HEAD **exit 2**(`:106`) · B 는 둘 다 exit 0 | 같은 본문을 애그리거트에 옮긴 합성 탐침 H2·H2n(인자 = `tuple(self._repository.list_all())`) → HEAD exit 2 · B exit 0 |

[확인] 현장 도메인 계층 전수(시제품 `survey_field.py`) 결과는 다음과 같다.

| 사본 | 자기 클래스 컬렉션 팩토리 | 인자 받음 | B 가 증명 |
|---|---|---|---|
| sds@25d70b636 | 2 | 2 | 2 |
| sdsR | 2 | 2 | 2 |
| kkebi | 0 | — | — |

같은 사본에서 단일 classmethod 팩토리(반환 애너테이션이 C·Self)는 164개다. 본문 증명 비율은 다음과 같다.

| 판 | 증명 | 비고 |
|---|---|---|
| B | 157/164 | |
| B0(`object.__new__` 관용 없음) | 139/164 | 차이 18개는 llm_access·accounts·promotion 의 «이름 있는 팩토리» 관용(`object.__new__(cls)` · 클래스가 `__new__` 로 공개 생성자를 막는 모양)이다 |

B 에서 증명되지 않는 7개는 다음과 같다. 모두 새로 짓지 않으므로 증명 실패가 맞다.
- 표 조회: `EarthlyBranch.from_index` 등 3개
- 열거 멤버: `DisplayLanguage.from_display_code`·`ValueKind.from_range_curie`
- Optional 반환: `SalesPeriod.from_optional`·`FactKind.static_from_type_name`

## 2. 후보

| 판 | 인자 있는 `C.m(..)` 을 전파하는 조건(무인자는 모든 판이 P1z 그대로) |
|---|---|
| **B(권장)** 본문 증명 | m 의 모든 return 이 새 원소만 담은 컬렉션이다. 새 원소 = `cls(..)`·`C(..)`·`cls.__new__(cls)`(셋 다 클래스 본문에 `__new__` 가 없을 때만)·`object.__new__(cls)`·증명된 C 의 단일 팩토리 `cls.f(..)`·그런 값에만 묶인 지역 이름·양쪽이 새 원소인 조건식. 컬렉션 = 컴프리헨션·리터럴·복사 래퍼·`+`·조건식·증명된 컬렉션 팩토리, 또는 누적 이름(§4) |
| B0 | B 에서 `object.__new__`·`cls.__new__` 를 뺀 판. 클래스가 `__new__` 를 정의하면 그 클래스를 통째로 증명하지 않는다 |
| (나) O 인자 출처 | 인자식에 리포지토리 호출이 없고, 리포지토리 호출에서 파생된 이름(대입·반복 고정점)도 없다. 선언(반환 애너테이션)만 본다 |
| (다-1) T 매개변수 타입(엄격) | cls 밖 모든 파라미터가 애너테이션을 갖고, 그 애너테이션이 {C, Self, object, Any} 를 언급하지 않는다 |
| (다-2) T2 매개변수 타입(느슨) | 금지 목록이 {C, Self} 뿐이다 |
| (참고) P1 | 선언만 본다(진단 기각안) |
| (참고) P2 | 진단 P2 를 재현한 판. 원소 = `cls(..)`·`C(..)`·`cls.<아무 메서드>(..)` · 누적·지역 이름·컬렉션 재귀 없음 |

## 3. 실측 — 탐침 비교

- 실행기는 `diag-I2/run_i2.py` 다. 판형은 fixture_matrix 와 같다: 임시 비-git 사본, `DJR_FINDINGS_JSON` 제거, `-B`, cwd 는 저장소 루트다.
- 대상은 268개다: 진단 19 · 구현 추가 8 · 리뷰 41+X1 · v2 12 · 재검토 71 · v4 17 · **I2 새 탐침 81** · 현장 8 · fixture 10.
- stderr 나 exit 1 은 0건이다. 원문은 `diag-I2/out/<판>__<대상>.txt`, 전체 표는 `matrix_v4.md` 에 있다.

### 3.1 묶음별 요약(칸 = 이상대로 나온 수 / 대상 수)

| 묶음 | 대상 | HEAD | **B** | B0 | P1 | P2 | O | T | T2 |
|---|---|---|---|---|---|---|---|---|---|
| 기존 세탁 탐침(HEAD red · 이상 red) | 75 | 75 | **75** | 75 | 73 | 74 | 75 | 75 | 75 |
| I2 세탁 공격(이상 red) | 55 | 55 | **55** | 55 | 1 | 54 | 44 | 45 | 43 |
| h 계열·현장 변형(이상 green) | 27 | 1 | **27** | 25 | 27 | 18 | 23 | 20 | 25 |
| fc — 이상은 green, fail-closed red 수용 | 3 | 0 | 0 | 0 | 2 | 0 | 2 | 2 | 2 |
| lim — 이상은 red, 한계 green 수용 | 2 | 2 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| 전체 이상 불일치(✗ · fc·lim 제외) | 268 | 63 | **36** | 38 | 92 | 48 | 51 | 53 | 50 |
| HEAD 와 출력이 다른 대상 | 268 | 0 | **29** | 27 | 91 | 22 | 37 | 33 | 40 |

- B 에 남는 불일치 36개는 모두 HEAD 에 이미 있던 한계다. 새로 생긴 것은 0이다.
  - 가정 밖 세탁: L1–L5·L7·L8·L14·A40·K11
  - 스칼라 채널: p·P·P3
  - fail-closed 오탐: L9·L10·L13a·L13b·G3·A1/A2/A9/A34/A35(+h)·F3/F7/F16(+h)·C1·C2
- 비교 판이 여는 세탁 공격과 막는 green 모양은 다음과 같다.

| 판 | 뚫리는 세탁 공격(이상 red → green) | 막히는 green(이상 green → red) |
|---|---|---|
| P1 | I2 공격 54/55 + f·m | — |
| P2 | m · B23(`cls.lookup` 레지스트리 위임) | H1·H1n·H1f·FH1·FH2(누적 리스트 · teller 모양) · H6(컬렉션 재귀) · H8 · H9 · H22 |
| O | 호출 인자가 명령 파라미터(`codes`)라 출처가 «깨끗한» 상태·클래스 수준 세탁 9개(B23·B33·B34·B26·B56b·B57·B58·B63·B65) · O1(리포지토리가 아닌 조회 포트) · O2(호출자가 넘긴 인스턴스) | **H2·H2n(after · 인자 = 조회 결과)** · **FH1·FH2**(`sequence_range` 가 `reserve_sequence_range` 조회 결과이고 `widgets` 가 저장 뒤 다시 읽은 turn 에서 나온다) |
| T | O 와 같은 상태·클래스 수준 9개 · B61(클래스 본문 이름 중복) | **H1·H1n·H1f·FH1·FH2**(`Mapping[str, object]`) · **H2·H2n**(`existing: tuple[C, ...]`) |
| T2 | T 의 10개 · B59a·B59b(`Sequence[object]`·`Sequence[Any]` 로 받아 골라냄) | **H2·H2n** |
| B0 | — | H21·H22(`object.__new__` 관용) |

[추론] (나)·(다)는 «인자에 C 가 들어올 수 있는가»를 묻는다. 그런데 `after` 는 C 를 받고도 원소를 새로 짓고, `teller_items` 는 조회에서 파생된 값을 받고도 원소를 새로 짓는다. 그래서 두 안은 현장 형태를 막는다. 게다가 인자가 깨끗해도 클래스·모듈 상태로 세탁하는 모양은 인자와 무관하게 열린다. 원소의 출생지를 직접 증명하는 B 만 두 목표(현장 green · 세탁 red)를 함께 만족한다.

### 3.2 기존 명명 탐침(요청 목록) — 판별 요약

G = green, R = red, ✗ = 이상과 다름. 전체 행은 `diag-I2/named_probes.md` 에 있다.

| 탐침 | 이상 | HEAD | B | B0 | P1 | P2 | O | T | T2 |
|---|---|---|---|---|---|---|---|---|---|
| a·b·b2·c·c2·c3·c4·k·l·r·L6·L11 | G | G | G | G | G | G | G | G | G |
| **h**(인자 받는 팩토리)·**w**(키워드 인자)·**L15a/L15b**(`*[]`·`**{}`) | G | R✗ | **G** | G | G | G | G | G | G |
| d·e·g·i·n·o·q·s·t·u·y·z·L12a/b/c·N1h–N6h·K1–K10·T3·T4·R1–R5·E1–E4 | R | R | R | R | R | R | R | R | R |
| f(선별 헬퍼) | R | R | R | R | G✗ | R | R | R | R |
| m(항등 헬퍼 `cls.identity`) | R | R | R | R | G✗ | G✗ | R | R | R |
| p·L1–L5·L7·L8·L14·K11(범위 밖·가정 밖) | R | G✗ | G✗ | G✗ | G✗ | G✗ | G✗ | G✗ | G✗ |
| L9·L10·L13a·L13b(fail-closed) | G | R✗ | R✗ | R✗ | R✗ | R✗ | R✗ | R✗ | R✗ |

- w 의 이상 판정은 D2 때 «red(fail-closed)» 였다. 본문이 증명되는 팩토리를 키워드로 부르는 것은 h 와 같은 부류라 이상을 green 으로 고쳤다. L15a/b 는 D2 리뷰 때부터 이상이 green 이었다.

### 3.3 I2 새 탐침(81 · `make_probes_i2.py`)

- **이상 green 21개**(B 는 21개 모두 green · HEAD 는 H15 만 green)
  - 진단 h 의 위치 인자판 H0
  - teller 모양 H1·H1n·H1f(필드 대입까지)
  - after 모양 H2·H2n(인자 = 조회 결과)
  - 리터럴 H3 · 단일 팩토리 위임 H4 · staticmethod `C(..)` H5 · 컬렉션 재귀 `+` H6 · 조기 `()` H7
  - 누적 H8(`[..]` 시작·extend(genexp)·`+=`·insert·sort) · 지역 이름 원소 H9 · 조건식 원소 H10 · `klass` 첫 파라미터 H11 · 정적 위임 H12
  - 호출 지점 래퍼·별표 H13·H14 · 통째 save H15(HEAD 부터 green)
  - `object.__new__` H21 · `__new__` 로 공개 생성자를 막은 클래스 H22
  - 나머지 H 탐침 5개는 아래 fc(H16~H18)·lim(H19·H23)에, H20 은 red 에 들어 있다
- **이상 red 55개**(B 는 55개 모두 red). 누적 이름 공격, 원소 공격, 이름 가림, 클래스 수준 가정, 출처·타입안을 노린 공격으로 나뉜다.
  - 누적 이름 공격
    - 결속 값: B1 인자로 시작 · B19 재결속 `items + list(kinds)` · B45 nonlocal 재결속
    - 받은 것을 들임: B2 `extend(kinds)` · B3 반복 append · B17 `+= list(kinds)` · B28 `__iadd__` · B30 `insert(0, kinds[0])` · B49 `extend(k for k in kinds)` · B50 증명 안 된 팩토리를 extend · B51 `append(max(kinds))`
    - 저장·탈출: B16 첨자 대입 · B18 슬라이스 대입 · B35 별칭 뒤 extend · B47 `list.append(items, ..)` · B5 헬퍼에 넘김
    - 중첩 범위: B14 중첩 def 에서 append · B15 sort key lambda 에서 append
    - 이름 공간: B27 `locals()` · B48 `vars()`
  - 원소 공격: B4 `cls.identity(k)` · B7 조건식 한쪽이 받은 원소 · B20 원소 이름 재결속 · B21 walrus · B23 `cls.lookup` 레지스트리 · B38 `dataclasses.replace`
  - return 공격: B6 한 갈래가 인자 반환 · B31 `+ tuple(kinds)` · B32 `(*items, *kinds)` · B40 `sorted(kinds)` · B41 중첩 def 반환 · B44 조건식 반환
  - 이름 가림: B8 `cls = …` · B8b 컴프리헨션 target 으로 `cls` 가림 · B9 staticmethod 첫 파라미터 이름이 cls · B10 지역에서 `C` 가림 · B56a 지역 `tuple` 가림 · B56b 모듈 `tuple` 가림 · B62 지역 `object` 가림 · B65 모듈 `classmethod` 가림
  - 클래스 수준 가정: B12 추가 데코레이터 · B13·B13b yield(+`return ()`) · B26 모듈 범위 클래스 이름 재결속 · B33 global 누적 · B34 클래스 속성 누적 · B57 `__new__` 풀 · B58 metaclass `__call__` · B61 클래스 본문 이름 중복(`dup = staticmethod(..)`) · B63 `__new__` 풀 + `cls.__new__(cls)`
  - 출처·타입안 공격: B59a/b `object`·`Any` 파라미터 · O1 조회 포트 · O2 호출자 인스턴스
  - 반복 변수 쪽 이름 단위 fail-closed 유지: H20 증명된 팩토리 결과를 list 로 받아 조회 결과를 extend
- **fc 3개**: H16 재귀 · H17 상속 메서드 · H18 dict 누적. **lim 2개**: H19 복제 팩토리 · H23 모듈 범위 메서드 바꿔 끼우기(§6).

### 3.4 현장 코퍼스와 fixture

| 대상 | HEAD | B | B 출력 = HEAD |
|---|---|---|---|
| sds@25d70b636(26 BC · 새 사본) | 0/0/0 | 0/0/0 | byte 동일 |
| sds-main · sdsR · kkebi(D2 재검토 사본) · field-copy · field-s4 | 모두 0/0/0 | 모두 0/0/0 | byte 동일 |
| FH1·FH2(현장 변형 · 반복 저장) | 2/1/1 | **0/0/0** | 의도한 차이 |
| 기존 fixture 8판(HEAD-D2·IMPL1·IMPL3·fcf051fd × good/bad_rules) | — | — | 8판 모두 byte 동일 |
| 제안 good(`open_batch_orders`) | **2/1/1**(`open_batch_orders_use_case.py:19` — 수리 전 red 증명) | 0/0/0 | 의도한 차이 |
| 제안 bad_rules(+`retouch_orders`·`merge_orders`) | 2/10/24 | 2/10/24 | byte 동일(두 참양성 모두 red) |

칸 = exit/#195 줄 수/발견 줄 수. 실행 시간은 현장 사본에서 HEAD 2.09s, B 2.01s 다.

### 3.5 행렬·lint(저장소 `--shared` 사본 `diag-I2/repo` 에 B·fixture·EXPECTED·pregate 를 적용해 실행)

| 도구 | 결과 |
|---|---|
| `fixture_matrix.py` | 케이스 104 · 일치 104 |
| `findings_count_matrix.py` | `--emit-expected` 로 73행을 대조했다. 다른 키는 `check-transaction-boundary.py` 하나다: `(2, 22, 2, "#195×8,…", 9a82b5d4…, 67a40e9a…, e34e0c9c…)` → **`(2, 24, 2, "#195×10,#197×3,#200×1,#282×1,#283×1,#285×1,#287×2,#355×2,#4×1,#597×1,#599×3", "c0213ec14e89fda5", "185583358fb3603e", "56b8f2e6343a1e33")`**. 갱신 뒤 73/73 |
| `checker_baseline_matrix.py` | 같은 키 하나만 다르다: `(2, 22, 21, 3, False)` → **`(2, 24, 23, 3, False)`**. 갱신 뒤 73/73 |
| `checker_cross_matrix.py` | census 347 · EXPECTED 347 · 차이 0(good 추가의 타 검사기 발자국 0) |
| `checker_lint.py` · `spec_lint.py` | 위반 0 · 위반 0 |
| `gen_pregate_symbol_kinds.py` → `--check` | `source_sha` 1줄만 바뀐다(`0cac462393f5e836` → 시제품 `5034a76e0fc4dacb`, 양 런타임). kinds 는 불변이다(`NO_BASE_MATERIAL`). in-sync |
| 미러 `diff -rq` | 무차이 |
| `make verify VERBOSE=1` | ontology·cross·backstop·regen 은 green 이다. core 는 **봉인 드리프트 8건으로만 RED** 다(scorer·packs·harness 봉인 후 변경 3 · tree_sha256 3 · script_trees 2). 봉인 단 앞의 fixture·baseline·count·lint·rulepack(`팩 == render(그래프)`)은 통과했다. 봉인 뒤 단계는 따로 돌렸다: seal self-test 는 M0 만 같은 드리프트로 red · ab_score 5/5 · 미러·가이드 rc 0 |
| `git apply --check`(메인 체크아웃 · 검사만) | 제안 패치 `diag-I2/I2-B.patch`(14 파일) 적용 가능 |

### 3.6 변이 가드(`make_proto_final.py` MUTANTS · `run_mutants.py`)

| 변이체(B 에서 조건 하나를 뗌) | B 대비 판정이 바뀌는 탐침 | 제안 bad_rules 가 잡는가 |
|---|---|---|
| MUT-P1 호출 지점의 증명 요구 탈락 | f·m·I2 공격 55개 전부 | **예** — 24→21(select·retouch·merge 소실) |
| MUT-anyclscall 단일 팩토리 재귀 대신 `cls.<아무 메서드>` 인정(진단 P2 의 구멍) | m·B4·B23·B50·B63 | **예** — 24→23(retouch 소실) |
| MUT-noreadcheck 누적 이름의 읽기 자리 검사 탈락 | B2·B3·B4·B5·B14·B15·B16·B18·B20·B21·B28·B30·B35·B47·B49·B50·B51 | **예** — 24→23(merge 소실) |
| MUT-noinitcheck 누적 이름의 결속 값 검사 탈락 | B1·B19 | 아니오(탐침) |
| MUT-nodeco 데코레이터 정확 일치 탈락 | B12 | 아니오 |
| MUT-nonew `__new__` 가드 탈락 | B57·B63 | 아니오 |
| MUT-nometa metaclass 제외 탈락 | B58 | 아니오 |
| MUT-nofirst `cls` 결속 검사 탈락 | B8·B8b | 아니오 |
| MUT-noyield yield 거부 탈락 | B13b | 아니오 |
| MUT-nonamevars 이름 원소 결속 검사 탈락 | B20 | 아니오 |
| MUT-nobuiltin 내장 가림 검사 탈락 | B56a·B56b·B62 | 아니오 |
| MUT-nodup 클래스 본문 이름 중복 검사 탈락 | B61 | 아니오 |
| MUT-nodecoshadow 데코레이터 이름 가림 검사 탈락 | B65 | 아니오 |

- 변이체 13종은 모두 탐침 1개 이상에서 판정이 바뀐다.
- fixture 로 무는 것은 핵심 3종(증명 요구·재귀 증명·누적 읽기)이다. D2 가 MUT-annot 을 탐침 소관으로 둔 선례와 같다. 나머지 10종을 모두 fixture 로 만들면 EXPECTED 변동이 커진다. 그래서 탐침 트리(`trees_i2`)를 재실행 증거로 남긴다.

## 4. 권장안 B 명세

### 4.1 코더가 예측할 문면(정직 기록 한 줄 요지)

> 인자를 받는 도메인 컬렉션 팩토리는 원소를 모두 그 메서드 안에서 새로 지어 돌려줄 때만 팩토리 태생으로 본다. 새로 짓는 방법은 `cls(..)`·`C(..)`·`object.__new__(cls)`, 또는 그렇게 짓는 같은 클래스 팩토리다. 받은 인스턴스가 원소로 섞일 길이 하나라도 보이면 전파하지 않는다. 그런 길의 예: 누적 리스트에 들이기, 그대로·골라 돌려주기, 증명 안 된 헬퍼에 맡기기, 누적 리스트를 밖으로 넘기기.

### 4.2 판정(시제품 `diag-I2/proto/B/scripts/check-transaction-boundary.py` · sha `5034a76e0fc4dacb`)

1. **증명 대상 메서드**
   - 클래스 본문에 **한 번만** 정의된 동기 `def` 이고, 데코레이터가 가려지지 않은 `@classmethod`·`@staticmethod` **하나뿐**이어야 한다.
   - 본문에 `yield`·`await`·`locals()`·`vars()` 가 없어야 한다.
   - metaclass 를 지정한 클래스나 모듈 범위에서 다시 묶인 클래스는 통째로 제외한다.
2. **새 원소**
   - `cls(..)` 는 첫 파라미터로만 묶인 `cls` 여야 한다. 대입·반복 target·중첩 파라미터로 다시 묶였으면 인정하지 않는다.
   - `C(..)` 는 지역에서 가려지지 않은 C 여야 한다.
   - `cls.__new__(cls)` 도 인정한다. 이 셋(`cls(..)`·`C(..)`·`cls.__new__(cls)`)은 클래스 본문에 `__new__` 가 없을 때만 인정한다.
   - `object.__new__(cls)` 는 `object` 가 가려지지 않았을 때 인정한다.
   - 증명된 단일 팩토리 호출 `cls.f(..)`/`C.f(..)` 를 인정한다.
   - 새 원소 값에만 단순 대입된 지역 이름을 인정한다(반복 target·walrus 등 다른 결속이 있으면 인정하지 않는다).
   - 두 갈래가 모두 새 원소인 조건식을 인정한다.
3. **새 컬렉션**
   - 새 원소만 담은 컴프리헨션(list·set·genexp)과 리터럴(별표 풀기는 새 컬렉션만)
   - 가려지지 않은 `tuple/list/set/frozenset` 의 빈 호출이나 복사
   - 증명된 컬렉션 팩토리 호출
   - 새 컬렉션끼리의 `+` 와 조건식
   - **누적 이름**
     - 결속: 모든 결속이 새 컬렉션 단순 대입이거나 `+=` 새 컬렉션이어야 한다.
     - 허용하는 읽기 자리:
       - `append/add(새 원소)`·`insert(i, 새 원소)`·`extend/update(새 컬렉션)`·`sort/reverse` 의 수신
       - 복사 래퍼 인자·반복 원천·리터럴 속 별표 풀기·`+` 피연산자
       - 순수 읽기(`len`·`bool`·`isinstance`·순수 비교·조건)
       - 이 메서드 자신의 `return`
     - 이 밖에서 읽히면 증명이 서지 않는다(중첩 def·lambda 안의 읽기도 같은 기준으로 본다).
4. **메서드 증명**
   - 단일 팩토리: 모든 return 이 새 원소다.
   - 컬렉션 팩토리: 모든 return 이 새 컬렉션이다(return 이 0개이거나 빈 `return` 이 있으면 증명하지 않는다).
   - 클래스마다 최소 고정점으로 계산하므로 재귀 순환은 증명되지 않는다.
5. **호출 지점**(`_elements_factory_born`)
   - `C.m(..)` 에서 m 이 기존 P1z 표(선언)에 있어야 한다. 무인자면 그대로 전파한다.
   - 인자(위치·키워드·별표)가 있으면 m 이 B 로 증명됐을 때만 전파한다.
   - 이름 단위 fail-closed(탈출·결속·불변 면제)는 D2 그대로다.

### 4.3 구현 윤곽(국소 · 다른 규칙 무영향)

- 상수 2개: `BUILD_ELEMENT_ARG = {"append": 0, "add": 0, "insert": 1}` · `BUILD_COLLECTION_METHODS = ("extend", "update")`.
- 새 함수 3개:
  - `_module_bound_names(mod)`(15행): 내장 가림 판정
  - `_built_collection_factories(mod)`(50행): 클래스마다 고정점
  - `_proves_fresh(m, want_coll, cname, scalar, coll, module_bound, plain)`(153행): 결속 수집 + `_elem`·`_coll`·`_accumulator`·`_read_ok`
- 바뀌는 기존 코드:
  - `_domain_class_index`: 값 튜플에 증명 표를 더한다. 도메인은 BC 당 1회 파싱을 유지한다.
  - `_domain_collection_factories`: 반환을 `{지역 클래스: {메서드: 증명 여부}}` 로 바꾼다.
  - `_check_execute_body`: 서명 표기.
  - `_elements_factory_born`: 가지 1개를 수정한다.
- 검사기 diff 는 **+267/−23** 이다(D2 수리 커밋의 검사기 변경 295행과 비슷한 규모).
- [추론] 누적 이름의 «순수 읽기 자리» 지식은 유스케이스 쪽 탈출 판정(`reads`)과 겹친다(원칙 06). 두 곳의 허용 목록은 목적이 달라 완전히 같지 않다(도메인은 새 원소 들이기를 허용한다). 공용 헬퍼로 모으는 것은 D2 코드를 건드리는 리팩터링이므로 이번 수리와 분리한다(원칙 08).
- 모듈 docstring «단순화(정직 기록)»은 세 곳을 고친다. 시제품에 반영했고, 줄바꿈은 구현 때 정리한다.
  - ② 문면: «인자가 없으면 선언만으로, 인자가 있으면 본문 증명이 설 때만»
  - 본문 증명 정의와 가정 밖(베이스 `__new__`·클래스 데코레이터·클래스 밖 바꿔 끼우기·복제 팩토리)
  - 비전파 목록: «본문 증명이 서지 않는 인자 받는 도메인 호출(선별 헬퍼·받은 컬렉션을 섞는 누적·증명 안 된 헬퍼 위임)»

## 5. 바꿀 파일

| 파일 | 변화 | 근거 |
|---|---|---|
| `dddjango/scripts/check-transaction-boundary.py` | §4.3 · 시제품 sha `5034a76e0fc4dacb` | `diag-I2/I2-B.patch` |
| `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py` | byte 미러 | Makefile `diff -rq` |
| `dddjango/scripts/pregate_symbol_kinds.json` + Codex 미러 | `source_sha` 1줄(`gen_pregate_symbol_kinds.py` 무인자로 재소성) | §3.5 |
| `workspace/eval/fixtures/transaction_boundary/good/…/domain_layer/order/order.py` | 클래스 **끝에** `@classmethod open_batch(cls, order_ids: tuple[str, ...]) -> tuple["Order", ...]` 를 붙인다. 빈 리스트에 `cls.open_pending(..)` 을 append 하고 `tuple(orders)` 로 돌려준다 | 수리 전 red 증명(HEAD exit 2) · B exit 0 · 타 검사기 발자국 0(cross 불변) |
| `…/good/…/application_layer/order/open_batch_orders/` (신규 4) | `open_batch_orders_use_case.py`(`execute(self, order_ids: tuple[str, ...])` · `for order in Order.open_batch(order_ids): save(order)`) + 빈 `_command/_query/_result.py` | D2 `seed_orders` 판형(1인자 `execute` — dto-placement #635 회피) |
| `…/bad_rules/…/domain_layer/order/order.py` | 클래스 끝에 3개를 붙인다: `@staticmethod kept(order) -> Order`(항등) · `@classmethod retouched(cls, orders) -> tuple[Order, ...]`(`tuple(cls.kept(o) for o in orders)`) · `@classmethod merged_with(cls, orders) -> list[Order]`(`[cls()]` 에 `extend(orders)`) | MUT-anyclscall·MUT-noreadcheck 가드 |
| `…/bad_rules/…/order/retouch_orders/retouch_orders_use_case.py` · `…/merge_orders/merge_orders_use_case.py` (신규) | 조회 결과를 인자로 넘겨 돈 뒤 `order.status = "closed"`·save — 참양성 1건씩 | B·HEAD red · MUT-P1/anyclscall/noreadcheck 에서 소실 |
| `workspace/tools/findings_count_matrix.py:134` | §3.5 새 튜플(`--emit-expected` 산출 · 이 키만 다름) | 사유: #195 ×8→×10(retouch·merge 참양성) |
| `workspace/tools/checker_baseline_matrix.py:261` | `(2, 24, 23, 3, False)` | 같은 사유 |
| `fixture_matrix.py` · `checker_cross_matrix.py` | 불변 | §3.5 |
| `dddjango/scripts/rulepack.json` · `ontology/**` · `LEDGER.tsv` · graph-owned md | **불변** | 아래 규범 문면 참조 |
| `workspace/eval/ab/T2-0b-manifest.json` | 수리 커밋 **뒤** 별도 chore 커밋으로 `manifest_seal.py --write` | D2 선례 |
| 기록(메인 세션 몫) | `progress.md` 행 · `step8b-improvements.md` I2 행 · 조감도 `ontology-adoption-map.html` 행 | 상시 지침 |

**규범 문면**: 변경은 필요 없다. [확인] 근거는 다음과 같다.
- #195 규칙 설명(docstring 9–11행 «save/remove 인자는 같은 함수 안에서 루트 메서드 호출을 받은 객체»)은 그대로다. 바뀌는 것은 docstring «단순화(정직 기록)»뿐이다.
- 이 검사기는 온톨로지에서 `djr:enforcedBy` 이름으로만 걸린다(`agent-design-architect.ttl:199·265` · `agent-design-review-db.ttl:40`).
- `#195` alias 는 없다. rulepack 은 검사기를 이름으로 45회 가리키고 해시는 싣지 않는다. `spec_lint.py:443` 매핑도 불변이다.
- 커맨드·에이전트·스킬 md 에는 «컬렉션 팩토리» 문면이 없다(grep 0).
- 그래서 graph-owned 절·LEDGER 재기준선·`make rulepack` 은 필요 없다.

**추정**은 약 3h 이고 적대 검토를 포함한다. 항목별로 보면 다음과 같다.
- 패치 이식·docstring 줄 정리: 0.5h
- fixture·EXPECTED·pregate·미러: 0.3h
- `make verify` + 봉인 chore: 0.5h
- 적대 검토·반영: 1.5h(D2 는 검토 2회에 결함 major 2건이 나왔다. 이번 설계는 그 탐침 전부와 공격 55개를 이미 통과했다)

## 6. 남는 한계(정직 기록 대상)

| 부류 | 모양 | B 판정 | 비고 |
|---|---|---|---|
| fail-closed 오탐 | 재귀 팩토리(H16 `(cls.f(x[0]),) + cls.recursive(x[1:])`) | red | 최소 고정점 |
| fail-closed 오탐 | 상속 메서드 `Sub.m(..)`(H17 · L9) | red | D2 와 같다 |
| fail-closed 오탐 | dict·기타 컨테이너 누적 뒤 `values()`(H18) · `sorted(items, key=..)` · `pop/remove/clear` 수신 · 모듈 함수 위임 · 다른 클래스 팩토리 위임 | red | 실례가 나오면 허용 목록에 한 줄씩 더한다(원칙 05) |
| fail-closed 오탐 | 본문이 표 조회·열거 멤버·Optional 을 돌려주는 단일 팩토리에 기대는 컬렉션 팩토리 | red | 현장 7/164 — 새로 짓지 않으므로 옳다 |
| 가정 밖(green) | 받은 인스턴스의 필드를 베껴 새로 짓는 복제 팩토리(H19 `cls(code=k.code, …)`) | green | 스칼라 `C(**vars(x))` 와 같은 부류다. 원소는 새 객체지만 같은 행을 덮어쓸 수 있다. 막으려면 필드 출처까지 추적해야 하는데, 그러면 `after`(받은 값을 읽어 새로 지음)와 가를 수 없다 |
| 가정 밖(green) | 클래스 본문 밖에서 메서드를 바꿔 끼우는 코드(H23 모듈 범위 `C.m = classmethod(..)`·`setattr`) | green | 무인자 P1z 도 같은 노출이다 |
| 가정 밖(green) | 베이스 클래스의 `__new__`(Enum 등)·클래스 데코레이터의 교체 | 미검사 | 애그리거트 루트가 Enum 인 경우는 없다 |
| 범위 밖(HEAD 와 같음) | 무인자 호출의 클래스·모듈 상태 세탁(L1–L5·L7·L8·L14·A40) | green | 아래 참고 |
| 범위 밖(HEAD 와 같음) | 스칼라 채널 `next(iter(조회))`(p·P·P3)와 save 인자가 이름이 아닌 모양(`save_items((item,))` — `arg_name == ""` 건너뜀) | green | 백로그 ④p. 후자는 이번 조사에서 새로 확인했다(`check-transaction-boundary.py` `_check_execute_body` 의 `if not arg_name: continue`) |

참고(범위 밖 · 별도 결정 후보): **«무인자도 본문 증명으로 통일»(판 Ball)** 을 실측했다.
- 효과: 무인자 선언 전파를 버리면 가정 밖 세탁 9개(L1–L5·L7·L8·L14·A40)가 red 로 닫힌다.
- 대가: k(모듈 상수로 미리 지은 인스턴스 반환)·L6(`functools.cache` 데코레이터)가 red 가 된다.
- fixture·현장 코퍼스 출력은 불변이다. 현장에 무인자 자기 컬렉션 팩토리가 0개이고, D2 fixture `seed_batch` 는 증명된다.
- [추론] 어제 승인된 P1z 의 동작을 바꾸는 결정이라 이번 ④h 수리와 섞지 않는다(원칙 08). 한 문장 규칙으로 통일되는 이점은 기록해 둔다.

## 7. 시제품·재실행 경로

`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag-I2/`

| 파일 | 역할 |
|---|---|
| `head-scripts/` | HEAD `fcf051fd` 스크립트 스냅숏 |
| `make_proto_b.py` → `proto/B0/` | 최소 본문 증명 판 |
| `make_proto_final.py` → `proto/B/` | 권장 판 + 변이체 `proto/MUT-*/`(13종) |
| `make_variants.py` → `proto/{P1,P2,O,T,T2}/` | 비교 판(B0 파생) |
| `proto/Ball/` | §6 참고 판 |
| `make_probes_i2.py` → `trees_i2/`(81) · `i2_cases.tsv` | 새 탐침 |
| `make_field_probes.py` → `field/{sds,FH1_teller_inline_loop,FH2_teller_named_loop}` | 현장 사본(`field-sds` = `git clone --shared` · `25d70b636`)과 변형 |
| `make_fixtures_x.py` → `fixtures-x/` | 제안 fixture 를 끼운 fixtures 전체 사본 |
| `run_i2.py [판…] [--묶음]` → `matrix_v4.md` · `out/` | 268 대상 × 8 판(대상은 기존 scratch `diag-D2`·`impl-D2`·`review-D2`·`review-D2b` 트리를 그대로 읽는다) |
| `run_mutants.py` → `mutants.md` | §3.6 |
| `survey_field.py` | §1 현장 전수 |
| `named_probes.md` | §3.2 전체 행 |
| `repo/` | 저장소 `--shared` 사본 + B 적용. `clone_*.out` · `clone_make_verify.log` · `fcm_emit.txt` · `cbm_emit.txt` |
| `I2-B.patch` | 메인 체크아웃 기준 제안 패치 14 파일(`git apply --check` 통과 · 적용하지 않음) |
