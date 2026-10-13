# dddjango-web 2.4.4 — SH1 «화면» 을 규칙 글의 소속에 맞춘다 (F4-91)

## 문제
- 레인 6-3-35 가 G2 앞에서 멈췄다. 지속 셸 안 부스트 링크 둘을 SH1 이 셸 밖으로 셌다(검사기 이의).
- 원인 ①: `check_shell.py` `_sh1` 의 화면 정규식 `/presentation_layer/(view|section|widget)/` 이 하우스룰 §2 의 개념 폴더 꼴 `presentation_layer/<개념>/section/` 을 놓쳤다.
- 원인 ②: 화면 후보가 «씨앗 ∪ extends 사슬» 뿐이라 사슬이 include 로 그리는 옛 배치 조각이 빠졌다. 규칙 글(implementation-django §2)은 «사슬이 include 하는 템플릿도 지속 셸 소속» 이다.

## 고침
- 화면 = 2.4.3 몫 ∪ (새 몫 − 표준 문서 이동 셸이 그리는 템플릿).
  - 새 몫 = 씨앗 ∪ (사슬 + 사슬에서 include 간선만 거듭 따른 템플릿) 가운데 개념 폴더 한 단을 허용한 view · section · widget · `root/scaffold/view/` · 옛 배치 경로.
  - include 대상이 extends 하는 부모 쪽은 따르지 않는다(설계 검토 차단 — 문서 레이아웃의 조각까지 넓어짐).
  - 문서 이동 셸 쪽 = 지속 아닌 표준 셸의 extends 사슬과 그 렌더 닫힘. 지속 셸이 없으면 계산하지 않는다.
- SH1 발견은 줄기만 한다(2.4.3 에서 통과한 것은 모두 통과). SH2 ~ SH5 · 다른 검사 · 빚 지문 무변.
- 규칙 글: implementation-django §2 지속 셸 절(화면 정의 + 두 방향 한계) · 867 줄 «hx-boost 는 nav 한 곳에만» 을 §9 와 맞춤 · implementation-htmx §9 참조 한 줄. Codex references byte 미러.

## 한계
- 막지만 규칙상 허용: 변수 include 로만 그리는 옛 조각(글자 include 로 고친다) · hx-get 응답으로만 지속 화면에 들어가는 옛 조각 · 카드 base 꼴(이 둘은 검사기 이의).
- 통과하지만 위반일 수 있음: 지속 셸 제품의 평평한 자리 view · section · widget 을 문서 셸 화면도 그림(2.4.3 부터) · 옛 문서 레이아웃이 함께 그리는 조각 · 문서 화면이 SH1 이 못 보는 길(변수 include · 변수 extends · hx-get 조각 응답)로 함께 그리는 조각(지속 제품 · 옛 배치 · 다른 제품 모두) — 감수.

## 시험
- `fixtures_patch240_shell.py` Z9: 경우표(선언 있음/없음) — 고치기 전 코드에서 10 붉음. 2.4.3 러너(`1328eba4` 고정)와 SH1 밖 출력 대조 · SH1 은 줄기만.
- 설계 검토: Claude 두 번(1판 차단 1 · 2판 차단 1 = 글 문장) — 기록은 운영 scratch `f91/`.
- 구현 검토(Claude): 차단 2 · 사소 3 — 모두 글 · 시험. 화면 정의를 셋(① 평평한 자리 · ② 개념 폴더 · ③ 사슬의 글자 include 닫힘 — 옛 배치 · 다른 제품 포함)으로 바로 적고, 통과 한계에 «문서 화면이 SH1 이 못 보는 길로 함께 그리는 조각» 을 넓혔다. Z9 의 옛 러너 대조는 `--only` 없이 전체 출력으로 본다.
- 재확인(Claude): 차단 0 · 사소 1(① root 조각은 선언 없을 때만 · ③ application 아래는 view · section · widget 만 — 글을 SH1 에 맞춤).
