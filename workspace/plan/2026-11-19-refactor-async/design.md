# 설계 v1.3 — dddjango 2.42.0 후보: 리팩토링 때 난 문제(F4-185 · F4-183 · F4-184)

> 정리본 — 일 폴더(`workspace/scratch/…`) 근거 파일 · 장난감 경로는 배포 뒤 정리에서 지워졌다. 판 결과는 `plan-2.42.0.md`.

(v1.3: 둘째 좁은 재확인 T 의 새 중요 — 일반 R-3760 에서 기준선과 지금 판을 같은 꼴로 · isort 갈래는 구현 때 실제 isort 로 잼 · 검토 P 첫째 재확인 문면 고침)

작성 2026-11-19 · 운영자. v1(17시대) → v1.1(18시대): 설계 독립 검토 T · P 처분(`DISPOSITION.md`) 반영 → v1.2: 좁은 재확인 T 의 남은 둘(정렬 맞춤과 일반 끝 검사 · 읽기만 꼴 `--no-fix --force-exclude`)과 사소 셋. 기준 배포판 2.41.0(`63e40084`). 근거: `work-a/REPORT.md` · `work-b/REPORT.md` · `work-b/DESIGN-DRAFT.md` · `work-c/REPORT.md` · `work-c/DESIGN-DRAFT.md` · `rev-t/REPORT.md` · `rev-p/`. 코드 초안: 탐침 `rev-p/probe-e/`(변형 E — `work-b/toy/probe-c` 에서 반환 때 참조를 놓는 한 줄) · P1 · P2 · P3 사본 `work-c/repo-exp/`.

## 0. 결정

