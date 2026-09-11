### Task 3: framework 소유 admin context만 완화 (F4-9)

**Files:** `dddjango/scripts/check-public-surface-annotation.py`, `design_pregate.py` 및 두 byte 미러. Test: `workspace/tools/field_report_checker_smoke.py`, `pregate_field_report_smoke.py`.

**규칙 표:** #493 주석 존재 유지, #645 framework 소유 슬롯 Any 제한 허용, #646 제네릭 런타임 안전 유지, #647 열린 UI context 조립/병합/전달 허용, #650 실제 JSON 소비 검증 유지. admin 경로·클래스 전체 면제는 없다.

**Interfaces:** `_admin_context_policy(mod, rel) -> dict[int, tuple[str, str]]`는 annotation AST identity별 `(allow|candidate|ordinary, 근거)`를 반환하며 `_check_explicit_any.judge`가 #645/#647에만 사용한다. allow는 확인된 framework 흐름, candidate는 framework 연결은 있으나 흐름 불명(exit 불산입+확인 질문), ordinary 또는 미등재는 현행 규칙 적용이다. 업무 소비가 확인되거나 무관한 슬롯을 후보로 낮추지 않는다. 모듈 import origin과 현행 TYPE_CHECKING alias 해소를 이용하되 이름-only 선언형 helper를 출처 증명으로 재사용하지 않는다. 이 AST identity는 같은 checker 프로세스 안의 정책용이며 pregate 프로세스 경계의 식별자로 쓰지 않는다.

- 출발점은 실제 `django.contrib.admin`의 ModelAdmin/InlineModelAdmin/TabularInline/StackedInline 계열로 해소되는 클래스와 그 framework override다. 검증된 외부 origin `parler.admin.TranslatableAdmin/TranslatableInlineModelAdmin/TranslatableStackedInline/TranslatableTabularInline`도 Django admin base 연결을 가진 좁은 목록으로 인정한다(설치 소스 `spring_dream_server/.venv/lib/python3.14/site-packages/parler/admin.py:41–42,173,624,705,719` 읽기로 확인). 임의 외부 모듈을 import/MRO 실행하지 않는다. 같은 파일의 명시 alias/기저 연결은 순환 방지하며, 동명 로컬 타입·rebind는 인정하지 않고 동적/불명 base는 후보 근거로 남긴다. 알려진 슬롯은 `changeform_view/change_view/add_view/changelist_view`의 `extra_context`, `render_change_form`의 `context`, `get_form/get_formset/get_fieldsets/get_readonly_fields`의 framework kwargs, `get_inline_instances` 반환과 `inlines`의 framework 제네릭 Any다. 같은 이름의 일반 클래스/함수는 제외하지 않는다.
- 열린 context로 인정하는 작업: 매개변수로 받기, `admin_site.each_context(request)`로 만들기, UI literal dict 조립, `dict(context)`·`{**context, ...}`·`.copy()`·`.update(extra_context)`·고정 문자열 UI 키 쓰기, `super()`의 대응 override·`render_change_form`·Django `TemplateResponse/render`에 전달.
- 알려진 hook에서 같은 클래스의 private helper로 context 인자가 직접 전달되고 **그 context binding의** 조립/전달이 확인되면 helper 매개변수·반환·지역 context annotation도 허용한다. helper 안의 form/inline/media 등 다른 UI 객체 조립 때문에 context를 배제하지 않는다. 함수 전체 statement whitelist로 판정하지 않는다. 단순 이름 context/extra_context만으로 허용하지 않는다. helper graph는 AST 함수별 방문 집합으로 끝나며 재귀/동적 호출은 불명 후보다.
- `extra_context or {}` 및 `is None/is not None`의 컨테이너 부재 처리는 조립/전달이다. request GET/POST에서 꺼낸 `is_popup/source_model/to_field` 같은 UI metadata를 context에 담아 framework sink로 전달하는 동작도 허용한다. 값이 request에서 왔다는 사실만으로 전체 context를 업무 dict로 만들지 않는다.
- context의 특정 값을 꺼내 비교·계산·상태 변경·ORM/use case/업무 함수 인자로 쓰는 행위는 실제 소비이며 기존 규칙을 적용한다. 실제 JSON 검증 규칙은 계속 독립 실행한다. 모르는 호출로 escape하면 연결된 context는 #645/#647 후보를 낸다. 동일함수의 별도 업무 dict는 여전히 검사한다.
- 스텁은 몸체의 흐름이 없다. 출처가 확정된 framework override의 고정 슬롯은 같은 규칙으로 허용한다. 생성한 admin private helper의 열린 dict annotation은 확정 pass 대신 **생성 근거가 있는 슬롯의 #645/#647를 S1 미검증 후보**로 남긴다. 슬롯 결합은 Task2 원본 record의 함수 def 행으로 생성 메서드를 고르고, 현행 producer의 정확한 `` `method()` 매개변수 `label` ``/`` `method()` 반환 타입 `` 또는 AnnAssign의 `` `target` 주석 `` 문구로 생성 AST annotation에 일대일 대응시킨다. 임의 자유 문구로 context 역할을 추측하지 않는다. multiline·동명 메서드·여러 슬롯에서 일대일 해소 실패 또는 같은 귀속 key에 다른/비생성 슬롯이 섞이면 원진단을 유지한다. 원래 candidate_records도 같은 슬롯 결합을 거쳐 S1 근거를 report/check-report에 남긴다. 다른 bare Any, 클래스 전체, 기존 실코드의 진단은 옮기지 않는다. 새 선언 채널·Findings 스키마 변경은 없다. G2는 실제 소비 흐름으로 다시 판단한다.
- 실제 모델 generic 런타임 안전과 입력 검증, #347 공통 use case 경유·ORM/BC 경계를 그대로 둔다. mypy를 느슨하게 만들거나 무주석을 허용하지 않는다.

