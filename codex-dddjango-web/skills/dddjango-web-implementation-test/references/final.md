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
- §8. 안 쓰는 것 — 스크린샷 비교·미디어 재생 자동 시험·외부 E2E 러너·pytest-mock·mutation

---

## §1. 패키지 라인 — 왜 표준 unittest.mock인가

- `pytest`·`pytest-django`(Django 설정 로드·`client`·`live_server`·`db` fixture) — 토대. 실행은 **build-state의 `test_command`** 한 줄이다(web 시험 경로만 · DB 표식으로 단계를 나누는 호스트면 단계마다 `&&` — 단계는 따로 돈다 · `&&` 는 단계 구분 표기다) — Coordinator가 G0 (8)에서 pytest가 settings를 찾는 길(호스트 pytest 설정의 `DJANGO_SETTINGS_MODULE` · 환경변수 · 없으면 `manage.py`의 기본값으로 `--ds=<모듈>`을 붙임)을 확인해 확정하고 coder-web 입력으로 넘긴다(예 `pytest web_test --import-mode=importlib --ds=config.settings`). G2 앞 Coordinator 전수 테스트는 이 명령을 그대로, coder-web 은 결정적 러너 `--test-scope`가 낸 좁힌 실행 줄로 쓴다(줄의 일꾼 지정 — 계층 중 `-n0` · 슬라이스 끝 최대 6(`-n auto`면 `--maxprocesses=6`) — 은 도구가 넣는다 · 어디까지 도는지는 coder-web «층별 green 래칫» · Coordinator «시험 범위») — 명령을 손으로 바꿔 settings 지정 · 표식 · 실행 옵션을 빼거나 다른 settings를 붙이지 않는다. 단계 하나의 exit 5(그 단계 표식에 걸린 시험이 없어 수집 0)는 그 단계 통과로 센다 — 모든 단계가 5면 통과가 아니다(경로 · 파일 이름을 확인해 다시 돈다). importlib 모드는 web 미러 트리의 여러 폴더에 같은 이름 테스트 파일이 있어도 충돌하지 않게 한다(대신 테스트 폴더를 `sys.path`에 넣지 않는다 — §7).
- Django 테스트 클라이언트(`django.test.Client` — Django 번들, 설치 0) — 페이지·조각 요청(§4).
- **더블은 표준 `unittest.mock` + pytest `monkeypatch`**: **추가 설치 0**이라 채택한다. 목 전용 플러그인(`pytest-mock`)을 더하면 같은 일을 하는 두 표기가 생기고 의존이 하나 늘어난다 — 표준 라이브러리만으로 가짜·호출 검증이 된다(§8 pytest-mock 주석-제외).
- `beautifulsoup4`(HTML 단언 — 응답 HTML을 `BeautifulSoup(response.content, "html.parser")`로 읽어 CSS 선택자로 집는다). Django의 `assertContains(…, html=True)`는 요소를 속성까지 통째로 맞춰야 해 클래스 하나만 바뀌어도 깨지고, 범위를 좁혀 개수를 셀 수 없다.
- (조건부) `pytest-playwright`(승인된 UI JS 기능이 있는 화면 · 지속 셸 · 완성 그림 행이 있는 화면 — §4) + 브라우저 설치 `playwright install chromium`. 호스트에 없으면 개발 선언에 고정해 설치한다 — 하위 프로세스 · 직접 띄우기로 우회하지 않는다(§4 «브라우저는 공용 고정물만» · 설치가 안 되면 coder-web 이 멈추고 보고).
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

