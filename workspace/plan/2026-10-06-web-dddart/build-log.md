# W3 짓기 기록 — dddjango-web 2.0.0 (dddart화)

- 시작 03:10:34 · 마지막 검증 04:16:12 · 기록 닫음 04:18:16 (모두 `date` 출력 · 10-06 KST) · 걸린 시간 1시간 8분
- 지시서 `web-new/brief-W3.md` · 대응 규약 `web-new/mapping.md`(lead 작성 — 트리 · 이름 · 낱말 대응 · 검사 패밀리)
- 원본: dddart HEAD `737d42b`(`/Users/hyun/Desktop/dddart/dddart` · `codex-dddart`) · 지금 web 판 HEAD `0cdb10f5` v1.3.1(`web-new/head/` 에 `git archive` 로 풂 — 바탕 자료 · 읽기만)
- 산출: `web-new/dddjango-web/`(Claude 판 56 파일 860,188 B) · `web-new/codex-dddjango-web/`(Codex 판 54 파일 828,554 B) · `web-new/release-prep/`(배포 준비 초안 — 운영자 추가 요구)
- 저장소 파일 · git 쓰기 · 커밋 · 배포 없음. Serena · Graphify 쓰지 않음.

## 1. 범위 변경(운영자 메시지)
- 03:1x(사용자 원문 «그럼 우선 추가한 셋을 빼고 진행해서 배포 하고 추가 작업을해서 다시 패호하는 방식으로 계획세워»): 빚 정리 · 외부 JS 승인 절차 · 리팩토링 입구는 1차(2.0.0)에서 뺌 → 2차(2.1.0). 외부 JS 는 dddart `flutter pub add` 자리처럼 coder 가 버전 고정 파일을 static 에 들임 · htmx 고정 판 그대로. 그 메시지가 왔을 때 일꾼을 띄우기 전이었다 — 멈출 일꾼 없음 · `web-new/later/` 로 옮길 산출물 없음(빈 폴더). 빈 절 · 스텁은 만들지 않았다.
- 03:2x: 동시 일꾼 5 까지 · 한 번에 기동 · 대응 규약은 짧게.
- 03:3x: Codex 판 시안 입력을 Claude 판과 같게(로컬 시안 폴더 · extract_dc) · Codex 스킬 이름 접두(겹침 0 확인 목록).
- 03:4x: 일꾼 ⑥ 추가(배포 준비 초안 · 동시 6).

## 2. 일꾼 배치
| # | 소유 | 원본 | 기동 → 끝 |
|---|---|---|---|
| ① | `commands/dddjango-web.md` · `agents/*-web.md` 7 | dddart `commands/dddart.md` · `agents/*.md` | 03:22 → 03:42:07 |
| ② | `skills/` discipline-houserules · architecture-ddd/ui/state/data | dddart 같은 이름 | 03:22 → 03:46:24 |
| ③ | `skills/` discipline-test · implementation-test/python/django/htmx/javascript · discipline-cleancode | dddart implementation-dart/flutter/riverpod 등 · 지금 web implementation-javascript | 03:22 → 04:06:30 |
| ④ | `scripts/**` | dddart `scripts/*.dart` · 지금 web `scripts/*.py` | 03:22 → 03:47:17 · 정렬 뒤 03:55:02 |
| ⑤ | `codex-dddjango-web/**` | codex-dddart 대응 | 03:22 → 04:14:43(네 번 나눠) |
| ⑥ | `release-prep/**` | 저장소 Makefile · AGENTS.md · DEVELOPMENT.md(읽기만) | 03:45:21 → 04:17:48(4판) |
| lead | `mapping.md` · `.claude-plugin/plugin.json` · `build-log.md` · 이음매 맞춤 · 검증 | — | 03:10:34 → 04:16:12 |

## 3. 이름 대응
| dddart | dddjango-web 2.0.0 |
|---|---|
| 플러그인 `dddart` · `/dddart` · `.dddart/` | `dddjango-web` · `/dddjango-web:dddjango-web` · `.dddjango-web/` |
| 에이전트 coder · design-architect · design-review-ddd/ui/state/data · discipline-reviewer | 같은 이름 + `-web`(7) |
| 스킬 architecture-ddd/ui/state/data · discipline-cleancode/houserules/test · implementation-test | 같은 이름(8) |
| implementation-dart / implementation-flutter / implementation-riverpod | implementation-python / implementation-django / implementation-htmx |
| (없음) | implementation-javascript — 웹이라 새로(지금 web 판 바탕 · SDK 절은 «외부 JS 고정 사본 소비»로) |
| Codex 역할 스킬 `dddart-<역할>` · 충돌 4종만 `dddart-<스킬>` | 역할 `dddjango-web-<역할>-web`(7) · 지식 12종 전부 `dddjango-web-<스킬>` · Coordinator `dddjango-web` |
| 검사 60종(ST12 · IM23 · NM17 · CY1 · TG1 · PJ2 · MD2 · RV1 · HV1) | 검사 72종(ST13 · IM27 · NM19 · CY1 · TG1 · MD2 · PJ3 · PU6) |

