# Task 1 구현 보고 — 명시 효과·marker 후상태·DTO 출처

작업 위치: `/Users/hyun/.cache/dddjango-field4-followup-20260911`.
상태: 구현·자가리뷰 완료, 독립 리뷰에 전달할 concern 1건 있음.

## 변경 파일

- `dddjango/scripts/design_pregate.py`
- `codex-dddjango/skills/dddjango/scripts/design_pregate.py` — 원본 byte 동일
- `workspace/tools/pregate_field_report_smoke.py` — 기존 15개 + 신규 9개 = 24개 테스트

산출물은 위 3개뿐이다. 이 디렉터리의 brief/report/log는 작업 증거다. primary, 실제 사용자 프로젝트, TTL·규범·원보고서·master.html·버전·봉인·Make는 수정하지 않았다. 커밋·브랜치·인덱스·배포 조작은 하지 않았으며, 테스트 helper가 생성한 임시 git 저장소에서만 fixture anchor commit을 만들었다.

## 지원한 동작

- add/update 전체 `declarations`와 `declaration_aliases`, 선행 클래스에 연결된 메서드를 보존한다. update 클래스 원본 본문을 덮어쓰지 않는다.
- 선택형 use-case-effects fence, 중복/어휘/빈 uow/annotation/계획 태그/선행 클래스 검증을 구현했다. 효과 블록 무기재는 S5 메모다. 효과 블록이 없을 때 기존 hash 알고리즘을 보존하고, 있을 때 마커와 원문을 마지막에 추가한다.
- 공개 `check_declarations(plan, copy)`는 파일을 쓰지 않는다. read-only와 명시 UoW의 모순, read-only/none과 출처가 확인된 UoW port 주입을 #197 확정으로 보고한다. 미해소 suffix는 후보이며, write/none과 명시 주입의 불일치는 비차단 채널 메모다. write/명시 UoW의 정상 생성자 주입은 선언 위반이 아니다.
- update marker는 최종 module 목록이다. 무기재 유지/빈 목록/교체, 정적 pytest alias, Assign/AnnAssign/list/tuple을 지원한다. 해당 AST statement의 UTF-8 byte 범위만 바꾸고 필요한 import/list는 docstring/future 뒤에 넣는다. 함수/class decorator와 기존 본문은 보존한다.
- 호출 인자가 있는 marker, 동적/중복/조건부/증분 대입, pytest 재바인딩, pytestmark import 바인딩, update nodeid/class 주소, 지원 밖 토큰은 S5로 남긴다. 같은 파일의 서로 다른 최종 목록은 형식 오류다. add nodeid의 기존 파일 결합과 첫 artifact 주소 규칙을 유지한다. base/client update는 미지원 S5다. 최종 marker가 이미 동일하면 실효 조치 0을 유지한다.
- DTO 출처 identity는 module/symbol이며, 명시 import·relative import·qualified annotation·같은 파일 alias·실제 사본의 클래스/필드와 update 클래스 후상태를 사용한다. 공개 Result/Out/Response에서 private DTO, 명시 alias, forward annotation, list/tuple/set/frozenset/dict/Mapping/Sequence, Optional/Union/`|`를 따라간다. domain aggregate의 표준 `<agg>/<agg>.py`, entity 경로를 판정하며 value_object/shared_value_object는 허용한다.
- Literal 값은 타입으로 읽지 않는다. 이름만 같은 catalog로 bare 타입을 해소하지 않는다. 중복/분기 불일치·alias cycle·불명확한 타입/컨테이너는 후보다. local Mapping/list가 표준 컨테이너라고 추측되어 오확정되지 않도록 출처를 확인한다. 클래스 사이 순환은 방문 집합으로 종료한다.
- DTO 탐색은 OHS에 domain import를 합성하지 않는다. Result 소비만으로 후보가 #95/#96으로 증폭되지 않는 반대 대조와 실제 명시 domain import의 현행 #95/#96 검출을 확인했다.
- 선언 확정/후보는 report의 별도 절과 --check-report 요약에 구분한다. 같은 rule/path의 여러 owner 근거를 하나의 기존 stable ID에 합친다. 확정만 처분 의무에 포함한다. 실체화 0이어도 선언 검증을 수행하고, 확정이면 exit 2, 후보만 있으면 기존 skip 4/실존 결손 5를 유지한다. 효과 hash 변경은 stale로 판정한다.

## RED 증거