- **(C) ApiClient 목 (seam C·통합·드물게)** — *실제* VM/UseCase/Repo 스택을 통제된 서버 데이터로 끝까지 돌릴 때만. Repo가 `ChannelDataSource(ApiClient())`를 직접 생성하므로(implementation-django §4) seam은 **ApiClient 계층**이다: 테스트가 `ApiClient`의 호출 메서드를 목으로 바꾼다(§3). 무게중심이 아니다(정전 = unit 두텁게) — 판정은 (A), view는 (B)로 덮고 (C)는 정말 필요한 통합 1~2건에 한정한다. 예외 하나 — 목록·반복 슬롯을 만드는 VM 이 BC·화면마다 사본이면(명세 시험 입장 표의 같은 코드 기준) 사본마다 그 사본 VM 을 진짜로 지나는 시험이 필요하다. 그 시험을 (C)의 view 시험(VM 대체 없이 ApiClient 목)으로 쓰면 «1~2건» 한정 밖이다 — 또는 VM 단위 정확 단언과 (B) view 정확 단언을 짝으로 둔다.

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

- 화면이 서는지 = `status_code == 200` + view 루트(`[data-testid="<화면>-view"]`) 정확히 1 — 화면 행위 시험과 완성 그림 case 가 함께 본다(따로 화면 서기 시험을 두지 않는다).
- **조용한 빈 렌더**: Django 템플릿은 없는 변수를 빈 문자열로 렌더한다(`string_if_invalid` 기본값) — 상태 필드 이름이 틀려도 200이 난다. 슬롯 단언(discipline-test §3.3)이 그 자리를 막는다 — 200만 보고 green으로 두지 않는다.
- **CSRF**: 테스트 클라이언트는 CSRF 검사를 하지 않는다(`enforce_csrf_checks=False` 기본) — POST 테스트에 토큰을 넣지 않아도 된다. 토큰 배선 자체는 implementation-django §6 표기로 지킨다.
- **로그인 화면**: `@login_required` 화면은 `client.force_login(user)`(pytest-django `django_user_model`·`db`) 뒤 요청한다 — 미로그인 GET은 로그인 주소로 302다.

**브라우저 테스트(승인된 UI JS 기능이 있는 화면 · 지속 셸의 root 시험 하나 · 완성 화면 갈무리)**: 파일은 `<화면>_browser_test.py`(web_test 미러). pytest-playwright `page` + pytest-django `live_server`:

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
- **브라우저는 공용 고정물만**: 시험은 pytest-playwright 의 `page`(또는 `context`, 시험마다 `browser.new_context(...)`)만 받는다 — `browser`는 일꾼마다 하나를 함께 쓰고 context · page 는 시험마다 새로 연다. 창 크기 · 시계 · 권한 · 가로채기는 context 단위(`browser_context_args` 덮기 · `new_context(...)` 인자 · `page.clock` · `context.route`)로 정한다. 쓰지 않는 꼴은 다섯이다 — (1) 하위 프로세스로 브라우저 띄우기(`node -e` 글 · `.js`/`.cjs`/`.mjs` 러너의 `chromium.launch` 등 · `npx playwright test`) (2) 시험 · 지원 코드의 직접 띄우기(`browser_type.launch` · `launch_persistent_context` · `connect` · `connect_over_cdp` · `sync_playwright()` · `launch_browser(...)`) (3) 브라우저 실행 파일(`chrome --headless` 등)의 하위 프로세스 · 외부 E2E 러너(Selenium · pyppeteer — §8) (4) 브라우저 단위 고정물의 정의 · 덮기(`playwright` · `browser_type` · `browser` · `launch_browser` · `browser_type_launch_args` · `connect_options`) (5) 이런 고정물 · 도우미 · 러너를 새 시험에서 받거나 부르기. 브라우저 단위 설정(채널 · 띄움 인자)은 프로젝트 시험 설정 몫이라 시험이 정하지 않는다 — 꼭 필요하면 고치지 말고 보고한다. 호스트에 pytest-playwright 가 없어도 우회 꼴로 쓰지 않는다(§1). 이미 있는 시험 파일의 우회 꼴은 그대로 둔다 — 그 파일에 시험을 더하면 새 시험만 공용 고정물로 쓰고, 기존 도우미 클래스 · 함수에는 공용 고정물에서 받은 page · context 를 넘긴다. 백스톱 TG4 가 이번 실행이 늘린 띄움 자리 · 띄우는 시험을 본다.