| 번호 | 결정 | 출처 |
|---|---|---|
| U1 | 이번 판 범위 = 리팩토링 때 난 문제 F4-185 + 같은 옮기기 도구 F4-183 · 184(F4-181 · 182 뺌 · F4-161 보류 유지) | 사용자 «그렇게하자.»(11-19 14:55 뒤 · 14:59 앞) |
| U2 | F4-185 = 탐침이 비동기 시험도 증거로 받게(«가») · 전후 녹색만(«나») · 기능 모드 문서만 인정(«다»)은 안 함 · SSE #63 9건은 리팩토링 V 로 | 사용자 «가.»(15:36 뒤 · 15:51 앞) |
| D1 | 결과 증거를 **프레임 결속**으로: 구간 안 · 같은 맥락에서 시작한 결속 코드 프레임만 세고 그 밖 프레임의 이어짐 · 반환은 맥락 밖 · 동기 · 비동기 한 갈래 · 반환한 프레임은 그때 표에서 빼고 참조를 놓음(v1.1 · P-I1) | 운영자 처리(질문 생략 · 설계 처리 · 이의 시 뒤집음) — U2 의 구현 |
| D2 | **실행기 닫힌 목록**: 코루틴 본문은 `pytest_asyncio.plugin.Coroutine` · `IsolatedAsyncioTestCase`(Django 시험 클래스 아님 · 실행기 메서드 재정의 없음)만 받고 그 밖은 G0 정지(사유 셋) · Django 판별이 먼저 | 운영자 처리 |
| D3 | 실행기 메서드 재정의 판별 이름 넷(`_callTestMethod` · `_callAsync` · `_callMaybeAsync` · `_setupAsyncioRunner`) · anyio 는 목록 밖 | 운영자 처리 |
| D4 | 사유 판형 «결과 증거 없음(시작 s · 정상 반환 r · 맥락 밖 사건 f)» 그대로 · 탐침 기록 판(2) 그대로 · behavior_support 무변 | 운영자 처리 |
| D5 | B0 영구 픽스처 `.venv-probe` 에 `pytest-asyncio==1.4.1.post1` 더함 · 새 사례 약 24 | 운영자 처리 |
| D6 | F4-183 P1: 이번 이동이 파일을 넣는 묶음 폴더에 표지가 없으면 빈 `__init__.py` 를 만든다 · 디스크에 이미 있으면(UTF-8 아님 · 링크 포함) 만들지 않음 · apply 가 `표지 <경로>` 줄을 따로 냄(v1.1 · T-S1 · S2) | 운영자 처리 |
| D7 | F4-183 P2: pre-gate empty 행 충돌 문면을 «묶음 창(`--debt` · 끝 맞춤) 몫 — file-plan 에서 뺀다» 로 가름(판정 · 요약 종류 그대로) | 운영자 처리 |
| D8 | F4-183 P3: pre-gate 사본의 `__init__` 체인 보강이 묶음 폴더는 건너뛰어 새 파일만으로 서는 묶음의 empty 행 빠짐을 #655 로 예보 | 운영자 처리 — D9 의 짝 |
| D9 | 슬라이스 중간 검사의 #656(`draft --run` 남은 이동 대상)과 «file-plan 에 그 `__init__.py` 행이 없는 묶음» 의 #655 는 끝 맞춤 몫(반송 · STOP 아님) — 조정자 R-3703 · coder s004/b15(TREE_CONTRACT_MISMATCH 블록)에(v1.1 · T-I4) | 운영자 처리 |
| D10 | F4-184: 묶음 창 coder 는 apply 뒤 명세 완료 조건 린터를 표준 입력 꼴로 **읽기만** 돌아 새 진단을 보고 → import 정렬 규칙(ruff `I` · isort) 진단이 있으면 조정자가 **«정렬 맞춤» 을 제 0C 창**으로 파견(두 모드 · 묶음 창 아님) → 그 밖 새 진단은 G2 배너 알림 · 기준선 = 묶음 창을 연 커밋 · 슬라이스 0 `--debt` 창 뒤도 같음(v1.1 · T-B1 · I1 · I2 · I3) | 운영자 처리 — 자매 web 과 같은 «coder 가 기준선 대비 린터» 수준 |
| D11 | 리팩토링 모드: 정렬 맞춤 0C 창(`--mode refactor`)에서 대상 BC 밖 파일(갈래 `묶음 import 치환`)은 고치지 않고 G2 배너 알림 | 운영자 처리 — 받아들일 한계 |
| D12 | 정렬 맞춤의 우회 위험은 0C 창 close · 감사 · suite · 게이트로 덮고 따로 기계 대조는 더하지 않음 | 운영자 처리 |
| D13 | (덧) B0 `old-13` 흔들림: 사례 장난감 `pytest.ini` 를 `addopts = -n 2 --dist each` 로(제품 · 러너 · 기대 무변 · v1.1 · P-I3) | 운영자 처리 — 원인 = 시험 장치 비결정 |
| D14 | 판 번호 2.42.0(minor) · dddjango-web 무변 | 운영자 처리 |
| D15 | 탐침 상태 조작 구멍(배포판 2.41.0 에도 있음 · P-I4)은 이번 판 밖 — 작업 리스트 «현장 보고 밖 후보» 에 올림 | 운영자 처리 — 사용자 범위(U1) 밖 · 사용자에게 알림 |

## 1. 재현 표(배포판 2.41.0)

| 보고 | 재현 | 조건 | 생기면 | 누가 | 운영자가 본 정도 |
|---|---|---|---|---|---|
| F4-185 | 재현됨 | 전체 suite 에 `async def` 시험이 하나라도(저장소 단위) | G0 `support --collect` exit 2 → 묻지 않고 정지 · G2 suite · verify 도 같은 까닭 red | 발주자(SSE 레인) | SSE 사본 수집 366 · 사유 426 · 레인 기록과 글자까지 같음 · 장난감 async exit 2 / sync exit 0 |
| F4-183 ① | 재현됨 | 끝 맞춤 앞에 새 파일이 묶음 폴더를 먼저 만듦 | 창 판정 · verify green 인데 G2 registry_gate #655 red · coder 가 손으로 보충 | 발주자(레인 둘) | 장난감 base 갈래(#655 red) |
| F4-183 ② | 재현됨 | 명세에 그 표지를 `empty` 로 적음 | pre-gate «empty 충돌(실존)» 형식 red · 설계 검토 한 바퀴 | 발주자(레인) | 일꾼 장난감 · 현장 리포트 글 |
| F4-183 ③(덧) | 재현됨 | 새 파일만으로 서는 묶음에서 empty 행을 빠뜨림 | 예보 green · 실제 #655 red | 이번 조사 | 일꾼 장난감 · 실제 작업에서 본 것은 아님 |
| F4-184 | 재현됨 | 묶음 이동 import 치환이 정렬 열쇠를 바꾸고 자리는 그대로(꼴 넷) | ruff I001 · 줄바꿈 꼴은 format 도 · pre-push 훅이 push 를 한 번 실패 | 발주자(레인) | 장난감 base 갈래(I001 ×2) |
| old-13(덧) | 재현됨(흔들림) | B0 r7-2c 사례가 시험 하나 · 일꾼 둘 · 마지막 일꾼 출력을 버림 | 시험을 돈 일꾼이 버려지면 사유 하나 더 → make verify 가 가끔 red | 일꾼 B · 2.41.0 첫 make release | 코드 읽어 원인 확인 |

