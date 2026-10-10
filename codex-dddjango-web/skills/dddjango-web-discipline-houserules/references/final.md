# dddjango-web 표준 파일트리

> **출처:** 제1 규약(dddart 표준 파일트리 확정 설계, 2026-06-11) · HaffHaff-App `lib/application/` 16 BC 전수 조사 · dddjango discipline-houserules(양식) · 백스톱 설계(2026-06-12) §2·§3 · dddjango-web 2.0.0 대응 규약(dddart → web).
> 본문 속 `(규약 §N)`·`(백스톱 설계 §N)`·`(본설계 §N)`은 **출처 표기**(설계 문서의 절 번호)이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 두 가지뿐: 타 스킬은 "스킬명 + 주제", 동봉 파일은 `undecidable.md`.

---

## 목차

- §1. 표준 트리 (전문)
- §2. 성장 규칙 — 개념 1차·종류 2차
- §3. 골격 완비 규칙 — 비어 있어도 형태를 유지한다
- §4. 명명 규약 총괄표
- §5. import 방향 — 계층 매트릭스·교차 BC 4채널·root 방향 규칙
- §6. common·design_system 입장 판별
- §7. 표기 표준화 — drift와 교정
- §8. 백스톱 연동 — 러너·게이트
- §9. 공식 플랫폼 SDK — 등재·사본·로드

---

## §1. 표준 트리 (전문)

4원칙 (규약 §1): ① 기준은 이론이 아니라 운영 중인 실제 앱(HaffHaff-App)이다 — 단 사용자가 명시적으로 교정한 결정(dddjango 정렬·철저한 MVVM·통용 용어)이 우선한다 ② **간소화 DDD** — repository 인터페이스 없음·DTO 없음·ACL 없음, 뼈대(컨테이너·4계층·개념 1차·종류 2차)는 유지 ③ **철저한 MVVM** — 지식은 View → VM → UseCase(Model 관문) → Repo 한 방향 ④ **파일트리가 곧 규약이다** — 어떤 파일을 어디에 어떤 이름으로 만드는지가 핵심 강제다.

```
web/                                         # Django 앱 "web" — dddjango-web 생성 영역의 뿌리
├── __init__.py · apps.py · urls.py          # 엔트리포인트 최소형 (Django 고정 자리) — apps.py WebConfig.ready()는 root_initializer 시동만, urls.py는 root_router의 urlpatterns를 내보내는 한 줄
├── root/                                    # 합성 루트 — 전체를 아는 유일한 곳, 계층 없음 (역할 4폴더)
│   ├── router/                              #   ① 내비 그래프
│   │   └── root_router.py                   #     전 BC <bc>_router 합산 (urlpatterns · BC 네임스페이스 include — plain 모듈 전역)
│   ├── scaffold/                            #   ② 루트 스캐폴드 (개념 폴더) — 문서 셸 + BC 어휘 없는 전역 게이트만
│   │   ├── view/                            #     root_view.html — 모든 페이지가 extends 하는 문서 셸(탭·내비 프레임)
│   │   ├── view_model/                      #     root_vm.py — "거의 빈 VM" 규범 (context processor root_context가 RootState를 셸에 준다)
│   │   └── state/                           #     root_state.py
│   ├── handler/                             #   ③ 전 BC 배선 — 이벤트원당 1파일 (*_handler)
│   │   ├── root_destination_handler.py      #     외부 진입 URL(알림 링크 등 — BC URL로 정규화) → BC 디스패치
│   │   ├── root_request_handler.py          #     요청 수명 (미들웨어 process_view — view 모듈이 web.일 때만) — 게이트·세션 신원 이월·탭 기록
│   │   └── root_error_handler.py            #     전역 에러 (handler404·handler500) → 로그·표시
│   └── initializer/                         #   ④ 시동
│       └── root_initializer.py              #     시동 연결 + BC ui_extension 템플릿 필터 조립 (settings TEMPLATES builtins 대상)
├── application/                             # BC 컨테이너 — 직속은 BC 폴더(또는 area 폴더)만 (균일)
│   ├── <area>/                              # (선택) BC 그루핑 — 순수 시각 네임스페이스 (아래 area 핵심 사실)
│   │   └── <bc>/                            #   area 하위 BC — 내부 구조는 아래 <bc>/와 완전 동일
│   └── <bc>/                                # 바운디드 컨텍스트 (기능 영역) 1개
│       ├── <bc>_router.py                   # urlpatterns·app_name·<Bc>Routes — URL path·name 단일 출처
│       ├── <bc>_navigator.py                # 정적 href 헬퍼 — 일반 이동은 이름 기반, 기본 홈 주소 예외는 architecture-ui §6, View import 금지
│       │
│       ├── domain_layer/                    # 순수 Python — django import 금지
│       │   └── <aggregate>/                 # 애그리거트(개념) 1차
│       │       ├── <aggregate>.py           # 애그리거트 루트 — 일관성 경계
│       │       ├── entity/                  # 종속 엔티티 (frozen dataclass + from_json)
│       │       ├── value_object/            # 값 객체·도메인 분류 값
│       │       ├── enum/                    # 도메인 enum
│       │       ├── domain_service/          # stateless 도메인 로직
│       │       ├── specification/           # Specification
│       │       └── exception.py             # 도메인 예외 (첫 예외 때 생성 — 골격 대상 아님)
│       │
│       ├── application_layer/
│       │   ├── use_case/                    # 유스케이스 (command+query 통합) — Model의 관문, Either 반환
│       │   ├── view_model/                  # 요청마다 view가 만드는 VM — 화면 1개의 상태 주인 (ViewModel)
│       │   ├── state/                       # 상태 모델 (frozen dataclass) — VM·SharedState·Service가 노출
│       │   ├── shared_state/                # 화면·조각 간 공유 상태 — VM의 공유 변종 (HX-Trigger 갱신·reset)
│       │   └── service/                     # 헤드리스 ViewModel — 비화면 이벤트 구동 (시그널·비화면 요청)
│       │
│       ├── infra_layer/
│       │   ├── data_source/                 # 데이터 출처 정의 — in-process api_client 호출 (평면)
│       │   ├── repository/                  # 구체 클래스 (인터페이스 없음) — safe_api_call로 감싼 단일 진실 원천
│       │   └── service/                     # 수동 SDK 어댑터 (호출당하는 쪽)
│       │
│       └── presentation_layer/
│           ├── view/                        # 화면 (<화면>_view.py 함수 + <화면>_view.html — 자기 VM 호출)
│           ├── section/                     # 한 화면 전속 구획 템플릿 (dumb — include 인자·href만) · HTMX 부분 교체 단위
│           ├── widget/                      # BC 내 재사용 부품 템플릿 (dumb, 화면 비전속)
│           └── ui_extension/                # 도메인 enum·VO → UI 매핑 템플릿 필터 (CSS 클래스·아이콘 이름·라벨)
│
├── common/                                  # 횡단 공통 — BC를 모른다 (application·root import 금지, 상태 동작 금지)
│   ├── enum/                                # 전역 enum (env 등)
│   ├── network/                             # api_client(in-process)·safe_api_call·bad_request_response·세션 신원 contextvar
│   ├── service/                             # BC 무관 플랫폼 서비스 (애널리틱스·이미지)
│   └── util/                                # 순수 유틸 (포맷터·계산기·either)
│
└── design_system/                           # BC 어휘를 모르는 시각 요소 — 토큰 + 컴포넌트 (STATICFILES 접두 design_system)
    ├── foundation/                          # 디자인 토큰 — 시각 값의 단일 출처 (표준 7파일 · CSS 변수)
    │   ├── app_color.css · app_typography.css · app_spacing.css · app_radius.css
    │   └── app_shadow.css · app_duration.css · app_asset.css
    ├── theme/
    │   └── app_theme.css                    #   foundation → 문서 전역 기본값: 브라우저 기본 여백 초기화·웹폰트 @font-face·body 글꼴/색 (light/dark 확장점)
    ├── component/                           # 공용 부품 — 부품군 1차, 직속 파일 금지 (부품 템플릿 + 옆에 부품 CSS)
    │   ├── app_bar/ · button/ · dialog/ · bottom_sheet/
    │   └── input/ · loading/ · image/ · feedback/ · background/ …
    └── util/                                # 시각 동작 헬퍼 CSS (미디어쿼리·스크롤 동작)

web/static/                                  # Django 정적 자리 (STATICFILES 접두 web) — .py와 섞이면 .py가 정적 파일로 나가서 따로 둔다
├── application/[<area>/]<bc>/<조각 stem>.css   # presentation 조각 CSS — 템플릿과 같은 stem · sparse
├── root/<조각 stem>.css                      # root scaffold 조각 CSS(셸 프레임 · 게이트 화면) — 템플릿과 같은 stem · sparse
├── js/<기능>.js                             # 승인된 UI 동작 JS — 기능당 한 파일 (implementation-javascript)
├── htmx/htmx.min.js                         # 2.0.10 고정 (Coordinator가 G0에 설치)
├── vendor/<sdk_id>/<파일> · vendor/.gitattributes   # G1 승인·등재된 공식 플랫폼 SDK 사본 + 고정 표지 (조건 생성 — Coordinator 도구만 · §9)
└── images/ · fonts/                         # 시안 이미지·웹폰트 (필요할 때만)

web/sdk_registry.json                        # 공식 SDK 등재 목록 (조건 생성 — 승인된 SDK가 있을 때만 · Coordinator 도구만 · §9)

web_test/                                    # web/ 1:1 미러 · sparse · <sut>_test.py · 브라우저 테스트 <화면>_browser_test.py
```

