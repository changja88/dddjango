# dddjango-web 2.3.1 — 현장 보고 F4-77(IM27 이 «요청 경로 비교» 를 «API 호출 주소» 로 막는다) (운영자 · 10-10 ~ 10-11 · 재현 · 설계 · 설계 점검 둘 · 구현 · 구현 검토 · 보완 · 재검토 · 실제 장면 반영판)

## 바탕
- 바탕: R main `f349f878`(dddjango-web 2.3.0). 2.3.1 은 패치다 — 검사 86종 그대로(새 검사 0 · 빚 지문 `CHECK_IDS` · `KEY_SCHEME` · 86 · 79 · 7 무변).
- 사본 `<S>/web-231e`(첫 구현) → `<S>/web-231g`(보완 1) → `<S>/web-231h`(보완 2 · 배포 후보). `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/f77/`(재현 `r1` · `r1-v230.txt` · 설계 `plan.md` · 설계 점검 `check.md` · `check-2.md` · 구현 `impl.md` · 구현 검토 `review-codex.md` · `review-claude.md` · 보완 `fix-1.md` · `fix-2.md` · 재검토 `rereview-codex.md` · `rereview-claude.md` · 마지막 재검토 `rereview2-codex.md` · `rereview2-claude.md` · 운영자 실측 `measure-v231.run` · `measure-v231b.run` · `measure-v231c.run` · `rv-fix2.run` · `rv1/` · `rv2/` · `rv3/` · 레인 현재 상태 사본 `sd13`).
- 현장 보고: `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` F4-77(6-3-13 · 2026-10-10 21:08:32 등록 — G2 를 이 한 건이 막음 · 레인 사용자 «플러그인 수리 뒤 이어 간다»).
- 사용자(글자 그대로):
  - (보고 붙여 넣기) «이런 보고가 왔어. 이것도 실제하는 문제인지 확인하고 맞다면 절차대로 수리 진행해줘»(10-10 21:12:21 date 뒤 · 21:14:50 date 앞).
  - 결정 18 «추천대로 해줘»(21:16 date 뒤 · 21:37:53 date 앞) = 이 고침을 F4-75 묶음과 따로 먼저 2.3.1 로 낸다 · 조건(픽스처 · verify-web · 실제 장면 여덟 · Codex · Claude 구현 검토 차단 0)을 모두 통과하면 묻지 않고 배포하고 끝난 뒤 보고한다.

## 판정과 넣은 것
| 항목 | 뿌리 | 넣은 것 |
|---|---|---|
| F4-77 IM27 이 요청 경로 비교 글자를 막음 | `check_imports.py` 의 IM27 리터럴 절반이 DataSource · common/network 밖 파일의 모든 문자열 앞 `/api/` 를 용도와 무관하게 잡는다(`_API_LITERAL_RE`) — 규칙의 뜻은 «API 를 **부르는** 주소는 DataSource 에서만 짓는다» 인데, 들어온 요청의 경로를 견주는 글자는 아무것도 부르지 않는다 | `.py` 에서만 AST 로: 요청 경로 식(`request.path` · `path_info` · `get_full_path()` · `get_full_path_info()` · `META["PATH_INFO"]` · `META.get("PATH_INFO")` · 그 값으로 한 번만 묶인 지역 이름)과 `==` · `!=` · `startswith` · `endswith` · `in (…)` · `not in (…)` 로 직접 견주는 **문자열 상수의 그 위치만** IM27 에서 뺀다(값 · 줄 단위가 아니다 — 같은 줄 · 같은 값의 호출 주소는 그대로 선다) |

- 보고자 제안 셋 가운데 «요청 경로와 비교되는 글자만 뺀다» 를 골랐다 — «호출에 쓰이는 문자열만» 은 DataSource 밖 상수(`CHART_URL = "/api/…"`)를 놓치고, «`root/handler/` 를 범위 밖» 은 그 안의 실제 호출을 숨기고 다른 자리의 같은 꼴은 못 푼다.
- **경계**(하나라도 어기면 그 함수의 글자는 하나도 빠지지 않는다):
  - 인자 이름이 `request` 이고 그 함수에서 다시 바인딩되지 않는다.
  - **요청 경로를 읽는 모든 꼴**(위 경로 식 + 인자가 붙은 `get_full_path(…)` · `build_absolute_uri` · `environ` · `scope` · `META` 의 경로 키 / 상수 키가 아닌 꼴)이 비교 자리 · 첫 `이름 = 경로 식` · 인정된 로그 문장의 인자 밖에서 나오지 않는다(호출 인자 · 반환 · 다른 이름에 대입 · 조건식의 값 · 안쪽 함수 · comprehension 에서 읽기 포함).
  - 연쇄 비교 · f-문자열 · 인접 문자열 결합 · walrus · 변수에 담은 컨테이너는 예외 꼴이 아니다.
  - **로그 예외** — 실제 보고 파일이 비교 앞에서 경로를 로그에 넘기기 때문에 둔다: 받는 쪽이 logging 출처로 확인되고(모듈 범위의 `import logging[.하위]` · `from logging import getLogger` · 한 번 묶인 `이름 = logging.getLogger(…)`), **그 파일에서 출처가 될 수 있는 이름 모두**(logging 의 모든 별칭 · `getLogger` 이름 · 어느 범위에서든 `getLogger(…)` 를 대입받은 이름)가 «바인딩 한 번 + 속성 읽기의 받는 쪽» 으로만 나오고 `from … import *` 가 없을 때(하나라도 벗어나면 그 파일의 로그 예외를 전부 끈다 — 같은 logging 객체를 다른 별칭 · `getLogger(…)` 로 다시 얻어 쓸 수 있어서다), 독립된 표현식 문장이며, 경로 식에서 그 호출까지 낀 노드가 `keyword` · f-문자열 · 왼쪽이 문자열 상수인 `%` · 튜플 · 사전뿐이고, 수준 메서드(`debug` ~ `critical`)이거나 `log`(level 자리 제외)일 때만 «재사용 아님».