**완성 화면 갈무리**(명세 `완성 그림:` 행이 있는 화면): 그 화면의 `<화면>_browser_test.py`에 `test_<화면>_render_capture` case 하나를 둔다. 기존 VM 대체 장치로 시안과 같은 State를 준비하고 `page.set_viewport_size({"width": W, "height": H})`로 명세 창을 맞춰 화면을 연다. 화면 루트 정확히 1개와 명세 `상태 단언:` 관찰을 하나도 빼지 않고 `expect(…)` 자동 재시도 단언으로 통과시킨다 — 정확 개수 `to_have_count(n)`·정확 글자 `to_have_text`·고른 속성 `to_have_attribute`·입력 값 `to_have_value`. 시안에 보이는 고른 탭·목록 수·채운 값과 `hx-trigger="load"` 자리마다 채워진 뒤에만 있는 요소를 확인한다. 마지막 단언 뒤 `page.evaluate("document.fonts.ready")` → 바로 `page.screenshot(path=tmp_path / "<화면>-<W>x<H>.png", animations="disabled")` 순서다 — 사이에 다른 동작을 두지 않고 고정 대기로 상태를 대신하지 않는다. 단언 실패면 그림은 없고 case 실패다. 영구 case는 `.dddjango-web/`를 읽거나 쓰지 않는다(시안 경로는 명세 정보, 고정물은 시험 트리 · 출력은 `tmp_path`뿐). G2에서 Coordinator가 같은 러너·settings·실행 옵션(`-n`은 `-n0` — Coordinator «시험 범위»)의 그 case만 `--basetemp=<산출물 폴더>/captures/tmp`로 실행해 결과를 `captures/`로 옮기고 실제 W×H를 확인한다. 상태 통과는 case 통과 때만 배너에 적고, 브라우저 부재·밖 실행 불가면 미실행·검증 대기다. 이 그림은 사람 눈 확인 자료이고 다른 그림과 자동 비교하지 않는다(§8).
- **샌드박스 안 브라우저**: macOS 샌드박스(예: Codex 셸 샌드박스)는 Chrome 시작에 필요한 시스템 서비스를 막아 브라우저가 시작 즉시 죽는다 — 이 환경에서 브라우저 테스트가 섞인 실행은 처음부터 샌드박스 밖에서 돈다(어디서·어떻게는 Coordinator·coder-web의 «브라우저 실행 환경» 규칙). 샌드박스 안에서 돈 실행의 브라우저 시작 실패(`BrowserType.launch: Target page, context or browser has been closed` · 브라우저 프로세스 `SIGABRT`/`SIGTRAP` · `bootstrap_check_in … Permission denied`)는 그것만으로 원인을 정하지 않는다 — 샌드박스 밖에서 다시 돈 결과가 그 테스트의 결과다(밖에서도 실패하면 실제 실패). 같은 실행에서 브라우저 없이 돈 테스트의 결과는 그대로다. 테스트를 건너뛰거나 지우거나 하니스·브라우저 판을 바꿔 우회하지 않는다.

