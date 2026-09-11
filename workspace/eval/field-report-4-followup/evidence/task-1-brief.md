### Task 1: 명시 효과·기존 marker·DTO 출처 (F4-1/F4-18)

**Files:**
- Modify: `dddjango/scripts/design_pregate.py`의 Plan/PlanEntry, `_parse_symbols`, `_parse_signals`, `parse_spec`, `block_hash`, `materialize`, `main`, report/check-report.
- Test: `workspace/tools/pregate_field_report_smoke.py`.
- Mirror: `codex-dddjango/skills/dddjango/scripts/design_pregate.py`.

**Interfaces:** 기존 `PlanEntry.symbols`는 렌더 재료로 유지한다. 추가 `declarations: list[Symbol]`와 `declaration_aliases: list[ModuleAlias]`는 add/update 명시 선언 전체를 보관한다. 메서드는 선행 클래스에 귀속하며 같은 객체를 add 렌더에 써도 되지만 update 클래스의 기존 본문을 교체하지 않는다.

```python
@dataclass
class UseCaseEffect:
    path: str
    owner: str
    effect: str       # read-only | write
    uow: str         # none | 명시된 타입 표현(한 계약)

@dataclass
class DeclarationFinding:
    rule: str        # #197 | #202
    path: str
    owner: str
    detail: str
    confirmed: bool

# Plan.effects: list[UseCaseEffect]
```

검증 함수의 공개 계약은 `check_declarations(plan: Plan, copy: Path) -> list[DeclarationFinding]`다. 효과 선언 대조와 아래 DTO 그래프 탐색 결과를 반환하며 파일을 수정하지 않는다.

**효과 문법:** 선택형 새 `<!-- machine: use-case-effects -->` 바로 다음 `effects` fence. 행은 `<파일>::<클래스>  <read-only|write>  uow=<none|타입식>`이다. 예:

```effects
application/shop/application_layer/books/list_books/list_books_use_case.py::ListBooksUseCase  read-only  uow=none
application/shop/application_layer/books/save_book/save_book_use_case.py::SaveBookUseCase  write  uow=BookUnitOfWork
```

- 동일 path/owner 중복·상충, 어휘 밖 effect, 빈 uow, file-plan 비등재/비-add·update, 선행 symbols 클래스 없는 행은 form exit 3이다. `uow`의 타입식은 Python annotation으로 파싱한다. 생성 의무가 없는 선택형 입력이며 기존 설계 무기재는 S5 미검증 메모다.
- **#197 확정의 모든 경로는 `effect == read-only`가 선행조건**이다. read-only + `uow != none`은 명시 모순 #197 확정. read-only + `uow=none`인데 같은 선언의 생성자/필드에 **명시 import/qualified 경로로 UoW port임이 확인된** 타입이 있어도 #197 확정. suffix만 UnitOfWork인 미해소 타입은 후보. write + 명시 UoW는 정상이고, write + none + 명시 주입 불일치는 채널 메모로만 남긴다(#197 확정 아님). write에 uow 없음 자체를 이번 새 오류로 만들지 않는다.
- 새 효과 블록이 없으면 기존 네 fence+입장 표 해시를 byte 동일 알고리즘으로 유지한다. 존재하면 새 마커와 원문을 hash 끝에 포함한다. 산문 변경은 hash에 무관하며 선언 한 글자/순서 변경은 재실행시킨다.

**marker 후상태:** 기존 입장 표 `[markers: a,b]`는 **파일 수준 최종 module pytestmark 목록**이다. update에서 무기재는 유지, `[markers:]`는 명시 빈 module 목록, 목록 지정은 교체다. nodeid `.py::case` 또는 class 경로는 module 변경으로 승격하지 않고 S5 메모를 낸다. 서로 다른 입장 행이 같은 파일의 다른 최종 목록을 선언하면 형식 오류다.

- 기존 module 수준 pytestmark의 단일 `Assign/AnnAssign`가 `pytest.mark.name`(정적 alias 포함) 또는 그 list/tuple일 때만 해당 statement를 byte 범위 치환한다. 호출 인자 있는 mark, 동적 계산/증분/조건부 대입·동명 pytest 재바인딩·중복 대입은 덮지 않고 S5로 남긴다. 선언 목록도 단순 identifier만 지원하며 알 수 없는 토큰을 가짜 Python으로 전사하지 않는다.
- module pytestmark가 없으면 future import 뒤에 필요한 pytest import와 명시 목록만 추가한다. pytest 이름이 다른 binding과 충돌하면 S5. 클래스/함수 decorator는 그대로 둔다. 명시 빈 목록은 module assign만 비우며 다른 DB 증거를 지우지 않는다.
- `[base:]`/`[client:]` update는 이번 범위 밖으로 유지하며 S5로 알린다. marker만 성공해도 기존 함수 본문 변경은 미검증이다.

