# 현장 보고 4 잔여 12건 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. 이 저장소의 사용자 권한·단계 게이트가 스킬의 자동 커밋·정리 기본값보다 우선한다.

**Goal:** F4-1·F4-9~19의 승인 방향을 규범·설계 예보·실검사에 일치시키고, 제거할 오탐과 보존할 진탐을 함께 검증한다.

**Architecture:** 기존 AST 검사기와 pre-gate의 명시 재료 전사 구조를 유지한다. pre-gate에 선택형 효과 선언과 명시 타입 연결 검증을 추가하며 실제 본문과 생성 본문의 근거를 분리한다. 규범은 TTL에서 개정하고 투영·소성·두 런타임 미러를 함께 갱신한다.

**Tech Stack:** 배포 Python 표준 라이브러리·AST, 메인테이너 `.venv` RDF 도구, unittest 기반 현행 smoke/fixture, Make 검증.

**Spec:** `workspace/eval/field-report-4-followup/brief.md`. 문제 리뷰 A/B/C는 같은 폴더의 `problem-*.md`다. 기준 HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996`, 플러그인 2.18.2.

## Global Constraints

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시와 기존 render-sync가 요구하는 개정 graph 절의 기준선에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.

## 문제 단계 판정과 계획 입장

문제 리뷰 3건의 BLOCKER는 0이다. F4-16은 승인된 규범 폐지, F4-9·13은 규범 정합화/완화, F4-19는 거절 정책 보존과 안내 개선이다. 나머지는 확인된 구현/예보 공백이다. 원 보고서의 ‘모든 OHS’, ‘모든 Enum’, ‘서로 다른 with이면 독립’, ‘OHS 소비 시 domain import 필수’라는 일반화는 채택하지 않는다.

MAJOR 구현 제약은 아래 계약과 반대 대조로 닫는다. 기술 문법·정적 지원 범위는 기존 사용자 방향의 구체화다. 계획 적대 리뷰에서 이 범위로 원 사례를 해결할 수 없거나 새 정책이 필요하다는 사실이 나오면 구현 전에 보고한다.

## 파일 책임과 작업 경계

| 작업 | 원본 소유 파일 | 산출물/검증 |
|---|---|---|
| 1. 효과·marker·DTO 명시 검증 (F1/F18) | `design_pregate.py` | `pregate_field_report_smoke.py`, machine 입력·보고·hash |
| 2. 생성 근거·실행 모드 (F12/F19) | `design_pregate.py` | 같은 smoke와 `pregate_fixture_run.py`의 실제 CLI |
| 3. admin context (F9) | `check-public-surface-annotation.py`, pregate의 생성 근거 연결 | `field_report_checker_smoke.py`, 실제/스텁 차등 |
| 4. AST 판정 (F10/F11/F14/F15) | `check-context-isolation.py`, `check-domain-model.py`, `check-port-adapter-pairing.py` | `field_report_checker_smoke.py` |
| 5. 기능 폴더·50행 (F16/F17) | `checker_target.py`, skeleton/pairing/domain-model/DTO/context 검사기, `registry_gate.py` | 같은 smoke, snapshot/직접 실행 |
| 6. 규범·현재 문서 정합화 (F1/F9/F13/F16/F18/F19) | 아래 TTL 좌표·현재 대장·문서 | render/corpus/rulepack, 규범 시나리오 |
| 7. 통합·구현 리뷰·최종 검증 | Make/봉인 및 이 계획의 검증 기록 | 리뷰 3인+최종 감사, 미처리 보고서 |

위 파일은 모두 기존 파일이며 경로 앞 `dddjango/scripts/` 또는 `workspace/tools/`는 작업별 Files에서 구체화한다. 별도 범용 AST 프레임워크나 예외 처리 DSL은 만들지 않는다.

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

- [x] **Step 1:** smoke에 literal 기대값을 가진 실패 테스트를 추가한다.

```python
self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, copy)], [("#197", True)])
self.assertIn("pytest.mark.django_db", updated_source)
self.assertEqual(original_source.read_bytes(), frozen_source)
```

대조: read-only/none 정상, read-only/명시 UoW 모순, read-only/none/주입 모순, write/명시UoW 정상과 write/none/주입의 비차단 메모, 이름 추정 금지, 효과 누락·중복·hash; marker 유지/추가/제거·class DB 유지·nodeid/동적/중복/지원주소 오전파 방지; DTO 직접/중첩/container/alias/forward/동명 VO/Literal/순환/update·실체화0; 실제 import #95/#96 유지.
- CLI 대조도 같은 smoke의 임시 git fixture로 수행한다: update만 있고 실체화0 + 선언확정→exit2/report 처분 누락 red, 선언후보만→기존 skip4/결손5 유지, marker update→실제 #387 생성/제거와 class/function DB 신호 보존, 효과 hash 변경→stale, 선언확정+S1 deferred 동시→exit2. helper 반환·marker 문자열만으로 CLI 성공을 주장하지 않는다. 기존 add의 nodeid 물리 신호 결합은 유지하고 새 nodeid 제한은 **update**에만 적용한다.
- [x] **Step 2:** `python3 -B workspace/tools/pregate_field_report_smoke.py`의 신규 실패가 해당 결함 때문임을 기록한다.
- [x] **Step 3:** 위 자료 구조·파서·명시 판정·marker의 국소 치환과 보고를 구현한다. source/사본 경계를 지키고 byte 미러한다.
- [x] **Step 4:** 같은 smoke를 재실행하여 신규 대조와 기존 15개를 함께 통과시킨다. 변경된 `.py`를 compile하고 테스트가 실제 parser/materialize/report 경로를 호출하는지 검토한다.
- [x] **Step 5:** 작업 diff/테스트 증거를 검토하고 중대한 문제를 닫는다. 커밋 없이 다음 작업으로 간다.

### Task 2: 생성 메서드의 미검증 분리와 실행 모드 안내 (F4-12/F4-19)

**Files:**
- Modify/Mirror: 양 runtime `design_pregate.py`.
- Test: `workspace/tools/pregate_field_report_smoke.py`, `workspace/tools/pregate_fixture_run.py`.

**Interfaces:** materialize report에 `generated_methods`를 추가한다. 구조는 `dict[path, list[{owner, method, lineno, end_lineno}]]`이며 **이번 렌더가 만든 AST에서만** 기록한다. 기존 `materialized`/`unsimulated` 등 key는 보존하고 구조화 필드를 담는 반환 타입으로 맞춘다. `run_gate`는 기존 `introduced.json`의 `attributed_lines`, `records`, `unmatched_lines`, `candidate_lines`, `candidate_records`와 raw exit/stdout을 함께 반환한다. `record.file`의 끝 `:숫자`가 원본 행이며 정규화 문자열의 `:N`에서 행을 복원하지 않는다.

후처리 `partition_generated_findings(gate_result, generated_methods) -> (retained, deferred)`는 **registry 전체 정규화 귀속 key → 그 key에 대응하는 원본 레코드 전부**를 결합한다. `_stable_id(rule+path)`로 cohort를 만들지 않는다. 기존 sidecar payload와 공용 정규화/레코드 line 변환을 쓰며 Findings 스키마·귀속 identity를 개편하지 않는다.

```python
if rule == "#376" and location_matches_generated_after_commit:
    deferred.append("S1: 생성한 after_commit 본문 — on_commit 구현 미검증")
