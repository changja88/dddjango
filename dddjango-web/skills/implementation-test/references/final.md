# 테스트 표기법 — pytest·Django 테스트 클라이언트·unittest.mock·결정성

> **출처:** pytest(docs.pytest.org — `monkeypatch`·`parametrize`·`--import-mode=importlib`)·pytest-django(pytest-django.readthedocs.io — `client`·`live_server`·`django_find_project`)·Django 테스트 문서(docs.djangoproject.com/en/stable/topics/testing/tools — `Client`·`headers=`·`force_login`)·unittest.mock(docs.python.org — «where to patch»·`create_autospec`)·Beautiful Soup(`select`)·Playwright for Python(playwright.dev/python — `expect` 자동 재시도·`page.route`·`page.clock`)·htmx 2.x 요청 헤더(htmx.org/reference — `HX-Request`) — dddart implementation-test(2026-06-17 확인)의 web 이식.
> 본문은 implementation-django §7(테스트 표기 이전 자리)을 받아 pytest·Django 테스트 클라이언트로 표기한 것이다. 무엇을 테스트할지·단언 FORM은 discipline-test, 요청 수명·CSRF는 implementation-django §6으로 위임한다.

---

## 목차

- §1. 패키지 라인 — 왜 표준 unittest.mock인가
- §2. 격리 — VM 대체·VM 단위·ApiClient 목
- §3. 더블 — unittest.mock·단언 어휘
- §4. 화면 테스트 결정성 — 테스트 클라이언트·HTMX 헤더·브라우저 테스트
- §5. 날짜·시간 결정성 — 주입
- §6. 외부 주소 이미지 — 조건부
- §7. 헬퍼 계약 — 단일 정의
- §8. 안 쓰는 것 — 스크린샷 비교·외부 E2E 러너·pytest-mock·mutation

---

## §1. 패키지 라인 — 왜 표준 unittest.mock인가

- `pytest`·`pytest-django`(Django 설정 로드·`client`·`live_server`·`db` fixture) — 토대. 실행은 **build-state의 `test_command`** 한 줄이다 — Coordinator가 G0 (8)에서 pytest가 settings를 찾는 길(호스트 pytest 설정의 `DJANGO_SETTINGS_MODULE` · 환경변수 · 없으면 `manage.py`의 기본값으로 `--ds=<모듈>`을 붙임)을 확인해 확정하고 coder-web 입력으로 넘긴다(예 `pytest web_test --import-mode=importlib --ds=config.settings`). Coordinator 전수 테스트와 coder-web green 래칫이 같은 명령을 쓴다 — 명령을 손으로 바꿔 settings 지정을 빼거나 다른 settings를 붙이지 않는다. importlib 모드는 web 미러 트리의 여러 폴더에 같은 이름 테스트 파일이 있어도 충돌하지 않게 한다(대신 테스트 폴더를 `sys.path`에 넣지 않는다 — §7).
- Django 테스트 클라이언트(`django.test.Client` — Django 번들, 설치 0) — 페이지·조각 요청(§4).
- **더블은 표준 `unittest.mock` + pytest `monkeypatch`**: **추가 설치 0**이라 채택한다. 목 전용 플러그인(`pytest-mock`)을 더하면 같은 일을 하는 두 표기가 생기고 의존이 하나 늘어난다 — 표준 라이브러리만으로 가짜·호출 검증이 된다(§8 pytest-mock 주석-제외).
- `beautifulsoup4`(HTML 단언 — 응답 HTML을 `BeautifulSoup(response.content, "html.parser")`로 읽어 CSS 선택자로 집는다). Django의 `assertContains(…, html=True)`는 요소를 속성까지 통째로 맞춰야 해 클래스 하나만 바뀌어도 깨지고, 범위를 좁혀 개수를 셀 수 없다.
- (조건부) `pytest-playwright`(승인된 UI JS 기능이 있는 화면만 — §4) + 브라우저 설치 `playwright install chromium`.
- 버전 값은 훈련 기억으로 적지 않는다 — 무핀 설치(`pip install <pkg>`)로 resolve된 실버전을 호스트의 개발 의존 선언(호스트가 쓰는 requirements-dev·pyproject dev 그룹)에 `==`로 고정한다(coder 경계 규율과 동일). 테스트 의존은 전부 dev.