## 2. F4-185 — 프레임 결속 + 실행기 닫힌 목록

### 2.1 왜 막혀 있었나

- 결과 증거 = passed 로 보고된 시험마다 그 본문이 call 단계 안 · 같은 맥락에서 시작해 정상으로 끝까지 돌았나(`sys.monitoring` · 탐침 `:15-18` · `:495-604`).
- 코루틴은 멈췄다 이어져, 창 밖에서 미리 시작한 다른 실행이 창 안에서 정상 반환하면 개수가 맞는다(실제 실행이 실패를 삼켜도) → v13 ①(4cd1999f · 2.20.0)이 일시 중단 가능한 본문을 통째로 뺐다(B0 R12-3 · R12-4).
- 관문만 걷으면 SSE 366 은 녹색이지만 같은 꼴 공격 9 꼴이 거짓 녹색(실측).

### 2.2 판정식(D1)

- call 동안 결속 코드 하나에 PY_START · PY_RESUME · PY_YIELD · PY_RETURN 지역 사건.
- 표 = 구간 안 · 같은 맥락에서 PY_START 한 결속 코드 프레임(콜백 안 `sys._getframe(1)` · 표에 있는 동안 참조를 쥠 — 주소 재사용 막음).
- s = 표에 넣은(누적) 프레임 수 · r = 표 안 프레임의 PY_RETURN 수(반환하면 그때 표에서 빼고 참조를 놓음 — 시험 몸의 지역 값 수명을 바꾸지 않음) · f = 다른 맥락의 모든 사건 + 표에 없는 프레임의 RESUME · YIELD · RETURN.
- passed call 마다 s ≥ 1 ∧ r = s ∧ f = 0 ∧ 재진입 없음(지금 식 · 문구 그대로) · 돌아오지 않은 프레임만 구간 끝까지 쥠 · PY_THROW · PY_UNWIND 는 켜지 않음.

### 2.3 실행기 닫힌 목록(D2 · D3) — 수집 때, 가장 안쪽 코드가 `CO_COROUTINE` 일 때만

1. 항목 종류 정확히 `pytest_asyncio.plugin.Coroutine` → 받음(`ALLOWED_ITEMS` 에도 · AsyncGenerator · AsyncStaticMethod · AsyncHypothesisTest 는 안 넣음).
2. `_pytest.unittest.TestCaseFunction` 이고 MRO 에 `__module__ == "django.test.testcases"` 클래스가 있으면 정지(Django 가 async 시험 메서드를 `async_to_sync` 로 다른 스레드에서 돌림 · Isolated 와 함께 상속해도 이 판별이 먼저).
3. 아니고 `IsolatedAsyncioTestCase` 하위이며 저장소 쪽 MRO 클래스가 D3 이름을 재정의하지 않으면 받음 · 재정의하면 정지.
4. 그 밖(Function 항목 코루틴 — anyio 표지 · strict 표지 없음 · pytest-asyncio 0.21 이하 · 그냥 `unittest.TestCase` async 메서드(몸이 돌지 않고 PASSED) · 동기 감싸개 `asyncio.run` 꼴) 정지.
- generator · iterable coroutine · async generator 는 지금처럼 «일시 중단 가능한 본문» 정지.
- 새 G0 사유 셋: `결과 증거 범위 밖 — 다른 스레드에서 도는 비동기 본문(Django 시험 클래스의 async 메서드 — async_to_sync)` · `결과 증거 범위 밖 — 실행기 메서드를 재정의한 비동기 본문(IsolatedAsyncioTestCase · <이름>)` · `결과 증거 범위 밖 — 실행기를 모르는 비동기 본문(coroutine · 항목 종류 <종류>)`.
- 정지는 지금 자리(flags · suspend · bad)로 가서 support 계수 · verify `suspend 0` 이 그대로 작동 · 실행 중에 실행 자리를 옮기는 꼴(재정의를 setUp · monkeypatch 로 · 꾸밈 함수가 몸을 다른 스레드로)은 G0 을 지나고 G2 에서 red(안전 쪽 · 한계).

