# 현장 보고 4 잔여 12건 — 독립 계획 적대 리뷰 C

2026-09-11. 검토 대상은 `workspace/plan/2026-09-11-field-report-4-followup.md`의 최초 계획이며, 요구 정본은 같은 폴더의 `brief.md`다. 문제 리뷰 A/B/C, 관련 현행 검사기·pre-gate·fixture를 대조했다. 구현은 검토 대상이 아니며 미래 구현의 테스트 성공을 주장하지 않는다.

**판정: BLOCKER 0, MAJOR 2, MINOR 4.** MAJOR는 원 admin 사례가 계획의 지원 경계에서 빠지는 문제와, cache-only 제외가 일부 직접 검사기에 연결되지 않는 문제다. 두 건 모두 기존 사용자 합의를 구현 가능한 대상으로 좁히는 기술 보완이며 **추가 사용자 정책 결정은 필요하지 않다.** 계획에 반영한 뒤 해당 지적을 재검토해야 구현 진입 가능 판정이 된다.

## 증거 범위

- scratch 결과: `/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/dddjango-plan-C-ozzpl7c7/results.json`.
- 현행 Python 3.14에서 cache-only 선택 인스턴스 3종과 실제 소스 혼재 대조 3종의 **직접 checker CLI**를 실행했다. 출력과 returncode를 위 파일에 보존했다. registry 전체 CLI는 이 리뷰에서 실행하지 않았다. 직접 검사기와 계획상 snapshot 제외 사이의 불일치는 이 실행과 실제 호출처를 연결한 추론이다.
- annotation 위치 확인은 `_check_explicit_any`의 **helper 직접 호출**이며 CLI 증거가 아니다. Findings/Candidates는 `defer=True`, CLI sink는 scratch로 격리했다. 실제 `spring_dream_server`에서는 소스만 읽었으며 import·검사·테스트를 실행하지 않았다.
- probe 작성 중 `FindingEntry`가 slots 객체여서 `vars()`를 쓰지 못한 시행착오가 있었고, 최종 결과는 공용 `entry.line`으로 다시 수집했다. 최초 OHS probe는 `driving_layer`가 빠진 경로라 검사 대상에 도달하지 않았다. 최종 OHS 결과는 아래 표의 정확한 경로로 재실행한 결과다. 그 최초 clean을 해결 근거로 사용하지 않는다.
- 코드·규범·영구 테스트·계획·원 보고서를 수정하지 않았다. 이 파일이 유일한 영구 출력이다.

## M-C1 — F9의 허용 경계와 fixture가 실제 원 사례를 해결하지 못한다

**계획 좌표:** Task 3의 출발점·허용 동작·private helper 문단(157~164행).

실제 원 사례는 다음 파일이다.

`/Users/hyun/Desktop/spring_dream_server/application/fortune_character/driven_layer/django_fortune_character/admin/character/panel.py`

1. 14행은 `from parler.admin import TranslatableAdmin`, 105행은 `class CharacterAdmin(TranslatableAdmin)`이다. 계획은 Django admin origin으로 해소된 클래스에서 시작하지만, 외부 상속 정의를 확인하는 방법은 고정하지 않았다. 단순 `ModelAdmin` fixture만 통과하면 실제 `CharacterAdmin`은 여전히 대상에서 빠질 수 있다.
2. 읽을 수 있는 설치 소스 `/Users/hyun/Desktop/spring_dream_server/.venv/lib/python3.14/site-packages/parler/admin.py`의 41행은 `from django.contrib import admin`, 173행은 `class TranslatableAdmin(BaseTranslatableAdmin, admin.ModelAdmin)`이다. 따라서 현재 원 사례의 Django base 연결은 이름 추측 없이 **소스 읽기만으로** 확인 가능하다. 임의 외부 클래스를 import하거나 MRO를 실행할 필요가 없다.
3. `_render_failed_submission`은 context 외에도 form·inline·media를 조립한다(192~219행). context에는 `is_popup`, `source_model`, `to_field`용 `request.POST/GET` 값이 들어간다(227~229행). 마지막에는 `context.update(extra_context or {})`를 사용한다(241행).

