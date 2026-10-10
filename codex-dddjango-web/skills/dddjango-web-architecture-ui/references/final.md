# 프레젠테이션 아키텍처 — 3단 규율·라우팅 짝·design_system 사용

> **출처:** 제1 규약(dddart 표준 파일트리, 2026-06-11~12) §3.1·§3.5·§6·§9-10·§9-12·§10-5 ① · dddjango-web 2.0.0 대응 규약(dddart → web).
> 본문 속 `(규약 §N)`은 **출처 표기**이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"와 공유 reference(`undecidable.md`)뿐.

---

## 목차

- §1. 3단의 정의 — 바인딩 1단 + 표현 2단
- §2. view 작성 규율 — VM과 1:1 바인딩 루트
- §3. section·widget 작성 규율 — dumb 표현 조각
- §4. 승격·이동 규칙 — 성장 시 단 이동
- §5. ui_extension — 도메인→UI 매핑의 유일한 자리
- §6. BC 루트 라우팅 짝 — router·navigator 작성·사용
- §7. design_system 사용 — 토큰·컴포넌트·show() 금지
- §8. 크기 연결 — 추출된 크기 토큰을 조각에 잇기

---

## §1. 3단의 정의 — 바인딩 1단 + 표현 2단

presentation_layer의 3단은 크기가 아니라 **VM 보유 / 화면 전속 / 재사용**으로 가른다 (규약 §3.5·§9-10). VM을 부르는 단은 view 하나뿐이고, section·widget은 VM·SharedState의 존재를 모르는 순수 템플릿 조각이다 — humble view를 구조로 보장한다(HaffHaff 실측: view 90%가 Consumer, block 93%·widget 98%가 dumb — 이 암묵 규율의 명문화).

**판별 절차** — 위에서부터 순서대로, 처음 해당하는 것이 답:

| # | 질문 | 답 |
|---|---|---|
| 1 | 자기 상태·로직(VM)이 필요한가? | **view** — 전체 화면이든 임베드 조각이든 삼총사(`_view`·`_vm`·`_state`)로 생성(임베드되는 view는 셸 없는 첫 렌더 `<화면>_embed_fragment`도 갖는다 — §2). 버튼 하나여도 동일(HaffHaff 선례: `chat_request_btn_view`+`_vm`) |
| 2 | 한 화면 전속인가 — 그 화면의 State나 맥락을 아는가? | **section** |
| 3 | BC의 도메인(엔티티·어휘)을 아는가? | 예 → **widget** / 아니오 → `design_system/`(BC 밖 — §7) |

- 갈리는 경계의 판별 신호(승격 신호 vs 불필요 VM 양산, "맥락"의 의미)는 공유 reference `undecidable.md`(`${CLAUDE_PLUGIN_ROOT}/skills/discipline-houserules/references/undecidable.md`) §1·§2 소유. 화면이 **어느 BC에 속하는지**(귀속 tie-break)는 `undecidable.md` §3.
- 3단 판별은 조각 3종에만 적용되고 `ui_extension/`은 판별 밖의 보조 종류다(§5). 파일·클래스 명명 사실은 discipline-houserules §4.

## §2. view 작성 규율 — VM과 1:1 바인딩 루트

view는 VM과 1:1로 바인딩되는 루트다 — view 함수(`<화면>_view.py`)가 요청마다 `<화면>VM`을 만들어 `build(...)`로 State를 받고, view 템플릿(`<화면>_view.html`)이 section·widget·임베드 view 자리를 조립한다 (규약 §3.5).

