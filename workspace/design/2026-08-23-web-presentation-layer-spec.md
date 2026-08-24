# dddjango-web 플러그인 빌드 — 통합 스펙 (정본)

- 상태: **4단계 적용 완료(2026-08-23) — 플러그인 v0.1.0 빌드 종료.** 이 문서는 빌드 기록·결정 대장으로 보존된다. 이후 플러그인 수정은 `dddjango-web/` 실물이 정본(산문 — 직접 수정)이다.
- 계획(사용자 확정 2026-08-23): **① 목표를 정한다 → ② dddart를 철저하게 분석한다 → ③ 버릴 부분/현지화할 부분/그대로 가져올 부분을 구분한다 → ④ 적용한다**
- 이력: 초기 계획(dddjango 안에 web 트랙 내장 — 에이전트 1+스킬 2+Coordinator 개정)은 D9(별개 플러그인)·D11(dddart 전수 현지화)로 대체됐다. 결정 이력은 아래 결정 대장에 보존한다. **계획 구조의 리셋이지 결정의 리셋이 아니다** — 확정 결정은 재논의 없이 승계.

## 1단계 — 목표 [**완료 2026-08-23**]

### 1.1 목표 선언 (**확정 2026-08-23 — 사용자**)

**dddart와의 차이 5축(사용자 확인 — 2단계 분석 태그·3단계 자동 필터)**: ①구현 기술이 Flutter가 아님(→Python·Django 템플릿·HTMX·CSS) ②BC/DDD 불고려(화면 단위) ③Model 미소유(계약 소비만 — domain/use_case/infra 계층 무관) ④반응성 없음(요청 구동 — 상주 상태·watch 소멸) ⑤테스트 없음.

> **dddjango-web**은 기존 Django 프로젝트의 **화면(web 표현계층)**을 dddart 수준의 구조 규율(MVVM 3단 분해·판별·승격·design_system·토큰)로 빌드하는 **독립 플러그인**이다.
>
> **사용 시나리오 3종(사용자 확정)** — ① **클로드 디자인 시안 반영**: 클로드가 만든 디자인(HTML)을 화면으로 구현 ② **주어진 HTML 카피**: 기존 웹페이지의 외형을 그대로 가져와 구현 ③ **기존 화면 수정**: 이미 만들어진 web/ 화면의 변경. (①②는 신규 빌드, ③은 수정 모드 — 파이프라인 양 모드 필요)
>
> - web은 **«내부의 외부 클라이언트»**다: 같은 저장소의 `web/` 영역에 살지만, 백엔드 BC의 **실물 API 계약(URL+JSON)만** in-process HTTP로 소비한다. `application/**` import는 0이며 결정적 백스톱이 강제한다. 필요한 API가 없으면 «/dddjango로 발주»를 안내한다.
> - **BC·DDD 개념을 전혀 다루지 않는다** — 단위는 화면(내비게이션 영역 > 화면 개념)이다.
> - **기술 제약(사용자 확정, D12 — v2 2026-08-24)**: **순수 HTML + HTMX + CSS만 사용한다.** JS 프레임워크·커스텀 JavaScript 없음 — JS는 vendored 닫힌 2파일(`static/js/`의 `htmx.min.js`·`motion.js`[동적 표현 발동 러너·조건 설치])뿐이며 그 외 vendored 추가도 금지다. 구조 표준은 **요청 구동 MVVM 삼총사**(view/view_model/state + 템플릿), 갱신 표준은 **HTMX 부분 재렌더**.
> - **자동 테스트를 두지 않는다** — 검증은 사용자 육안 + 결정적 백스톱 + 규율 리뷰다.
> - **완료 선언은 dddart 게이트 판형과 동일(사용자 확정)** — 결정적 백스톱 green + 규율 감사 + 게이트 배너에서 사용자 승인(화면은 육안 확인).
> - 형상(배치·생김새)의 근거는 **동결된 시안**(이미지 또는 시안 HTML)이며, **재현하되 직수입하지 않는다**(마크업·클래스·인라인 스타일 복붙 금지 — 구조는 규범으로 재구축).
> - **non-goals(사용자 확정)**: JS 프레임워크 앱 ✗ · 모바일/데스크톱 앱 ✗ · 백엔드 API 생성 ✗(발주 안내만) · 자동 테스트 ✗ · 배포·인프라 ✗.
> - Claude(`dddjango-web/`)·Codex(`codex-dddjango-web/`) 양 런타임 지원, 같은 GitHub 레포 마켓 배포. dddjango 플러그인은 **무수정**.

