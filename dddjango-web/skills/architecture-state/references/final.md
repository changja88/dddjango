# 상태 아키텍처 — ViewModel 3변종·State 계약·생명주기

> **출처:** 제1 규약(dddart 표준 파일트리, 2026-06-11~12) §3.3·§3.6·§8·§9·§10-5 ① · dddart 파이프라인 본설계(2026-06-12) §8 · HaffHaff-App 실물 대조(2026-06-12) · dddjango-web 2.0.0 대응 규약(dddart → web).
> 본문 속 `(규약 §N)`·`(본설계 §N)`은 **출처 표기**(설계 문서의 절 번호)이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"와 공유 reference(`undecidable.md`)뿐.

---

## 목차

- §1. application_layer 지도 — Model 관문 1 + ViewModel 3변종
- §2. ViewModel — 화면 상태의 주인
- §3. State 계약 — 항상 frozen dataclass `*State`
- §4. 에러 2채널 — 조회는 raise, 액션은 error 필드 (정식 예제)
- §5. SharedState — 화면 간 공유 상태
- §6. Service — 헤드리스 ViewModel
- §7. 교차 BC 상태 — SharedState 접근 금지·root 면제
- §8. refresh 채널 처방 — 폐지된 갱신 버스의 대체
- §9. keepAlive — 수명 결정 기준
- §10. 합성 루트의 상태 — root_vm·handler·initializer 동작 규율

---

## §1. application_layer 지도 — Model 관문 1 + ViewModel 3변종

application_layer는 **Model의 관문 하나(`use_case/`)와 ViewModel의 세 변종(`view_model/`·`shared_state/`·`service/`), 그리고 ViewModel이 노출하는 상태 모델(`state/`)**로 구성된다 (규약 §3.3). 세 변종을 가르는 축은 *상태의 수명*과 *구동원* 둘뿐이다:

| 종류 | MVVM 위치 | 상태 | 구동원 | 수명 |
|---|---|---|---|---|
| `use_case/` | Model 관문 | 무상태 | 호출당함 | — |
| `view_model/` | ViewModel | 화면 1개 | View 요청 | 요청 (화면 응답 하나) |
| `shared_state/` | ViewModel (공유) | 화면 N개 공유 | 여러 VM/View | 화면 그룹 (세션) |
| `service/` | ViewModel (헤드리스) | web 전역 | 비화면 이벤트 (Django 시그널·비화면 요청) | 프로세스 전체 (keepAlive) |

의존은 단방향 하나로 고정된다: View → VM·SharedState(·비화면 이벤트 → Service) → UseCase → Repo·infra service. VM·SharedState·Service는 **Model 방향으로는 UseCase만 호출**한다 — Repo/DataSource/SDK 직접 호출 금지. 위임 한 줄짜리 UseCase도 정상이며, 관문의 일관성이 VM→Repo 지름길의 근거가 되지 않는다 (규약 §3.3). UseCase는 VM을 모른다(역방향 금지) — UseCase 자체의 규율(도메인 개념 명명·판정 소유·Either 통과)은 architecture-ddd §8 소유.

application_layer 안의 **수평 협력은 허용**: VM·View가 **같은 BC의** SharedState를 읽고 호출하며, Service가 SharedState를 갱신할 수 있다(타 BC는 §7).

**이 스킬과 architecture-data의 경계** (본설계 §8 — 한 주제 한 소유자): data = 데이터가 web 바깥(백엔드 API)과 어떻게 오가는가 / state(이 스킬) = 들어온 데이터가 web 안에서 화면들 사이에 어떻게 살아 있는가. 판례 ① **캐싱**: 디스크 캐시 층은 web에 없다(data §5), 세션·프로세스 수명 보관 = state — 목적이 같아도 소유자가 다르다. ② **에러**: 서버 에러가 오는 모양(Either 계약·정규화) = data, 그 에러를 State에 담아 표시·소비하는 방식 = state(§4).

파일·폴더·명명·import 매트릭스 사실은 discipline-houserules §1·§4·§5 소유 — 이 문서는 각 종류의 **동작 계약과 결정 절차**를 소유한다.

## §2. ViewModel — 화면 상태의 주인