- **VM 호출은 view에서만 허용**되며, view는 **자기 VM(+필요한 같은 BC SharedState)만** 부른다 — 그 외 VM·SharedState 호출 금지. 타 view(같은 BC든 타 BC든)를 임베드할 수는 있다 — 임베드는 부모 템플릿의 자리 하나 `<div hx-get="{{ state.<자식>_embed_href }}" hx-trigger="load" hx-swap="outerHTML">`다. href는 부모 VM이 자식 BC navigator의 `<화면>_embed_href()`로 받아 State에 싣는다. 자식 view 모듈은 셸 없는 첫 렌더 함수 `<화면>_embed_fragment`를 갖고, 자기 VM의 `build()`로 자기 본문 section을 렌더한다 — 부모는 자식 VM을 부르지 않는다(임베드된 view가 자기 VM을 스스로 부르므로 배치만으로 충분). «조각의 첫 데이터 요청 금지» 규칙의 유일한 예외가 이 임베드 자리(`load` 트리거 하나)다 — 그 view의 첫 렌더를 그 view의 VM이 맡기 때문이다(표기는 implementation-htmx §5·§7). `<화면>_embed_fragment`는 조각 응답 함수 이름 규칙 `<화면>_<조각>_fragment` 안에 든다(NM17 그대로).
- 조회 실패의 오류 분기 처리·액션 에러의 표시 소비 패턴은 architecture-state §4 소유 — view 작성 시 그 정식 예제를 그대로 쓴다.
- 요청 입력(`request.GET`·`request.POST`·경로 인자)의 읽기는 view가 한다 — 값은 VM 메서드 인자로(architecture-state §2).
- VM 없는 정적 view(약관·안내)는 VM·State 없이 허용된다 — 삼총사 대응 검사는 VM 기준이다(사실은 discipline-houserules §4).
- **view 템플릿이 직접 그리는 것은 section·widget include·임베드 view 자리의 조립과, error/loading 분기의 표준 component(§4·design_system)뿐이다** — view 템플릿 안에 목록·상세·빈 상태 마크업을 직접 쓰거나, view `.py` 안에 HTML을 짓는 함수(`format_html`·문자열 조립 류)를 두지 않는다. 분기 화면(목록·상세·빈 상태)은 section으로, 재사용 조각은 widget으로 분리한다 — backstop **NM17**이 view `.py` 안의 주 view 함수·조각 응답 함수 밖 함수를 기계 차단한다.

- **private 필드 전용 타입 Protocol만 동거 허용**: 베이스가 import 해석으로 확정된 `typing.Protocol` 또는 `typing_extensions.Protocol` 하나(두 모듈의 import 별칭 포함)이고 class keyword(`metaclass=` 등)·데코레이터가 없어야 한다. 몸통은 한 개 이상의 값 없는 `AnnAssign`만이며 target은 단순 Name, annotation은 호출·대입식 등 실행식 없는 타입 표기다. `pass`·`...`·docstring·메서드·대입·초깃값·attribute target은 예외 밖이다. 선언 전 재바인딩·조건부 import로 불확정하거나 AST 해석에 실패하면 면제하지 않는다. 소비는 annotation/cast용으로 한정한다.

## §3. section·widget 작성 규율 — dumb 표현 조각

둘 다 VM·SharedState·UseCase를 모르는 템플릿 조각이다(커스텀 템플릿 태그로 부르는 우회 포함 금지) — 데이터는 include의 `with` 인자로, 행위는 State가 준 href(`hx-post`·링크)로 받는다 (규약 §3.5).

| 단 | 받아도 되는 것 | 금지 | 명명 |
|---|---|---|---|
| `section/` — 한 화면 **전속** 구획 | 그 화면의 State·엔티티·href | VM·SharedState 접근 | **소속 화면 접두 필수** (`<화면>…_section.html`) |
| `widget/` — BC 내 **재사용** 부품 | 엔티티·원시값·href | VM·SharedState 접근 + **화면 State 받기 금지** | 파일명에 화면 이름 금지 (`<부품>_widget.html`) |

