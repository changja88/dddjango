### Task 4: 실행·Enum·UoW·속성 출처의 AST 판정 (F4-10/11/14/15)

**Files:** `dddjango/scripts/check-context-isolation.py`, `check-domain-model.py`, `check-port-adapter-pairing.py`와 byte 미러. Test: `workspace/tools/field_report_checker_smoke.py`.

**F10:** `_check_ohs_service`의 계수만 교정한다. source module import가 표준 BC composition_root인 builder의 반환 binding(`uc=builder()`, alias, qualified module, `builder().execute()`)에 대해 execute를 센다. direct imported usecase/type-annotated receiver도 출처가 application usecase 칸으로 확인되면 센다. 재대입은 binding을 무효화한다. `ast.walk`로 호출되지 않은 nested function/class의 본문을 상위 실행에 합치지 않는다. builder는 준비이며 실행0/실제복수/출처 불명은 #153 후보다. 임의 cursor.execute 1회는 usecase1회의 증명이 아니다. 분기의 동적 path-count를 증명하지 않으며 정적 복수 호출 후보를 유지한다. 별도의 도메인 예외 속성 접근 #153 확정 진단은 보존한다.

표준 builder의 확인은 composition_root 주소만으로 끝내지 않는다. `build_*_use_case`의 표준 심볼 형태와 읽을 수 있는 선언의 usecase 반환 annotation/직접 생성 반환 중 하나를 대조한다. 명시 표준 경로·심볼은 있으나 선언 자료가 없으면 불명 후보. 분기 한쪽에서 재바인딩된 receiver는 join 이후 불명으로 유지한다. AST 마지막 방문 순서로 확정 binding을 되살리지 않는다.

```python
if proven_usecase_execution_count != 1 or unknown_execution:
    candidates.add("#153", where, "실행 횟수/출처 확인 필요", question)
```

**F11:** `_check_value_object_file`에서 `enum.Enum/StrEnum/IntEnum`의 직접 표준 import/별칭/module alias 출처와 닫힌 형태를 확인하면 #268 자체 검증 후보를 제거한다. `_missing_`, 사용자 `__new__`/`__init__`/`__call__`, custom metaclass·사용자 기저·rebind·동적 멤버·Flag/IntFlag는 후보를 유지한다. 값 객체 다른 #264/#259 검사는 계속 수행한다.

모듈의 `Kind._missing_ = classmethod(...)` 같은 사후 클래스 속성 변경도 동적 확장이며 닫힌 Enum 면제에서 제외한다.

**F14:** `_check_application_side`의 #546만 함수 전체 written 집합에서 구간 집합으로 바꾼다. 현행 repository 타입→aggregate 종류 계수를 유지하며 새 instance identity 분석으로 확대하지 않는다.

| 형태 | 계수 |
|---|---|
| 표준 UoW port import로 해소한 매개변수/필드, 순차 with | 최상위 with 각각 별도 region; 변수 이름이 같아도 분리 |
| 한 with 안 nested UoW/alias/여러 context item | 가장 바깥의 하나의 region으로 합산 |
| 외부 `transaction.atomic` with/decorator 아래 여러 UoW | 하나의 외부 region으로 합산 |
| UoW 아닌 lock/file with | 독립성 증거로 쓰지 않음 |
| factory/with-as가 표준 UoW 타입으로 해소됨 | 같은 region 규칙, alias를 그 블록 안에서만 전파 |
| import/타입 불명·현재 함수 안에서 확인되는 불명 외부 transaction/동적 alias/경계 | 함수 전체 관련 쓰기를 후보로 알리고 독립 트랜잭션으로 확정하지 않음 |
| 미호출 nested 함수 | 상위 실행의 계수에 넣지 않음; 그 함수 자체는 별도 검사 |

관찰 단위는 **현재 함수의 명시 lexical transaction region**이다. 알려진 outer atomic/decorator·중첩·다중 with-item 결합이 개별 UoW 분리보다 우선한다. 모든 주입 UoW를 ‘바깥에서 활성일 가능성’만으로 후보로 되돌리지 않는다. 주어진 함수 안에 외부 경계 증거가 없는 순차 표준 UoW는 위 표대로 나누되 실제 전체 호출의 독립 commit을 증명했다고 표현하지 않는다. 확정된 한 region에서 서로 다른 repository/aggregate 종류 두 개는 #546 위반. 범위 밖 쓰기의 기존 2종 형상은 근거가 없는 ‘동일 트랜잭션’ 확정 대신 후보로 남긴다. 외부 호출자/ATOMIC_REQUESTS/간접 helper의 전역 transaction 증명은 지원 밖으로 문면에 적는다. #550/#257은 기존 역할을 보존한다.