### 1.2 확정 결정 대장 (승계 — 재논의 없음)

| # | 결정 | 상태 | 결론 |
|---|---|---|---|
| D1 | web 트리 «값»의 거처 | **결정 (D11 귀결)** | `discipline-web-houserules` 스킬 — 값/절차 이원화 판형 유지. «필요 없을 때 미로드»는 플러그인 분리로 자동 충족 |
| D2 | implementation-django-web §4·§5 관할 | **해소 (D9 귀결)** | 플러그인 분리로 문제 소멸 — 두 세계는 트리 위치로 기계 구분, 기존 스킬 무수정 |
| D3 | web 검사기 | **부분 결정** | 격리 백스톱 `check-web-isolation` = **필수(사용자)**: ①`web/**`에 `application.`·`framework.` 내부 import 0 ②API 호출 코드는 client/ 전속 ③client 대상 URL은 driving_layer api 표면만. 골격 검사기는 미결(권장: 신설) |
| D4 | dddjango houserules «최상위는 셋» 문장 | 선택·미결 | 의무 아님 — 상호 참조 한 줄(4단계 선택 항목) |
| D5 | 계약 소비 강도 | **결정 (사용자)** | HTTP 표면만 — URL+JSON, web 소유 응답 모델 파싱. driving_layer schema import도 금지 |
| D6 | web 표준 | **결정 (사용자)** | MVVM 삼총사+HTMX 부분 재렌더 1급 표준. 요청 구동(무상태 VM — watch·SharedState 번역 안 함). section=hx-target, fragment 진입점은 소속 view. forms↔VM 분담(입력 검증=form·표시 상태=VM). htmx 의존 전제 |
| D7 | 호출 방식 | **결정 (사용자)** | D5 유지 — in-process HTTP(파이썬 코드로 주소를 불러 JSON 수신·네트워크 없음). 호출 주체는 VM·거처는 client/ 전속. 메커니즘(미들웨어 경유)은 구현 표기에서 확정 |
| D8 | implementation-ui 범위 | **결정 (사용자)** | web 트랙 구현 전반(HTML·템플릿·삼총사 .py·client·urls) — «web/ 트리 코드 = implementation-ui» |
| D9 | 제공 형태 | **결정 (사용자)** | **별개 플러그인 dddjango-web** — 같은 레포·마켓(Claude·Codex), dddjango 무수정. 접점 = 대상 프로젝트 공유·실물 API 계약 소비·격리 백스톱 |
| D10 | dddjango 기존 서버렌더 세계 | **결정 (사용자)** | 유지(무수정)·공존 — 삭제하지 않고 dddjango-web 신설에 집중 |
| D11 | 스펙 작성 방법 | **결정 (사용자)** | dddart 전수 인벤토리 → 3처분(버림/현지화/그대로) 대조표로 유도. 필터: BC/DDD 불요·테스트 없음·요청 구동·화면 단위·계약=실물 API |
| D12 | 기술 제약 | **결정 (사용자 · v2 2026-08-24)** | **순수 HTML+HTMX+CSS만.** JS 프레임워크·커스텀 JS 금지 — JS는 vendored **닫힌 2파일**(`htmx.min.js`·`motion.js` — 동적 표현 발동 러너, 명세의 러너 채택 항목 ≥1일 때만 설치)이며 다른 JS 라이브러리의 vendored 추가도 금지. 화면 코드는 `data-motion` 선언만·motion.js 수정 금지(판형 해시 대조). 백스톱: WP — .js 화이트리스트(그룹별)·inline `<script>` 금지·htmx `js:` 채널 금지·해시 대조 |
| — | 형상 SoT | **결정 (사용자)** | 시안(이미지 또는 시안 HTML)이 형상의 유일 근거·명세 산문 레이아웃 금지·«재현이지 직수입이 아니다»·시안 없으면 coder 재량+사용자 육안·충실도 대조는 리뷰 항목(시안 있을 때만) |
| — | 갈림 이력 | 결정 | (a)영역=내비게이션 단위(경계 곤란 시 G0 배치축 3선택 판형) · (b)템플릿 병치 · (d)CSS 병치 · (e)templatetags 금지(`{% include %}` 전용) · (g)ui_extension 미차용(VM이 그 자리) · (h)theme/util 미차용 시작 · (i)라우트 리터럴 단일 출처 · test/ 없음 · 공통 호출기 없음 |