1. `python3 -B workspace/tools/pregate_field_report_smoke.py`
   - 로그: `task-1-red.log`
   - 20개 실행, 실패 15 + 오류 9(신규 subTest 포함). use-case-effects 마커 미지원, check_declarations 부재, marker update 미실체화, 선언확정 CLI exit 4 등의 실제 결함이었다. 기존 15개는 통과했다.
2. 같은 명령, 자가리뷰 보강 23개 단계.
   - 로그: `task-1-red-extra.log`
   - 표준 aggregate 경로의 중첩 DTO를 놓치는 실패, 기존 pytestmark import 바인딩 앞에 목록을 추가하는 실패 2개를 확인한 뒤 고쳤다.
3. `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_typegraph_container_identity_and_literal_alias`
   - 로그: `task-1-red-container.log`
   - local Mapping/list 및 미해소 Mapping이 표준 컨테이너로 추측돼 #202 확정으로 나오는 대조 실패 3개를 확인한 뒤 후보로 보수화했다.
4. `python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_declaration_only_cli_and_report_dispositions`
   - 로그: `task-1-red-summary.log`
   - check-report 구조화 요약의 선언 확정 계수 누락을 확인한 뒤 추가했다.

추가 테스트의 #96 oracle은 최초에 잘못된 `check-context-isolation.py`를 호출한 것을 확인했다. 현행 소유자는 `check-event-publish.py:212–239`이므로 테스트를 그 실제 checker로 교정했다. production checker는 변경하지 않았다.

## 최종 검증

- `python3 -B workspace/tools/pregate_field_report_smoke.py` — exit 0, 24개 통과. 최종 로그 `task-1-green.log` (24 tests, 20.883s).
- 변경 Python 3개를 `compile(read_bytes(), path, 'exec')`로 검증하고 두 배포본 bytes를 직접 대조 — 통과, `task-1-compile-mirror.log`. 검증용 pycache는 생성하지 않았다.
- 실제 `design_pregate.py`/`--check-report` CLI: 선언확정 exit 2 → 처분 전 exit 3 → ignored 처분 후 exit 0, 요약에 선언 확정 1건. `task-1-check-report-cli.log`에 입력 산출 report와 CLI 출력 저장.
- `git diff --check` — 통과.
- 기존 전체 fixture 최종 실행 결과는 아래 최종 상태 행에 기록한다. 명령 `python3 -B workspace/tools/pregate_fixture_run.py`, 로그 `task-1-legacy-fixtures.log`.

## 자가리뷰 및 남은 경계

1. **독립 리뷰 concern: public 메서드에 직접 UoW 인자를 적는 기존 source #197 경로.**
   `add .../save_book_use_case.py`, `SaveBookUseCase.execute(self, uow: BookUnitOfWork) -> None`, 효과 `write uow=BookUnitOfWork`, 명시 port import를 전사하면 선언 checker는 정상 `[]`이다. 하지만 기존 transaction checker는 생성된 `raise NotImplementedError` 본문에 쓰기 호출이 없으므로 #197을 낸다. 재현의 정확한 입력·스텁·출력은 `task-1-source-197-probe.log`에 있다. 소유 분기는 `check-transaction-boundary.py:449`에서 public 메서드를 순회해 `:499–504`의 has_uow/no-write 조건을 적용하는 부분이다.
   같은 입력을 `__init__(self, uow: BookUnitOfWork)` 생성자 주입으로 바꾸면 선언 `[]` 및 transaction checker clean이다. 따라서 원 요구의 표준 생성자 주입은 해결되어 있으며, concern은 실제 기존 코드 update가 아닌 생성 public 메서드 직접 파라미터형이다. `check-usecase-dto-placement.py:392–399`와 정본 #635는 execute가 자기 Command/Query 계약 객체 하나를 받는 형태를 소유하므로 해당 직접 UoW 입력의 표준 적합성도 따로 검토해야 한다. 입력 계약 적합성과 생성 본문의 사각은 별개의 판단이다. 새 source 필터는 추가하지 않았고, Task2 책임으로 확정하지 않았다.
2. 선언확정 + S1 deferred 결합 CLI는 brief의 의존 경계대로 Task2 생성 분리 이후 통합 검증 대상이다. 이번 Task1 단독 완료 증거로 주장하지 않는다.
3. 역할·프롬프트·정본 의미 동기화는 지정된 Task6 책임이다. 이번 변경은 Python 원본과 byte 미러, smoke만 소유한다.
4. update 기존 함수/class 본문은 검증되지 않는다. marker 성공은 본문 update 성공의 증명이 아니며 S5가 유지된다. 지원 밖 동적 타입 의미/컨테이너는 후보로 남긴다. 실제 프로젝트 실행은 하지 않았다.
5. Serena/Graphify는 opt-in 표식이 없다는 coordinator 확인에 따라 검색·로드·초기화·호출하지 않았다.