**지속 셸의 root 시험**(브라우저 — implementation-django §2 «지속 셸»): `web_test/root/scaffold/view/root_view_browser_test.py` 하나 — 탭 누름 전 `window.__bar` 를 잡고 누른 뒤 본문 · 주소 · 제목 · `aria-current` 를 기다려 `window.__bar === document.getElementById('root-tab-bar') && window.__bar.isConnected` 참 · **‹뒤로› · ‹앞으로› 뒤에도 같은 단언**(막대 다시 그림 없음) · 같은 주소 부스트에서 `history.length` 불변 · **재탭 ②**(이미 첫 화면 — 서버 요청 0 · `history.length` 불변 · 맨 위 · 입력 글 남음) · 뒤로 직후 탭 · 뒤로 연타 · 화면 안 링크를 요청 중 두 번 누른 뒤 뒤로 · **조각 요청(늦은 `HX-Redirect`) 진행 중 탭 → 끝 = 탭 화면 · 새 문서 0** · **`HX-Location` 후속 GET(늦은 `HX-Redirect`) 진행 중 탭 → 끝 = 탭 화면 · 새 문서 0**(그 기능이 `HX-Location` 을 쓸 때 — 지속 셸 BC 는 쓰지 않는다 · 2.4.0 지킴 시험으로만 남김 · 그 `swap` 에 `swap:` 지연이 있으면 후속 응답이 온 뒤 · 교체 전에 탭 → 새 화면 뒤 OOB 적용 0 · 고른 탭 = 누른 탭) — 조용해진 뒤 주소 = 본문 = 고른 탭 · 게이트로 가는 탭 = 새 문서(`performance.getEntriesByType('navigation')` 가 바뀜). 이 단언들은 그대로 두고, 떠난 화면 보관(지속 셸 판 2.6)에 아래를 더한다:

- 탭 왕복 뒤 쓰던 글 · 펼침 · 스크롤 그대로
- ‹뒤로› · ‹앞으로›로 돌아간 화면 그대로(서버 요청 0)
- 재탭 ① 첫 화면 그대로
- 누른 작업 안에서 고른 탭 class 가 바뀜
- `#root-announce` 글 = 새 제목
- (알림 기능이 있으면) 알림이 탭 이동 뒤에도 남음
- 보관 중 폴링 0 · 돌아오면 다시 돎
- 동작 뒤 같은 출처 이동 = 새 문서 0
- 새로고침 = 주소
- 다른 계정 로그인 뒤 탭 = 그 탭 첫 화면

이 시험의 «서버 요청 0»은 문서·htmx·`fetch` 요청으로 센다 — 미디어 바이트 요청은 세지 않고, 미디어가 있는 화면에서도 미디어 재생 결과를 단언하지 않는다(§8).

처리기 시험(아래)은 그대로다. RootVM 시험에 `first_href` 와 `who` 를 더한다. `who` 는 넷을 본다 — 익명 = `None` · 인증 시 16 자 · 세션 저장만으로는 바뀌지 않음(DB 세션 · 탭 기록 쓰기 뒤 같은 값) · 로그인으로 세션 키가 바뀌면 바뀜 · 서명 쿠키 엔진이면 `None`.

**지속 셸의 root 처리기 시험**(브라우저 없음): `web_test/root/handler/root_request_handler_test.py` — 요청 넷(문서 · 조각 · 부스트 · 복원) × 응답(같은 셸 · 별칭 `data-hx-history-elt` · 다른 판 · 게이트 302 + `Set-Cookie` · 셸 없음 · 주석 속 표지 · `<main>` 없음 · `<main>` 앞 `textarea` · `text/htmlx` · 404 · 500)의 상태(복원 500 은 500 그대로) · `HX-*` · `Location` 지움 · `Set-Cookie` 보존 · `Vary: HX-Request` · `no-store` 와 **탭 기록**을 단언한다. 탭 기록은 실제 탭 페이지 view 로 요청한다(시험 전용 view 를 web 트리에 두지 않는다):