## §2. 격리 seam — dddjango-web no-DI에서 가짜 주입

dddjango-web은 **DI 없음**이다(architecture-state §10 "DI 없음"): UseCase·Repo·DataSource는 plain class라 VM이 `ChannelUseCase()`로 직접 생성하고, view가 요청마다 VM을 직접 생성한다(implementation-htmx §2). → **repo·usecase를 주입할 자리가 없으므로 생성자로 갈아끼울 수 없다**(선택적 인자 + `or Default()` 폴백 seam도 두지 않는다 — architecture-state §2). seam은 셋뿐이다:

- **(A) 순수 도메인 직접** — 판정(구별·정렬·도메인 양갈래·계산)은 도메인 단위(애그리거트 메서드·domain_service·specification·ui_extension 필터)라 입력을 인자로 받는다. 그것을 *직접 생성·호출*하고 단언한다(VM·요청 불요). discipline-test §3.1·§3.2·§3.5·§3.6이 이 seam — thick domain 무게중심이 여기다.
- **(B) VM 대체** — view 행위(렌더·탭)는 화면 VM을 *통제된 State를 돌려주는 가짜로* 갈아끼워 검증한다. view 모듈이 VM 클래스를 이름으로 불러 생성하므로 **그 view 모듈의 이름**을 바꾼다:

```python
def test_detail_shows_temperatures(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    state: ForecastDetailState = detail_state(high=7, low=-3)
    monkeypatch.setattr(
        "web.application.weather.presentation_layer.view.forecast_detail_view.ForecastDetailVM",
        lambda: FakeDetailVM(state),  # 진짜 VM처럼 인자 없이 생성되고, build(day)가 state를 돌려준다
    )
    page: BeautifulSoup = get_page(client, WeatherNavigator.forecast_detail_href("2026-06-17"))
    assert len(page.select('[data-testid="forecast-detail-view"]')) == 1
```

바꿀 이름은 **쓰는 자리**(view 모듈)의 이름이다 — VM 정의 모듈의 이름을 바꾸면 view는 import 시점에 받아 둔 원래 클래스를 계속 쓴다(unittest.mock 문서의 «where to patch»). `monkeypatch`는 테스트가 끝나면 원래 이름을 되돌린다. VM의 `build(...)`가 경로 인자(예: 날짜)를 받으면 가짜 VM이 그 인자를 State에 *echo*하게 만들어 "전달된 인자"를 검증한다(discipline-test §3.4 탭 FORM의 날짜-echo — `FakeDetailVM`·§7).

- **(C) ApiClient 목 (seam C·통합·드물게)** — *실제* VM/UseCase/Repo 스택을 통제된 서버 데이터로 끝까지 돌릴 때만. Repo가 `ChannelDataSource(ApiClient())`를 직접 생성하므로(implementation-django §4) seam은 **ApiClient 계층**이다: 테스트가 `ApiClient`의 호출 메서드를 목으로 바꾼다(§3). 무게중심이 아니다(정전 = unit 두텁게) — 판정은 (A), view는 (B)로 덮고 (C)는 정말 필요한 통합 1~2건에 한정한다.

VM을 *단위*로 볼 땐 VM을 직접 생성해 `build(...)`가 돌려준 State를 단언한다(`state: ChannelSummaryState = ChannelSummaryVM().build()`) — 요청 하나에 VM 하나라 정리할 수명이 없다. 조회 실패(채널 ①)는 `with pytest.raises(BadRequestResponse):`로, 액션 실패(채널 ②)는 액션 메서드가 돌려준 State의 `error` 필드로 단언한다(architecture-state §4) — 단 *통제된 입력*이 필요하면 위 (C) ApiClient 목을 함께 쓴다(repo 주입은 불가).

## §3. 더블 — unittest.mock·단언 어휘

순수 도메인 테스트(seam A)는 *값*을 넣지 더블이 거의 없다. 더블이 필요한 곳은 (C) ApiClient 목과, (B)에서 쓰는 가짜 VM 정도다. **표준 `unittest.mock`**(설치 0 — 목 플러그인을 더하지 않는다):

