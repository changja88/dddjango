# 잔여 12건 독립 문제 리뷰 C — 증거·일반화·진탐 보존

2026-09-11 · reviewer C · 기준 HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996` · 문제 검증 단계, 구현 없음.

## 판정과 증거의 범위

합의한 12개 방향을 폐기해야 할 반증은 찾지 못했다. 다만 원 보고서의 인과·발생조건 일부는 과장되어 있다. 특히 **UoW 구간의 독립성, DTO 소비가 OHS domain import를 강제한다는 인과, git 미추적과 캐시 잔재의 동일시, Phase 1 거절을 정책 모순으로 부르는 해석**은 수정되어야 한다. 이 네 보정은 이미 brief의 보존 경계와 일치하므로 새 사용자 정책 결정이 아니다.

증거는 다음처럼 구별했다.

- **R(보고)**: 원 보고서의 STOP 시각·횟수·당시 gate exit·레인별 비용은 보고자 진술이다. 당시 로그 전부와 STOP 직전 커밋을 재실행하지 않았으므로 독립 재현이라고 부르지 않는다.
- **S(정적 확인)**: 현재 checker, pre-gate, 규범의 실제 분기와 현재 사용 프로젝트의 제한된 파일을 읽었다. 사용 프로젝트의 현재 파일에는 이미 우회/교정된 코드가 있으므로 당시 코드와 동일하다고 전제하지 않았다.
- **P(합성 실행)**: 현재 checker/pre-gate의 순수 helper를 임시 트리에서 호출했다. Findings/Candidates는 `defer=True`이고 실제 사용 프로젝트에서는 검사기 CLI·테스트·코드를 실행하지 않았다. helper 결과는 전체 registry/pre-gate CLI의 exit 증명이 아니다.
- **I(추론)**: 정적 코드나 합성 실행으로부터 예상하는 적용 범위다. 원 실런의 빈도·시간 절감·회귀 부재를 증명하지 않는다.

재현 자료:

- `/private/tmp/dddjango-followup-C-evidence/probe.py`와 `results.json` — F1/F10/F11/F12/F14/F15/F16/F17/F18/F19 및 미러 대조.
- `/private/tmp/dddjango-followup-C-evidence/additional_probe.py`와 `additional-results.json` — 현재 admin 파일의 타입 후보, 읽은 실물 8파일 SHA-256, OHS import 필수설의 실행 반례.
- `/private/tmp/dddjango-followup-C-evidence/snapshot_probe.py`와 `snapshot-results.json` — cache-only 기능 폴더의 registry snapshot에서 빈 부모가 남는 경계 재현(exit 0).
- 실행: `python3 -B /private/tmp/dddjango-followup-C-evidence/probe.py`, `python3 -B /private/tmp/dddjango-followup-C-evidence/additional_probe.py`; 둘 다 exit 0. 인터프리터 Python 3.14.7. `-B`/`sys.dont_write_bytecode`로 원본 검사기 경로의 pycache 쓰기를 막았다.
- Claude/Codex manifest는 모두 2.18.2. 관련 checker 8종, `design_pregate.py`, `registry_gate.py`, `rulepack.json` 11파일은 현재 byte 동일이다(해시는 `results.json`). 설치 cache 전체·manifest 검증·전체 `make verify`를 실행한 것은 아니다.
- 원 보고서/brief와 개발 가이드를 읽었다. 정본·영구 테스트·사용자 코드·원 보고서·`docs/master.html`은 변경하지 않았다.

## F4-1 — 명시된 읽기 UoW와 기존 테스트 marker update

**판정: 설계 예보의 제한 지원과 명세 모순 검사 공백은 성립한다. 기존 구현 전체를 pre-gate가 시뮬레이션하지 않는 것은 명시된 S5이고, 이번 합의는 명시 재료만 추가로 검증하는 범위다.**

- **S/P:** `design_pregate.py:691` `_parse_signals`는 entry가 `add`가 아니면 `physical-signals 미반영(미등재 또는 비-add)`로 버린다. probe의 기존 unit test `update`에 `[markers: django_db]`, `[markers: ]`를 각각 넣어도 `signals=None`이었다. 무기재도 `None`이지만 미반영 note마저 없다. 현재 `Plan`에는 독립된 read-only/UoW 선언 채널이 없고 `symbols`는 함수·메서드·필드 선언을 보존한다. `materialize:1351`의 update는 제한된 새 OHS 함수 전사만 지원한다.
- **발생조건:** 새 UoW 인자나 DB marker가 산문/명시 표에 있어도 기존 파일 update이므로 전사되지 않는 경우다. `check-transaction-boundary.py:499`의 현행 #197은 함수 이름이 아니라 받은 UoW와 도달 쓰기 API를 본다. 따라서 `list_*` 이름만으로 읽기라고 판정해서는 안 된다.
- **의도적으로 없앨 공백:** 설계가 읽기 전용을 명시하면서 UoW를 선언한 모순의 G1 누락, 명시된 기존 unit test DB marker 추가의 누락.
- **계속 잡을 것:** 읽기+UoW 모순, unit DB 사용 #387, 기존 DB class/base/`.objects` 등 물리 신호. marker를 제거했다고 다른 DB 증거가 사라진 것으로 계산하지 않는다.
- **I/계획에 남길 제약:** update의 marker 어노테이션이 최종 집합인지 증분인지 현재 문법은 설명하지 않는다. 현재 add 채널의 “무기재=부재”를 update에 그대로 복사하면 기존 marker를 지우거나 유지할 의도를 훼손한다. **명시 최종 집합·명시 빈 집합·무기재 유지**의 세 경우를 구별하는 설계가 자연스럽지만, 이번 리뷰에서는 새 문법을 확정하지 않았다. 함수·클래스 수준 marker가 따로 있으면 전체 파일 marker 스냅숏을 곧 개별 marker 제거로 보지 않는다. 이는 계획의 입력 계약 명료화로 해결할 수 있고 추가 사용자 정책 결정은 현재 필요 없다.

## F4-9 — admin 타입·형식 규율

**판정: 현행 규범과 전달 context의 처분이 맞지 않는 규범 보완/완화 과제다. 단순 checker 오탐으로만 분류하면 합의한 admin 완화가 누락된다.**

- **S/P:** 현재 실물 `application/fortune_character/driven_layer/django_fortune_character/admin/character/panel.py`를 AST로만 읽어 `_check_explicit_any`에 넣었다. #647은 `changeform_view.extra_context`, `_render_failed_submission.extra_context`, `context` 지역 변수의 **후보 3건**, 위반 0이다. 별도 #645 `inlines` nested Any 후보도 1건 있다. 전체 감사/전체 annotation checker 결과가 아니다.
- **S:** `extra_context`의 값은 직접 꺼내지 않고 `super().changeform_view`와 `context.update`로 전달한다. 그러나 `context`는 단순 원형 전달만 하는 것이 아니라 자체 키를 채우고 `show_save` 등의 UI 값을 변경한다. “모든 dict는 우리가 만들지도 소비하지도 않는다”로 일반화할 수 없다. `discipline-houserules/SKILL.md:78–80`은 object의 자리와 내부 리터럴 TypedDict를 엄격하게 규정한다.
- **의도적으로 없앨 진단/의무:** 합의한 admin 화면 구성·Django 연동 자리에서 불필요한 타입/형식 교정이나 매번 동일 후보 처분을 강제하는 부분. 후보 3건만 닫는 한 줄과 실제 admin 완화 전체는 동일 범위가 아니므로 계획에서 대상 규칙을 열거해야 한다.
- **계속 잡을 것:** admin에서 읽어 업무 판단에 쓰는 입력의 검증, 업무 규칙과 변경 경계, 공통 업무 동작의 use case 경유. admin 폴더 안이라는 사실만으로 파일 전체를 면제하지 않는다.
- **R/I 한계:** STOP/리뷰어 간 불일치는 보고자 진술이다. 후보가 blocker가 아니므로 “검사기 자체가 G1/G2를 차단했다”는 표현은 부정확하다. 감수 처분 규범의 반송이 직접 원인이다. 현재 #645 후보 1건이 있다는 사실만으로 그 Any까지 자동 면제할 정책은 도출되지 않는다.

## F4-10 — builder와 실제 use case 실행의 혼산

**판정: 계수 결함이 성립한다. “표준 OHS 함수 모두 후보”는 반증되었다.**

- **S/P:** `check-context-isolation.py:443–452`는 함수 호출 표현식의 `ast.dump` 안에 `use_case`가 있는 수와 모든 `.execute` 호출 수의 최댓값을 사용한다. `use_case=build_book_use_case(); use_case.execute()`는 후보 “2회”, 같은 동작에서 변수만 `uc`이면 후보 0이다. `uc.execute()` 두 번은 후보 “2회”이고, `return build_book_use_case()`만 있어도 후보 0이다.
- **발생조건:** builder/receiver 이름에 `use_case` 토큰이 함께 들어가는 현재 휴리스틱에 좌우된다. 실제 실행 횟수 측정이라고 부를 수 없다.
- **의도적으로 없앨 진단:** 표준 composition builder의 준비 + 그 반환 use case 실행 1회의 #153 호출수 후보.
- **계속 잡을 것:** 실제 0회/복수 use case 실행 후보, 도메인 예외 속성 접근 등 같은 #153의 다른 확정 위반. 준비를 제외하느라 모든 `build_*`를 제외하거나 모든 `.execute`를 use case로 간주하면 기존 구멍이 남는다. 현재 builder-only 누락도 실행계수의 반례에 포함한다.
- **I 한계:** import 출처와 반환값 binding을 연결해야 한다는 방향은 정당하지만, 복합 분기·동적 factory·다른 객체의 `execute`는 확인되지 않은 호출로 남길 수 있다. 이 정밀화가 모든 함수의 실제 동적 실행 횟수를 증명할 것이라고 약속하지 않는다.

## F4-11 — 닫힌 Enum 자체 검증

**판정: 표준 닫힌 Enum의 반복 후보 제거는 성립한다. Enum 계열이라는 이름만으로 자동 면제하는 제안은 기각해야 한다.**

- **S/P:** `check-domain-model.py:450–486`은 상속 타입 출처를 보지 않고 `__init__/__post_init__`의 raise 유무만 보고 #268 후보를 낸다. 표준 `StrEnum`, `from enum import StrEnum as Closed`, `import enum as e; class Kind(e.StrEnum)` 모두 후보 1이고 정의 밖 값 생성은 `ValueError`였다. `_missing_`이 기존 멤버를 반환하는 변이는 같은 후보 1이지만 정의 밖 입력을 받아들였다. `StrEnum=object` 재정의도 후보 1이었다.
- **S:** 현재 실물 `BookKind`와 `FortuneFailureTicketOutcome`는 `from enum import StrEnum` 직접 상속, 상수 멤버뿐이며 `_missing_`·메타클래스 등 사용자 확장이 없다. 현장 두 타입에 대한 자동 판정 개선 근거는 강하다.
- **의도적으로 없앨 진단:** 출처가 표준 `Enum/StrEnum/IntEnum`으로 확인되고 멤버 조회 허용범위를 바꾸는 사용자 동작이 없는 닫힌 타입의 #268 후보. 별칭도 실제 출처가 같으면 포함한다.
- **계속 잡을 것:** `_missing_`, 사용자 상위 클래스/메타클래스의 변형, 재정의/바인딩 불명 등 자체 검증을 확정할 수 없는 타입의 검토 후보. 후보를 남기는 것은 그 Enum의 사용자 구현이 잘못됐다는 확정이 아니다. Flag/IntFlag의 조합 허용을 닫힌 Enum 근거로 묶지 않는다.
- **반증:** “정의된 멤버 밖 값은 항상 거절하므로 Q2는 항상 불가능”은 `_missing_` 반례로 거짓이다. 표준 Enum은 허용 멤버 집합을 제한할 뿐, 선언된 멤버가 해당 업무에서 적절한지까지 증명하지 않는다. Python은 `_missing_`과 EnumType 확장을 명시적으로 지원한다. [Python Enum 공식 문서](https://docs.python.org/3/library/enum.html)

## F4-12 — after_commit 생성 스텁과 #376

**판정: 생성 스텁을 실제 미구현으로 확정하는 교차 오탐이 성립한다.**

- **S/P:** `design_pregate.py:857`이 생성한 `after_commit` 스텁을 임시 driven UoW 파일에 넣어 현재 `_check_driven`으로 검사하면 #376 1건이다. 실물형 `callback()`만 있는 본문도 #376 1건, `transaction.on_commit(callback)`는 #566 1건, `robust=False` 명시형은 두 규칙 0이다.
- **발생조건:** pre-gate가 실제로 생성한 UoW 구현 파일에 `after_commit` 메서드 스텁이 있는 경우다. “새 UoW를 계획하는 모든 설계”는 입력 채널에 메서드가 있고 해당 driven 파일/selector에 도달한다는 조건이 빠져 있다. 기존 update 본문은 S5라 같은 원인이 자동으로 성립하지 않는다.
- **의도적으로 없앨 진단:** 생성 provenance가 있는 `after_commit` 스텁 본문만 근거로 하는 pre-gate #376 확정 위반. S1 미검증으로 보고해야 한다.
- **계속 잡을 것:** 실제 구현/기존 실코드의 on_commit 미사용 #376, 실제 on_commit의 robust 미기재 #566. 파일 전체나 #566 전체를 제외해서는 안 된다. `raise NotImplementedError`라는 텍스트만 보고 실물까지 생성 스텁으로 분류하면 안 된다.
- **R/I 한계:** 레인 4회의 STOP/시간 비용을 독립 집계하지 않았다. 현재 probe가 보인 것은 위 분기 하나다. 합성 on_commit 한 줄로 green을 만드는 것은 실제 본문 계약 검증의 증거가 되지 않으며 합의한 S1 미검증 방향이 더 정확하다.

## F4-13 — 잡은 IntegrityError와 raw 500 경계

**판정: 잡은 벤더 실패의 내부 정규화와 HTTP 공개 오류의 구별이 불명확한 규범 정합화 과제다.**

- **S:** `discipline-reviewer.md:94`는 안정된 public meaning이 승인될 때만 concrete 변환과 controller mapping을 묶어 설명한다. `check-port-adapter-pairing.py:986–1007`은 이미 계약에 선언된 예외의 재던짐은 허용하지만 그 밖의 adapter bare raise는 #555로 확정한다. 따라서 보고된 `except IntegrityError`에서 나머지 bare raise가 red가 되는 근거는 명확하다.
- **S:** 현재 사용자 repository 두 파일은 이미 알려진 UNIQUE를 구체 예외로, 나머지를 `InformationItemIntegrityViolation`/`RelationKindLabelIntegrityViolation`으로 번역한다. 당시 bare raise 버전은 재실행하지 않았다. 현재 실물은 보고된 교정 방향의 선례이지 당시 충돌의 실행 증거는 아니다.
- **의도적으로 없앨 충돌:** “HTTP public meaning이 없으니 이미 잡은 IntegrityError를 raw로 재던져야 한다”는 설계 안내. 승인된 일반 저장소 실패 계약으로 번역하되 공개 HTTP는 기존 500을 유지할 수 있어야 한다.
- **계속 잡을 것:** 이미 잡은 벤더 예외의 무정규화 재던짐, 선언되지 않은 임의 일반 예외로 교체, 벤더 code/SQLSTATE를 위층에서 판정, controller의 raw catch. 이미 정규화된 계약 예외를 관찰 후 재던지는 기존 합법 경로는 보존한다.
- **범위 반증:** “잡았으면 무엇이든 새 백스톱 하나”로 넓히면 안 된다. 합의는 이미 잡은 IntegrityError의 unknown 잔여다. 모든 Exception을 새로 잡거나 예외마다 HTTP schema를 늘릴 권한이 없다. 현재 검사기 #555는 일부 출처 불명 handler도 fail-closed하므로 그 전부가 실제 벤더 누수라는 일반화도 하지 않는다. repository의 계약 소유가 domain exception인 기존 규약을 무시하고 모두 capability port exception 파일로 옮길 근거도 없다.

## F4-14 — 함수 전체 합산과 실제 UoW 구간

**판정: #546의 함수 단위 대리 지표 오탐은 성립한다. 다만 보고자의 “서로 다른 with이므로 정상 독립 트랜잭션” 결론에는 구현·외부 경계 조건이 필요하다.**

- **S/P:** `check-domain-model.py:779–816`은 함수마다 `written=set()`을 만들고 `ast.walk(fn)`에서 타입명이 `*Repository`인 수신자의 `save/remove`를 모은다. probe에서 순차 같은 UoW 객체, 중첩 다른 UoW, 공통 outer UoW, with 없는 두 쓰기는 모두 같은 #546 1건이다. 반대로 같은 Repository 타입의 객체 두 개를 쓰는 경우는 0건이다. 현행 규칙은 실제 인스턴스 수나 모든 쓰기 종류를 완전 계수하지 않는다.
- **현재 실물:** `item_dictionary_unit_of_work.py`의 `__enter__`는 매번 `transaction.atomic()`을 생성하고 `__exit__`는 저장된 `_atomic_context`를 비운 뒤 종료한다. 같은 객체의 **순차 재사용**은 구간 분리의 근거가 된다. 같은 객체의 중첩 재진입은 단일 `_atomic_context` 슬롯을 덮어쓰므로 정상적인 독립 실행으로 확정할 수 없다. 이 사용 프로젝트를 고치거나 별도 결함으로 편입하지 않는다.
- **외부 경계:** Django의 내부 `atomic`은 바깥 atomic 아래에서 savepoint일 수 있다. 다른 UoW 변수여도 같은 외부 트랜잭션이면 하나의 커밋 단위다. [Django transaction 공식 문서](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) 현재 settings 파일에서 `ATOMIC_REQUESTS`/`transaction.atomic` 문자열은 발견하지 못했지만 호출자·동적 설정 전체와 당시 실행을 조사하지 않았으므로 “외부 경계 없음”의 증거는 아니다.
- **의도적으로 없앨 진단:** 독립 구간으로 확인된 순차 UoW 실행들에 쓰기 타입이 각각 하나인데 함수 전체 합산으로 내던 #546.
- **계속 잡을 것:** 하나의 확정 UoW 실행 구간에서 다른 애그리거트 타입을 바꾸는 것, 중첩·공유 구간을 별개로 잘라 없애려는 형태. 불명 구간은 이유 있는 후보/한계로 남겨야 하며 변수명이 다르다는 이유만으로 확정 green을 내면 안 된다.
- **R/I 한계:** 현재 `seed_items_use_case.py`는 이미 `_save_relation_kinds`/`_save_items`로 분리되어 당시 함수 본문은 아니다. 합성 probe는 checker의 잘못된 계수 단위를 증명하지만 당시 모든 호출에서 실제 commit이 분리됐음을 증명하지 않는다. 같은 타입의 여러 인스턴스·간접 호출·다른 save 명칭까지 이번 기회에 전면 분석하는 범위 확대도 피한다.

## F4-15 — code/errno/status_code 출처

**판정: 도메인 속성을 벤더 오류로 확정하는 오탐이 성립한다. except 바인딩 한정만으로는 해결되지 않는다.**

- **S/P:** `check-port-adapter-pairing.py:1165–1171`은 `Compare.left`가 해당 이름의 Attribute인지만 본다. probe에서 명시된 `Relation.code`, `VendorError.code`, 로컬 `DomainError.code`의 except 바인딩이 모두 #557 1건이다. 같은 벤더 비교를 `1 == error.code`로 뒤집으면 0건이다.
- **발생조건:** application_layer의 비교 왼쪽에 세 속성명이 있는 것이다. 이름·except 바인딩만으로 벤더 출처를 증명할 수 없다. 오른쪽·chained 비교까지 실제 비교 피연산자를 확인하는 것이 출처 판정과 함께 필요하다.
- **의도적으로 없앨 진단:** domain/command 등 확인된 업무 데이터 필드의 같은 이름 비교 #557 확정 위반. 현재 명시 출처 없는 값도 “벤더”로 단정하는 것은 후보로 내려야 한다.
- **계속 잡을 것:** 실제 벤더 오류/벤더 응답 출처가 확인된 code/errno/status_code의 위층 판정. domain exception이 except에 묶였다는 이유만으로 vendor로 처리하지 않는다.
- **R/I 한계:** 당시 레인의 쌍 분리 교정이 모든 동작을 보존했다는 것은 보고자 진술이다. 원 프로젝트의 업무 변경을 독립 검증하지 않았다. 역방향 비교 probe의 누락은 현행 속성명 휴리스틱의 한계이며, 이번 변경의 진탐 보호 예제로 적절하다.

## F4-16 — 50행 강제 하한 제거

**판정: 원 보고서의 identity 문제는 성립하지만 현재 합의의 본체는 규범 변경이다. #642 신규 판정 보정만 하면 요청 미완료다.**

- **S/P:** `check-layer-skeleton.py:95,147–149`의 하한은 50이고 메시지에 현재 행 수가 들어간다. `registry_gate.py:149`의 정규화는 위치 행 번호와 스냅숏 경로만 제거한다. probe의 동일 경로 “부품 24행”/“부품 21행”은 서로 다른 normalized identity다. 전체 앵커 gate를 재실행하지 않았지만 행 수 변경이 키를 바꾼다는 원인 추정은 확인되었다.
- **S:** `discipline-houserules/SKILL.md:42`와 해당 TTL은 승격 술어에 클러스터 개별 50행 이상을 둔다. 하한 삭제는 현행 규범을 고의로 바꾸는 일이므로 “현재 규범대로 진단하니 결함 아님”으로 종료할 수 없다.
- **의도적으로 없앨 진단/의무:** 승격 가능성 판단의 50행 강제 조건, 승격 부품의 신규/기존 불문 #642 출생 하한 자체. 기존 검출 집합 동일을 목표로 삼지 않는다.
- **계속 잡을 것:** 이동/승격/유지의 소관·응집 판단, 감사자의 주도, 참조/패치 표면 조사, 승격 본체·재수출·평면성·정크드로어·형제 중복 등 별도 형태 검사, 200행 감사 신호. 전체 저장소의 숫자 50을 일괄 삭제할 근거는 없다.
- **범위:** 메시지의 가변값이 다른 규칙 identity에도 영향을 주는 문제는 이번 합의와 별개다. #642를 폐지하면서 모든 registry identity를 일반 개편하면 범위가 확대된다.

## F4-17 — cache-only 기능 폴더

**판정: 작업 트리의 캐시 잔재를 선택적 기능 인스턴스로 오인하는 결함이 성립한다. `git ls-files 0`를 부재 조건으로 삼는 제안은 진탐 손실을 만든다.**

- **S/P:** 현재 `_entries`는 `__pycache__` 자체는 건너뛰지만 그 부모 기능 폴더는 `is_dir()`만으로 열거한다. 임시 `port/relation_table/__pycache__/old.pyc`만 있는 경우 같은 capability에 #488 2건 + #218 + #225가 발생했다. 미추적 실제 `draft.py`를 둔 경우에도 같은 필수 파일 진단과 #216이 발생했다. 후자는 유효한 검사 대상이다.
- **snapshot 경계 S/P:** `registry_gate.py:118–120`의 `_snapshot_current`는 `copytree(ignore=...__pycache__, *.pyc...)`를 사용한다. 별도 probe에서 원본 캐시는 그대로인 채 사본의 `relation_table/`만 빈 폴더로 남았다(`copied_parent_exists=true`, 자식 0). 따라서 checker에서 “캐시가 실제 남은 폴더”만 제외해도 G2 사본에는 그 증거가 없어 다시 오탐한다. **원 작업 트리에서 cache-only로 확인된 선택적 기능 폴더를 복사 시 제외하는 경계**도 계획에 포함해야 한다. 빈 폴더 일반 면제로 우회하지 말고, 정상 `__init__.py`·미추적 실물·고정 골격의 대조를 보존한다.
- **고정 골격 반례:** `port/unit_of_work/__pycache__`만 남은 경우 고정 폴더의 `__init__.py` 부재 #488은 유지해야 한다. “cache-only 폴더를 모든 위치에서 미존재 취급”하거나 부모까지 무조건 가지치기하면 고정 골격의 의무도 사라질 수 있다.
- **의도적으로 없앨 진단:** 실물 소스가 없고 캐시만 남은 **선택적 기능 인스턴스** 때문에 생긴 #488/#218/#225 등 파생 진단.
- **계속 잡을 것:** 새 미추적 소스가 있는 기능, 이미 선언된 필수 고정 골격, 캐시와 소스가 섞인 기능의 위반. Git 추적 여부와 실제 소스 존재는 별개다. 단순 `git ls-files 0` 또는 tracked-only snapshot은 신규 작업을 통째로 제외하므로 채택할 수 없다.
- **I/계획 제약:** 실제 소스 존재를 재귀적으로 확인하되 캐시 자식만 제외하는 좁은 규칙이 필요하다. 어떤 비-Python 실물이나 `__init__.py`가 기능 존재 근거인지 계획에서 닫아야 한다. 현재 합의의 캐시 제거 범위 밖인 임의 빈 폴더/모든 ignored 파일 제거까지 넓히지 않는다. 사용자 폴더 삭제는 해법이 아니다. 보고서의 레인별 8/10건 총수는 재현하지 않았다.

## F4-18 — result 타입 출처와 OHS import 추정

**판정: 명시 타입 재료에서 aggregate/entity 포함을 예보하지 못하는 공백은 성립한다. “result 투영에는 도메인 import가 필수”라는 보고자의 인과는 반증되었다.**

- **S/P:** `check-usecase-dto-placement.py:429–449`의 현재 #202는 DTO 필드 그래프가 아니라 import 경로를 본다. `outline: AnswerOutline`만 있으면 0건, aggregate import를 넣으면 1건, aggregate import만 있고 결과 필드는 `name: str`이어도 1건이다. private 보조 DTO의 aggregate 필드→`tuple[_Helper, ...]`는 import가 없으면 0건이다. 값 객체 import와 로컬 동명 DTO는 0건이다.
- **발생조건:** machine symbols가 보유 관계를 명시했지만 그 타입 출처가 import 전사에 드러나지 않는 경우, 또는 보조 DTO/별칭/컨테이너 간 연결이 필요한 경우다. 미래 주석을 가진 스텁은 정의되지 않은 필드 타입 이름이 있어도 compile되므로 import 결손만으로 현재 전사 실패가 되지 않는다.
- **의도적으로 없앨 공백:** 타입 출처가 aggregate/entity로 확인된 결과 DTO의 직접·보조 DTO·컨테이너 경유 포함 #202 누락. 명시된 OHS domain 의존의 #95/#96 누락도 실제 출처 규범에 따라 판정한다.
- **계속 잡을 것/보존할 정상:** aggregate/entity가 포함된 결과, 명시 금지 domain import는 계속 잡는다. 합법 값 객체, 같은 이름의 별도 DTO, 스코프가 다른 이름, 타입/모듈 별칭을 이름 매칭만으로 위반으로 바꾸지 않는다. 출처를 연결할 수 없으면 확인 불가/후보이지 확정 domain 타입이 아니다.
- **독립 반증 P:** scratch의 `dto.Result`는 domain aggregate tuple을 보유하지만 consumer `facade.py`는 `from dto import Result` 하나만 import하고 `tuple(outline.title for outline in result.outlines)`로 정상 투영했다(출력 `('title',)`). 이는 DTO의 #202 위반을 정당화하지 않지만, **DTO 위반이 OHS domain import 위반을 논리적으로 강제하지 않음**을 증명한다. Python 타입 출처를 알고 있는 것과 소비 파일이 그 타입을 직접 import해야 하는 것은 다르다.
- **범위:** “명시 의존은 확정, 추정은 후보”라는 합의가 정확하다. import를 합성해 #95/#96을 강제로 만들거나 별도 직접 domain 의존이 없는 모든 소비 OHS에 확정 위반을 붙이면 새 오탐이다. 소비 사실조차 추론만 가능한 때는 그 불확실성도 후보 이유에 명시해야 한다. 현장 G1=0/S3=6 전체 조합은 재실행하지 않았다.

## F4-19 — Phase 1 미추적 add/update 충돌

**판정: 양 태그 충돌 현상은 성립하지만 초기 검사/재발화 구분은 의도된 현행 정책이다. 안내 결함과 잘못된 작업 기록 file-plan 편입을 바로잡는 과제다.**

- **S/P:** 기준선에는 없고 사본에 있는 `docs/report.md`에 대해 `baseline_form_errors`는 add를 통과시키지만 `materialize`는 add 충돌을 낸다. update는 기준선 부재 오류다. 같은 add에 `explicit_base=True`로 `lift_realized_adds`를 거치면 스텁으로 실체화하며 already-built에 기록된다. 기준선에 있는 add도 “add 충돌(실존)”이라 작업 트리만 실존인 경우와 메시지가 동일하다.
- **S:** `design_pregate.py:1101`, `commands/dddjango.md:98`은 명시 `--base`를 재발화로 정의하고 기본 경로의 판정을 유지한다고 명시한다. `materialize` docstring의 “사본에 실존하는 add는 기준선 트리 실존뿐”은 명시-base 문맥에서만 참인데, 기본 실행에서는 거짓이라 혼동을 만든다.
- **의도적으로 없앨 안내:** 기준선 실존과 overlay 실존을 같은 모순으로 안내하는 문구, “update가 아니니 add”만 따라가면 다음 단계의 거절 이유가 불명확해지는 안내. lane REPORT처럼 작업 기록이 계획 대상에 잘못 편입된 경우 실제 소유권을 먼저 짚어야 한다.
- **계속 잡을 것:** 기본 Phase 1의 기실현 add 충돌, 기준선 없는 update 재라벨, 기준선에 있는 add, 부적절한 기준선 이동/Phase 2 G2 증거 세탁. 기본 Phase 1에서 `--base HEAD`를 자동 처방해 통과시키면 정책 변경이므로 이번 합의 밖이다.
- **범위 반증:** “어느 태그도 통과 못하니 무조건 판형 결함/정책 충돌”은 성립하지 않는다. 계획 선행과 초기 검사 정책상 의도된 거절일 수 있다. `docs/**`/비-Python 전체를 file-plan 금지로 만들 근거도 없다. 검토한 REPORT는 사용자 작업 기록이라는 역할로 제외되는 것이지 확장자로 제외되는 것이 아니다. 원 로그의 exit 3은 R이며 probe는 두 helper의 분기 결과다.

## B / M / m와 추가 사용자 결정

**현재 미해결 BLOCKER 0, 미해결 MAJOR 0.** 아래 문제 정의 보정은 이 리뷰에 반영했으며, 후속 계획이 brief와 함께 보존하면 다음 단계에 필요한 새로운 사용자 결정은 없다.

- **M 보정 4건:** F14의 `with=독립 트랜잭션` 확정 금지, F17의 `git ls-files 0=기능 부재` 금지, F18의 `DTO 소비=필수 domain import` 인과 기각, F19의 현상 재현과 정책 결함 구별. 이 네 오해를 계획에서 되살리면 MAJOR 반송 사유다.
- **m 보정 3건:** F10의 “모든 표준 OHS”는 receiver 이름 반례가 있고, F11의 “Enum이면 항상 폐쇄”는 사용자 동작 반례가 있으며, F12의 “모든 새 UoW”는 명시 after_commit 생성과 검사 대상 도달 조건이 필요하다. 모두 위 항목에서 발생조건을 좁혔다.
- **계획에서 확정할 통상 설계 사항:** F1 marker 최종 집합/빈 집합/무기재의 의미, F9 정확한 admin 완화 규칙 목록, F11/F15/F18 출처 해소의 지원 형태와 불명 후보 경계, F14 중첩·외부 구간의 불확실성 기록, F17 캐시만 있는 선택적 인스턴스의 좁은 정의. 합의한 경계를 보존하는 보수적 설계는 새 사용자 정책을 요구하지 않는다.
- **추가 사용자 결정이 꼭 필요한 사항: 현재 없음.** 광범위 admin 경로 면제, 기본 Phase 1 기실현 자동 허용, 모든 벤더 실패 catch/HTTP 계약 확대, 임의 폴더 삭제 같은 방향을 다시 선택하려 한다면 그때는 현재 합의 밖이므로 사용자 결정이 필요하다. 이번 리뷰는 이를 제안하지 않는다.

Serena/Graphify는 opt-in 표식이 없다는 지시에 따라 검색·로드·호출하지 않았다. 기본 읽기와 scratch의 좁은 프로브만 사용했다.
