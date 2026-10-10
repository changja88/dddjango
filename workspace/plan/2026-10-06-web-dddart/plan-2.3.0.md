# dddjango-web 2.3.0 — 한 web 앱의 화면 제품마다 design_system 뿌리와 문서 셸(F4-71) (운영자 · 10-10 · 사전 설계 둘 · 설계 점검 · 구현 · 구현 검토 · 실제 장면 반영판)

## 바탕
- 바탕: R main `f19ced8b`(dddjango-web 2.2.6). 2.3.0 은 마이너다 — 새 규약(선택형 제품 선언)이 들지만 **검사 86종 그대로**(새 검사 ID 0 · 빚 스캔 지문 `CHECK_IDS` · `KEY_SCHEME` 무변 — 진행 중 레인의 동결본이 «판 경계» 에 걸리지 않게).
- 사본: 검사기 `<S>/web-230`(2.2.5 위에서 시작) → 보완 `<S>/web-230c` · 글 `<S>/web-230b` → 2.2.6 위로 합침 `<S>/web-230i` → 구현 검토 보완 `<S>/web-230j`. `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/web-230-notes/`(사전 설계 `design-claude.md` · `design-codex.md` · 설계안 `plan.md` · 설계 점검 `check-230.md` · 구현 `impl-scripts.md` · `impl-docs.md` · 검토 `review-scripts-*.md` · `review-docs-codex.md` · `review-final-*.md` · 보완 `fix-scripts-1.md` · `fix-final.md` · 합치기 `integrate.md` · 운영자 실측 `measure-operator.md` · 원문 `host-measure/`).
- 현장 보고: `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` F4-71(한 web 앱에 운영자 화면과 손님 화면 — 디자인 묶음 두 벌 · 화면 틀 둘인데 플러그인 규약은 뿌리 하나 · 틀 하나 → 손님 쪽 옛 파일 넷이 «옮길 자리가 없는 빚» 으로 남아 6-3-32 · 6-3-33 · 6-3-26 이 멈춤).
- 사용자(글자 그대로):
  - 결정 15 «가.»(10-10 14:24:09 date 뒤 · 14:25:02 date 앞) = 같은 web 안에서 제품마다 디자인 묶음과 화면 틀을 따로 둔다 · 운영자 것은 지금 자리 그대로 · 손님 것은 새 자리(`design_system/guest/…`)와 손님 전용 틀.
  - «수리를 좀 서둘러야 할거 같은데 지금 최대 리소르로 하고 있는거야? 그리고이제 codex, claude 모두 써도되»(14:15:08 date 뒤 · 14:16:20 date 앞) → 사전 설계 둘 · 구현 둘(검사기 · 글) · 검토를 Codex · Claude 로 한꺼번에.
  - 결정 16 «2.3.0은 끝나는 대로 배포하자. 그리고 결17은 준비되면 말해줘»(20:12 date 뒤 · 20:13:19 date 앞) = 검증(픽스처 · verify-web · 실제 장면 · Codex · Claude 검토 차단 0)이 끝나면 묻지 않고 배포하고 끝난 뒤 보고한다.

