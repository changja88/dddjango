---
name: discipline-web-houserules
description: dddjango-web 파이프라인 에이전트 주입용 — 생성하는 web 표현계층 코드의 파일트리·디렉터리 구조·명명·참조 격리(import 방향)·JS 순수성 하우스룰. 코드를 어느 디렉터리에 어떤 이름으로 만들지 결정하거나 검수할 때 로드한다. 판별·승격 절차는 architecture-web, 구현 표기는 implementation-ui, 보편 클린코드는 discipline-cleancode 소유.
---

# dddjango-web 하우스룰

dddjango-web이 만드는 `web/` 코드에 한정된 집안 규칙이다. **표준 파일트리·명명·격리의 사실은 `references/final.md`가 단일 출처**이고, 이 본문은 그 사실을 쓰는 결정 절차다. 판별·승격 절차는 architecture-web, 구현 표기는 implementation-ui, 보편 클린코드는 discipline-cleancode 소유.

## §1 파일트리 결정 순서

새 코드를 배치할 때 위에서부터, 결론이 나면 멈춘다.

1. **표준은 새로 만드는 코드부터 적용한다 — 기존 코드의 수정·개명·이동을 요구하지 않는다.** 적용 경계는 둘로 갈린다: 표기(파일명·접두·접미사·클래스)는 **모든 새 파일**에, 폴더 구조는 **신규 단위부터** — §2 경계 규칙.
2. **신규 단위(영역·화면 개념·client BC 폴더)는 표준 트리를 적용한다** — `references/final.md` §1을 반드시 읽는다. 생략·축소 불가 골격(final.md §3 정신 — YAGNI로 접을 수 없다):
   - 화면 개념 = **종류 4폴더(view·view_model·state·section) 항상 생성** — `form/`은 조건 생성(입력 form이 있는 화면만 — final.md §3). 빈 폴더 마커는 Python 패키지 `__init__.py`·HTML 전용 `.gitkeep`(final.md §3). 그 외 선택 폴더 없음.
   - `widget/`은 영역 수준 — 화면 개념 폴더 안에 만들지 않는다.
   - `design_system/`은 foundation·component **2칸 시작** — theme·util 칸은 만들지 않는다(final.md §3).
   - **test/ 없음** — web 트랙은 자동 테스트를 두지 않는다. 테스트 폴더·파일을 만들지 않는다(final.md §3).
3. **배치 판별**: **0순위 — API 호출 코드는 판별 없이 언제나 `client/`다(final.md §5②)**. UI 조각은 판별 순서를 architecture-web §2가 단독 소유하고(상태 조립을 먼저 묻는다) 위치 답은 final.md §6이다 — 상태 조립이 필요하면 view 삼총사, 화면 전속이면 그 화면 `section/`, 영역 재사용·BC 어휘 보유면 `widget/`, BC 어휘가 없으면 `design_system/component/`. 이름은 명명 총괄표(final.md §4)에서 찾는다 — 위치·접두·접미사가 전부 정해져 있다.
4. **의미 판별 6종**(view/section, 화면 전속, BC 어휘, 영역 귀속, 두 번째 개념, base «거의 빈»)은 `references/undecidable-web.md`의 절차·배정을 따른다 — 1차 결정자와 검증자가 같은 파일을 본다.
5. **새로 만드는 단위들 사이에서 레이아웃을 혼용하지 않는다** — 레거시 단위 내부 추가는 §2의 경계 규칙.

## §2 충돌 중재