계층·종류의 동작 규율(각 폴더에 담기는 코드의 내용 규칙)은 lens 스킬 소유다: domain_layer 내부 → architecture-ddd(전술 패턴 §3·§4·판정 소유 §5) / application_layer 내부 → architecture-state(VM 3변종 §1·State 계약 §3·에러 2채널 §4) / infra_layer 내부 → architecture-data(safe_api_call §2·Either §3) / presentation_layer 내부·design_system 사용 → architecture-ui(3단 판별 §1·승격 규칙 §4). 이 문서는 **어떤 폴더·파일·이름이 존재해야 하는가(사실)** 를 소유한다.

**root/ 핵심 사실** (규약 §3.6 — 동작 규율은 architecture-state §10, view 작성 규율은 architecture-ui §2 위임): root는 application·common·design_system 세 컨테이너를 전부 아는 유일한 곳이라 `application/` 밖, `apps.py`·`urls.py` 옆이 정위치다. 내부는 계층 없이 역할 4폴더(`router/`·`scaffold/`·`handler/`·`initializer/`)이고 scaffold만 종류 2차(view·view_model·state)를 갖는다. root/ 이하 모든 파일은 `root_` 접두를 유지한다 — BC 코드의 `import …root_…` 한 줄로 위반이 즉시 식별된다(페이지 템플릿의 `root_view.html` extends 하나만 예외 — §5). 다수 BC 투영 화면(예: 피드 `home_view`)은 root가 아니라 자기 이름의 **일반 BC**다.

**area 핵심 사실** (feedback-031 — opt-in 그루핑): `application/` 직속에는 BC 폴더 외에 **area 폴더**(BC 그루핑 — `application/<area>/<bc>/`)를 둘 수 있다. area는 **순전히 사람의 시각적 도움을 위한 네임스페이스**다: ⓐ **기본은 평면** — area는 G0에서 사용자가 명시 판정할 때만 쓴다(에이전트 자동 추론 금지 — 판별 배정은 `undecidable.md` §13) ⓑ area 직속은 BC 폴더만(`__init__.py` 외 파일·`ruff.toml`·`.gitkeep` 금지)·중첩 1단만·빈 area 금지 ⓒ **BC 이름은 web 전역 유일 유지(접두 유지)** — area는 어떤 식별자·클래스명·URL name·`app_name`·파일명에도 등장하지 않는다. URL 네임스페이스(`app_name`)·CSS 클래스·HTMX 이벤트 이름은 전역이라 접두를 폴더로 대체하면 전역 충돌한다 — area는 접두의 *대체*가 아니라 접두 *위의* 그루핑이다 ⓓ area·BC 이름에 계층명(`*_layer` 4종)·컨테이너명(root·application·common·design_system) 금지 ⓔ **리트머스** — area 폴더를 지워 평면으로 되돌려도 바뀌는 것은 경로(web·web_test·static 미러의 디렉터리 위치, import 문, 템플릿 경로 문자열)뿐, 식별자·클래스명·URL name·파일명·코드 동작은 불변이어야 한다. 러너는 area를 적극 증명될 때만 인정(직속 파일 0·직속 전부 BC꼴)하고 그 외 전부 기존대로 BC 취급한다(보수 폴백 — 레거시·drift 형상의 분류 불변).

**web_test/ 핵심 사실** (pytest가 찾는 자리 — 프로젝트 뿌리, `web/`의 형제. 뿌리 `test/`는 백엔드 `application/` 트리와 헷갈려서 쓰지 않는다): 테스트는 `web_test/`에 두고 **`web/` 구조를 1:1 미러**한다 — `web/application/<bc>/<계층>/<sut>.py` → `web_test/application/<bc>/<계층>/<sut>_test.py` (area 그루핑 시에도 그대로 — `web/application/<area>/<bc>/…` → `web_test/application/<area>/<bc>/…`). 단 **web_test/는 sparse다 — SUT가 있는 자리에만 테스트 파일을 두고 빈 미러 폴더·빈 테스트 파일을 만들지 않는다**(골격 완비의 명시적 예외 — §3). 무엇을 테스트할지·단언 FORM은 discipline-test, Django 메커니즘·결정성은 implementation-test 소유다. 백스톱 TG1은 신규 BC의 행위 테스트 *존재*만 검사하고(부재 차단 — 슬라이스 0이 기존 파일을 옮기기만 해 생긴 BC는 새 테스트를 요구하지 않는다: 리팩토링은 기존 테스트 충분 가정이다 · 옮긴 SUT의 미러 테스트는 같은 경로 대응으로 함께 옮기고 단언은 그대로다), 미러 배치·FORM은 discipline-reviewer가 감사한다.

## §2. 성장 규칙 — 개념 1차·종류 2차

계층별로 개념 분할 시점이 다르다 (규약 §4):

- **domain_layer — 항상 애그리거트(개념) 1차.** BC가 작아도 애그리거트 폴더부터 만든다. 도메인 개념이 불명확한 BC는 **BC와 동명의 애그리거트**가 기본값.
- **application_layer·presentation_layer — 두 번째 개념이 등장하는 시점에 개념 1차로 분할**하고 그 안에 종류 폴더를 둔다. 분할은 새 코드부터 적용하며 기존 파일 이동을 요구하지 않는다:

```
chat/application_layer/
├── chat/                                # 개념 1차
│   └── use_case/ · view_model/ · state/ · shared_state/ · service/   # 종류 2차 — 완비(§3)
└── chat_request/
    └── use_case/ · view_model/ · state/ · shared_state/ · service/
```

- **infra_layer — 평면 유지.** 개념 분할 없이 종류 폴더만 (HaffHaff 16 BC 전수에서 동일). 하위층은 없다(web에는 로컬 저장 층이 없다 — architecture-data §5).
- 분할 후 기존 직속 종류 폴더는 **동결** — 신규 파일 금지, 새 코드는 개념 폴더로.
- `root/`의 성장도 같은 문법: 한 이벤트원이 두 번째 파일을 낳으면 `handler/<이벤트원>/` 개념 폴더로 분할. 미리 파지 않는다.
- **같은 개념은 계층이 달라도 같은 철자** — `lounge_post_manage` ↔ `manage_lounge_post` 같은 어순 불일치 금지. ("두 번째 개념" 식별·철자 일치의 판별 배정은 `undecidable.md` §9.)

## §3. 골격 완비 규칙 — 비어 있어도 형태를 유지한다

BC를 만들면 **4계층 폴더와 모든 표준 종류 폴더를 항상 생성한다 — 비어 있어도 둔다. 선택 폴더는 없다** (규약 §5, 사용자 확정). 트리의 형태 자체가 규약이므로 빈 폴더가 "이런 종류가 올 자리"라는 안내 역할을 한다. 폴더는 무조건, 코드는 필요할 때만.

| 계층 | 항상 생성하는 종류 폴더 (전부) |
|---|---|
| `domain_layer` | `<aggregate>/` + 애그리거트 루트 `<aggregate>.py`(항상 생성) + `entity/`·`value_object/`·`enum/`·`domain_service/`·`specification/` — `exception.py`는 첫 예외 때(골격 대상 아님) |
| `application_layer` | `use_case/`·`view_model/`·`state/`·`shared_state/`·`service/` |
| `infra_layer` | `data_source/`·`repository/`·`service/` |
| `presentation_layer` | `view/`·`section/`·`widget/`·`ui_extension/` |

- 빈 폴더 표지: `web/` 아래 Python 경로(design_system·static 제외)는 전부 `__init__.py`를 둔다(Python 패키지 표지 겸 빈 폴더 표지 — git은 빈 디렉터리를 추적하지 않는다). design_system·static의 빈 폴더에는 `.gitkeep`을 둔다.
- 개념 1차로 분할된 경우(§2) 표준 종류 폴더는 **각 개념 폴더 안에** 완비한다.
- `web/root/`는 BC 골격 비적용 — 자체 골격(역할 4폴더 + scaffold 하위 `view/`·`view_model/`·`state/`)을 비어 있어도 항상 생성한다.
- design_system 골격(foundation·theme·component·util 4폴더 + foundation 7파일 자리)도 같은 정신으로 항상 생성한다.
- BC 루트 직속에는 `<bc>_router.py`·`<bc>_navigator.py` 둘만 온다(+ 패키지 표지 `__init__.py`·국소 `ruff.toml`) — `application/` 직속은 BC(또는 area) 폴더만(조립 파일 금지). area 폴더 자체는 골격 비대상이다(§1 area 핵심 사실 — 직속은 BC 폴더만·빈 area 금지) — BC 골격은 area 유무 무관 동일하게 완비한다.
- **`web_test/`는 골격 완비의 명시적 예외 — sparse다.** "선택 폴더 없음"은 `web/` 한정이다: `web/`는 빈 폴더로 자리를 안내하지만 `web_test/`는 *빈 미러 폴더·빈 테스트 파일을 만들지 않는다* — 테스트는 SUT가 생긴 자리에만 둔다(§1 web_test/ 핵심 사실). 빈 슬롯을 채우려는 유혹이 헛테스트(vacuous)를 부르기 때문이다(테스트 규율은 discipline-test). 미러 배치 자체는 리지드 골격 검사가 아니라 discipline-reviewer 감사 대상이다(nav·fixture·common·VM-unit 등 '미러'가 자명하지 않은 자리가 있어 false-FAIL·게이밍을 피한다).
- **타입 강제 국소 lint** — 골격을 만들 때 dddjango-web 생성 영역 루트(BC `application/<bc>/` 또는 `application/<area>/<bc>/`·`common/`·`root/` — `.py`가 없는 `design_system/`은 제외)마다 `ruff.toml`을 생성해 타입 전면 명시(implementation-python §2 일탈3)를 *그 폴더에 국소* 강제한다. **호스트 루트 ruff 설정(`ruff.toml`·`pyproject.toml`의 `[tool.ruff]`)은 절대 수정하지 않는다** — ruff는 파일마다 가장 가까운 설정 파일 하나를 쓰고 하위가 부모를 *대체*하므로(병합 아님 — `extend`를 쓰면 부모를 잇게 되므로 쓰지 않는다) 템플릿에 규칙을 전부 명시한다(plugin 경계 — 호스트 기존 lint 정책 무파괴). 코드 생성물은 없으므로 exclude 대상도 없다:

```toml
# dddjango-web 생성 폴더 국소 — 호스트 루트 미수정. ruff는 가장 가까운 설정 하나만 쓰고 부모와 병합하지 않는다
# (extend를 쓰지 않는다 — 쓰면 호스트 규칙을 잇는다). 그래서 규칙을 전부 여기 적는다.
# 주의: ruff가 설치돼 있지 않으면 이 파일은 아무것도 강제하지 못한다(G0 전제조건 검사가 고지).
# ANN은 함수 인자·반환 타입만 본다 — 이름의 첫 대입 타입은 ruff가 못 잡는다(implementation-python §2).
[lint]
select = ["E4", "E7", "E9", "F", "ANN"]
```

## §4. 명명 규약 총괄표

공통 원칙 (규약 §7.1):

1. **파일명 = 주 선언명의 snake_case.** 한 파일에 주 선언 하나 (도메인 `exception.py`는 예외). View 주 선언 밖에는 architecture-ui §2의 private 필드 전용 타입 Protocol만 동거한다(확정된 Protocol 베이스 하나·class keyword/데코레이터 없음·값 없는 단순 이름 필드 annotation만·실행식 없음). 주 선언이 클래스가 아닌 파일(view 함수·ui_extension 필터 모듈·router 모듈·템플릿·CSS)은 아래 표의 이름 규칙을 따른다.
2. **종류는 폴더가 결정하고, 접미사가 그것을 재확인한다.** 접미사 판별은 긴 것 우선 — `_shared_state.py`는 shared_state 종류이지 state 종류가 아니다.
3. **화면 삼총사는 같은 접두**: `<화면>_view.py`(+ `<화면>_view.html`) ↔ `<화면>_vm.py` ↔ `<화면>_state.py` 1:1:1 대응. 조각(버튼) 단위 VM도 동일(`chat_request_btn_view` ↔ `chat_request_btn_vm`). 검사 방향은 **VM 기준** — VM이 존재하면 같은 접두의 view·state가 대응해야 하며, VM이 필요 없는 정적 view(약관·안내)는 VM·State 없이 허용. **접두 `<화면>`은 view 파일 stem에서 `_view`를 뗀 것이다** — view=`weekly_forecast_view.py`면 접두는 `weekly_forecast`이고 VM·State는 `weekly_forecast_vm.py`·`weekly_forecast_state.py`(클래스 `WeeklyForecastVM`·`WeeklyForecastState`)다. 접두에 `_view`를 끼운 `weekly_forecast_view_vm.py`·`weekly_forecast_view_state.py`(클래스 `…ViewVM`·`…ViewState`)는 **금지** — `_view_state.py`는 백스톱 NM2 deny 접미사이고 `…_view_vm`은 짝 view 부재로 NM4가 발화한다.
4. **UseCase는 화면이 아니라 도메인 개념 단위로 짓는다** — 여러 VM이 하나의 UseCase를 공유한다 (판별 배정은 `undecidable.md` §8).
5. **도메인 종류 명명은 dddjango 원형과 동일** — specification은 풀네임 `_specification`(`_spec` 축약 금지), 도메인 서비스는 `_service`. specification의 평가·조합은 Model(UseCase 이하)에서만 — VM이 도메인 판정을 직접 수행하지 않는다(판정 소유 상세는 architecture-ddd §5·`undecidable.md` §8).
6. **상태를 갖는 동작(State 조립·세션 보관·시그널 수신 연결)은 ViewModel 3변종(VM·SharedState·Service)과 root의 2변종(root_vm·root handler)에만.** UseCase·Repo·DataSource는 무상태 plain class — 사용처에서 직접 생성(DI 없음, 규약 §9-13).

총괄표 (규약 §7.2):

| 위치 | 이름 기준 (접두) | 파일명 | 주 선언 |
|---|---|---|---|
| BC 루트 라우터 | BC명 | `<bc>_router.py` | `urlpatterns` + `app_name = "<bc>"` + `class <Bc>Routes`(URL name 상수) |
| BC 루트 내비게이터 | BC명 | `<bc>_navigator.py` | `class <Bc>Navigator` |
| root `router/` | 고정 | `root_router.py` | 모듈 전역 **`urlpatterns`** (plain — 전 BC router include) |
| root `scaffold/` — 삼총사 | 고정 접두 `root` | `root_view.html`·`root_vm.py`·`root_state.py` (게이트 화면은 `root_<게이트>_view.py`·`.html` 등) | `RootVM`·`RootState` (+ context processor 함수 `root_context`) |
| root `handler/` | 이벤트원 | `root_<이벤트원>_handler.py` | `Root<이벤트원>Handler` |
| root `initializer/` | 고정 | `root_initializer.py` | `RootInitializer` (+ 필터 조립 `register = Library()`) |
| 애그리거트 루트 | 애그리거트명 | `<aggregate>.py` (폴더 직속) | 애그리거트명 |
| domain `entity/` | 개념명 (단수 명사) | `<개념>.py` | 개념명 |
| domain `value_object/` | 개념명 | `<개념>.py` | 개념명 |
| domain `enum/` | 개념명 | `<개념>.py` | 개념명 |
| domain `domain_service/` | 행위·정책 | `<행위>_service.py` | `<행위>Service` |
| domain `specification/` | 규칙 풀네임 | `<규칙>_specification.py` | `<규칙>Specification` |
| 도메인 예외 | 고정 | `exception.py` (폴더 직속) | `*Exception` 모음 |
| app `use_case/` | **도메인 개념** (화면 금지) | `<개념>_use_case.py` | `<개념>UseCase` |
| app `view_model/` | **화면** — view와 동일 접두 | `<화면>_vm.py` | `<화면>VM` |
| app `state/` | 노출 주체와 동일 접두 | `<화면·관심사·기능>_state.py` | `…State` |
| app `shared_state/` | 공유 관심사 | `<관심사>_shared_state.py` | `<관심사>SharedState` |
| app `service/` | 플랫폼 기능 | `<기능>_service.py` | `<기능>Service` |
| infra `data_source/` | 개념 — repo와 동일 접두 | `<개념>_data_source.py` | `<개념>DataSource` |
| infra `repository/` | 개념 | `<개념>_repo.py` | `<개념>Repo` |
| infra `service/` | SDK·기능 | `<기능>_service.py` | `<기능>Service` |
| pres `view/` | 화면 (VM 보유 단위) | `<화면>_view.py` + `<화면>_view.html` | 함수 `<화면>_view` (+ 같은 화면의 조각 응답 함수 `<화면>_<조각>_fragment`) |
| pres `section/` | **소속 화면 접두 필수** | `<화면>…_section.html` | — |
| pres `widget/` | 부품 — 화면 이름 금지 | `<부품>_widget.html` | — |
| pres `ui_extension/` | 도메인 개념 | `<개념>_ui_extension.py` | `register = Library()` + 필터 함수 |
| pres 조각 CSS | 템플릿과 같은 stem | `web/static/application/[<area>/]<bc>/<조각 stem>.css` | — |
| root scaffold 조각 CSS | 템플릿과 같은 stem | `web/static/root/<조각 stem>.css` | — |
| UI 동작 JS | 기능 | `web/static/js/<기능>.js` | — |
| ds `foundation/` | 토큰 종류 | `app_<토큰>.css` | 변수 접두 `--color-*`·`--typography-*`·`--spacing-*`·`--radius-*`·`--shadow-*`·`--duration-*`/`--easing-*`·`--asset-*` |
| ds `component/<군>/` | 수식·변형 | `<수식>_<군>.html` + `<수식>_<군>.css` | CSS 클래스 접두 `<수식>-<군>` (무접두 — 종류 접미사가 구별자) |
| ds `theme/` | 고정 | `app_theme.css` | — |
| common 4종·ds `util/` | 기능·도구 | 파일명 = 주 선언명 snake_case (`service/`는 `<기능>_service.py`) | 주 선언명 |
| 테스트 | SUT 경로 | `web_test/<web/와 같은 경로>/<sut>_test.py` | — |