## 운영자 판정(플러그인 자신의 정의에서 나온 것 — 설계 점검이 «되돌릴 근거 없음» 확인)
| 갈린 곳 | 고른 것 | 까닭 |
|---|---|---|
| 선언 자리 | `web/product_registry.json`(git 추적 · `web/sdk_registry.json` 옆) | 검사기는 `.dddjango-web/config.json` 을 읽지 않고 승인 유입의 부모 측정은 `.dddjango-web` 을 뺀다 — 선언이 `web/` 안에 있어야 부모 판에도 실린다 |
| 선언 크기 | 이름 + 자리 꼴(`flat` / `own`) + 화면 범위(BC 목록)뿐 · 자리는 규약으로 고정 | «파일트리가 곧 규약» |
| 새 검사 ID | 0 — 기존 검사의 제품 분기 | 빚 스캔 지문 = 검사 ID 목록 + 키 꼴. ID 를 더하면 진행 중 레인 전부가 «판 경계» |
| 옛 값 파일을 그대로 새 자리에 받는 «보존» 꼴 | 없음 | «옛 배치는 규약이 아니라 아직 안 갚은 빚» — 면제 목록을 만들지 않는다 |
| 공용 HTML 부품 | 평면 `design_system/component/<군>/*.html` 마크업을 어느 제품이든 include(CSS 는 제품 뿌리의 같은 군 · 같은 이름) · `shared/` 자리 · 연결표 없음 | 지금 두 제품이 이미 그렇게 쓴다 |
| 페이지가 셸 CSS 를 직접 싣는 예외 | 만들지 않는다 | «잘못된 틀을 고른 손님 화면» 에서만 필요한 꼴 — 그 화면이 손님 틀로 바뀔 때 함께 없어진다 |

## 넣은 것
### 계약
- **제품 선언** `web/product_registry.json`(선택 · 사용자 결정으로만 쓴다): `{"schema": "dddjango-web-products/1", "products": {"<id>": {"design_system": "flat" | "own", "bcs": ["<bc>" | "<area>/<bc>", …] | "*"}}}`. `flat`(정확히 한 제품)= 지금 자리 `design_system/{foundation,theme,component,util}` + 셸 `root/scaffold/view/root_view.html` · `own` = `design_system/<id>/…` + 셸 `root/scaffold/view/root_<id>_view.html` + 틀 CSS `static/root/root_<id>_view.css`. `"*"` = application 아래 나머지 BC 전부(최대 한 제품 · 배열 밖 문자열로만). 선언에 적힌 BC 가 아직 없어도 오류가 아니다(예정 BC — 알림 한 줄).
- **선언 없음 = 2.2.6 그대로**(뿌리 하나 · 셸 하나 · 제품 폴더 자동 발견 없음). 새 규칙은 전부 «선언 있음» 뒤.
- **선언 오류 → exit 1 «판정 불가»**(무선언 동작으로 내려앉지 않는다): JSON 파손 · 중복 키 · schema · 타입 · 모르는 키 · `flat` 이 0 또는 2 이상 · id 꼴 · `"*"` 둘 이상 또는 배열 안 · 같은 BC 가 두 제품 · BC 경로 꼴(성분마다 소문자 snake_case 식별자 · 층 폴더 이름 금지 · 절대 경로 · `..` · 세 성분 이상) · 선언 자리가 일반 파일이 아님(링크 · 폴더) · 선언이 있는지 조사할 수 없음. 검증은 검사보다 먼저, 선언을 쓰는 모든 입구에서(게이트 · `--slice-end` · `--only` · `--all` · `--debt-scan`[`--refactor`] · `--debt-residual` · `refactor_audit`). `--subst-check` 는 선언을 읽지 않는다.
- **소속 판정**: 페이지 = 그 BC 의 선언 제품(상속한 셸이 아니다) · 셸 = 선언된 셸의 제품 · design_system CSS = 소유 뿌리의 제품 · BC 조각 CSS = 그 BC 의 제품 · 틀 CSS = 그 셸의 제품 · 옛 배치 최상위 폴더의 페이지 = 소속 없음.
- **혼입 금지**(IM13 제품 분기): 소속이 정해진 문서가 다른 제품의 표준 자리 CSS(foundation 표준 7 파일 · `theme/app_theme.css` · `component/<군>/*.css` · `util/*.css`)를 `{% static %}` 링크 · CSS `@import` · 정적 경로 `url()` 로 실으면 발견(꼬리 `?…` · `#…` 와 `..` 로 돌려 실어도 같은 판정). 게이트는 새 링크 줄 · 새 extends 줄(그 문서의 직접 CSS 링크 전부)만 — 손댄 파일의 옛 링크 · 선언만 바뀐 경우는 새 위반으로 만들지 않는다. 빚 스캔은 전수.
- **잘못된 셸**(IM26 제품 분기): 선언 BC 의 페이지는 그 제품 셸만 extends · 선언이 있으면 평면 셸과 own 셸 모두 독립 문서(어떤 템플릿도 extends 하지 않는다).
- **자리 규칙**: own 뿌리는 평면 뿌리와 같은 골격 · 같은 명명(ST10 · ST4 · NM10~12 를 제품 뿌리 안 상대 경로에 적용) · 평면 뿌리 직속은 네 종류 폴더 + 등록된 own 뿌리만 · 선언된 own 제품의 뿌리 골격 또는 셸이 없으면 ST4(신설 여부와 무관 · 빚 질문에서 **미룰 수 없음**).
- **착륙 묶음**: 새 own 제품의 선언 커밋과 그 제품의 골격 · 셸은 같은 착륙 묶음으로 넣는다 — 선언만 든 중간 상태에서는 골격 · 셸 부재가 모든 실행의 G2 에 선다.
- **선언과 무관하게 바뀌는 것**: 치환 확인이 static 접두를 건너는 이동(예: `web/static/css/base.css` → `web/design_system/guest/theme/app_theme.css`)의 치환을 받는다(static 식별자 · `/static/` URL · `web/…` 저장소 경로 문자열 — 2.2.6 은 «치환만으로 설명되지 않는다» 로 막았다).