- **동시 요청 흉내**: 처리기가 저장소를 다시 읽기 직전에 `mock.patch` 로 `_stored_tabs` 를 감싸(원래 함수를 부르기 전에) 다른 `SessionStore` 로 더 큰 번호와 다른 탭 기록을 저장소에 적는다 → 작은 번호 부스트: 요청마다 저장이 켜진 설정(`override_settings`)이면 응답 뒤 저장소 값이 그 값 그대로 · 꺼진 설정이면 저장이 일어나지 않음 / 문서 GET 은 그 값의 다른 탭 기록을 지우지 않고 번호를 지움 / 같은 요청에서 `write_tab` 으로 다른 탭을 고침 · 지움 → 응답 뒤 저장소에 그 처분이 남음(늦은 부스트여도).
- **빈 동작 지움**(사본에도 쓰기 목록에도 없는 탭의 `write_tab` 지움 — 요청마다 저장 끈 설정 · 조각 요청): 쓰기 목록이 비어 처리기는 저장소를 다시 읽지 않으므로 `_stored_tabs` 를 감싸서는 다른 요청의 저장을 흉내 낼 수 없다 — 실제 탭 페이지 view 가 부르는 VM 을 `mock.patch` 로 감싼 시험 장치가 **view 안에서** ① 그 요청의 세션 사본을 먼저 읽어 그 탭이 없음을 확인하고 ② 다른 `SessionStore` 로 그 탭 기록을 저장소에 적어 저장한 뒤(다른 요청의 저장 흉내) ③ `write_tab(request, 그 탭, None)` 을 부른다 → 주입 1 · `_stored_tabs` 불림 0(감싸 세기만) · 그 요청의 세션 저장 0(저장소 행의 `session_data` 가 주입 직후와 같음 · 세션 `Set-Cookie` 없음) · 그 탭 기록 남음.
- **자기 탭 기록 뒤 같은 탭 지움**: 저장된 세션 · 사본에 그 탭 없음 · 그 탭 페이지의 문서 GET 과 큰 번호 부스트에서 view 안(VM 감싸기) 또는 응답 쪽 처분 자리에서 `write_tab(request, 그 탭, None)` → 응답 뒤 저장소에 그 탭 기록 없음(문서 이동 셸과 같음). 응답 쪽 처분이 있는 호스트면 그 처분이 `_record_page` 앞에서 불려 저장소 최신 값 위에 남음도 단언한다.
- **세션 끝냄 — 칸마다 따로**: ⓐ 기록 대상 GET 에서 view 가 `logout()`(= `flush()` — 실제 탭 페이지 view 의 VM 을 `mock.patch` 로 감싸 그 안에서 부르게 함 · 쿠키는 바깥 미들웨어가 지움) ⓑ 호스트 꼴 빈 세션 교체(`request.session = SessionStore(None)` + 응답 세션 쿠키 지움 — 그런 처리기 코드가 있는 호스트만 · 객체만 바꾸는 꼴 ⓑ1 과 백엔드 로그아웃이 같은 저장소의 옛 세션 행도 지우는 꼴 ⓑ2 를 따로 — ⓑ2 는 시험 장치가 옛 키의 행을 따로 지운 뒤 교체) ⓒ 저장소 사라짐(감싼 `_stored_tabs` 가 그 세션 행을 지움) → 바깥 `SessionMiddleware` 를 지난 응답(테스트 `Client` 의 응답)에서 새 세션 키 `Set-Cookie` 0 · **추가 세션 행 0**(되살림 0) · ⓐ ⓑ2 ⓒ 는 그 세션 행 0 · ⓑ1 의 옛 행은 그대로(처리기는 지우지도 다시 쓰지도 않음 — 행 수 · `session_data` 가 요청 앞과 같음 · 문서 이동 셸도 같음) · ⓐ ⓑ1 ⓑ2 는 세션 쿠키 지움도 / ⓓ 키는 두고 응답이 세션 쿠키만 지움(문서 GET · 받아들인 부스트) → 끝냄 아님(세션 다시 저장 · 쿠키 다시 달림 · 이 요청의 탭 기록 있음 — 문서 이동 셸과 같음).
- **세션 쿠키 없는 요청 · 만료 쿠키 요청** 각각에서 실제 탭 페이지 GET 이 `write_tab` 으로 다른 탭을 넣었다 지움(종료 없음) → 새 세션에 자기 탭 기록 있음 · 다른 탭 없음 · 같은 두 요청에서 view 가 `flush()` → 세션 0.