## 4. 파일 대응표(Claude 판)
| dddart 파일 | B | 새 파일 | B | 처리 |
|---|---|---|---|---|
| `.claude-plugin/plugin.json` | 581 | `.claude-plugin/plugin.json` | 619 | 갈아 끼움 |
| `commands/dddart.md` | 58,960 | `commands/dddjango-web.md` | 62,544 | 갈아 끼움 + Django 연결 설정 점검 |
| `agents/coder.md` | 15,944 | `agents/coder-web.md` | 16,397 | 갈아 끼움 |
| `agents/design-architect.md` | 21,770 | `agents/design-architect-web.md` | 21,749 | 갈아 끼움 |
| `agents/design-review-ddd.md` | 4,281 | `agents/design-review-ddd-web.md` | 4,316 | 갈아 끼움 |
| `agents/design-review-ui.md` | 7,141 | `agents/design-review-ui-web.md` | 6,944 | 갈아 끼움 |
| `agents/design-review-state.md` | 4,883 | `agents/design-review-state-web.md` | 5,077 | 갈아 끼움 |
| `agents/design-review-data.md` | 4,542 | `agents/design-review-data-web.md` | 4,263 | 갈아 끼움 |
| `agents/discipline-reviewer.md` | 17,763 | `agents/discipline-reviewer-web.md` | 18,153 | 갈아 끼움 |
| `skills/architecture-ddd/SKILL.md` · `references/final.md` | 3,935 · 27,793 | 같은 경로 | 3,995 · 28,672 | 갈아 끼움 |
| `skills/architecture-ui/SKILL.md` · `references/final.md` | 3,619 · 18,554 | 같은 경로 | 3,803 · 20,360 | 갈아 끼움 |
| `skills/architecture-state/SKILL.md` · `references/final.md` | 3,987 · 20,764 | 같은 경로 | 4,250 · 23,570 | 갈아 끼움 |
| `skills/architecture-data/SKILL.md` · `references/final.md` | 3,762 · 15,953 | 같은 경로 | 3,368 · 14,463 | 갈아 끼움(§5 로컬 2층은 «해당 없음» 한 줄) |
| `skills/discipline-cleancode/SKILL.md` · `references/final.md` | 3,668 · 92,915 | 같은 경로 | 3,726 · 92,320 | dddart 절 구조 + 지금 web 판 Python 예시 |
| `skills/discipline-houserules/SKILL.md` · `final.md` · `undecidable.md` | 8,164 · 38,960 · 13,729 | 같은 경로 | 8,455 · 42,146 · 13,989 | 갈아 끼움(새 트리) |
| `skills/discipline-test/SKILL.md` · `references/final.md` | 4,972 · 19,048 | 같은 경로 | 5,141 · 20,121 | 갈아 끼움 |
| `skills/implementation-test/SKILL.md` · `references/final.md` | 4,127 · 16,342 | 같은 경로 | 4,406 · 22,388 | 갈아 끼움 |
| `skills/implementation-dart/SKILL.md` · `references/final.md` | 3,315 · 15,800 | `skills/implementation-python/…` | 3,891 · 21,363 | 갈아 끼움(이름 바뀜) |
| `skills/implementation-flutter/SKILL.md` · `references/final.md` | 3,816 · 20,100 | `skills/implementation-django/…` | 4,895 · 33,534 | 갈아 끼움(이름 바뀜 · §10 CSS · §11 외부 JS 고정 사본 새 절) |
| `skills/implementation-riverpod/SKILL.md` · `references/final.md` | 3,312 · 13,612 | `skills/implementation-htmx/…` | 3,927 · 23,545 | 갈아 끼움(이름 바뀜) |
| `scripts/backstop.dart` | 4,604 | `scripts/backstop.py` | 6,669 | Python 으로 옮김(러너만) |
| `scripts/src/common.dart` | 22,103 | `scripts/src/common.py` | 34,387 | Python — 지금 web common.py 바탕 |
| `scripts/src/check_structure.dart` | 19,154 | `scripts/src/check_structure.py` | 22,613 | Python |
| `scripts/src/check_imports.dart` | 15,996 | `scripts/src/check_imports.py` | 19,857 | Python |
| `scripts/src/check_naming.dart` | 20,372 | `scripts/src/check_naming.py` | 26,883 | Python |
| `scripts/src/check_cycles.dart` | 4,679 | `scripts/src/check_cycles.py` | 5,745 | Python |
| `scripts/src/check_tests.dart` | 2,502 | `scripts/src/check_tests.py` | 2,516 | Python |
| `scripts/src/check_models.dart` | 6,227 | `scripts/src/check_models.py` | 6,696 | Python |
| `scripts/src/check_pubspec.dart` | 4,088 | `scripts/src/check_project.py` | 4,915 | Python(이름 바뀜 — web 토대 PJ1~3) |
| `scripts/src/check_riverpod.dart` · `check_hive.dart` | 3,865 · 2,279 | — | — | 뺌 |
| `scripts/extract_contract.dart` | 7,847 | `scripts/extract_contract.py` | 10,548 | 지금 web 판 byte 그대로 |
| `scripts/extract_design.dart` | 30,694 | `scripts/extract_design.py` | 20,347 | 지금 web 판 byte 그대로 |
| `scripts/extract_dc.dart` | 22,861 | `scripts/extract_dc.py` | 15,273 | 지금 web 판 byte 그대로 |
| `scripts/fetch_images.dart` | 12,417 | `scripts/fetch_images.py` | 12,020 | 지금 web 판 byte 그대로 |
| `scripts/extract_layout.dart` · `icon_map.json` | 11,736 · 1,729 | — | — | 뺌 |
| `scripts/test/run_fixtures.sh` | 45,433 | `scripts/test/run_fixtures.sh` | 28,904 | 새 트리 픽스처(F0~F8) |

dddart 에 없는 새 파일(10):
| 새 파일 | B | 바탕 · 까닭 |
|---|---|---|
| `skills/implementation-javascript/SKILL.md` · `references/final.md` | 4,328 · 19,200 | 지금 web 판(4,114 · 21,219) — JS 작성 규칙(웹이라 필요) |
| `scripts/src/check_purity.py` | 16,524 | 지금 web 판 WP(23,447) → PU — JS · 템플릿 출력 안전 |
| `scripts/src/__init__.py` | 78 | Python 패키지 표지 |
| `scripts/asset_io.py` · `design_sources.py` · `freeze_design.py` | 10,508 · 15,865 · 8,785 | 지금 web 판 byte 그대로 — `fetch_images.py` · `extract_dc.py` 가 함수 안에서 import(의존) |
| `scripts/test/fixtures_extract.sh` · `fixtures_contract.sh` | 11,893 · 8,536 | 지금 web 판 byte 그대로 — 추출 도구 픽스처(dddart 는 run_fixtures.sh 안에 있었음) |
| `scripts/test/test_assets.py` | 708 | 옛 `test_assets.py` 의 `png()` 하나만(fixtures_extract 가 씀) |

크기: Claude 판 56 파일 860,188 B(dddart 50 파일 734,698 B · 지금 web v1.3.1 84 파일 2,027,085 B) · Codex 판 54 파일 828,554 B(codex-dddart 50 파일 661,147 B · 지금 Codex web v1.3.1 86 파일 2,038,262 B). Coordinator 62,544 B(dddart 58,960 · 지금 web 206,992) · Codex Coordinator 69,342 B(codex-dddart 52,498 · 지금 Codex web 213,987).