### 검사기(두 벌 byte 미러 · 새 ID 0)
- 새 `src/products.py`(선언 적재 · 검증 · 경로 → 제품 · 셸 집합) · `check_structure.py`(ST10 · ST4) · `check_naming.py`(NM10~12) · `check_imports.py`(IM2 · IM13 · IM26) · `subst.py`(접두 횡단 치환) · `backstop.py` · `debt.py` · `refactor_audit.py`(사전 점검 배선 · 선언 파일은 어느 단위도 아님 · 선언 변경 알림 · 참조 완전성 grep 에서 선언 파일 제외 — `web/sdk_registry.json` 선례).
- 2.2.6 이 넘긴 한계 둘을 닫음: `inflow.py` 수신 증명의 링크 조사 범위 = 저장소 전체(루트가 저장소 하위 폴더인 프로젝트의 숨김 반례) · `check_purity.py` PU2 ③ 판독에서 점 하나(`.` · `?.`) 바로 뒤 낱말은 속성 이름(값) — `range.in / Kakao.x() / 2` 의 참조를 센다(숫자 리터럴의 점은 속성 접근이 아니다).
- 픽스처: `fixtures_patch230.py`(새) · `fixtures_patch226.py` · `fixtures_sdk.sh` · `fixtures_refactor_audit.sh` · `run_fixtures.sh`.

### 글(산문 정본 · Codex 미러)
하우스룰 §1(트리 · «제품 핵심 사실») · §3 · §5 · §6 · §8(선언 검증 · 판정 불가 · 미룰 수 없음 · 치환 확인이 받는 꼴) · architecture-ui · implementation-django(셸 · theme · 부품) · Coordinator(G0 제품 질문 · `chore(web-products):` 선언 커밋 · 착륙 묶음 · 개명 이동 묶음의 선언 갱신 · G2 배너 선언 diff · Phase 1 STOP 선택지의 처분 `플러그인 결함`) · 역할 넷(architect · review-ui · coder · discipline) · REQUEST_GUIDE(«어느 제품의 화면인지» 한 줄) · 지식 SKILL 요약 · AGENTS.md · README.