계획의 “helper에서도 위 조립/전달만 수행”을 함수 전체 문장 whitelist로 읽거나 “request 추출 값은 실제 소비”를 context에 들어가는 모든 값에 적용하면, 이 UI 전달 사례를 계속 차단한다. 반대로 원 사례를 통과시키려고 request 값이 담긴 모든 context를 면제하면 `save_price(context['price'])` 같은 업무 소비의 진단까지 사라진다.

**최소 수정안:**

- 지원하는 외부 admin 상속은 확인한 import origin과 읽기 가능한 정의 체인, 또는 그 근거를 가진 좁은 origin 표로 연결한다. 같은 이름의 로컬 `TranslatableAdmin`은 허용하지 않는다. 출처를 못 읽거나 동적으로 바꾸면 후보로 남긴다.
- 면제 여부는 함수 전체의 순수성 대신 **해당 context binding의 조립·이동·escape·소비**로 판단한다. 같은 함수의 별도 업무 dict를 면제하지 않는 기존 문장을 유지한다.
- `extra_context or {}`, `if extra_context is None/is not None` 같은 컨테이너 부재 처리와 업무 값 비교를 구별한다. UI 메타데이터를 framework sink로 전달하는 경우와 값을 추출해 ORM/use case/업무 함수에 넘기는 경우를 분리한다.
- fixture에 실제 형태인 `TranslatableAdmin → changeform_view → _render_failed_submission`, 여러 UI 객체 조립, UI request 키, `extra_context or {}`를 넣는다. 같은 값의 업무 소비·동명 가짜 base·불명 외부 base를 반대 대조한다. Django/Parler를 fixture에서 실제 import해 실행하지 않아도 AST와 확인된 origin 재료로 검사 가능하다.

**제거할 진단:** 근거가 확인된 실제 UI context의 #645/#647. **보존할 진단:** 같은 함수의 업무 dict, 실제 입력·업무 소비, #493/#646/#650 및 ORM/공통 use case 경계. **사용자 결정:** 불필요. 광범위 admin 경로 면제는 해결안이 아니다.

## M-C2 — F17의 직접 검사기와 snapshot 적용 범위가 다르다

**계획 좌표:** Task 5 Files 및 optional 열거·snapshot 문단(229~243행).

계획은 skeleton의 optional instance, pairing의 capability/adapter instance를 필터하고 registry snapshot에서는 같은 선택 인스턴스를 제외한다. 그러나 다음 검사기도 같은 인스턴스를 직접 열거하고 필수 파일 진단을 낸다.

| cache-only 선택 인스턴스 | 현행 직접 CLI | 재현된 returncode와 진단 |
|---|---|---|
| `application/shop/domain_layer/book/__pycache__/old.pyc` | `check-domain-model.py` | exit 2, #299 + #256 |
| `application/shop/application_layer/books/list_books/__pycache__/old.pyc` | `check-usecase-dto-placement.py` | exit 2, #193 + #570 + #569 두 건 |
| `application/shop/driving_layer/open_host_service/records/__pycache__/old.pyc` | `check-context-isolation.py` | exit 2, #152 |

직접 호출 명령은 각 scratch 루트를 TARGET으로 하는 `python3 -B <dddjango/scripts/checker.py> <scratch/종류>`이며 정확한 argv는 결과 JSON에 있다. OHS에는 채택 신호용 `domain_layer/`도 두었다. 실제 소스 `draft.py`를 혼재시키면 세 경우 모두 exit 2가 유지됐으며, OHS에는 #154도 추가됐다. 따라서 캐시만 있는 사례와 미추적 실물을 구별할 수 있는 반대 대조다.

실제 호출처는 `check-domain-model.py::_aggregate_dirs/_check_layout`(172~205행), `check-usecase-dto-placement.py::_check_use_case`의 #193/#570/#569 발행(342~361행), `check-context-isolation.py::_check_ohs`(344~365행)다. 이 파일들은 Task 5의 직접 필터 수정 목록에 없다. snapshot에서 optional을 넓게 제외하면 G2는 조용해지고 직접 checker는 위 진단을 계속 내므로 “직접 checker와 snapshot gate가 같은 결과”라는 계획 계약을 위반한다. snapshot도 두 검사기 범위로 좁히면 나머지 선택 기능 폴더의 오탐이 남아 F17 전체 완료를 주장할 수 없다.

