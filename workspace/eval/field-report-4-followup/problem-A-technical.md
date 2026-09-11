# 현장 보고 4 잔여 12건 — 독립 문제 리뷰 A(기술)

2026-09-11. 검토 기준: `brief.md`의 사용자 결정 12건과 HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996`의 현재 검사기. 원 보고서 `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` 및 `docs/DEVELOPMENT.md`를 읽었다. 코드·규범·영구 테스트·원 보고서는 변경하지 않았다.

판정은 **문제 성립 여부와 향후 구현 제약**이다. BLOCKER는 0건이며, 아래 MAJOR 제약을 계획에서 닫기 전에는 구현 가능 판정으로 읽지 않는다. 현재 사용자 합의를 뒤집어야 할 기술적 사실은 발견하지 않았다. 세부 문법·정적 지원 범위를 계획에 명시하면 추가 사용자 정책 결정 없이 진행 가능한 범위다. 다만 불명확한 증거를 확정 위반으로 끌어올리거나 면제를 넓히는 선택은 기존 합의에서 나오지 않는다.

## 증거와 한계

- 독립 scratch: `/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/dddjango-f4-review-A-b3if_s3e/`.
- 재현 소스 `probe.py`, 결과 `results.json`, 검증 요약 `verification.txt`.
- Python 3.14.7, **67개 시나리오**, 진단 수 단언 33개와 의미 단언 4개 통과. 모든 Findings/Candidates는 `defer=True`, JSON sink도 scratch에 두었다. `sys.dont_write_bytecode=True`로 읽은 검사기나 사용 프로젝트에 캐시를 만들지 않았다.
- 이 증거는 현재 **함수 수준 직접 호출**이다. 전체 `registry_gate`/`design_pregate` CLI의 exit·차분·리포트 처분을 재실행한 증거가 아니다. 특히 F12의 G1 차단 왕복, F19 전체 CLI exit 3은 현장 보고와 코드 경로로 대조했으며 이 리뷰의 독립 CLI 실측으로 주장하지 않는다. 계획 검증에 전체 CLI 경로가 필요하다.
- 사용 프로젝트 `spring_dream_server`의 현재 `record_archive_service.py`, `book_kind.py`, `seed_items_use_case.py`를 읽었다. F10은 현재 실물 서비스에도 검사기를 직접 호출했다. F14/F15 현장 원형은 현재 private 쓰기 메서드/존재 여부 쌍으로 이미 정정되어 있으므로, **정정 전 실물 재실행**이 아닌 독립 최소 재현이다.
- Serena/Graphify: opt-in 표식 없음이라는 배정 조건에 따라 검색·로드·초기화·호출하지 않았다.

## 12건 판정

| 항목 | 분류와 판정 | 심각도 | 사용자 결정 필요 |
|---|---|---|---|
| F4-1 | 명시 설계 입력의 pre-gate 미전사/지원 범위 결손 성립. 기존 검사기 #197·#387의 진탐 자체와 구별 | MAJOR | 명시 효과·마커 문법과 불명 처리 경계를 계획에 고정하면 추가 결정 불필요 |
| F4-9 | 현행 규범대로 나온 후보지만 admin 적용 규범 변경 필요성 성립. 단순 검사기 버그만으로 분류 불가 | MAJOR | 정확한 완화 목록을 제시해야 함. 전 경로 면제는 미승인 |
| F4-10 | 이름 의존 호출 합산 오탐 성립. 표준 builder+실행을 2회로 셈 | MINOR | 추가 결정 불필요 |
| F4-11 | 닫힌 표준 Enum의 불필요 후보 성립. 후보 자동 판정 개선 | MINOR | 추가 결정 불필요. 동작 확장 Enum까지 면제하면 범위 밖 |
| F4-12 | 생성 스텁에 대한 #376 본문 판정 오탐 성립 | MAJOR | 추가 결정 불필요. S1 미검증 처리만 허용 |
| F4-13 | 이미 잡은 오류의 내부 정규화 계약과 외부 500 경계 설명 부족 성립. #555 제거 사유는 아님 | MAJOR | 승인된 일반 실패 계약을 유지하면 추가 결정 불필요 |
| F4-14 | 함수 전체 저장소 타입 합산 오탐 성립. 단순 with 분리는 불충분 | MAJOR | 지원 가능한 구간·불명 후보를 명시하면 추가 결정 불필요 |
| F4-15 | 속성명만으로 벤더 오류 확정하는 오탐 성립. 비교 방향에 따른 기존 미탐도 확인 | MAJOR | 출처 불명은 후보라는 합의로 처리 가능 |
| F4-16 | 기존 #642 차분 문제 성립. 현재 작업은 50행 강제 자체 제거라는 규범 변경 | MAJOR | 추가 결정 불필요. #642 identity 보정으로 대체 불가 |
| F4-17 | 캐시 잔재를 기능 인스턴스로 세는 오탐 성립 | MAJOR | 추가 결정 불필요. 미추적 소스 제외는 미승인 |
| F4-18 | 필드 타입과 출처 연결의 설계 예보 결손 성립. OHS 소비→domain import 필연 주장은 불성립 | MAJOR | 명시 출처 확정/동명 불명 후보를 구분하면 추가 결정 불필요 |
| F4-19 | 초기 add 거부 자체는 합의된 비결함. 원인·다음 조치·file-plan 소유 안내 개선 성립 | MINOR | 기본 판형 자동 기실현 허용은 미승인 |

## 항목별 기술 근거와 구현 제약

### F4-1 — 효과 선언과 테스트 마커

`design_pregate.py::_parse_symbols`(524행 이후)는 add일 때만 클래스와 메서드를 `entry.symbols`에 적재한다. update는 새 모듈 함수만 적재하며 클래스 이름은 `declared` 자기 해소 자료에 남을 뿐이다. `_parse_signals`(693행 이후)는 **비-add를 만나면 Signals를 만들기도 전에 버린다**. `materialize`(1293행 이후)의 update는 `_render_service_update`만 호출한다. 따라서 보고서의 update 사각은 단순 렌더 실패보다 앞선 **입력 보존 결손**이다.

독립 재현 `F1_update`: 명세에 `ListUseCase.__init__(uow: OrdersUnitOfWork)`와 기존 `test/unit/test_list.py::test_list [markers: django_db]`를 적어도 클래스 심볼 `[]`, signals `None`, materialized `[]`, #387 `0`. 채널 메모/S5에는 미반영 이유가 남는다. 별도 #197 대조는 같은 `execute` 이름에서 UoW+read 본문이면 1, UoW+save이면 0이다. 함수 이름을 read 판정에 쓰지 않는다는 합의를 유지해야 한다.

계획 필수 제약:

- optional 명시 효과 채널(`path::Class`와 read-only/write 등)은 가능한 해법이다. **명시 read-only와 명시 UoW 의존의 모순**만 판정하고, 무기재를 read-only로 추론하지 않는다. 현재 본문 또는 메서드 이름만으로 효과를 채우지 않는다.
- UoW 출처는 표준 포트 import·명세의 정확한 선언으로 확인한다. 이름 suffix만 같은 외부 클래스·alias·재정의는 불명 처리한다. update 클래스/메서드 재료를 이 검증에 보존하되 기존 메서드 본문을 팬텀 코드로 갈아치우는 부작용을 만들지 않는다.
- 기존 `[markers: a,b]`는 add에서 파일 수준 `pytestmark` 전체 목록으로 렌더된다. add 파서 대조: 무기재는 `None`, `[markers: ]`는 빈 목록, `+django_db`·`-django_db`는 현재 **증감 연산이 아닌 이름 문자열**이다. 이를 현재 지원 문법처럼 설명하면 잘못이다.
- update의 유지/제거/추가를 명시적으로 정의한다. 무기재 유지와 명시 빈 목록을 구별하고, 동적 pytestmark·기존 함수/클래스 decorator의 범위가 파일 수준 목록과 같다고 간주하지 않는다. `.py::case`는 현재 **파일 주소 해소**이지 case 단위 마커 전사 계약이 아니다.
- `block_hash`, 보고서 사각/S5·스킵 판정·`--check-report` 최신성에 새 명시 채널을 포함한다. class 정보만 파싱하고 해시에서 빠지면 예전 보고서를 그대로 승인할 수 있다.

대상: `design_pregate.py::PlanEntry/Signals/_parse_symbols/_parse_signals/materialize/block_hash/BLIND_SPOTS`, `check-transaction-boundary.py::_check_execute_body`, `check-test-config.py::_check_bc_test`. 후자의 본문 검사는 독립 진탐 대조로 보존한다.

### F4-9 — admin 완화의 범위를 먼저 닫아야 함

`check-public-surface-annotation.py::_check_explicit_any`(715행 이후)는 `dict[..., object]`의 매개변수/지역 변수면 #647 후보, 반환/클래스 속성이면 위반을 낸다. 소비 여부는 보지 않는다. `F9_passthrough`는 전달 전용 매개변수+context 지역 변수에 후보 2개, `F9_consumed`는 가격을 읽고 저장하는 업무 입력에도 후보 1개다. **동일 후보 형태가 면제할 정상형과 보존할 위험형에 함께 쓰인다.**

규범 정본 `ontology/rules/discipline-houserules-skill.ttl`과 현재 `discipline-houserules/SKILL.md` §4는 object 즉시 좁힘·고정 레코드 TypedDict·generic Django base를 강제한다. 따라서 현행 규범 준수형 후보라는 이유로 사용자 결정의 규범 변경 필요성을 폐기하면 안 된다.

계획은 #493(첫 바인딩), #645(Any), #646(admin/form generic base), #647(object/레코드), #650(JSON 소비) 중 **각각 무엇을 어떤 admin 화면/연동 자리에서 완화하는지** 열거해야 한다. 원 보고서의 pass-through만 고치면 현재 사용자 결정의 더 넓은 admin 타입·형식 완화가 완결됐다고 할 수 없고, 다섯 규칙을 admin 폴더에서 전부 끄면 합의 경계를 넘는다. 사용자 입력 소비·업무 판정·데이터 변경은 기존 경계로 남겨야 한다. 함수 이름/경로만으로 데이터 사용이 없다고 단정하지 않는다.

대상: 위 정본, `check-public-surface-annotation.py::_scan_class/_check_signature/_check_explicit_any/_check_stub_generic_bases/_check_json_load`, 관련 architect/discipline-reviewer 기준·pre-gate 정형 base. 이 리뷰는 전체 admin 실물 타입체커 실행을 하지 않았다. 정확한 완화 표의 타당성은 계획 적대 리뷰에서 검토해야 한다.

### F4-10 — 준비와 실제 실행의 바인딩

`check-context-isolation.py::_check_ohs_service` 443–452행은 `ast.dump(call.func)`에 `use_case` 문자열이 있으면 세고, 임의 `.execute` 개수와 max를 취한다. `F10_standard`와 inline builder는 후보 1개(2회), receiver를 `use_case`→`uc`로 바꾸거나 builder import를 `make`로 별칭하면 후보 0이다. 실제 두 `.execute`는 후보 1로 남는다. 별도 `cursor.execute()` 한 번도 후보 0이므로 현재 `.execute`는 출처를 증명하지 못한다.

현재 사용 프로젝트 `record_archive_service.py` 직접 재현은 공개 함수 6곳 모두 “유스케이스 호출 2회” 후보를 냈다. 최초 보고의 함수만 유일 사례가 아니다.

표준 `composition_root` import에서 builder 출처를 해소하고 반환 객체의 실행을 세어야 한다. 모든 `build_*`를 빼거나 모든 `.execute`를 use case로 확정해서는 안 된다. alias·module attribute·inline `build().execute()`·receiver 재대입을 대조한다. 실제 복수 실행/실행 0의 후보는 보존하며, 조건 분기 경로의 최대 실행 횟수까지 증명하지 못하는 경우는 후보의 정적 한계로 적는다. 함수 안 호출되지 않은 nested 정의를 실행으로 세지 않는 범위도 계획에 고정한다.

대상: `check-context-isolation.py::_check_ohs_service`의 호출 계수 부분과 import binding 해소. 같은 함수의 도메인 예외 속성 접근 **확정 #153**은 별도 진단이므로 변경하지 않는다.

### F4-11 — 실제 표준 닫힌 Enum만

`check-domain-model.py::_check_value_object_file` 450–486행은 생성자 raise만 보므로 표준 StrEnum·별칭·module alias가 모두 #268 후보다. `_missing_`가 임의 입력을 허용하는 변형도 동일 후보이며, 동명 로컬 `StrEnum`과 `IntFlag`도 검사 대상이다. 현재 실물 `BookKind`는 `from enum import StrEnum`에 멤버 두 개뿐인 표준형이다.

표준 모듈의 Enum/StrEnum/IntEnum 출처를 확인한 닫힌 형상만 자체 검증으로 인정한다. `_missing_`, 사용자 기저/메타클래스·재정의·동적 alias 등 허용 집합이 불명인 형상은 검토를 유지한다. 특히 Enum suffix 또는 `Flag/IntFlag`까지 일반화해서는 안 된다. 기존 타입 검사기의 이름 기반 선언형 면제 helper는 자체 문서상 로컬 동명·receiver 무검사 사각이 있으므로 그대로 가져오는 것으로 출처 검증이 완료되지 않는다.

대상: `check-domain-model.py::_check_value_object_file`; enum import 별칭/재정의의 보수적 해소. 값 객체의 다른 #264/#259 판정을 함께 면제하지 않는다.

### F4-12 — 스텁 생성 provenance가 필요

`design_pregate.py::_class_stub` 857행 이후의 after_commit은 `raise NotImplementedError`다. `check-port-adapter-pairing.py::_check_driven` 726–758행의 본문 검사는 이 스텁에 #376을 낸다. `F12_generated`와 **실제 잘못된 구현** `F12_real_bad`는 동일 #376=1, 실제 `on_commit`에 robust가 빠지면 #566=1, robust 명시 정상형은 둘 다 0이다.

따라서 `raise NotImplementedError`라는 AST 형태·파일 이름·pre-gate 실행 환경만으로 #376을 없애면 실제 미구현 코드의 진탐이 사라진다. **이번 pre-gate가 실제로 합성한 파일/메서드 provenance**를 명시적으로 연결해 그 after_commit 본문에 대해서만 S1 미검증으로 기록해야 한다. `materialized`에는 remove/empty/다른 전사도 들어가므로 그것만으로 본문 생성 여부를 단정하지 않는다. 동일 파일에 기존 실코드와 새 선언이 섞이는 경우에도 파일 전체 면제보다 좁아야 한다.

전체 #376/#566 스텁 면제와 정형 `on_commit` 합성으로 green을 만드는 방안은 현재 합의에서 벗어난다. S1 미검증은 검증 성공/적용 불가가 아니다. 게이트 귀속·리포트·`--check-report`에 미검증 근거가 남고, 실제 G2와 기존 코드 본문 검사는 계속 발화해야 한다. 현재 `_stable_id`는 rule+path여서 메서드 둘의 신원을 구별하지 못한다는 한계도 필터 설계에 고려한다.

대상: `design_pregate.py::_class_stub/materialize/run_gate/write_report/BLIND_SPOTS`, `check-port-adapter-pairing.py::_check_driven`. 전체 registry CLI에서 stub/existing real/robust 누락의 차등 대조를 계획 검증에 넣는다.

### F4-13 — 내부 예외를 곧 공개 HTTP 오류로 만들지 않기

`check-port-adapter-pairing.py::_check_adapter_families` 986행 이후는 handler의 bare raise를 #555로 검사한다. `_handler_declared_error`는 이미 계약에 선언된 실패 재던짐을 인정한다. `F13_bare_vendor`=1, 승인 포트 실패로 정규화=0, 원래 잡지 않은 호출=0, 선언된 포트 실패 재던짐=0을 재현했다.

`ontology/rules/agent-discipline-reviewer.ttl`의 raw infrastructure 문면(현재 `agents/discipline-reviewer.md:94`)은 안정된 public meaning 승인 때만 정규화한다고 읽힐 수 있다. 새 문면은 **잡힌 IntegrityError의 내부 포트 계약 정규화**와 **안정된 외부 오류의 controller mapping**을 분리해야 한다. 알려진 제약은 구체 실패, 나머지는 승인된 일반 저장소 실패 1로 번역하고, 그 일반 실패를 controller가 새 concrete HTTP schema로 잡지 않아야 기존 500이 유지된다.

모든 Exception 포획·오류 코드 recognizer 확장·오류별 schema 증설은 불필요하다. `_handler_declared_error`가 인정하는 계약 오류 재던짐을 “모든 bare raise 금지” 산문으로 뒤집어서도 안 된다. 일반 실패 계약의 **선언 위치·예외 타입 이름은 설계가 제공할 재료**이고 검사기가 발명할 값이 아니다.

대상: `ontology/rules/agent-discipline-reviewer.ttl`의 raw/ACL 전수성 관련 표현, architecture DDD/DB 및 설계 체크 기준의 관련 번역 문면. #555의 실제 판정 변경 필요성은 이번 재현에서 발견하지 않았다.

### F4-14 — 함수 경계도 임의 with 경계도 트랜잭션이 아님

`check-domain-model.py::_repo_bindings`(711행)는 `*Repository` 타입 주석 이름을 snake로 변환한다. 실제 repository import 출처를 확인한다는 진단 문면과 달리 **import를 해소하지 않는다**. `_check_application_side`(723행 이후)는 `ast.walk(fn)`의 save/remove 수신자 타입을 함수별 `written`에 합친다.

독립 재현: 순차 `with uow` 두 구간=위반 1(오탐), 단일 with의 두 타입=1(보존 진탐), 중첩 공유 alias=1(단순 분리 시 잃을 진탐), 서로 다른 lock 블록=1(UoW 분리 증거 아님). **호출되지 않은 nested 함수의 두 번째 저장도 함수 전체에 합산되어 #546=1**이다. 반대로 `uow.first_repository.save`+`uow.second_repository.save`는 현재 0이라, 이번 수리 전부터 receiver 추적 사각이 있다.

필수 제약은 독립된 표준 UoW 실행 구간마다 변경 타입을 세는 것이다. 같은 변수명의 순차 context는 다른 구간일 수 있고, 다른 이름의 중첩/alias는 같은 트랜잭션일 수 있다. 외부 활성 UoW를 이어받는 helper, factory·with-as, `with uow1, uow2`, 공유 저장소, 분기·루프를 계획의 지원/불명 표에 둔다. `with`마다 카운터를 초기화하는 수정은 부적합하다. 불명 경계는 확정 위반으로 과장하지 말고 후보/지원 한계로 드러낸다.

별칭 타입 두 개가 같은 aggregate repository인지도 이름 집합만으로는 알 수 없다. 구간 개선을 빌미로 무제한 전역 데이터흐름 분석까지 구현할 필요는 없지만, 현행 이름 기반 계수의 한계를 “타입 출처 증명”으로 잘못 표기하지 않아야 한다. #550/#257이 같은 순회에 있으므로 #546 구간 변경 중 진단이 소실되지 않게 대조한다.

대상: `check-domain-model.py::_repo_bindings/_check_application_side`; 기존 `check-transaction-boundary.py`의 UoW/저장소 binding 지원은 재사용 가능성을 검토할 자료이며 그대로 의미 동일하다고 간주하지 않는다.

### F4-15 — 출처 확인과 비교식 전체

`check-port-adapter-pairing.py::_check_use_side` 1165–1171행은 Compare 왼쪽 Attribute의 code/errno/status_code만 검사한다. 재현은 domain field=확정 1, vendor Error=확정 1, **domain exception handler**=확정 1, unknown payload=확정 1이다. vendor 속성을 오른쪽에 놓거나 `400 <= err.status_code < 500`으로 쓰면 둘 다 0이다.

예외 handler 바인딩 자체는 vendor 출처 증명이 아니다. domain exception도 같은 구문이다. annotation·정확한 import origin·assignment·alias/rebind를 구분하고, 벤더→확정/도메인→없음/불명→후보를 닫는다. 비교 좌항만 유지하면 같은 오류의 문법적 변형이 계속 사라지므로 모든 비교 피연산자의 해당 속성을 검토하고 중복 후보를 억제해야 한다. “application 아닌 모듈”을 모두 벤더로 분류하지 않는다.

대상: `check-port-adapter-pairing.py::_check_use_side`, 필요한 보수적 출처 해소. import 없는 외부 전달·복합 helper 반환의 출처를 증명하지 못하면 후보다. 실제 표준 벤더 타입 목록/해소 범위는 계획에서 명시해야 한다.

### F4-16 — 삭제할 규범과 남길 규범

`check-layer-skeleton.py::_check_promoted`의 `PROMO_PART_MIN_LINES=50` 및 #642 발행이 존재한다. `registry_gate.py::_normalize`는 줄번호만 정규화하며 메시지 안 “부품 21행/25행”은 남긴다. `F16_normalization`에서 동일 경로 진단의 두 key가 다르다는 점을 직접 확인했다. 전체 앵커 차분 CLI 재현은 하지 않았다.

그러나 사용자 결정은 그 key를 고치는 것이 아니라 **승격 판단의 개별 50행 조건과 부품 출생 50행 하한 제거**다. `ontology/rules/discipline-houserules-skill.ttl`의 캐스케이드 개별 50행 조건과 `discipline-houserules-final.ttl`의 출생 하한, `_check_promoted`의 #642 발행을 함께 정합화해야 한다. 유지할 것은 소관·응집에 따른 이동/승격/유지, 감사 주도, 모듈/문자열 참조처 조사, 본체·재수출·평평함·부품 0개 등의 형태 검사 및 200행 감사 신호다.

규칙 ID를 다른 신규 여부 판정으로 재해석하지 않는다. 모든 50 문자열을 일괄 삭제하지 않는다. 예컨대 adapter 고정 역할 파일의 “50행 하한 대상 아님”은 새 정본에 맞게 문면 정리가 필요할 수 있으나 다른 수치 규율을 지우는 근거가 아니다.

대상: 위 TTL 두 파일, `check-layer-skeleton.py::PROMO_PART_MIN_LINES/_check_promoted`, rulepack/미러/해당 fixture 기대값. 이번 범위의 필수 구현에 `registry_gate::_normalize` 변경은 필요하지 않다.

### F4-17 — 캐시 제외는 작업 트리 실존 판정

`check-layer-skeleton.py::_entries`는 `__pycache__` 자신은 제외하지만 그 부모 `ghost/`는 디렉터리로 돌려준다. `_check_level`은 이를 capability 인스턴스로 재귀하며 고정 파일 두 개를 요구한다. `check-port-adapter-pairing.py::_check_port_tree`도 직계 `__pycache__`만 제외하여 parent capability에 #218/#225를 낸다.

표준 good_bc 임시 사본 대조에서 `ghost/__pycache__/removed.pyc`와 `ghost/obsolete/__pycache__/removed.pyc`는 각각 #488 2개+#218 1개+#225 1개였다. `ghost.py` 실제 소스와 빈 `__init__.py` 소스도 같은 네 진단을 내며, 이 둘은 제외하면 안 된다. 완전히 빈 폴더도 현재 네 진단이다. 고정 `application_layer/port/__init__.py`를 없애고 캐시만 남긴 대조는 #488 1개여서 보존할 고정 골격 검사를 확인했다.

Git 추적 목록만으로 대상을 정하면 신규 미추적 소스가 사라진다. **실제 작업 트리에서 캐시 흔적만 있는 동적 기능 인스턴스**를 제외하고, 고정 부모/골격의 의무를 똑같이 지우지 않는다. 캐시를 품은 조상에 실제 source가 있는 경우, 읽기 오류·symlink·빈 폴더를 어떤 분기로 둘지 계획에서 보수적으로 고정한다. 캐시 없는 빈 폴더의 자동 제외까지 이번 결정으로 넓힐 필요는 없다. 자동 삭제는 하지 않는다.

대상: `check-layer-skeleton.py::_entries/_check_level`의 동적 인스턴스 선택, `check-port-adapter-pairing.py::_check_port_tree/_check_capability_folder` 및 같은 삭제 대상 adapter 열거. 공통 술어를 두면 `checker_target.py`가 후보 위치다. **전역 모든 디렉터리 열거를 일괄 필터링하는 구현은 고정 골격 진탐 손실 위험**이 있다.

### F4-18 — 필드 의미와 Python binding을 연결

`check-usecase-dto-placement.py::_check_dto_file`(429행 이후)는 실제 DTO 필드의 포함 그래프가 아니라 절대 import 경로를 검사한다. `_import_records`는 상대 import도 다루지 않는다. `design_pregate.py::render_stub`는 `outlines: tuple[AnswerOutline, ...]`를 그대로 전사하지만 이름을 선언 타입 출처와 잇지 않는다.

재현은 bare AnswerOutline 필드+import 없음→#202 0, 명시 aggregate import→1, 동명 VO import→0, 보조 `_OutlineData`의 aggregate 필드를 결과에서 컨테이너로 감쌈→0이다. 이는 **명시 aggregate import는 이미 잡고, bare/보조 타입 출처 연결이 사각**임을 보여준다. 모든 #202가 빠지는 문제로 확대해서 설명하지 않는다.

설계의 정확한 module/type 식별자와 imports·aliases·필드 edges를 연결하고 `Result/Out`에서 보조 DTO·컨테이너를 통해 도달하는 aggregate/entity를 탐색한다. 실제 import 또는 정확한 qualified annotation이 있으면 확정 근거가 된다. **다른 파일 어딘가 같은 이름의 aggregate 선언이 있다는 것만으로는 이 파일의 Python binding을 증명하지 못한다.** same-BC 유일 catalog 이름도 추정 후보+출처 명시 요구로 두는 안이 안전하다. 동명 VO/외부 타입, `Literal["AnswerOutline"]`, 문자열 전방 참조, alias cycle, TYPE_CHECKING import를 대조한다.

OHS에서 `result.outlines`를 읽거나 다른 DTO로 바꾸는 것은 domain 클래스 이름 import 없이도 가능하다. 따라서 원 보고서의 “result를 투영하려면 domain import가 필요하다” 파생은 일반적으로 성립하지 않는다. **직접 의존이 명시된 OHS만 #95/#96 확정**, 소비만 확인된 경우는 별도 후보·설계 확인이다. 결함 #202를 알리려고 불필요한 domain import를 스텁에 합성해서 #95/#96까지 만들어서는 안 된다.

대상: `design_pregate.py::_parse_symbols/_parse_imports/PlanEntry/parse_spec` 및 명세 타입 그래프 예보 채널, `check-usecase-dto-placement.py::_check_dto_file`와 `check-context-isolation.py::_scan_imports`, `check-event-publish.py`는 실제 import 진탐 대조. 새 사각 축소에 맞춰 S2/S3/S5 문면을 실제 지원 범위만큼만 갱신한다.

### F4-19 — 거부 정책 보존, 잘못된 처방 제거

`baseline_form_errors`(1953행)는 기준선 기준 태그를 판정하고, `lift_realized_adds`(1101행)는 explicit_base일 때만 오버레이 add/empty를 걷어낸다. `materialize`(1293행)는 남아 있는 실존 add를 거부한다. 12조합 함수 대조에서 기준선 부재+오버레이 실존은 기본 add/empty 거부, 명시 재검사 add/empty만 기실현 스텁으로 전환, 기준선 실존 add/empty는 두 모드 모두 거부, 기준선 부재 update는 두 모드 모두 거부했다. 합의된 초기/명시 재검사 정책과 일치한다.

결함은 `materialize` 문서가 “사본의 add 실존은 기준선 실존뿐”이라고 단정하는 점, 기본/명시 모드가 같은 `(--base HEAD)` 헤더로 보이는 점, update 오류의 “add다” 안내만 따라도 기본 add에서 다시 충돌하는 점이다. **기준선 실존 충돌과 오버레이 실존 충돌을 분리해 원인과 실행 모드를 정확히 안내**해야 한다. `--base HEAD`를 초기 금지 위반 우회 명령처럼 무조건 권하지 않는다.

별도 작업 기록인 REPORT의 file-plan 편입은 artifact 소유 문제다. 문서 전체 `docs/**`를 허용/금지하는 정책으로 일반화하지 않는다. scratch 대조에서 docs add가 명시 모드로 들어가면 현재 Python 스텁 텍스트로 실체화되었다는 사실도 기록한다. 이는 보편 문서 실체화 지원의 증거가 아니다.

대상: `design_pregate.py::baseline_form_errors/lift_realized_adds/materialize/write_report/write_report_stub/main`의 모드·오류 전달 및 architect의 file-plan 소유 안내. 기본 판형의 exit/귀속/ID 의미는 유지한다.

## 계획 입장 조건

MAJOR를 해결할 최소 계획은 (1) F1 효과와 마커의 명시 문법·해시·불명 처리, (2) F9의 규칙별 admin 완화 표, (3) F12의 생성 메서드 provenance와 G2 진탐 보존, (4) F13 내부 계약/외부 500 분리, (5) F14 구간/alias/불명 표, (6) F15 출처 3분류와 비교식 전체, (7) F16 규범의 50행 조건 제거 목록, (8) F17 동적 캐시 인스턴스만 제외하는 술어, (9) F18 명시 타입 binding과 보조 DTO 추이 연결을 각각 구체화해야 한다.

검증 목표는 전후 진단 집합 완전 동일이 아니다. 표준 builder·닫힌 Enum·생성 스텁·독립 UoW·도메인 code·캐시 잔재·50행 하한의 제거 예정 진단과, 실제 복수 실행·사용자 정의 Enum·실제 누락 on_commit/robust·공유 트랜잭션·벤더 code·미추적 소스·필수 골격·명시 aggregate 결과 필드의 보존 진단을 구분한다. 이 구분이 없는 “전체 green”은 완료 근거가 아니다.

정본 수정은 `docs/DEVELOPMENT.md`에 따라 TTL→render→rulepack→미러를 따르고, 검사기는 Claude 원본과 Codex byte 미러를 함께 반영해야 한다. 이번 리뷰에서는 그 수정·소성·make verify를 수행하지 않았다.