**DTO 연결:** 타입 identity는 `(절대 모듈 경로, 심볼)`이다. 명시 boundary-imports(상대 import 포함), qualified annotation, 같은 파일의 선언/별칭 및 실제 사본의 타입 선언을 사용한다. update는 명시한 해당 클래스 선언을 후상태로 보되 미기재 전체 파일을 삭제/교체로 간주하지 않는다.

- 표준 `*_result.py`/OHS `*_response.py`의 공개 Result/Out/Response 선언에서 필드를 탐색한다. 보조 private DTO와 컨테이너 `list/tuple/set/frozenset/dict/Mapping/Sequence`, `Optional/Union`·`|`·문자열 forward annotation·명시 alias를 순환 방지 집합으로 따라간다. `Literal` 값은 타입 이름으로 읽지 않는다. 도달한 domain `aggregate/entity`는 #202 확정, value_object는 허용, 외부/primitive 타입은 해당 규칙 밖이다.
- bare 미해소 타입은 동일 이름 catalog가 있어도 확정하지 않고 #202 후보+출처 보완 질문을 낸다. 중복/별칭 cycle·TYPE_CHECKING 분기 불일치도 후보. 외부 타입인지 알 수 없으면 후보이며 이름에서 aggregate를 추측하지 않는다.
- OHS domain import는 실제 선언이 있을 때 현행 #95/#96가 판정한다. Result 소비만으로 import를 만들지 않는다. 새 checker가 직접 증명한 DTO 오염의 후보가 OHS의 추가 확정 위반으로 증폭되지 않는다.
- 선언 확정 위반은 소스 차분 예보와 별도로 보고하고 exit 2에 합친다. 후보는 차단하지 않으며 review 질문/ID를 남긴다. **실체화 0건이어도 선언 검증을 먼저 수행**한다. 확정 위반 0이면 기존 skip4/실존 결손5 의미를 유지한다. 새로운 형식/실행 오류는 각각 3/1이다.
- report와 `--check-report`는 `선언 확정`/`선언 후보`를 구분한다. 기존 `_stable_id(rule+path)`의 처분 단위는 유지하고 같은 파일의 여러 근거를 합쳐 빠뜨리지 않는다. 후보를 violation filtered 처분과 섞지 않는다.

- [ ] **Step 1:** smoke에 literal 기대값을 가진 실패 테스트를 추가한다.

```python
self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, copy)], [("#197", True)])
self.assertIn("pytest.mark.django_db", updated_source)
self.assertEqual(original_source.read_bytes(), frozen_source)
```

대조: read-only/none 정상, read-only/명시 UoW 모순, read-only/none/주입 모순, write/명시UoW 정상과 write/none/주입의 비차단 메모, 이름 추정 금지, 효과 누락·중복·hash; marker 유지/추가/제거·class DB 유지·nodeid/동적/중복/지원주소 오전파 방지; DTO 직접/중첩/container/alias/forward/동명 VO/Literal/순환/update·실체화0; 실제 import #95/#96 유지.
- CLI 대조도 같은 smoke의 임시 git fixture로 수행한다: update만 있고 실체화0 + 선언확정→exit2/report 처분 누락 red, 선언후보만→기존 skip4/결손5 유지, marker update→실제 #387 생성/제거와 class/function DB 신호 보존, 효과 hash 변경→stale, 선언확정+S1 deferred 동시→exit2. helper 반환·marker 문자열만으로 CLI 성공을 주장하지 않는다. 기존 add의 nodeid 물리 신호 결합은 유지하고 새 nodeid 제한은 **update**에만 적용한다.
- [ ] **Step 2:** `python3 -B workspace/tools/pregate_field_report_smoke.py`의 신규 실패가 해당 결함 때문임을 기록한다.
- [ ] **Step 3:** 위 자료 구조·파서·명시 판정·marker의 국소 치환과 보고를 구현한다. source/사본 경계를 지키고 byte 미러한다.
- [ ] **Step 4:** 같은 smoke를 재실행하여 신규 대조와 기존 15개를 함께 통과시킨다. 변경된 `.py`를 compile하고 테스트가 실제 parser/materialize/report 경로를 호출하는지 검토한다.
- [ ] **Step 5:** 작업 diff/테스트 증거를 검토하고 중대한 문제를 닫는다. 커밋 없이 다음 작업으로 간다.


## Global Constraints

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.

## 의존 작업 경계
Task1의 선언확정+S1 deferred 결합 CLI는 Task2의 생성 분리 기능이 있어야 가능하므로 Task2에서 통합 검증한다. Task1은 단독 선언/marker/typegraph/보고/hash 경로를 완성한다. Task2/3의 provenance 또는 admin 완화를 앞당겨 구현하지 않는다.