**최소 수정안:**

- cache-only라는 내용 술어를 유지하되, **선택적 instance를 열거하는 소유 지점**에 위 세 검사기도 연결한다. 전체 `_entries`나 모든 폴더를 일괄 무시하는 변경은 하지 않는다. 필요하면 같은 술어를 쓰는 구체 선택 슬롯 목록을 먼저 계획에 적는다.
- snapshot이 제거하는 상대 경로 집합과 각 직접 검사기의 제외 대상을 대응시킨다. 소스가 있는 instance·빈 `__init__.py`·캐시 없는 빈 폴더·필수 고정 부모/자식은 남긴다.
- 세 실제 CLI 사례를 수정 후 direct/snapshot 양쪽 대조에 넣는다. snapshot helper의 파일 목록만 확인하거나 pairing fixture 하나만 통과시키는 것으로 전체 일치를 주장하지 않는다.

**예상 삭제 집합:** 위 cache-only 경로에 기인한 #299/#256/#193/#570/#569/#152 및 기존 capability 사례의 파생 진단. **보존 집합:** 동일 경로에 실물 소스가 있으면 기존 필수 파일 진단, 고정 골격 부재 #488. **사용자 결정:** 불필요. 현재 합의가 선택적 기능 인스턴스 전반을 대상으로 하므로 직접 소비 지점을 연결하는 기술 보완이다.

## m-C1 — F9 생성 annotation의 S1 근거를 보고서에 남기는 실제 경로가 필요하다

현재 `_check_explicit_any`는 함수의 모든 매개변수·반환 annotation을 `fn.lineno`로 출력한다(`check-public-surface-annotation.py:773~781`). scratch의 6행 context, 7행 payload, 8행 반환 annotation이 전부 `panel.py:4`로 기록됐다. 이 중 `context: dict[str, object]`는 candidate, `payload: dict[str, Any]`와 열린 object 반환은 violation이다.

Task 2의 `generated_methods`는 메서드 범위만 가지며 `run_gate()`는 `introduced.json`의 `attributed_lines`만 반환한다(`design_pregate.py:1428`). Task 3의 “해당 annotation 위치로 S1 미검증 후보”를 이 위반 라인 partition만으로 구현하면 원래 candidate인 context 매개변수의 S1 정보는 보고서에 연결되지 않거나, 같은 함수 줄의 다른 annotation을 잘못 묶을 수 있다.

**보완:** 생성 시 annotation의 owner/method/slot(매개변수명·반환·지역 변수)과 위치를 기록하거나 동등한 구조화 식별자를 쓴다. 원래 candidate도 S1 근거를 보고서와 `--check-report`에 보존하는 경로를 정한다. 같은 함수의 context, 다른 payload, bare Any를 함께 둔 CLI 대조로 좁은 처분을 증명한다. 위치만 불명하면 기존 진단 유지라는 Task 2 원칙을 따른다. 외부 출력 포맷 전체 재설계는 필요하지 않다.

## m-C2 — 출처 판정에서 import 주소와 실제 정의를 같은 증거로 쓰지 않는다

F10/F11/F15는 단순 이름 추측을 배제하고 있어 방향은 적절하다. 구현 검토에서는 다음 작은 반례를 입력 경계에 명시해야 한다.