## 5. dddart 와 어쩔 수 없이 달라진 곳 — 까닭
### 5-1. 폴더 배치(Django 규칙)
- `main.dart` 자리 → `web/apps.py`(`WebConfig.ready()` 가 root_initializer 만 부름) + `web/urls.py`(root_router 를 내보내는 한 줄) + `web/__init__.py` — Django 가 앱 · URL 입구로 찾는 고정 자리.
- 정적 파일은 `web/static/` 에 따로: 조각 CSS `web/static/application/[<area>/]<bc>/<조각 stem>.css` · root scaffold CSS `web/static/root/<stem>.css` · `js/` · `htmx/` · `vendor/<라이브러리>/<버전>/` · `images/` · `fonts/` — `.py` 가 있는 폴더를 정적 자리로 열면 `.py` 가 정적 파일로 나가서. design_system 은 `.py` 가 없어 제자리(`web/design_system/` — foundation CSS 7 · theme · component 템플릿 + 옆 CSS · util)에 두고 STATICFILES 접두 `design_system` 로 연다.
- 테스트는 `web_test/`(프로젝트 뿌리 · `web/` 1:1 미러 · sparse · `<sut>_test.py`) — 뿌리 `test/` 는 백엔드 `application/` 트리와 헷갈림. pytest 는 `--import-mode=importlib`(BC 마다 같은 이름 `render_smoke_test.py`).
- 빈 폴더 표지: Python 경로는 `.gitkeep` 대신 `__init__.py`(패키지 표지 겸).
- 페이지 템플릿은 `root/scaffold/view/root_view.html` 을 extends — BC 가 root 를 아는 유일한 예외(Django 템플릿 상속 방향이 Flutter 셸 임베드와 반대).
- `common/` 5종 → 4종(local_database 뺌) · `data_source/local_storage/` 뺌 — hive 짝.
- 국소 `analysis_options.yaml` → 국소 `ruff.toml`(BC · common · root — design_system 은 `.py` 없어 제외). ruff `ANN` 은 시그니처만 봄 → 지역 변수 첫 대입 타입은 표기 규율 + 리뷰어. ruff 가 없으면 G0 고지.
- Django Form 자리 없음(dddart 에 Form 층 없음 — 입력 읽기는 view · 검증은 VO · VM).

### 5-2. Coordinator · 에이전트
- G0 전제조건의 `analysis_options` exclude 고지 자리 → Django 연결 설정 점검 8(INSTALLED_APPS · TEMPLATES DIRS/builtins/context_processors · STATICFILES_DIRS 접두 튜플 · `include("web.urls")` + handler404/500 · MIDDLEWARE · ALLOWED_HOSTS testserver · htmx 2.0.10 고정 판 받기 · 테스트 도구) + 호스트 ruff exclude 고지.
- 연결 설정 적용 시점 = «연결 대상이 있느냐». 없으면 Phase 2 진입 준비에서 Coordinator 가 연결 대상 최소 자리(빈 `web/urls.py` · 빈 `Library()` root_initializer · `{}` 를 주는 root_context · 통과 미들웨어 · 기본 404/500 · `__init__.py`)를 만든 뒤 적용하고 산출물과 같은 커밋에 넣음 — settings 가 root 모듈 경로를 가리켜 대상 없이 넣으면 `manage.py check` 가 ImportError. Coordinator 직접 쓰기 목록에 이 예외가 하나 늘었다(지금 web 판도 같은 예외를 둠).
- `analyze_baseline` → `check_baseline`(py_compile + manage.py check + ruff). 빌드(apk) · codegen 재생성 확인 자리 → «전수 테스트»(`pytest web_test --import-mode=importlib` + `manage.py check`). 수정 모드의 «빌드 = 조건부» → 전수 테스트(빌드가 없어 생략 근거가 없음).
- 추출 명령은 지금 web 도구 CLI 에 맞춤(`--icon-map` · screens 위치 인자 · extract_layout 뺌). 아이콘은 추출하지 않고 material-symbols 이름 그대로. 그림자는 `shadows` 버킷(도구 산출 꼴).
- hive 문구(local_storage 3파일 · 어댑터 조립) 자리 → ui_extension 필터 조립 1줄 · root_router include · context processor.
- 경계 새 줄: 백엔드 코드는 고치지 않음 — 필요한 API 가 없으면 가정 계약으로 짓고 실제 API 는 `/dddjango` 로 요청 안내(dddart 는 서버가 다른 저장소라 저절로 지켜지던 것).
- coder-web: codegen 항목 뺌 · render-smoke 는 `web_test/application/<bc>/_support.py` 의 `SCREEN_PROBES` + `render_smoke_test.py` · FID 평가 하네스 언급 뺌 · JS 동작은 브라우저 테스트 `<화면>_browser_test.py`(pytest-playwright — JS 기능이 있을 때만) · 의존성은 requirements 고정 · 외부 JS 는 `web/static/vendor/<라이브러리>/<버전>/`.
- 리뷰어: state 는 keepAlive → 요청 · 세션 · 프로세스 수명 · `HX-Trigger`. data 는 hive 항목 뺌. discipline-reviewer-web 은 implementation-javascript 를 함께 싣고 «UI JS 는 표시 동작만» 한 구절.
- (2.0.1 · 사용자 결정 10-06 «API는 https,http 아니어도 괜찮아 왜냐하면 서버 프로젝트도 같은 컴퓨터에 있을수 있어.» · «넣자») API 위치 세 꼴 — `http(s)://` 주소(`curl`) · 로컬 OpenAPI 파일 경로(`cp` — web 1.3.1 문장 복원) · 이 프로젝트 안 path(`/api/openapi.json` 꼴 — `manage.py shell -c` 로 Django 테스트 클라이언트 GET · 서버 없이 · 2xx 이고 JSON 일 때만 저장). dddart(와 2.0.0)는 `http(s)://` 주소만 받는다. config 키 `openapi_url` 과 동결 뒤 처리(extract_contract · G1 절단)는 그대로.

