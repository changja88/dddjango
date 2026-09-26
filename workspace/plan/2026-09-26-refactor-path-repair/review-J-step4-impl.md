# 구현 리뷰 J — 로드맵 4 동작 보존 장치(최소판) (2026-09-27)

## 판정: **수정 후 진행** — blocker 1 · major 7 · minor 13

한 줄 결론: 파일 단위 순수 이동(재생 기준 5커밋)과 계약 변경 red(7커밋)는 주장대로 재현된다. 그러나 **디렉터리·패키지 단위 이동은 여전히 거짓 red 다(B-1 재발)**. 설계 v4 §1 이 «0C 에서 된다»고 한 #429 `charging_test/` 이관을 SDS 사본에서 재생하니 거짓 red 가 40건 나왔다. 반대 방향으로는 거짓 green 경로가 넷 있다. ① 이름 문자열 치환이 관찰 가능한 이름 변경을 통과시킨다. ② 테스트를 수집 밖으로 옮겨도 green 이다. ③ 머지로 판정을 세탁할 수 있다. ④ `remove` 행 해석이 넓다.

- 대상: `dddjango/scripts/behavior_guard.py`(853행) · 러너 `workspace/tools/behavior_guard_fixture_run.py` · 규범 diff(Coordinator·coder·DR·Codex 3곳).
- 대조 문서: 설계 `step4-behavior-guard-design-v4.md`, 앞 검토 `review-G3-step4-v3.md`, 결정 8·9(`evening-report.md` §5).
- 실측 환경(전부 스크래치 `…/scratchpad/review-J/` 아래)
  - 반례 하네스는 `harness.py` 다. 러너의 `BASE`·`_repo`·`_guard` 를 빌려 쓴다.
  - 반례 스크립트는 `cases_fg.py`(거짓 green) · `cases_fr.py`·`cases_rn.py`(거짓 red) · `cases_fail.py`(실패 경로) · `cases_dyn.py`(동적 마이그레이션 — 스크래치 venv `djv` 의 Django 6.1, uv 캐시에서 오프라인 설치)다.
  - 출력은 `fg.out`·`fr.out`·`rn.out`·`fail.out`·`fail2.out`·`dyn.out`·`replay-*.out`·`rp-<commit>.out` 에 남겼다.
- 현장 재생은 `bg-replay/replay.sh`(사본 `bg-replay/sds` — alternates 는 scratch `bt/sds-main`)로 했다. **원본 `~/Desktop/spring_dream_server` 는 건드리지 않았다.** 사본 작업 트리는 재생마다 `checkout -f`·`clean` 으로 정리했다(`git status` 비어 있음 확인).
- 코드·규범 파일은 고치지 않았다. Serena·Graphify 는 이 워크트리에 opt-in 표식이 없어 쓰지 않았다. `make verify` 는 돌리지 않았다(러너만 단독 실행).

---

## Blocker

### J-B1. 0C 대응표·정규형이 디렉터리·패키지 단위 이동을 설명하지 못한다 — 설계가 약속한 #429 이관이 거짓 red 40건 (B-1 재발)

- **위치**
  - `behavior_guard.py:352-361`: 모듈 쌍은 «import 뺀 AST 동일»일 때만 맺어지고, `__init__.py` 는 제외된다.
  - `:393-401`: 후속 모듈 대응은 `mm`/`fm` 에만 들어가고 `pairs` 에는 들어가지 않는다. 그래서 분류 중립이 성립하지 않는다.
  - `:670-674`: 비 `.py` 쌍은 내용이 똑같을 때만 맺어진다.
  - `:692-702`: 쌍이 없는 테스트 쪽 삭제·추가는 red 다. 빈 파일 «추가»만 판정 밖이고 «삭제»는 red 라서 비대칭이다.
  - `:451-480`·`:498-502`: 모듈 바인딩의 속성 접근은 이름 대응(rn)만 풀고, 정의 이동(dm)은 풀지 않는다.