**영구 시험 재현성**: `web_test/`·호스트 시험 트리와 시험 지원 코드(`conftest.py`·`_support.py` 등)는 `.dddjango-web/`를 읽거나 쓰지 않고 프로젝트 루트 밖 머신 고정 고정물·기준판·캐시에 기대지 않는다. 기록 폴더(`.dddjango-web/`·`.dddjango/`)에 둔 시험 원문 사본은 영구 시험이 아니다 — 그 사본을 영구 시험으로 옮겨 오면 새 시험으로 본다. 고정물·기대 자료는 시험 트리에, 실행 기록은 `tmp_path` 등 임시 폴더에 둔다. 시험 실행의 `--basetemp` 는 기록 폴더(`.dddjango-web/` · `.dddjango/`) 밖 임시 폴더로 준다 — 하나의 예외는 G2 «완성 화면 그림»의 `captures/tmp`(Coordinator 가 PNG 를 옮긴 뒤 커밋 전에 지운다). 기록 폴더 안 basetemp 는 pytest 가 만드는 `<이름>current` 절대 경로 링크를 기록과 함께 커밋하게 만든다. 선택 도구 부재는 호스트 규칙대로 skip하고 설치된 도구의 고장은 실패로 남긴다. 레인 전용 환경 변수 존재 단언으로 실행 전제를 만들지 않는다 — 정상 환경 변수 행위 시험·필수 settings는 허용하며 환경 변수 의미 판정은 TG2 밖, discipline 감수와 G2 표준 실행이 확인한다.

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

영구 시험 헬퍼도 §4의 재현성 계약을 따른다. 호스트 도구 탐색 결과(`shutil.which` 등)는 허용하되 머신 고정 실행파일·캐시 주소를 새로 박지 않는다. G0에서 명령(web 시험 경로만)·settings 지정·호스트 필수 환경 출처·레인 추가 변수 이름을 확정하고 G2 한 번(Coordinator «시험 범위» — 이 실행이 바꾼 web 시험 경로 밖 시험 파일 포함)은 레인 추가 변수만 제거한 꼴로 돈다(`env -i` 아님). skip 수·사유를 실행 통과와 분리해 보고한다.

discipline-test §3 FORM이 쓰는 헬퍼의 *계약*을 여기서 정의한다(이름은 weather 예시 — BC에 맞춰 환언하되 계약은 유지). 같은 헬퍼를 테스트 파일마다 재정의하지 말고 `web_test/application/[<area>/]<bc>/_support.py` 한 곳에 두고 `from web_test.application.[<area>.]<bc>._support import …`로 가져온다 — 실제 BC 경로(area 그루핑이면 area 세그먼트 포함)를 그대로 미러한다. `--import-mode=importlib`은 테스트 폴더를 `sys.path`에 넣지 않아 형제 모듈 상대 import가 안 되고, pytest-django가 `manage.py` 폴더를 `sys.path`에 넣으므로 `web_test.` 절대 import가 된다. `_support.py`는 `*_test.py`가 아니라 수집되지 않는다:

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
| `TINY_PNG: bytes` | 외부 주소 이미지 고정 응답 바이트(§6 — 브라우저 테스트가 있을 때만). |

**시험 규칙 2.7.1 실행만**(build-state `test_rule`이 `2.7.1`인 실행 — 2.8.0 전에 G1 을 받고 Phase 2 를 잇는 실행 · 새 실행에는 적용하지 않는다): 명세가 적은 화면 진입점 맵과 render-smoke 시험은 이 계약대로 쓴다.

- **타입 별칭** — `_support.py`에 `ScreenProbe: TypeAlias = Callable[[Client, pytest.MonkeyPatch], list[Tag]]`(`typing.TypeAlias` · 이름·반환 고정 — `ScreenGetter`·`None` 반환 등 변형 금지)와 `SCREEN_PROBES: dict[str, ScreenProbe]`(화면 role → 대표 fixture 로 그 화면을 받아 `[data-testid="<화면>-view"]` 선택 결과를 돌려주는 함수 · 기존 요청 헬퍼 위에 얇게 · 중복 요청 정의 금지).
- **반환 소비** — 별도 `render_smoke_test.py`(같은 폴더 · `*_test.py`라야 수집된다)가 `@pytest.mark.parametrize("role", sorted(SCREEN_PROBES))` 로 role 마다 `assert len(SCREEN_PROBES[role](client, monkeypatch)) == 1` — probe 를 부르기만 하고 반환을 버린 채 다른 선택자로 단언하지 않는다.
- **빈 맵 차단** — 같은 파일에 `assert SCREEN_PROBES`(빈 parametrize 는 실패가 아니라 건너뜀이라 green 이 된다).