- 헤더가 있는지만 보는 `"<헤더 키>" in request.META`(`not in`)는 경로 읽기가 아니다(경로 키 · 변수 키 · `.keys()` · `.items()` 는 경로 읽기).
- 파싱하거나 판정하지 못하는 파일(문법 오류 · 너무 깊은 식 — 판정 고리의 `RecursionError` · `MemoryError` 포함)은 2.3.0 판정 그대로 · 보조 파싱은 경고를 흘리지 않는다.
- 글: implementation-django `references/final.md` §4 문장 한 구 · `SKILL.md` 요약 한 구 — Codex 미러.

## 넣지 않은 것
- 템플릿의 같은 꼴(`{% if request.path == "/api/" %}`) · 정규식(`re.search("/api/", path)`) · 부분 문자열(`"/api/" in request.path`) · `match request.path:` — 계속 IM27(다른 파서 · 위치 처리가 든다).
- `self.request.path`(클래스 기반 뷰) · `request.path.rstrip("/")` 처럼 가공한 뒤의 비교 · structlog 등 표준 logging 밖 로그.
- 설계 점검이 처음 권한 «경로 값을 호출 인자로 다시 쓰면 무조건 무효» 는 그대로 두면 **보고된 파일이 풀리지 않아**(비교 앞의 로그 줄) 보완 점검(`check-2.md`)을 거쳐 위 로그 예외로 좁혔다.

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| S1 픽스처 · `make verify-web` | 전체 실패 0(본체 171 · extract 53 · contract 13 · 2.2.5 308 · 2.2.6 114 · 2.3.0 956 · IM27 121 · debt 119 · subst 196 · sdk 368 · refactor_audit 309) · exit 0(보완 2 판) |
| S2 재현 저장소 `<S>/f77/r1` | 2.3.0 IM27 다섯(처리기 `:6` · `:8` + VM 셋) → 처리기 둘만 사라지고 VM 셋(상수 · 호출 인자 · f-문자열)은 그대로 |
| S2′ 실제 레인(6-3-13 현재 상태 사본 `<S>/f77/sd13` = `b4901d71f` + 미커밋 · `--diff-base cb546747 --slice-end --design-build <기록 폴더>`) | 2.3.0 막힘 4(IM27 `root_error_handler.py:18` · MD2 2 · PU2 1) + 승인 유입 2 → **IM27 한 건만 사라짐**(막힘 3 — 남은 셋은 레인이 진행 중인 자기 작업 몫) · 그 밖 출력 같음 |
| S3 무변 | 실제 장면 여덟(`<S>/web-226-notes/s2.sh`) 2.3.0 과 byte 동일 · 호스트 시점별 사본 넷 빚 조사 같음 · 빠질 글자가 없는 입력의 stdout · stderr · exit 동일(픽스처 U 묶음) |
| S4 숨김 0 | 운영자 재현 `<S>/f77/rv2`: 숨던 꼴(logger 메서드 바꿔치기 둘 · 별표 import · 인자 붙은 경로 식 · 기본값 붙은 `META.get`)은 보완 뒤 다시 서고, 보고된 실제 파일 · 호스트 logger 관례(`_logger: logging.Logger = logging.getLogger(__name__)`) · 헤더를 읽는 미들웨어는 0 · 변이 89 가운데 88 을 픽스처가 잡음(남은 하나는 결과가 같은 변이) · 보완 2: `<S>/f77/rv3` 의 같은 logging 객체를 다른 이름으로 쓴 꼴 셋(별칭 둘 · `getLogger` 다시 얻기 · 한 logger 오염이 같은 파일 다른 logger 로 옮음)이 다시 섬 · Django 관용 `logger.warning("Not Found: %s", request.path, extra={…})` · `"HTTP_AUTHORIZATION" in request.META` 미들웨어 · 함수마다 `log = logging.getLogger(…)` 는 0 · 실제 코드 3,865 파일에서 예외 0 · 이번 바퀴 변이 60 가운데 놓친 하나는 픽스처를 더해 잡음 |
| S5 구현 검토(Codex · Claude) | 구현 검토: Codex «차단 3»(로그 출처 덮어쓰기 · 별표 import · 파싱 경고) · Claude «차단 1»(인자 붙은 경로 식으로 다시 씀) — 넷 다 운영자 · 검토자 실행으로 재현 → 보완 1 → 재검토: Codex «차단 1»(같은 logging 객체를 다른 별칭 · `getLogger` 다시 얻기로 쓰면 오염이 안 옮음 — 운영자 재현 `rv3`) · Claude «차단 1»(lambda 1,000 겹에서 판정 고리 `RecursionError` → exit 1) → 보완 2 → 마지막 재검토: Codex «배포 가능 · 차단 0»(코드 읽기) · Claude «배포 가능 · 차단 0»(임시 저장소 실행 — 앞 차단 둘 닫힘 · 900 · 980 겹 정상 판정 · 1,000 · 1,100 · 3,000 겹 2.3.0 과 exit · stderr byte 동일 · Python 3.14 · 3.12 · 고치기 전 판 51 FAIL 재확인 · 남은 숨김 22 꼴은 모두 logger 메서드 자리에 API 호출 함수를 넣어야 생기는 꼰 꼴로 한계 안) |