### 2.4 바뀌는 파일

- `dddjango/scripts/pytest_probe/dddjango_collect_probe.py`(±50줄 · 초안 `rev-p/probe-e` 를 D3 넷으로 좁혀): 머리 주석 `:15-18` · `:77` ALLOWED_ITEMS + 상수 · `:85` 상태 칸 · `:320-322` 코루틴 갈래 + `_async_runner_gap(item)` · `:495-508` 콜백(시작 · 중간 · 반환 — 반환 때 표에서 뺌) · `:521-522` 등록 · `:575-583` 구간 열고 닫기.
- `dddjango/scripts/behavior_guard.py`: `_suite_lines` `:3759-3760` 설명 글(«구간 안에 시작한 프레임 ≥ 1 · 모두 정상 반환 · 그 밖 프레임 · 맥락 사건 0») · `:3720` · `:3761` 표시 이름 «일시 중단 본문 n» → «결과 증거 밖 본문 n»(실행기 목록 밖 정지도 셈).
- `behavior_support.py` 무변 · 탐침 기록 판 2 그대로(rel support 로 B0 · SSE 판정 — 실측).
- Codex byte 미러 둘 · 봉인 대상 둘.
- 그래프 0(조정자 `:286` R-3624 · `:326` R-3643 은 탐침 지원 범위 · 결과 증거 식을 적지 않음).
- B0(`workspace/eval/fixtures/behavior_probe/`): 기대가 바뀌는 기존 칸 8(AS1 통과 · AS2 사유 «다른 스레드 …» · R12-3 · R12-4 G0 사유 2 → 1 · G2 사유가 «결과 증거 없음(1·0·2)» 로) · 새 사례 약 25(DESIGN-DRAFT §3.6 의 20 — 단 AP8 은 «재귀 · 차례 두 번 · parametrize 통과» 대조로만(변형 E 에서는 참조 보유 변이를 못 잡음 · v1.2) + p5 꼴 동기 tearDown weakref 통과(반환 때 놓기 변이를 잡음) · Isolated + Django 함께 상속 두 차례 G0 정지(Django 판별 순서 변이) · greenlet 숨김 동기 공격 G2 red(결속을 코루틴에만 거는 변이 · conftest 는 `sys.modules.pop` 만 — 복원 쓰기를 넣으면 정적 규칙이 먼저 잡아 뜻이 바뀜) · 같은 스레드 `run` 재정의 통과(D3 넷 고정) · old-13 짝 «완료 조건만» 사례(§5)) · 칸 수 줄 · counts · 탐침에서 안 쓰게 된 `_S["returned"]` 지움.
- `probe-fixture-requirements.txt` 한 줄 · `Makefile:343` probe-env 확인 줄.
- README `:319` 리팩토링 G1 항목 끝: «비동기 시험(pytest-asyncio · unittest `IsolatedAsyncioTestCase`)도 그 증명에 쓴다 — 시험 몸이 그 실행 안에서 끝까지 돌았는지를 실행 단위로 본다. Django 시험 클래스의 async 메서드처럼 다른 스레드에서 도는 시험이나 실행기를 알 수 없는 비동기 시험은 대개 시작(G0)에서 멈추고, 실행 자리를 실행 중에 옮기는 시험은 증거 실행(G2)에서 붉다.»

