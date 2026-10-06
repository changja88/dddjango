# 대응 규약 — dddart → dddjango-web 2.0.0 (W3 일꾼 공통)

작성: W3 lead · 10-06 03:2x. 이 문서에 없는 것은 **dddart 원문을 그대로 따른다**(절 · 순서 · 문장 · 게이트 · 배너). 바꾸는 것은 Flutter/Dart 낱말 · 예시 · 명령뿐이다. 이 문서와 dddart 가 부딪히면 이 문서가 이긴다.

## 0. 범위
- 넣지 않는다: 빚 정리(빚 스캔 · 슬라이스 0 · debt.py · subst.py) · 외부 JS 승인 절차(sdk_vendor · sdk_registry · check_vendor · sdk_boundary.js · G1 SDK 문항) · 리팩토링 입구. 빈 절 · 스텁도 만들지 않는다(2.1.0 에서 끼운다 — 자리를 막는 문장만 쓰지 않으면 된다).
- 빼는 것: riverpod · hive · codegen(build_runner) · icon_map · apk 빌드 · extract_layout · 지금 web 판의 시안 기계 검사 전부 · 정확값 토큰 규칙 · 시각 연결표 · REQUEST_GUIDE.

## 1. 이름
| dddart | dddjango-web |
|---|---|
| 플러그인 `dddart` · `/dddart` | `dddjango-web` · `/dddjango-web:dddjango-web` · 버전 2.0.0 |
| `commands/dddart.md` | `commands/dddjango-web.md` |
| 에이전트 `coder` · `design-architect` · `design-review-ddd/ui/state/data` · `discipline-reviewer` | 같은 이름 + `-web` (예 `coder-web` · `design-review-ddd-web`). 호출 표기 `dddjango-web:<이름>` |
| 스킬 architecture-ddd/ui/state/data · discipline-cleancode · discipline-houserules · discipline-test · implementation-test | 같은 이름 |
| implementation-dart / -flutter / -riverpod | implementation-python / implementation-django / implementation-htmx |
| (없음) | implementation-javascript (지금 web 판 것을 바탕 — JS 작성 규칙) |
| `.dddart/` 산출물 폴더 | `.dddjango-web/` |
| `dart run ${CLAUDE_PLUGIN_ROOT}/scripts/X.dart` | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/X.py` |
| Codex: 역할 스킬 `dddart-<역할>` · 충돌 4종 `dddart-<스킬>` | 역할 스킬 `dddjango-web-<역할>-web`(지금 Codex web 판과 같음) · **지식 스킬 12종 전부 `dddjango-web-<스킬>`**(dddart · dddjango Codex 판과 이름이 겹쳐서 — codex-dddart README 의 충돌 회피 규칙을 전부에 적용). Coordinator 스킬 `dddjango-web` |

## 2. 기술 낱말 대응
| dddart | web |
|---|---|
| Flutter 프로젝트 · 앱 | Django 프로젝트 · web |
| `lib/` · `test/` | `web/` · `web_test/`(프로젝트 뿌리의 형제 — 뿌리 `test/` 는 백엔드 `application/` 트리와 헷갈려서) |
| `main.dart` | `web/apps.py`(`WebConfig.ready()` 가 root_initializer 만 부름) + `web/urls.py`(root_router 의 urlpatterns 를 내보내는 한 줄) — Django 가 정한 자리 |
| 위젯 · ConsumerWidget | Django 템플릿 + CSS · view 함수 |
| go_router `GoRoute` · `GoRouter` | `path()` · `urlpatterns`(`app_name` 네임스페이스) |
| `<Bc>Routes` 상수 | `<bc>_router.py` 안 `class <Bc>Routes`(URL name 상수) — 경로 · name 리터럴은 router 파일에만 |
| navigator push | `<bc>_navigator.py` 의 `reverse()` 헬퍼 — VM 이 href 를 State 에 담고, view 가 redirect 에 쓴다. 템플릿은 URL name 을 직접 쓰지 않고 State 의 href 를 쓴다 |
| riverpod VM `build()` · `ref.watch` | 요청마다 view 가 `<화면>VM` 을 만들어 `build(...) -> <화면>State` · 갱신은 HTMX 부분 교체(조각 응답) |
| SharedState(keepAlive + reset) | 같은 BC 화면 · 조각 사이 공유 값 — 값의 출처는 서버(API)·세션, 바뀌면 응답 `HX-Trigger` 이벤트로 그 값을 보여 주는 조각이 다시 요청 · reset 메서드 유지 |
| Service(헤드리스 VM · keepAlive) | 화면 요청이 아닌 이벤트(Django 시그널 · 비화면 요청)를 받아 UseCase 를 부르는 처리 — 연결은 root_initializer |
| AsyncValue loading/error | 첫 렌더 · `hx-indicator` / 조회 실패는 예외 → 오류 조각(에러 2채널 그대로) |
| freezed · copyWith · union | `@dataclass(frozen=True, slots=True, kw_only=True)` · `dataclasses.replace` · `A \| B` + `match` |
| json_serializable fromJson | 모델의 `from_json(cls, data) -> Self` 클래스메서드 하나 — 누락 · 타입 불일치는 그대로 예외(조용한 기본값 · try/except 금지) |
| dartz Either | `web/common/util/either.py` 의 `Left` · `Right`(frozen dataclass) · `Either = Left[L] \| Right[R]` |
| dio · retrofit · DioClient · safeApiCall · DioException | `web/common/network/api_client.py`(in-process `django.test.Client(raise_request_exception=False)` — 매 호출 생성 · 세션 쿠키는 contextvar 에서) · `safe_api_call.py` · 실패 종류(상태코드 · JSON 파싱 · 예외) · `bad_request_response.py` |
| 세션 신원 이월(dio 인터셉터 자리) | `root/handler/root_request_handler.py` 미들웨어가 요청 세션 키를 common/network 의 contextvar 에 심는다(common 은 BC · root 를 모름 — 콜백 주입 원칙 그대로) |
| hive · local_storage · common/local_database | 뺌 |
| `Image.asset` · `assets/images/` · pubspec assets | `<img src="{% static 'web/images/…' %}">` · `web/static/images/`(fetch 도구 · asset-manifest local_path 그대로) |
| `Icons.*` · icon_map | material-symbols 글꼴 리거처 이름 그대로 |
| AppColor 등 foundation 7 클래스 | CSS 변수 파일 7 — 아래 §3 |
| ui_extension(Dart extension) | Python 모듈 — Django 템플릿 필터(`register = Library()`) · 도메인 값 → CSS 클래스 · 아이콘 이름 · 라벨. 전역 등록은 `root_initializer.py` 가 BC 필터 묶음을 한 줄씩 합침(dddart 의 hive 어댑터 조립 1줄 자리) · settings `TEMPLATES OPTIONS builtins` 에 `web.root.initializer.root_initializer` |
| `flutter analyze` 기준선 | `python -m py_compile` + `python manage.py check` 기준선(+ ruff 가 있으면 ruff) — 기준선 대비 신규 0 |
| 국소 `analysis_options.yaml` | 국소 `ruff.toml`(생성 영역 루트마다 — ANN 등 타입 명시 규칙 · 호스트 루트 설정 수정 금지 · ruff 가 없으면 G0 고지) |
| `flutter test` · 위젯 테스트 · render-smoke | `pytest web_test`(pytest + pytest-django · Django 테스트 클라이언트 · HTMX 요청은 `HX-Request: true` 헤더) · 화면이 서는지 테스트 = 페이지 · 조각 GET 200 + 핵심 요소 · JS 동작은 브라우저 테스트(pytest-playwright — JS 기능이 있을 때만) |
| mocktail · ProviderContainer.test | `unittest.mock` / pytest `monkeypatch` · VM 직접 생성 |
| `flutter run -d <기기>` | `python manage.py runserver` + 브라우저 |
| 빌드(apk) · codegen 재생성 확인 | 뺌 — G2 직전 `pytest web_test` 전수 + `manage.py check` |
| `flutter pub add`(무핀 → 실버전 핀) | Python: 호스트 requirements 선언에 버전 고정 추가 · 외부 JS: 공식 배포 파일을 `web/static/vendor/<라이브러리>/<버전>/<파일>` 로 내려받아 고정(명세가 고른 것만 · CDN 실행 태그 금지). htmx 는 `web/static/htmx/htmx.min.js` 2.0.10 고정 판(Coordinator 가 G0 에 설치) |
| `analysis_options` exclude 점검(G0) | Django 연결 설정 점검 + htmx 고정 판 받기(아래 §5) |

## 3. 표준 트리(`lib/` → `web/` 1:1)
```
web/                                   # Django 앱 "web" (= lib/)
├── __init__.py · apps.py · urls.py    # main.dart 자리 (Django 고정 자리)
├── root/
│   ├── router/root_router.py          # 전 BC <bc>_router 합산 (urlpatterns · BC 네임스페이스 include)
│   ├── scaffold/
│   │   ├── view/root_view.html        # 모든 페이지가 extends 하는 문서 셸(탭 · 내비 프레임) · 게이트 화면은 root_<게이트>_view.py/.html
│   │   ├── view_model/root_vm.py      # "거의 빈 VM" — context processor root_context(request) 가 RootState 를 셸에 줌
│   │   └── state/root_state.py
│   ├── handler/                       # root_<이벤트원>_handler.py — 예: root_error_handler(handler404/500) · root_request_handler(미들웨어) · root_destination_handler(외부 진입 URL → BC)
│   └── initializer/root_initializer.py  # 시동 + ui_extension 필터 조립 (settings builtins 대상)
├── application/[<area>/]<bc>/
│   ├── <bc>_router.py · <bc>_navigator.py
│   ├── domain_layer/<aggregate>/<aggregate>.py · entity/ · value_object/ · enum/ · domain_service/ · specification/ · exception.py   # 순수 Python — django 금지
│   ├── application_layer/use_case/ · view_model/ · state/ · shared_state/ · service/
│   ├── infra_layer/data_source/ · repository/ · service/
│   └── presentation_layer/view/ · section/ · widget/ · ui_extension/
├── common/enum/ · network/ · service/ · util/          # local_database 뺌 (hive 짝)
└── design_system/
    ├── foundation/app_color.css · app_typography.css · app_spacing.css · app_radius.css · app_shadow.css · app_duration.css · app_asset.css
    ├── theme/app_theme.css            # foundation → 문서 전역 기본값: 브라우저 기본 여백 초기화 · 웹폰트 @font-face · body 글꼴/색 (light/dark 확장점)
    ├── component/<군>/<수식>_<군>.html + <수식>_<군>.css   # 부품 CSS 는 부품 템플릿 옆
    └── util/                          # 시각 동작 헬퍼 CSS (미디어쿼리 · 스크롤 동작)