## 알려진 한계
- **이름 휴리스틱**: 인자 이름이 `request` 인 것이 실제 요청 객체인지 증명하지 않는다. `request` 를 통째로 넘긴 뒤의 사용(`api_client.forward(request)` · `getattr(request, "path")`) · `request` 의 별칭(`r = request` 뒤 `r.path`) 은 쫓지 않는다(숨김 쪽 · 일부러 써야 생기는 꼴).
- **로그 출처**: 다른 모듈이 바깥에서 logger 를 바꾸는 것 · `globals()["logger"] = …` · `from logging import Logger` 뒤 클래스 메서드 덮어쓰기 · `logging.root` · `logger.manager` 처럼 출처 이름에서 읽어 낸 값을 다른 이름에 담아 고치는 것 · 동적으로 얻은 logging 모듈(`sys.modules["logging"]` · `importlib.import_module("logging")` · `__import__("logging")`)로 메서드를 바꾼 뒤 정상 이름으로 로그를 남기는 것 · logging 설정 호출(`setLoggerClass` · `addHandler` · `addFilter`)로 로그를 다른 데로 흘리는 것 · `self.logger` · 함수 인자로 받은 logger 를 통로로 같은 logger 를 고치는 것 · 맨이름이 아닌 그릇(사전 · 튜플 풀기 · `for` · `cast` · 조건식)으로 받은 logger · 하위 모듈 별칭을 거친 logging(`h.logging…`) · `mock.patch("logging…")` · `loggerDict.update(…)` 는 보지 못한다(숨김 쪽 · 일부러 써야 생기는 꼴 — 마지막 재검토 둘이 «한계로 적을 것» 으로 분류).
- **글과 주석**(마지막 재검토의 «고치면 좋음» · 이 판에서 안 고침): reference 한 구는 로그 예외가 **파일 단위로 꺼진다**는 것을 적지 않아 과보고 쪽으로 넓게 읽히고, 검사기 머리 주석 ① 의 «`getLogger(…)` 를 대입받은 모든 이름» 은 실제 수집(맨이름 대상)보다 넓게 읽힌다. 픽스처는 `import logging.handlers` 만 있는 파일에서 `logging` 을 고치는 꼴을 따로 묶지 않는다(코드는 옳다). 호스트가 쓰는 선언 관례(`이름: logging.Logger = logging.getLogger(__name__)`)를 막지 않으려고 `logging.Logger` 읽기는 출처를 무효로 하지 않는다.
- **과보고로 남는 것**(2.3.0 과 같은 판정): 템플릿 · 정규식 · 부분 문자열 `in` · `match` · `self.request.path` · 가공한 경로의 비교 · `self.logger` · 인자로 받은 logger · 속성을 대입한 logger(`logger.propagate = False` — 파일 단위라 같은 파일의 다른 logger 로 남긴 로그도) · 별표 import 가 있는 파일의 로그 · 변수 키 META 읽기 · `request.META.items()` · 인자 붙은 `build_absolute_uri("/login/")` · `JsonResponse({"path": path})` · `redirect(request.path)` 처럼 비교 밖에서 경로를 읽는 함수 · UTF-8 BOM 으로 시작하는 파일.
- 인접 문자열 결합 `"/api" "/x"` 는 2.3.0 부터 IM27 정규식에 안 걸린다(이번에 안 바꿈).
- 2.3.0 으로 동결한 `debt-g0.json` 은 «판 경계» 없이 이어진다 — 이 예외로 사라진 `IM27|<경로>` 키는 잔존 확인에서 «갚음» 으로 읽힌다(오탐이 사라진 것과 실제 수정을 가르지 않는다).
- 2.3.0 이 «다음 web 판에서 닫는다» 고 적은 `{% static '…css' <공백> 토큰 %}` 놓침은 결정 18 에 따라 이 판이 아니라 2.3.2 에서 닫는다.