최종 기존 fixture 상태: **exit 0 / PASS**. 15종 + E 계열 6단계 + 유닛 매트릭스, imports exit 0/5/5, enforce 7, --check-report 14단계를 최종 코드로 통과했다(`task-1-legacy-fixtures.log`).
최종 상태: **DONE_WITH_CONCERNS** — 위 public 메서드 직접 UoW 입력의 기존 source #197은 독립 리뷰 판단 대상으로 남겼다.

## Fix round 1 — 독립 리뷰 M1/M2 보완

리뷰의 **B0/M2/m0, spec FAIL / quality CHANGES REQUIRED**를 확인하고 필수 두 건만 고쳤다. 라운드 변경은 `_render_marker_update`, 원본 byte 미러, smoke 신규 테스트 2개에 한정된다. 라운드 차분은 `task-1-fix-round1.diff`다. 정본/원보고서/TTL·Task2·#197 필터는 수정하지 않았다.

- **M1**: module pytestmark가 없는 상태에서 새 비어 있지 않은 목록을 prefix에 삽입할 때, 그 위치에서 참조할 `import pytest`를 함께 삽입한다. 기존 pytest import와 본문 bytes는 이동/삭제하지 않는다. 따라서 기존 import가 있으면 import 문이 한 번 더 들어가지만 새 목록 평가 전에 binding이 존재하며, docstring/future 위치도 유지한다. 기본 입력과 docstring/future 입력을 최소 fake pytest module로 실제 평가해 `pytestmark == ['slow']`, 기존 함수 반환값, 기존 코드 구간 및 원 source bytes 보존을 확인했다.
- **M2**: module 범위에서 pytestmark를 root로 하는 Subscript Store/Del을 발견하면 `module pytestmark subscript mutation — 최종 목록 미해소`라는 구체적 S5로 보류한다. 대입/삭제/slice/AugAssign/조건부 subscript 변경에 대해 빈 목록과 비어 있지 않은 목록을 각각 요청해 사본·원본 bytes 불변, materialized 0, 구체적 S5를 확인했다. 대표 원본은 fake pytest 실제 평가에서 `['django_db']`를 내는 정상 입력임도 검증했다. 동적 최종 상태를 추론하거나 실행하는 기능은 추가하지 않았다.

**RED** 명령:

```sh
python3 -B workspace/tools/pregate_field_report_smoke.py FieldReportTest.test_marker_new_list_evaluates_after_pytest_binding FieldReportTest.test_marker_subscript_mutations_remain_s5_without_writes
```

`task-1-fix-round1-red.log`: exit 1, 2 tests / failures=10, errors=2. M1은 새 목록이 pytest import보다 먼저 평가되어 두 입력에서 NameError. M2는 원문 불변 또는 구체적 S5 단언 실패. 수정 전에 직접 확인한 실패다.

**GREEN**:

- 같은 focused 명령: exit 0, 2 tests, 0.482s — `task-1-fix-round1-focused-green.log`.
- `python3 -B workspace/tools/pregate_field_report_smoke.py`: exit 0, **26 tests, 20.494s, OK** — `task-1-fix-round1-green.log`. 기존 24개와 신규 2개, 기존 실제 CLI 대조를 함께 실행했다.
- 변경 Python 3개 `compile(read_bytes(), path, 'exec')`, 배포본 byte 대조: 통과 — `task-1-fix-round1-compile-mirror.log`.
- `git diff --check`: exit 0. 최종 함수·신규 테스트와 라운드 변경을 직접 읽어 자가리뷰했다.

변경이 marker update에 한정되어 코디네이터가 지정한 covering run까지만 수행했다. 앞선 전체 pregate fixture PASS를 이번 수정 이후 재실행한 것으로 주장하지 않는다. Serena/Graphify는 opt-in 부재로 사용하지 않았다.

라운드 결과: **DONE — M1/M2 수정과 covering 검증 완료, 독립 재리뷰로 전달.** 기존 직접 execute UoW source #197은 리뷰에서 #635 비표준 입력 경계로 판정했으므로 필수 수정으로 확장하지 않았다. Task2/Task6 의존 경계는 그대로다.
