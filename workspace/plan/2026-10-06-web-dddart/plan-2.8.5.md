# dddjango-web 2.8.5 — 글꼴 줄임 뒤 숫자 모양 허용 · htmx 상태 class 는 조상 자리로 읽지 않는다 (F4-127 · F4-129)

상태: 계획 사용자 승인(2026-10-30 · «진행») → 구현 · 작은 수리 둘(규칙 글만 · scripts 무변).

## 문제

- **F4-127**(낮음 · 규칙 빈자리): 규칙 «`--typography-*` 는 `font` 줄임 묶음 값 — 같은 규칙에서 그 뒤에 `font-*` 를 다시 선언하지 않는다»(houserules `final.md:227` · implementation-django `final.md:1411`)를 글자대로 따르면 숫자 칸 맞춤(`font-variant-numeric: tabular-nums`)을 쓸 길이 없다.
  - 재현(배포판 2.8.4 규칙 글 · 헤드리스 Chromium 계산값): `font-variant-numeric: tabular-nums; font: 16px serif;` → `normal`(줄임이 초기값으로 되돌림) · `font: 16px serif; font-variant-numeric: tabular-nums;` → `tabular-nums`. 즉 같은 규칙에서는 **줄임 뒤에만** 살아남는데, 규칙 글이 그 자리를 막는다. 보고는 «줄임이 덮지 않는 속성»이라 했으나 실제로는 덮는다 — 결론(규칙 글 빈자리)은 같다.
  - 규칙의 목적은 토큰 묶음(글꼴 · 크기 · 굵기 · 줄 높이 · 기울임)을 부품이 부분 덮지 않게 하는 것이다. 숫자 모양은 묶음에 담을 수 없는 값이라 목적과 부딪히지 않는다. 검사기(NM10)는 `font-variant-numeric` 을 글자 리터럴로 세지 않는다.
- **F4-129**(낮음 · 오탐 후보로 접수): 부품 CSS `.htmx-request .standard-button__busy { … }` 를 NM12 가 «접두 위반» 으로 잡는다.
  - 재현(배포판 2.8.4 `check_naming._css_classes`): 조상 자리 `.htmx-request .x__busy` → 위반 · 겹친 꼴 `.x__busy.htmx-request` → 통과 · 남의 class `.card-panel .x` → 위반.
  - 검사기는 규칙 글(implementation-django `final.md:1439` «htmx 상태 클래스는 접두 붙은 클래스와 겹친 선택자로만») 그대로다 — 오탐이 아니다. 규칙 안에서 같은 화면을 만드는 길이 있다: 요청 중에 바꿀 요소(단추 안 링)를 `hx-indicator` 로 가리키면 htmx 가 그 요소에만 `htmx-request` 를 붙이고, 부품 CSS 는 `.x__busy.htmx-request` · `.x:has(> .x__busy.htmx-request) > .x__icon` 로 읽는다.
  - 조상 꼴을 허용하면 생기는 일: htmx 는 `hx-indicator` 가 없으면 요청을 낸 요소에 `htmx-request` 를 붙인다 — 그 단추를 품은 바깥 영역(목록 새로 고침 등)이 요청을 내도 안쪽 단추 링이 모두 켜진다.
  - 빈 곳은 규칙 글이 이 길을 말하지 않는 것이다(레인은 이 길을 찾지 못하고 오탐으로 올렸다).

## 고침 (지식 글만 · Claude 정본 → Codex byte 복사 · 검토 반영 뒤 최종)

1. houserules `final.md:227` · implementation-django `final.md:1411`(같은 문장 두 곳): 금지 «같은 규칙에서 그 뒤에 `font-*`를 다시 선언하지 않는다» 는 그대로 두고 뒤에 «예외는 묶음에 없는 숫자 · 합자 모양(`font-variant-numeric`·`font-variant-ligatures`·`font-feature-settings`) 셋뿐이고, 줄임이 이 값들을 초기값으로 되돌리므로 줄임을 쓴 그 규칙 안 `font` 뒤에 둔다(부모 규칙에 두면 자식의 줄임이 지운다)» 를 더한다.
2. implementation-django `final.md:1439`(부품 CSS 절 · htmx 상태 class 문장 뒤): «접두 클래스와 겹치지 않은 `.htmx-request`를 조상 자리(`.htmx-request .spinner-loading`)에 두지 않는다(바깥 영역의 다른 요청에도 켜진다). 부품이나 부품 안 한 요소만 요청 중에 바꾸려면 요청을 내는 요소(감싼 폼이 보내면 그 폼)의 `hx-indicator`로 그것을 가리키고 겹친 선택자로 읽는다 — 부품을 가리켰으면 `.standard-button.htmx-request .standard-button__busy`처럼 겹친 묶음은 조상 자리여도 된다(implementation-htmx §5).»
3. implementation-htmx `final.md` 속성 표 `hx-indicator` 줄 · §5 «요청 중(조각)» 줄: 다는 자리(요청을 내는 요소 — 안쪽 단추에 단 것은 무시된다) · 가리키는 대상(로딩 부품 · 요청 중 모양이 바뀌는 부품이나 그 안 요소) · 부품 CSS 는 접두 클래스와 겹친 선택자로 읽는다. 계획 뒤 더함 — 행동 시험 첫 바퀴에서 두 세션 모두 «로딩 부품만 가리켜야 하나» 로 망설였다.
4. implementation-django `SKILL.md:33` 요약 줄(+ Codex 같은 뜻): «htmx 상태 클래스는 접두 클래스와 겹쳐서만(NM12)».
5. 검사기(NM12)는 그대로 둔다(승인 범위).