### 1.3 확정 규범 자산 (3·4단계의 입력)

**㉠ web 표준 트리 v3 (확정)** — dddart 트리 현지화 대조표로 유도(대조표 전문은 진행 기록 이전 판 참조, 결정 필터는 D11):

```text
web/
  urls.py                              # 전 영역 urls 합산 (root_router 번역)
  apps.py
  base/
    base.html                          # 공통 문서 골격·내비 셸 (root_scaffold 번역 — «거의 빈» 규범)
  <screen_area>/                       # 내비게이션 영역
    urls.py                            # 영역 path·name 리터럴 단일 출처
    <view>/                            # 화면 개념 1차 — 예: order_list/
      view/
        <view>_view.py                 # 진입점 — URL 바인딩·VM 호출·render·fragment 소유
        <view>.html                    # 페이지 템플릿
      view_model/
        <view>_view_model.py           # VM — client 호출·표시 상태 조립
      state/
        <view>_state.py                # 표시 상태 dataclass
      form/
        <view>_form.py                 # 입력 검증 Django Form — 입력 form이 있는 화면만 생성(조건 생성)
      section/
        <view>_<section>.html          # 화면 전속 조각 — HTMX 재렌더 단위·접두 필수
    widget/
      <widget>.html                    # 영역 재사용 조각 — 화면 비전속·명시 context만
  client/
    <bounded_context>/
      <capability>_client.py           # 계약 클라이언트 — in-process HTTP, api 표면만
      response/
        <response>_response.py         # web 소유 응답 모델
      exception.py                     # 계약 오류 표현
  design_system/
    foundation/
      tokens.css                       # 색·타이포·간격·모션 토큰
      motion.css                       # 공용 keyframes·모션 유틸(motion-*) — 값 정의는 tokens.css
    component/
      <부품군>/
        <component>.html               # BC 어휘 없는 순수 부품 — 부품군 1차·직속 금지
  static/
    css/  js/                          # htmx 포함 (js는 vendored 2종 — htmx·motion[조건 설치] — D12v2)
    images/                            # 시안 이미지 착지 (fetch 도구·asset-manifest 배선)
```

(트리 v3.2 — 2026-08-24 모션 축 반영: foundation/motion.css·static/js vendored 2종[D12v2]. v3.1 — 2026-08-23 R1 처분 Q1·Q2 반영: form/ 종류 폴더(조건 생성)·static/images/ 추가.)

**㉡ architecture-web 스킬 절 구성 (확정)** — §1 정의와 경계(외부 클라이언트·요청 구동 MVVM·형상 공리·handoff 표) / §2 3단 판별표 / §3 삼총사 규율(view 진입점뿐·VM 표시 판단 유일 자리·state 불변·forms↔VM 분담) / §4 section·widget 규율(dumb·접두·HTMX 재렌더 단위) / §5 승격·이동 표(+역방향 절제) / §6 계약 소비(client 전속·api 표면만·발주 안내·백스톱 근거) / §7 라우팅(리터럴 단일 출처) / §8 design_system 사용(토큰 강제·재사용 우선·BC 어휘 금지)

**㉢ implementation-ui 스킬 절 구성 (초안 — D8 범위: web 구현 전반)** — §1 책임 범위 / §2 시안 재현 절차(외형 추출→토큰화→분해·직수입 금지) / §3 삼총사 표기 / §4 템플릿 표기 / §5 section·HTMX 표기 / §6 widget·component 표기 / §7 토큰·CSS 표기 / §8 client 표기(in-process 메커니즘·파싱·예외 변환) / §9 urls 표기

**㉣ 플러그인 골격 (D9)** — `dddjango-web/`: `.claude-plugin/plugin.json` + `commands/dddjango-web.md`(자체 Coordinator) + `agents/` + `skills/` + `scripts/` · `codex-dddjango-web/` 미러 · 전 파일 산문 정본 시작(온톨로지 밖)