### 5-3. 스킬
- architecture-state: 액션 에러 소비 단위 = 응답 하나(State 가 요청 수명이라 `consumeError()` · `ref.mounted` 없음) · SharedState = 세션 수명 + `HX-Trigger` 갱신 + reset(view 가 넘긴 세션 매핑을 `MutableMapping` 으로 받음 — 백스톱 IM12 가 application_layer 의 django · request 토큰을 막음) · Service = 비화면 이벤트(시그널 연결은 root_initializer) · 게이트 redirect = root_request_handler 미들웨어(Django urls 에 전역 redirect 훅이 없음).
- architecture-ui: ui_extension = Django 템플릿 필터 모듈(root_initializer 가 묶어 settings builtins 로) · navigator = `reverse` href 헬퍼(템플릿은 State 의 href 사용 · navigator 는 router 를 함수 안에서 import — Python 순환 import) · `<img>` 는 `{% static %}` + asset-manifest local_path(`--asset-*` 는 CSS 쪽만) · Key → `data-testid` · theme `app_theme.css` 에 브라우저 기본 여백 초기화 · 웹폰트.
- architecture-data: §5 로컬 2층 «web 에는 해당 없음» · 실패 종류 8 → 3(상태코드 `ApiStatusError` · 백엔드 미처리 예외 = 500 · 파싱 — in-process 라 타임아웃 없음) · `BadRequestResponse(Exception)`.
- architecture-ddd: from_json 은 손으로 하나(codegen 없음 — 금지는 수기 타입 리더 · try/except · 조용한 기본값) · Specification 조합 `and_/or_/not_`(예약어) · 예시 동기.
- implementation-python: Either 분해는 `match`(lambda 가 raise 를 못 담아 fold 없음) · 문법 하한 3.11 · 상수 UPPER_SNAKE(PEP 8) · 소진성 `assert_never` · 컬렉션 필드 tuple.
- implementation-django: §3 탭 재탭은 탭 링크 href 로 성립 · §5 hive «해당 없음» · §10 CSS · §11 외부 JS 고정 사본 새 절.
- implementation-htmx: hx-* 허용 일곱(get/post/target/swap/trigger/headers/indicator) · 금지 표면(hx-on · js: · 조건식 · hx-ext · hx-boost 등) · 오류 조각은 200(htmx 2 는 4xx/5xx 를 교체하지 않음) · lint 연동 절 → 백스톱 PU 연동 표.
- implementation-test: seam B = VM 대체(`monkeypatch`) · 테스트 도구에 beautifulsoup4(HTML 단언 — Django 에 선택자 단언 도구가 없음) · golden 비채택 그대로.
- discipline-houserules: §7 drift 표 43 → 41줄(hive 줄 2 지움) · 명명표 33행 유지(local_storage 3행 → 조각 CSS · UI JS · 테스트).
- 각 final.md 의 «출처» 줄과 discipline-test 의 실패 내력 문장에는 dddart · HaffHaff 이름이 남는다(출처 표기 — 18줄).

### 5-4. 백스톱
- 참조 = Python import(함수 안 포함) + 템플릿 extends · include · static + CSS `@import` · `url()` 세 갈래. 판별은 정규식 + 표준 `ast`(MD · NM14).
- 새 번호: ST12(`web/static/` 트리) · IM24(상대 import 금지) · IM25(백엔드 `application.`/`framework.` import 금지) · IM26(extends 대상) · IM27(HTTP 호출 표면 · API URL 리터럴) · NM18(view `.py`↔`.html` 짝) · NM19(조각 CSS ↔ 템플릿 stem) · NM20(snake_case) · PJ3(vendor 버전 폴더) · PU1 · 2 · 3 · 6 · 7 · 8.
- 뜻이 옮겨진 번호: NM8(common `@riverpod` 금지 → common 상태 동작 proxy) · NM10(색 · font 계열 리터럴 — CSS · 템플릿 style) · NM13(`path()` 가 router 밖 · `reverse`/`redirect` 문자열 리터럴 · 템플릿 `{% url %}`) · NM17(view `.py` 의 주 view · `_fragment` 밖 함수) · IM12(application_layer 의 django · request 토큰) · MD1(frozen · slots · kw_only dataclass) · MD2(from_json 형태) · PJ1 · 2(pytest · pytest-django 선언 · htmx 단일 2.0.10).
- 비운 번호: NM7(`@riverpod` 허용 위치) · PU4(→ NM10) · PU5(motion.js 판형). RV · HV 패밀리 없음.

### 5-5. Codex 판 — codex-dddart 와 다른 곳
- **시안 입력을 Claude 판에 맞춤**: codex-dddart 의 Stitch MCP(HTML 모드 · `--from-theme`) 대신 `DesignSync`(세션 도구 목록에 있을 때만) 또는 사용자가 내려받은 Claude Design 시안 폴더(`.dc.html` · `_ds_manifest.json` · `tokens/*.css` · `screenshots` · 이미지 — config `source:"local",path`) → 같은 동결(`ls`·`cp`) → `extract_design --from-ds-manifest` → `extract_dc` → 화면 확인 게이트. codex-dddart 에 없던 `extract_dc.py` 와 의존 3 파일을 실음. 까닭: 지시서 9 · 운영자 요구(W4 는 Codex 로 로컬 동결 시안) · 추출 도구에 theme 모드 없음.
- 지식 스킬 접두가 12종 전부(codex-dddart 는 충돌 4종만) — Codex 스킬은 플러그인 이름공간이 없음.
- Codex 전용 문장 둘: 확인 게이트 렌더는 경로로 제시 · coder-web «렌더를 판독 못 하면 미대조로 G2 에 넘김»(이미지 판독 비보장). Coordinator 경계에 «내려받은 시안 폴더도 읽기만».
- codex-dddart 가 Claude 판보다 뒤처진 곳(area 문단 · `has_stitch_html` 어휘)은 따르지 않고 Claude 판 내용 + 플랫폼 치환만.
- `scripts/test/` 는 싣지 않음(codex-dddart 와 같음) · README 동기 절차는 `diff -rq`·`rsync`(web 은 corpus_mirror_sync 대상 밖) · defaultPrompt 셋 모두 플러그인 이름을 부름(저장소 `request_guide_contract.py` 의 Codex 발견 계약).