## 되돌아옴 막기

- `make verify-web` 레시피 계약 줄: 글꼴 예외 문장 두 곳 · 1439 조상 자리 문장 · htmx §5 다는 자리 · 대상 문장 있음(양성 grep — 배포판 글에 대면 붉음 확인). Claude · Codex 는 기존 references byte 미러 대조가 잡는다.

## 행동 시험 (새 세션 · 규칙 발췌만 주고 같은 일감 · 옛 글 / 새 글)

- **F4-127**(가격 표시 부품 · 숫자 칸 맞춤): 옛 글 → 같은 선택자를 규칙 둘로 쪼개 «글자 그대로는 지켰지만 의도에 어긋날 수 있다» 며 망설임 · 새 글 → `font: var(--typography-body); font-variant-numeric: tabular-nums;` 한 규칙 · 망설임 없음. 옛 판 재현 · 새 판 해소.
- **F4-129**(감싼 폼이 요청하는 동안 단추 안 링): 두 바퀴.
  - 첫 바퀴(일감에 «목록 영역 새로 고침» 힌트가 있었음): 옛 글 · 새 글 모두 `hx-indicator` 로 단추를 가리키고 `.standard-button.htmx-request …` 겹친 꼴 — 둘 다 «로딩 부품만 가리켜야 하나» 로 망설임 → 고침 3 을 더함.
  - 둘째 바퀴(힌트 없이 실제 규칙 글 그대로 · 새 글은 고침 3 포함): 옛 글 · 새 글 모두 바른 꼴. 새 글은 망설임 없음 · 옛 글은 «폼에 indicator 를 안 달면 조상 꼴이 필요한데 문구에서 벗어난다» 고 스스로 판단.
  - 결론: 작은 장난감에서는 옛 글로도 결함(조상 꼴)이 재현되지 않았다 — 현장 레인은 큰 맥락 속에서 조상 꼴을 썼다. F4-129 글 고침은 «규칙 안의 길을 적어 둔 정리» 이고 효과는 이 시험으로 보이지 않았다(멈출 기준 «새 글도 같은 잘못» 은 해당 없음).

## 독립 검토 반영(차단 0 · 중요 2 · 사소 7 → 좁은 재확인 중요 2 닫힘 · 새 사소 2)

- 중요 1 받음: `hx-indicator` 를 어디에 다는지 글에 없었다 — htmx 2.0.10 은 요청을 낸 요소에서 위로만 `hx-indicator` 를 찾는다(`findAttributeTargets` → `getClosestAttributeValue`) · 폼 안 단추에 단 것은 무시된다 → 고침 2 · 3 에 다는 자리.
- 중요 2 받음: «감싼 요소의 `htmx-request` 를 조상 선택자로 읽지 않는다» 는 글자대로면 `.standard-button.htmx-request .standard-button__busy`(NM12 통과 · 바른 꼴)까지 막았다 → 금지를 «접두 클래스와 겹치지 않은 `.htmx-request`» 로 좁히고 겹친 묶음 허용을 적음.
- 사소 받음: 3 · 4 · 5 글꼴 예외를 닫힌 셋 + 그 규칙 안 + 부모 주의로 · 7 의 SKILL 요약 줄 · 9 와 재확인 사소 2 계약 줄 보강(속성 표 줄 · 허용 문장) · 재확인 사소 1 docs «판마다 바뀐 것» 줄 문구.
- 받지 않음: 6 architecture-state `final.md:72` 는 로딩 화면을 부품으로 include 하라는 줄이지 `hx-indicator` 대상을 좁히는 글이 아니다 · 7 의 NM12 안내문(htmx 상태 class 일 때 겹친 꼴 안내)은 검사기 코드라 승인 범위 밖 — 다음 후보 · 8 `htmx-indicator` 를 «htmx 가 붙이는 상태 클래스» 로 적은 기존 글(htmx 는 붙이지 않는 표지이고 htmx 기본 CSS 가 조상 꼴로 읽는다)은 이번 변경 전부터 있던 것 — 다음 후보.
- 검토자 실측: 헤드리스 Chromium 1243 + htmx 2.0.10 원본(S1~S9) · 배포판 `_css_classes` · NM10 · 계약 줄 붉음 넷.

## 검사 · 문서

- 바뀐 경로: web md(Claude · Codex) · `Makefile` · 판 기록 → `make verify` 전체 + `make verify-web` 의 `run_fixtures.sh` 뒤 줄(§5 «검사 고르기» · 커밋 뒤 push 전 한 번).
- 문서: 판 표기 2.8.5(master · work_flow_web_guide(+ «판마다 바뀐 것» 줄) · work_flow_web · file_tree_web) · 요청 가이드 확인.

## 한계

- F4-129 의 레인 코드는 그대로면 다음 빚 판정에서도 NM12 로 잡힌다 — 고칠 길은 규칙 글이 알려 준다(레인 일).
- `font` 줄임이 정하는 값 목록은 CSS Fonts 4 의 줄임 구성 그대로다 — 토큰이 그중 일부만 쓰더라도 나머지를 다시 선언하는 것도 막는다(토큰이 정하지 않은 값을 부품이 정하는 길은 foundation 토큰 추가).

## 멈출 기준

- 행동 시험에서 새 글도 같은 잘못을 내면 글을 다시 쓰고, 두 번째도 같으면 멈추고 묻는다.