- F10: composition_root가 import한 객체 모두가 use case builder는 아니다. 허용 builder의 표준 경로·심볼/반환 증거를 고정하고, builder binding이 분기 한쪽에서 cursor로 바뀌면 마지막 방문 순서대로 “확정 use case”를 되살리지 않는다. 불명 호출 후보로 남기면 된다.
- F11: `Enum` 클래스 본문에 `_missing_`가 없어도 파일 뒤에서 `Kind._missing_ = classmethod(...)`처럼 허용 동작을 붙일 수 있다. 계획의 “동적 멤버·rebind”가 이 클래스 속성 변경도 포함하도록 적고 후보 대조를 둔다. 닫힌 멤버형 `Enum/StrEnum/IntEnum` 이외를 자동 승인할 이유는 없다.
- F15: `application/.../port/exception.py`가 벤더 예외를 그대로 re-export한 경우, 소비자의 import 경로가 port라는 이유만으로 domain 값으로 면제하면 안 된다. 실제 로컬 계약 클래스 선언이면 domain, 명시 re-export가 표준 vendor로 이어지면 vendor, 체인을 못 해소하면 후보로 둔다. `except (DomainError, IntegrityError) as err`는 단일 vendor 확정도 domain 면제도 아닌 불명 후보에 해당한다.

이는 전역 데이터 흐름 엔진을 추가하라는 요구가 아니다. 이미 계획한 alias/rebind/출처 불명 계약의 fail-closed 경계를 작은 대조로 고정하라는 보완이다. 위 미래 구현 반례를 현재 구현에서 재현한 증거로 주장하지 않는다.

## m-C3 — F14 구간 표의 확정과 불명 우선순위를 한 문장으로 닫는다

Task 4 표는 표준 UoW 타입의 매개변수/필드를 사용한 순차 with를 별도 region으로 분류하면서, 함수 바깥에서 활성 UoW를 받을 가능성이 있으면 후보라고도 쓴다. 같은 주입 매개변수가 두 행에 걸칠 수 있다. 첫 행만 적용해 외부 transaction 부재를 증명했다고 보고하거나, 마지막 행을 모든 주입에 적용해 실제 순차 사례를 계속 후보로 남기는 양쪽 해석을 피해야 한다.

**보완:** 지원 범위에서 확인하는 것은 “현재 함수의 명시 lexical transaction region”이며 외부 활성 여부는 별도 사각이라는 식으로 관찰 수준을 고정한다. 현재 함수 안에서 확인한 outer atomic/decorator·중첩·다중 with-item 증거는 우선 결합한다. 호출자/ATOMIC_REQUESTS를 조사하지 않고 독립 실제 커밋을 증명했다고 쓰지 않는다. 명시 불명 경계를 후보로 남기는 계획은 유지한다. #546의 repository 타입 이름 계수도 실제 aggregate instance identity를 증명하는 것으로 표현하지 않는다.

## m-C4 — 새 exit/보고 계약은 helper 단언과 분리해 검증한다

Task 2는 실제 CLI를 명시해 적절하다. 같은 원칙이 Task 1에도 필요하다. `check_declarations()`에 #197/#202가 반환되는 것과, 실체화 0건 경로에서 최종 exit 2가 나오며 보고서 처분까지 연결되는 것은 다른 주장이다. 현행 `main()`은 실체화 0이면 2252~2266행에서 skip4/결손5로 반환한다. marker 문자열이 사본에 있다는 단언도 해당 update가 실제 #387 예보 경로에 들어갔다는 증거는 아니다.

**보완:** 최소 CLI fixture로 (1) update만 있고 실체화 0 + 선언 확정 → exit 2, (2) 선언 후보만 있음 → 기존 skip/결손 의미 유지, (3) marker update → 실제 단위 테스트 DB 진단의 의도한 생성/제거와 class/function DB 증거 보존, (4) 효과 hash 변경 → stale, (5) 선언 확정·S1 deferred 동시 → 남은 확정 때문에 exit 2를 검증한다. 정상 fixture의 `assertNotIn(rule, output)`만으로 검사 대상 도달을 증명하지 말고 반대 대조가 같은 CLI 경로에 도달하는 것을 함께 확인한다. 구현 테스트 수를 불필요하게 늘릴 필요는 없으며 기존 runner에 결합할 수 있다.

## 12건 전체 검토 결과

