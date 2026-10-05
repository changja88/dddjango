---
name: dddjango-web-architecture-ui
description: dddjango-web 프레젠테이션 아키텍처 — view/section/widget 3단 작성 규율과 승격 규칙, ui_extension(템플릿 필터), BC 루트 라우팅 짝(router·navigator), design_system 사용 규칙(전역 JS show() 진입 금지). 화면을 분해·작성·검수할 때 로드한다.
user-invocable: false
---

# 프레젠테이션 아키텍처

## 언제 쓰나

화면을 분해·작성·검수할 때, UI 조각의 단(view/section/widget)을 정하거나 승격할 때, URL·내비게이션을 만들 때, design_system 토큰·컴포넌트를 쓸 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일·폴더·명명·import 매트릭스 **사실**(design_system 허용 위치 닫힌 열거 포함) → `dddjango-web-discipline-houserules`
- VM·State 계약·에러 표시 소비 패턴 → `dddjango-web-architecture-state`
- 화면 귀속 tie-break·판별 경계 사례 → 공유 reference `undecidable.md`(dddjango-web-discipline-houserules 동봉)
- urls·템플릿·CSS **표기법** → `dddjango-web-implementation-django`

## 핵심 운영 원칙

- 3단은 크기가 아니라 VM 보유(view)/화면 전속(section)/재사용(widget)으로 가른다 — 판별은 위에서부터, 처음 해당하는 것이 답 (§1)
- VM 호출은 view 하나뿐 — view는 자기 VM(+같은 BC SharedState)만 부른다, 임베드 view는 자기 VM을 스스로 부르므로 배치만(`hx-trigger="load"` 자리 하나 → 자식 `<화면>_embed_fragment`) (§2)
- section·widget은 VM·SharedState 접근 금지 — include 인자·href만. section은 화면 State 가능(전속), widget은 화면 State 금지 (§3)
- 테스트가 집는 슬롯·tile은 안정 식별 속성·공개 표면으로 노출 — 구별 슬롯에 리터럴 `data-testid` 부착(dddjango-web-discipline-test §3.3/§3.4 FORM과 짝) (§3)
- 자기 상태·로직이 필요하면 버튼 하나여도 view 삼총사로 — section에 VM 호출이 필요해지는 것은 승격 신호이지 예외가 아니다 (§1·§4)
- 성장하면 단을 옮긴다: 두 번째 화면→widget으로, 상태 발생→view+vm으로, BC 어휘 탈피→design_system으로 (§4)
- 도메인 enum·VO→UI 매핑(CSS 클래스·아이콘 이름·라벨)은 ui_extension이 유일한 자리 — 템플릿 필터만, 템플릿 조각·상태 금지 (§5)
- URL path·name 리터럴은 `<bc>_router.py` 안에서만 — navigator는 이름만 참조(`reverse`), View import 금지, 템플릿은 State의 href (§6)
- 시각 값·정적 에셋 경로는 foundation 토큰만 — 색·생 글자 스타일·매직 연출 시간·raw 이미지 경로 리터럴 금지, CSS의 정적 래스터 경로는 `--asset-*` (§7)
- design_system 컴포넌트에 전역 JS 진입 함수로 스스로를 띄우는 show() 경로 금지 — 표시는 view 템플릿이 State로 include한다 (§7)
- BC 어휘를 벗은 부품만 design_system 승격 — 부품군 폴더로, 정크드로어 금지 (§4·§7)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 이 조각은 view·section·widget 중 무엇인가 | [`references/final.md`](references/final.md) §1 |
| view가 불러도 되는 범위·정적 view | final.md §2 |
| section·widget이 받아도 되는 것·접두 규칙 | final.md §3 |
| 언제 단을 옮기나 — 승격·이동 | final.md §4 |
| 도메인 값을 CSS 클래스·아이콘으로 바꾸는 곳 | final.md §5 |
| URL·내비게이션 작성 — router·navigator 분업 | final.md §6 |
| 토큰·컴포넌트 사용, show() 금지, 승격 절차 | final.md §7 |
| 판별이 갈리는 경계(VM 필요성·맥락·화면 귀속) | 공유 reference `undecidable.md` §1·§2·§3 (dddjango-web-discipline-houserules 동봉) |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