VM은 화면 1개의 상태 주인이다 (규약 §3.3): view가 요청마다 VM을 만들어 `build(...)`가 State를 반환하고, View 이벤트(요청)를 UseCase 호출로 **번역**하며, 도메인 결과를 화면 State로 **변환**한다. VM의 일은 번역과 변환이다 — 도메인 어휘로 진술되는 판정·계산은 1곳째부터 domain이 기본이며(판정 소유·강등 규칙은 architecture-ddd §5 소유), specification의 평가·조합도 Model(UseCase 이하)에서만 한다.

- **`HttpRequest` 직접 보유 금지** (규약 §3.3·§9-7): 화면 전환은 `<bc>_navigator`(BC 루트) 경유 — VM이 navigator로 href를 얻어 State에 담고 view가 redirect에 쓴다. navigator의 일반 이동은 이름 기반이며 기본 홈 주소 예외는 architecture-ui §6을 따른다 — VM이 호출해도 계층 역류·import 순환이 없다. HaffHaff 실측: `_vm` 77개 중 73개가 이미 준수(BuildContext 비보유).
- **입력 읽기는 View 소유** (규약 §3.3 — §10-5 ① 확정): 요청 입력(`request.GET`·`request.POST`·경로 인자)은 View가 읽고, **값은 VM 메서드 인자로 전달**한다. HaffHaff 실측: 입력 컨트롤러의 VM 보유 0건 — 이미 관례다. (탭 재탭 스크롤톱은 §8 참조.)
- **DI 없음** (규약 §3.3·§9-13): UseCase는 VM 안에서 **직접 생성**한다(`ChannelUseCase()`). **생성자에 의존성을 선택 키워드 인자로 받아 `or Default()` 폴백으로 외부 치환을 허용하는 DI seam은 두지 않는다**(`def __init__(self, use_case: ChannelUseCase | None = None) -> None: self._use_case = use_case or ChannelUseCase()` 형태 — 테스트용이라도). 싱글턴·클라이언트를 위치 인자로 넘기는 직접 생성(`ChannelDataSource(ApiClient())`)은 정당하다 — 테스트는 생성자 주입이 아니라 도메인 직접·VM 직접 생성·api_client 목(`monkeypatch`)으로 한다(implementation-test §2). UseCase·Repo·DataSource는 무상태다 — 상태는 서버·세션·State 모델에만 둔다. 상태 동작이 허용되는 위치의 닫힌 열거는 discipline-houserules §4 소유 — 결정 절차는 단순하다: **상태를 다루는 ViewModel 변종(VM·SharedState·Service, root에선 root_vm·handler)만 상태 동작(State 조립·세션 보관·시그널 수신 연결)을 갖는다.**
- **base VM·공용 헬퍼 없음** (규약 §10-5 ① 확정): 에러 처리·표시 패턴을 상속·믹스인으로 공통화하지 않는다 — 상속은 전 VM을 한 몸으로 묶는 결합 표면이고, AI coder에겐 반복이 더 결정적이다. 패턴은 §4의 정식 예제를 그대로 반복한다(반복>상속 일반 규율은 discipline-cleancode §18 소유).

## §3. State 계약 — 항상 frozen dataclass `*State`

**VM은 도메인 엔티티·패키지 타입을 직노출하지 않고 항상 자기 frozen dataclass `*State`를 노출한다** (규약 §3.3 — §10-5 ① 확정).

- 페이지네이션 객체(Django `Page`) 같은 패키지 타입은 **State의 필드로** 감싼다.
- **액션 전용 VM도 최소 State를 갖는다** — error 필드 1개짜리 State가 최소형이다.
- *왜* — 직노출은 액션 에러를 담을 자리가 없어 전역 다이얼로그 직행을 유발한다(HaffHaff 실측: App 44개 중 36개가 ErrorDialog 직접 호출 — 그 오염 경로의 입구가 State 부재다).
- State는 `application_layer/state/`의 frozen dataclass 모델이고 노출 주체(화면·관심사·기능)와 같은 접두를 쓴다 — 명명·위치 사실은 discipline-houserules §1·§4.
- State에는 **액션 실패 표준 필드** `error: BadRequestResponse | None = None`을 둔다(§4). frozen dataclass 문법 상세는 implementation-python §4 소유.

