---
name: dddjango-web-discipline-houserules
description: dddjango-web 파이프라인 에이전트 주입용 — 생성하는 web(Django·템플릿·CSS) 코드의 파일트리·디렉터리 구조·명명·import 방향 하우스룰. 코드를 어느 디렉터리에 어떤 이름으로 만들지 결정하거나 검수할 때 로드한다.
user-invocable: false
---

# dddjango-web 하우스룰

dddjango-web이 만드는 코드에 한정된 집안 규칙이다. **표준 파일트리·명명·import의 사실은 `references/final.md`가 단일 출처**이고, 이 본문은 그 사실을 쓰는 결정 절차다. 보편 클린코드는 dddjango-web-discipline-cleancode, 계층 동작 규율은 architecture 4종(ddd·ui·state·data), 문법 표기는 implementation 3종(python·django·htmx) 소유.

## §1 파일트리 결정 순서

새 코드를 배치할 때 위에서부터, 결론이 나면 멈춘다.

1. **새로 만드는 코드는 표준을 따른다. 기존 코드의 위반은 면제가 아니라 빚이다** — 백스톱 검사기가 내는 빚은 기능 요청의 G0 빚 질문(지금 정리 → 슬라이스 0 — 동작 불변 · 출처 있는 미룸)으로, 검사기가 내지 않는 관행·의미 정리는 리팩토링 입구 `$dddjango-web-refactor`로 다룬다. 빚 정리의 범위는 **이번 요청이 손대는 파일 + 그 파일을 부르는 곳**이다(final.md §8). 기존 코드의 **이동**(파일·폴더를 다른 경로·이름으로 옮기는 일 — 개명 포함)은 이 두 경로에서만 한다: G0에서 «지금 정리»로 정한 빚의 교정이 아닌 이동을 기능 작업에 섞지 않는다. 새 코드의 적용 경계는 둘로 갈린다: 표기(파일명·접미사·클래스)는 **모든 새 파일**에, 폴더 구조는 **신규 단위부터** — §2 경계 규칙.
2. **신규 단위(BC·애그리거트·개념 폴더·화면)는 표준 트리를 적용한다** — `references/final.md` §1을 반드시 읽는다. 생략·축소 불가 골격(§3 정신, YAGNI로 접을 수 없다):
   - BC = **4계층 + 표준 종류 폴더 전부** 항상 생성, 비어도 `__init__.py`(final.md §3). 선택 폴더 없음.
   - **생성영역 루트(BC·`root`)마다 `ruff.toml`** — 타입 전면강제 국소 lint(final.md §3·decision A). `.py`가 없는 `design_system`은 제외. 호스트 루트는 미수정. 백스톱 ST4가 누락을 골격 미완비로 차단한다.
   - domain_layer는 **항상 애그리거트(개념) 1차** + 루트 파일 `<aggregate>.py`. 불명확하면 BC 동명 애그리거트.
   - application·presentation은 **두 번째 개념 등장 시** 개념 1차 분할, infra는 평면 유지 — 하위층 없음(final.md §2).
   - `application/` 직속은 BC 폴더만 — 단 **G0에서 사용자가 area 판정한 접두**는 `application/<area>/<bc>/`로 그루핑한다(area = 순수 시각 네임스페이스·직속은 BC 폴더만·식별자 미등장 — final.md §1 area 핵심 사실·판별은 undecidable.md §13). BC 루트 직속은 `<bc>_router.py`·`<bc>_navigator.py` 둘만.
   - `web/root/`는 자체 골격(역할 4폴더, scaffold만 삼총사), design_system은 4폴더(foundation·theme·component·util)+foundation 7토큰 자리(제품 선언이 있으면 제품 뿌리마다 같은 골격) — 부품군 폴더는 수요 시 생성(final.md §3·§6).
   - 제품 선언은 선택이다 — 없으면 평면 뿌리·셸 하나 그대로, 있으면 `web/product_registry.json`의 BC 목록에 따라 제품 뿌리·문서 셸을 고른다(사용자 결정으로만 · coder는 읽기만). 표준 자리는 final.md §1 제품 핵심 사실, 혼입·선언 오류·알려진 한계는 §5·§8이다.
   - **테스트는 `web_test/`(web/ 1:1 미러·sparse)** — `web/.../<sut>.py` → `web_test/.../<sut>_test.py`. 단 SUT가 있는 자리에만 두고 빈 미러 폴더·빈 테스트 파일을 만들지 않는다(골격 완비의 *명시적 예외* — final.md §1·§3). 무엇을·단언 FORM은 dddjango-web-discipline-test, Django 메커니즘은 dddjango-web-implementation-test.