- 폴더명은 `repository/`(전체 표기), 파일 접미사는 `_repo.py`(축약) — 혼동 주의.
- 라우트 path·name 문자열 리터럴은 `<bc>_router.py` 안에서만 등장한다 — `class <Bc>Routes`(클래스 상수)로 묶고 일반 이동의 navigator·root_destination_handler는 이 이름 상수를 참조한다. **기본 홈 주소의 좁은 예외**: 활성 URLconf와 무관하게 반환해야 하는 **프로젝트의 기본 홈 목적지 한 건**만 예외로 둔다. 명세에 소유 BC·router 상수·navigator 메서드를 적고, 그 단일 상수를 소유 navigator가 가공 없이 반환한다. 다른 BC는 그 navigator를 호출한다. 상수 복제·타 BC router 직접 import(IM5)·BC별 기본 주소·개별 화면·조각 주소로의 확대는 금지한다. 나머지 named href의 역참조 실패를 이 주소로 폴백하지 않는다(`NoReverseMatch`를 잡아 아무 주소로 넘기기 금지). URLconf 독립은 href 반환에 URL 이름 등록이 필요 없다는 뜻이며 모든 격리 URLconf에서 그 주소를 GET할 수 있다는 뜻은 아니다. 템플릿은 URL name을 직접 쓰지 않고 State가 준 href를 쓴다.
- `--typography-*`는 `font` 줄임 묶음 값이다 — 쓰는 쪽은 `font: var(--typography-title)`이고, 같은 규칙에서 그 뒤에 `font-*`를 다시 선언하지 않는다.

## §5. import 방향 — 계층 매트릭스·교차 BC 4채널·root 방향 규칙

**참조는 세 경로를 함께 센다** — Python `import`, 템플릿 `{% include %}`·`{% extends %}` 경로, CSS 참조(템플릿의 `<link href="{% static … %}">`·CSS `@import`·`url()`). presentation 조각 CSS(`web/static/application/[<area>/]<bc>/`)는 그 BC presentation_layer로 센다. import는 `web.`으로 시작하는 절대 경로만 쓴다(상대 import 금지) — 백엔드 `application.`·`framework.` import는 0이다.

**BC 내부 계층 매트릭스** (규약 §3.7 — 행=from, 열=to). `common/`은 전 계층에서 import 가능하되 **domain_layer만 예외**(순수 Python — `django`·common 포함 비순수 import 금지 — 단 `common/util/json_field.py` 하나는 허용: 직파싱 단일 출처, dddart에서 모델이 json_serializable 패키지를 쓰던 자리). **`design_system/` 참조 허용 위치는 닫힌 열거**(러너와 동일): presentation_layer 전체 · `root/scaffold/` · design_system 내부 — **그 외 전부 금지**(router·navigator·handler·initializer·application_layer(VM·SharedState·UseCase·State)·infra·domain·common — 시각 토큰 매핑이 VM으로 새면 ui_extension "유일한 자리" 규칙이 무너진다). web의 router는 화면 전환 연출을 갖지 않으므로(전환 연출은 CSS·HTMX 교체의 일) 허용 위치에 들지 않는다:

| from \ to | domain | application | infra | presentation | BC 루트 |
|---|---|---|---|---|---|
| domain | ✓ | ✗ | ✗ | ✗ | ✗ |
| application | ✓ | ✓ | ✓ — UseCase→Repo·infra service만 | ✗ | ✓ — **VM만**→navigator (service는 금지: 비화면 이벤트의 내비는 root_destination_handler 소유) |
| infra | ✓ | ✗ | ✓ | ✗ | ✗ |
| presentation | ✓ | ✓ — view→VM·State·SharedState만 | ✗ | ✓ | ✓ — navigator (view `.py`만 — 템플릿은 State의 href) |
| BC 루트 | ✗ | ✗ | ✗ | router→view만(path 바인딩) — navigator는 View import 금지 | ✓ |

셀 규칙의 동작 의미(왜 VM만 navigator를 부르나, view는 무엇을 부르나)는 architecture-state §2(VM 규율)·architecture-ui §2·§3(presentation 규율) 소유다.

**교차 BC 통신 — 4채널만 허용** (규약 §9-3, 백스톱 검사 대상):

| # | 채널 | 비고 |
|---|---|---|
| ① | 도메인 타입 import | 엔티티·VO·enum (예: channel이 member의 `Candidate` 사용) |
| ② | 타 BC UseCase 호출 | 행위·데이터 접근의 단일 관문 |
| ③ | 타 BC navigator 호출 | 일반 이동은 이름 기반 — href를 얻는다. 기본 홈 주소 한 건은 architecture-ui §6의 소유 navigator를 호출한다 |
| ④ | 타 BC view 임베드 | `view/`는 전부 임베드 가능 — 임베드는 부모 템플릿의 자리 하나 `<div hx-get="{{ state.<자식>_embed_href }}" hx-trigger="load" hx-swap="outerHTML">`다(href는 부모 VM이 ③으로 자식 BC navigator의 `<화면>_embed_href()`에서 받음). 자식 view의 셸 없는 첫 렌더 `<화면>_embed_fragment`가 자기 VM을 스스로 부르므로 임베드는 배치만 |

**금지**: 타 BC의 Repo·DataSource 직접 호출, 타 BC VM 호출, 타 BC SharedState 읽기·구독(root만 면제), 타 BC section·widget 템플릿 include·ui_extension 사용(부품 재사용은 design_system 승격 경유). 채널 *선택* 절차(어느 채널이 적정한가)는 architecture-ddd §2·architecture-state §7 소유.

**root·common·전역 방향 규칙**:

- **`root/`를 아는 곳은 `web/apps.py`·`web/urls.py`·호스트 settings(문자열 경로)뿐.** BC가 root를 알면 전체를 알게 되어 격리가 무너진다. 유일한 예외는 페이지 템플릿의 `{% extends "root/scaffold/view/root_view.html" %}` 하나다 — Django 템플릿 상속은 자식 페이지가 부모 셸을 가리키는 방향이라 셸이 화면을 임베드하는 구조를 그대로 옮길 수 없다. root/ 내부의 상호 참조는 자유.
- **템플릿 상속 채널**: 페이지 템플릿(`presentation_layer/view/*_view.html`·root 게이트 화면 `root/scaffold/view/root_*_view.html`) → `root/scaffold/view/root_view.html`만 · 조각 템플릿(section·widget·design_system component) → design_system component(`design_system/component/**/*.html`)만이다. 조각의 extends는 slot = block 채우기다 — 공용 부품이 내놓은 이름 붙은 `{% block %}`만 채우며, 그 조각 파일은 그 부품의 채워진 사례 하나다(같은 파일 안에 다른 마크업·두 번째 extends·block 밖 내용 금지). 조각이 root_view.html을, 페이지가 component를 extends하면 위반이다(백스톱 IM26).
- **root → BC는 자유**(전부 아는 것이 존재 이유 — 4채널 면제). 단 Model 방향 규율은 동일: root도 BC의 **UseCase만** 호출(Repo·DataSource 직행 금지). `root_initializer` → BC `presentation_layer/ui_extension/<개념>_ui_extension.py`(템플릿 필터 조립 — 시동 배선)는 Model 접근이 아니라 이 규율 밖이다.
- **`common/`은 `application/`·`root/`를 import하지 않는다.** common은 모두가 아는 곳, root는 모두를 아는 곳.
- **`design_system/`은 `application/`·`root/`를 참조하지 않는다.**
- **`web/apps.py`·`web/urls.py`는 엔트리포인트 최소형** — `WebConfig.ready()`는 `root_initializer` 시동 한 줄, `web/urls.py`는 `root_router`의 urlpatterns를 내보내는 한 줄. 전역 에러는 호스트 루트 urls의 `handler404`·`handler500`이 `root_error_handler`로 위임한다 — 빈 핸들러로 전역 에러를 침묵 삼키지 않는다; `root_error_handler`도 받은 에러를 침묵 삼키지 않고 최소한 관찰 가능하게 둔다(로그 — 외부 크래시리포트 SDK 연결은 앱 소관·§7 반송표). 테마는 `root_view.html`의 `app_theme.css` 링크 한 줄. import 화이트리스트: root/·django 계열 — 정확한 경계는 러너가 단일 출처(§8). 역방향(`application/`·`common/`·`design_system/`이 `apps.py`·`urls.py`를 import) 금지 — BC 무관 전역 인스턴스(logger 등)는 common 소속이다.
- domain_layer는 `django` import 금지 — `dataclasses`·`enum`·`typing`·`datetime`·`decimal` 등 순수 표준 라이브러리만. 단 domain → common은 `common/util/json_field.py` 하나만 예외다(직파싱 단일 출처 — dddart에서 모델이 json_serializable 패키지를 쓰던 자리).

## §6. common·design_system 입장 판별

**common은 모든 BC가 의존하는 곳이다 — 따라서 어떤 BC도 알면 안 된다.** 편의 버킷이 아니다. 입장 판별 — 위에서부터, 처음 해당하는 것이 답 (규약 §6):