else:
    retained.append(line)
```

- 같은 귀속 key에 대응하는 **모든** 원본 record의 path+line이 정확한 생성 `after_commit` 내부인 #376일 때만 그 key를 S1로 분리한다. 생성파일의 다른 메서드·다른 규칙, 기존 update 실코드, 단순 `raise NotImplementedError` 실물은 제외 근거가 아니다. 비생성·다른 위치·불명 record가 하나라도 섞이거나 대응 record가 없거나 unmatched이면 key 전체를 유지한다. #566은 이 분리에 넣지 않는다.
- raw registry exit 1/자료 결손은 계속 RunError이며 분리로 green을 만들지 않는다. registry의 확정 귀속 항목을 분리한 후 남은 항목과 Task1 선언 확정으로 최종 exit를 정한다. raw exit2에 설명할 귀속 항목이 없으면 RunError로 fail-closed한다.
- 화면/리포트에는 ‘원 registry 결과’와 ‘생성 본문 S1 미검증’을 구분한다. S1을 verified/적용 불가/filtered로 표현하지 않는다. `--check-report`에서 미검증 정보가 보존되며 실제 G2 checker는 수정하지 않는다.
- 실행 모드는 `초기 예보(기준선 기본 HEAD)` / `명시 재예보(--base X)`로 표시한다. baseline 실존 add와 baseline 부재+overlay 실존 add를 다른 오류로 안내한다. update가 기준선에 없을 때 add라는 말만 내지 말고 초기/재예보의 적용 목적을 함께 적는다.
- 기존 12조합(add/empty/update × 기준선 실존/부재 × 초기/명시) exit 정책과 기실현 lifting을 유지한다. 초기 add를 자동 허용하지 않는다. commit/stash/기준선 이동을 자동 실행하거나 무조건 처방하지 않는다.
- file-plan은 승인 제품 변경의 경로, coordinator 작업 기록·gate report·임시 로그는 계획 재료 밖임을 안내한다. docs/**나 비-Python 파일을 일괄 금지하지 않는다. 당시 작업기록 오편입 사례를 설명하되 파일명만으로 자동 삭제하지 않는다.

- [x] **Step 1:** 실제 CLI에서 생성 after_commit/#376 S1, 기존 잘못된 본문/#376 유지, 실제 robust 누락/#566 유지를 반대 대조한다. 기존 fixture builder를 사용하고 original bytes를 비교한다.

```python
self.assertEqual(generated_exit, 0)  # 해당 규칙 외 위반이 없는 최소 fixture
self.assertIn("S1", generated_report)
self.assertEqual(real_bad_exit, 2)
self.assertIn("[#376]", real_bad_output)
self.assertIn("[#566]", robust_missing_output)
```

추가: 동일 정규화 key의 두 위치가 모두 생성/생성+실물 혼재/행번호 누락, 가짜 stub 텍스트, 자료 결손·unmatched, 선언확정과 deferred 동시, 기존 12조합의 exit/원인문구/모드, report-check. raw 귀속 수와 retained/deferred 수를 별도로 대조한다.
- [x] **Step 2:** 실패 테스트 실행·원인 기록 후 provenance를 생성 시점에 연결하고 후처리/메시지를 구현한다.
- [x] **Step 3:** `python3 -B workspace/tools/pregate_field_report_smoke.py`와 `python3 -B workspace/tools/pregate_fixture_run.py`를 실행한다. helper 결과만으로 CLI exit를 증명하지 않는다.
- [x] **Step 4:** byte 미러와 작업 리뷰를 완료한다.

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

- [x] **Step 1:** 실제 원형을 가진 작은 admin fixture(Parler TranslatableAdmin→override→private `_render_failed_submission`→UI request metadata/form·inline·media 조립→`context.update(extra_context or {})`→render), 별칭 ModelAdmin, each_context+UI dict를 추가한다. 동명 가짜/불명 외부 base, 도메인 소비/일반 클래스/같은 함수 별도 dict/JSON/맨몸 generic/무주석을 반대 대조한다. 생성 스텁 CLI는 multiline의 열린 context+별도 payload+bare Any, 두 클래스의 동명 메서드, 반환+인자 진단과 원래 후보의 S1 보고를 함께 확인한다.

```python
self.assertEqual(context_rules(valid_admin_flow), [])
self.assertIn("#647", context_rules(context_used_for_business))
self.assertIn("#650", json_rules(admin_parses_unvalidated_input))
```

- [x] **Step 2:** RED 확인 후 좁은 origin/annotation 소유·흐름 판정을 구현한다. 불명 흐름은 후보를 유지한다.
- [x] **Step 3:** 실제 checker와 pregate 생성 스텁을 각각 실행하고 차이를 S1로 표시한다. 위 두 smoke와 현행 typing fixtures를 실행한다.
- [x] **Step 4:** diff와 반대 대조를 리뷰한다. Task6의 같은 규칙 표와 연결 전에는 F9를 완료 처리하지 않는다.

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

- [x] **Step 1:** builder alias/inline/rebind/0·2·cursor·nested, Enum closed/custom/rebind/Flag, UoW 순차동명/중첩/outer atomic/lock/unknown/nested 함수/#550/#257, code domain/vendor/unknown/except/RHS/chained 대조를 literal rule 기대값으로 추가한다.

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

- [x] **Step 2:** 각 그룹 RED 확인 → 최소 AST 수정 → 해당 그룹 GREEN을 순서대로 수행한다. 이름 변경만으로 동일 의미의 판정이 달라지지 않는 대조를 포함한다.
- [x] **Step 3:** `python3 -B workspace/tools/field_report_checker_smoke.py` 및 관련 현행 checker fixture를 실행하고 미러한다.
- [x] **Step 4:** 작업 리뷰에서 자동확정/후보 경계와 scope를 확인한다. 현재 기능보다 광범위한 데이터 흐름 분석을 추가하지 않는다.

### Task 5: 캐시뿐인 선택적 인스턴스와 50행 폐지 (F4-16/F4-17)

**Files:** `dddjango/scripts/checker_target.py`, `check-layer-skeleton.py`, `check-port-adapter-pairing.py`, `check-domain-model.py`, `check-usecase-dto-placement.py`, `check-context-isolation.py`, `registry_gate.py`와 byte 미러. Test: `workspace/tools/field_report_checker_smoke.py`, `registry_gate_smoke.py`의 snapshot 경계.

**Interfaces:** `checker_target.cache_only_instance(path: Path) -> bool`. 재귀 실제 작업 트리 검사에서 `__pycache__`와 그 아래 캐시 파일 흔적이 적어도 하나 있고 그 밖의 파일이 전혀 없어야 True. 빈 하위 디렉터리는 허용하지만 캐시 흔적 없는 완전 빈 폴더는 False. `.py`/빈 `__init__.py`/기타 실파일·숨김 비캐시 파일·symlink·읽기 오류가 있으면 False. Git tracking은 판정 재료가 아니다.

```python
if is_optional_instance_slot and checker_target.cache_only_instance(child):
    continue
