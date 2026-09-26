# 적대 재검토 G2 — 로드맵 4 동작 보존 장치(최소판) 설계 v2 (2026-09-27)

- 대상: `step4-behavior-guard-design-v2.md`(이하 v2). 앞 검토 `review-G-step4.md`(G) · 앞 설계 v1 · 측정 세부 `diag-B2-behavior-evidence.md`(B2) · 사용자 결정 `evening-report.md` §5 결정 2.
- 규범 대조: `dddjango/commands/dddjango.md`(C — 절 이름으로 인용) · `dddjango/agents/{coder,acceptance-tester,discipline-reviewer}.md`(coder · AT · DR). `design_pregate.py` 의 입장 표·file-plan 파서도 대조했다.
- 방법: G 처분표(v2 §8)의 «수용»을 믿지 않고 v2 본문 절과 한 줄씩 대조했다. 새 결함은 SDS 실측으로 확인했다.
- 실측: scratch clone `bt/sds-main`(HEAD `12d876dcc`)에서 읽기·grep·AST 파싱만 했다. 인터프리터는 SDS `.venv/bin/python` + `PYTHONDONTWRITEBYTECODE=1` 이다. clone 의 `git status --porcelain --untracked-files=all` 은 작업 전후가 같다(`rv4b/status-{before,after}.txt` · CLEAN). `/Users/hyun/Desktop/spring_dream_server` 는 git log/show/grep 으로 읽기만 했다. 스크립트는 scratch `rv4b/`(`strref.py` · `strref2.py` · `oldref.py` · `ohs_consumers.py` · `dupdefs.py` · `wlayer_v2.py` · `import_rebind.py`)에 있다. OpenAPI 입력은 G 의 `rv4/probe-test-1.json` 을 재사용했다.
- Serena · Graphify 는 쓰지 않았다. 이 파일 밖에는 쓰지 않았다.

## 판정: **설계 수정 후 재검토** — 앞 발견: 해소 8 · 부분 11 · 미해소 1 / 새 발견: blocker 0 · major 10 · minor 12

- G 의 두 blocker 는 본문으로 해소됐다. B-1 은 probe 안 autodetector 와 «미측정 ≠ 무변» 원칙으로, B-2 는 «close = 캡처 + 비교»로 풀렸다.
- 그러나 v2 가 새로 만든 절차 층에 문제가 몰려 있다.
  - 감수 입력과 close 가 서로를 기다린다(N-1 · M-6 미해소).
  - import 전용 수정은 «보고»인데, P 편집은 «G1 행 없으면 STOP»이다. 두 규칙이 서로 어긋나 M-3 의 구조적 STOP 이 그대로 남는다(N-3).
  - P 는 e2e 파일의 글자만 지킨다. 그 e2e 가 쓰는 factories·fake 는 지키지 않는다(N-2). SDS e2e 68파일 중 52파일이 대상 BC 의 test 지원 모듈을 import 한다.
- 측정 층에서는 문면 그대로 구현하면 조용한 green 이 생기는 곳이 둘이다.
  - W 정규화가 `title`·`description` 이라는 이름의 wire 필드를 지운다(N-5 · SDS 7곳 실측).
  - env 허용 목록은 결정적이지 않다(N-4).
- 재검토 범위는 N-1 · N-2 · N-3 · N-6 (절차 · 오라클)으로 좁힐 수 있다. 나머지 major 는 대부분 한 문단짜리 명세 보강이다.

## 1. 앞 발견(G) 해소 대조