3. **배치 판별**: BC 어휘를 알면 그 BC → 전 BC 조립이면 `web/root/` → 시각 부품이면 `design_system/` → 그 외 횡단 기반만 `common/`(final.md §6). 이름은 명명 총괄표(final.md §4)에서 찾는다 — 위치·접두·접미사가 전부 정해져 있다.
4. **의미 판별 18종**(view/section, BC 어휘, 판정·계산의 귀속, 살아있는 상태, 두 번째 개념, 접두↔area 등)은 `references/undecidable.md`의 절차·배정을 따른다 — 1차 결정자와 검증자가 같은 파일을 본다.
5. **새로 만드는 단위들 사이에서 레이아웃을 혼용하지 않는다** — 레거시 단위 내부 추가는 §2의 경계 규칙.

## §2 충돌 중재

- **사실 vs 절차**: 트리·명명·import의 *사실*은 final.md가 권위다. architecture 4종 스킬은 그 사실 위의 판별·결정 *절차*를 소유한다 — 두 문서가 어긋나 보이면 사실은 final.md, 절차는 lens 스킬을 따르고, 진짜 모순이면 보고한다(임의 절충 금지).
- **레거시 vs 표준 — 경계 규칙(표기는 파일, 구조는 단위)**: ⓐ 새로 만드는 **파일**은 어느 폴더에 두든 표준 표기만 쓴다 — final.md §7 표의 변형 표기(`_app.py`·`viewmodel/` 류)로 새 파일·새 폴더를 만들지 않는다(백스톱 명명 검사는 added 파일 기준·폴더 무관 발화). ⓑ **폴더 구조**의 표준 강제는 신규 단위(BC·개념 폴더·화면 삼총사)부터 — 레거시 단위 내부 추가에 표준 폴더 신설을 강제하지 않는다(final.md §7·§8). 이것과 기존 htmx core 설치 1개·그 `root_view.html` 로드 태그의 그대로 소비는 **브라운필드 허용 규범**이라 빚이 아니다. 그 밖의 기존 파일 위반(표준 트리 밖 옛 배치 파일 포함)은 빚이다 — 개명·이동은 §1 1번의 두 경로로만 한다.
- **명세 vs 하우스룰**: 설계 명세가 이 골격을 생략·축소하면 명세 오류로 보고한다 — 검수자는 명세가 아니라 이 하우스룰과 코드를 대조한다.

## §3 레드 플래그

다음이 보이면 구조 결정이 빠졌거나 평면을 답습한 신호다(상세 교정표는 final.md §7):