## 넣지 않은 것
- 평면 자리가 없는 구성 · 여러 web 뿌리 · 제품 뿌리를 리팩토링 입구의 단위로 · CSS 변수 이름 치환 행 · `var()` 로 다른 제품 토큰을 부르는 것의 검사 · include 된 조각 안 링크 · 동적 경로 · 옛 값 파일을 거친 간접 `@import` · 옛 배치 페이지의 제품 경계.
- PU2 벤더 분기의 제품 대응(셸 하나 전제 그대로).
- BC 개명 · 이동 뒤 선언에 남은 옛 BC 이름의 자동 차단(«예정 BC» 허용과 구별할 수 없다 — Coordinator 의 «개명 · 이동 묶음에서 선언의 BC 목록을 같이 고친다» 문장이 통제다).
- 선언 유입으로 판정만 바뀐 레인 파일을 승인 유입으로 가르는 것(레인이 지은 화면의 잘못된 셸은 그 레인 몫이 맞다).

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| S1 픽스처 · `make verify-web` | 2,607 실패 0(본체 171 · extract 53 · contract 13 · 2.2.5 픽스처 308 · patch226 114 · patch230 956 · debt 119 · subst 196 · sdk 368 · refactor_audit 309) · exit 0(최종 판 `7ae360dc`) |
| S2-무변 실제 장면 여덟(`<S>/web-226-notes/s2.sh`) | 여덟 모두 2.2.6 과 **byte 동일** |
| S2-무변 호스트 main 사본(`e3899198f` · 선언 없음) `--debt-scan --json` | 2.2.6 과 JSON(`scanned_at` 밖 전부) · 글 출력 같음(키 468 · 발견 635) |
| S2-판 경계 없음(6-3-33 장면 · 2.2.3 으로 동결한 기록 폴더에 `--debt-residual`) | 2.2.6 과 출력 byte 동일 · «판 경계» 0 · 선언을 얹은 뒤에도 «판 경계» 0(«G0 에 없던 키 4 — 보고만») |
| S2-손님 셸(호스트 main 사본에 선언 → 손님 골격 → 세 파일 이동 + 참조 치환 18 파일) | 선언만으로 기존 키 감소 0(새 키 6 — IM13 2 · IM26 2 · ST4 2) · 1단계 뒤 **옛 키 넷 사라짐**(`ST0|base/base.html` · `PU2|base/base.html` · `ST10|design_system/foundation/motion.css` · `ST12|static/css/base.css`) · 옮긴 새 자리의 키 0 · 게이트 exit 0 · 치환 확인 exit 0(같은 입력을 2.2.6 은 어긋남 3 으로 막음) |
| S2-잘못된 셸(6-3-13 장면에 «선언이 든 main» 을 승인 병합으로 받음) | 레인이 지은 손님 화면 둘(`preferences_view.html:1` · `shared_chart_view.html:1`)에 IM26 + 그 화면의 IM13 7 = 이 레인 몫 · main 이 들인 쇼케이스 · 가입 완료의 발견 12 는 승인 유입(종료 코드 밖) |
| S2-선언 오류(깨진 선언 열여섯 꼴 × 입구 여덟) | 모두 exit 1 «판정 불가 — 제품 선언 …» · `--subst-check` 만 설계대로 선언을 읽지 않음 |
| S3 구현 검토(Codex · Claude) | 검사기 · 글 따로(Codex 차단 3 · Claude 차단 2 / 글 Codex 차단 3) → 보완 1 · 합치기 → 합친 판(Codex 차단 4 — 셋 재현 · 하나 의도된 차이 / Claude 실해 차단 0) → 보완 → 재검토(Codex 차단 1 — 필터 붙은 `{% static %}` 과보고 · 재현 / Claude 차단 0) → 보완 둘째 → 재검토(Codex «배포 가능 · 차단 0» / Claude «배포 가능 · 차단 0» — 임시 저장소 재현 · 선언 없는 프로젝트 게이트 · `--all` · 빚 스캔 byte 동일) |
| S2 최종 판 재측정(`7ae360dc`) | 실제 장면 여덟 2.2.6 과 byte 동일 · 호스트 시점 넷 앞 후보와 같음(선언 전 2.2.6 과 같음) · 1단계 게이트 · 치환 확인 exit 0 · 필터 꼴 둘 IM13 0 · `./` 꼴 · 꼬리 안 `/../` 꼴 IM13 1 · 선언 없는 프로젝트의 `plan web/product_registry.json` 오류 문구 2.2.6 과 같음 · 6-3-33 잔존 2.2.6 과 같음 · 6-3-13 병합 장면 앞 후보와 같음 |