화면 상태 모델이 domain_layer가 아니라 application_layer에 사는 이유 (규약 §9-4·§9-7): state 파일은 VM·View만 import한다(HaffHaff 사용처 추적 — 도메인 코드 사용 0건) = 화면이 바뀔 때 같이 바뀌는 ViewModel 계층의 소유물이다.

## §4. 에러 2채널 — 조회는 raise, 액션은 error 필드 (정식 예제)

에러 표시는 두 채널뿐이다 (규약 §3.3 — §10-5 ① 확정). 서버 에러가 **오는 모양**(전 실패가 `Either[BadRequestResponse, T]`로 정규화되어 도착)은 architecture-data §2·§3 소유 — 이 절은 도착한 에러를 화면에 **전달하는** 방식이다.

| 채널 | 실패 지점 | 경로 | 표시 |
|---|---|---|---|
| ① 조회(빌드) | `build()` | BadRequestResponse를 **raise** → view(페이지·조각 함수)가 잡아 같은 템플릿을 맥락 `{"load_error": e, "retry_href": <Bc>Navigator.<화면>_<조각>_href(...)}`로 렌더(retry_href는 view가 navigator로 얻는다 — presentation → navigator 허용) | 그 section 템플릿이 자기 루트 요소(같은 `id`)를 유지한 채 그 안의 오류 분기로 — 화면 단위 에러·재시도 (**자동 재시도 없음**이 dddjango-web 확정 — 다시 시도는 사용자가 누르는 `retry_href`의 `hx-get`. 표기는 implementation-htmx §8) |
| ② 액션 | 버튼·제출 등 메서드 (`hx-post`) | State의 표준 필드 `error`(BadRequestResponse 또는 None)에 담는다 | 그 응답 조각이 감지·표시(`is_show` 존중) — error를 세션·SharedState에 남기지 않는다(State는 응답 하나의 수명이라 **응답이 곧 명시 소비 단위**) |

> view·section 템플릿의 오류·로딩 분기는 design_system 컴포넌트(`feedback/error_feedback.html`·조각 요청의 `hx-indicator`가 가리키는 `loading/` 컴포넌트)를 **직접 include**한다 — 에러·로딩·빈 상태 UI를 템플릿 안에 마크업으로 직접 쓰지 않는다(architecture-ui §2 — view `.py` 쪽은 backstop **NM17**). 본문(목록·상세)은 section으로 분리한다. 조회 실패 응답은 공용 `error_feedback.html`을 바로 돌려주지 않고 **그 section 템플릿 자신**이 렌더한다 — 루트 요소(같은 `id`)를 유지하고 그 안에서 `error_feedback.html`을 include하므로 `outerHTML` 교체 대상과 다시 시도 주소가 사라지지 않는다. State에는 `load_error`·`retry_href` 필드를 만들지 않는다(맥락 값이다).

UseCase는 Repo의 Either를 통과·조합하며 새 raise를 만들지 않는다 — 조회 실패를 오류 분기로 넘기는 raise는 **VM의 일**이다 (규약 §3.4).

**정식 예제** — base VM·공용 헬퍼 없이 이 패턴을 그대로 반복한다 (HaffHaff "플래그→listen→표시→리셋" 33파일 관례의 에러 확장). frozen dataclass·VM·HTMX 표기법 상세는 implementation-python §4·implementation-htmx §2 소유:

```python
# application_layer/state/channel_summary_state.py (개념 1차 분할 전 평면 — 성장 규칙은 discipline-houserules §2)
@dataclass(frozen=True, slots=True, kw_only=True)
class ChannelSummaryState:
    channels: tuple[Channel, ...] = ()
    error: BadRequestResponse | None = None  # 액션 실패 표준 필드 — 철자는 HaffHaff 실물(error_type·msg·is_show)


# application_layer/view_model/channel_summary_vm.py
class ChannelSummaryVM:
    def build(self) -> ChannelSummaryState:
        result: Either[BadRequestResponse, list[Channel]] = ChannelUseCase().get_channels()  # 직접 생성 — DI 없음
        match result:
            case Left(value=error):
                raise error  # ① 조회 실패 — view의 오류 분기로
            case Right(value=channels):
                return ChannelSummaryState(channels=tuple(channels))

    def leave_channel(self, channel_id: str) -> ChannelSummaryState:
        result: Either[BadRequestResponse, None] = ChannelUseCase().leave_channel(channel_id)
        match result:
            case Left(value=error):
                return replace(self.build(), error=error)  # ② 액션 실패 — State의 error 필드
            case Right():
                return self.build()  # 성공 — 목록 재조회


# presentation_layer/view/channel_summary_view.py — View 쪽 소비
def channel_summary_view(request: HttpRequest) -> HttpResponse:
    try:
        state: ChannelSummaryState = ChannelSummaryVM().build()
    except BadRequestResponse as error:  # ① 조회 실패 — 같은 템플릿을 load_error·retry_href 맥락으로
        return render(request, "application/channel/presentation_layer/view/channel_summary_view.html",
                      {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, "application/channel/presentation_layer/view/channel_summary_view.html", {"state": state})


def channel_summary_list_fragment(request: HttpRequest) -> HttpResponse:  # hx-get 조각 응답 — retry_href가 가리키는 자리
    try:
        state: ChannelSummaryState = ChannelSummaryVM().build()
    except BadRequestResponse as error:  # ① 조회 실패
        return render(request, "application/channel/presentation_layer/section/channel_summary_list_section.html",
                      {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, "application/channel/presentation_layer/section/channel_summary_list_section.html", {"state": state})


def channel_summary_leave_fragment(request: HttpRequest, channel_id: str) -> HttpResponse:  # hx-post 조각 응답
    try:
        state: ChannelSummaryState = ChannelSummaryVM().leave_channel(channel_id)  # 값은 VM 메서드 인자로
    except BadRequestResponse as error:  # 재조회까지 실패 — ① 채널
        return render(request, "application/channel/presentation_layer/section/channel_summary_list_section.html",
                      {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, "application/channel/presentation_layer/section/channel_summary_list_section.html", {"state": state})
```

```django
{# presentation_layer/view/channel_summary_view.html #}
{% extends "root/scaffold/view/root_view.html" %}
{% block content %}
  {% include "application/channel/presentation_layer/section/channel_summary_list_section.html" with state=state load_error=load_error retry_href=retry_href %}
{% endblock content %}

{# presentation_layer/section/channel_summary_list_section.html — hx-get·hx-post 응답 단위(outerHTML) #}
<section id="channel-summary-list">
  {% if load_error %}
    {# ① 조회 실패 — 루트 요소(같은 id)를 유지한 채 그 안에서 표시 · 다시 시도는 retry_href로 이 조각을 hx-get #}
    {% include "design_system/component/feedback/error_feedback.html" with error=load_error retry_href=retry_href target_id="channel-summary-list" only %}
  {% else %}
    {% if state.error and state.error.is_show %}
      {# ② 표시 — design_system 컴포넌트를 응답이 State로 include (architecture-ui §7, include 표기는 implementation-django §6) #}
      {% include "design_system/component/feedback/error_feedback.html" with error=state.error only %}
    {% endif %}
    {# State는 이 응답 하나의 수명 — error를 세션에 남기지 않으므로 다음 요청에서 다시 표시되지 않는다(명시 소비) #}
    …
  {% endif %}
</section>
```

- `is_show=False`인 에러도 **소비는 한다** — 세션·SharedState에 남겨두면 다음 액션 실패와 구별되지 않는다.
- **조회 전용 화면(액션 메서드 없음)은 채널①만 쓴다** — 실패가 `build()` raise로만 흐르므로 State의 `error` 필드엔 채울 writer가 없다. 필드 선언 자체는 무해하나, **view·section이 `state.error`에 분기(`{% if state.error %}`)를 그리면 어떤 VM도 채우지 않는 도달 불가 死코드**다 — 조회 화면의 에러 표시는 채널①(section 템플릿의 `load_error` 분기)이 전담한다. `state.error` 분기를 그릴 거면 그 State를 쓰는 VM에 채널② writer(액션 메서드의 `replace(…, error=…)`)가 실재해야 한다(읽기 전용 BC가 채널① 위에 채널② 분기를 덧그리는 것이 전형 死채널이다).
- 에러를 시각·카운터 핵으로 위장한 "이벤트 신호"로 바꾸지 않는다 — §5의 과거형 사건명 금지와 같은 축.