| # | 질문 | 답 |
|---|---|---|
| 1 | BC의 도메인 어휘를 아는가? | common 금지 → 그 BC로 (enum은 `domain_layer/.../enum/`, 공유 상태는 `shared_state/`, 서버 데이터 접근은 `data_source/`) |
| 2 | 모든 BC를 알아야 하는 조립 코드·조립 화면인가? (URL 조립·외부 진입 디스패치·전역 요청 수명·시동·루트 스캐폴드) | 합성 루트 `web/root/`. 단 루트 스캐폴드가 아닌 다수 BC 투영 화면은 자기 이름의 일반 BC |
| 3 | 시각 UI 부품인가? | `design_system/` |
| 4 | 그 외 — BC 무관 횡단 기반 | **common** |

- 헷갈리면 import 방향으로 가른다: `application/`을 import하면 조립 코드라 root, BC들이 이것을 import하면 common.
- **common은 살아있는 상태를 갖지 않는다 — `common/`에서 상태 동작(시그널 수신·세션 쓰기·변경 통지) 금지**(백스톱 proxy). proxy가 못 잡는 가변 모듈 전역(세션 키 보관자 류)도 변경 통지·구독을 노출하기 시작하면 common 실격 — 정체를 따져 제자리로(BC 어휘 있으면 그 BC shared_state, 전 BC 배선이면 root). 판별 배정은 `undecidable.md` §7.
- common 종류는 **4종 고정**: `network/`·`service/`·`enum/`·`util/`. `provider/` 같은 비표준 종류 금지(로컬 저장 층이 없으므로 `local_database/`도 없다).
- common이 BC 일을 필요로 하면(401 처리 등) 직접 import 대신 **콜백 주입** — 콜백·추상만 정의하고 구현 연결은 `root_initializer`(조립)가 담당. 세션 신원 이월도 같은 원칙이다: `root_request_handler`(미들웨어)가 `process_view`에서 — view 모듈이 `web.`으로 시작할 때만 — 요청 세션 키를 `common/network`의 contextvar에 심고(토큰은 `request`에 두었다가 `__call__`의 응답 뒤 reset), common은 BC·root를 모른다. 같은 프로세스 API 호출이 닿는 백엔드 view(모듈이 `web.` 밖)에는 아무것도 하지 않아 미들웨어 재진입이 끊긴다(architecture-state §10).

**design_system — BC 어휘도 도메인 어휘도 모르는 시각 요소**:

- `foundation/` 7토큰이 시각 값의 **단일 출처** — BC presentation·root scaffold·component의 템플릿·CSS에서 색 리터럴(`#…`·`rgb(…)`)·생 글자 스타일(`font-size`·`font-family` 등 리터럴)·연출 시간(`transition`·`animation`의 `ms`/`s` 리터럴 — 전환·애니메이션·press 피드백은 `--duration-*`/`--easing-*` 토큰) 금지. *비시각* duration(네트워크 timeout·디바운스 — `hx-trigger`의 `delay:` 등)·구조 명명 값(`transparent`·`currentColor`처럼 브랜드 시각값 아닌 것)은 제외 — 상세 경계는 architecture-ui §7. `font-size`는 아이콘 글리프에도 foundation 토큰으로 쓴다. 글리프 크기는 `app_spacing.css`의 `--spacing-icon-*`로 정의하고 `font-size: var(--spacing-icon-*)`로 인용한다. `width`·박스 `height` 등 비-typography 크기는 architecture-ui §8의 추출값 직접 인용 규칙을 따른다.
- `component/`는 부품군 1차 — **부품군 폴더 = 파일 접미사 = CSS 클래스 접두의 군**(`button/` 안은 `*_button.html`+`*_button.css` → 클래스 `<수식>-button`). 축약(btn)·직속 파일·정크드로어 군(`widget/`·`etc/`) 금지. 분류 안 되는 부품이 생기면 새 부품군 폴더를 만든다.
- 컴포넌트 표시 경로 규율(전역 JS 진입 함수 `show()` 금지 포함)은 architecture-ui §7 소유 — 규칙 본문은 그 스킬에만 둔다.

## §7. 표기 표준화 — drift와 교정

HaffHaff-App 전수 조사에서 발견된 변형들(web 표기로 옮김). dddjango-web은 **새로 만드는 코드에서 아래 표준만 쓰며**, 백스톱이 변형을 잡는다. 기존 코드의 변형은 면제가 아니라 **빚**이다 — 기능 요청이 손대는 파일과 그 파일을 부르는 곳의 빚은 G0 빚 질문으로 정해 슬라이스 0(동작 불변)에서 먼저 정리하고, 그 밖의 기존 코드 수정은 요구하지 않는다(§8 빚 모드).

**적용 경계 — 표기는 파일, 구조는 단위**: ⓐ **새로 만드는 파일은 어느 폴더에 두든 표준 표기**(파일명·접미사·클래스)만 쓴다 — 아래 표의 변형 표기(`_app.py`·`_bridge.py` 류)로 새 파일을 만들지 않는다. 백스톱 명명 검사는 added 파일 기준으로 폴더와 무관하게 발화한다. ⓑ **폴더 구조의 표준 강제는 신규 단위**(BC·개념 폴더·화면 삼총사)**부터** — 레거시 단위 내부에 파일을 추가할 때 표준 폴더 신설을 강제하지 않으며(구조 검사는 added 디렉터리 기준), 게이트는 기존 파일의 개명·이동을 요구하지 않는다(규약 §8 문면 그대로 — "새로 만드는 코드에서 표준만") — 기존 파일의 위반은 빚으로 따로 다룬다(위 문단 · §8 빚 모드). ⓒ **표준 트리 밖 옛 배치 파일**(`web/root`·`web/application`·`web/common`·`web/design_system`·`web/static`·`web/{__init__,apps,urls}.py` 밖)은 **층 판정 불가 레거시**다 — 그 파일에 줄을 더해도 층 규칙 import 검사(«X는 Y만» 허용 자리·층별 금지)는 불발화하고, 층 무관 import 검사(상대 import·백엔드 `application.`/`framework.` import·HTTP 호출 표면·DataSource 밖 API 주소 리터럴)는 그대로 건다. 옛 배치 단위 안에 표준 표기로 둔 파일은 그 역할로 알아본다 — `view/` 폴더의 템플릿은 페이지(기능 JS·htmx core 실행 태그의 자리 — 조각 폴더와 공식 SDK 로드는 그대로다), `<개념>_data_source.py`는 DataSource(API 주소 리터럴의 자리), 옛 배치 최상위 폴더 직속 `<폴더>_router.py`는 라우터(`path()`·라우트 리터럴·`class <Bc>Routes`의 자리)다. 옛 배치 파일 자체는 빚이다 — 빚 스캔이 파일마다 `ST0` 키로 내고, 빚 범위(손대는 파일 + 부르는 곳)에 든 것은 슬라이스 0이 새 트리로 옮긴다(옮긴 파일은 새 트리의 층·명명·골격 규칙을 처음 받는다 · 범위 밖 옛 배치는 그대로 둔다):