```

- 적용 소유 지점은 skeleton의 optional `<instance>` 열거, pairing의 capability/adapter 인스턴스 열거, domain-model의 `_aggregate_dirs/_check_layout`, DTO의 usecase 인스턴스 열거 및 `_check_use_case` 진입, context-isolation의 `_check_ohs` 서비스 인스턴스 열거다. 동일 상대경로 선택 슬롯을 snapshot에서도 사용한다. 필수 BC/layer/port/adapter 고정 부모·골격 요구는 필터하지 않으며 전역 `_entries` 전체 제외로 대체하지 않는다.
- registry `_snapshot_current`는 copytree ignore가 캐시를 없애기 **전 원 작업 트리에서** 동일 술어로 선택적 인스턴스의 상대 경로 집합을 구한다. 사본의 해당 인스턴스만 제외한다. 고정 경로·다른 부모를 따라 지우지 않으며 원 작업 트리 파일은 삭제하지 않는다. 직접 checker와 snapshot gate가 같은 결과를 낸다.
- pre-gate가 이미 가진 계획 remove의 부모 정리 정책과 섞지 않는다.
- skeleton에서 `PROMO_PART_MIN_LINES`와 #642 방출을 제거한다. `_phys_lines`와 #644 200행 후보 및 #638/#639/#640/#641/#643는 유지한다. 규범 삭제는 Task6에서 완성한다. registry 진단 identity를 이 문제 때문에 고치지 않는다.

- [x] **Step 1:** cache-only 직접/중첩, untracked 실제소스/빈init, cache 없는 빈폴더, source+cache, symlink, 필수고정골격 누락, snapshot 경계 테스트를 추가한다. aggregate 캐시의 #299/#256, usecase 캐시의 #193/#570/#569, OHS 캐시의 #152를 직접 checker CLI와 snapshot gate 양쪽에서 대조하고 실소스 혼재 시 기존 진단 유지도 확인한다. 원본 파일 목록/bytes를 보존 비교한다. 1~49행 부품은 #642 없음, 부품0/본체누락/중첩/정크드로어/201행은 기존 진단 유지.

```python
self.assertTrue(checker_target.cache_only_instance(cache_only))
self.assertFalse(checker_target.cache_only_instance(untracked_python))
self.assertNotIn("#642", violations(short_valid_component))
self.assertIn("#643", violations(no_component))
```

- [x] **Step 2:** RED 확인 후 제한된 술어·열거·snapshot 경계를 구현한다.
- [x] **Step 3:** `python3 -B workspace/tools/field_report_checker_smoke.py`와 `python3 -B workspace/tools/registry_gate_smoke.py`를 실행한다. fixture 기대값 변경은 실제 폐지 진단에만 한정한다.
- [x] **Step 4:** byte 미러·작업 리뷰를 완료한다.

### Task 6: 규범·현행 문서·미러 정합화 (F4-1/9/13/16/18/19)

**Files/좌표:**
- `ontology/rules/agent-design-architect.ttl`: `s005/b33~b37` R-3424~R-3429/R-3431(채널·명시검증·후상태·사각), `s005/b11` R-1617(내부/외부 오류 분리).
- `ontology/rules/command-dddjango.ttl`: R-3432~R-3436/R-3445(새 hash·미검증·모드). 실제 doc_key/Work를 원문으로 확인하고 존재하지 않는 블록을 만들지 않는다.
- `ontology/rules/discipline-houserules-skill.ttl`: R-3447/R-3448/R-3451/R-3452/R-3457(admin), R-3417(승격 50행 제거). R-3148~R-3154/#493·R-3458/R-3459/#646·#650 유지.
- `ontology/rules/discipline-houserules-final.ttl`: R-3410의 50행 부분만 삭제하고 #643 유지, R-3468의 없어진 하한 비교 문구 정리.
- `ontology/rules/agent-discipline-reviewer.ttl`: R-1117/R-1118(admin 처분), R-1037/R-1071(내부 실패/HTTP), Enum Q2·#546/#557 관련 판정이 새 확정/후보 범위와 충돌하면 해당 문장만 정합화.
- `ontology/rules/agent-design-review-api.ttl`: R-2677.
- `ontology/rules/implementation-django-ninja-final.ttl`: R-0084.
- `ontology/rules/implementation-django-ninja-skill.ttl`: R-2941.
- `workspace/design/2026-08-08-tree-revision-spec.md`: 현행 #192/#642/#645/#647/#546/#557/#197/#202 적용범위 설명.
- `workspace/plan/2026-08-11-rule-owner-map.md`: 현행 #642 폐지, #645/#647/변경 검사범위의 소유 설명.
- `workspace/design/2026-08-11-predicates.md`: #645/#647 admin 허용·후보·기존규칙, #546/#557의 확정/후보/물음. #546/#557은 spec/owner-map/술어를 `ast+`·검사기+감수자 소유로 동기화한다. 새 #197/#202 선언 후보는 architect·해당 설계 리뷰/감수 처분이며 실코드 검사 범위와 구분한다.
- `docs/file_tree.html`, `docs/mkrev2.py`: 승격 50행 하한과 고정 adapter의 50행 비교 문구만 수정. `docs/master.html` 제외.
- 렌더된 Claude/Codex 역할·SKILL·reference, `workspace/reference/**`, 양쪽 `rulepack.json`; 필요한 ledger/census seal.
- Test: `workspace/tools/field_report_checker_smoke.py`의 규범 계약 대조와 이 작업 리뷰 기록.

**F13 문면의 결과(6중복에 같은 의미 적용):**

> 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다.

F13은 #555/계약 예외 소유를 약화하지 않는다. 검사기 변경이 필요 없는 규범 수리이며 exception-map을 catch DSL로 확장하지 않는다.

**F16 현행 대장:** #642를 현행 시행 규칙으로 남기지 않고 대장의 기존 폐지 표현을 따른다. spec #490/#644와 predicates #644의 `#638~#643`을 `#638~#641·#643`으로 맞춰 폐지한 번호의 의미상 잔존도 없앤다. #642 폐지와 #546/#557 grade 변경에 따른 현행 집계표·읽는 법 수치는 실측으로 맞춘다. R-3410 Work 전체를 삭제하지 않으며 기존 ID/ISSUED 이력 보존. R-3417/R-3410 label/currentExpression은 남은 의미로 개정한다. 다른 ‘트리 50행’/함수길이 smell50은 유지한다.

**F1/F18/F9/F12 문면:** 선택형 6번째 입력(use-case-effects, 기존 다섯 채널+효과)을 선언하고 hash 문면을 맞춘다. S2의 ‘내부 모순 전부 사각’은 명시 read-only/UoW와 출처 결합 DTO에 한해 축소한다. S3/S5는 명시 후상태 지원과 기존 본문 미검증을 분리한다. 생성 메서드의 S1은 실제 구현 검증을 대신하지 않는다. F9는 Task3의 다섯 규칙 표·private 전달 helper·실제 소비 경계를 architect와 감수자가 같은 뜻으로 적용한다.

- [x] **Step 1:** 규범 시나리오의 전후 기대 처분을 기록한다: admin 화면 조립 허용/업무 소비 검증, IntegrityError known→concrete/unknown→일반 내부 계약+500, 20행 응집 부품 허용/부품0 환원, read-only+UoW 모순/미기재 미검증. 기존 문면에서 반송/모순되는 직접 문장을 대조한다. 문구 grep만으로 역할 수행을 증명했다고 주장하지 않는다.
- [x] **Step 2:** 기존 Work 리터럴을 최소 개정하고 새 Expression을 저작 규약대로 연결한다. 새 독립 의무가 꼭 필요할 경우에만 ISSUED 마지막 번호 뒤 채번한다. TTL을 정본 직렬화하고 게이트를 통과한다.

```bash
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py
for doc_key in agent-design-architect command-dddjango discipline-houserules-skill discipline-houserules-final agent-discipline-reviewer agent-design-review-api implementation-django-ninja-final implementation-django-ninja-skill
do
  PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render.py --apply "$doc_key"
done
make rulepack
python3 workspace/tools/corpus_mirror_sync.py --write
python3 -B workspace/tools/spec_lint.py
```

위 여덟 doc_key의 소유 블록을 개정한다. 통째 재생성·중복 문장 추가로 범위를 넓히지 않는다.
- [x] **Step 3:** 현재 사람용 문서/생성원/대장과 의미 미러를 맞춘다. NAR을 바꾼 경우 해당 SHA와 사유를 LEDGER에 append한다.
- [x] **Step 4:** ontology gate/render sync/structural/spec lint·관련 smoke를 실행하고 규범 리뷰로 여섯 raw 문면과 F9/F16 전파를 확인한다.

### Task 7: 통합 리뷰·검증·미처리 목록 정리

**Files:** 이 계획의 진행 상태, `workspace/eval/field-report-4-followup/`의 구현/리뷰/최종 증거, `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md`, 변경 시 `workspace/tools/manifest_seal.py`의 현행 봉인 산출물. 기존 harness 확장이므로 새 독립 test runner/Make target은 만들지 않는다.

- [x] **Step 1:** 변경 코드/규범/미러와 테스트를 동결해 독립 구현 리뷰 3명에게 전달한다. A: 실제 검출·미탐 반례, B: 규범·입력/리포트 일치, C: 증거·scope·기존 진탐 보존. 자기 구현을 본인이 승인하지 않는다.
- [x] **Step 2:** BLOCKER/MAJOR를 모두 수정하고 해당 변경을 재리뷰한다. 새 정책이 필요한 지적은 임의로 해결하지 않고 사용자에게 보고한다. 단순 기술 보완은 합의 범위 안에서 처리한다.
- [x] **Step 3:** 12건 각각 actual checker/pregate/규범에 필요한 증거가 있는지 독립 최종 감사한다. 기능 테스트가 없는 항목, S1을 green으로 과장한 항목, 실제 해결이 없는 보고서 삭제는 실패다.
- [x] **Step 4:** 완료한 항목만 원 보고서의 요약+본문에서 제거한다. 부분 미처리면 그 잔여를 ID 그대로 남기고 번호를 당기지 않는다. 원 보고서의 사용자 추가분이 변했는지 현재 SHA와 동결본을 비교해 새 내용을 보존한다. 완료 증거는 본 계획/리뷰 기록에 남긴다.
- [x] **Step 5:** 봉인 대상 최종 수정 이후 봉인을 재발행하고 최종 필수 검증을 수행한다.

```bash
python3 workspace/tools/manifest_seal.py --write
make verify-mutation
make verify
git diff --check
```

verify 실패로 봉인 대상 파일을 고쳤으면 봉인→make verify를 다시 실행한다. 보고에는 마지막 실행 로그 경로와 그 수치만 사용한다. manifest/설치구조를 실제 변경했다면 `claude plugin validate dddjango --strict`도 실행한다. 버전은 이 계획에서 올리지 않는다.
- [x] **Step 6:** 사용자에게 구현 결과, 의도적으로 남긴 지원 한계, 3리뷰/최종 감사·검증 결과, 미처리 수를 보고하고 종료한다. Serena/Graphify opt-in 부재를 한 줄 남긴다. 커밋·배포가 수행됐다고 말하지 않는다.

## 진행 기록

- 2026-09-11: 문제 리뷰 A/B/C 완료. BLOCKER 0, 추가 사용자 정책 결정 필수 0. MAJOR 구현 제약을 위 계획에 수용했다.
- 최초 계획 SHA-256 `bc3e95b7d0146e917ecbbe70ab5e69fee95cbfb26ed3020a9beb0e7dc5eccdad`에 계획 리뷰 A(0/2/0), B(0/3/0), C(0/2/4)를 받았다. 중복 지적을 합쳐 원본 레코드 운반/슬롯 식별, read-only 조건, 실제 admin 원형과 세 상태, 현행 술어/소유 전파, cache-only 직접 소비 지점을 보완했다. C의 minor 4도 반례와 CLI 검증 계약으로 반영했다.
- 개정 계획 재리뷰: A/B/C 모두 지적 ADDRESSED, 잔여 B/M/m 0/0/0. 추가 사용자 정책 결정 필수 0. 승인에 따라 구현 단계 진입.
- 기준 회귀 실행: `python3 -B workspace/tools/pregate_field_report_smoke.py` 15/15, `python3 -B workspace/tools/field_report_checker_smoke.py` 12/12 green. 신규 구현 검증 증거가 아닌 변경 전 기준선이다.

- 실행 위치: `/Users/hyun/.cache/dddjango-field4-followup-20260911` (기준 HEAD에서 분리한 detached worktree). Task1~6 및 구현 리뷰·독립 최종 감사·최종 전체 검증 완료. 검증된 요청 대상 변경을 primary에 반영했으며 `docs/master.html`은 기존 상태를 보존했다.

- Task2 검증 구체화: 기존 dirty update 본문은 pre-gate 앵커에 들어가 legacy이므로 그 자체로 새 exit2가 되지 않는다. 실제 checker/registry CLI의 clean anchor→bad current에서 exit2와 원본 record를 확보해 S1 분리 뒤 보존을 대조한다. dirty update의 기존 pregate exit0 경계도 보존하고, 생성 스텁·선언 확정+S1은 실제 pregate CLI로 검증한다. 앵커 정책 변경 없음.

- Task6 절차 구체화: 현행 ontology_render_sync.py는 graph-owned 절도 LEDGER baseline_sha256에 대조한다. 개정 9절은 기존 이력을 보존하고 기준선 행을 append한다. NAR 변경은 없으며 새 정책·검사기 완화가 아니다.

- Task6 corpus 주소 보존: graph 기준선 개정 후 기존 migrated SHA가 비어 있던 reference 2절은 변경 전 동결 소스의 실제 스팬 해시를 검증해 원장 행으로 보충한다. source 파일은 바꾸지 않고 과거 행도 보존한다.

- Task7 최종 검증 1차: 6묶음 중 ontology/core/regen에서 기존 기대값·생성 메타데이터 불일치가 확인됐다. 승인한 Expression 31개 개정, #546/#557의 확정→후보 전환 및 관련 문구 변경을 실제 레코드와 대조해 `workspace/eval/fixtures/ontology_gate/target-counts.json`, `workspace/tools/checker_baseline_matrix.py`, `workspace/tools/findings_count_matrix.py`, `workspace/tools/construct_drift_report.py`, `workspace/tools/findings_smoke.py`의 해당 기대값만 맞춘다. 기존 생성기로 양쪽 `pregate_symbol_kinds.json`의 소스 해시를 갱신한다. 종류·검사기 동작·fixture·정규화 규칙은 바꾸지 않는다. 보완 후 독립 재검토 → 재봉인 → 필수 전체 검증을 다시 수행하며, 1차 RED는 완료 수치로 사용하지 않는다.

- Task7 전체 검증 2차: 5묶음 green, core의 findings 스모크에서 동일 #546 전환의 중복 기대값이 발견됐다. 64개 전체 기록은 보존되며 위반 51+후보 13에서 위반 50+후보 14로 바뀐다. SHA·두 계수·표시 문구 4곳만 보완하고 독립 재검토 및 전체 검증을 다시 수행한다.

- Task7 최종 검증 3차: 재봉인 후 변이 11/11 검출, `make verify` 6/6 green(247초), `git diff --check` exit 0. 마지막 원로그는 `workspace/eval/field-report-4-followup/evidence/final-verify.log`와 `final-verify-groups/`다. 같은 실행의 pre-gate 38개·checker 49개 회귀가 모두 통과했고, 최종 봉인 63파일 해시도 유지됐다.

- 최종 반영 완료: 검증된 63개 tracked 파일과 계획·리뷰·검증 기록을 primary에 반영하고 SHA 동일성을 확인했다. primary의 `git diff --check`와 봉인 draft 대조도 exit 0이다. 완료 항목 12건은 목록에서 제거했고 F4-20 본문은 byte 그대로 보존했다. 커밋·배포 없이 종료하며 최종 결과는 `workspace/eval/field-report-4-followup/completion.md`에 기록했다.