## 2단계 — dddart 철저 분석 [**완료 2026-08-23**]

서브에이전트 3병렬 전수 분석 완료(전 50파일 — 커맨드 214행·에이전트 7·스킬 11×2·undecidable·스크립트 16·매니페스트). 산출물(항목 단위 인벤토리 + 차이 5축 태그):
- **분석 A(커맨드·에이전트)**: `workspace/design/2026-08-23-dddart-analysis-A-command-agents.md` — 게이트·배너·폴더·모드·배선·재호출 루프 7종·에이전트 판형
- **분석 B(스킬 11종)**: `workspace/design/2026-08-23-dddart-analysis-B-skills.md` — 절 단위 인벤토리·경계망(위임 46건)·undecidable 18종 배정표
- **분석 C(스크립트·부속)**: `workspace/design/2026-08-23-dddart-analysis-C-scripts.md` — 백스톱 러너 판형(exit 0/1/2·diff 게이트·래칫)·검사기 9패밀리·파이프라인 도구 5종·매니페스트

주요 발견: ①클로드 디자인 절단 도구 체인 실재(extract_design·extract_dc·fetch_images — 시나리오 ①② 직결) ②discipline-cleancode 원본이 dddjango 소스판(예제만 Dart 치환 — 복원 저비용) ③extract_layout은 미소비 ④완료 선언(=dddart 게이트 판형)에 백스톱 green+규율 감사 포함.

## 3단계 — 3처분 분류 [**완료 2026-08-23**]

### 처분 대조표 (파일 단위 — 절 단위 세부는 4단계 작성 시 각 스펙에서)

