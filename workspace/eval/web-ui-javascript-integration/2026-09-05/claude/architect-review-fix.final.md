완료 — 리뷰어 finding 1(호스트 include 모호성)만 제자리 해소했고, 다른 절·경계·파일 목록은 불변이다.

## 변경된 절과 이유

1. **§6 라우팅·HTMX — 신규 하위 표 "HTMX 선언 조각의 include 호스트·지배 플래그"**
   - 3개 선언 조각 ↔ include 호스트 템플릿 ↔ 지배 플래그를 **1:1로 확정**: `ui_lab_panel_swap.html` → `section/ui_lab_panel.html` / `panel.root_swap_enabled`(패널 B만), `ui_lab_preview_swap.html` → `section/ui_lab_preview.html` / `preview.child_swap_enabled`(패널 A만), `ui_lab_note_swap.html` → `section/ui_lab_note.html` / `note.swap_enabled`(패널 A만). 조건 판형(`{% if %}{% include %}{% endif %}`)까지 표기.
   - *왜*: 호스트가 «그 조각이 교체하는 단위 자신»이어야 outerHTML 교체 후에도 트리거가 재렌더되어 반복 swap(I7)이 성립한다(architecture-web §4). 페이지 템플릿 include는 **0건**으로 명시 금지했다.
   - 조건은 §4 VM이 이미 결정한 bool의 단순 표시 분기임을 못 박아 템플릿 판단 금지 규율(architecture-web §3·implementation-ui §4)을 유지했고, 이로써 패널 B의 미리보기/노트에 자식 swap 트리거가 렌더될 여지를 없앴다(요구 4·5 경계).
   - 각 조각의 target id는 §6 DOM id 계약의 고정 문자열을 쓰며 참 인스턴스가 1개뿐이라 id 계산이 불필요함을 명시(코더 발명 지점 제거).

2. **§7 UI 동작 계약 — swap 3행의 «JS/HTMX 파일» 칸**
   - 각 칸에 include 호스트 section과 지배 플래그 조건을 병기. *왜*: 리뷰어가 지적한 «§6 의도 ↔ §12 표기 불일치»를 계약 표 자체에서 단일 사실로 읽히게 하기 위함.

3. **§12 파일 목록 — 신규 19·20·21 비고**
   - 각 선언 조각 행에 호스트·조건을 병기해 파일 목록만 보고 작업하는 경로에서도 배치가 확정되게 함(파일 목록/슬라이스 도출 입력 정합).

4. **§12 «템플릿 참조 경로» 문장**
   - 기존의 호스트 미지정 예시(`{% include "static/htmx/ui_lab_panel_swap.html" %}`)를 **"페이지가 아니라 §6 표가 지정한 section에서, 같은 표의 VM 플래그 `{% if %}` 안에서만 include"**로 교체. *왜*: 이 문장이 코더에게 §6과 다른 사실(페이지 include)을 줄 수 있던 실제 모호성 원인이었다.

5. **§13 자기 점검 — 수량 대조 1줄**
   - `fragment 라우트 3 = view 함수 3 = section swap 단위 3 = 선언 파일 3 = include 호스트 3 = 지배 플래그 3(페이지 include 0)`으로 대조 항을 확장.

## 하지 않은 것
- nit 2~5(disclosure 소유 템플릿 행, R4 결정 기록, `autocomplete` 값 확정, `--border-color` 신설)는 **미반영** — 지시대로 스타일 nit에 추가 토큰·선택 기능을 만들지 않았고, 나머지는 구현 계약 사실의 실질 누락이 아니라 판단했다(disclosure는 §2 «section 신설 없음»과 §7 «JS 필요 없음»으로 이미 결정 상태, 노트 배치는 §6에 근거가 서술됨).
- 동작·경계·파일 목록·토큰 처분·행위 목록은 전부 불변. UI 구현 코드는 작성하지 않았다.
- 쓴 파일은 `/private/tmp/dddjango-web-js-integration-20260905/claude/app/design.md` **하나뿐**이다. 브라우저 실행·`manage.py check`는 수행하지 않았으므로 어떤 검증 성공도 주장하지 않는다.