## §5. SharedState — 화면 간 공유 상태

한 화면의 변화(좋아요·댓글)를 같은 BC의 다른 화면·조각에 동기화하는 공유 값의 주인이다 (규약 §3.3). 같은 BC의 VM·View가 읽고 호출하며 Service가 갱신할 수 있다(§1 수평 협력). 값의 출처는 서버(UseCase 재조회)·세션이고, 값이 바뀌면 변화를 일으킨 응답이 그 SharedState가 소유한 `HX-Trigger` 이벤트를 실어 그 값을 보여 주는 조각이 다시 요청하게 한다.

- **세션 수명으로 둔다(keepAlive 자리)** — 화면 그룹보다 수명이 길어야 하는데 요청 수명(VM)에 두면 보는 화면이 바뀔 때 상태가 유실된다(HaffHaff `comment_added_bridge` 실측 위험). **+ 명시적 reset**(상태를 초기값으로 되돌리는 공개 메서드)을 둔다 — 규약은 reset의 존재까지 규정하며, 호출 시점은 소유 데이터의 수명을 따라 설계가 정한다.
- **과거형 사건명 금지** (규약 §3.3·§8): `*_added`·`*_completed`·`*_received` 류는 상태로 위장한 이벤트다 — 값이 시각·카운터 핵이 되고, 소비자가 값을 읽지 않고 변화 자체에만 반응하게 된다. 공유 **상태**는 명사 관심사로 짓는다(`<관심사>_shared_state`). 판별 절차·개명 가이드는 공유 reference `undecidable.md`(`${CLAUDE_PLUGIN_ROOT}/skills/discipline-houserules/references/undecidable.md`) §10 소유. 이벤트형 요구가 진짜면 설계 반송 — 도메인 이벤트는 dddjango-web 비채택(규약 §9-15·§10-6 재논의 항목)이며, 그 전까지 shared_state로 위장하지 않는다.
- **일회성 소비가 필요한 상태**(표시 후 사라져야 하는 것)는 §4의 소비와 같은 패턴을 쓴다 — 값을 읽은 소비자가 명시적으로 리셋 메서드를 호출한다. 리셋 없이 "두 번 발화 방지"를 위해 시각 핵·센티널 초기값을 도입하기 시작하면 이벤트 위장의 신호다.

## §6. Service — 헤드리스 ViewModel

View 요청이 아닌 **비화면 이벤트**(Django 시그널 — 로그인·로그아웃 등 · 비화면 요청)를 받아 UseCase를 호출하는 처리다 (규약 §3.3) — 수신 연결(시그널 receiver 등록)은 `root_initializer`가 시동 때 한 번 하고, 그 뒤 프로세스 수명으로 산다(keepAlive 자리). 화면이 없을 뿐 ViewModel 변종이므로 Model 방향 규율(UseCase만 호출)이 동일 적용된다.

- **능동이면 application, 수동이면 infra** (규약 §3.3·§3.4): 이벤트를 받아 유스케이스를 구동하면 `application_layer/service/`, 호출당하는 SDK 어댑터(무상태)면 `infra_layer/service/`(architecture-data §6). HaffHaff drift 실례: `permission_service`가 keepAlive Notifier·App 호출·상태 노출인데 infra에 있었다 — 성격상 application_layer 물건.
- **알림의 분업** (규약 §3.6): 같은 알림이라도 링크 진입(목적지 분배)은 root_destination_handler(§10), 수신 처리(알림 저장 등)는 알림 BC의 service다. BC service에서 redirect·navigator 호출 금지 — 입장 판별 절차는 공유 reference `undecidable.md` §5.

## §7. 교차 BC 상태 — SharedState 접근 금지·root 면제

교차 BC 통신 4채널의 전체 목록(닫힌 열거)은 discipline-houserules §5 소유다. 이 절은 그중 **상태 측면**의 규율만 다룬다 (규약 §9-3):