web/static/                            # Django 정적 자리 (.py 와 섞이면 .py 가 정적 파일로 나가서 따로 둠)
├── application/[<area>/]<bc>/<조각 stem>.css   # presentation 조각 CSS — 템플릿과 같은 stem · sparse
├── root/<조각 stem>.css                      # root scaffold 조각 CSS — 템플릿과 같은 stem · sparse (03:50 lead 추가)
├── js/<기능>.js                       # 승인된 UI 동작 JS — 기능당 한 파일 (implementation-javascript)
├── htmx/htmx.min.js                   # 2.0.10 고정
├── vendor/<라이브러리>/<버전>/<파일>    # 명세가 고른 외부 JS 고정 사본 (필요할 때만)
├── images/ · fonts/                   # 시안 이미지 · 웹폰트 (필요할 때만)
web_test/                              # web/ 1:1 미러 · sparse · <sut>_test.py · 브라우저 테스트 <화면>_browser_test.py
```
- 골격 완비 · area · 성장(개념 1차 · 종류 2차) · BC 루트 직속 둘(+ ruff.toml) 규칙은 dddart 그대로.
- 빈 폴더 표지: `web/` 아래 Python 경로(design_system · static 제외)는 전부 `__init__.py`(빈 폴더 표지 겸) · design_system · static 의 빈 폴더는 `.gitkeep`.
- 템플릿 이름: settings `TEMPLATES DIRS` 에 `web/` 뿌리 → 예 `application/order/presentation_layer/view/order_list_view.html`.
- import 는 `web.` 로 시작하는 절대 경로만(상대 import 금지). 백엔드 `application.` · `framework.` import 0.
- 페이지 템플릿의 `{% extends %}` 대상은 `root/scaffold/view/root_view.html` 하나 — BC 가 root 를 아는 유일한 예외(Django 템플릿 상속 방향이 Flutter 셸 임베드와 반대라서). 그 밖에 root 를 아는 곳은 `web/apps.py` · `web/urls.py` · 호스트 settings(문자열 경로)뿐.
- design_system import 허용 자리(닫힌 열거)는 dddart 그대로 옮김: 템플릿 `{% include %}` · CSS 참조가 허용되는 곳 = presentation_layer 전체 · root/scaffold · design_system 내부.

## 4. 명명(dddart §4 를 옮김 — 다른 줄만)
| 위치 | 파일 | 주 선언 |
|---|---|---|
| BC 라우터 · 내비게이터 | `<bc>_router.py` · `<bc>_navigator.py` | `urlpatterns` + `app_name` + `class <Bc>Routes` · `class <Bc>Navigator` |
| root | `root_router.py` · `root_view.html` · `root_vm.py` · `root_state.py` · `root_<이벤트원>_handler.py` · `root_initializer.py` | `RootVM` · `RootState` · `Root<이벤트원>Handler` · `RootInitializer` |
| view | `<화면>_view.py` + `<화면>_view.html` | 함수 `<화면>_view` (+ 같은 화면의 조각 응답 함수 `<화면>_<조각>_fragment`) |
| view_model · state | `<화면>_vm.py` · `<화면>_state.py` | `<화면>VM` · `<화면>State` (삼총사 VM 기준 · `_view_vm` · `_view_state` 금지 — dddart 그대로) |
| section · widget | `<화면>…_section.html` · `<부품>_widget.html` | — |
| ui_extension | `<개념>_ui_extension.py` | `register = Library()` + 필터 함수 |
| 그 밖 Python | dddart 표의 `.dart` → `.py` (예 `<개념>_use_case.py` → `<개념>UseCase`, `<개념>_repo.py` → `<개념>Repo`, `<개념>_data_source.py` → `<개념>DataSource`) | 파일명 = 주 클래스명 snake_case |
| foundation 변수 | 파일별 접두 `--color-*` · `--typography-*`(`font` 줄임 묶음 값 — 쓰는 쪽 `font: var(--typography-title)` · 그 뒤 같은 규칙에서 font-* 재선언 금지) · `--spacing-*` · `--radius-*` · `--shadow-*` · `--duration-*`/`--easing-*` · `--asset-*` | |
| component | `component/<군>/<수식>_<군>.html` · `.css` | 군 폴더 = 파일 접미사 · CSS 클래스 접두 `<수식>-<군>` |
| 테스트 | `web_test/<web 와 같은 경로>/<sut>_test.py` | |

토큰 규칙은 dddart 그대로: 색 · 글자 스타일 · 연출 시간 리터럴 금지(presentation · root scaffold · component) · 한 곳에서만 쓰는 비-typography 크기(width · height · 아이콘 크기)는 추출값 숫자 그대로 허용 · 크기 전수 연결(산문 · 빈칸 0) · 신규 색은 architect 가 토큰 추가.

## 5. Coordinator G0 의 Django 연결 설정 점검(dddart analysis_options 고지 자리)
(1) `INSTALLED_APPS` 에 `"web"` (2) `TEMPLATES` — `DIRS` 에 `web/` 뿌리 · `OPTIONS.builtins` 에 `web.root.initializer.root_initializer` · `context_processors` 에 `web.root.scaffold.view_model.root_vm.root_context` (3) `STATICFILES_DIRS` 접두 튜플 `("design_system", web/design_system)` · `("web", web/static)` (4) 루트 urls 에 `include("web.urls")` · `handler404`/`handler500` → root_error_handler (5) `MIDDLEWARE` 에 `web.root.handler.root_request_handler.RootRequestHandler` (6) `ALLOWED_HOSTS` 에 `"testserver"` (7) htmx core `web/static/htmx/htmx.min.js` 2.0.10 — 없으면 `curl -fsSL https://unpkg.com/htmx.org@2.0.10/dist/htmx.min.js` 로 설치 · 기존 `web/static/js/htmx*.js` 는 그대로 소비 (8) 테스트 도구 pytest · pytest-django(없으면 coder 가 requirements 에 고정 추가). 미비는 G0 배너에 표면화 · 승인 · 실제 적용은 기존 web/ 이 있으면 G0 승인 직후, 첫 실행이면 Phase 2 진입 준비(골격 뒤). 지금 web 판 Coordinator Phase 0 step 1 ② 문장을 바탕으로 쓴다.
- 경계 새 줄: **백엔드 코드(`application/` · `framework/` · `<project>/` 의 settings · urls 연결 밖)는 고치지 않는다** — 필요한 API 가 없으면 가정 계약으로 짓고(dddart 그대로) 실제 API 는 `/dddjango` 로 요청하라고 안내한다.