## 6. 검증 출력(지시서 «검증» 절 · lead 실행 04:15:54~04:16:12)
- `claude plugin validate <S>/web-new/dddjango-web --strict` → `✔ Validation passed`
- `python3 -m py_compile`(scripts 아래 .py 19) → `py_compile ok: 19 files`
- `bash scripts/test/run_fixtures.sh` → `결과: PASS 95 / FAIL 0` · `fixtures_extract: PASS 31 · FAIL 0` · `PASS=13 FAIL=0` · exit 0
  - F0 깨끗한 새 트리 — blocker 0 / F1 위반 diff — exit 2 · 검사 ID 72 개가 각각 발화(F1 줄 78 PASS) / F2 상대 import 클램핑 / F3 주석 · docstring 속 import 불발화 / F4 added 줄 게이트 / F5 CY1 래칫 / F6 area / F7 사용 오류 / F8 CSS 참조
- `python3 scripts/backstop.py --help` → `[backstop] 사용 오류: 알 수 없는 옵션 --help` · exit 1
- frontmatter: Claude 판 커맨드 1 + 에이전트 7 + SKILL.md 12 = 20 파싱(ruby YAML) · name = 파일/폴더 이름 · bad 0
- 교차 참조: `dddjango-web:<이름>` 인용과 `<스킬> §N` 인용 전부 실제 스킬 · 절에 닿음(깨진 것 0)
- 남은 Flutter 낱말(`flutter|riverpod|hive|freezed|.dart|go_router|pubspec|mocktail|dddart|apk`): 커맨드 · 에이전트 · SKILL.md 0줄 · references 18줄(전부 출처 · 내력 표기)
- Codex 판(04:15:34): `plugin.json` JSON 파싱 `dddjango-web 2.0.0 ./skills/` · SKILL.md 20 frontmatter 파싱(name = 폴더 이름) · references 12 스킬 13 파일 Claude 판과 같음 · scripts 18 파일 같음(test 제외) · `<N>` 잔존 0

## 7. Codex 스킬 이름 겹침 확인(04:15:34 · `~/.codex/plugins/cache`)
새 판 Codex 스킬 20: `dddjango-web` · `dddjango-web-architecture-data` · `-architecture-ddd` · `-architecture-state` · `-architecture-ui` · `-coder-web` · `-design-architect-web` · `-design-review-data-web` · `-design-review-ddd-web` · `-design-review-state-web` · `-design-review-ui-web` · `-discipline-cleancode` · `-discipline-houserules` · `-discipline-reviewer-web` · `-discipline-test` · `-implementation-django` · `-implementation-htmx` · `-implementation-javascript` · `-implementation-python` · `-implementation-test`
| 설치된 플러그인 | 스킬 수 | 겹침 |
|---|---|---|
| dddart 1.2.0 | 19 | 0 |
| dddjango 2.19.1 | 20 | 0 |
| dddjango-web 1.3.1 | 11 | 4 — `dddjango-web` · `dddjango-web-coder-web` · `dddjango-web-design-architect-web` · `dddjango-web-discipline-reviewer-web`(같은 플러그인의 판 올림이라 교체됨) |
옛 dddjango-web 1.3.1 의 접두 없는 스킬(`architecture-web` · `discipline-cleancode` · `discipline-web-houserules` · `implementation-javascript` · `implementation-ui`) · `dddjango-web-design-review-web` · `dddjango-web-refactor` 는 새 판에 없다(판 올림 때 사라짐).

## 8. 이음매 맞춤 기록(lead)
- 03:48~03:56: ② 문면 ↔ ④ 백스톱(번호 뜻 · design_system 허용 자리 · 함수 안 import · NM8 proxy · ruff.toml) · ② ↔ ③(Either `value=` · `ApiClient`/`ApiStatusError` · `build()` · `load_error` · `data-testid`) · ④ ↔ ③(NM9 · 10 · 12 · 13 · 17 · IM12 와 SharedState 표기).
- 03:49~04:02: 추출 도구 의존 3 파일 복사 · root scaffold CSS 자리 추가 · design_system ruff.toml 제외 · 추출 픽스처 2 + `test_assets.py`.
- 04:07~04:11: architecture-data 예시의 `Left(…)`/`Right(…)` 를 `value=` 키워드로 · 테스트 헬퍼 파일 `_support.py`(dddart `_support.dart` 이름)로 통일 · `ScreenProbe` 별칭을 implementation-test §7 계약(`Callable[[Client, pytest.MonkeyPatch], list[Tag]]` · `TypeAlias` — `type` 문은 3.12 문법)으로 coder-web 과 맞춤 · 테스트 도구에 beautifulsoup4 를 Coordinator (8) · coder-web 에 반영 · `pytest web_test --import-mode=importlib`.

## 9. 남은 것(W3 밖 · 운영자 몫)
- 버전 길: scratch 매니페스트는 지시서대로 2.0.0. `make release-web` 은 판을 스스로 올리므로 옮겨 넣을 때 1.3.1 로 두고 major 를 고르는 길(A)과 2.0.0 그대로 current 를 고르는 길(B)이 있다(`release-prep/move-plan.md` §8).
- 새 판을 저장소에 넣으면 `workspace/tools/request_guide_contract.py`(web REQUEST_GUIDE 요구)와 Makefile `verify-web`(옛 파일 대조)이 맞지 않아 `make verify` 가 RED — `release-prep/tools.diff` · `makefile.diff` · `readme.diff` 를 같은 커밋에. Makefile 은 봉인 대상.
- `mapping.md` §7(일꾼 금지 절)과 scratch 경로 표기를 스펙 정본으로 옮길 때 남길지 · `workspace/plan/2026-10-06-web-dddart/` 미추적 3 파일을 함께 커밋할지.
- 2.1.0 에서 끼울 자리: G0(빚 스캔 · 질문) · 슬라이스 도출(슬라이스 0) · G1 배너(SDK 문항) · G2(남은 빚) · `commands/refactor.md`. 2.0.0 문면에 이 자리를 막는 문장은 없다.
- 시험하지 않은 것: 실제 Django 프로젝트에서 끝까지 돌려 본 적 없음(W4 몫). 스킬 예시 코드는 문법 · 일부 실행만 확인.