- **타 BC SharedState 읽기·구독(그 `HX-Trigger` 이벤트 수신) 금지·타 BC VM 호출 금지.** 다른 BC의 데이터·행위가 필요하면 **그 BC의 UseCase를 호출**한다(단발). 반응형으로 "살아 있는" 타 BC 상태가 필요해 보이면 설계를 다시 본다 — 대부분은 ① 그 화면을 view 임베드로 가져오거나(view는 자기 VM을 스스로 부르므로 배치만으로 충분) ② 변화 시점에 자기 BC의 SharedState를 갱신하는 것으로 충분하다.
- **root만 면제** (규약 §3.6): root_vm·root_view·handler는 BC SharedState를 읽을 수 있다 — 뱃지처럼 BC에서 발원하는 반응형 전역 표시 상태의 표준 공급 채널이다(UseCase는 단발 호출이라 반응성이 없다). 면제는 root/ 안에서만이다 — BC끼리는 불가.
- HaffHaff 실측: 교차 BC import 321건이 전부 4채널과 그 위반으로 분류됐고 이벤트형 통지는 0건 — 교차 BC에 이벤트 버스는 필요하지 않았다.

## §8. refresh 채널 처방 — 폐지된 갱신 버스의 대체

HaffHaff의 `refresh_notifier`(8개 BC의 VM 12개를 import해 `ref.refresh`를 조작하는 교차 갱신 버스)와 `scroll_to_top_notifier`(BC 어휘+needTo/complete 플래그의 위장 이벤트)는 **종류째 폐지**됐다 (규약 §8·§9-11). 같은 요구가 오면 처방은 3분기다:

| 요구 | 처방 |
|---|---|
| 데이터가 바뀌어서 다른 화면도 갱신돼야 한다 | **그 BC의 SharedState**(§5) — 변화를 일으킨 쪽이 SharedState를 갱신하고 응답에 그 `HX-Trigger` 이벤트를 싣는다, 갱신이 필요한 화면의 조각이 그 이벤트로 다시 요청한다 |
| 요청·세션 수명(로그인·로그아웃 등)발 갱신 | **root handler → BC service**(§6·§10) — 전역 이벤트의 분배는 root, 도메인 반응은 BC |
| 탭 재탭 스크롤톱 | **root_view가 직접 처리** — BC는 신호를 듣지 않는다(탭 href는 RootVM이 만든다 — §10). 메커니즘은 2단 동작(중첩이면 첫 화면 복귀·루트면 스크롤톱)으로 확정(2026-06-12 §10-5 ④) — 구현 표기는 implementation-django §3 소유 |

공통 원칙: **VM을 바깥에서 조작하지 않는다.** 타 BC·common이 다른 BC 조각의 갱신 이벤트를 발행하거나 그 VM을 직접 부르는 구조는 어떤 명분이든 금지 채널(타 BC VM 접근)의 우회다.

## §9. keepAlive — 수명 결정 기준

이 스킬은 **수명 결정**(어느 변종을 쓰고 언제 세션·프로세스 수명인가)을 소유하고, 세션 보관·시그널 연결 **표기법**은 implementation-htmx §3이 소유한다. web에서 keepAlive는 세션 수명(SharedState)·프로세스 수명(Service·root handler)이다:

| 대상 | 수명 | keepAlive |
|---|---|---|
| VM | 요청 | **아니오** — 요청과 함께 사라진다(요청마다 새로 만든다) |
| SharedState | 화면 그룹 | **예**(세션) + 명시적 reset(§5) — 보는 화면이 바뀌어도 상태 유지 |
| Service | 프로세스 전체 | **예** — 비화면 이벤트는 화면과 무관하게 도착한다 |
| root handler | 프로세스 전체 | **예**(Service 변종 — §10) |

- 결정 절차: "이 상태를 보는 화면이 전부 사라졌을 때 상태가 살아 있어야 하는가?" — 아니오면 VM(기본), 화면 그룹 사이에서 예면 SharedState, 화면과 무관하게 항상이면 Service.
- root_vm의 수명은 규약이 명시하지 않는다 — handler와 달리 명시 결정이 없는 항목이며, 동작 규율은 §10.
- **세션·프로세스 수명 보관을 캐싱 수단으로 쓰는 것은 이 스킬 소관이다** — 디스크 캐시 층은 web에 없다(architecture-data §5). 목적이 같아도 소유자가 다르다(§1 경계).