- section이 화면 State를 받는 것은 정상(전속이니까)이고, widget이 화면 State를 받기 시작하면 section으로 오배치된 것이다(`undecidable.md` §2 신호).
- 접두 규칙의 의미: section의 화면 접두는 "전속"의 선언이고, widget의 화면 이름 금지는 "재사용"의 선언이다 — 이름이 곧 단의 계약을 드러낸다.
- **테스트가 집는 표면은 안정적으로 노출한다 — 식별 속성 짝 규약**: discipline-test §3.3/§3.4 FORM이 슬롯을 `data-testid="temp-high"`로 집고 tile의 도메인 요약을 그 요소에서 읽는다 — 그러므로 *그 마크업을 그리는 view/section/widget 템플릿이* ⓐ 구별돼야 하는 슬롯(최고/최저 기온 등)에 **안정 식별 속성**(`data-testid` — 리터럴·텍스트 내용이 아니라 *역할*을 가리킴)을 부착하고 ⓑ tile은 자신이 받은 도메인 요약(관찰 가능 값)을 **그 요소의 텍스트·속성으로 노출**한다. 식별 속성이 없으면 테스트가 텍스트 위치를 추정하다 디코이가 되거나 약화되므로, 슬롯 식별 속성 부착은 view 작성의 일부다(테스트 FORM은 discipline-test 소유).

## §4. 승격·이동 규칙 — 성장 시 단 이동

성장하면 단을 옮긴다 — 단의 정의를 깨면서 제자리에 머무르지 않는다 (규약 §3.5):

| 신호 | 이동 |
|---|---|
| section이 **두 번째 화면**에서 필요해짐 | 화면 State 의존을 벗겨 **widget으로** |
| section·widget에 자기 상태·로직이 생김 — VM 호출이 필요해짐 | **view+vm 쌍으로 승격**(삼총사 생성). section에 VM 호출이 필요해지는 것은 승격 신호이지 예외가 아니다 |
| BC 어휘 없이도 성립하는 순수 시각 부품이 됨 | **`design_system/component/`로** (§7) |

- 반대 방향 절제: include 인자·href만으로 성립하면 view로 승격하지 않는다 — 불필요한 VM 양산 금지(`undecidable.md` §1).
- 타 BC가 section·widget 템플릿을 직접 include하는 것은 금지 — 부품 재사용은 design_system 승격 경유다(4채널 닫힌 열거는 discipline-houserules §5).

## §5. ui_extension — 도메인→UI 매핑의 유일한 자리

도메인 enum·VO를 UI 값(CSS 클래스·아이콘 이름·라벨)으로 매핑하는 템플릿 필터 모듈의 자리다 (규약 §3.5): 도메인은 django 금지·design_system은 BC 어휘 금지라 **여기가 유일한 자리**다. 단 라벨 *텍스트*는 도메인 유비쿼터스 언어다(architecture-ddd §2) — task가 표시 라벨을 열거하면 그 정본 문자열을 verbatim 따르고(왕복 번역·발명·누락 금지), 도메인 enum이 표시명을 소유하면 여기선 인용한다; 이 필터가 신규로 결정하는 시각값은 CSS 클래스·아이콘이다.

- 필터만 — 템플릿 조각·상태 금지. `<개념>_ui_extension.py` → `register = Library()` + 필터 함수. 전역 등록은 `root_initializer`가 BC 필터 묶음을 한 줄씩 합치고(settings `TEMPLATES` `OPTIONS.builtins`), 템플릿은 `{% load %}` 없이 `{{ order.status|order_status_class }}`로 쓴다.
- 시각 토큰 매핑이 VM·State 필드로 새면 이 "유일한 자리" 규칙이 무너진다 — application_layer의 design_system 참조 금지(사실은 discipline-houserules §5)와 한 몸.
- HaffHaff에는 이 자리가 없어 매핑이 산재했다 — dddjango-web 신설 종류.
- **아이콘 매핑**은 이 필터의 `match`다 — 도메인 enum→Material Symbols 리거처 이름(문자열). 시안의 Material Symbol 이름을 그대로 쓴다(아이콘 대응표·별도 아이콘 패키지 도입은 방언 이탈). 상수 클래스·별도 enum으로 빼지 않는다(필터 모듈만 — NM14). 시안이 FILL축을 쓰면 채움(FILL 1)·윤곽(FILL 0)은 리거처 이름이 아니라 글꼴 변형 축(`font-variation-settings`)을 거는 CSS 클래스로 가른다. **글리프 아이콘 vs 정적 래스터 경계**: 폰트 글리프(Material Symbols 리거처)는 이 필터의 `match`가 매핑하지만, 로고·일러스트 같은 정적 래스터(PNG 등)는 글리프가 아니라 정적 에셋 경로(§7)로 간다 — 둘은 다른 트랙이다(ui_extension은 리거처 이름 전용·래스터 경로는 foundation 토큰·asset-manifest).
- **design-tokens.json 소비**(디자인 출처 동결 시 Coordinator가 `extract_design`로 생성): web의 design-tokens.json에는 아이콘 축이 없다 — 아이콘 이름은 동결 시안 마크업의 Material Symbol 리거처 텍스트를 그대로 옮기고, design-ref 이미지로 충실도를 확인한다 — 완전 1:1은 design-review-ui·인간 오라클이 판정한다. 색 매핑도 여기서 `app_color` foundation 토큰(`var(--color-*)`)을 쓰는 CSS 클래스로 한다(생 색 리터럴 금지 §7) — design-tokens.json `colors`의 신규 색은 architect가 foundation 토큰 추가로 결정한다.