| dddart 자산 | 처분 | dddjango-web 대응 | 근거 |
|---|---|---|---|
| 커맨드 dddart.md | **현지화** | `commands/dddjango-web.md` | 게이트 배너·트래커·산출물 폴더·모드 삼분류·재개 앵커·재호출 루프 판형 **그대로**. 제거: TDD·test·analyze 래칫·codegen·빌드([TEST][FLUTTER]) / 대체: 가정 계약·tracer·미니 게이트 → **«/dddjango로 발주» 안내**(web은 없는 API를 가정하지 않음), area 그루핑 → 영역(내비 단위) 판정, 디자인 플래그 3종·화면 확인 게이트·기계 추출 순서는 그대로(시나리오 ①②) |
| design-architect | **현지화** | design-architect-web | 단일 통합 작성자·명세에 담는 것·자기모순/백스톱 정합 스캔·좁은 재호출 판형 그대로. lens 4→화면 1+계약 소비. 형상 산문 금지 유지 |
| design-review-ui | **현지화** | design-review-web | 점검 7항+충실도 4항 이식. **design-review-data의 계약 대조 축 흡수**(실계약 대조·출처 명시성) |
| design-review-ddd / -state | **버림** | — | [BC]/[STATE]. state의 잔여 관심(표시 상태 계약)은 review-web이 흡수 |
| design-review-data | **버림·흡수** | → design-review-web | 위 흡수 항목 외 [MODEL][FLUTTER] |
| coder | **현지화** | **coder-web** (역할 표 N5 해소) | 무기억 집행자·입력 배선·형상 재현(직수입 금지)·반송 5종·경계 판형 그대로. 테스트 산출 의무·codegen·green 래칫([TEST][FLUTTER]) 제거 — green 판정 대체는 갈림 ③ |
| discipline-reviewer | **현지화 (갈림 ② 확인)** | discipline-reviewer-web | 완료 선언(=dddart 동일, 사용자 확정)에 규율 감사가 포함되므로 사실상 확정. 의미 변종 전담(수동성·분해 실현·이름-위장·판별 2차 검증) 유지, 테스트 FORM 감사([TEST]) 제거 |
| architecture-ddd | **버림** | — | [BC][MODEL] 전절 |
| architecture-ui | **현지화 완료** | architecture-web (§S2 확정) | — |
| architecture-state | **버림** | — | [STATE] 전절 — 요청 구동. 표시 상태·에러 표시 잔여는 architecture-web §3·§6 |
| architecture-data | **버림 + §7·§8 현지화** | 계약 스냅샷 체계(동결→기계 절단→경량본 독자 규율) → architecture-web §6·커맨드 | §7·§8은 기술 중립 — 갈림 ④(차용 범위) |
| discipline-cleancode | **갈림 ①** | (권장: 차용 — dddjango 소스판 복원) | 원본이 dddjango판(예제만 Dart 치환) — Python 예제판 복원 저비용. dddart 고유 삽입부(§18 반복>상속 등)는 web 문맥 재검 |
| discipline-houserules | **현지화** | discipline-web-houserules (D1 확정) | 트리 v3(§S1)+성장 규칙(개념1차·종류2차)+골격 완비+명명 총괄표(web판 신규 작성)+import 방향(격리)+백스톱 연동 |
| undecidable.md | **현지화 축소** | web 판별 곤란 절차(±6종: view/section·화면 전속·영역 귀속·widget↔design_system·두 번째 개념·같은 철자) | 배정표 판형(1차 결정/검증) 그대로 — discipline-web-houserules 부속 |
| discipline-test / implementation-test | **버림** | — | [TEST] 전절(갈림 ① 테스트 없음) |
| implementation-dart | **버림** | 필요 관용구만 implementation-ui §3에 흡수 | [FLUTTER] |
| implementation-flutter | **버림 + §8·§9 현지화** | §8 에셋(manifest SSOT·토큰 경유·멱등)→implementation-ui, §9 형상 재현→implementation-ui §2(기채택) | 나머지 [FLUTTER] |
| implementation-riverpod | **버림** | — | [FLUTTER][STATE] 전절 |
| backstop 러너+ST/IM/NM 패밀리 | **현지화 (Python 재작성)** | check-web 백스톱 러너 — 구조·격리(check-web-isolation)·명명 3패밀리 + **D12 검사**(커스텀 .js·inline script 금지 — PJ «토대 불변식» 판형 전용) | **D3 골격 검사기 = 신설로 해소**(완료 선언에 백스톱 green 포함). exit 0/1/2·diff 게이트·일괄 출력·값 3중 사본 구조 그대로 |
| check_cycles/tests/pubspec/models/riverpod/hive | **버림** | (PJ 판형만 D12 검사로 전용) | [BC][TEST][FLUTTER][MODEL][STATE] |
| extract_design·extract_dc·fetch_images | **현지화 (Python 재작성)** | 시안 HTML→토큰 절단·클로드 디자인 화면부 절단·이미지 동결 | 시나리오 ①② 직결. Flutter 아이콘 매핑(icon_map) 제거·산출은 tokens.css 지향 |
| extract_contract | **현지화 (Python 재작성)** | OpenAPI 동결본 기계 절단 | 갈림 ④ 범위 확정 후 |
| extract_layout·icon_map.json | **버림** | — | 미소비 / Flutter 전용 |
| run_fixtures.sh | **현지화** | 검사기 자기 회귀 픽스처(positive-control 짝 판형) | 검사기 재작성의 안전망 |
| plugin.json·마켓 등록 | **판형 차용** | dddjango-web 매니페스트+marketplace.json 등재+Makefile 확장 | — |

### 자동 해소된 미결

- **N5(구현 담당)** = 전용 `coder-web` 에이전트 신설(dddart coder 현지화 — D11 귀결)
- **D3(골격 검사기)** = 신설(백스톱 러너 현지화에 포함 — 완료 선언에 백스톱 green 포함)
- 가정 계약·tracer·미니 게이트 = **발주 안내로 대체**(web은 없는 API를 가정하지 않는다)

### 갈림 4건 — **전건 결정 2026-08-23 (사용자) → 3단계 완료**

1. **갈림 ① 결정: discipline-cleancode 차용** — 근거(사용자): view/VM에 가벼운 로직이 실재. dddjango 소스판(Python 예제) 복원 + dddart 고유 삽입부(§18 반복>상속 등) web 문맥 재검
2. **갈림 ② 결정: discipline-reviewer-web 신설**
3. **갈림 ③ 결정: ㉮** — green 판정 = `python -m py_compile`(문법) + `manage.py check` 경량 조합
4. **갈림 ④ 결정: 계약 스냅샷 체계 전체 차용** — G0 동결 → G1 기계 절단 → coder-web은 경량본만

