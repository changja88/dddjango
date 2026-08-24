---
name: architecture-web
description: dddjango-web 프레젠테이션 아키텍처 — view/section/widget 3단 판별과 승격 규칙, 요청 구동 MVVM 삼총사 규율, HTMX 부분 재렌더, client 계약 소비와 스냅샷 체계, 라우팅 리터럴 단일 출처, design_system 토큰·component 사용. web 화면 표면을 설계·리뷰할 때 먼저 로드한다. 트리·명명·import 사실은 discipline-web-houserules, HTML·삼총사 .py·client·urls 표기는 implementation-ui, 클린코드는 discipline-cleancode로 위임.
user-invocable: false
---

# dddjango-web 프레젠테이션 아키텍처

## 언제 쓰나

화면을 분해·작성·검수할 때, 조각의 단(view/section/widget)을 정하거나 승격할 때, client 계약 소비·라우팅·design_system 사용을 결정할 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일·폴더·명명·import 방향 **사실** → `discipline-web-houserules`
- HTML·삼총사 .py·client·urls **표기** → `implementation-ui`
- 이름·함수 형태·중복 등 클린코드 → `discipline-cleancode`
- 판별이 갈리는 경계 사례 → 공유 reference `undecidable-web.md`(`discipline-web-houserules` 동봉)

## 핵심 운영 원칙

- web은 «내부의 외부 클라이언트»다 — 백엔드 BC는 실물 API 계약(URL+JSON)으로만 소비, `application/**` import 0. 없는 API는 가정하지 않고 «/dddjango로 발주»를 안내한다 (§1·§6)
- 요청 구동 MVVM — VM은 무상태 조립기로 매 요청 재조립된다. watch·구독·상주 상태 없음 (§1)
- 형상의 유일 근거는 동결 시안 — 명세에 산문 레이아웃 서술 금지·재현하되 직수입 금지. 기술은 순수 HTML+HTMX+CSS뿐(JS는 vendored 2파일 — htmx·motion 러너[조건 설치], 화면 코드는 `data-motion` 선언만) (§1)
- 3단은 크기가 아니라 상태 조립(view)/화면 전속(section)/재사용(widget)으로 가른다 — 판별은 위에서부터, 처음 해당하는 것이 답 (§2)
- view는 얇은 진입점(URL 바인딩·VM 호출·render·fragment 소유)뿐 — 판단 금지, 표시 판정은 VM이 유일한 자리다 (§3)
- state는 불변 dataclass·템플릿이 아는 유일한 모양 — 패키지 타입 직노출 금지(예외: 검증 실패 재렌더용 Django Form 1종 허용). 입력 검증=form(`form/` 조건 생성)·표시 상태=VM 분담 (§3)
- section·widget은 dumb — section은 화면 접두 필수·HTMX 재렌더 단위(hx-target), widget은 명시 context만(`with … only`). fragment 진입점은 소속 view 소유·페이지와 같은 auth·CSRF (§4)
- 성장하면 단을 옮긴다: 두 번째 화면→widget, 상태 조립 발생→삼총사 승격, BC 어휘 탈피→design_system(widget이 두 번째 영역에서 필요해져도 같은 경로 — 탈피 불가하면 설계 반송) — 타 영역 widget include 금지, state 렌더 또는 명시 context만으로 성립하면 승격 금지 (§5)
- 호출 코드는 client/ 전속 — in-process HTTP·driving_layer api 표면만·web 소유 응답 모델 파싱(schema import 금지)·오류는 client exception. 계약은 동결 스냅샷이 사실의 출처 — coder-web은 기계 절단 경량본만 보고, 에이전트는 스냅샷을 갱신하지 않는다 (§6)
- 라우트 리터럴 단일 출처 — 자기 화면 path·name은 urls.py, BC API URL은 client 모듈. 참조는 `{% url %}`/`reverse` 이름만 (§7)
- 시각 값은 tokens.css 토큰만·component 재사용 우선·BC 어휘는 입장 불가 — BC 어휘 표시 매핑은 VM이 그 자리 (§8)

## 상세 레퍼런스

| 주제 | 절 |
|---|---|
| web 트랙의 정의·경계·handoff | [`references/final.md`](references/final.md) §1 |
| 이 조각은 view·section·widget 중 무엇인가 | final.md §2 |
| view·VM·state 규율과 forms 분담 | final.md §3 |
| section·widget·HTMX fragment 규율 | final.md §4 |
| 언제 단을 옮기나 — 승격·이동 | final.md §5 |
| client 전속·계약 스냅샷·발주 안내 | final.md §6 |
| 라우팅 — 리터럴의 단일 출처 | final.md §7 |
| 토큰·component 사용, BC 어휘 차단 | final.md §8 |
| 판별이 갈리는 경계 — VM 필요성 §1·전속/맥락 §2·widget↔design_system §3 | 공유 reference `undecidable-web.md`(discipline-web-houserules 동봉) |
| 영역 귀속 — Coordinator G0 배치축·사용자 판정 소관(설계자는 ③ 위임 시에만 결정) | undecidable-web.md §4 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