| 항목 | 계획 검토 결론 | 제거/보존 근거와 필요한 증거 |
|---|---|---|
| F4-1 | 방향 수용, m-C4 보완 | 선택 효과·module marker 후상태·동적/주소 범위 S5가 명시됐다. marker 텍스트와 helper 반환을 최종 CLI 증거로 과장하지 않는다. |
| F4-9 | **M-C1 반송**, m-C1 보완 | 실제 외부 admin 상속 및 UI metadata 흐름을 포함해야 한다. annotation별 실제/생성 근거를 분리하고 업무 소비를 보존한다. |
| F4-10 | 방향 수용, m-C2 대조 | builder+execute는 하나, 0·복수·cursor/불명은 후보. 미호출 nested 정의 제외와 별도 domain 예외 속성 #153 보존이 적절하다. |
| F4-11 | 방향 수용, m-C2 대조 | 닫힌 표준 Enum만 후보 제거. 커스텀 확장·Flag·동명/rebind 및 #264/#259 보존이 적절하다. |
| F4-12 | 수용 | 생성 after_commit 위치의 #376만 S1로 옮기고 실제 #376/#566을 유지한다. raw registry 실행 오류/자료 결손을 fail-closed하는 계약과 실제 CLI 검증이 포함됐다. |
| F4-13 | 수용 | 잡힌 IntegrityError의 known/unknown 내부 계약과 HTTP 500을 분리했다. 새 catch-all·schema 증설이 없고 선언된 계약 예외 재던짐도 보존한다. 산문 일치만으로 역할 수행을 검증했다고 주장하지 않는 조건도 적절하다. |
| F4-14 | 방향 수용, m-C3 보완 | 구간 합산·중첩/outer atomic 유지·불명 후보는 합의에 맞는다. lexical 관찰과 실제 커밋 증명은 구분한다. #550/#257 보존 대조가 있다. |
| F4-15 | 방향 수용, m-C2 대조 | domain=없음/vendor=확정/불명=후보와 RHS/chained 비교를 명시했다. 예외 tuple·re-export·branch join에서는 단순 import 주소가 정의 증거를 대체하지 않아야 한다. |
| F4-16 | 수용 | #642 자체 폐지와 50행 규범 제거이며 identity 수리로 바꾸지 않는다. #643·200행 신호와 다른 50 숫자 보존이 적절하다. |
| F4-17 | **M-C2 반송** | 내용 술어와 snapshot 전 원본 판정은 적절하다. 그 술어를 쓰는 직접 선택 인스턴스 열거 호출처가 불완전하다. |
| F4-18 | 방향 수용, m-C4 보완 | 명시 출처·보조 DTO/container/alias·update·실체화0를 포함하고 OHS import를 합성하지 않는다. 별칭 cycle/동명/미해소 후보를 보존한다. |
| F4-19 | 수용 | 초기/명시 재예보 정책과 12조합을 유지한다. 기준선/overlay 오류를 구분하고 coordinator 기록을 역할로 안내하며 docs 전체 금지는 하지 않는다. |

## 재검토 조건과 권한 판단

코디네이터는 검토 중 전달한 M-C1/M-C2를 수용하고 실제 상속·UI 흐름 및 domain/DTO/OHS 직접 열거를 계획에 명시하겠다고 답했다. **수용 의사와 수정 완료는 다르므로 이 보고서에서는 두 MAJOR를 아직 닫지 않는다.** 수정된 계획에서 해당 계약·Files·반대 대조가 연결됐는지 확인한 뒤 닫을 수 있다.

새 정책 선택은 0건이다. 두 MAJOR와 네 MINOR는 현재 합의 안에서 보수적으로 처리 가능하다. 실제 원 사례를 남기면서 F9 전체 완료를 선언하거나, 캐시 제외를 특정 검사기에만 좁히면서 F17 전체 완료를 선언하는 방식은 수용하지 않는다. 광범위 admin 면제·모든 폴더 무시·외부 프로젝트 수정으로 문제를 우회할 권한도 없다.

Serena/Graphify는 opt-in 부재 지시에 따라 검색·로드·호출·초기화하지 않았다. 추가 위임 없음.

## 계획 v2 한정 재검토 — 2026-09-11