## 4단계 — 적용 [**완료 2026-08-23 — W0~W4·R1~R4 전체 green**]

**최종 플러그인 구성**(3단계 처분 확정 결과):

```text
dddjango-web/
  .claude-plugin/plugin.json
  commands/dddjango-web.md            # Coordinator — dddart 게이트 판형 현지화
  agents/  design-architect-web.md · design-review-web.md · coder-web.md · discipline-reviewer-web.md
  skills/  architecture-web/ · implementation-ui/ · discipline-web-houserules/(+undecidable-web.md) · discipline-cleancode/
  scripts/ backstop.py + src/(구조·격리·명명·D12 검사) · extract_design.py · extract_dc.py · fetch_images.py · extract_contract.py · test/run_fixtures.sh
codex-dddjango-web/                   # 의미·byte 미러
```

**웨이브** (의존 순 · **웨이브마다 적대 리뷰 삽입** — 사용자 지시 2026-08-23, T2-2 선례 판형: 발견 처분·blocker 전건 수정 후 다음 웨이브):
- **W0 스캐폴딩**: 디렉터리·plugin.json (Coordinator 직접·소규모. 마켓 등재는 미완성 노출 방지 위해 W4로 이동)
- **W1 스킬 코퍼스 (병렬 4)**: discipline-web-houserules(트리 v3·성장·골격·명명 총괄표 web판·import 격리·백스톱 연동 + undecidable-web) / architecture-web(§S2 확정 8절) / implementation-ui(§S3 9절) / discipline-cleancode(dddjango 소스판 복원·web 문맥 재검·graph-owned 마커 제거)
- **R1 적대 리뷰 (병렬)**: dddart 원본 대비 현지화 누락·오역 / 확정 결정(D1~D12·형상 SoT) 위반 / 상호 위임망·§번호 정합 / 판형 위반 / 내부 모순(dddart 자체 불일치 5건 반복 금지)
- **W2 에이전트·커맨드 (병렬 5)**: 에이전트 4종 + commands/dddjango-web.md(게이트·폴더·모드·플래그·발주 안내·계약 절단·디자인 절차 현지화)
- **R2 적대 리뷰**: 배선 정합(스킬 § 인용 실재·산출 계약·경계)·파이프라인 드라이런 사고실험(발주→G0→G1→G2 시나리오 3종 통행 검증)