**F15:** `_check_use_side`의 비교식 left+comparators 전체에서 세 속성(`code/errno/status_code`)을 찾아 수신자 출처를 판정한다. 정확 module import·annotation·constructor assignment·alias·except binding을 읽고 rebind는 무효화한다.

- domain_layer 및 application command/query/result/port contract의 **읽을 수 있는 실제 로컬 클래스 선언**으로 확인된 데이터/예외 타입은 도메인 계약 값으로 보며 해당 속성 진단을 내지 않는다. import 주소만 port라서 domain으로 면제하지 않는다. 명시 re-export는 순환 방지하며 실제 vendor 정의로 이어지면 vendor, 소스 결손/불명은 후보로 둔다.
- 표준 지원 vendor origins: `django.db`/`django.db.utils`의 DatabaseError/IntegrityError/OperationalError, `sqlite3`의 DatabaseError/IntegrityError/OperationalError, `psycopg`/`psycopg2`의 Error 계열, `requests`/`httpx`의 HTTPError/RequestException 및 Response. 정확 import된 알려진 타입만 확정한다. 외부 SDK 전체를 오류로 보지 않는다.
- 출처 불명·타입이 불확정인 exception·동적 helper 반환은 #557 후보. `except (DomainError, IntegrityError)`처럼 서로 다른 출처를 합친 바인딩도 후보이며 하나로 확정하지 않는다. except라는 사실 자체는 벤더 근거가 아니다. 동일 비교식의 같은 receiver/속성은 한 번만 낸다. branch join의 상충 binding은 불명으로 보존한다.

- [ ] **Step 1:** builder alias/inline/rebind/0·2·cursor·nested, Enum closed/custom/rebind/Flag, UoW 순차동명/중첩/outer atomic/lock/unknown/nested 함수/#550/#257, code domain/vendor/unknown/except/RHS/chained 대조를 literal rule 기대값으로 추가한다.

```python
self.assertNotIn("#153", candidates(standard_builder_once))
self.assertIn("#153", candidates(builder_without_execution))
self.assertNotIn("#268", candidates(closed_str_enum))
self.assertIn("#268", candidates(enum_with_missing))
self.assertNotIn("#546", violations(two_independent_regions))
self.assertIn("#546", violations(two_aggregates_one_region))
self.assertNotIn("#557", all_rules(domain_code))
self.assertIn("#557", violations(vendor_code_on_right))
self.assertIn("#557", candidates(unknown_code))
```

- [ ] **Step 2:** 각 그룹 RED 확인 → 최소 AST 수정 → 해당 그룹 GREEN을 순서대로 수행한다. 이름 변경만으로 동일 의미의 판정이 달라지지 않는 대조를 포함한다.
- [ ] **Step 3:** `python3 -B workspace/tools/field_report_checker_smoke.py` 및 관련 현행 checker fixture를 실행하고 미러한다.
- [ ] **Step 4:** 작업 리뷰에서 자동확정/후보 경계와 scope를 확인한다. 현재 기능보다 광범위한 데이터 흐름 분석을 추가하지 않는다.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Start gate and task ownership
Do not begin until coordinator dispatch after Task3 independent gate. Only the three specified source checkers + byte mirrors + field_report_checker_smoke.py are owned. Task1/2 pregate changes and Task3 publicsurface changes must remain intact. Task6 owns normative alignment: no TTL/spec/owner-map/report cleanup/seal/Make edits here. Existing related fixtures are workspace/eval/fixtures/context_isolation, domain_model, port_adapter_pairing and their fixture_matrix entries. Run relevant lanes, not unrelated full matrix until final integration gate.
F14 lexical current-function regions do not claim whole-call independent commit. Confirmed external atomic/decorator overrides separated UoW regions; uncertain boundaries/calls remain candidate. F15 contract re-export requires actual origin, so a port import path alone never exempts vendor type. No new generic dataflow engine or instance-identity model.

Task3 preceding work adds admin origin/context/consumption and source-vs-generated tests; checker smoke current18. Preserve those tests while adding Task4 regressions. No Task3 publicsurface/pregate edits owned here. New F4-20 (#195 factory-born collections) appeared in primary report during execution; it is OUTSIDE the12 approved directions, so leave transaction-boundary checker and F20 unchanged. No new user policy decision has been required so far.

Task4 F10 unknown-execution refinement: a single execute AST site inside loop/comprehension does not prove one execution. No dynamic path-count solver is added; keep #153 candidate for unknown multiplicity. Implementer added two loop/comprehension RED failures after initial F10 correction, then unknown_execution handling GREEN. F10/F11 focused green; F14 lexical regions now in progress.