## §10. 합성 루트의 상태 — root_vm·handler·initializer 동작 규율

root의 위치·폴더 구조·`root_` 접두 사실은 discipline-houserules §1 소유다. 이 절은 root 구성물의 **상태 동작 규율**이다 (규약 §3.6 "root 내부 협력 규칙"):

- **root_vm은 "거의 빈 VM"이다** — 탭·뱃지·점검 안내 같은 web 전역 표시 상태만 갖는다. context processor `root_context`가 요청마다 RootState를 문서 셸에 준다. 탭별 마지막 경로는 `RootRequestHandler.process_view`가 세션 `root.tab_last`에 적어 두므로(dddart `StatefulNavigationShell`의 branch 보유 자리) root_vm은 그보다도 가볍다. **탭 href는 `RootVM`이 만든다** — 현재 탭은 그 탭 첫 화면 href(재탭 = 첫 화면으로 · 이미 첫 화면이면 다시 열려 맨 위로 — dddart 2단 동작), 다른 탭은 세션 `root.tab_last`의 마지막 경로(없으면 첫 화면 — dddart `goBranch`의 마지막 위치 복원). 탭 = 그 view의 URL 네임스페이스 첫 마디(= BC)이고 root의 탭 표가 BC → 탭을 정한다. BC는 탭 기록을 모른다. 특정 도메인 기능이 자라기 시작하면 그 화면은 root가 아니다 — 판별은 공유 reference `undecidable.md` §6.
- **root handler들은 ViewModel의 Service 변종이다**(web에 필요한 이벤트원 handler 수만큼 — 예: 외부 진입 목적지 분배·요청 수명·전역 에러; **개수는 닫힌 목록 아님**) — Django 연결 지점(`MIDDLEWARE`·`handler404`/`handler500`·시그널 receiver)에 등록되어 프로세스 수명으로 산다. 등록은 settings 연결(G0 점검)과 `root_initializer`가 한다.
- **root_initializer는 부수효과만 책임진다**(시그널 receiver 연결·ui_extension 템플릿 필터 조립) — 결과 객체를 반환하지 않는다. 자동로그인 성패·점검 여부 같은 **시동 질문은 root_vm이 요청마다 UseCase를 호출해 직접 획득**한다 — 시동과 요청 사이 간극을 전달이 아니라 재조회로 해소한다(in-process 호출이라 네트워크 비용이 없다).
- **root_router는 plain 모듈 전역 `urlpatterns`다** — 게이트의 상태 확인은 UseCase를 직접 생성·호출한다. DI 없음 덕분에 연결이 필요 없다(HaffHaff redirect의 TokenManager 직행 교정).
- **게이트의 상태 주인**: 게이트 표시 여부는 root_vm이, 게이트 화면 내부 상태는 게이트 자신의 VM(`root_<게이트>_vm`)이 갖는다. 차단 메커니즘은 요청 수명 handler(`root_request_handler` 미들웨어)의 redirect(조각 요청이면 `HX-Redirect`) + scaffold의 게이트 라우트(root_router에 등록) — 셸 밖 라우트·조각 요청까지 덮는다. **게이트의 실행 경계**: `RootRequestHandler`는 `__call__`이 아니라 `process_view(request, view_func, view_args, view_kwargs)`에서 **view 모듈이 `web.`으로 시작할 때만** 게이트·세션 신원 이월·탭 기록을 한다. 같은 프로세스 API 호출이 닿는 백엔드 view(모듈이 `web.` 밖)에는 아무것도 하지 않는다 — 게이트 UseCase가 API를 조회해도 middleware → RootVM → UseCase → Client → middleware 재진입이 끊긴다. 신원 contextvar는 `process_view`에서 set하고 토큰을 `request`에 두었다가 `__call__`의 응답 뒤 reset한다(표기는 implementation-django §2).
- root도 Model 규율 동일 적용: **UseCase만 호출**(Repo·DataSource 직행 금지). BC SharedState 접근 면제는 §7.
