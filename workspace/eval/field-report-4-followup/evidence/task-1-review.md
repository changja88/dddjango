# Task1 독립 구현 리뷰

- 대상: HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996` 대비 Task1 미커밋 diff. 검토한 3파일의 현재 SHA-256은 review package와 일치한다. 두 배포본 SHA-256도 동일하다.
- **Spec compliance: FAIL — Task1 자체 marker 계약의 필수 수정 M 2건.**
- **Task quality: CHANGES REQUIRED — B 0 / M 2 / m 0.**
- Task2/Task6 의존사항을 이 실패의 근거로 삼지 않았다. 코드·테스트·계획·원보고서·Git 상태는 수정하지 않았다.

## M1 — 기존 pytest import가 있는 파일에 새 marker를 그 import보다 먼저 삽입한다

- 위치: `dddjango/scripts/design_pregate.py:1427`, `:1444–1451` 및 동일 Codex 미러.
- 발생 조건: update 파일에 `import pytest`는 있고 module `pytestmark`는 없으며, `[markers: slow]` 같은 비어 있지 않은 최종 목록을 선언한다. 정상적으로 지원해야 하는 «module pytestmark가 없으면 목록 추가» 입력이다.
- 원인: `import_needed`는 파일 전체의 바인딩만 보고 False가 되지만, 목록 삽입 위치는 docstring/future 뒤이므로 기존 일반 import보다 앞이다.
- scratch focused probe의 실제 결과:

```python
# 원본
import pytest
def test_case(): pass