- 4계층·종류 폴더 생략, domain_layer 평면(애그리거트 폴더 없음), `application/`(또는 area) 직속에 BC 아닌 파일.
- area 규칙 위반: G0 판정 없는 area 신설, area 직속 파일, area 중첩·빈 area, area가 클래스명·URL name 등 식별자에 등장(final.md §1 area 핵심 사실 위반).
- 구명칭·변형: `app/`·`bridge/`·`block/`(→ use_case·shared_state·section), `viewmodel/`·`repo/` 폴더, `_view_state.py`, `container/`.
- 화면 삼총사 접두 불일치(VM 기준 — `<화면>_view`↔`_vm`↔`_state`), UseCase가 화면명, section에 화면 접두 없음, widget이 화면 State를 받음.
- navigator가 presentation_layer에, URL path·name 리터럴이 `<bc>_router.py` 밖에(템플릿의 URL name 직접 사용 포함).
- BC 코드가 `root_` 파일을 참조(`root/`를 아는 곳은 `web/apps.py`·`web/urls.py`뿐 — 페이지 템플릿의 문서 셸 extends만 예외 — 제품 선언이 있으면 자기 제품 셸), `common/`·`design_system/`이 `application/`·`root/`를 참조, `common/`에 상태 동작(시그널 수신·세션 쓰기)·BC 어휘·비표준 종류 폴더.
- domain_layer에 `django` import·`common/util/json_field.py` 밖의 common import, VM·UseCase·State가 design_system을 참조(component 템플릿 경로·CSS 변수 이름 보유 — 허용 위치는 닫힌 열거 — final.md §5), 타 BC의 Repo·DataSource·VM·SharedState 직접 접근(4채널 밖 — final.md §5).
- 상태 동작(State 조립·세션 보관·시그널 수신 연결)이 VM·SharedState·Service·root 2변종 밖에(UseCase·Repo·DataSource는 무상태 plain class 직접 생성).
- shared_state에 과거형 사건명(`*_added` 류), component 직속 파일·정크드로어 군, 색 리터럴(`#…`)·생 글자 스타일 리터럴(foundation 토큰만).
- `apps.py`·`urls.py` 비대(시동 로직·URL 분기 조립·전역 인스턴스).
- `web_test/`가 `web/` 미러를 벗어난 위치·빈 테스트 미러 폴더·SUT 없는 자리에 채운 빈/헛(vacuous) 테스트(web_test/는 sparse — 골격 완비 비전이·§1·final.md §3·테스트 규율은 dddjango-web-discipline-test·미러/FORM은 discipline-reviewer 감사).
- 등재 밖 외부 JS — `web/static/vendor/`의 등재 목록 밖 사본·버전 폴더, CDN 실행 태그, 기능 JS의 외부 스크립트 끌어오기. 외부 JS는 G1 승인·Coordinator 도구가 등재한 공식 플랫폼 SDK(`vendor/<sdk_id>/<파일>`)뿐이고 설계자·코더는 목록·사본을 읽기만 한다(final.md §9).

## §4 백스톱 연동

파이프라인 게이트에서 결정적 러너가 구조(ST)·import(IM)·명명(NM)·순환(CY) 4패밀리를 검사한다 — 발견은 전부 blocker·반송(Phase 2에서는 슬라이스가 끝날 때마다 `--slice-end`로 먼저 돌고 G2 직전에 전부 돈다 · 오탐으로 보이는 발견은 스스로 면제하지 않고 보고한다 — 처분은 Coordinator의 «검사기 이의»). 게이트는 added(새 파일·디렉터리)·added 줄·신규 단위 기준이라 **이번 작업이 들인 위반**을 잡는다. 기존 코드의 위반(빚)은 Phase 0 빚 스캔(`--debt-scan` — web/ 전체)이 G0에 드러내고, G2 잔존 판정(`--debt-residual`)이 «지금 정리»한 빚이 사라졌는지 확인한다(final.md §8). 검사를 흉내내지 말고 이 하우스룰대로 만들면 통과한다. 러너 사용법·게이트 의미론은 final.md §8, 러너가 못 보는 의미 판별은 undecidable.md 소유.

## 상세 레퍼런스

| 주제 | 위치 |
|---|---|
| 표준 트리 전문·root 핵심 사실 | [`references/final.md`](references/final.md) §1 |
| 성장 규칙(개념 1차·종류 2차·동결) | final.md §2 |
| 골격 완비 표(계층별 종류 폴더) | final.md §3 |
| 명명 총괄표·공통 원칙 | final.md §4 |
| import 매트릭스·4채널·root 방향 | final.md §5 |
| common·design_system 입장 판별 | final.md §6 |
| drift 교정표(변형→표준) | final.md §7 |
| 백스톱 러너·게이트 의미론 | final.md §8 |
| 공식 플랫폼 SDK — 자격·제외·등재 목록·늘 검사·승인·범위·로드·키 | final.md §9 |
| 의미 판별 18종 절차·배정 | [`references/undecidable.md`](references/undecidable.md) |

각 절은 필요한 절만 읽는다(전체 로드 불필요 — `## §N.` 헤더로 grep 가능).