## 10. 배포 준비 초안(`release-prep/` · 일꾼 ⑥ · 04:17:48)
| 파일 | B | 무엇 |
|---|---|---|
| `makefile.diff` | 7,790 | Makefile `verify-web` 블록을 새 배치에 맞춤(run_fixtures · 문단 앵커 1 · scripts 미러 `--exclude=test` · 지식 스킬 12 references 미러) |
| `tools.diff` | 8,111 | `workspace/tools/request_guide_contract.py` — 가이드 계약을 dddjango 로 좁힘(self-test 104/104 · 얼린 두 판 모의 검사 위반 0건 · 옛 검사기로는 6건) |
| `readme.diff` | 11,142 | README 의 web 가이드 절 · 빠른 시작 · 자매 플러그인 절 |
| `agents-md.diff` | 3,191 | AGENTS.md 의 dddjango-web 설명 |
| `development-md.diff` | 15,566 | docs/DEVELOPMENT.md 의 dddjango-web 설명 |
| `release-notes-2.0.0.md` | 8,324 | 배포 노트 초안 |
| `move-plan.md` | 17,964 | 옮겨 넣기 경로 목록 — 지움 123(Claude 57 · Codex 66) · 새로 63(29 · 34) · 같은 경로 47(27 · 20 · 그중 byte 그대로 18) · 새 판 전체 110(56 · 54) · 순서 · 운영자가 정할 것 셋 |
- diff 다섯은 HEAD `0cdb10f5` 사본에 `patch -p1` 로 적용됨(04:17:34 확인). 저장소 파일에는 적용하지 않았다. make 타깃 실행 없음.
- dddjango 배포가 Makefile · AGENTS.md · DEVELOPMENT.md · README.md 를 바꾸면 diff 를 다시 맞춰야 한다.

## 11. scratch 에 남은 작업 파일(산출물 아님)
- `web-new/head/`(v1.3.1 `git archive` 사본) · `web-new/later/`(빈 폴더) · `web-new/release-prep/work/`(diff 원본 · 작업 사본 · 목록)
- 일꾼 ③ 이 남긴 `<S>/w3c/` · `<S>/w3-cc-dart-heads.txt` · `<S>/w3-cc-web-heads.txt`(discipline-cleancode 합치기 중간 파일 — 지워도 됨)

## 12. 검토 r1 고침(W5 Codex 검토 반려 — blocker 4 · important 9 · minor 3 · 04:42:34 ~ )
- 검토 원문 `web-new/review/review-web2-codex-r1.md` · 결정 · 소유 `web-new/review/fix-plan-r1.md`(lead). 기준은 «dddart 와 같은 동작 · 규칙». 일꾼: S(scripts · ④ 재개) · I(implementation-* · ③ 재개) · A(architecture-* · houserules · 에이전트 · ② 재개) · ⑤(Codex 맞춤) · lead(Coordinator). `<S>/w4/**` 는 열지 않음.

| # | 고친 것 | 파일:줄(Claude 판) |
|---|---|---|
| 1 | 전수 테스트 미통과는 환경 면제 없이 coder-web 반송(dddart 그대로) — «실행 환경 부재 → 미실행 보고» 문장 삭제 · 미니 게이트의 «step 6과 동일하게» 삭제 | `commands/dddjango-web.md:166` · `:167` · `:189` |
| 2 | `RootRequestHandler.process_view` 가 view 모듈이 `web.` 일 때만 게이트 · 신원 이월 · 탭 기록 — 같은 프로세스 API 호출(백엔드 view)은 건드리지 않아 재진입 끊김 · contextvar 는 응답 뒤 reset | `skills/implementation-django/references/final.md:132` · `:135-184` · `skills/architecture-state/references/final.md:218` · `skills/discipline-houserules/references/final.md:37` · `:263` |
| 3 | NM12 — htmx 상태 클래스 5개는 접두 붙은 클래스와 겹친 선택자에서만 허용 · 픽스처 F9 | `scripts/src/check_naming.py:74` · `:415-431` · `skills/implementation-django/references/final.md:452` |
| 4 | 탭 전환 = 세션 `root.tab_last` 의 탭별 마지막 경로 · 현재 탭 재탭 = 첫 화면(dddart `goBranch` + 2단 동작) | `skills/implementation-django/references/final.md:130` · `:173-182` · §3 `:192-243` · `skills/architecture-state/references/final.md:214` · `skills/architecture-ui/references/final.md:92` · `undecidable.md:63` |
| 5 | 직파싱 타입 확인 — `web/common/util/json_field.py` 의 `json_field(data, key, kind)` 단일 출처(bool↔int 구별 · float 자리 int 허용) · domain → common 은 이 파일 하나만 예외(IM19 예외 — dddart 의 json_serializable 자리) · 픽스처 F10 | `skills/implementation-python/references/final.md:148-190` · `skills/architecture-ddd/references/final.md:72` · `:108-111` · `:138` · `skills/architecture-data/references/final.md:40` · `:96` · `:106` · `skills/discipline-houserules/references/final.md:217` · `:247` · `scripts/src/common.py:66` · `scripts/src/check_imports.py:80` |
| 6 | 임베드 view = 부모 자리 `hx-get="{{ state.<자식>_embed_href }}" hx-trigger="load"` + 자식 `<화면>_embed_fragment`(자기 VM) — «조각 첫 데이터 요청 금지» 의 유일한 예외 | `skills/architecture-ui/references/final.md:29` · `:40` · `skills/implementation-htmx/references/final.md:39` · `:123-133` · `:242-262` · `skills/implementation-django/references/final.md:53-91` |
| 7 | 조회 실패 = `build()` 는 raise(dddart 채널 ① 그대로) → view 가 잡아 같은 section 을 맥락 `load_error` · `retry_href` 로 렌더 · section 은 루트 id 유지하고 안에서 `error_feedback.html`(`error` · `retry_href` · `target_id`) include · State · VM 변경 없음 | `skills/architecture-state/references/final.md:69` · `:72` · `:109-144` · `skills/implementation-htmx/references/final.md:43` · `:143-169` · `:213` · `:221` · `:274-285` |
| 8 | G0 가 확인한 실제 htmx core 경로를 `htmx_core_static`(scope.md · build-state)으로 · 문서 셸이 그 경로를 로드 · coder 입력 · PJ2 는 새로 더한 htmx 파일만 · 픽스처 F11 | `commands/dddjango-web.md:53` · `:108` · `:160` · `agents/coder-web.md:31` · `:64` · `skills/implementation-htmx/references/final.md:25-27` · `skills/implementation-django/references/final.md:114` · `scripts/src/check_project.py:52-60` |
| 9 | **원본 결함 고침**(dddart `commands/dddart.md:124-125` 에서 물려받음): PROJECT 추출 ① 에 실제 동결된 manifest 경로 `design-ref/_ds/<…>/_ds_manifest.json` 를 넘김 | `commands/dddjango-web.md:127` |
| 10 | Phase 2 진입 순서 — 산출물 커밋 → `git_snapshot` → 연결 대상 최소 자리 · 연결 설정 **별도 커밋** → check 기준선(이번 런이 만든 root 가 added 로 남아 ST4 · PJ2 대상) · 검사기는 그대로 · 픽스처 F12 | `commands/dddjango-web.md:153` · `scripts/test/run_fixtures.sh`(F12) |
| 11 | NM10 — CSS · `<style>` · style 속성은 선언 값에서만 색 · typography 리터럴(선택자 `#add` 불발화) · 픽스처 F13 | `scripts/src/check_naming.py:75` · `:383-410` |
| 12 | `RootRequestHandler.__call__` — HX 요청의 3xx 응답을 200 + `HX-Redirect` 로(조각의 로그인 이동이 전체 페이지 이동) | `skills/implementation-django/references/final.md:151-152` · `:68` · `:185` · §6 `:373` · `skills/implementation-htmx/references/final.md:181` · `:265` |
| 13 | G0 (8) 이 pytest settings 길(호스트 pytest 설정 → 환경변수 → `manage.py` 기본값 `--ds=`)을 확정해 `test_command` 로 기록 · 전수 테스트 · coder-web green 래칫 · implementation-test 가 같은 명령 · G0 (5) 에 미들웨어 순서(Session · Authentication 뒤) | `commands/dddjango-web.md:54` · `:108` · `:160` · `:166` · `:189` · `agents/coder-web.md:30` · `:39` · `:45` · `skills/implementation-test/references/final.md:23` |
| 14 | design_system 은 국소 ruff.toml 대상에서 뺌(SKILL · coder 지시를 reference · 검사기와 같게) | `skills/discipline-houserules/SKILL.md:18` · `agents/coder-web.md:28` |
| 15 | 테스트 헬퍼 · render-smoke · import 경로에 area 마디 반영 `web_test/application/[<area>/]<bc>/` | `agents/coder-web.md:39` · `skills/implementation-test/references/final.md:141` · `:170` · `:175` |
| 16 | `--only` 에 없는 패밀리 · 검사 ID(비운 번호 포함)는 사용 오류 exit 1 · `FAMILIES` 8 · `CHECK_IDS` 72 단일 출처 · 픽스처 F14 | `scripts/backstop.py:47-54` · `:93-98` |