## 알려진 한계
- **선언 없는 프로젝트의 2.2.6 대비 출력 차이(의도된 것 다섯)**: ⓐ 치환 확인이 static 접두를 건너는 이동을 받는다 ⓑ 참조 완전성 grep 의 판정 명령 기록에 `':(exclude)web/product_registry.json'` 토큰이 붙는다 ⓒ 수신 증명의 링크 조사 범위(루트가 저장소 하위 폴더일 때만 달라진다) ⓓ PU2 ③ 의 JS 판독(점 · `?.` 바로 뒤 낱말과 `#이름` 은 속성 이름 · 숫자 리터럴은 한 토큰 — 2.2.6 이 놓치던 `range.in / Kakao.x() / 2` · `1..in / …` · `this.#in / …` 의 참조를 세고, 2.2.6 이 판독 불명으로 소비로 세던 `1. / "Kakao" / 2` 는 참조 아님) ⓔ `web/product_registry.json` 이 있는지 조사할 수 없는 환경(예: `web/` 탐색 권한 없음)은 exit 1 «판정 불가» — 2.2.6 은 아무것도 검사하지 못한 채 통과했다.
- 제품 혼입 보증은 표준 자리의 직접 정적 참조까지다 — 표준 7 파일 밖 foundation 파일(옛 `tokens.css` 류) · 제품 뿌리 직속 파일 · 동적 경로 · include 를 따라간 참조 · 옛 값 파일을 거친 간접 `@import` · `var()` 로 부르는 다른 제품 토큰은 보증 밖(감수 몫).
- `{% static %}` 의 닫는 따옴표 뒤에 공백을 두고 다른 토큰이 오는 꼴(`'…css' |cut:'x'` · `'…css' extra` · `'…css' as` · `'…css' as css extra` — Django 는 공백 뒤 토큰을 버리고 그 파일을 싣는다)은 혼입 판정에서 빠진다(놓침 쪽 · 정상 코드에 안 나오는 꼴 · 다음 web 판에서 닫는다 — 최종 재검토 Claude). 줄바꿈이 낀 `{% static %}` 태그는 2.2.x 부터 혼입 판정에 들어간다(Django 는 태그로 안 봄 — 과보고 쪽).
- 혼입 판정이 못 읽는 참조 꼴: 하드코딩 `href="/static/…"` · `<style>@import …</style>` · 대소문자만 다른 파일 이름(대소문자를 안 가리는 파일시스템) · 필터 · 변수가 붙은 `{% static %}` 인자(동적 경로). 앞머리 `./` 와 꼬리(`?…` · `#…`) 안의 경로 꼴은 이 판에서 읽는다.
- `web/product_registry.json` 은 예약 이름이다 — 같은 이름의 다른 JSON 이 있는 프로젝트는 판정 불가. git 이 무시하는 선언은 승인 유입의 부모 측정에 실리지 않는다.
- 옛 배치 최상위 폴더의 페이지는 어느 제품에도 속하지 않는다 — 그 페이지가 틀을 잘못 고르는 것은 이 판이 막지 않는다(레인이 새로 만든 옛 배치 페이지가 옮겨진 옛 셸 · CSS 를 가리켜도 백스톱은 조용하다 — 화면은 깨진다).
- 디렉터리 발견(ST10 허용 밖 폴더 · ST4)은 승인 병합이 들여도 승인 유입으로 가르지 못한다(기존 동작).
- PU2 벤더 분기는 셸 하나 전제 — own 셸에 SDK 를 실으면 «block 밖» 과보고 · 평면 셸의 SDK 를 own 페이지에도 실린 것으로 읽는 중복 과보고 · own 셸 + own 페이지 중복 로드는 놓침.
- BC 를 개명 · 이동하고 선언의 옛 이름을 그대로 두면 옛 이름은 «예정 BC» 알림으로 지나간다(`"*"` 제품이 있으면 새 BC 는 그 제품으로 · 없으면 소속 없음).
- 치환 확인의 접두 횡단은 static 식별자 · `/static/` URL · `web/…` 저장소 경로 문자열만 받는다 — web 기준 상대 경로(`"static/css/…"`) 꼴은 지원 밖.
- 수신 증명(2.2.6): 루트가 저장소 하위 폴더인 프로젝트에서는 레인이 루트 밖 자리의 링크를 손대기만 해도 수신 증명이 전부 꺼진다(막는 쪽) · 저장소 밖 링크 · git 이 무시하는 미추적 링크는 여전히 보지 않는다.
- PU2 ③ 판독은 완전한 JS 낱말 가름이 아니다 — 문자열 접근(`window["<전역>"]`) · 간접 호출 · 같은 이름의 지역 변수는 2.2.6 그대로.
- 호스트 1단계는 완전한 CSS 격리가 아니다 — 손님 셸은 옛 `tokens.css` · `components.css` · `app_shell.css` 를 옛 자리에서 계속 싣는다(그 파일들의 빚 키는 그대로 남는다).