| 발견된 변형 | 표준 |
|---|---|
| `viewmodel/` | `view_model/` |
| `repo/` (폴더명) | `repository/` |
| `presentation_later/` 류 오타 | `presentation_layer/` — 계층 철자 정확히 |
| `my_louge_post/` 류 개념 폴더 오타 | 개념 철자 통일 |
| 계층 간 어순 불일치 (`lounge_post_manage` ↔ `manage_lounge_post`) | 같은 개념 같은 철자 |
| `container/` (presentation 비표준 종류) | view/section/widget 3종으로 정리 |
| 능동 service가 infra에 (시그널 수신·UseCase 호출·상태 노출) | 이벤트 구동·UseCase 호출 service는 `application_layer/service/` |
| `<화면>_view_state.py` 변형 | `<화면>_state.py` — `view`를 끼우지 않는다 |
| state 폴더 파일의 `_state` 접미사 누락 | `_state.py` 필수 |
| section·widget의 VM 호출 (커스텀 템플릿 태그로 우회 포함) | dumb 유지 — 상태가 필요하면 view+vm 쌍으로 승격 |
| navigator가 presentation_layer에 | BC 루트 `<bc>_navigator.py` — 일반 이동은 이름 기반, 기본 홈 주소 예외는 architecture-ui §6, View import 금지 |
| BC 어휘 enum이 common에 | 그 BC의 `domain_layer/.../enum/` |
| 전 화면 URL name 상수가 common에 | `<bc>_router.py`로 해체 — URL path·name의 단일 출처 |
| BC 공유 상태가 common에 | 해당 BC의 `application_layer/shared_state/` |
| 교차 BC 화면 갱신 버스 (전역 `HX-Trigger` 이벤트 하나로 여러 BC 조각을 다시 부르는 `refresh_notifier` 류) | 종류 폐지 — 데이터 변화는 그 BC SharedState로, 요청·세션 수명발 갱신은 root handler→BC service (처방 상세는 architecture-state §8) |
| 위장 이벤트 신호 (`scroll_to_top_notifier` 류) | 종류 폐지 — 탭 재탭 스크롤톱은 root_view가 직접 처리, BC는 신호를 듣지 않는다 |
| 조립 코드가 common/service에 | 합성 루트 `root/handler/`의 `root_<이벤트원>_handler.py` |
| 시동 코드가 web 루트 떠돌이 파일 (`apps.py`에 직접 등) | `root_initializer.py` — 부트스트랩도 BC UseCase 호출로 |
| 조립 코드의 Repo·DataSource 직접 접근 (게이트 미들웨어 등) | root도 Model 규율 적용 — UseCase 경유 |
| 조립 파일이 `application/` 직속에 | `web/root/` — application/ 직속은 BC(또는 area) 폴더만 |
| 동일 접두 BC군이 평면에 나열 (`driver_*`·`rider_*` 류 역할·서브도메인 축) | (선택) `application/<area>/<bc>/` 그루핑 — area는 순수 시각 네임스페이스(§1 area 핵심 사실)·G0 사용자 판정으로만 도입 |
| 전역 에러 배선 산재 (빈 `handler500`·미들웨어의 `except: pass` 등) | `root/handler/root_error_handler.py` |
| 전 BC 목적지 enum (알림 BC에 전 BC 목적지 어휘) | 외부 진입 링크의 BC URL 정규화로 소멸 — 목적지 어휘는 각 BC URL path |
| 파일명 오타 (`certificcation`·`servcie` 류) | 철자 교정 |
| 타이포 값이 Python 상수·템플릿 인라인 스타일에 (글꼴 크기 상수 등) | `foundation/app_typography.css` |
| component 정크드로어·직속 파일 (`widget/`·`etc/`) | 부품군 폴더로 해체 (input·feedback 등) |
| `btn/` 축약·`_btn`/`_button` 혼재·`ds_` 접두 | `button/`·`_button.html`·무접두 통일 |
| design_system 오타·토큰 표기 혼재 (`--WHITE`/`--gray_50` 류) | 철자 교정 · 토큰 변수는 §4 접두 규칙의 kebab-case |
| state로 위장한 이벤트 (`*_added` 과거형 사건명·시각 값 핵·센티널 초기값) | 과거형 사건명 shared_state 금지 (판별 배정은 `undecidable.md` §10) |
| 셸이 타 BC 화면을 흡수 | 화면 귀속 규칙 — UseCase 소속 BC로. 탭 셸은 `root_*`, 다수 BC 투영 화면은 자기 이름 BC |
| 교차 BC VM 호출·화면 삼총사 분할 | 4채널만(§5) — 삼총사는 한 BC에 |
| `app/`·`_app.py`·`*App` | `use_case/`·`_use_case.py`·`*UseCase` |
| `bridge/`·`_bridge.py`·`*Bridge` | `shared_state/`·`_shared_state.py`·`*SharedState` |
| `block/`·`_block.html`·`*Block` | `section/`·`_section.html` |
| UseCase의 UI 직접 호출 (오류 템플릿 render·`HttpResponse` 반환 등) | UseCase는 Either만 반환 — 에러 표시 채널은 architecture-state §4(에러 2채널) |
| VM의 `HttpRequest` 보유 | navigator 헬퍼 경유 — `HttpRequest` 보유 금지 |
| 화면 state가 `domain_layer/<agg>/state/`에 | `application_layer/state/` |
| domain_layer 평면 (애그리거트 폴더 없음) | 애그리거트(개념) 1차 |
| `apps.py`·`urls.py` 비대 (시동 로직·URL 분기 조립·전역 인스턴스) | 엔트리포인트 최소형 — 시동은 root_initializer, URL 조립은 root_router, 전역 인스턴스는 common |
| BC 어휘 service가 common에 | 그 BC `application_layer/service/` |
| common 비표준 종류 폴더 | 4종 외 금지(§6) — 내용물은 입장 판별대로 재배치 |
| `appbar/` | `app_bar/` |

## §8. 백스톱 연동 — 러너·게이트

dddjango-web 파이프라인은 이 하우스룰의 기계 판별 가능 부분을 **결정적 러너**가 게이트에서 검사한다 (백스톱 설계 §2·§3이 단일 근거 — 개별 검사의 열거·모사는 금지, 검사 의미가 바뀌면 러너가 단일 출처):

```
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> \
  [--diff-base <commit>] [--all] [--slice-end] [--only st,im,nm,cy,tg,pj,md,pu,wv|<검사ID>…] [--update-baseline] [--design-build <산출물 폴더>]
```

(파이프라인에서는 Coordinator가 플러그인 루트를 해소해 호출한다 — 에이전트가 경로를 추측하지 않는다.)