- **사실 vs 절차**: 트리·명명·격리의 *사실*은 final.md가 권위다. architecture-web은 그 사실 위의 판별·승격 *절차*를 소유한다 — 두 문서가 어긋나 보이면 사실은 final.md, 절차는 architecture-web을 따르고, 진짜 모순이면 보고한다(임의 절충 금지).
- **레거시 vs 표준 — 경계 규칙(표기는 파일, 구조는 단위)**: ⓐ 새로 만드는 **파일**은 어느 폴더에 두든 표준 표기만 쓴다(백스톱 명명 검사는 added 파일 기준·폴더 무관 발화). ⓑ **폴더 구조**의 표준 강제는 신규 단위(영역·화면 개념·client BC 폴더)부터 — 레거시 화면 내부 추가에 표준 폴더 신설을 강제하지 않고, 기존 파일의 개명·이동도 요구하지 않는다.
- **명세 vs 하우스룰**: 설계 명세가 이 골격을 생략·축소하면 명세 오류로 보고한다 — 검수자는 명세가 아니라 이 하우스룰과 코드를 대조한다.

## §3 레드 플래그

다음이 보이면 구조 결정이 빠졌거나 격리가 새는 신호다:

- 종류 4폴더 생략, 화면 파일이 영역 직속에 평면 나열, 화면 개념 폴더 안의 `widget/`.
- G0 판정 없는 영역 신설, 영역 직속 파일(urls.py·widget/·화면 개념 폴더·마커 파일 외), 빈 영역, 영역 중첩, 영역 이름에 컨테이너명·종류명(final.md §1).
- `web/**`에 `application.`·`framework.` import — driving_layer schema import 포함(final.md §5①).
- view·VM·템플릿의 API URL 리터럴·직접 HTTP 호출 — client/ 밖(final.md §5②~④).
- 커스텀 `.js` 파일 신설·템플릿 inline `<script>`·htmx 속성 JS 채널(`hx-on*`·`js:` 접두·`hx-trigger` 조건식) — vendored 닫힌 2종(htmx·motion) 외 JS·motion.js 판형 이탈(final.md §5⑤).
- 삼총사 접두 불일치, section에 소속 view 접두 없음, widget·component 이름에 view 이름 등장.
- web path·name 리터럴이 urls.py 밖에(템플릿 하드코딩 href·redirect), 또는 `web/urls.py`에 영역 리터럴 직접 정의(영역 include 합산만 — final.md §5④), 커스텀 templatetags 신설(`{% include %}` 전용).
- design_system/component 직속 파일, component에 BC 어휘, 템플릿·CSS의 생 색·간격 리터럴(tokens.css 밖).
- `test/` 폴더·테스트 파일 생성(web 트랙 비채택).
- widget이 화면 state를 통째로 받음, base.html에 화면 어휘.

## §4 백스톱 연동

파이프라인 게이트에서 결정적 러너가 **구조·골격(WS)·격리(WI)·명명(WN)·순수성(WP)** 4패밀리를 검사한다 — 발견은 전부 blocker·일괄 반송. 게이트는 added(새 파일·디렉터리)·added 줄·신규 단위 기준이라 **레거시에는 불발화한다** — "새 코드부터 표준"의 기계 집행. 검사를 흉내내지 말고 이 하우스룰대로 만들면 통과한다. 러너 사용법·게이트 의미론은 final.md §7, 러너가 못 보는 의미 판별은 undecidable-web.md 소유.

## 상세 레퍼런스

| 주제 | 절 |
|---|---|
| 표준 트리 전문·4원칙·백엔드 트리와의 공존 | [`references/final.md`](references/final.md) §1 |
| 성장 규칙(영역·개념 1차·종류 2차) | final.md §2 |
| 골격 완비(종류 4폴더·form 조건 생성·마커 파일·design_system 2칸·test 없음) | final.md §3 |
| 명명 규약 총괄표·공통 원칙 | final.md §4 |
| 참조·import 방향(격리·수평 격리·D12 순수성) | final.md §5 |
| widget·section·component·view 입장 위치 답(판별 순서는 architecture-web §2) | final.md §6 |
| 백스톱 러너·게이트 의미론·배선 handoff | final.md §7 |
| 표기 표준화 — 브라운필드 관행 교정 사전 | final.md §8 |
| 의미 판별 6종 절차·배정 | [`references/undecidable-web.md`](references/undecidable-web.md) |

각 절은 필요한 절만 읽는다(전체 로드 불필요 — `## §N.` 헤더로 grep 가능).