dddart 와 달라진 곳에 더함:
- **#9 원본 결함 고침** — dddart Claude 판 Coordinator 도 `_ds/…/_ds_manifest.json` 을 같은 트리로 동결하고 `design-ref/_ds_manifest.json` 을 읽는다(그대로면 exit 1). 실제 동결 경로를 넘기게 고쳤다.
- **#4 탭 전환** — Flutter 의 `StatefulNavigationShell.goBranch`(탭별 스택 보존)를 웹에서 가장 단순하게 내려고 세션에 탭별 마지막 경로를 둔다(`root.tab_last` — root_request_handler 가 web 페이지 GET 마다 기록 · RootVM 이 탭 href 를 만듦 · BC 는 모름). 재탭 2단 동작은 «현재 탭 href = 첫 화면» 으로(이미 첫 화면이면 다시 열려 맨 위).
- **#5** — Python 에는 codegen 이 없어 직파싱 타입 확인을 `json_field` 한 파일에 모음. domain → common 예외가 그 파일 하나 늘었다(dddart 의 domain → json_annotation 패키지 자리).
- **#2 · #12** — Django 미들웨어가 같은 프로세스 API 호출에도 다시 돌기 때문에 생긴 경계(Flutter 에는 없는 일): 게이트 · 신원 이월 · 탭 기록은 web view 에서만 · HX 요청의 리다이렉트는 `HX-Redirect`.
- **#10** — Coordinator 가 연결 대상 최소 자리를 만드는 예외(§5-2) 때문에 생긴 순서: 연결 설정은 `git_snapshot` 뒤 별도 커밋.

### r1 검증 출력(Claude 판 04:56:55 · Codex 판 05:03:37 — W3 «검증» 절 그대로 · 검토 바퀴는 다시 돌리지 않음)
- `claude plugin validate dddjango-web --strict` → `✔ Validation passed`
- `python3 -m py_compile` → 19 파일 ok
- `bash scripts/test/run_fixtures.sh` → exit 0 · `결과: PASS 108 / FAIL 0`(F1 의 검사 ID 72 개 각각 발화 · 새 픽스처 F9a·b · F10a·b · F11a·b · F12 둘 · F13a·b · F14a·b·c 모두 PASS) · `fixtures_extract: PASS 31 · FAIL 0` · `PASS=13 FAIL=0`
- `backstop.py . --only typo` → `[backstop] 사용 오류: 알 수 없는 --only 값 typo …` · exit 1
- frontmatter: Claude 판 20 · Codex 판 SKILL.md 20 파싱(name = 파일/폴더 이름) · bad 0
- 교차 참조(`dddjango-web:<이름>` · `<스킬> §N`): 깨진 것 0
- 스킬 · 에이전트 python 예시 블록 124 개 compile — 문법 오류 0
- 결정 이름(`root.tab_last` · `_embed_href` · `_embed_fragment` · `htmx_core_static` · `test_command` · `HX-Redirect` · `load_error` · `retry_href` · `json_field` · `process_view` · `target_id`)이 fix-plan 글자 그대로 쓰임
- Codex 판: `plugin.json` 파싱 · references 12 스킬 13 파일 · scripts 18 파일이 Claude 판과 byte 같음 · `<N>` 0 · Codex 전용 문장 하나 더함(로컬 시안 폴더를 `cp` 로 동결해도 `_ds/<…>/` 트리를 그대로 두고 그 경로를 추출에 넘김)
- 크기: Claude 판 56 파일 896,495 B · Codex 판 54 파일 859,706 B
- 일꾼 I 가 `<S>/w3c/venv`(Django 5.2.17)로 `RootRequestHandler` 예시를 실제 실행: 게이트 호출 1회(재진입 없음) · 같은 프로세스 API 까지 신원 전달 · 요청 뒤 contextvar None · 탭 기록 · HX GET 은 기록 안 함 · HX 302 → 200 + HX-Redirect · 비 HX 302 그대로.