```python
from unittest.mock import MagicMock


def test_channel_summary_builds_from_api(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_get: MagicMock = MagicMock(return_value=[{"id": "ch-1", "name": "공지"}])  # (C) ApiClient 계층 목
    monkeypatch.setattr(ApiClient, "get", fake_get)
    state: ChannelSummaryState = ChannelSummaryVM().build()
    assert [channel.name for channel in state.channels] == ["공지"]
    fake_get.assert_called_once_with("/api/channels")  # 호출 검증 · 호출 없음은 assert_not_called()
```

- 손으로 쓴 가짜 클래스(`class FakeDetailVM:` — 고정 반환) · `MagicMock(return_value=…)`·`create_autospec(X, instance=True)`(상호작용 검증 — autospec은 실제 시그니처와 다른 호출을 `TypeError`로 막는다). 인자 매처 `unittest.mock.ANY`·`call(…)`. 클래스 속성 자리에 둔 `MagicMock`은 함수가 아니라 `self`를 받지 않는다 — 호출 검증 인자에 `self`가 없다.
- **pytest 단언 어휘**(단언 FORM의 도구 — 형태 규율은 discipline-test §3): 맨 `assert`(pytest가 실패 시 양쪽 값을 펼쳐 보인다) — 동등 `==` · 순서 있는 컬렉션은 리스트끼리 `==`(리스트와 튜플은 같지 않다) · 길이 `len(x) == n` · 타입+필드 `isinstance(x, T) and x.field == expected`(frozen dataclass는 통째 `==`) · 예외 `with pytest.raises(E):` · 정상 종료는 호출 자체. Either 양갈래는 `result == Right(value=expected)` / `isinstance(result, Left)`(discipline-test §3.5 — Left=`BadRequestResponse`는 네트워크 실패라 (C) seam과 함께).
- **HTML 단언 어휘**: `page.select('[data-testid="…"]')`(일치 전부 — 리스트) · `len(…) == n`(정확 개수) · `tag.get_text(strip=True)`(글자) · `tag["href"]`·`tag["data-date"]`(속성) · 범위는 찾은 요소에서 다시 `select`. `select_one`(첫 하나)은 개수를 숨기므로 단언에 쓰지 않는다(discipline-test §3.4).

## §4. 화면 테스트 결정성 — 테스트 클라이언트·HTMX 헤더·브라우저 테스트

**페이지·조각 요청**: Django 테스트 클라이언트로 GET 한다 — 주소는 navigator의 reverse 헬퍼(`WeatherNavigator.forecast_list_href()` — implementation-django §2)로 만든다(경로 리터럴 금지). 조각(HTMX) 요청은 실제 htmx가 붙이는 요청 헤더를 그대로 붙인다:

```python
page_response: HttpResponse = client.get(WeatherNavigator.forecast_list_href())
fragment_response: HttpResponse = client.get(rows_href, headers={"HX-Request": "true"})  # 조각 요청(Django 4.2+ headers=)
assert fragment_response.status_code == 200
rows: BeautifulSoup = BeautifulSoup(fragment_response.content, "html.parser")
```

- 화면이 서는지 = `status_code == 200` + view 루트(`[data-testid="<화면>-view"]`) 정확히 1(§7 render-smoke).
- **조용한 빈 렌더**: Django 템플릿은 없는 변수를 빈 문자열로 렌더한다(`string_if_invalid` 기본값) — 상태 필드 이름이 틀려도 200이 난다. 슬롯 단언(discipline-test §3.3)이 그 자리를 막는다 — 200만 보고 green으로 두지 않는다.
- **CSRF**: 테스트 클라이언트는 CSRF 검사를 하지 않는다(`enforce_csrf_checks=False` 기본) — POST 테스트에 토큰을 넣지 않아도 된다. 토큰 배선 자체는 implementation-django §6 표기로 지킨다.
- **로그인 화면**: `@login_required` 화면은 `client.force_login(user)`(pytest-django `django_user_model`·`db`) 뒤 요청한다 — 미로그인 GET은 로그인 주소로 302다.

**브라우저 테스트(승인된 UI JS 기능이 있는 화면만)**: 파일은 `<화면>_browser_test.py`(web_test 미러). pytest-playwright `page` + pytest-django `live_server`:

```python
import os

from playwright.sync_api import Page, expect

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")  # Playwright 동기 API의 이벤트 루프 위 DB 접근 허용(테스트 하니스 제약)


def test_password_toggle_reveals_input(page: Page, live_server: LiveServer) -> None:
    page.goto(live_server.url + AccountNavigator.sign_in_href())
    page.get_by_test_id("password-toggle").click()
    expect(page.get_by_test_id("password-input")).to_have_attribute("type", "text")
```

- **`DJANGO_ALLOW_ASYNC_UNSAFE`**: Playwright 동기 API는 테스트 스레드에서 이벤트 루프를 돌리므로 같은 테스트의 Django DB 접근이 `SynchronousOnlyOperation`으로 막힌다 — 앱 결함이 아니라 하니스 제약이라 브라우저 테스트 파일 머리에서만 연다.
- `live_server`는 같은 프로세스의 다른 스레드에서 돈다 — `monkeypatch`로 바꾼 VM(seam B)이 브라우저 요청에도 그대로 적용된다. `{% static %}` 파일도 함께 서빙된다(`django.contrib.staticfiles` 설치 시).
- **기다림은 `expect(…)`의 자동 재시도 단언만** 쓴다 — `page.wait_for_timeout`·`time.sleep` 고정 대기 금지(느린 기계에서 깨지고 빠른 기계에서 시간을 버린다). 타이머·지연 진행 자체가 필요하면 `page.clock`(`install` 후 `run_for`)으로 결정적으로 진행한다 — 끝나지 않는 대기를 걸어 둔 채 테스트를 끝내지 않는다.
- 브라우저 테스트도 discipline-test FORM을 그대로 쓴다: 정확 개수 `to_have_count(n)` · 정확 글자 `to_have_text(x)`(부분 일치 `to_contain_text` 금지) · non-edge `nth(2)`.
- **샌드박스 안 브라우저**: macOS 샌드박스(예: Codex 셸 샌드박스)는 Chrome 시작에 필요한 시스템 서비스를 막아 브라우저가 시작 즉시 죽는다 — 이 환경에서 브라우저 테스트가 섞인 실행은 처음부터 샌드박스 밖에서 돈다(어디서·어떻게는 Coordinator·coder-web의 «브라우저 실행 환경» 규칙). 샌드박스 안에서 돈 실행의 브라우저 시작 실패(`BrowserType.launch: Target page, context or browser has been closed` · 브라우저 프로세스 `SIGABRT`/`SIGTRAP` · `bootstrap_check_in … Permission denied`)는 그것만으로 원인을 정하지 않는다 — 샌드박스 밖에서 다시 돈 결과가 그 테스트의 결과다(밖에서도 실패하면 실제 실패). 같은 실행에서 브라우저 없이 돈 테스트의 결과는 그대로다. 테스트를 건너뛰거나 지우거나 하니스·브라우저 판을 바꿔 우회하지 않는다.

**영구 시험 재현성**: `web_test/`·호스트 시험 트리와 시험 지원 코드(`conftest.py`·`_support.py` 등)는 `.dddjango-web/`를 읽거나 쓰지 않고 프로젝트 루트 밖 머신 고정 고정물·기준판·캐시에 기대지 않는다. 고정물·기대 자료는 시험 트리에, 실행 기록은 `tmp_path` 등 임시 폴더에 둔다. 선택 도구 부재는 호스트 규칙대로 skip하고 설치된 도구의 고장은 실패로 남긴다. 레인 전용 환경 변수 존재 단언으로 실행 전제를 만들지 않는다 — 정상 환경 변수 행위 시험·필수 settings는 허용하며 환경 변수 의미 판정은 TG2 밖, discipline 감수와 G2 표준 실행이 확인한다.

## §5. 날짜·시간 결정성 — 주입

시간 의존 테스트는 pre-commit에서 *무관한 날*에 깨진다(테스트 수행 시각에 통과 여부가 달라지면 결함이다). dddjango-web은 시간을 **주입**으로만 들인다(게이트 없음·시계 고정 도구 불필요):