## 호스트가 할 일(배포 뒤 · 플러그인 밖)
1. 선언 + 손님 골격(`web/design_system/guest/{foundation(표준 7 파일),theme,component,util}`) + 손님 셸(`web/base/base.html` → `web/root/scaffold/view/root_guest_view.html`) + 두 파일 이동(`web/static/css/base.css` → `web/design_system/guest/theme/app_theme.css` · `web/design_system/foundation/motion.css` → `web/design_system/guest/util/motion.css`)과 참조 치환을 **한 착륙 묶음**으로 main 에 넣는다(scratch 사본 `<S>/f71/host` 의 커밋 셋이 그 꼴 — 치환 18 파일 · 23 줄). 선언의 운영자 BC 목록에는 예정 BC(`admin/operator_teller`)도 넣는다.
2. 선언이 main 에 들어간 뒤 진행 중 레인이 main 을 받으면 그 레인이 지은 손님 화면이 운영자 틀을 상속한 줄이 그 레인 몫으로 선다(6-3-13 의 `preferences_view.html` · `shared_chart_view.html` · 6-3-26 도 해당 가능) — 레인 착륙 뒤에 선언을 넣거나, 넣고 손님 틀로 바꾸게 한다.
3. 1단계가 main 에 들어간 뒤 main 을 받은 레인은 옮겨진 옛 이름 셋(`base/base.html` · `web/css/base.css` · `design_system/foundation/motion.css`)을 자기 변경에서 grep 한다 — 옛 배치 폴더에 새로 만든 페이지가 옛 이름을 가리켜도 백스톱은 잡지 않는다.
4. 별도 작업(화면 변화 · 기존 시험 기대값 변경 승인이 든다): 운영자 틀을 고른 기존 손님 화면 둘(쇼케이스 · 가입 완료 — 선언 뒤 빚 키 IM26 2 · IM13 2 로 보인다)의 손님 틀 전환과 틀 CSS `app_shell.css` 이동 · `components.css` 해체 · `tokens.css` 분해. 손님 화면의 틀 전환(extends 줄 변경)은 그 문서가 싣던 운영자 표준 CSS 링크를 한꺼번에 게이트에 세운다(쇼케이스는 9줄) — 틀 전환과 링크 정리를 한 묶음으로 한다.