## 13. W4 결함 둘 고침(05:36:55 ~ 05:43:27 · 결정 `web-new/review/fix-plan-r2.md`)
W4 결과 `<S>/w4/result.md` §7(G2 까지 레인 1:02:54). 픽스처 원본은 `<S>/w4/a` 커밋 `f89fa1af5` 의 두 파일을 `git show` 로 읽어 복사만(W4 사본은 고치지 않음).

### 결함 1 — IM13 옛 배치 경로
- **dddart 소스 확인**: `dddart/scripts/src/check_imports.dart:13-31`(IM 은 lib 의 모든 `.dart` 중 touched 파일의 added 줄에만 · 층은 경로 마디 `presentation_layer` 등으로만 가림) · `:149-160`(IM13 = 허용 자리 화이트리스트 — presentation_layer 마디 · root/scaffold · main · design_system · router 가 아니면 발화) · `common.dart:336` · `:369-376`(added 줄 게이트). 그래서 dddart 를 글자 그대로 옮기면 **층 마디가 없는 파일이 design_system 을 새로 import 하면 발화한다** — 새 판도 같은 판정이었다. dddart 의 브라운필드(HaffHaff)는 옛 코드도 이미 `lib/application/<bc>/presentation_layer/` 안에 있어 이 자리를 밟지 않았고, 원칙 문면은 «레거시(기존 drift)에는 불발화 — 새 코드부터 표준»(houserules §8) · «레거시 단위 안에 파일을 더해도 표준 폴더 신설 · 이동을 요구하지 않는다»(§7) 다.
- **고침**: 표준 트리(web 직속 `__init__/apps/urls.py` · `root` · `application` · `common` · `design_system` · `static` · `locale`) 밖 파일 = «층 판정 불가 레거시». 층을 알아야 하는 IM(IM1~IM23 · IM26 — 화이트리스트 꼴 IM2 · IM13 · IM16 · IM22 · IM26 과 층별 금지)은 그 파일에 걸지 않고, 층 무관 IM(IM24 상대 import · IM25 백엔드 import · IM27 HTTP 표면 · `/api/` 리터럴)은 그대로 건다. 반대 방향(표준 파일 → 옛 배치)은 표준 파일의 층 규칙 그대로.
- **dddart 와 달라진 곳**: dddart 의 경로 마디 판정을 글자 그대로 옮기면 web 옛 배치(presentation 코드가 표준 트리 밖)를 고칠 때마다 막혀 dddart 의 «이동 요구 없음» 원칙과 부딪힌다 → dddart 가 실제로 낸 결과(옛 presentation 코드에 불발화)와 원칙을 따름. 옛 배치를 새 트리로 옮기는 일은 2.1.0 빚 정리 몫.
- 파일:줄 — `scripts/src/common.py:115`(`is_standard_path`) · `scripts/src/check_imports.py:26`(`LAYER_FREE_IM`) · `:71-76` · `skills/discipline-houserules/references/final.md:276`(§7 ⓒ) · `:335`(§8) · 픽스처 F15a(W4 원본 extends · include 불발화) · F15b(옛 배치 파일의 백엔드 import → IM25 발화).

### 결함 2 — IM26 공용 부품의 자리 채우기
- dddart 의 같은 자리: 공용 위젯의 Widget slot 인자(`leading:` · `actions:` · `child:`)에 child 위젯을 넘겨 채움.
- **고른 웹 꼴**: 값 인자는 `{% include … with … only %}` · 마크업 인자는 **부품이 내놓은 `{% block %}` 을 쓰는 쪽 조각이 `{% extends "design_system/component/…" %}` 로 채움**(파일 = 그 부품의 채워진 사례 하나). 까닭: Django 템플릿에서 마크업을 부품의 정해진 자리에 넣는 표준 장치는 block 하나뿐(include 는 값만 · 커스텀 templatetag 금지) · W4 의 architect · 리뷰어가 스스로 고른 꼴 · 템플릿 이름 변수 include 는 참조를 기계로 셀 수 없어 버림.
- **IM26 새 규칙**: 페이지 템플릿(`presentation_layer/view/*_view.html` · `root/scaffold/view/root_*_view.html`) → `root_view.html` 만 · 조각 템플릿(section · widget · design_system component) → `design_system/component/**/*.html` 만. 72종 · 새 ID 없음 그대로. «block 밖 내용 금지 · 두 번째 extends 없음» 은 기계 검사 없이 리뷰어 감사 몫(새 ID 가 필요해서).
- 파일:줄 — `scripts/src/check_imports.py:66-69` · `:244-259` · `skills/discipline-houserules/references/final.md:243`(§5 템플릿 상속 채널) · `skills/architecture-ui/references/final.md:107`(§7 인자 두 꼴) · `skills/implementation-django/references/final.md:377`(§6 extends 규칙) · `:383` · `:464-486`(§10 slot 부품 예시 — Django 5.2.17 로 실제 렌더 확인) · `skills/implementation-django/SKILL.md:24` · 픽스처 F16a(section → component 불발화) · F16b(section → root_view 발화) · F16c(페이지 → component 발화 · 페이지 → root_view 불발화) · F1 의 IM26 probe 를 section → root_view 로 바꿈.

### 검증(05:42:35 ~ 05:43:27)
- `claude plugin validate dddjango-web --strict` → `✔ Validation passed`
- py_compile 19 파일 ok
- run_fixtures → exit 0 · `결과: PASS 113 / FAIL 0` · `fixtures_extract: PASS 31 · FAIL 0` · `PASS=13 FAIL=0`
- frontmatter: Claude 20 · Codex 20 · bad 0 · 교차 참조 · python 블록 124 문법 오류 0
- Codex 판: implementation-django SKILL.md 에 같은 한 줄(접두 걷으면 Claude 판과 같음) · references 13 · scripts 18 byte 같음 · `<N>` 0
- 크기: Claude 판 56 파일 908,724 B · Codex 판 54 파일 867,649 B