## §6. BC 루트 라우팅 짝 — router·navigator 작성·사용

BC 루트의 두 파일이 라우팅을 분업한다 (규약 §3.1 — 위치·명명 사실은 discipline-houserules §1·§4):

| 파일 | 역할 | 규율 |
|---|---|---|
| `<bc>_router.py` | `urlpatterns`(path 바인딩)·`app_name`을 export — root_router가 include로 조립 | **URL path·name 문자열 리터럴은 이 파일 안에서만**. 같은 파일의 `class <Bc>Routes`(클래스 상수)로 묶는다 |
| `<bc>_navigator.py` | 정적 href 헬퍼(`reverse`) | 일반 이동은 **URL name 참조**(`<Bc>Routes`·`reverse`) — 기본 홈 주소 한 건은 아래 예외, **View import 금지** |

- navigator가 BC 루트(계층 밖)에 있는 이유: presentation에 두면 VM이 호출하는 순간 계층 역류, navigator가 View를 import하면 `VM→navigator→View→VM` import 순환 — BC 루트 + 일반 이동의 이름 참조(기본 홈 주소 한 건은 아래 예외)로 둘 다 해소된다.
- 일반 이동에서 navigator·root_destination_handler는 `<Bc>Routes` 이름 상수를 참조한다. 기본 홈 목적지 한 건은 아래 예외를 따른다. 탭 조립(셸의 탭 목록·탭 href)은 root 소유 — BC는 urlpatterns만 export하고 탭 기록을 모른다. 탭 href는 `RootVM`이 만든다(현재 탭 = 그 탭 첫 화면 · 다른 탭 = 세션 `root.tab_last`의 마지막 경로 — architecture-state §10).
- **기본 홈 주소의 좁은 예외**: 활성 URLconf와 무관하게 반환해야 하는 **프로젝트의 기본 홈 목적지 한 건**만 예외로 둔다. 명세에 소유 BC·router 상수·navigator 메서드를 적고, 그 단일 상수를 소유 navigator가 가공 없이 반환한다. 다른 BC는 그 navigator를 호출한다. 상수 복제·타 BC router 직접 import(IM5)·BC별 기본 주소·개별 화면·조각 주소로의 확대는 금지한다. 나머지 named href의 역참조 실패를 이 주소로 폴백하지 않는다(`NoReverseMatch`를 잡아 아무 주소로 넘기기 금지). URLconf 독립은 href 반환에 URL 이름 등록이 필요 없다는 뜻이며 모든 격리 URLconf에서 그 주소를 GET할 수 있다는 뜻은 아니다.
- **정적 href 헬퍼의 수단**: `reverse()`는 urlconf만 알면 되므로 요청·전역 키가 필요 없다 — VM이 navigator로 href를 얻어 State에 담고, view는 그 href로 redirect하며(HTMX 요청이면 `HX-Redirect` 헤더), 템플릿은 State의 href를 링크·`hx-get`·`hx-post`에 쓴다(템플릿이 URL name을 직접 쓰지 않는다). 덕분에 `HttpRequest` 없는 VM도 navigator를 부를 수 있다(architecture-state §2).
- navigator→router(상수 참조)→view(path 바인딩)는 **같은 BC 안의 합법 import 사슬**이다 — 순환 래칫(CY)은 BC 간 그래프만 본다. 단 Python은 모듈 최상단의 순환 import를 풀지 못한다(`VM→navigator→router→view→VM` 사슬이 첫 import에서 `ImportError`) — navigator는 router를 **href 헬퍼 함수 안에서** import한다(표기는 implementation-django §2). `<Bc>Routes`를 별도 파일로 빼지 않는다(라우트 리터럴의 단일 출처가 우선 — 사슬을 끊겠다고 상수 파일을 신설하는 것은 표준 이탈).
- VM이 화면 전환할 때 navigator 헬퍼를 부르는 것은 계층 역류가 아니다(architecture-state §2). urls 표기법은 implementation-django §2 소유.
- **navigator 공개 메서드·router path 바인딩이 넘기는 인자는 원시 path-param이다** — 도메인 VO를 *인자 타입*으로 받지 않는다. VO를 받으면 navigator/router 파일이 domain을 import해 백스톱 IM21(navigator)·IM22(router) 위반이다. VM이 `vo.to_api_path()`로 `str`을 만들어 넘기고, 수신 view가 `Vo.from_api_path(str)`로 복원한다(carrier 경계·*왜*는 architecture-ddd §3).
- web의 router는 화면 전환 연출을 갖지 않는다 — 전환 연출은 CSS(`--duration-*` 토큰)·HTMX 교체의 일이라 router는 design_system을 참조하지 않는다(§7. 허용 위치 닫힌 열거는 discipline-houserules §5).