- 검사 패밀리 4종: **구조(ST)·import(IM)·명명(NM)·순환(CY)**(+ 시험 존재·재현성·방법 TG·토대 PJ·모델 형태 MD·출력 안전 PU·공식 SDK 등재 WV — §9 · 합계 86종은 러너 머리말이 단일 출처). 승인 유입도 발견이며 종료 코드 밖이고 보고 의무가 있다 — 남은 blocker는 반송(오탐으로 보이는 발견의 처분은 Coordinator의 «검사기 이의» — 에이전트가 스스로 면제하지 않는다).
- **게이트 의미론**: 구조·명명은 **added**(새로 만든 파일·디렉터리)만, import는 touched 파일의 **added 줄**만, 골격 완비는 **신규 단위**(새 BC·애그리거트·개념 폴더)만, TG2·TG3은 기준 commit→현재 작업 트리(staged·unstaged·커밋된 변경 포함)의 root 상대 diff에서 영구 시험·지원 파일을 수집하되, **새쪽 추가 줄과 검출 사슬의 실제 표현식·대입·I/O·실행·비교 위치가 겹칠 때만** 발화한다. TG2는 해당 입력 식·정의·대입·호출 함수 이름, TG3 비교는 비교 두 입력·두 screenshot 생성 출처·호출 함수 이름(==/!=는 연산자) 위치로 좁힌다. 호출·함수·클래스·블록 전체나 비교의 메시지·다른 키워드·JS 미사용 argv·같은 숫자 행끼리의 비교를 사슬 대응으로 쓰지 않는다. **안전한 재대입·출처 무효화 줄의 삭제로 같은 sink에 새 금지 사슬이 닿는 경우**는 지원 정적 범위의 기준판↔현재판 사슬 비교로 발화한다. 시험→시험 순수 rename은 새 줄 0이며 내용 변경은 old→new 새쪽 hunk를 쓴다(명시 rename 판별·D/A 동일 blob 이동 대응). copy·시험 밖에서 영구 시험으로 편입·기준점에 없는 비무시 미추적은 전 줄 새 줄이고, 기준점 파일이 미추적이 된 경우는 기준판과 비교한다. 기록 폴더(`.dddjango-web/`·`.dddjango/`) 아래 파일은 추적 여부와 무관하게 영구 시험·지원 파일 후보가 아니다 — 그 사본을 영구 시험으로 옮겨 오면 편입이다(전 줄 새 줄). 삭제된 파일은 검사하지 않는다. 모듈 상수→함수 내부 등 지원 흐름의 원점·중간 대입 위치와 실행 JS의 Python 문자열 정의·중간 대입·실행 인자 및 디코드 문자→원본 좌표를 보존한다. 확정된 Node 명령은 `--` 옵션 종료·스크립트 entry point 앞의 eval/print 옵션만 실행 JS로 추출하고, 코드·옵션 표지·JS I/O에서 쓰지 않은 argv를 일반 Python 경로로 다시 판정하지 않는다. JS는 키워드 뒤 정규식의 가짜 호출을 제외하며 세미콜론 없는 ASI 대입의 screenshot 비교도 판정한다. `with` 항목은 표현식 검사 뒤 해당 바인딩을 갱신하고 다음 항목을 검사한다. 함수 인자·반환·타 파일 전달 등 지원 밖은 감수 대상이며 추적 실패를 무관함의 증명으로 쓰지 않는다. G0 명시 시험 경로는 `git_snapshot`과 `--diff-base`를 같은 commit OID로 해소해 비교한 기록에서 수집한다(관례·pytest 설정 밖도 포함). 개별 build-state의 읽기·JSON·snapshot·`test_command` 형상(null·비문자열)/shell quoting 실패는 그 기록만 건너뛰고 다른 기록·관례 시험 수집은 계속한다. 기준점·old/new 대응·위치 해석 실패는 범위 미확정·미실행을 고지하며 파일 전체 검사로 퇴화하지 않고 `ctx.files`도 넓히지 않는다. 환경 변수 단언의 의미는 TG2 밖으로 감수·G2 표준 실행이 본다. 순환은 전역+베이스라인 래칫(`.dddjango-web/backstop-baseline.json`). → 게이트는 **이번 작업이 들인 위반**만 잡는다 — 기존 코드의 위반(drift)은 면제가 아니라 빚이며 아래 빚 모드가 다룬다. **표준 트리 밖 옛 배치 파일 = 층 판정 불가 레거시** — 층 규칙 IM은 불발화하고, 층 무관 IM(상대 import·백엔드 import·HTTP 표면·DataSource 밖 API 주소 리터럴)은 그대로 걸고, 옛 배치 단위 안에 표준 표기로 둔 페이지·DataSource·라우터는 그 역할로 알아본다(§7 ⓒ). 반대 방향(표준 트리 안 파일이 옛 배치 파일을 참조)은 그 표준 파일의 층 규칙으로 판정한다. 승인 목록이 있으면 그 산출물 폴더를 `--design-build`로 전달한다 — 검사를 다 돌린 뒤 W·F1·L로 증명된 승인 유입만 종료 코드에서 빼며 CY·WV·ST12·PU1·PU2는 늘 blocker다. TG2·TG3 발견의 승인 유입은 부모 측정 대신 **수신 증명**으로 가른다 — 기준 뒤 그 파일을 바꾼 첫 부모 걸음이 전부 승인 병합의 상류판 그대로 수신이고 작업 트리 현물이 그 판의 바이트 그대로일 때만이다(필터·줄 끝 변환 없이 대조한다 · 관례 시험 자리 — `web_test`·`test`·`tests` 폴더 아래와 `conftest.py` — 의 파일에만 서고, 레인이 손댄 현물 심볼릭 링크가 프로젝트 루트 밖을 가리키면 하지 않는다). 병합 뒤 레인이 그 파일을 더 고쳤으면 그 파일의 발견은 기준판 대비 그대로 이 레인 몫이다. 승인 유입도 발견이므로 G2 배너에 원문으로 올리고(발주자·호스트의 몫으로 남는다), 수신 증명이 선 시험 파일의 «자동 판정 밖 흐름» 고지만 이 레인의 discipline 감수 대상에서 빠진다.
- **슬라이스 끝 실행**(`--slice-end`): Phase 2에서 슬라이스가 끝날 때마다 커밋 전에 돈다(coder가 끝 래칫에서, Coordinator가 커밋 앞에서 — 실행문은 Coordinator가 준다). 86종 중 79종을 실행하며 TG2·TG3은 미루지 않는다. 뒤 슬라이스가 채울 짝·골격·미러·순환 검사(목록은 러너 요약 줄이 단일 출처)를 미루고 순환 기준선 파일을 만들지 않는다 — 미룬 검사는 G2 직전 실행(`--slice-end` 없이 86종 전부)이 본다. `--update-baseline`·`--only`·빚·치환 모드와 함께 쓰지 않는다. exit 0은 잔여 blocker 0이며 승인 유입도 발견이다 — 그 절의 원문·증명 M·부모 표지를 슬라이스 보고로 Coordinator에 전달해 G2 배너에 올린다. exit 2의 수정·반송은 남은 blocker 대상이고 exit 1은 미실행이다.
- **빚 모드**(러너 모드 — 검사 ID가 아니다):

  ```
  python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> --debt-scan [--json <경로>]
  python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> --debt-residual <산출물 폴더>
  python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> --subst-check <기준 커밋> <대상 커밋> [--names <명세>] [--except <경로>]… [--build <산출물 폴더>]
  ```

  `--debt-scan`은 web/ 전체(git 추적 + 미추적·비무시 파일)를 «모두 새 것»으로 보고 ST·MD·IM·NM·PU·WV 패밀리를 돌려 키 (검사, 경로)마다 `C<n>`을 매긴다(Phase 0 빚 스캔 — exit 0 = 빚 0[web/이 아직 없는 첫 실행 포함 — 비git이어도] · 2 = 빚 있음 · 1 = 실행 불능[web/이 있는 비git · web/이 심볼릭 링크이거나 git 밖·무시돼 우주가 빔]). CY(베이스라인 래칫)·TG(테스트 추가 — 동작 불변 정리 밖)·PJ(늘 검사)는 빚 모드에 넣지 않는다. 폴더 발견은 그 아래 파일마다의 키다 — 표준 트리 밖 옛 배치는 파일마다 `ST0` 키(§7 ⓒ), 허용 밖 디렉터리(ST3·ST5~ST8·ST10~ST12)도 그 아래 파일마다의 키다(폴더 키로 남는 것은 ST4 골격 미비와 `static/vendor/` 벤더 단위뿐). 브라운필드 허용 규범 — 기존 htmx core 설치 1개와 그 `root_view.html` 로드 태그(core 설치가 하나일 때) · 기존 단위의 골격 미비 — 은 빚으로 내지 않는다. **빚 정리의 범위는 이번 요청이 손대는 파일 + 그 파일을 부르는 곳**이다 — 그 범위의 키를 G0에서 묻고(지금 정리 → 슬라이스 0 · 출처 있는 미룸), 범위 밖 키는 동결본에만 남는다. `--debt-residual <산출물 폴더>`는 같은 의미론으로 다시 스캔해 `debt-g2.json`에 쓰고 `refactor-scope.md`의 마지막 `## G0` 절부터 순서대로 G0·G0 재승인 절의 ⓐ·요구 키를 더하고 `ⓐ 재상정` 절의 키를 뺀 집합이 사라졌는지 센다(G2 — exit 0 = 잔존 0 · 2 = 잔존 있음 · 1 = 판정 불가[마지막 `## G0` 절이 `debt-g0.json` 스캔보다 이르거나 · 스캔의 검사 집합·키 의미론이 지금 러너와 다름 — 플러그인 판 글자만 다르면 알림 한 줄을 내고 판정한다]). ⓐ·요구 키와 같은 폴더 발견에서 나온 범위 밖 파일 키가 남으면 «범위 밖 남은 빚»으로 보고만 한다(잔존이 아니다 — 범위가 옮긴 파일 몫은 끝났다). `--subst-check`는 슬라이스 0 끝에서 web/ 밖 테스트 변경(`web_test/` 포함)이 명세 슬라이스 0 절의 옛 경로·옛 이름 → 새 경로·새 이름 치환뿐인지 본다. 세 모드는 단독이다(`--diff-base`·`--all`·`--only`·`--design-build`·`--update-baseline`와, 그리고 서로 함께 쓰지 않는다 · `--json`·`--refactor`는 `--debt-scan` 전용 · `--names`·`--except`·`--build`는 `--subst-check` 전용).
- `--all`은 게이트 무시 전역 감사용 — 레거시 프로젝트에서 발견 폭주가 정상이며 파이프라인 게이트 용도가 아니다(빚 조사는 `--debt-scan`).
- 비git 폴백은 전역 검사로 퇴화 — 파이프라인 전제조건(G0)이 `git init`+초기 커밋을 제안하는 이유.
- **반송 패밀리 → 교정 절 백링크**: ST(구조) → §1 트리·§2 성장·§3 골격·§7 변형 / IM(import) → §5 / NM(명명) → §4 / CY(순환) → §5 교차 BC 4채널(신규 순환은 import 경로 재설계 — 채널 선택 절차는 architecture-ddd §2·architecture-state §7).
- **에이전트 분업**: 러너가 잡는 것(경로·import·명명·순환)은 흉내내지 말고 이 문서대로 만들면 통과한다. 러너가 못 보는 **의미 판별 18종**(view/section, BC 어휘, 판정·계산의 귀속, 살아있는 상태, 접두↔area 등)은 `undecidable.md`가 판별 절차·배정의 단일 출처다.

## §9. 공식 플랫폼 SDK — 등재·사본·로드

web 이 들이는 외부 JS 는 이것 하나뿐이다: 플랫폼 운영자가 자기 서비스 API 를 부르라고 직접 배포하는 브라우저 SDK 를 사용자가 G1 에서 한 번 승인하고 `web/sdk_registry.json` 에 등재한 것만 `web/static/vendor/<sdk_id>/<파일>` 에 운영자 원본 그대로 둔다. 그 밖의 제3자 JS(라이브러리)는 들이지 않는다 — 결과는 서버가 만드는 설계·평범한 링크·native 로 낸다. htmx core(`static/htmx/htmx.min.js` 2.0.10 고정 판)는 이 절이 아니라 G0 연결 설정 점검의 몫이다.

**자격**(모두):
① 배포자 = 그 서비스의 운영자
② 원본·문서 주소가 운영자 공식 도메인의 https(리다이렉트 최종 주소 포함). 공용 라이브러리 CDN(cdnjs·jsdelivr·unpkg·code.jquery.com·skypack·esm.sh·`/ajax/libs/` 경로 …)은 운영자 소유여도 아니다
③ 운영자 자기 문서 쪽이 그 원본 주소를 인용(도구가 직접 받은 원문으로 확인)
④ 라이선스·약관 확인
⑤ 승인된 요구의 결과가 서버·평범한 링크·native 로는 안 됨을 운영자 문서로 보임
⑥ 원본 그대로 한 파일이고 실행 중 다른 코드를 받아 실행하지 않음
⑦ 운영자 자기 서비스 API 의 클라이언트(사본의 주석 밖 코드가 배포·문서 호스트와 다른 운영자 서비스 호스트를 부른다)

**제외**: UI 프레임워크·컴포넌트 라이브러리, 상태 계층, 일반 유틸리티, 화면 캡처·렌더, 차트·시각화, 애니메이션, 폴리필·로더, htmx 와 그 확장, 비공식 래퍼. 운영자가 냈더라도 자기 서비스를 부르지 않으면 제외다. SDK 가 우리 DOM 에 UI 를 그리는 기능·ESM 전용·여러 파일·SDK CSS 는 받지 않는다.