# 생성 결과
pytestmark = [pytest.mark.slow]
import pytest
def test_case(): pass
```

`compile()`은 통과하고 실행은 첫 줄에서 `NameError: name 'pytest' is not defined`가 난다. AST 검사기가 목록을 읽어 #387 등을 판정할 수 있는 것과 유효한 Python module 후상태를 만드는 것은 별개다.

- 최소 보완: 새 목록이 참조하는 pytest binding이 삽입 위치에서 이미 존재하도록 import/list 배치 순서를 보장한다. 기존 import·본문 bytes 보존 요구도 유지한다.
- 검증 조건: 위 입력 및 future import가 있는 동형 입력에서 새 목록의 실제 평가 성공·정확한 marker 값·기존 함수 본문/source 보존을 단언한다. pytest 설치에 의존하지 않는 최소 fake module로 scratch 생성 결과만 평가해도 된다.
- 현재 테스트가 놓친 이유: `workspace/tools/pregate_field_report_smoke.py:334–335`는 «pytest import와 기존 목록이 둘 다 있음» / «둘 다 없음»만 비교한다. `:345`의 compile은 이름 바인딩 순서를 실행하지 않는다.

## M2 — module marker의 후속 subscript 대입을 정적 단일 대입으로 오인한다

- 위치: `dddjango/scripts/design_pregate.py:1397–1415`, `:1432–1435` 및 동일 Codex 미러.
- 발생 조건: module에 아래와 같은 동적 marker 변경이 있고 `[markers:]`로 비운다.

```python
import pytest
pytestmark = [pytest.mark.slow]
pytestmark[0] = pytest.mark.django_db
```

- 원인: `visit()`는 `Name('pytestmark', Store/Del)`만 추가한다. subscript 대입에서 pytestmark 이름은 Load이고 Subscript가 Store이므로 후속 변경을 놓친다. 따라서 첫 Assign만 `pytestmark = []`로 바꾸고 `pytestmark[0] = ...`는 그대로 둔다.
- scratch focused probe: fake pytest module을 넣은 원본은 정상 실행되어 최종 `['django_db']`였다. 생성 결과는 compile을 통과한 뒤 `IndexError: list assignment index out of range`로 실패했다. 비어 있지 않은 다른 목록으로 치환해도 후속 대입이 최종 선언을 다시 바꿀 수 있다.
- 요구 영향: 동적 계산/증분/조건부 대입은 덮지 않고 S5로 남기라는 Task1 계약과 «파일 수준 최종 목록» 의미를 충족하지 않는다.
- 최소 보완: module pytestmark를 대상으로 하는 subscript Store/Del 등 명시적인 후속 mutation이 있으면 원본을 그대로 두고 S5로 남긴다. 동적 후상태를 실행·추론하는 지원 확장은 필요하지 않다.
- 검증 조건: 위 입력에 대해 원본 bytes 그대로, materialized 미계수, 구체적 S5 사유를 단언한다. 직접 대입·AugAssign 검사만으로 mutation 전부를 검증했다고 주장하지 않는다.
- 현재 테스트가 놓친 이유: smoke `:346–349`는 Name 대상 중복/조건부/AugAssign을 다루지만 Subscript 대상 Store가 없다.

## Named concern — 생성 execute(uow)의 source #197

**판정: 현재 Task1의 추가 필수 수정으로 삼지 않는다. 지원 밖 생성 public 입력의 잔여 source 판정 경계로 남긴다.** 새 source checker 필터를 Task1에 요구할 근거는 확인하지 못했다.

직접 읽은 `task-1-source-197-probe.log`에서는 `write uow=BookUnitOfWork`가 선언 checker `[]`를 내며, 생성자 주입은 transaction checker clean이고 `execute(self, uow: BookUnitOfWork)`는 source #197을 낸다. source `check-transaction-boundary.py:449–504`를 좁혀 확인한 결과 public 메서드의 직접 UoW 파라미터와 스텁의 쓰기 호출 부재를 결합한 기존 경로다. 효과 선언이 write임에도 스텁만으로 읽기 의미를 확정할 수 없다는 concern 자체는 타당하다.

다만 #635 정본인 `workspace/design/2026-08-08-tree-revision-spec.md:1164`는 execute의 입력을 자기 Command/Query 계약 객체 하나로 정한다. 직접 UoW 입력은 그 표준 계약에 맞지 않는다. `check-usecase-dto-placement.py:392–399`는 인자 수만 검사하므로 해당 probe가 그 checker에서 검출되지 않는다고 표준 적합성이 증명되는 것도 아니다.

F4-1의 승인 경계(`workspace/eval/field-report-4-followup/brief.md:16`)는 명시 read-only/UoW 모순 검증과 기존 marker update이며, 원 보고서 `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md:25–30`도 기존 update S5 결손을 소유한다. Task1 brief는 생성자/필드 주입의 명시 출처 대조를 정하고 기존 본문 전체 검증을 요구하지 않는다. 이 문맥에서 «#197 확정의 모든 경로는 read-only 선행»은 새 선언 판정의 모든 분기를 제한하며, 실제 기존 source checker를 효과 무기재라는 이유로 전역 면제하라는 계약으로 확대하지 않는다. 검토한 새 선언 코드에는 write를 #197 확정으로 내는 경로가 없다.

⚠️ 후속 생성 provenance/S1 검토에서 이 사례를 확인한다면, 실제 source #197 보존·생성 근거의 정확한 범위·표준 생성자+자기 Command/Query execute 대조를 함께 증명해야 한다. 이를 Task2의 이미 승인된 필수 기능이나 이미 해결된 사례로 판정하지 않는다.

## 명시 후속 의존

- ⚠️ Task2: 선언확정과 S1 deferred가 함께 있는 실제 CLI에서 exit 2, 선언 확정 처분 의무, S1의 비차단 분리가 유지되는지 통합 검증해야 한다. Task1 단독 green 주장에 사용할 증거가 아니다.
- ⚠️ Task6: 선택형 효과 채널·hash·S5 후상태 범위의 TTL/역할/프롬프트 의미 동기화와 해당 게이트를 확인해야 한다. 이번 Python 3파일 범위를 넘어선다.

## 직접 확인한 증거와 한계

입력 brief(첫 읽기, Global Constraints 포함), 구현 report, 10행 context 전체 diff package를 읽었다. 최초 결합 출력이 잘려 원본 diff 구간을 나눠 확인했으며, 미러 중복 본문은 동일 diff와 현재 SHA-256으로 대조했다. parser/declarations/hash/DTO 출처/보고·exit/marker 변경과 새 smoke의 실제 호출·단언을 diff에서 검토했다. 같은 rule/path owner 근거 합치기와 후보/확정 별도 보고, 실체화 0 분기 앞 선언 검사, 기존 본문을 덮지 않는 자료 구조는 diff로 확인했다. 기존 tests 전체를 재실행하지 않았고, 구현 보고의 24개 green 및 전체 fixture 통과를 독립 재실행 사실로 표시하지 않는다.

추가 파일 읽기는 named concern의 #635/F4-1 정본 좌표와 기존 source #197 소유 분기, marker 함수 및 smoke의 정확한 행 번호 확인으로 한정했다. 새 실행은 위 marker 의문에 대한 임시 디렉터리 scratch probe와 현재 3파일 SHA 확인뿐이다. 두 scratch 재현은 사용자 프로젝트를 import하거나 실행하지 않았다. 이 리뷰는 Task1 단독 범위이며 전체 코드베이스·전체 후속계획 감사를 대신하지 않는다.

Serena/Graphify: opt-in 없음이라는 전달된 조건에 따라 검색·로드·초기화·호출하지 않았다.

## Fix round 1 재리뷰 — M1/M2 종결

**Spec compliance: PASS (Task1 단독 범위). Task quality: APPROVED. M1 ADDRESSED / M2 ADDRESSED. 잔여 B 0 / M 0 / m 0.** 최초 FAIL / CHANGES REQUIRED 판정은 이 라운드의 수정·검증에 따라 위와 같이 갱신한다.

- **M1 ADDRESSED:** `dddjango/scripts/design_pregate.py:1437`은 새 module 목록을 삽입할 때 기존 파일의 pytest import 여부와 관계없이 그 위치에 필요한 import를 함께 넣는다. 기존 import와 함수 본문은 이동·삭제하지 않고, 새 목록 평가 전에 binding을 만든다. 기존 import 한 줄이 중복될 수 있으나 기존 bytes 보존과 삽입 위치의 실행 순서를 만족하는 작은 수정이다. `workspace/tools/pregate_field_report_smoke.py:533`의 신규 테스트는 일반 입력과 docstring/future 입력을 fake pytest로 실제 평가하여 `['slow']`, 기존 함수 반환값, 기존 코드 구간 및 source bytes 보존, materialized 계수를 단언한다. 최초 문제를 놓쳤던 compile 단독 검증을 넘어선다.
- **M2 ADDRESSED:** `dddjango/scripts/design_pregate.py:1398–1416`은 module pytestmark를 root로 하는 Subscript Store/Del을 수집하고, statement 치환 전에 명시 사유로 보류한다. 기본 Name Store 검사와 기존 class/function 비재귀 경계는 유지한다. `workspace/tools/pregate_field_report_smoke.py:554`는 대입·삭제·slice·AugAssign·조건부 대입 각각에 빈 목록/비어 있지 않은 목록을 요청하여 사본·source bytes 불변, materialized 0, 구체적 S5를 확인한다. 대표 원본이 실제로 정상 평가되어 `['django_db']`가 되는 대조도 있다.

현재 라운드의 n10 diff package와 구현 report의 Fix round 1 append를 읽었으며, 두 production 미러의 변경은 동일하고 marker 함수 외 동작을 추가하지 않는다. 이 작은 변경에서 새로 명명할 수 있는 결함을 발견하지 않았다. 검사 범위를 다시 넓히거나 source #197 판단을 재개하지 않았다.

직접 읽은 실행 증거는 `task-1-fix-round1-focused-green.log`의 **2 tests / OK**, `task-1-fix-round1-green.log`의 **26 tests / OK**(기존 실제 CLI 대조 포함), `task-1-fix-round1-compile-mirror.log`의 **변경 Python 3파일 compile OK / byte mirror OK**다. fake pytest 평가의 내용은 위 테스트 diff의 실제 exec·단언과 focused/full 로그의 해당 테스트 성공을 함께 대조했다. 새 probe나 suite 재실행은 하지 않았으며, 구현자가 기록한 실행을 리뷰어의 재실행으로 표시하지 않는다.

Task2의 선언확정+S1 통합 검증과 Task6 규범·프롬프트 동기화는 앞서 기록한 명시 의존 조건으로 남는다. 이 PASS는 그 후속 작업의 완료 판정이 아니다. 재리뷰에서 작성한 파일은 이 리뷰 append뿐이며 production·테스트·Git 상태는 변경하지 않았다. Serena/Graphify는 opt-in 부재로 사용하지 않았다.