- **재현 1 — 현장(#429 모양)**: SDS 사본 `12d876dcc` 에서 0C 창을 연다. `git mv spring_dream_server/charging_test tests/charging_test` 를 하고, 폴더 안 `spring_dream_server.charging_test` 를 `tests.charging_test` 로, 파일 경로 문자열도 함께 치환한 뒤 close 를 돌렸다.
  ```
  요약: 창 w1 close red 40건 · 종류 0C · 바뀐 경로 98 · 치환 green 0 · 대응(모듈 43 · 정의 230 · 개명 0) …
    red: tests/charging_test/test/test_a01_counter_non_fortune.py — 치환으로 설명되지 않는 변경: import 바인딩 −[('attr','spring_dream_server.charging_test.common.gate','live_e2e',…)] +[('attr','tests.charging_test.common.gate',…)]   (×31 + conftest)
    red: spring_dream_server/charging_test/test/__init__.py — 테스트 파일 삭제(이동 쌍 없음)
    red: tests/charging_test/{,common/,test/,util/}__init__.py · common/gate.py · run.py — 테스트 파일 추가
    red: tests/charging_test/README.md — 테스트 디렉터리의 비 .py 오라클 변경
  ```
  - `common/gate.py` 는 docstring·오류 메시지에 자기 경로가 있어서, 옮기며 고치면 «import 뺀 AST» 가 달라지고 쌍이 깨진다. 그래서 `gate.py` 를 import 하는 테스트 32파일이 전부 red 다.
  - 문자열·docstring 을 낡은 채 두고 import 줄만 고쳐도 red 5건이 남는다. 5건 모두 `__init__.py` 쌍 제외 때문이다(`요약: … red 5건 · 치환 green 32`).
- **재현 2 — 합성**(`cases_fr.py`·`cases_rn.py`)

  | 사례 | 결과 | 원인 |
  |---|---|---|
  | FR1 BC 패키지 통째 이동(`app/bc/` → `app/pricing/`, `test/`·`test/unit/` 빈 `__init__`) | red 2 «테스트 파일 삭제(이동 쌍 없음)» | `__init__.py` 쌍 제외 · 빈 파일 삭제 비대칭 |
  | FR1b 위 + 같은 내용 `.gitkeep` 두 벌 이동 | red 6 | 비 `.py` 쌍이 유일 동일 내용만 |
  | FR2 부분 이동(`calc.add` → `arith.add`) + 테스트가 `from app.core import calc; calc.add` | red | 모듈 바인딩 속성 접근을 dm 으로 못 푼다 |
  | FR4 재수출 `__init__` 패키지 이동, 테스트 `from app.wallet import Coin` | red | 패키지 수준 대응 없음 |
  | FR5 `import app.core.money` 뒤 `app.core.money.Money` | red | 전체 경로 속성 사슬 미치환 |
  | FR11 `import toolz; toolz.slug` 개명 | red | alias 없는 `import` 는 `alias_attr` 대상 밖 |
  | RN1 결정 7 모양 `money_out.py`/`MoneyOut` → `money_in.py`/`MoneyIn`, 테스트 `from app.core.port import money_out` | red | 개명에서 모듈 대응이 생기지 않는다(후속 모듈은 dm 만 센다) · 로컬 이름도 바뀐다 |
  | RN2 포트 파일 개명 → 페이크 파일 개명(#577 페이크 = 포트 이름) | red 4 | 페이크 클래스 본문이 개명된 이름을 참조해서 «이름 뺀 AST» 가 다르다(연쇄 개명) |

- **SDS 노출(실측, `12d876dcc`)**
  - 테스트 쪽 `__init__.py` 142개(빈 파일 136).
  - 테스트 쪽 비 `.py` 가운데 같은 내용이 여러 벌인 묶음 8개(18파일).
  - 모듈 바인딩 뒤 속성 접근을 쓰는 테스트 98파일(1,160회).
  - import 가 있는 제품 `__init__.py` 77개.
  - SDS 는 테스트를 BC 안 `test/` 에 두므로, BC 배치 수리(#325·#329~#332 류)와 BC 개명은 모두 FR1 모양이다.
- **영향**
  - 설계 v4 §1 의 수락 예시(#429 두 건 · #575)와 G3 M-4·M-5 가 «된다»고 한 모양(분류 중립 이동 · #577 개명)이 장치 오탐 → `ⓐ 재상정(플러그인 결함)` 으로 빠진다.
  - 캠페인에서 디렉터리 단위 정리는 구조적으로 STOP 이다. G3 B-1 과 같은 등급이다.
  - 재생 5커밋이 green 인 것은 그 커밋들이 파일 단위 이동이었기 때문이다.
- **권고(최소)**
  1. 모듈 쌍 판정은 «옛 판에 지금까지의 대응표를 적용한 뒤 import·docstring 을 뺀 AST 동일»로 한다. 대응표가 더 늘지 않을 때까지 되풀이한다(자기 경로 문자열·연쇄 개명 흡수). 후속 모듈 대응도 `pairs` 에 등록한다.
  2. 디렉터리 대응을 둔다. 한 디렉터리의 쌍 과반이 가리키는 새 디렉터리가 있으면, `__init__.py`·비 `.py` 파일은 (디렉터리 대응, 파일 이름)으로 짝짓는다. 짝지은 파일은 옛 판에 치환을 적용해 비교한다(`.py` 는 정규형, 비 `.py` 는 `_sub_string`). 빈 파일 삭제는 추가와 대칭으로 판정 밖에 둔다.
  3. 정규형은 이름 참조를 대상의 전체 경로로 풀어서 비교한다. 대상은 from-import 로 묶인 이름, 모듈 바인딩의 속성, `import a.b` 사슬이다. 이렇게 하면 로컬 이름 차이(RN1)와 모듈 속성 접근(FR2·FR5·FR11)이 함께 흡수된다. 패키지 재수출(FR4)은 `__init__` 의 `from X import Y` 를 한 단계 따라가면 된다.
  4. 러너에 #429 재생(또는 같은 모양의 합성)과 FR1·FR2·FR4·RN1·RN2 를 음성 사례로 넣는다.

---

## Major

### J-M1. 이름 대응이 관찰 가능한 이름 변경을 green 으로 통과시킨다(결정 9 조건 위반) — 반대로 무관한 문자열에서는 거짓 red

- **위치**
  - `behavior_guard.py:414-417`·`:441`: `bare` 는 개명된 옛 이름과 **정확히 같은 모든 문자열**을 새 이름으로 바꾼다. 파일·모듈과 무관하게 적용된다. 설계 v4 §2.3 에 없는 확장이다.
  - `:305`: 이름을 뺀 해시가 `'{name}'` 을 dump 에서 모두 비운다. 그래서 자기 이름과 같은 **문자열 상수**도 지워진다.
- **재현**(`cases_fg.py` · 추가 실행)
  - FG1: `class InsufficientFunds(Exception): code = "InsufficientFunds"` → `NotEnoughFunds` 로 바꾸고, 테스트 단언도 `== "NotEnoughFunds"` 로 바꿨다. 결과는 `close green · 개명 1`.
  - FG1b: `__str__` 이 `"Gold"` 를 돌려주는 클래스를 `Platinum` 으로 개명하고 단언을 고쳤다. 결과는 green.
  - FG1c: 클래스 본문에 문자열이 없고 `handle()` 이 `type(exc).__name__` 을 돌려준다. 개명하고 단언을 고쳤다. 결과는 green.
  - FR3: `create` → `create_order` 로 개명했다. 같은 테스트의 무관한 `{"action": "create"}` 가 옛 판에서 `"create_order"` 로 치환된다. 결과는 red «본문 문장 1 이 다르다».
- **영향**
  - 클래스·함수 이름이 선 위 계약이나 기록값이면 테스트 기대값이 이름을 따라 바뀌어도 «치환»으로 통과한다. 해당하는 경우는 오류 코드, `__name__` 기록, `__str__` 이다.
  - SDS 에 실재한다. `application/llm_access/driven_layer/adapter/external_system/openai/generation_adapter.py:399` 등이 `provider_exception_type=type(error).__name__` 을 기록한다.
  - 결정 9 는 «정의 본문이 이름 말고 같을 때만»이다. 이 경우 본문은 같아도 **동작이 바뀐다**. 치환 없이 테스트를 그대로 두면 런타임에서 잡힌다.
- **권고**
  - `bare` 를 없앤다. `patch.object(<개명 정의가 있는 모듈 바인딩>, "옛이름")` 의 둘째 인자처럼 위치가 특정되는 곳에서만 치환한다.
  - 이름을 뺀 해시는 `FunctionDef/ClassDef.name` 과 `Name`/`Attribute` 자기 참조만 비운다. `Constant` 는 그대로 둔다.
  - 러너에 FG1c(red 기대)와 FR3(green 기대)를 넣는다.

### J-M2. 0C 에서 테스트 파일을 수집 밖으로 옮기면 green — 테스트가 조용히 사라진다

- **위치**: `behavior_guard.py:698-712` 는 이동 쌍이면 옛 판과 새 판을 비교만 한다. 0C 에는 케이스·수집 검사가 없다(`:679-714`).
- **재현**
  - FG2: `app/test/test_money.py` → `app/test/money_cases.py`(`python_files` 에 안 맞음) 로 옮겼다. 결과는 `close green · 치환 green 1`.
  - FG2b: `app/test/test_money.py` → `app/core/money_checks.py`(제품 자리) 로 옮겼다. 결과는 green.
- **영향**: 0C 의 약속 «테스트 고정 — 테스트 추가·삭제 red»를 이동으로 우회할 수 있다. 수집 대상 케이스가 줄어도 장치와 테스트 실행이 둘 다 green 이다.
- **권고**: 이동 쌍의 새 자리가 수집 패턴(pytest 설정 `python_files`, 기본값 `test_*.py`·`*_test.py`)과 `testpaths` 를 유지하는지 확인한다. 더 단순한 대안은 0C 에서도 «수집 가능한 파일의» 케이스 다중집합 동일을 요구하는 것이다.

### J-M3. 창 안 머지 처리 — 자기 머지로 세탁되고, 제외가 불완전해 거짓 red 가 나며, rebase 는 탐지하지 못한다

- **위치**
  - `behavior_guard.py:619-627`: first-parent 머지이면 `M^1..M` 전부를 «머지가 들여온 경로»로 본다. 출처는 확인하지 않는다.
  - `:661`: 경로 제외는 `changed` 에만 적용된다.
  - `:713`(pytest 설정)·`:720-731`(케이스 다중집합): 머지 제외가 적용되지 않는다.
- **재현**
  - FG3(거짓 green): 레인이 곁가지 `side` 에서 단언을 `== 3 or True` 로 약화하고 `merge --no-ff side` 했다. 결과는 `close green · 바뀐 경로 0 · 머지 제외 1경로`.
  - FG3b(거짓 green): `merge --no-commit up` 뒤 테스트 약화를 끼워 커밋했다(evil merge). 결과는 green, `머지 제외 2경로`.
  - FR8(거짓 red): 0T 창 안에서 main 머지가 `test_upstream` 을 들여왔다. 결과는 red «테스트 케이스 추가 `test_upstream`»이고, exit 2(red)라서 exit 1(판정 불가)이 아니다.
  - FR9(거짓 red): 0C 창 안에서 main 머지가 `addopts` 를 추가했다. 결과는 red «pytest 설정 변경».
  - FR10(거짓 red): 창 안에서 `git rebase up` 을 했다. 결과는 red «tests/test_up.py — 테스트 파일 추가». main 의 변경이 레인 편집으로 판정된다.
- **영향**: (가)는 테스트 고정 전체를 우회하는 경로다. 레인이 곁가지와 머지를 쓰는 습관만 있어도 성립한다. (나)·(다)는 긴 캠페인 창에서 나는 거짓 STOP 이다. G 의 실측에서 승인 머지가 있는 실행은 15/79 다.
- **권고(각 수 행)**
  - `M^2` 가 open HEAD 의 후손이면(레인 곁가지) 제외하지 않는다.
  - `M` 이 두 부모 **모두와** 다른 경로(충돌 해소·끼운 편집)는 레인 편집으로 본다.
  - 케이스 다중집합과 pytest 설정 비교에서도 머지 경로의 기여를 뺀다.
  - `git merge-base --is-ancestor <open HEAD> HEAD` 가 거짓이면 exit 1 «창 기준 커밋이 조상이 아님(rebase·reset)»으로 한다.

### J-M4. pytest 설정 ⓐ 는 어느 창에서도 고칠 수 없다 — 규범과 스크립트가 모순

- **위치**
  - 규범: `dddjango/commands/dddjango.md:113`(Codex `SKILL.md` 같은 문장)은 «ⓐ 항목의 경로가 테스트 쪽(… · **pytest 설정 절**)이면 0T»라고 한다.
  - 스크립트 0T: `behavior_guard.py:716-719` 는 `_is_test`(`:126-132`)가 경로로만 가르기 때문에 `pyproject.toml`·`pytest.ini` 를 제품 쪽 변경 red 로 낸다.
  - 스크립트 0C: `:713-714` 에서 pytest 설정 변경은 red 다.
- **재현**
  - FR12: 0T 에서 `[tool.pytest.ini_options] DJANGO_SETTINGS_MODULE` 을 수정했다. 결과는 `red: pyproject.toml — 제품 쪽 변경(0T 는 제품 코드 고정)`.
  - FR12b: 0T 에서 `pytest.ini` 를 신설했다. 결과는 red(같은 사유).
- **영향**: check-test-config(«pytest Django settings binding» 등)의 ⓐ 는 Coordinator 문면대로 0T 로 가지만, 항상 red 가 되어 철회 불가 STOP 에 빠진다. G3 M-3 이 이 항목을 근거로 설정을 테스트 쪽으로 옮긴 취지가 스크립트에서 사라졌다.
- **권고**: 0T 에서는 설정 파일 변경 가운데 pytest 절만 바뀐 경우를 허용한다(절 밖 변경은 red). 0T 가 수집을 좁힐 수 있게 되므로 `testpaths`·`python_files`·`addopts` 의 변경은 `보고:` 1행으로 싣고, DR hunk 대조 입력으로 넘긴다.

### J-M5. 0T `remove` 행 해석이 넓다 — 대체 커버리지로 인용된 테스트까지 지워도 green

- **위치**: `behavior_guard.py:786-796`. `| remove |` 가 있는 행에서 **모든** `.py::name` 을 허용 목록에 넣고, 경로를 떼고 이름만 센다.
- **재현**
  - FG10: design-architect 표 형식(`candidate | … | existing authoritative coverage | decision | owner/path`)으로 행을 만들었다. coverage 열이 `app/test/test_service.py::test_total`, owner/path 열이 `…::test_factory` 다. 0T 에서 **둘 다** 삭제했다. 결과는 `close green`.
  - FG8: `remove` 행이 `test_service.py::test_total` 인데 다른 파일 `test_other.py::test_total` 을 삭제했다. 결과는 green.
- **영향**: 입장 표 구조상 `remove` 행의 coverage 열에는 대체 보장 위치가 늘 들어간다(design-architect.md:80). 0T 의 유일한 예외가 그 보장까지 지우는 길을 연다.
- **권고**: owner/path 열(마지막 열)의 `path::name` 만, 경로를 포함한 채로 대조한다. 케이스 다중집합도 `(파일 기준 경로, 이름)` 으로 세되, 이동 쌍은 옛 경로로 환원한다.

### J-M6. 0T 케이스 추출이 `Test*` 클래스만 센다 — Django 관례(`XxxTests(TestCase)`)에서는 0T 기계 검사가 공허하다

- **위치**: `behavior_guard.py:177-189`.
- **재현**: FG5 는 `class MoneyTests(TestCase)` 의 `test_b` 를 삭제한 경우다. 결과는 `close green · 종류 0T`.
- **영향**
  - pytest 와 Django runner 는 unittest.TestCase 하위 클래스를 이름과 무관하게 수집한다.
  - `python_classes`·`python_functions` 설정과 믹스인이 상속한 케이스도 세지 않는다.
  - SDS 노출은 0 이다(실측: `Test*` 밖 클래스의 케이스 0). 그러나 dddjango 는 임의의 기존 Django 프로젝트를 대상으로 하므로 일반 대상에서는 0T 판정이 비어 버린다.
- **권고**: 베이스에 `TestCase`/`SimpleTestCase`/`TransactionTestCase`/`unittest.TestCase`(이름 끝이 `TestCase`) 가 있는 클래스를 포함한다. pytest 설정의 `python_classes`·`python_functions` 를 반영한다. open 요약에 «테스트 파일 N · 케이스 0» 경고를 싣는다.

### J-M7. 규범 — 감사 반영 편집이 창 밖에서 일어난다 (G3 M-1 잔여)

- **위치**
  - `dddjango/commands/dddjango.md:114`: «그 창의 마지막 슬라이스 보고를 받으면 **다음 파견 전에** close», 그리고 «0T 와 0C 는 각각 창 하나다».
  - 같은 절: «close 보고는 5번 규율 감사 입력에 붙인다».
  - `:116`(4번 하위): 슬라이스 ≥3 이면 슬라이스마다 경량 감사 → «원작성자 반송으로 반영».
- **문제**
  - 감사(경량·홀리스틱) 파견은 close **뒤**다. 감사가 슬라이스 0 파일에 낸 발견(blocker·important)을 coder 가 반영하는 편집은 어느 창에도 들지 않는다. 치환 hunk 를 고치거나 0T 테스트 편집을 되돌리는 경우가 그렇다.
  - 스크립트는 green 으로 닫힌 뒤 새 창을 허용한다(`cmd_open` 은 열린 창만 거부). 그러나 규범 문면 «각각 창 하나»가 재open 을 막는다.
  - 수정 모드의 focused DR 도 같다.
- **권고(1구절)**: «감사 반영이 슬라이스 0 파일을 고치면 같은 종류의 창을 새로 open → 반영 파견 → close 한다». 이렇게 하면 «각각 창 하나»는 «종류마다 최소 하나»가 된다.

---

## Minor

| ID | 위치 | 재현 · 관측 | 영향 | 권고 |
|---|---|---|---|---|
| J-m1 | `behavior_guard.py:826-849` | argparse 오류(`bogus` 명령·잘못된 `--kind`)는 **exit 2** 이고 `요약:` 이 없다. 5000항 이항 사슬(`X = 1 + 1 + …`)은 `ast.dump` RecursionError 로 트레이스백·exit 1 이며 `요약:` 이 없다(`fail2.out` F8·F8b — SDS 2019 파일 노출 0). | «exit 2 = red»·«모든 경로 요약 1행» 계약이 깨진다. 오타가 red 로 읽힌다. | `ap.parse_args` 의 `SystemExit` 를 잡아 exit 1 + 요약을 내고, `except` 에 `RecursionError`·`MemoryError` 를 더한다. |
| J-m2 | `:801-821` | 없는 폴더(`verify .dddjango/none`)도 `exit 0 · 요약: 동작 보존 해당 없음`. | 폴더 경로 오타가 G2 에서 조용히 통과한다. | 폴더가 없으면 exit 1 로 한다(폴더는 있고 `refactor-scope.md` 가 없을 때만 «해당 없음»). |
| J-m3 | `:753-757`·`:611` | D5: open 미측정(venv 없음) 뒤 close 에만 `--python` 을 주고 필드를 추가하면 `close green`(`동적 미판정` 보고만). D3: 드리프트가 있는 기준도 open 요약이 «동적 무변 기준»이다. | 스키마 변경이 green 으로 통과할 수 있다. 문구도 오도한다. | close 에서 변경이 있고 open 이 미측정이면 exit 1 «기준 없음 — open 을 `--python` 으로 다시 연다». open 요약은 «동적 기준 N건»으로 적는다. |
| J-m4 | `:231-261` · docstring `:14` | sqlite 설정에서 open 한 번에 저장소 루트에 `db.sqlite3` 가 **생성된다**(makemigrations 의 history 점검이 연결한다). 무시 목록에 없는 저장소에서는 0T close 가 `red: db.sqlite3 — 제품 쪽 변경`. | «저장소를 바꾸지 않는다»는 주장과 어긋난다. 장치가 자기 부작용으로 거짓 red 를 낸다. | 동적 측정 env 에 `DATABASES` 를 덮는 대신 측정 전후 untracked 목록을 비교해 새로 생긴 파일을 지우거나, 사각·요약에 적는다. 최소한 close 판정에서 open 뒤 장치가 만든 파일은 뺀다. |
| J-m5 | `:596-606` | SDS open 기록 `w1-open.json` 이 **604 KB** 다. `tests` 해시 맵 195 KB 는 close 가 읽지 않는 죽은 데이터이고, `cases` 383 KB 는 0T 전용이며 이름 목록이 중복된다. `indent=1`. | G3 m-7 이 줄인 크기(창마다 0.5~0.7 MB · `.dddjango/` 커밋)로 돌아갔다. | `tests` 를 없애고, `cases` 는 0T 에서만 `Counter` 로, JSON 은 압축 형식으로 쓴다. |
| J-m6 | `:390` | FR7: 모듈 상수 `MAX_RETRY` → `RETRY_LIMIT` 개명이 red 다. 이름 대응을 `F`(def·class)로만 한정했다. | 설계 §2.3 «정의»(단일 이름 대입 포함)와 다르다. 사각 목록에도 없다. | 값이 유일한 대입도 이름 대응에 넣거나, 사각 목록과 docstring `:21-23` 에 적는다. |
| J-m7 | `:732-739` | FR6: 마이그레이션이 참조하는 제품 callable(`upload_to` 등) 이동 → 옛 마이그레이션 import 경로 수정이 `red: 마이그레이션 수정`(SDS 노출 0 — 프로젝트 모듈을 import 하는 마이그레이션 0/86). | 일반 Django 에서 callable·필드 이동이 거짓 red 가 된다. | 마이그레이션 `.py` 에도 치환 정규형 비교를 적용하거나 사각에 적는다. |
| J-m8 | `:724-731` · design-architect.md:83 | 입장 표는 «명시 승인된 의미 보존 move/split/**rename** 재조직»을 `retain` 으로 허용하지만, 0T 는 이름이 바뀐 케이스를 감소+추가 red 로 낸다(`remove` 만 예외). | 승인된 재조직 행이 0T 에서 늘 STOP 이 된다. | 0T 허용 목록에 `retain` 재조직 행의 전후 이름 쌍을 넣거나, Coordinator 에 «rename/split 재조직은 0T 밖(기능 슬라이스)» 한 구절을 둔다. |
| J-m9 | docstring `:21-23` · 설계 §2.1 | 알려진 사각 목록에 빠진 것(모두 green 실측) <ul><li>테스트 환경을 바꾸는 제품 분류 파일(테스트 settings 모듈·pytest 플러그인 모듈 — FG7)</li><li>conftest 이동으로 autouse 범위가 바뀌는 것(FG6)</li><li>0T parametrize 리터럴 감소(FG9)</li><li>`.gitignore` 된 테스트 데이터(F5)</li><li>모듈 경로가 관찰값인 곳(로거 이름·Celery 기본 태스크 이름·pickle)</li><li>`python_files` 의 `tests.py` 분류 제외(SDS 0개)</li><li>파일 경로 치환에 경계가 없음(`:340`)</li></ul> | 사각이 문서화되지 않으면 DR hunk 대조가 볼 자리를 모른다. | docstring·설계 §2.1 사각 목록에 한 줄씩 더하고, DR 문장의 «close 가 못 보는 자리»에 연결한다. |
| J-m10 | `dddjango/agents/coder.md:78` vs `:73` (Codex coder `SKILL.md:68` vs `:63`) | 0C 문장은 «테스트 소유와 무관하게(외부 계약 테스트 포함)»라고 허용하지만, 0T 문장에는 그 구절이 없다. `:73` 은 외부 계약 테스트 편집을 금지한다. | e2e·API 통합 테스트에 난 0T ⓐ 는 편집 주체가 없다(AT 는 설계 §5-1 로 범위 밖). | 0T 문장에도 «ⓐ 항목 수리 편집은 소유 무관»을 넣거나, 0T e2e ⓐ 는 STOP 으로 올린다는 한 구절을 둔다. |
| J-m11 | `:771-782` · DR `discipline-reviewer.md:58` | close 보고와 기록에는 «치환 green N» **건수만** 있다. 어느 파일이 치환 green 인지 목록이 없다. | R-3507 의 «close 가 green 으로 판정한 치환 hunk» 예외 범위를 DR 이 기계 출처로 좁힐 수 없다. 기능 슬라이스 hunk 를 섞어 면제할 위험이 있다. | close 기록에 치환 green 파일 목록과 open HEAD..close HEAD 범위를 싣는다. |
| J-m12 | `dddjango/commands/dddjango.md:114`·`:192` | <ul><li>exit 1 «머지 겹침»의 «사유 해소»가 무엇인지 없다(되돌릴지, STOP 할지).</li><li>잇기 재개 때 verify 는 창을 열기 전이면 «창 누락» red 를 내는데, 문면은 «열린 창»만 말한다.</li><li>수정 모드 3번의 «6번 규칙의 `build_anchor`» 가 어느 6번인지 모호하다(Phase 2 6번).</li><li>verify 는 ⓐ 일부만 재상정하고 창이 0 이어도 «해당 없음»이다(`:806`·`:815` — grep 단순화의 대가).</li><li>`앞 실행` 절은 `#` 헤딩일 때만 분리된다(`:804`).</li></ul> | 규범 문면만으로는 레인이 멈추는 자리가 생긴다. | 각 한 구절: 겹침 해소 = 머지 철회 또는 `STOP_FOR_USER_APPROVAL` · 재개 verify 의 «창 누락»은 창 열기 전이면 무시 · «Phase 2 6번» 명시 · 재상정 절에 남은 ⓐ 가 있으면 창 필요(사각에 적기라도). |
| J-m13 | 설계 v4 §2.5 | 설계는 «`.venv/bin/python` → `uv run python`»인데 구현·규범은 `.venv`/`venv`/`--python` 만이다(`:221-228`). 구현 쪽이 옳다(`uv run` 은 가상환경을 만들 수 있다). | 문서가 어긋난다. | 설계 문서 §2.5 를 구현에 맞춘다. |

---

## 확인됨 (문제 없음 · 실측)

- **러너**: `python3 workspace/tools/behavior_guard_fixture_run.py` 의 20사례와 창 절차가 전부 PASS 다(30.5 s).
  - Codex byte 미러는 `cmp` 로 동일하다. `Makefile:171` 의 `diff -rq` 가 미러를 덮는다. `verify-base-regen` 에 러너가 들어 있다. `manifest_seal`·`rulepack_smoke`·`reverse_coverage` 에도 등재돼 있다.
- **현장 재생(설계 §4 기준 — 주장과 일치)**
  - 순수 이동 4커밋은 모두 `exit 0` 이다: `51374b5e1`(치환 green 9) · `c4c609c5e`(1) · `e3a26f666`(2) · `902bcd4fc`(1).
  - `ddf3f260b` 는 치환 green 28 에 red 2 다. red 는 `tests/test_seed_fortune_catalog_initial_fortune_types_data.py` 새 파일과 `tests/saju_taxonomy_interaction.test.js` 오라클 변경이다. 그 커밋에 섞인 새 기능이므로 정당하다.
  - 계약 변경 7커밋은 전부 `exit 2` 다: `339bc7f17` 12 · `75e3672ab` 5 · `390f57db1` 56(정적 마이그레이션 red) · `543170693` 21(정적 red) · `62b467b19` 18(정적 red) · `d6b0fc570` 9 · `839af8a0a` 1.
  - `339bc7f17` 의 red 는 새 메서드·새 테스트가 섞인 탓이다(커밋 제목 «item 메서드 신설»).
- **기준 밖 표본**
  - `3588986c7`(RAG 통합)은 red 9 다. 새 테스트 파일 6개와 JS 오라클 때문이며 정당하다.
  - `3adadb752`(C10→C11 개명)은 red 3 이다. 테스트 파일과 테스트 함수 이름까지 바꿨으므로, 0C 규칙상 정당하다.
  - `1717f5a9f` 는 red 15 다. 이동에 설계 변경이 섞였다.
  - 순수 이동 표본을 더 찾지 못해, #429 를 사본에 직접 재연했다(J-B1).
- **0C 양성(러너 · 재확인)**: 단언 변경 · 동명의 다른 정의로 재결합 · 대응표 밖 patch 대상 · golden 수정 · pytest 설정 수정 · 테스트 추가 · 마이그레이션 수정이 모두 red 다.
- **0C 음성**
  - 파일 이동 · 파일→패키지 승격 · isort 재배열 · 함수·클래스 개명(from-import 형) · 분류 경계 파일 이동 · 제품만 변경이 모두 green 이다.
  - RN1 의 from-import 형 테스트(`test_port.py`)와 페이크 파일 제자리 수정도 green 이다.
- **동적 마이그레이션**(스크래치 venv 의 Django 6.1 · `.venv` 심링크)
  - `--skip-checks` 를 받는다.
  - D1(필드 추가·마이그레이션 없음)은 red `shop: Add field sku to item` 이다.
  - **D2(G3 M-8 — 모델을 다른 앱으로 이동, db_table 동일, 마이그레이션 파일 무변)는 red `ledger: Create model Item`·`shop: Delete model Item`** 이다.
  - D3(드리프트 위 변경)은 새 변경만 red 다.
  - D4(close 에서 `--python` 누락)는 red «측정 실패»다.
  - `__pycache__` 는 생기지 않는다(`PYTHONDONTWRITEBYTECODE`). `uv run` 폴백이 없고 가상환경을 만들지 않는다. 부작용 예외는 J-m4 에 적었다.
- **정적 마이그레이션**: `label: str = …`(AnnAssign)을 읽는다. 앱 재배치(라벨 같음)는 green 이다(러너).
- **실패 경로**: 깨진 AST · 비 UTF-8 `.py` · 깊은 괄호(파서가 거부 → «파싱 불가» red) · 저장소 밖 심볼릭 링크 · 20 MB 바이너리 · `.gitignore` 파일 · 깨진 close JSON · 실행 줄 없는 scope · 앵커 부재 · 열린 창 없는 close · `--kind` 누락은 모두 크래시가 없다. `요약:` 1행이 나오고 exit 코드도 계약대로다. 예외는 J-m1 에 적었다.
- **창 절차**
  - 앵커 선행 · 열린 창 재open 거부 · red → 철회 → close 재실행(이력 append · «판정 2회째») · 두 번째 창 번호 · 머지 경로 제외(무관 경로) · 머지 겹침 exit 1 을 확인했다.
  - verify 는 창 누락 · 열린 창 · `ⓐ 재상정` 만 있는 경우를 가른다.
  - 실행 식별자(`behavior/<G0 값>/`)로 실행마다 번호 공간이 분리된다.
- **규범**
  - Coordinator 의 3번 분할 · «동작 보존 창» 하위 항목 · 7번 G2 차단과 `동작 보존:` 행 · 수정 모드 3번 상속 · 경계 절 기계 기록 · 슬라이스 0 STOP 의 «동작 보존 장치 오탐»이 Codex `SKILL.md`(:132·:192·:208·:233 등)에 같은 문장으로 들어가 있다.
  - coder 와 DR 미러도 일치한다.
  - 설계 메타코멘트 오염은 보지 못했다. DR 의 «close 가 못 보는 자리다»는 감사 초점 지시로 허용 범위다.
  - 스크립트 경로 `scripts/…` 는 pre-gate 문단(`:102`)의 «registry 게이트와 같은 규약» 선례를 따른다.

## 우선순위 제안

1. **J-B1**(대응표·정규형 고정점 · 디렉터리 대응 · FQ 정규형)과 **J-M1**(`bare` 제거 · 이름 뺀 해시 정정)은 같은 비교기 수정이다. 러너에 #429 모양과 FG1c·FR3 을 넣은 뒤, 재생 5커밋이 green 을 유지하는지 확인한다.
2. **J-M2·J-M5·J-M6**(0C 수집 보존 · `remove` 열 · 케이스 추출)은 수십 행 규모다.
3. **J-M3**(머지·rebase)은 30행 안팎이다.
4. **J-M4·J-M7** 과 J-m10·J-m12 는 규범 구절이다. 그래프에서 개정하고 재투영한다.
5. minor 는 J-m1·J-m2·J-m4·J-m5 만 이번에 넣고, 나머지는 사각 목록 정리로 충분하다.