## §7. design_system 사용 — 토큰·컴포넌트·show() 금지

design_system은 **BC 어휘도 도메인 어휘도 모르는 시각 요소**의 자리다 (규약 §6·§9-12 — 폴더 구조·입장 판별·참조 가능 위치의 닫힌 열거 사실은 discipline-houserules §1·§5·§6). BC 코드가 그것을 **쓰는** 규율이 이 절이다. 제품 선언이 있으면 토큰·theme·부품 CSS의 한 곳은 그 제품의 한 곳이다(선언이 없으면 기존 평면 한 벌). 재사용 조사는 자기 제품 뿌리와 평면 공용 component 마크업을 대조한다:

- **시각 값은 foundation 토큰만**: BC presentation·root scaffold·component의 템플릿·CSS에서 색 리터럴(`#…`·`rgb(…)`)·생 글자 스타일(`font-size`·`font-family` 리터럴) 금지 — `app_color.css`·`app_typography.css` 등 표준 7토큰(CSS 변수)이 시각 값의 단일 출처다(제품 선언이 있으면 그 제품의 7파일). 매직 넘버 연출 시간도 동일(`--duration-*`·`--easing-*`) — 전환·애니메이션·press 등 *상호작용 연출* 시간은 토큰이며, 시안에 명시값이 없어 연출 시간을 코더가 정해야 해도 생 `200ms`를 CSS에 직접 박지 않고 토큰에 의미값을 두고 인용한다(발명이 아니라 경유). 단 *비시각* duration(네트워크 timeout·디바운스 — `hx-trigger`의 `delay:` 등 화면 연출과 무관한 시간)은 이 규율 밖이고(토큰 강제 아님), 구조적 명명 값(`transparent`·`currentColor`처럼 브랜드 시각값이 아닌 것)도 토큰화 대상이 아니다(무의미 토큰 양산 방지). 크기(글자 크기·아이콘 크기 등)도 눈대중 픽셀 상수가 아니라 `design-tokens.json`이 추출한 값을 인용한다(§8 — 글자 크기는 위 생 글자 스타일 금지에 이미 포함이다). `font-size`는 아이콘 글리프에도 foundation 토큰으로 쓴다. 글리프 크기는 `app_spacing.css`의 `--spacing-icon-*`로 정의하고 `font-size: var(--spacing-icon-*)`로 인용한다. `width`·박스 `height` 등 비-typography 크기는 architecture-ui §8의 추출값 직접 인용 규칙을 따른다.
- **브라우저 기본값·웹폰트도 theme 한 곳에서**(제품 선언이 있으면 그 제품의 한 곳): 브라우저 기본 여백 초기화·웹폰트 `@font-face`·`body`의 글꼴·색 기본값은 `theme/app_theme.css`가 foundation 토큰으로 조립한다 — 화면·부품 CSS가 각자 기본 여백을 지우거나 글꼴을 선언하지 않는다(문서 셸이 한 번 링크한다 — 제품 선언이 있으면 자기 제품 theme만). 다른 제품 테마를 화면 CSS로 덮어 고치지 않는다.
- **정적 이미지·아이콘 경로도 foundation 토큰**: CSS가 쓰는 정적 래스터(배경 로고·일러스트 등)의 경로는 `app_asset.css`의 `--asset-*` 변수에서 온다(제품 선언이 있으면 자기 제품 foundation) — CSS에 raw `url(…)` 경로를 직접 박지 않는다(색 리터럴→`--color-*`와 같은 평행: 경로도 리터럴이 아니라 토큰을 가리킨다). 템플릿 `<img>`의 `src`는 CSS 변수를 쓸 수 없으므로 `{% static 'web/images/…' %}`로 쓰되 경로는 공급 파이프라인의 `local_path`를 그대로 옮긴다 — 시안 원본 URL·눈대중 경로를 박지 않는다. 표준 7토큰의 7번째가 `app_asset`이다(7토큰 닫힌 열거 자체는 discipline-houserules 소관 — 여기는 *사용 절차*만 정한다). 경로 *값*은 공급 파이프라인(`fetch_images`→`asset-manifest.json`→coder가 `local_path` 조인→`web/static/images/`·`app_asset.css`)이 채운다 — 이 절은 *사용*이고 *획득*은 design-architect 명세·implementation-django §8 소관이다.
- **컴포넌트 표시는 view 템플릿이 State로 include한다** — 컴포넌트는 **전역 JS 진입 함수(`window.showDialog(…)` 류)·전역 이벤트 수신으로 스스로를 띄우는 `show()` 경로를 갖지 않는다** (규약 §6 — §10-5 ① 확정). *왜* — 이 문이 열려 있으면 UseCase·VM의 UI 직행(HaffHaff 실측: App 44개 중 36개가 ErrorDialog 직접 호출 — web에서는 서버 코드가 전역 이벤트를 실어 모달을 띄우는 경로)이 재발한다. web에서는 이 대응이 약하다 — 서버 코드는 애초에 브라우저 표시를 직접 부를 수 없고, 남는 문은 전역 JS 진입 함수·전역 이벤트 수신뿐이다. 에러 다이얼로그도 view 템플릿이 그 응답의 State로 include한다(architecture-state §4 정식 예제의 표시 지점 — include 표기는 implementation-django §6 소유).
- **컴포넌트에 인자를 넘기는 두 꼴**: 값 인자(문자열·숫자·State 값)는 `{% include "design_system/component/<군>/<수식>_<군>.html" with … only %}`로 넘긴다. 마크업 인자(dddart의 Widget slot 인자 — `leading:`·`actions:`·`child:` 류)는 부품이 내놓은 이름 붙은 `{% block <자리> %}기본값{% endblock %}`을 쓰는 쪽 조각 템플릿(section·widget·design_system component)이 `{% extends "design_system/component/<군>/<수식>_<군>.html" %}`로 채운다 — Django에서 마크업을 부품의 정해진 자리에 넣는 장치는 block 하나뿐이다. 그 조각 파일은 그 부품의 채워진 사례 하나다(block 밖 내용·두 번째 extends 금지 — 상속 채널 사실은 discipline-houserules §5, 표기는 implementation-django).
- **승격 절차**(§4와 연결): BC 어휘를 벗은 부품은 `component/<부품군>/`으로 — 부품군 폴더=파일 접미사=CSS 클래스 접두의 군, 이름은 무접두(`error_dialog.html`·클래스 `error-dialog` — 종류 접미사가 구별자). 부품 CSS는 부품 템플릿 옆(`<수식>_<군>.css`)에 둔다. 제품 선언이 있으면 승격 자리는 쓰는 문서의 제품 뿌리다 — 평면 공용 마크업을 쓰면 CSS는 자기 제품의 같은 군·같은 이름이다. 분류 안 되는 부품이 생기면 정크드로어(`widget/`·`etc/`)가 아니라 새 부품군 폴더를 만든다.
- 도메인 어휘가 필요한 시각 매핑은 design_system이 아니라 그 BC의 ui_extension(§5)이다 — 방향을 헷갈리면 design_system에 BC 어휘가 스민다.