- [ ] **Step 1:** 실제 원형을 가진 작은 admin fixture(Parler TranslatableAdmin→override→private `_render_failed_submission`→UI request metadata/form·inline·media 조립→`context.update(extra_context or {})`→render), 별칭 ModelAdmin, each_context+UI dict를 추가한다. 동명 가짜/불명 외부 base, 도메인 소비/일반 클래스/같은 함수 별도 dict/JSON/맨몸 generic/무주석을 반대 대조한다. 생성 스텁 CLI는 multiline의 열린 context+별도 payload+bare Any, 두 클래스의 동명 메서드, 반환+인자 진단과 원래 후보의 S1 보고를 함께 확인한다.

```python
self.assertEqual(context_rules(valid_admin_flow), [])
self.assertIn("#647", context_rules(context_used_for_business))
self.assertIn("#650", json_rules(admin_parses_unvalidated_input))
```

- [ ] **Step 2:** RED 확인 후 좁은 origin/annotation 소유·흐름 판정을 구현한다. 불명 흐름은 후보를 유지한다.
- [ ] **Step 3:** 실제 checker와 pregate 생성 스텁을 각각 실행하고 차이를 S1로 표시한다. 위 두 smoke와 현행 typing fixtures를 실행한다.
- [ ] **Step 4:** diff와 반대 대조를 리뷰한다. Task6의 같은 규칙 표와 연결 전에는 F9를 완료 처리하지 않는다.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Start gate and evidence
Do not implement until the coordinator explicitly dispatches this task after Task2 review passes. Task1 effects/DTO/markers are already implemented and must be preserved. The coordinator will append Task2 actual interfaces after its gate. Current publicsurface source has explicit origin/alias helpers; use bounded existing mechanisms, not a generic new type/flow framework. Actual Parler source was read during plan review at /Users/hyun/Desktop/spring_dream_server/.venv/lib/python3.14/site-packages/parler/admin.py (imports41–42, TranslatableAdmin173, TranslatableInlineModelAdmin624, Stacked/Tabular705/719). Do not execute/import the user project.
Norm propagation is Task6: no TTL or graph-owned edits in Task3. Actual #493/#646/#650 must continue to run independently. This task cannot close F9 in the original report until Task6 and final audit.

## Task2 actual interfaces (pending independent gate at preparation)
materialize -> MaterializationReport TypedDict: existing four list keys + generated_methods dict[path,list[GeneratedMethod]], where owner/method/lineno/end_lineno come from final generated AST only. For add all generated class methods are recorded (owner dotted for nested classes); module function owner empty. OHS append records only appended new function names. Other/marker-only update has no generated methods.
run_gate -> GateResult TypedDict with raw_exit/raw_stdout/attributed_lines/records/unmatched_lines/candidate_lines/candidate_records. Both candidate keys may originally be absent and are returned empty; partial keys/missing required material raise RunError.
partition_generated_findings(gate_result, generated_methods) returns retained list[str], deferred list[str] (S1 prefix). It uses exact checker + registry._normalize(findings.line_of_record(record),()) full keys and every raw record cohort. file numeric suffix alone is location proof; :N and file_raw may not recover it. Unjoinable record prevents deferral. #376 generated class after_commit only today; keep #566. Report/check-report S1 channels already exist.
Review task-2-report.md only for concrete API questions. Task2 actual pregate anchoring stays baseline+dirty before materialization: bad unchanged update is legacy. Task3 source-vs-stub contrast must similarly distinguish actual checker/registry diagnostics from newly attributed pregate output; do not change anchor semantics to fabricate exit2.

Task2 M1 correction: generated OHS functions retain their newly appended owner/method identities, then ranges are collected AFTER final marker composition. Do not regress this ordering. Task2 covering baseline now33 smoke; checker smoke remains12 baseline.

### Task3 generated-slot interpretation
Generated private helpers have no body flow to prove a context role. For confirmed admin origin, an exact generated private-helper open-dict annotation may become S1 unverified after one-to-one raw producer-slot join, independent of whether its parameter is named context or payload. A name is not semantic proof. Bare Any/non-open-dict slots, mixed or unresolved cohorts and existing bodies retain their diagnoses. This never marks the helper verified or exempts the real implementation: actual code's known business consumption remains ordinary. Include rename-invariance and S1 report checks. This is the plan's generated-vs-actual boundary, not a new exemption policy.

Task3 fixture oracle clarification: an update-only admin plan with no materialization keeps existing skip4, not green0; declarations/import defects retain their existing priority. For source-vs-generated test, assert no S1 plus skip4 rather than adding unrelated dummy files solely for a zero exit. Actual checker/registry CLI supplies real business-diagnosis evidence. This is a fixture correction; anchor and materialization policies are unchanged.