**R1 결과·처분 (2026-08-23 — blocker 11·important 33·nit 22, 뿌리별 처분)**:
| # | 뿌리 | 발견(대표) | 처분 |
|---|---|---|---|
| P1 | **form의 트리 거처 부재** | D6 필수 산출물(Django Form)의 폴더·명명 행이 트리·총괄표에 전무(R1-a B1) + form-in-state 3중 모순(R1-b B1·R1-c B4) | **결정 2026-08-23 (사용자): ⓑ 종류 폴더 `form/` 신설·조건 생성**(입력 화면만 — exception.py 판형·골격 완비 비대상). 트리 v3.1 반영. state 모순은 «state 필드 타입 예외로 Django Form 1종 허용»(검증 실패 재렌더 시 form을 state 필드로 운반) 명문화로 3문서 일관 개정. 명명: `<view>_form.py`→클래스 `<View>Form` |
| P2 | **client 메커니즘 4중 결함** | CSRF 면제 오서술·신원 전파 무규정·5xx 원시 예외 관통·testserver 호스트(R1-c B1·B2·B3·I5) | 처분 확정: ①`Client(raise_request_exception=False)` 명시 ②CSRF는 브라우저→web view 경계에서 1회 집행, 내부 호출은 검사 비대상임을 정직 명문화 ③**신원 이월 규범** — view가 받은 세션 자격(세션 쿠키)을 VM 경유 client가 이월(자격 운반 인자 시그니처) ④`ALLOWED_HOSTS`에 "testserver" 전제 — 배선 절(P3)에 |
| P3 | **호스트 배선 무소유** | INSTALLED_APPS·TEMPLATES DIRS·STATICFILES_DIRS·ROOT_URLCONF include·htmx vendored·ALLOWED_HOSTS 소유자 없음(R1-d B5·R1-c I6·I7·R1-a #10) | 처분 확정: **커맨드 Phase 0 «web 배선 전제조건 검사»**(dddart 전제조건 검사 판형)가 소유 — 미비 시 G0 배너 표면화·승인 하에 Coordinator 직접 배선. 정적 서빙은 STATICFILES_DIRS **프리픽스 튜플**(("design_system", …)·("web", …))로 tokens.css 서빙+네임스페이스 충돌 동시 해소. houserules·implementation-ui에는 handoff 행만 |
| P4 | **값 이중 서술** | 판별 순서 상반 2판(R1-d B2)·view 명명 계약 모순(R1-d B1)·base.html 목록 3판(R1-d I6)·공통 호출기 완화구(R1-b I3·R1-d I4) | 처분 확정: 판별 순서 표는 architecture-web §2 **단독 소유**(houserules §6은 위치 답만+위임)·총괄표 view 행=함수 기준(`order_list_view` 함수)·VM 모듈 함수 허용 병기·base.html 목록은 undecidable-web §6 단독+타문서 위임·완화구 삭제(«만들지 않는다» 종결) |
| P5 | **기계 치환 위임 계열** | cleancode의 부재 대상 위임·순환 위임·소유 오귀속(R1-d B3·B4·I3·I1) | 처분 확정: cleancode 조정부의 타 스킬 위임 **전건 실재 검증** 일괄 — §12.3 소유를 VM으로 재작성·§4.7/§5.2는 implementation-ui §3에 독스트링·줄 길이 최소 규칙 신설로 수신·§2.14 값 객체 문장 web 문맥 재검·§12.2 괄호 명확화·§N 헤더/grep 안내 복원(R1-d I10) |
| P6 | **트리 소보완** | static/ 이미지 칸 부재(R1-a #8)·갈림(d) 정의 소실(R1-a #9) | (d) 정의 복원: **design_system CSS(tokens.css)는 foundation/ 병치**(화면 CSS는 static/css/ — 별개, 서빙은 P3 프리픽스 튜플). 이미지 칸 **결정(사용자): `static/images/` 추가** — 트리 v3.1 반영 |
| P7 | **dddart 장치 소실** | 크기 토큰 전수 연결(R1-b I4)·정적 view 판례(R1-b I2)·수평 격리(R1-b I5·R1-a #11)·주 클래스 예외(R1-a #5)·§4 ③위임 단서(R1-a #4)·캐스케이드 0순위(R1-a #2)·영역 레드 플래그(R1-a #6)·«전부 검사 대상» 과대(R1-a #3)·`__init__.py` 처분(R1-a #7)·동결 사실 배치(R1-a #16) | 처분 확정: 전건 수정 — 크기 전수 연결은 architecture-web §8+설계자 명세 규율로, 수평 격리는 §5 신설(타 영역 widget include 금지·교차 재사용은 design_system 승격 경유·불가면 설계 반송), `__init__.py`는 dddjango #488 선례로 표준 채택(.gitkeep 대체) |
| P8 | **교정 사전(표기 표준화) 부재** | 브라운필드 Django 관행(views.py 단일·forms.py·전역 templates/) 명명 어휘 없음(R1-a #12) | **결정 2026-08-23 (사용자): 신설** — houserules final.md에 소형 교정표 절(§8, ~8행: views.py 단일→화면 개념 분해 / forms.py 모음→form/ / 전역 templates/→병치 / CBV 관성→함수 뷰+VM / context dict→state / inline script→htmx 속성 / 색·크기 리터럴→tokens / 무네임스페이스 static→프리픽스) |
| P9 | 기타 important·nit | 예제 hx-post 오용·hx 속성 목록·이미지 token 소비처·auth 표기 부재·용어(판정/판단)·예시 세계관·표 축 통일 등 | 처분 확정: 일괄 수정(파일별 수정 에이전트 브리핑에 전건 포함) |
- **W3 스크립트 (병렬)**: Python 재작성 — 백스톱 러너+검사기 3패밀리+D12 / 추출 도구 3종 / extract_contract / 픽스처 러너
- **R3 검증**: 픽스처 러너 실제 실행(기계 검증) + 코드 적대 리뷰(exit 계약·게이트 의미론·우회 벡터)
- **W4 마감**: `claude plugin validate dddjango-web --strict` · codex 미러 · marketplace 등재·Makefile·README·AGENTS.md·DEVELOPMENT.md 갱신 · `make verify` · 조감도·work_flow.html 재도해 · 메모리 갱신
- **R4 최종 감사**: 전체 정합(계수·미러 byte/의미·매니페스트·문서 교차 참조)

선택 항목(적용 중 결정): dddjango 상호 참조 2건 — houserules «최상위» 문장(D4)·implementation-django-web handoff 행(R2′).

## 진행 기록

- 2026-08-23 정본 생성(구판 — dddjango 내장 web 트랙 계획). 선례(dddart)·현행 배선(dddjango) 조사, 역할 표 합의.
- 2026-08-23 D5·D6(MVVM+HTMX)·D1(구판)·D4·형상 SoT·D8 확정. §S1 트리 v3·§S2 확정. 갈림: test/ 없음·공통 호출기 없음·D7(in-process HTTP 유지·격리 백스톱).
- 2026-08-23 **D9 확정: 별개 플러그인 dddjango-web** → D1 재개·D2 해소·D4 축소, D10(기존 서버렌더 유지) 확정.
- 2026-08-23 **D11 확정: dddart 전수 현지화 방법** → D1=discipline-web-houserules로 재확정.
- 2026-08-23 **계획 리셋(사용자)**: 4단계 구조(목표→분석→3처분→적용)로 정본 재작성. 확정 결정·규범 자산 전량 승계.
- 2026-08-23 **1단계 완료**: 목표 선언 확정(사용 시나리오 3종·완료 선언=dddart 동일·D12 순수 HTML+HTMX+CSS·non-goals). 차이 5축 확인.
- 2026-08-23 **2단계 완료**: dddart 전수 분석 3병렬(A 커맨드·에이전트 / B 스킬 11종 / C 스크립트·부속) — 산출물 3파일 영속화. **3단계 처분 대조표 초안 작성** — 자동 해소 3건(N5=coder-web·D3=신설·tracer→발주 안내), 갈림 4건 사용자 결정 대기.
- 2026-08-23 **3단계 완료**: 갈림 4건 전건 결정(①cleancode 차용 ②reviewer-web 신설 ③green=py_compile+manage.py check ④계약 체계 전체 차용). 4단계 착수 승인(+웨이브별 적대 리뷰 삽입 — 사용자 지시).
- 2026-08-23 **W0·W1·R1 완료**: 스캐폴딩+스킬 4종 작성, R1 적대 리뷰 66건(blocker 11) 전건 처분·수정 — form/ 종류 폴더(트리 v3.1)·client 메커니즘 재설계·배선 소관 확정(P1~P9). make verify green·커밋 push(6334188).
- 2026-08-23 **W2 완료**: 에이전트 4종(design-architect-web 73행·design-review-web 45행·coder-web 58행·discipline-reviewer-web 69행) + 커맨드 dddjango-web.md(192행 — 게이트 판형·배선 검사 6종·발주 안내 축·화면 확인 게이트).
- 2026-08-23 **R2 완료**: 배선 정합+드라이런 51건(blocker 6 — 폴더 확정 순서·합치기 가드·첫 실행 시퀀싱·htmx 소유·영역 판정 검증 단절) 전건 처분·수정(수정-E 커맨드 14처분·수정-F 에이전트·스킬 8건).
- 2026-08-23 **W3 완료**: backstop.py(검사 24종 WS8/WI4/WN8/WP4)·extract_design/dc/fetch_images·extract_contract — Python 표준 라이브러리·픽스처 3파일. **R3 green**: 픽스처 101단언 PASS·snake_case 교차 결함(도구 slug 하이픈↔WN8) 패치.
- 2026-08-23 **W4 완료**: `plugin validate --strict` 통과 · marketplace.json 등재 · Makefile verify-web 편입 · README «자매 플러그인» 절 · AGENTS.md·DEVELOPMENT.md 저장소 지도 · codex-dddjango-web 미러(31파일·byte 20/20) · work_flow.html 현행화(validate 9종 0오류·기하 불변) · 조감도 연혁 · 메모리(dddjango-web-plugin 신설). R4 최종 감사 + make verify 전체로 마감.