repo를 갈아끼우는 헬퍼(`FakeRepo` 류)는 만들지 않는다 — dddjango-web엔 repo 주입 자리가 없다(§2). 정렬은 도메인 단위를 직접 호출하므로(discipline-test §3.2) VM 격리 헬퍼가 불요하다.

## §8. 안 쓰는 것 — 스크린샷 비교·미디어 재생 자동 시험·외부 E2E 러너·pytest-mock·mutation

- **스크린샷 비교**(Playwright `to_have_screenshot`·픽셀 diff) — **비채택**. 같은 실행·같은 브라우저의 옛 판 ↔ 지금 판 이미지 비교도 비채택이며, 승인 명세나 시험 목록에 있어도 예외가 아니다. 사람 눈 확인용 갈무리는 그대로 유지한다. 시각 충실도는 인간 오라클이 본다(G2 배너). 스크린샷 도구 자체가 폰트·플랫폼 렌더 비결정을 인정(허용 오차·OS별 기준 이미지)하는 점이 생성 파이프라인 결정성과 상충한다.
- **미디어 재생 자동 시험** — **비채택**. 미디어 요소(`<video>`·`<audio>`·`new Audio()`로 만든 요소)의 재생 동작 — 재생·멈춤·이어 감·소리 켜기/끄기·보관(숨김) 중 멈춤·늦은 재생 완료·재생 취소처럼 재생 상태를 바꾸거나 그 상태에 따라 달라지는 동작(재생 상태에 따라 바뀌는 표시 포함) — 은 자동 시험으로 재지 않는다. 미디어 재생 결과(실행 중 요소 값 `paused`·`readyState`·`currentTime`·`ended`·`muted`·`volume` · `play()`·`pause()`의 결과 · 미디어 이벤트 · 재생 상태에 따라 바뀌는 표시 — 재생 버튼 글·소리 버튼 `aria-pressed` 등 · 대역 시험이면 흉내 낸 `play()`·`pause()`의 호출 기록과 흉내 낸 미디어 이벤트)를 실제 재생으로 재든 대역으로 흉내 내든 같고, 승인 명세나 시험 목록에 있어도 예외가 아니다. 실제 재생 결과는 브라우저 내부 시점과 미디어 준비 상태에 달려 결정적으로 재현되지 않는다(`play()` 직후 `pause()`를 불러도 그 `play()` 약속이 `AbortError`로 거부된다는 보장이 없다). 검증은 **G2 사용자 확인**이다 — 명세 행위 목록의 그 행은 `시험 방법: G2 사용자 확인(미디어) · 화면 <화면> · 차례 <어디서 무엇을 어떤 차례로> · 보여야·들려야 <무엇>` 한 줄(칸 셋)이고, Coordinator 가 G2 배너 «미디어 사용자 확인»으로 올린다. 그 행에 시험이 없는 것은 검증 빼기·오라클 완화가 아니다. 그 동작을 짓는 제품 코드(기능 JS 의 P12 멈춤·이어 감 등)는 그대로 짓는다. Web Audio·플레이어 SDK·iframe 임베드 플레이어의 재생은 이 줄 밖이다(공식 SDK 는 implementation-javascript §7 SDK 행 그대로).
  - **그대로 자동 시험**: State 가 정한 미디어 마크업 값(`src`·`poster`·자동 재생 여부·`muted` 속성 — 템플릿에 고정된 속성은 discipline-test §4) · 미디어 아닌 P12(보관 중 타이머·요청·연결 멈춤) · 미디어 기능 JS 를 포함한 `root:screen-hide`/`root:screen-show` 짝(이벤트가 오는지·리스너 수 — `play`·`pause` 호출과 `paused` 값은 보지 않는다) · 지속 셸 root 시험(§4). 미디어가 있는 화면의 이 시험들과 완성 그림 case 는 미디어 재생 결과·미디어 바이트 요청을 단언하지 않는다(요청 수는 문서·htmx·`fetch` 로 센다 · 자동 재생 화면에 들어가는 root 시험은 미디어 재생 결과를 통과 조건으로 삼지 않는다). 한 행에 재생 관찰과 미디어 아닌 관찰이 섞이면 나누고, 미디어 행에는 미디어 아닌 관찰을 두지 않는다.
  - **붉은 미디어 재생 자동 시험·이미 있던 시험**: 실패한 단언이 미디어 재생 결과에서 갈린 시험(그 결과를 기다리다 넘긴 시간 초과 — `expect`·`wait_for_*`·미디어 이벤트 기다림 — 도 든다)은 어느 모드(기능·수정·리팩토링)·어느 단계(슬라이스 green·슬라이스 0 끝 green·전수 테스트)에서도 반송·새 실패·정지 사유가 아니다 — green 판정에서 빼고 Coordinator 가 G2 배너 «미디어 자동 시험 붉음»(노드 id·화면·실패 단언 원문 · 사용자 확인 권장)으로 올린다. 실패한 단언 뒤에 있어 돌지 못한 미디어 아닌 단언이 있으면 같은 행에 `뒤 단언 미실행 — 미디어 아닌 단언 n개`를 적는다(root 시험·root 처리기 시험이면 ★ · 승인 출처와 상관없이 검증 대기). **이번 실행이 새로 쓴 시험**은 이번 실행의 슬라이스 커밋과 지금 슬라이스의 미커밋 변경이 새로 쓴(기준점 `git_snapshot`에 없던) 시험 함수다 — 슬라이스 0 이 옮기거나 이름을 바꾼 시험·승인된 메서드 자리 대응·검증된 0T 만 바뀐 시험·승인 병합으로 들어온 시험·리팩토링 모드의 시험은 기준점 시험과 같다. 기준점 시험은 이 규칙으로 지우거나 나누지 않는다 — 제품 변경에 맞춘 준비·호출 맞춤은 평소대로 하고, 미디어 재생 관찰을 새로 더하지 않는다. 이번 실행이 새로 쓴 미디어 재생 자동 시험은 지운다(미디어 아닌 단언이 섞였으면 재생 관찰만 지운다) — 이번 실행의 작업을 되돌리는 것이라 약화·삭제가 아니다. 기준점 시험에 미디어 재생 관찰을 새로 더한 바꿈은 그 더함을 되돌린다. 미디어 재생 결과를 단언하는 시험 함수는 `시험 전환:` 행으로 받지 않는다(결과가 흔들려 전환 확인이 서지 않는다).
- **외부 E2E 러너**(Selenium·Cypress·pyppeteer)와 **하위 프로세스 브라우저 시험**(파이썬 시험이 node 스크립트 · 브라우저 실행 파일로 브라우저를 띄우는 꼴) — 주석-제외. 브라우저가 필요한 곳은 pytest-playwright 공용 고정물 한 줄기로 *얇게*(정전 = unit 두텁게 · §4 «브라우저는 공용 고정물만»).
- **pytest-mock**(`mocker`) — 주석-제외. 표준 `unittest.mock`+`monkeypatch`가 같은 일을 설치 없이 한다(§1).
- **mutation**(`mutmut`·`cosmic-ray`) — 이번 회차 비채택(dddart 009 조건부 승계). generic 연산자/불리언 변이라 "두 enum case가 색을 공유" 같은 *도메인 의미* 변이는 생성하지 않고 변이마다 테스트 1회라 느리다 — 색 distinctness는 discipline-test §3.1 집합-크기 FORM이 직접 보장한다.