| 발견 | 판정 | v2 본문 근거 | 남은 것 |
|---|---|---|---|
| B-1 마이그레이션 조용한 green | **해소** | §3 표 2행(probe 안 `MigrationLoader(None, ignore_no_migrations=True)` + autodetector · `translation.override(None)` · DB 가드) · §3 머리 «측정 산출물이 없으면 미측정» · §7 B-1 회귀 시험 | minor m2-3(describe 만 비교) · N-4(해시 시드 — 집합에서 나온 choices 순서) |
| B-2 compare 가 G2 직전 | **해소** | §1 «close … 캡처와 비교를 함께 한다 · exit ≠ 0 이면 다음 슬라이스를 파견하지 않고» · §6 ② | red 처방 뒤 **close 를 다시 돌리는 규칙**이 없다(N-1에서 다룬다) |
| M-1 입력 미고정 | **부분** | §2(pytest 설정 · 인터프리터·버전·env 해시 기록 · DB 가드) | ① env 허용 목록의 «정적 수집»은 비결정적이다(N-4) ② v1 의 `--python` 이 사라졌다. 인터프리터를 어떻게 고르는지 규칙이 없다 ③ «G0 에서 사용자에게 한 번 묻는다»는 Coordinator 3문장에 없다. 답을 적을 곳과 스크립트로 넘길 길도 없다(m2-10) |
| M-2 close 기동 실패 = 미측정 | **부분** | §3 표 0행 boot · §5 마지막 줄 | boot 만 red 로 정의했다. 나머지 런타임 단계(autodetector · OpenAPI 생성 · URL 순회 · 체크 레지스트리)에서 «open 성공 ∧ close 실패»는 v2 가 새로 만든 «close 미측정(환경 사유) = STOP»으로 떨어진다. 이 STOP 에는 선택지가 없다(m2-6) |
| M-3 P ↔ 재조직 충돌 | **부분** | §3 표 1행(import 제외 AST · G1 재조직 행 대조) · §6 coder | ① G1 입장 표에는 «전→후 경로»의 기계 형식이 없다. `design_pregate.py:757-790` 은 owner/path 셀에서 첫 Python 경로만 읽는다 ② §6 절차 · DR «retain 무편집» · AT 규범이 import 전용 허용과 모순된다 ③ P 밖에서 P 안으로 들어오는 이동(#390)은 «추가»라서 red 다 ④ 문자열 참조 수정은 사전 승인 길이 없다(SDS e2e 5파일) → N-3 |
| M-4 P 범위 | **부분** | §3 표 1행 | «창 대상 BC»의 출처가 없다. «미룰 수 없음» ⓐ 는 대상 BC 밖에도 있을 수 있다. «기타 테스트 루트»도 정의되지 않았다(N-8). 대상 BC 의 test 지원 모듈은 여전히 무보호다(N-2) |
| M-5 창 경계 5 | **부분** | §1 경계 규칙 ①~⑤ | ① 문면은 있다. 그러나 순환이 있다(N-1) ② `--window k` 는 있다. 번호 배정은 m2-9 ③ 머지 금지는 집행자 · 탐지 · 복구가 없고 현장 발주 계약과 충돌한다(N-6) ④ 실행 줄 창 표지를 누가 쓰는지 정하지 않았다. C «경계» 절의 기계 기록 열거(«시각·앵커·G2 승인»)도 고쳐야 한다(m-4) ⑤ 해소 |
| M-6 감수자 입력 시점 | **미해소** | §6 DR · §1 close 시점 | close 는 «감사 반영 뒤»인데 감사 입력은 «close 가 만든 report.md»다(순환). 슬라이스가 3개 미만이면 슬라이스 0 경량 감사 자체가 없다. «홀리스틱 직전 집계»를 실행할 명령도 없다 → N-1 |
| M-7 W 거짓 red 5 | **부분** | §3.1 다섯 규칙 · §7 smoke | 다섯 규칙은 들어왔다. 그러나 «모든 깊이에서 D»가 wire 속성 `title`·`description`(SDS 7곳)을 지운다. security 정의 치환은 인증 클래스 교체(SDS 6 op)를 가린다 → N-5 |
| M-8 OHS import 이름 | **해소** | §3 표 4행 | SDS 실측: 교차 BC 가 OHS 모듈에서 import 하는 이름은 정의 530 · contract 재수출 10 · 하위 모듈 10 이다. 그 밖의 재수출은 0 이다(`rv4b/ohs_consumers.py`). wallet 별칭(현장 OHS 유일 사례)도 주석 붙은 대입이라 잡힌다(`dd8ace685`). minor m2-5 |
| M-9 URL 이름 | **해소** | §3 표 5행 | minor m2-1(path 파라미터 이름 변경) |
| M-10 accepted-file 제3 경로 | **해소** | §5 | «장치 오탐»은 C 재상정 절의 처분 목록에 없는 새 라벨이다. 규범 개정 목록에 빠져 있다(m2-12) |
| M-11 사각 · 옛 참조 | **부분** | §3 표 6·7행 | 표면 7 은 적중을 분류하지 않는다. 그래서 #490 승격 때는 전건이 오탐이 되고, 재수출 경유 patch 헛돎은 못 가른다. 비 .py 이동과 `.yaml`·`.cfg` 등도 빠진다 → N-10 · 표면 6 m2-4 |
| m-1 줄 번호 | 해소 | §6 끝 줄 | — |
| m-2 tree SHA 소실 | **부분** | §4 | tree 는 버렸다. 그런데 표면 7 · 창 이후 재편집 · 머지 탐지에 필요한 재료(open HEAD · 창 변경 목록)를 대신 저장하지 않는다 → N-7 |
| m-3 산출 크기 | 해소 | §4 | N-7 의 재료를 넣을 때 크기 조건을 지켜야 한다(SDS 추적 26,734 · `.py` 6,880 파일 — 전체 목록은 싣지 못한다) |
| m-4 Coordinator 부하 | **부분** | §6 «세 문장» | 실제 규범 삽입 지점은 3문장이 아니라 C 9곳 + coder · DR · AT 다(§4 목록). ③ 은 조건 없이 적혀 있다(N-9) |
| m-5 값 수준 사각 | **부분** | §3.1 끝 | «보호막 수치»가 무엇인지, `verify` 요약 행에 들어가는지 정하지 않았다(m2-10) |
| m-6 open 미측정 반복 | **부분** | §5 | «정적 표면만» 결정 줄을 어디에 쓰는지, close 가 그 결정을 어떻게 아는지 정하지 않았다(m2-10) |
| m-7 manage.py 조건 | 해소 | §2 첫 줄 | — |

## 2. 새 발견

### Major

#### N-1. 창 닫기 순서가 순환이다. 슬라이스가 3개 미만이면 감사가 없고, close 를 다시 돌리는 규칙도 없다 (M-6 미해소의 원인)

- 근거
  - v2 §1: close 는 «마지막 리팩터 슬라이스 보고와 **그 경량 감사 반영**을 받은 뒤»에 한다.
  - v2 §6: DR 은 «**close 가 만든** `report.md` 를 슬라이스 0 경량 감사 입력으로 받는다».
  - 마지막 리팩터 슬라이스의 경량 감사는 close 보다 앞서야 하고, 동시에 close 산출을 입력으로 받아야 한다. 앞 슬라이스들의 감사 시점에는 `report.md` 가 아직 없다. 결국 D 층 · 옛 참조 · import 전용 수정의 판정자가 창 안에 없다.
  - 슬라이스별 경량 감사는 «슬라이스가 3개 이상»일 때만 있다(C Phase 2 4번). 슬라이스 0 + 기능 1 인 레인에는 슬라이스 0 경량 감사가 없다. 판정은 기능 슬라이스 뒤의 홀리스틱(5번)으로 밀린다. 비차단 표면에서 B-2 가 재발하는 셈이다.
  - «창 이후 재편집은 홀리스틱 감사 직전에 한 번 집계»(§6)를 실행할 명령이 없다. 명령은 open · close · verify 셋뿐이고, verify 는 «G2 배너 직전»이다.
  - red 처방 네 선택지 가운데 셋(철회해 별도 요청 · 출처 있는 ⓑ · 그리고 1차 철회)은 편집을 되돌린 뒤 **close 를 다시 돌려야** 끝난다. v2 는 close 재실행의 가능 여부를 정하지 않았다. 어느 close 가 판정인지, 앞 red 기록이 보존되는지도 정하지 않았다(`close-w<k>.json` 한 벌 · §4).
- 수정 제안
  - 순서를 이렇게 고정한다: 마지막 리팩터 슬라이스 보고 → `close` → **창 감사**(DR 경량 1회 · 슬라이스 수와 무관 · `report.md` 입력) → 반영 편집이 있으면 `close` 재실행 → 다음 파견.
  - close 는 «첫 비리팩터 파견 전»까지 몇 번이든 다시 돌릴 수 있다. 마지막 close 가 판정이고, 앞 판정은 `report.md` 에 append 로 남긴다.
  - «창 이후 재편집» 집계는 `verify` 를 두 번(홀리스틱 호출 직전 · G2 배너 직전) 부르는 것으로 대신한다. 명령 수는 그대로다.
  - 비용: 슬라이스가 3개 미만인 레인에서 DR 호출이 1회 는다. 이 비용이 싫으면 창 감사를 홀리스틱에 합치고, 그 대가(비차단 판정이 기능 슬라이스 뒤로 밀림)를 §1 에 정직하게 적는다.

#### N-2. P 는 e2e 파일의 글자만 지킨다. 그 e2e 가 쓰는 지원 모듈과 import 재결합을 통한 오라클 변경은 막지 못한다

- 근거
  - P = e2e ∪ 대상 BC 밖 테스트다(§3 표 1행). 대상 BC 의 `test/factories/**`·`test/fake/**`·`conftest.py` 는 P 밖이다.
  - SDS e2e 테스트 파일 68개 중 **52개가 자기 BC 의 `test.factories|fake|fixtures` 를 import** 한다(실측). 슬라이스 0 이 factory 본문을 제자리에서 바꾸면(예: #392 factory_boy 전환 · 기본값 변경) e2e 파일은 byte 동일하다. 그래서 신호가 0 이다. 슬라이스 0 의 전형 빚(#383~#392 factories)이 바로 이 모듈을 고친다(B2 §2.1).
  - «import 문을 뺀 AST 해시»는 **같은 이름의 다른 객체로 재결합**하는 것을 «import 줄만 바뀐 파일»(비차단 보고)로 분류한다.
    - SDS 테스트 지원 정의 136개 중 **5개 이름이 BC 마다 다른 본문**을 가진다: `MediaModelFactory` · `MediaKindModelFactory` · `FakeFortuneLibraryPort` · `DetachedTaskFake` · `ClockFake`(`rv4b/dupdefs.py`).
    - `fortune_teller` 와 `fortune_employee` 의 `MediaModelFactory` 는 다른 모델(테이블)을 만든다.
    - 이 import 한 줄을 바꿔 끼워도 open/close 해시는 같다(`rv4b/import_rebind.py` 실측: `0c23e04e1f16` = `0c23e04e1f16`).
  - 같은 사각: 함수 안 import · 상대 import 단계(`.`→`..`) 변경 · fixture 를 import 로 들여오는 conftest.
  - 판정자는 LLM 감수자다. 그런데 N-1 때문에 그 감수가 창 안에 없다.
- 수정 제안
  - P 에 **지원 정의 다중집합**을 더한다. P 파일과 대상 BC e2e 가 import 하는 test 지원 모듈, 그리고 그 경로의 `conftest.py` 체인에 있는 최상위 def/class 를 모은다. 그리고 `(이름, import 제외 AST 해시)` 다중집합을 **위치와 무관하게** 비교한다. 본문 변화는 red 이고, 이동은 무변이다.
  - «import 줄만 바뀐 파일»은 바인딩 이름마다 close 쪽 해소 대상의 `(이름, 해시)` 가 open 쪽에 같은 것으로 있을 때만 보고로 둔다. 그렇지 않으면 red 다. 해소는 저장소 안 정적 해소면 된다(`from M import n` → M 의 정의 또는 재수출).
  - 비용: 정적 해소기 1개. SDS 지원 정의 136개 규모다.

#### N-3. import 전용 수정의 «보고»와 P 편집의 «G1 행 없으면 STOP»이 모순된다. M-3 의 구조적 STOP 이 절차 층에 남는다

- 근거
  - 측정 층(§3 표 1행): import 줄만 바뀐 P 파일은 보고(비차단)다.
  - 절차 층(§6): coder 는 «P 편집이 필요하면 **편집하지 말고 보고**»하고, Coordinator 는 «G1 입장 표 재조직 행 유무로 AT 파견 **또는 STOP**»을 정한다. factories 를 옮기면 import 수정이 강제된다. SDS 에서 e2e 52파일 · 교차 BC 26줄이 여기에 걸린다. G1 에 이 파일마다 재조직 행이 없으면 STOP 이다. 측정이 허용한 것을 절차가 막는다.
  - DR 은 «일반 `retain` 은 무편집»을 hunk 대조로 감사한다(DR «Phase 2 hunk 대조»). v2 §6 은 DR 에 입력만 더하고, 이 규칙의 예외를 두지 않는다. 그래서 import 전용 수정은 DR blocker 가 된다.
  - AT 는 v2 규범 범위(§6: command · coder · DR)에 없다. 그런데 §6 은 AT 를 파견한다. AT 의 허용 행동은 `add/update/reuse/retain/remove/reject` + 명시 승인 재조직뿐이다. 자기가 방금 쓴 `add` Red 테스트(open 직전 산출)의 import 수정조차 «재조직 행 없음 → STOP»이 된다. 다른 BC 의 내부 테스트는 coder 소유인데, 이것도 «AT 파견»으로 보낸다(소유자 오류).
  - G1 행 대조는 기계로 할 수 없다. 입장 표 owner/path 셀에는 전→후 형식이 없다(`design_pregate.py:757-790` — 첫 Python 경로만 읽는다). 결국 Coordinator 가 LLM 으로 대조하게 된다.
  - P 경계를 넘는 이동이 «추가»가 된다. #390(e2e 자리 빚)은 표준 자리 밖 e2e 를 `test/e2e/` 로 옮긴다. open 의 P 에 없던 파일이 close 의 P 에 나타나므로 «추가 = red»다. `remove` 로 승인된 P 파일(예: #637 migration 전용 테스트 삭제 — coder 절대 규칙)도 «삭제 = red»다.
- 수정 제안
  - ⓐ 이동이 강제한 import 전용 수정은 **그 파일의 소유 역할이 G1 행 없이 한다**(e2e = AT · 그 밖 = coder). 검증은 N-2 의 바인딩 대조가 맡는다. coder · AT · DR 문면에 각각 한 구절을 넣는다. AT 를 규범 범위에 추가한다.
  - 이동 · 추가 · 삭제의 사전 승인 출처는 입장 표가 아니라 **design-spec 의 file-plan 기계 블록**(`add`·`remove` 행 — pregate 가 이미 파싱·검증함)으로 한다. `remove X` + `add Y` 이고 import 제외 AST 가 같으면 승인된 이동이다.
  - P 소속은 open 경로와 close 경로의 합집합으로 판정한다. 이동은 P 경계를 넘어도 짝을 찾는다.
  - (선택) C Phase 2 에서 **슬라이스 0 을 AT Red 앞에** 둔다(open → 슬라이스 0 → close → AT → 기능). AT 가 옮겨진 트리 위에서 새 테스트를 쓰므로 창 안 import churn 이 사라진다. open 기준선에 AT Red 가 섞이지 않게 하려던 B2 §2.0 의 목적도 그대로 지켜진다.

#### N-4. env 허용 목록의 «settings 가 읽는 이름을 정적으로 모은 것»은 결정적이지 않다

- 근거(SDS 실측)
  - `settings/test.py` 자체에는 env 읽기가 0 이다. 전부 `from .base import *` 너머에 있다. 수집 범위(모듈 하나인가, import 폐포인가)가 정의되지 않았다.
  - `base.py` 는 래퍼로 읽는다: `required_environment_value(key)` → `os.environ.get(key)`(`:21-22`). 인자가 변수라 리터럴 수집으로는 이름이 0개다.
  - 키 이름을 조립한다: `f"{_LLM_KEY_PREFIX}{kind}_MODEL"`(`:121-122`).
  - **접두 순회**를 한다: `name for name in os.environ if name.startswith(_LLM_KEY_PREFIX)`(`:112`) — 모르는 `LLM_` 키 하나로 기동이 RuntimeError 로 죽는다.
  - settings 밖 코드도 env 를 읽는다: `application/llm_access/driven_layer/adapter/generation_configuration/environment_adapter.py:22` · `framework/technology/rag/runtime/rag_builder/model_snapshot.py:118·128`.
  - `settings/local.py:11-12` 는 `load_dotenv` 로 **파일**을 읽는다. env 가 아니라 파일 입력이다.
- 결과
  - 허용 목록에 없는 env 가 open 과 close 사이에 달라져도(세션 재시작 · compact — 현장 HANDOFF 14건) 입력 고정 검사는 통과한다.
  - 그 차이가 기동을 깨면 boot red 가 된다. boot red 는 «승인 불가 · accepted 불가»라서, env 드리프트가 슬라이스 0 탓으로 돌아가고 빠져나갈 길이 없다.
  - 같은 이유로 집합에서 나온 choices·enum 순서(해시 시드)가 autodetector·OpenAPI 에 비결정성을 만들 수 있다.
- 수정 제안
  - env 를 «모아서 고정»하지 말고 **비운다**. probe 는 고정 키만 가진 env 로 실행한다: `DJANGO_SETTINGS_MODULE` · `PYTHONHASHSEED=0` · `PYTHONDONTWRITEBYTECODE=1` · `LC_ALL=C.UTF-8`.
  - 여기에 pytest 설정이 선언한 env(pytest-env 항목)만 더하고, 그 키·값 해시를 `open.json` 에 적는다.
  - SDS `settings.test` 는 env 0 으로 돈다(G 실측). 비용은 0 이고, 정적 수집 코드가 통째로 빠진다.
  - 이 env 로 기동이 안 되는 프로젝트는 open 미측정이 된다. 그러면 m-6 경로(«정적 표면만»)로 간다.

#### N-5. W 정규화 «모든 깊이에서 D»가 wire 필드를 지운다(조용한 green). security 정의 치환은 인증 교체를 가린다

- 근거
  - v2 §3.1 첫 규칙은 «description · summary · example(s) · title 은 **모든 깊이에서** D»다. 문면대로 키 이름으로 지우면 `properties` 아래 **속성 이름**이 `title`·`description` 인 wire 필드도 지워진다.
  - SDS 컴포넌트에 7곳이 있다: `CharacterBookOut.{title,description}` · `CharacterContentOut.title` · `FortuneAnswerSectionOut.title` · `EmployeeListItemOut.description` · `EmployeeDetailOut.description` · `CharacterDetailOut.description`.
  - 실측(`rv4b/wlayer_v2.py` — v2 다섯 규칙 + B2 의 required·키 정렬을 문면대로 구현):
    - `CharacterBookOut.title` 을 `string → integer` 로 바꿔도 **W 해시가 같다**.
    - 제거는 `required` 목록으로만 드러난다. 선택 필드였다면 제거도 보이지 않는다.
  - security: SDS 의 두 스킴 `SessionAuth`·`ChatRelaySessionAuth` 는 정의가 같다(`apiKey · cookie · sessionid`). 인증 클래스를 서로 바꾼 6 op 이 **W 무변**이다(같은 스크립트). 인증 클래스 교체는 동작 변경이다(사용자 로더 · CSRF 처리가 다를 수 있다).
- 수정 제안
  - D 키 삭제는 **스키마 키워드 자리에서만** 한다. `properties`·`patternProperties` 의 키, `parameters[].name` 의 값, `discriminator.mapping` 의 키는 지우지 않는다.
  - security 는 정의(type·in·name) 치환을 W 로 두고, 스킴 **이름** 변화는 D 로 보고한다. 이름만 같고 정의가 같은 경우의 교체 사각은 §3.1 사각 목록(m-5)에 명시한다.
  - smoke 에 «`title` 속성 타입 변경 → W red» 픽스처를 더한다.

#### N-6. 창 안 머지 금지는 집행자 · 탐지 · 복구가 없다. 현장 발주 계약과도 충돌한다

- 근거
  - C «산출물 위치»의 승인 머지 문단은 «Phase 2 중 main→레인 머지는 발주자 승인 사안»이다. 시점 제한이 없고, 코디네이터·실행자는 머지를 하지 않는다.
  - 현장 발주서는 «발주자가 이 브랜치에 넣는 `merge main (...)` 커밋은 **사전 승인된 기준 이동**이다(… STOP 없이 계속)»라고 계약한다(SDS `docs/superpowers/orders/` 다수 — product · promotion · wallet · fortune-reading 발주). 머지는 레인 세션 밖에서, 비동기로 들어온다.
  - 그래서 v2 §1 ③ «close → 머지 → 새 창 open 으로 끊는다»를 실행할 주체가 없다. Coordinator 3문장에도 없다.
  - v2 는 머지를 탐지하지 않는다. open 에 HEAD 도 적지 않는다(N-7). 창 안에 머지가 들어오면 다른 레인의 e2e · 마이그레이션 · URL · W 변화가 전부 창 Δ 가 된다. 그러면 red → STOP 인데, §5 의 네 선택지(철회 · ⓑ · 중단 · 장치 오탐)는 이 경우에 맞지 않는다. 슬라이스 0 탓도 아니고, 측정 결함도 아니다.
  - 순수 리팩터 레인(K1·K2)은 창 = Phase 2 전체다(v2 §1 · B2 §4). 캠페인 레인에서 이런 머지는 예외가 아니라 상례다(G: 승인 머지 목록이 있는 실행 15/79).
- 수정 제안
  - open 이 HEAD 를 기록한다. close 는 open HEAD..HEAD 의 first-parent 사슬에서 2-부모 커밋을 찾으면 **exit 1 «창 안 머지 <sha> — 판정 무효»**를 낸다(red 가 아니다).
  - 처방: 슬라이스 0 을 철회하고 머지 뒤 트리에서 창을 다시 연다. 또는 사용자가 «해당 창 런타임 미측정 수용(출처)»을 고른다.
  - 발주 판형(요청 가이드)에 «실행 줄에 `창k open` 이 있고 `close` 가 없으면 머지를 보류한다» 1줄을 둔다. 그리고 C 승인 머지 문단에 창 예외 한 구절을 넣는다. provenance 차분은 여전히 만들지 않는다.

#### N-7. open 이 기록하는 재료가 부족하다. 표면 7 · 창 이후 재편집 · 머지 탐지를 구현할 수 없다

- 근거
  - §4: `open-w<k>.json` 에는 «실행 식별자 · 입력 고정값 · 표면별 정규형 해시와 항목 목록»만 들어간다. 표면 7 은 open 에서 측정하지 않는다(§3 표 7행 «close 트리 전체에서 grep»).
  - 필요한 재료
    - 표면 7 은 «창에서 삭제·이동된 Python 모듈» = open 쪽 모듈 목록 − close 쪽 목록이 있어야 한다.
    - «창 이후 재편집»은 창 변경 파일과 그 close 시점 해시가 있어야 한다.
    - 머지 탐지(N-6)는 open HEAD 가 있어야 한다.
  - m-2 로 tree SHA 를 버렸고, m-3 으로 전체 인벤토리도 싣지 못한다. SDS 추적 파일 26,734 · `.py` 6,880 이다. 전체 경로→해시 맵은 약 0.7~2.6MB 이고, 커밋 대상 폴더다.
  - «AT 산출 뒤 open»이므로 open 시점 작업 트리는 보통 커밋되지 않은 AT Red 를 포함한다. `git diff <HEAD>` 만으로는 창 변경과 AT 변경을 가를 수 없다.
- 수정 제안
  - open 에 `HEAD SHA` + **open 시점 dirty 경로·blob 해시**(작다)를 적는다.
  - close 는 `git diff --name-status <open HEAD>` + untracked 에서 open dirty 분을 보정해 창 변경·삭제 목록을 만든다. close JSON 에는 **그 목록(경로 · close 해시)**만 싣는다.
  - 대안: open tree 를 비공개 ref(`refs/dddjango/<실행>/w<k>-open`)로 고정한다. gc 에 안전하고 크기는 0 이다. 단 저장소 ref 에 쓰기가 생긴다.

#### N-8. «창 대상 BC»와 테스트 루트가 입력으로 정의되지 않았다

- 근거
  - P 의 경계는 «창 대상 BC»다(§3 표 1행). 그런데 `open --window k` 에는 BC 인자가 없고, 스크립트가 무엇을 읽어 정하는지도 없다(`scope.md` 의 대상 BC? `refactor-scope.md` 의 ⓐ 경로?).
  - «미룰 수 없음» 진단은 경로와 무관하게 ⓐ 로 남는다(C Phase 0 3번 — «catch-all handler 류는 공유 표면에 산다»). 그 항목이 `framework/` 나 다른 BC 에 있으면, 그 항목을 고치는 슬라이스 0 은 자기 자리의 테스트를 P 편집으로 막힌다.
  - 다중 창(G2 시점 재상정 → G1′ → 새 슬라이스 0)에서는 창마다 대상이 다를 수 있다.
  - «기타 테스트 루트»가 정의되지 않았다. SDS 에는 pytest `testpaths = application · tests · spring_dream_server · framework · scripts` 가 있다(`pyproject.toml`). `spring_dream_server/charging_test/` 같은 루트가 여기에 든다.
- 수정 제안
  - 창 k 의 대상 = 창 k 의 ⓐ 항목 경로가 속한 BC 로 한다(BC 밖 경로면 그 최상위 트리). 출처는 `refactor-scope.md` 의 결정 줄 − `ⓐ 재상정` 제외 항목이고, 스크립트가 직접 읽는다.
  - 테스트 루트 = pytest `testpaths` 로 한다(없으면 저장소 전체의 pytest 파일 패턴).

#### N-9. 슬라이스 0 이 없는 레인에서 ③ 이 조건 없이 적혀 있다. 수정 모드는 빠졌다(사용자 결정 2 Q1)

- 근거
  - §6 ③ «G2 배너에 `verify` 의 `요약:` 행을 그대로 싣는다. exit ≠ 0 이면 G2 금지»에는 «슬라이스 0 이 있으면»이 없다. 그런데 창이 0개일 때 verify 의 동작은 정의되지 않았다.
    - B2 §5 처럼 «open 부재 = exit 1»로 구현하면 슬라이스 0 이 없는 **모든 레인의 G2 가 막힌다**.
    - «창 0 = exit 0»으로 구현하면 open 누락(가장 흔한 준수 실패)을 잡지 못한다.
  - v1 §2 는 규범 대상에 «수정 모드 · Phase 3»을 넣었다. v2 §6 은 둘을 뺐다.
  - C «수정 모드» 3번은 Phase 2 가운데 명시한 것만 상속한다(3번의 선행·혼합 금지·커밋 분리, 7번의 ⓐ 잔존 1행과 차단). 새 문장이 Phase 2 3·4·7번에 들어가면 수정 모드의 슬라이스 0 은 창을 열지 않는다. 사용자 결정 2 Q1 «정리가 들어가는 **모든 작업**»에 어긋난다.
- 수정 제안
  - verify 는 `refactor-scope.md` 의 ⓐ 결정 줄 − 재상정 제외를 읽는다.
    - ⓐ 0 이면 exit 0 · `요약: 동작 보존 해당 없음(슬라이스 0 없음)`.
    - ⓐ > 0 ∧ 창 0 이면 exit 1 «창 부재».
  - 이렇게 하면 슬라이스 0 이 없는 레인의 비용은 정적 실행 1회 + 배너 1행이다.
  - C «수정 모드» 3번 상속 목록에 «Phase 2 의 동작 보존 창(open·close·verify)» 한 구절을 넣는다. §7 행동 시험에 «슬라이스 0 없는 레인»과 «수정 모드 슬라이스 0» 두 칸을 더한다.

#### N-10. 표면 7(옛 참조)은 적중을 분류하지 않는다. #490 승격에서는 전건 오탐이고, 현장의 핵심 신호(재수출 경유 patch 헛돎)는 가르지 못한다

- 근거
  - 오탐량 실측(`rv4b/oldref.py`): SDS 의 #490 대상 `.py` 32개 모듈은 옛 dotted 경로를 담은 줄이 **73줄 · 72파일**이다(모듈당 0~5줄). 표준 수리인 동명 폴더 승격(`x.py` → `x/x.py`)을 하면 새 경로 `…x.x` 가 옛 경로 `…x` 를 접두로 품는다. 소비처를 다 고쳐도 **적중 전건이 남고, 전건이 오탐**이다. 형제 접두(`…x` vs `…x_other`)로 인한 오탐은 SDS 에서 0 이다.
  - 판정 단위가 모호하다. «삭제·이동된 Python 모듈»이 파일 단위면 승격은 이동이라 위의 오탐이 난다. 모듈 단위면 `…x` 가 여전히 import 되므로 이동이 아니고 적중이 0 이 된다. 그러면 G §6.3 이 표면 7 에 맡긴 «재수출로 옛 경로가 해석돼 patch 가 헛도는» 경우(`REPORT-notification-2.md:55`)를 놓친다. 어느 쪽으로 구현해도 핵심 신호를 가려낼 수 없다.
  - 짧은 식별자: «개명된 BC·app_label 이면 옛 식별자»를 단어 grep 하면 폭발한다. 예: `accounts` **2,523줄 · 447파일**, `fortune_teller` 1,883줄. 개명 뒤에도 REST 접두·영문 문장처럼 의도적으로 남는 적중이 섞인다.
  - 비 .py 이동은 대상 밖이다. #490 적중 가운데 JSON 데이터 파일이 9개 있다(`lunisolar_calendar_table.json` 등). 현장 사례(`Path(__file__)` 기준 데이터 경로)는 이 종류다.
  - 확장자 목록은 `.yaml`(pre-commit · compose) · `.cfg` · `.ini` · `.txt` · `.sh` · `Dockerfile` 을 뺀다.
- 수정 제안
  - 검색은 `git grep -F`(추적 + untracked 텍스트 전부 − `docs/` · `.dddjango/`)로 한다. 확장자 목록을 없앤다.
  - 적중마다 close 트리에서 해소해 세 층으로 나눈다.
    - **해소 불가**: 강 신호. `.py` 문자열 리터럴이 open 에서 해소되던 옛 경로와 정확히 같으면 red 후보다.
    - **재수출 경유 해소**: «patch 헛돎 위험»으로 따로 표시한다.
    - **새 경로 접두 일치**: 버린다.
  - 비 .py 이동은 basename 으로 grep 한다.
  - BC·app_label 개명은 dotted · 따옴표 · 경로 구분자 문맥만 센다.

### Minor

| # | 위치 | 문제 | 제안 |
|---|---|---|---|
| m2-1 | §3.1 · §3 표 5행 | path 파라미터 이름을 바꾸는 명명 수리(약어 등)는 wire(위치)가 무변인데도 W(`parameters[].name`)와 URL route(`<int:name>`)에서 red 다 | `in: path` 파라미터와 route 변환자 이름은 위치 번호로 정규화한다 |
| m2-2 | §3 표 2행 정적 | `**/migrations/*.py` **경로**→blob 이다. Django 앱을 표준 칸 `driven_layer/django_<bc>/` 로 재배치하는 일(일반 brownfield 의 전형 슬라이스 0)은 런타임 무변인데 red 다. SDS 는 20앱 모두 표준 자리라 영향이 0 이다 | 키를 (app_label, migration 이름)→blob 으로 바꾼다 |
| m2-3 | §3 표 2행 런타임 | `describe()` 는 필드 정의를 담지 않는다. open 에 같은 필드의 AlterField(기존 드리프트)가 있으면 추가 변경이 가려진다 | 연산 `deconstruct()` 직렬화를 비교한다 |
| m2-4 | §3 표 6행 | 체크 «함수 이름 집합»: 개명(check-naming 수리)은 제거+추가라 red 다. 이름이 겹치면 집합이 한쪽의 누락을 가린다 | 이름 대신 함수 본문 AST 해시의 다중집합을 쓴다 |
| m2-5 | §3 표 4행 | 정의 = «def · class · 주석 붙은 대입»이라서 주석 없는 모듈 수준 별칭(`alias = impl` — brownfield 흔함) 제거를 놓친다 | 밑줄 없는 최상위 `Assign` 대상도 정의로 본다 |
| m2-6 | §5 끝 · §3 머리 | «close 미측정(환경 사유) = STOP»은 선택지가 없다. 입력이 §2 로 고정되면 open 성공 ∧ close 실패는 정의상 코드 원인이다. close 에서 DB 가드에 걸리는 것도 새 import 시점 질의(동작 변경)다 | «open 성공 ∧ close 실패 = 그 표면 red(accepted 불가)»로 일반화한다. 미측정은 open 에서만 생긴다 |
| m2-7 | §7 smoke | 메인테이너 `.venv` 에 Django 가 없다(실측 `ModuleNotFoundError`). 그래서 probe(런타임 절반)는 `make verify` 에서 **영구 skip** 이다. ninja·Django 판 변화로 probe 가 깨지면 레인마다 «open 미측정 → 정적만» 결정으로 조용히 줄어든다 | smoke 런타임을 `uv run --with django==<핀> --with django-ninja==<핀>` 같은 격리 실행으로 돌리거나 픽스처 Django 프로젝트를 둔다 |
| m2-8 | §6 coder | «보호 목록 P 를 받는다»: SDS 에서 대상 BC 밖 테스트는 약 1,000 파일이다(테스트 루트 전체 1,095) | 목록이 아니라 규칙(«e2e · 대상 BC 밖 테스트 · 지원 정의»)을 준다 |
| m2-9 | §1 ② · §4 | 창 번호 k 를 Coordinator 가 고른다. 재사용하면 앞 창 결과를 덮어쓴다. «창 1 이후 재편집»은 창 2 가 기계로 검증한 편집까지 이중으로 센다 | 스크립트가 다음 번호를 배정하고 닫힌 창의 재open 을 거부한다. 재편집 집계에서 뒤 창이 덮은 파일을 뺀다 |
| m2-10 | §2 · §5 · §3.1 | settings G0 질문의 답, m-6 «정적 표면만» 결정, 인터프리터 선택, «보호막 수치»에 대해 **기록 위치 · 스크립트 전달 경로(CLI) · `요약:` 행 필드**가 정해지지 않았다 | `open` CLI 에 `--python`·`--settings`·`--static-only <결정 줄 파일:행>` 을 명시한다. 보호막 = 창 대상 BC e2e 파일 수를 `요약:` 필드로 둔다 |
| m2-11 | §7 탐지 시험 | 공유 scratch clone `sds-main` 에 «임시 커밋»을 하면 다른 행동 시험(T 계열)의 기준 HEAD `12d876dcc` 가 흔들린다. 적대 음성 사례(import 재결합 · `title` 속성 · #490 승격 옛 참조 · 창 안 머지 · env 차이 · 슬라이스 0 없는 레인 · 슬라이스 <3 레인)가 없다 | 별도 clone/worktree 에서 한다. 위 7개를 음성·양성 칸으로 더한다 |
| m2-12 | §5 | «장치 오탐»은 C Phase 1 «슬라이스 0 과 비위반 이동의 STOP»의 처분 목록(«별도 요청 \| 선행 별도 요청(정지) \| ⓑ \| 플러그인 결함 \| 작업 중단»)에 없는 새 라벨이다. `accepted.txt` 의 소유도 C «산출물 위치»에 없다 | §6 규범 개정 목록에 두 곳을 명시한다 |

## 3. 「특히 볼 것」 답

| 물음 | 답 | 발견 |
|---|---|---|
| 표면 7 오탐량 | SDS #490 32모듈: 73줄 · 72파일. 승격 수리를 하면 전건 오탐이다(옛 경로가 새 경로의 접두). 형제 접두 오탐은 0. 짧은 식별자 grep 은 `accounts` 2,523줄 · 447파일로 폭발한다. 재수출로 옛 경로가 유효하면 «이동 아님»(적중 0 · 헛돎 놓침)과 «전건 적중»(오탐) 사이에서 갈리지 못한다 | N-10 |
| import 제외 AST 해시가 숨기는 것 | 같은 이름의 다른 팩토리로 재결합하면 해시가 같다(실측). SDS 에 동명 이체가 5개 있다. 함수 안 import · 상대 import 단계 · conftest fixture import 도 같은 사각이다. 지원 모듈을 제자리에서 바꾸면 e2e 파일은 byte 동일하다(52/68 e2e 가 의존) | N-2 |
| 대상 BC 밖 전 테스트 = P | 창 밖 기능 슬라이스와는 충돌하지 않는다(창 밖은 판정하지 않는다). 문제는 셋이다. ① «대상 BC»의 출처가 없다 ② «미룰 수 없음» ⓐ 는 대상 BC 밖에 있을 수 있다 ③ 다중 창에서 대상이 달라진다. 대상 BC 의 지원 모듈은 무보호이고, P 로 들어오는 이동(#390)은 «추가» red 다 | N-8 · N-2 · N-3 |
| env 허용 목록의 결정성 | 결정적이지 않다. SDS 에는 래퍼 · f-string 키 · 접두 순회 · settings 밖 env 읽기 · dotenv 파일이 모두 있다. 드리프트는 boot red(탈출 불가)로 슬라이스 0 탓이 된다 | N-4 |
| 창 안 머지 금지 | 충돌한다. C 승인 머지 문단은 Phase 2 중 시점 제한이 없고, 현장 발주는 «발주자 머지 = 사전 승인 · STOP 없이 계속»이다. 집행자(Coordinator 는 머지하지 않는다) · 탐지 · 복구가 모두 없다 | N-6 |
| 슬라이스 0 없는 레인 비용 | ③ 이 조건 없이 적혀 있고, 창 0 개일 때 verify 의 의미가 없다. 구현에 따라 «모든 레인 G2 차단» 또는 «open 누락 불탐지»가 된다. 수정 모드는 빠졌다 | N-9 |
| 최소판 규모 | 아래 §4 | — |

## 4. 구현 규모

- v2 에는 재추정이 없다. B2 의 4~5일은 다섯 표면 기준이다.
- v2 가 더한 것: 표면 0·6·7 · W 다섯 규칙 · 다중 창 · 실행 식별자 · G1 대조 · 표면당 양·음 시험. 여기에 N-1 · N-2 · N-6 · N-7 · N-9 의 필수분까지 합치면 **약 6~8일**로 본다.
- **빼거나 바꿀 수 있는 것**(비용 감소)
  - 창 안 머지 «끊기» 절차 → 탐지(exit 1)만 둔다(N-6).
  - env 정적 수집 → 비운 env(N-4). 코드가 통째로 빠진다.
  - 입장 표 전→후 파서 신설 → 기존 file-plan `add/remove` 짝(N-3). pregate 파서를 재사용한다.
  - admin `app_list` 정규식 alternation 정렬 → 그 패턴을 URL 비교에서 빼고 `_registry` 집합으로 대신한다(등록 누락은 집합이 더 직접 잡는다).
- **빼면 안 되는 것**: close 재실행 · 창 감사(N-1), 지원 정의 다중집합 · 바인딩 대조(N-2), open HEAD · dirty 기록(N-7), verify 의 ⓐ 판독(N-9).
- **«3문장»의 실제 삽입 지점**(m-4)
  - C 9곳: ① «산출물 위치»(`behavior/` · `accepted.txt` 소유 · 승인 머지 창 예외) ② «실행과 앵커»(실행 줄 창 표지) ③ «경계»(기계 기록 열거) ④ Phase 0 G0 settings 질문 ⑤ Phase 1 재상정 처분 «장치 오탐» ⑥ Phase 2 3·4번(open·close · 병렬 예외 · 창 감사) ⑦ 5번(DR 입력) ⑧ 7번(금지 목록 · 배너) ⑨ «수정 모드» 3번 상속
  - 역할 3곳: coder(P 규칙 · import 전용 수정 허용) · DR(retain 무편집의 import 전용 예외 · report 입력) · **AT**(import 전용 수정 · 규범 범위 추가)
  - Codex 의미 미러 4곳(SKILL · coder · DR · AT)
  - 문장 수를 줄이는 것보다, 스크립트가 판독할 수 있는 것(ⓐ 결정 줄 · 창 번호 · 머지 탐지)을 스크립트로 옮기는 편이 준수율에 더 효과적이다.