- **도메인 판정은 순수 함수** — '오늘'·'기준일'을 *인자로 받는다*(`def is_stale(self, now: datetime) -> bool` 식). 도메인 안에서 `datetime.now()`·`date.today()`·`timezone.now()`를 직접 부르지 않는다.
- **'지금'이 실제로 필요한 edge**는 view가 `timezone.now()`를 한 번 읽어 VM 생성 인자로 넘긴다 — 테스트는 VM을 직접 만들며 고정 값을 넘기거나 VM 대체(seam B)로 통제한다.
- **테스트는 고정 `datetime`을 주입한다**: `base: datetime = datetime(2026, 6, 17, tzinfo=UTC)` — 실시각을 읽지 않으므로 어느 날 돌려도 결과가 같다. 호스트가 `USE_TZ = True`면 aware 값(`tzinfo=UTC`)을 쓴다 — naive와 섞으면 비교에서 `TypeError`다.

```python
def test_is_stale_after_7_days_from_base_date() -> None:
    base: datetime = datetime(2026, 6, 17, tzinfo=UTC)          # 고정 주입 — 실시각 무관
    assert forecast(updated_at=base).is_stale(base + timedelta(days=8)) is True
    assert forecast(updated_at=base).is_stale(base + timedelta(days=6)) is False
```

(`freezegun`·`time-machine` 같은 시계 고정 도구는 코드가 실시각을 직접 읽을 때만 의미가 있다. dddjango-web은 그 결합을 만들지 않고 *인자 주입*으로 푼다. 실시각을 꼭 읽어야 하는 BC가 등장하면 그때 재고한다.)

## §6. 외부 주소 이미지 — 조건부

테스트 클라이언트 단언(§4)은 HTML만 받는다 — 이미지를 내려받지 않으므로 이 절과 무관하다. **브라우저 테스트**에서 화면이 외부 주소 이미지(API가 준 원격 URL)를 그리면 그 요청이 실제 네트워크를 탄다 — 느리거나 막히면 결과가 흔들린다(앱 결함 아님). 페이지 이동 전에 그 요청을 고정 응답으로 돌린다:

```python
page.route("https://cdn.example.com/**", lambda route: route.fulfill(status=200, content_type="image/png", body=TINY_PNG))
page.goto(live_server.url + ChannelNavigator.channel_list_href())
```

- `{% static %}` 이미지(시안 이미지 — implementation-django §8)는 미해당이다 — `live_server`가 정적 파일을 같은 출처로 서빙한다. 아이콘이 글꼴 리거처면 미해당이다 — 외부 주소 이미지를 *그리는* 화면에서만 발동하는 일반 함정이다. `TINY_PNG`는 §7 헬퍼.

## §7. 헬퍼 계약 — 단일 정의

영구 시험 헬퍼도 §4의 재현성 계약을 따른다. 호스트 도구 탐색 결과(`shutil.which` 등)는 허용하되 머신 고정 실행파일·캐시 주소를 새로 박지 않는다. G0에서 명령·settings 지정·호스트 필수 환경 출처·레인 추가 변수 이름을 확정하고 G2에서는 레인 추가 변수만 제거한 같은 명령을 실행한다(`env -i` 아님). 바뀐 `tests/` 시험을 실제 수집하는 호스트 명령도 확인하고 skip 수·사유를 실행 통과와 분리해 보고한다.

discipline-test §3 FORM이 쓰는 헬퍼의 *계약*을 여기서 정의한다(이름은 weather 예시 — BC에 맞춰 환언하되 계약은 유지). 같은 헬퍼를 테스트 파일마다 재정의하지 말고 `web_test/application/[<area>/]<bc>/_support.py` 한 곳에 두고 `from web_test.application.[<area>.]<bc>._support import …`로 가져온다 — 실제 BC 경로(area 그루핑이면 area 세그먼트 포함)를 그대로 미러한다(render-smoke 파일도 같은 폴더). `--import-mode=importlib`은 테스트 폴더를 `sys.path`에 넣지 않아 형제 모듈 상대 import가 안 되고, pytest-django가 `manage.py` 폴더를 `sys.path`에 넣으므로 `web_test.` 절대 import가 된다. `_support.py`는 `*_test.py`가 아니라 수집되지 않는다:

| 헬퍼 | 계약(반환·역할) |
|---|---|
| `d(day_offset: int) -> date` | 고정 기준일 + day_offset일 — 정렬 fixture를 *뒤섞어* 만든다(§3.2·실시각 무관 §5). |
| `fc(day: date) -> ForecastSummary` | 도메인 요약 값 빌더 — 순수 도메인 테스트(seam A)의 입력. 더블 아님(값). |
| `detail_state(*, high: int, low: int) -> ForecastDetailState` · `list_state(week: list[ForecastSummary]) -> ForecastListState` | 통제된 State 빌더 — VM 대체(seam B)가 돌려줄 State. |
| `FakeListVM(state)` · `FakeDetailVM(state)` | 화면 VM 자리 — 진짜 VM처럼 view가 생성하고 `build(...)`가 고정 State를 반환(seam B — view 모듈 이름을 `lambda: FakeListVM(state)`로 바꾼다). detail fake의 `build(day)`는 state의 날짜를 *받은(navigated) day로 바꿔* 돌려준다(§3.4 날짜-echo). |
| `get_page(client: Client, url: str) -> BeautifulSoup` · `get_fragment(client: Client, url: str) -> BeautifulSoup` | GET → `status_code == 200` 확인 → HTML 파싱. `get_fragment`는 `HX-Request: true` 헤더를 붙인다(§4). |
| `get_list(client: Client, monkeypatch: pytest.MonkeyPatch, week: list[ForecastSummary]) -> BeautifulSoup` | 목록 VM 대체(week) + 상세 VM 대체(날짜 echo) 뒤 목록 페이지를 받는다. week는 **≥3**(§3.4 `[2]` 전제). |
| `get_detail(client: Client, monkeypatch: pytest.MonkeyPatch, state: ForecastDetailState) -> BeautifulSoup` | 상세 VM 대체(state) 뒤 상세 페이지를 받는다 — 위치 FORM(§3.3). |
| `count_text(root: Tag, text: str) -> int` | `root` 범위 안에서 앞뒤 공백을 뗀 글자가 `text`와 *정확히 같은* 글자 노드 수 — §3.4 범위 안 정확 개수. |
| `format_date(day: date) -> str` · `format_temp(celsius: int) -> str` | 화면 표기와 *동일한* 포맷 — §3.4 날짜-echo·§3.3 기온 정확 일치. **SUT 포맷터를 재사용**한다(별도 포맷을 만들면 디코이). |
| `SCREEN_PROBES: dict[str, ScreenProbe]` (`ScreenProbe: TypeAlias = Callable[[Client, pytest.MonkeyPatch], list[Tag]]`) | **화면 진입점 맵**. role 문자열(`'list'`·`'detail'`…)→그 화면을 *대표 fixture로* 받아 **view 루트 요소 목록**(`[data-testid="<화면>-view"]` 선택 결과)을 반환하는 함수. view·헬퍼·fixture 이름을 전부 *맵 값 안에* 가둬 외부 프로브가 BC 이름에 의존하지 않게 한다 — 화면마다 한 항목, 화면 추가 시 여기 등록. 기존 `get_list`/`get_detail`·`detail_state` 위에 얇게 얹는다(중복 요청 정의 금지). |
| `TINY_PNG: bytes` | 외부 주소 이미지 고정 응답 바이트(§6 — 브라우저 테스트가 있을 때만). |

`SCREEN_PROBES`는 discipline-test §3 FORM이 직접 부르지는 않지만 **별도 render-smoke 테스트 파일(`render_smoke_test.py`)이 직접 소비한다**(아래) — 그 단언이 맵을 돌므로 `SCREEN_PROBES` 미작성·빈 맵이면 green이 깨진다(coder 필수 산출·green 경로 강제). 이 render-smoke는 *헬퍼(`_support.py`)가 아니라 `*_test.py`*라야 pytest가 수집·실행한다. 평가측 렌더 덤프도 이 한 맵만 import해 산출물의 모든 화면을 *배선 추론 0*으로 일관 덤프한다. "모든 화면이 대표 데이터로 렌더된다"는 render-smoke 시드를 겸한다. 키는 화면 role로 고정하고, 값에서 BC별 view·헬퍼 이름을 환언한다(그 이름들이 밖으로 새지 않는 게 핵심):