재검토 대상 계획 SHA-256: `a3b0ebb2b309f901afc20d48adee8252e46b1f9cb7ab363c3503b64f82b317c8`. 최초 리뷰의 지적 6건과 그 수정이 만든 모순만 대조했다. 새로운 전체 리뷰·구현·테스트 실행은 하지 않았다.

| 지적 | 상태 | 수정 확인과 판정 |
|---|---|---|
| M-C1 · 실제 admin 원형 | **ADDRESSED** | Task 3은 확인한 Parler origin을 좁은 목록으로 인정하고 동명/rebind는 배제한다. context binding별 흐름 판정, form/inline/media의 별도 조립 허용, UI request metadata와 `extra_context or {}`/None 처리를 명시했다. 같은 값의 업무 소비는 현행 판정으로 남긴다. 실제 원형과 반대 대조도 Step 1에 연결됐다(159~169행). |
| M-C2 · cache-only 직접 소비 지점 | **ADDRESSED** | Task 5 Files에 domain-model/DTO/context-isolation이 추가됐고 `_aggregate_dirs/_check_layout`, usecase 열거·진입, `_check_ohs`의 선택 인스턴스 열거를 지정했다. snapshot도 같은 상대경로 선택 슬롯을 사용하며 전역 `_entries` 면제를 금지한다. 재현한 세 CLI 진단과 실소스 혼재·고정 골격의 보존을 direct/snapshot 양쪽 검증으로 명시했다(238~252행). |
| m-C1 · 생성 annotation S1 전달 | **ADDRESSED** | Task 2가 원본 records와 candidate_records를 전달하고 Task 3이 함수 def 행+producer의 정확한 슬롯 문구를 생성 AST에 일대일 결합한다. 다중 슬롯·동명 메서드·불명/비생성 혼재는 원진단 유지이며 원래 후보도 S1 report/check-report에 남긴다. bare Any 보존과 multiline CLI 대조가 있다(120~132,166~169행). |
| m-C2 · 실제 정의·변형 출처 | **ADDRESSED** | F10은 composition_root 주소 외에 표준 builder 심볼과 읽기 가능한 usecase 반환 선언/직접 생성 반환을 요구하며 branch join 상충은 불명으로 둔다. F11은 사후 클래스 속성 확장을 명시적으로 제외한다. F15는 실제 로컬 클래스 선언·명시 re-export·혼합 except·상충 binding을 구분한다(187,196,214~216행). |
| m-C3 · UoW 구간 관찰 수준 | **ADDRESSED** | F14 표의 불명 조건을 현재 함수에서 확인되는 경계로 고쳤다. 현재 함수의 명시 lexical region과 outer atomic/중첩/다중 item 우선순위를 고정하고, 주입 가능성만으로 모두 후보로 되돌리거나 실제 독립 commit을 증명했다고 표현하는 양쪽 해석을 배제했다(200~210행). |
| m-C4 · 실제 CLI exit·보고 대조 | **ADDRESSED** | Task 1은 실체화0+선언확정의 exit2/처분 누락 red, 후보만 있을 때 skip4/결손5, marker의 실제 #387 변화와 decorator DB 신호 보존, hash stale, 선언확정+S1 동시 exit2를 임시 git CLI 대조로 명시했다. helper 반환/문자열을 CLI 증거로 주장하지 않는 조건도 포함됐다(108행). |

**한정 재검토 잔여: BLOCKER 0, MAJOR 0, MINOR 0. NOT ADDRESSED 0. 추가 사용자 정책 결정 필요 0.** 지적을 처리한 문단 사이에서 새 반송 사유가 되는 모순은 확인하지 않았다. 최초 리뷰의 MAJOR 2와 MINOR 4는 계획 단계에서 닫는다.

이는 수정된 계획의 구현 진입을 허용하는 판정이다. 실제 Parler 원형의 진단 제거, cache-only 직접/snapshot 일치, S1 슬롯 결합 및 새 CLI 결과가 이미 구현·검증됐다는 뜻은 아니다. 해당 증거는 계획에 명시한 구현·검증 단계에서 확인해야 한다. 이 재검토에서는 본 파일에 이 절만 추가했고, 실제 사용 프로젝트 실행·Serena/Graphify·추가 위임은 없었다.
