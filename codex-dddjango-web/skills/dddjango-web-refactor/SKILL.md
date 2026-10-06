---
name: dddjango-web-refactor
description: 사용자가 `$dddjango-web-refactor <대상 단위> [불편 서술]` 로 명시적으로 부를 때만 쓰는 dddjango-web 리팩토링 입구. 대상 단위 하나의 기존 web 코드 전체를 표준으로 정리한다(동작 불변). 자연어 요청에는 쓰지 않는다.
---

# dddjango-web 리팩토링 입구

형제 스킬 `dddjango-web` 의 Coordinator 로 작동하라. 본문은 이 스킬 폴더의 형제 `../dddjango-web/SKILL.md` 다 — 먼저 `wc -l` 로 길이를 잰 뒤 구간으로 나눠 끝까지 읽는다(도구 출력이 중간에 잘릴 수 있다 — 마지막 절 «리팩토링 모드»의 끝 문장까지 읽어야 한다). 그 Coordinator 문면의 `scripts/` 와 역할 스킬 경로의 기준은 형제 `../dddjango-web/` 폴더다.

Coordinator 의 요청 첫 줄은 아래 한 줄을 그대로 쓴다. `<인자>` 자리에는 사용자가 이 스킬 이름 뒤에 적은 글을 한 글자도 바꾸지 않고 넣는다. 다른 일은 하지 않는다.

리팩토링 모드(입구 $dddjango-web-refactor) · 대상: <인자>