```python
ScreenProbe: TypeAlias = Callable[[Client, pytest.MonkeyPatch], list[Tag]]  # typing.TypeAlias — 3.11 문법(`type` 문은 3.12부터)

# role → 대표 fixture로 그 화면을 받아 view 루트 요소 목록을 반환. 화면 추가 시 여기 등록.
SCREEN_PROBES: dict[str, ScreenProbe] = {
    "list": lambda client, monkeypatch: get_list(client, monkeypatch, fixture_week()).select('[data-testid="forecast-list-view"]'),
    "detail": lambda client, monkeypatch: get_detail(client, monkeypatch, detail_state(high=28, low=19)).select('[data-testid="forecast-detail-view"]'),
}
```

```python
# web_test/application/[<area>/]<bc>/render_smoke_test.py — 헬퍼가 아니라 *_test.py라야 pytest가 수집한다.
# 단언이 SCREEN_PROBES를 소비해 green 경로로 강제(coder 필수 산출).
import pytest
from django.test import Client

from web_test.application.weather._support import SCREEN_PROBES, ScreenProbe  # area 그루핑이면 web_test.application.<area>.weather._support


def test_screen_probes_registers_screens() -> None:
    assert SCREEN_PROBES  # 빈 맵 도망 차단(빈 parametrize는 실패가 아니라 건너뜀이라 green이 된다)


@pytest.mark.parametrize("role", sorted(SCREEN_PROBES))
def test_renders(role: str, client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    probe: ScreenProbe = SCREEN_PROBES[role]
    assert len(probe(client, monkeypatch)) == 1
```

`SCREEN_PROBES`를 `_support.py`(헬퍼·import 대상)에 정의하고 테스트 함수는 별도 `render_smoke_test.py`에 둔다 — `_support.py`의 함수는 pytest가 수집하지 않는다. **render_smoke는 probe 반환 목록을 *소비*하는 형태(`len(probe(client, monkeypatch)) == 1`)라야 한다** — `probe(…)`를 부르기만 하고 반환을 버린 채 다른 선택자로 단언하면 probe가 아무것도 돌려주지 않아도 green이 통과해 화면 진입점 계약을 깬다. 타입 이름 `ScreenProbe`·반환 `list[Tag]` 고정(`ScreenGetter`·`None` 반환 등 변형 금지).

repo를 갈아끼우는 헬퍼(`FakeRepo` 류)는 만들지 않는다 — dddjango-web엔 repo 주입 자리가 없다(§2). 정렬은 도메인 단위를 직접 호출하므로(discipline-test §3.2) VM 격리 헬퍼가 불요하다.

## §8. 안 쓰는 것 — 스크린샷 비교·외부 E2E 러너·pytest-mock·mutation

- **스크린샷 비교**(Playwright `to_have_screenshot`·픽셀 diff) — **비채택**. 같은 실행·같은 브라우저의 옛 판 ↔ 지금 판 이미지 비교도 비채택이며, 승인 명세나 시험 목록에 있어도 예외가 아니다. 사람 눈 확인용 갈무리는 그대로 유지한다. 시각 충실도는 인간 오라클이 본다(G2 배너). 스크린샷 도구 자체가 폰트·플랫폼 렌더 비결정을 인정(허용 오차·OS별 기준 이미지)하는 점이 생성 파이프라인 결정성과 상충한다.
- **외부 E2E 러너**(Selenium·Cypress) — 주석-제외. 브라우저가 필요한 곳은 pytest-playwright 한 줄기로 *얇게*(정전 = unit 두텁게).
- **pytest-mock**(`mocker`) — 주석-제외. 표준 `unittest.mock`+`monkeypatch`가 같은 일을 설치 없이 한다(§1).
- **mutation**(`mutmut`·`cosmic-ray`) — 이번 회차 비채택(dddart 009 조건부 승계). generic 연산자/불리언 변이라 "두 enum case가 색을 공유" 같은 *도메인 의미* 변이는 생성하지 않고 변이마다 테스트 1회라 느리다 — 색 distinctness는 discipline-test §3.1 집합-크기 FORM이 직접 보장한다.