**목록**: 스키마 `dddjango-web-sdk-registry/2` · 정규 JSON 바이트(키 정렬 · 2칸 · NFC)다. 해시·크기·최종 주소·문서 증거·접속 호스트·파일이 담은 기능은 도구만 쓴다. `use_scope` 는 이 승인이 덮는 SDK 함수다. `operator`·`name` 에는 운영자 문서의 공식 이름과 사용자가 부르는 이름을 함께 적는다(예: `Kakao Corp.(카카오)`) — 승인 원문 대조의 운영자 낱말이 여기서 나온다. 공개 설정 이름에는 `SECRET`·`PASSWORD`·`PRIVATE`·`TOKEN`·`ADMIN` 낱말을 쓰지 않는다(공개 흐름으로 HTML 에 나간다 — JavaScript 키만).

**늘 검사의 대상**:
- 목록이 있으면 목록 자체(형식·결속·공식성)와 **등재 id 디렉터리**·그것을 가리키는 모든 템플릿 참조·`vendor/.gitattributes` 가 게이트와 무관하게 늘 검사되고, 발견은 «미룰 수 없음»이다.
- 목록에 없는 벤더 단위(`vendor/` 아래 디렉터리 또는 직속 파일)는 지금 내용이 처음 생긴 때로 가른다. 목록이 저장소에 들어온 뒤(«목록 시대» — 목록을 들인 커밋의 자손)에 처음 생긴 내용이 하나라도 있으면 늘 발견이다(강등 금지 — 목록 삭제·항목 삭제·개명·병합 해소 탈락 모두). 등재에서 빠지는 길은 디렉터리째 지우는 `remove` 뿐이다(`sdk_vendor.py remove <루트> <id|미등재 단위 이름>` — 미등재 단위도 아무 템플릿이 부르지 않으면 그 단위째 지운다 · 목록은 그대로). 목록에서 빠진 등재 바이트의 사본은 어디에 있든 늘 발견이다. 지금도 등재된 바이트의 다른 자리 사본은 목록 이전에 그 자리에 있던 것만 «등재 전»이다. 목록 시대는 마지막 SDK 를 지워도 끝나지 않는다. 얕은 이력에서는 판정하지 않고 멈춘다.
- 목록이 생기기 전부터 있던 내용만 담은 미등재 단위(2.0.0 의 `vendor/<라이브러리>/<버전>/` 고정 사본 포함)는 «등재 전»이다. 새 벤더 파일·새 로드 줄만 diff 게이트가 막고, 빚 스캔은 이관 항목 WV12 를 낸다. 입구는 그 단위·그 사본을 부르는 화면에 닿는 요청의 빚 질문 ⓐ = 슬라이스 0 «기존 등록»(G1 SDK 문항)이다 — 이관은 «옛 폴더와 다른 id 로 등록 → 로드 줄을 등재 파일로 치환 → 참조 0 인 옛 단위 `remove`» 세 걸음이라 걸음마다 늘 검사가 통과한다(등재 id 디렉터리 안에 옛 판 폴더를 남기는 같은 id 등록은 도구가 거절한다) · 자격 밖이거나 G1 에서 등록이 기각되면 `ⓐ 재상정` «등록 거절 — 제거(별도 요청) / 출처 있는 ⓑ / 중단»이다. 그 사본이 main 에 들어오면 main 을 받는 레인의 diff 게이트가 등록 착륙까지 red 이므로, 미등재 사본을 main 에 들이지 않는다. 그런 사본이 든 가지는 merge 로 합친다(rebase·squash 로 합치면 «목록 시대에 생긴 내용»이 된다).
- OS 잡파일(고정 목록 · 미추적이거나 무시된 것)은 세지 않는다.

**승인**: 승인은 approval 을 뺀 항목 전체의 정규 JSON sha256(NFC)에 묶인다. 한 칸이라도 바뀌면 다시 승인한다. 출처는 «본인 직접(<시각>)» 또는 «사용자 원문 <저장소 상대 경로>@<커밋>:<행>(<시각>)» 뿐이고, 대리할 수 없다. 원문은 다음을 모두 지켜야 한다.
- 커밋이 지금 HEAD 의 조상이고, 경로가 `web/`·`.dddjango-web/` 밖이다.
- 그 줄에 시각과, 도구가 항목에서 뽑은 운영자·제품 낱말과, 판(또는 도구가 만든 표지 `<id>@<판>#<지문 앞 12>`)이 있다. 시각이 후보 수집보다 이르면 배너에 알린다.
- 판 올림은 새 판(새 표지)을 담은 새 원문이고, 범위 넓힘은 그 이름공간의 낱말(예: «카카오 로그인»)을 담은 원문이다. 범용 함수 경로는 첫 채택·기존 등록에 함께 들어와도 경로마다 그 경로 문자열(예: `/v2/user/me`)을 담은 원문이어야 한다.

**범위**: 승인은 `use_scope` 의 원소 — 핵심 함수 · `<이름공간>.*` 묶음 · 이름 지정 함수 — 만 덮는다. 묶음은 그 이름공간의 호출형·수명 함수만 덮는다. 사용자 자료·계정 상태를 운영자 쪽에 보내거나 바꾸거나 지우는 함수(업로드·저장류)는 묶음에 들지 않고, 이름을 적어 따로 승인한다. 운영자 API 경로를 인자로 받는 범용 함수는 경로마다 적어 따로 승인한다. 한 요청이 함께 들이는 것은 한 번에 묻는다. SDK 가 우리 DOM 에 UI 를 그리는 함수는 어떤 승인으로도 쓰지 않는다. 함수 분류는 목록의 `namespace_members` 에 있고 승인에 묶인다. 같은 이름공간 안 호출형 함수는 다시 묻지 않는다(정보 줄). 새 이름공간·이름 지정 함수·범용 함수 경로는 G1 에서 한 줄로 다시 묻고, 요청 원문이 대응 낱말로 이미 말했으면 그 줄이 출처다(범용 함수 경로는 예외 없이 묻는다). 파일이 담은 다른 기능은 이렇게 다시 승인하기 전에는 쓰지 않는다.

**바이트**: 사본은 심볼릭 링크·변환 속성 없이 git 에 일반 파일로 저장된 운영자 원본이다(`static/vendor/.gitattributes` 고정 표지).

**쓰는 쪽**: 목록·사본은 Coordinator 가 `sdk_vendor.py` 로만, 그 둘만 담은 `chore(web-sdk):` 커밋으로 바꾼다. 설계자·코더는 읽기만 한다.

**복원**: 다시 받은 원본이 등재 지문과 같을 때의 복원, 목록 재정규화(NFC 포함), 표지 재기록, 아무도 부르지 않는 비등재 사본 제거는 승인 없이 어느 작업에서든 언제든 한다(G0 뒤에 들어온 파손 포함).

**로드**: 그 SDK 를 쓰는 페이지 템플릿(`presentation_layer/view/<화면>_view.html`)의 `{% block scripts %}` 안(모든 페이지가 쓰면 `root/scaffold/view/root_view.html` 의 `{% block scripts %}` 여는 줄 앞)에 외부 `{% static 'web/vendor/<sdk_id>/<파일>' %}` 로 한 번 둔다. 속성은 `src`·`defer` 만(CSP nonce 는 허용)이고, 그 SDK 를 부르는 기능 JS 태그보다 앞이다. root_view·페이지 중복 로드와 조각(section·widget·component) 안 로드는 금지다. 검사기는 앞선 기능 JS 원문의 코드(주석·문자열·정규식 밖)에 그 SDK 의 등재 전역 이름이 나오는 파일을 «부르는 JS» 로 본다 — 문자열 접근(`window["<전역>"]`)·다른 JS 를 거친 간접 호출은 감수 몫이다.

**호출·키**: SDK 호출은 UI 동작 계약이 지정한 기능 JS(`static/js/<기능>.js`) 안에서, `use_scope` 묶음의 함수만, 부르는 순간 전역 경로로 한다. 공개 키는 settings 값만 출처다 — application_layer 는 django 를 모르므로(§5) settings 를 읽는 자리는 `common/`(호스트 설정을 읽는 횡단 모듈 — 명세 파일 목록이 정한다)이고, VM 이 그 값을 state 에 담아 템플릿이 escape 된 data 속성·`json_script` 로 넘긴다. 키 리터럴·`os.environ` 직접 읽기·새 context processor 는 금지다.

**정리 단위**: 벤더 칸(`static/vendor/`)과 등재 목록은 리팩토링 입구의 단위가 아니다 — 등록·복원·미사용 제거는 이 절의 절차(Coordinator 의 `sdk_vendor.py` · G1 SDK 문항)가 맡는다.

**백스톱**: 등재는 WV 패밀리 13종(WV1~WV13 — 목록 형식 · 사본 바이트 · 결속·출처 · 공식성 덫 · id 디렉터리 · 템플릿 참조 · 공개 키 리터럴 · 기능 JS 외부 코드·주소 · 사용 범위 · 변경 격리 · 미사용 · 등재 전 미등재 · 목록 시대 미등재)이 본다. WV1~WV6·WV13 은 «늘 검사»(게이트 무관 · 빚 스캔에서도 미룰 수 없음)이고, WV11·WV12 는 빚 스캔에서만 낸다. 벤더 자리의 새 파일·디렉터리는 ST12 벤더 분기가, 미등재 벤더 JS 는 PU1 이, 로드 태그 규칙은 PU2 벤더 분기가 덫으로 막는다. `sdk_vendor.py verify <루트>` 가 늘 검사만 돈다.