## 6. 백스톱 — `scripts/backstop.py`
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all] [--only st,im,nm,cy,tg,pj,md,pu|<검사ID>…] [--update-baseline]
```
- 종료 0 깨끗 · 1 사용/내부 오류 · 2 blocker. 게이트 의미론 dddart 그대로(구조 · 명명 = added · import = touched 의 added 줄 · 골격 = 신규 단위 · 순환 = 전역 + 베이스라인 `.dddjango-web/backstop-baseline.json`).
- 패밀리: ST 구조 · IM import · NM 명명 · CY 순환 · TG 테스트 존재(`web_test/` 미러에 `*_test.py`) · PJ 토대(dddart 의 riverpod 토대 자리 → web 토대: 테스트 도구 선언 · htmx 단일 설치 등 — scripts 일꾼이 정함) · MD 모델 형태(frozen dataclass · from_json 형태) · PU 출력 안전(지금 web `check_purity.py` WP — JS 순수성 · 템플릿 출력 · 인라인 스크립트 · CDN 실행 태그). RV · HV 뺌.
- 번호는 dddart 번호를 그대로 쓰고(뜻이 옮겨지는 것), 옮길 수 없는 번호는 비워 두며(재번호 금지), 새 검사는 패밀리 끝 번호 뒤에 붙인다. 최종 검사 수와 목록은 scripts 일꾼이 `backstop.py` 머리와 `build-log` 에 적는다 — Coordinator 문면의 «검사 N종» 은 lead 가 마지막에 채운다(일꾼은 `<N>` 그대로 둔다).
- 추출 도구 4: 지금 web 판 `extract_contract.py` · `extract_design.py` · `extract_dc.py` · `fetch_images.py` 의 CLI 를 그대로 쓴다(Coordinator 문면은 그 CLI 에 맞춘다 — `--icon-map` 뺌).

## 7. 일꾼 공통 금지(지시서 그대로)
- 출력은 `<S>/web-new/` 아래 자기 소유 파일만. 저장소(`/Users/hyun/Desktop/dddjango/**` · `/Users/hyun/Desktop/dddart/**`)는 읽기만. git 은 `GIT_OPTIONAL_LOCKS=0` 붙인 읽기 명령(log · show · diff · archive · ls-tree)만 · `git status` 금지 · 커밋 · 배포 금지.
- 열지 않는 곳: `<S>/rq-p0/**` · `<S>/rq-p0r/**` · `<S>/p0-ops/**` · `<S>/web-discard-1006/**` · `~/.dddjango-testbed/**` · 하네스 tool-results 파일 · 서브에이전트 output JSONL. `~/.claude/settings.json` · `.claude/settings.local.json` · `~/.codex/config.toml` 은 열거나 고치지 않는다. spring_dream_server · `~/.herdr/worktrees/**` 는 읽기만.
- Serena · Graphify 쓰지 않음. 검토 바퀴 · 안전 도구 · 채점 도구 · 판정기를 새로 만들지 않음. 하위 에이전트를 띄우지 않음.
- md 파일은 Write/Edit 로만(셸 heredoc 금지). 시각은 `date` 출력만, 어림은 [추정].
- 끝나면 자기 파일 목록 · 바이트 · dddart 와 어쩔 수 없이 달라진 곳(까닭 한 줄씩)을 보고에 담는다.

## 8. 2.2.0 에서 dddart 와 달라진 것(이 문서는 2.0.0 대응 규약 — 덧)
- 백스톱 실행 시점: dddart 는 G2 직전 한 번이다. dddjango-web 2.2.0 은 슬라이스가 끝날 때마다 `backstop.py … --slice-end` 로 먼저 돌고(뒤 슬라이스가 채울 검사 일곱 CY1 · NM4 · NM5 · NM18 · NM19 · ST4 · TG1 은 미룸) G2 직전에 84종을 전부 돈다. 게이트 의미론(added · added 줄 · 신규 단위 · 순환 래칫)은 그대로다. 스펙: `plan-2.2.0.md`.