### 2.5 실측

- 적대: 일꾼 B 14 꼴 + 검토 P 새 꼴(같은 코드 객체 다른 함수 · `__code__` 바꿔치기 · greenlet 숨김 · 주소 재사용 노림 · eager task factory · contextvars · 클래스 안 async 메서드 · Isolated + Django · 실행 자리 옮김) — 변형 C · E 비동기 새 구멍 0 · greenlet 숨김 동기 공격은 배포판 거짓 녹색을 새 판이 닫음.
- B0 644: 바뀌는 칸 8 뿐(C · D(이름 넷) · E 모두) · pytest-asyncio 를 더한 환경도 같음 · `pre_route_behavior_smoke` PASS · `uv pip check` 31 맞음.
- SSE 사본 전체(366 · 일꾼 6): C · E 모두 366 passed · 탐침 bad 0(운영자 직접 C).
- Python 3.12.16 · 3.13.18 · 3.14.10 · 3.15.2 에서 콜백 안 프레임 · 탐침 전체(장난감 8 꼴) 판정 같음(검토 P).
- 동기 tearDown weakref(p5): 탐침 없음 · rel · E 2 passed · C 1 failed(운영자 직접) → E 채택.

## 3. F4-183 — 묶음 표지

- P1(D6) `folder_group.py:1483-1485`: `received = {이동 쌍 새 경로의 폴더}` · `d not in before or d in received` 인 묶음 폴더에 `setdefault(<d>/__init__.py, "")` · `perform` 은 새로 만드는 표지가 디스크에 이미 있으면(`lexists` — UTF-8 아닌 글 · 링크) 쓰지 않음 · apply 출력에 `표지 <경로>` 줄(실제로 쓴 목록 = `perform` 반환에서 · v1.2) · 설명 `:1468-1470` · `perform:2110`.
- P2(D7) `design_pregate.py` `materialize(…, group_made=frozenset())` · empty 갈래에서 대상이 이미 있고 `group_made` 안이면 `empty 충돌(묶음 창 몫): <경로> — 이 실행의 묶음 이동이 이 묶음에 파일을 넣고 표지를 만든다(묶음 창 — --debt · 끝 맞춤 · folder_group.py apply) — file-plan 에서 이 행을 뺀다` · 그 밖 «empty 충돌(실존)» 그대로.
- P3(D8) `design_pregate.py:4738-4745` 체인 보강이 묶음 허용 칸의 직계 묶음 폴더(`folder_group.slot_of` · `recognize == "group"`)는 표지를 만들지 않음(승격 · 시험 거울 · 새 애그리거트 부모 · web 은 지금처럼 — 검토 T 실측 오탐 0).
- 실측: P1 장난감 registry_gate 귀속 0 · P2 문면 · P3 예보 · make verify 안 러너 7종 판정 · 요약 배포판과 같음 · folder_group 3.9 다리 green · S1 데이터 손실은 운영자 재현(고칠 것).
- 픽스처: folder_group 새 시나리오 «이미 있는 묶음 폴더 + 끝 맞춤 이동»(옛 표지 없는 묶음은 손대지 않음 · 변이 둘) · «이미 있는 UTF-8 아닌 · 링크 표지는 그대로» · pre-gate «묶음 group» 셋(① 묶음 창 몫 문면 ② 새 파일만 · empty 없음 #655 ③ + empty green · 변이 둘).
- Codex byte 미러 둘 · 봉인 대상.

## 4. F4-184 · D9 — 글(graph-owned)

| 자리 | 블록 · 규범 | 바뀜 |
|---|---|---|
| coder `agents/coder.md:47` | s004/b10 · R-3760 개정 | nit 치환 · 정렬 맞춤 파견(슬라이스 0 포함)은 이 일반 검사 대신 제 검사(v1.2 · T 재확인 ③) · 일반 검사도 기준선과 지금 판을 같은 꼴(같은 플래그 · stdin 또는 같은 플래그를 준 경로)로 잰다 — 플래그는 검사마다: 린터(`ruff check`) `--no-fix --force-exclude` · 포매터 검사(`ruff format --check`) `--force-exclude` · 타입 검사 해당 없음(v1.3 · T 둘째 · 셋째 재확인 — 기준선만 바꾸면 린트 제외 파일에서 거짓 «새 진단» · 운영자 재현 `op/t/stdin/` · `ruff format` 은 `--no-fix` 를 받지 않음) · 묶음 창 파견은 apply 뒤 명세 완료 조건 린터를 **표준 입력 꼴로 읽기만**(`git show`/파일 → `ruff check --no-fix --force-exclude --stdin-filename <f> -` · isort 면 `--check-only`(제외 설정을 따르는 꼴) · 고침 · 포매터 없음 · 대상 = apply 출력의 이동 새 경로 · 고침 파일 · 기준선 = 묶음 창을 연 커밋 · 옮긴 파일은 옛 경로) · 새 진단을 `묶음 창 린터 <명령>: 새 진단 n — <파일 · 규칙 코드>` 로 보고하고 고치지 않음 · 기존 기준선 재기(stdin 꼴)에도 `--no-fix --force-exclude`(v1.2 · 같은 꼴 · `fix = true` 설정에서 진단을 놓침 — 운영자 재현) |
| coder s004/b15(TREE_CONTRACT_MISMATCH) · s004/b2 참조 | 개정(교차 참조) | 슬라이스 파견 검사의 #656(묶음 자리)과 «file-plan 에 그 `__init__.py` 행이 없는 묶음» 의 #655 는 끝 맞춤 묶음 창 몫 — 반송하지 않고 완료 보고에 적음(판정은 Coordinator) · s004/b2(골격 위반 반송)에 한 구 참조 |
| coder `:81` | s006/b7 · R-3708 개정 + 새 규범 «정렬 맞춤» | 읽기만 린터는 편집이 아님 · 새: «정렬 맞춤» 파견(0C 창 안)이면 준 파일에 린터의 import 정렬 고침만(`ruff check --force-exclude --select I --fix <파일…>` · isort 면 `isort --filter-files <파일…>`) · 테스트 소유와 무관하게(0C 치환처럼) · 다른 규칙 · 포매터 · 손 편집 없음 · 끝 검사 = 기준선(묶음 창을 연 커밋) 대비 import 정렬 규칙 새 진단 0 을 위 읽기만 꼴(`--select I --no-fix --force-exclude` stdin)로 — 그 밖 규칙 진단은 보고만 |
| 조정자 `commands/dddjango.md:164` | s007/b61 · 새 규범 «정렬 맞춤 창» · R-3703 개정 | 묶음 창(`--debt` · 끝 맞춤) `verify --window` 뒤 coder 보고에 import 정렬 새 진단이 있으면 다른 편집 전에 0C 창을 열어(`open --kind code --mode feature|refactor`) coder 를 «정렬 맞춤» 으로 파견(그 진단 파일만 · 기준선 = 묶음 창을 연 커밋) → (커밋하는 실행이면 커밋) → close → `draft --run` 남은 이동 0 · 리팩토링 모드는 대상 BC 밖 파일(갈래 `묶음 import 치환`)을 빼고 G2 배너 알림 «묶음 import 차례(대상 BC 밖) n» · import 정렬 밖 새 린터 진단(줄 길이 등)은 G2 배너 알림 · R-3703: 끝 맞춤 앞 수시 검사의 #656 과 `draft --run` 남은 이동 새 경로 폴더의 #655 는 끝 맞춤 몫(반송 · STOP 아님) · 그 밖 #655(P3 를 놓친 «새 파일만 묶음») 는 설계 반송 · pre-gate 재예보 |
| 조정자 `:312` · Codex `:329` | 리팩토링 슬라이스 차례 | «→ 끝 0C 묶음 창» 뒤에 «(→ 정렬 맞춤 0C 창)» |
| 조정자 `:153` | s006/b13 · R-3697 명료화 | 묶음 표지 두 갈래: 이 실행의 묶음 이동이 파일을 넣는 묶음 = 묶음 창이 만듦(명세에 안 적음) · 새 파일만으로 서는 묶음 = file-plan `empty`(빠지면 pre-gate #655 예보) |
| discipline-reviewer `:67` | agent-discipline-reviewer 블록 개정 | 일반 `retain` 무편집의 예외 = «0C 창(슬라이스 0 · 묶음 · 정렬 맞춤)의 close green_files» · 정렬 맞춤 창의 hunk 는 «import 문 집합 같음 · 차례 · 괄호 줄바꿈만 바뀜» 을 본다(v1.2) |

- 파이프라인(DEVELOPMENT §3): canon_turtle 왕복 먼저 → `ontology/rules/agent-coder.ttl` · `command-dddjango.ttl` · `agent-discipline-reviewer.ttl`(개정 = 새 Expression(지난 판이라 제자리 아님) · 신설 둘 = ISSUED(끝 R-3782 뒤) · Block statesNorm · delegatedTo) → ontology_gate → `ontology_render.py --apply` → LEDGER 재기준선 → target-counts(Norm +2 · Expression 개정 · 신설 수만큼) → q4 golden → `make rulepack` · 체크리스트 8 은 검사기 무변이라 해당 확인만.
- Codex 뜻 미러(손): `codex-dddjango/skills/dddjango-coder/SKILL.md:39` · `:44` · `:71` · `codex-dddjango/skills/dddjango/SKILL.md:173` · `:183` · `:329` · `codex-dddjango/skills/dddjango-discipline-reviewer/`.
- 실측: 제 0C 창 정렬 맞춤 = close green(시험 파일 치환 green) · verify · draft · folder_group verify · registry_gate 귀속 0 · ruff · format --check green(운영자 직접 `op/t/`) · 시험 함수 안 지역 import · 커밋 안 하는 실행도 green(검토 T) · 리팩토링 모드 대상 BC 밖 파일 정렬은 어느 창이든 red(일꾼 C R2 ~ R4).

## 5. (덧) B0 old-13 흔들림(D13)

- 원인: 사례 «r7-2c xdist -n 2 · 워커 출력 하나 빠짐» 이 시험 하나 · 일꾼 둘 · `drop_worker`(`behavior_support.py:832-835` · 시험 자리)가 출력 파일(pid 이름) 글자 차례의 마지막 일꾼을 버림 → 시험을 돈 일꾼이 버려지면 사유 하나 더 · 실레인 영향 0.
- 고침: 사례 장난감 `pytest.ini` 를 `addopts = -n 2 --dist each`(두 일꾼이 모두 시험을 돎) — 제품 · 러너 · 기대 무변(검토 P 러너 12/12 · 흉내 20/20) · 구현 때 20번 돌려 흔들림 0 확인.
- 짝 사례(T-S9 · 검토 P 재확인): «처분 = 선택 · 완료 < 선택»(완료 조건만 걸리는 꼴)을 고정하는 사례가 지금 B0 에 없음(«확인 못 함 — 선택 …» 을 고정하는 same13-06 · v11-33 · prev-32 는 모두 처분 < 선택) → `-n 2` · 시험 둘 · `drop_worker` 사례 하나 더함(두 일꾼이 하나씩 돎 · 사유 둘 «xdist 출력 불완전(준비 ['gw0', 'gw1'] · 출력 ['gw0'])» · «선택 2 · 처분 2(call 보고 2 · skip 0) · 완료 1» · 흉내 20/20).

## 6. 받아들일 한계

1. 몸 반환 뒤 task 실패 · 다른 입력으로 다시 부름 · 몸 안 try/except 로 단언 건너뜀 · `__wrapped__` 미끼 감싸개 — 동기 시험과 같은 한계(감사 몫).
2. 자기 실행을 시작만 하고 닫는 몸 → 거짓 red(보수 쪽).
3. Django async · anyio · 실행기 재정의 · 모르는 실행기 · pytest-asyncio 0.21 이하 · 동기 감싸개 `asyncio.run` 꼴 → G0 정지(지원 밖 · 사유가 갈려 보임) · 실행 자리를 실행 중에 옮기는 꼴은 G0 을 지나 G2 에서 red.
4. pytest-asyncio 0.23 ~ 0.26 · trio · uvloop · greenlet 적재 asyncio 는 재지 않음.
5. 돌아오지 않은 프레임 참조는 구간 끝까지 쥠 · 참조 보유를 빼는 변이는 B0 로 결정적으로 못 박지 못함(주소 재사용을 재현 못 함 · v1.2 문면 고침).
6. 리팩토링 모드 대상 BC 밖 파일 I001 은 남음(G2 알림 · 프로젝트에 고침 훅이 있으면 그것이 한 번 고침) · 정렬 밖 새 린터 진단(줄 길이 등)도 G2 알림 · 포매터 실패는 재지 않아 알리지 않음(플러그인 수준 — 포매터는 coder 정적 검사 밖).
7. 리팩토링 모드 정렬 맞춤 0C 창의 대상 BC 시험 파일마다 개별 감사 키 1 · 정렬한 «옮긴 파일 자신» 은 registry_gate `pure` 에서 빠져 승인 머지 유입 판정에서 귀속으로 남을 수 있음 · refactor_audit `_rename_only` False(리뷰 쪽).
8. P1 뒤에도 S1 ~ 끝 맞춤 사이 #655 는 남음(D9 글로 끝 맞춤 몫).
9. P3 로 «새 파일만 묶음 · empty 없음» 명세가 pre-gate red(진탐 · architect 반송 한 번 늘 수 있음).
9b. 표지 없는 옛 묶음이 이 실행의 묶음 이동을 받고 명세가 그 `__init__.py` 를 `empty` 로 적으면 배포판 green → 새 판 pre-gate 형식 red «묶음 창 몫»(R-3697 대로 · D7 의 «판정 그대로» 는 이 갈래만 예외 · 진행 레인 재예보에서 드러날 수 있음 · 구현 검토 IC 중요-1).
10. 린터가 명세 완료 조건에 없는 프로젝트는 정렬 맞춤 없음 · nit 치환이 바꾼 import 이름의 I001 도 범위 밖 · isort 갈래 — stdin 꼴은 skip 대상이면 도구 오류로 끝나 지금 판은 경로 꼴로 재고 기준선 재기가 도구 오류면 기준선 0 으로 셈(skip 경로 → 비skip 경로로 옮긴 파일은 엄격한 쪽으로 셈 · 구현 G 실측 · IT 사소-3).
11. old-13 의 남은 비결정(pid 자릿수 경계 · 감김)은 드묾.
12. 탐침 상태 조작(같은 프로세스 코드가 탐침 셈을 고침)은 배포판부터 있는 구멍 — 이번 판 밖(D15).

## 7. 좁은 재확인에서 볼 자리

- T: B1(정렬 맞춤 = 제 0C 창 · reviewer 예외) · I1(기준선) · I2(조건 · 알림) · I3(읽기만 꼴 · force-exclude) · I4(자리 · 넓이) · S1(이미 있는 표지).
- P: I1(변형 E) · I2(새 사례) · I3(old-13 길).

## 8. 검사 · 문서

- `make verify` 전체 + `make verify-mutation`(rulepack · behavior_guard) · 봉인 두 번 · 매니페스트 판 올림 때 `claude plugin validate`.
- README `:246`(«묶음 폴더 표지(빈 `__init__.py`)도 만들고, 바뀐 import 차례는 명세 완료 조건 린터의 import 정렬로 맞춘다(리팩토링 모드 대상 밖은 G2 알림)») · `:319`(§2.4) · master `work_flow.spec.json` «창 안에서만» 노트 · «묶음 창 · verify» 노드 글 · 기준 판 줄 · REQUEST_GUIDE 바뀔 것 없음(요청 칸 · 좋은 예 · 나쁜 예 · 플러그인이 묻는 일 그대로 · 묶음 · 린터 · async 언급 0).