## §8. 크기 연결 — 추출된 크기 토큰을 조각에 잇기

화면을 3단(§1)으로 분해하는 축은 *상태*다 — 크기가 아니다. 그래서 추출된 시각 크기(아이콘·대형 요소 등)는 묶일 도메인이 없어, 명세에서 각 조각에 직접 잇지 않으면 사라진다. design-architect가 이 연결을 명세에 박고 coder는 그 명세를 집행한다 — 강제는 설계 명세 한 곳에서 닫힌다. 제품 선언이 있으면 크기 토큰 승격·정의도 쓰는 문서의 제품 foundation에서 닫힌다.

- **표적은 추출 트랙**: `design-tokens.json`의 `arbitraryValues` 등 추출 치수 토큰과 비도메인 `typography` 항목이다. 추출기(extract_design)가 정규화한 치수 토큰을 전수한다 — 특정 형식이나 버킷 이름으로 표적을 좁히지 않는다(미세 간격 `gap-`·`p-`·`m-`은 §7 `app_spacing` 소관이라 추출되지 않는다 — 표적 아님). 도메인에 묶인 typography(본문·강조 텍스트 등)는 ui_extension(§5)·토큰이 이미 담당하니 제외 — 시각 눈대중("큰 요소")이 아니라 *기계 추출된 토큰 목록*을 1건씩 본다. 추출된 *typography* 크기 토큰도 전수 표적이되 그 *적용*은 직접 인용이 아니라 `app_typography` 토큰 정의다(아래 '발명이 아니라 인용').
- **전수·빈칸 0**: 추출 토큰을 빠짐없이 채택(어느 조각의 어느 크기 속성에 연결)/기각(왜 안 씀)한다. 추출 토큰 수만큼 항목이 있어야 한다 — 빈칸을 남기면 coder가 그 크기를 흘린다.
- **발명이 아니라 인용**: 새 픽셀을 눈대중으로 만들지 않는다. *비-typography 크기*(`width`·박스 `height`)는 단일 사용처면 추출값을 그 CSS 속성에 직접 인용하고, 여러 조각이 공유하면 foundation 토큰으로 승격해 참조한다(공유 시 토큰 승격이 더 규율적이나 직접 인용도 위반은 아니다). *typography 크기*(글자 크기·행간(`line-height`)·자간(`letter-spacing`))는 단일 사용처여도 `app_typography` 토큰으로 정의해 참조한다 — 기존 토큰을 `font: var(--typography-*)`로 쓴 뒤 같은 규칙에서 `font-size: N`으로 덮는 것은 '직접 인용'이 아니다(생 글자 스타일이 §7 금지이듯, 토큰 위 typography 리터럴도 값의 단일 출처를 우회한다). `font-size`는 아이콘 글리프에도 foundation 토큰으로 쓴다. 글리프 크기는 `app_spacing.css`의 `--spacing-icon-*`로 정의하고 `font-size: var(--spacing-icon-*)`로 인용한다. `width`·박스 `height` 등 비-typography 크기는 architecture-ui §8의 추출값 직접 인용 규칙을 따른다. `--typography-*`는 기존대로 `font` 묶음 값이다. typography는 `app_typography`, 그 밖 크기는 직접 인용/`app_spacing` 승격이다. 미세 간격은 §7 `app_spacing`.
- **형상과 직교**: 이 규율은 *절대 크기*만 다룬다. 요소의 *배치·축*은 코퍼스가 규정하지 않는다 — design-ref 시안이 형상 근거이고 coder가 재현한다(implementation-django §9). 크기='얼마나 큰가', 형상='어떻게 놓이나' — 둘은 직교하며 후자는 코퍼스 밖(시안)이 소유한다.
