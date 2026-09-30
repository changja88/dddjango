# 진단 — web plan 경계 교차 소비자 누락 (2026-09-30)

> 진단 서브에이전트 결과를 운영 세션이 옮겨 저장(사용자 결정 09-30 10시대 «둘 다 지금 진단 (권장)» · 11:50 «배포전에 고치자»).
> 기준 HEAD `a1d97bc3`(plan 절은 6b `3c3f0e8f` 이후 무변 → 리허설 실행본과 같음 · Codex 미러 byte 동일). scratch 산출물: `diag-plan-consumer/`(`repo/` 레인 사본 APFS 복제 · `head/` · `probe_refs.py` · `probe_time.py` · `mini/` 합성 14 모양 · `protoA/` 프로토타입 A · `out1/`·`outA/`·`out-names/`). 저장소 파일은 고치지 않았다.

## 0 요약
- **원인은 분류다. 검색은 제대로 한다.** plan 은 `login_view.py:18` 의 import 줄을 점 경로 grep 으로 **찾는다**. 그러나 소비자로 받는 정규식 `CONSUMER_LINE` 은 `{% include|extends %}` 만 받고, 로드 줄(`LOAD_LINE`)도 아니면 그 줄은 어느 목록에도 들어가지 않는다(else 갈래 없음 · 조용히 탈락). 뿌리는 설계 v5 §3-3 이 소비자를 «템플릿 include·extends» 로만 정의한 것 — 구현은 설계를 그대로 따랐다.
- **재현 [실측]:** 레인 사본에서 HEAD 도구로 다시 돌려 레인 plan.md 와 같음(소비자 0). Python 모양의 소비 9가지가 모두 탈락.
- **결과:** 소비자 목록을 쓰는 곳은 도구 밖 둘 — Phase 2 «영향 화면 수정 전 렌더 보존»·G2 전후 대조, R2 리뷰어 입력. 목록이 빠지면 그 화면은 수정 전 렌더도 전후 대조도 없고, plan 은 이를 «- 없음» 이라는 긍정 단언으로 적는다 → **fail-open**.
- **규모 [실측]:** `web/employee_choice` 단위면 6개 영역 VM import 가 전부 탈락해 소비자 0. 첫 리허설 R8-WR(`step8-rehearsal.md:72`)에 이어 두 번째 관찰.
- **core:** plan 에 소비자 개념 자체가 없음(설계 v3 B-M4(a) 보류) → 거짓 «없음» 약점 없음.
- **`plan --names` 120초 초과:** 같은 `_refs` 경로 — git grep 108회 개별 실행 + `--names` 가 plan 전체 재계산.
- **판정:** major · 배포 전 수리 권장(권장안 A = 수 줄 + 픽스처).

## 1 코드 경로 (HEAD `a1d97bc3`)
1. `dddjango-web/scripts/refactor_audit.py:685-696`: 범위 파일마다 `_refs(project, f)` → 적중 줄 중 범위 밖 `web/` 줄만 분류.
2. `_refs`(`:620-626`) → `tail_of`(`src/debt.py:470`) 꼬리 둘: 경로 꼬리 `home/home/view_model/home_view_model.py`(-F) · 점 경로 `web.home.home.view_model.home_view_model`(-F -w) → `reference_lines`(`src/debt.py:477-`) 가 `git grep --untracked` · pathspec `REF_PATHSPEC`(`debt.py:46`: `web` + 저장소 전역 `*.py/*.html/*.css/*.js`).
3. 분류: `:693` `CONSUMER_LINE`(`:154` `\{%\s*(?:include|extends)\b`) → `consumers` · `:695` `LOAD_LINE`(`:153`) → `line_edits` (가) · **둘 다 아니면 else 없음 → 버림**(web/ 밖 적중 `:689-690` → `outside_refs` 와 달리 어디에도 안 남음).
4. 출력 `:824`: 목록이 비면 `["- 없음"]`.
5. 설계 근원: `workspace/eval/web-refactor-entry/design-v5.md:128`(§3-3) · 픽스처 A6(`fixtures_refactor_audit.sh:115`)은 include 한 경우만 · Python 소비 음성 대조 없음.

## 2 재현
- 방법 [실측]: 레인 사본 복제 → `home_view_model.py` 를 HEAD 로 되돌려 plan 시점 재현 → HEAD 도구 `plan web/home` → 레인 plan.md 와 같음(소비자 0).
- 탐침 [실측]:

| 범위 파일(꼬리) | 범위 밖 web/ 적중 | 분류 |
|---|---|---|
| `home/__init__.py`(`web.home`) | `login_view.py:18` · `web/urls.py:7` | 탈락 · 탈락 |
| `home/home/__init__.py` · `view_model/__init__.py` · `home_view_model.py` | `login_view.py:18` | 탈락(3회) |
| `home/urls.py`(`web.home.urls`) | `web/urls.py:7` | 탈락 |

- `:27`(`HomeViewModel().redirect_authenticated(...)`)은 경로 문자열이 없어 grep 미적중 — 소비자는 파일이 화면 판정 근거라 `:18` 한 줄로 충분.
- 모양별(합성 14 모양) [실측]:

| 모양 | grep | 분류 |
|---|---|---|
| `from web.<단위>… import X` / `import … as m` / `from web.<단위>.<화면> import view_model` | 적중 | **탈락** |
| 함수 안 지역 import / 여러 줄 import(첫 줄) | 적중 | **탈락** |
| 문자열 점 경로 / `importlib.import_module("…")` | 적중 | **탈락** |
| 다른 영역 view 의 `render(…, "home/home/view/home.html")` / 다른 영역의 state import | 적중 | **탈락** |
| `{% include "home/…" %}` | 적중 | 소비자 + 줄 편집(가) |
| `{% extends "home/…" %}` | 적중 | 소비자 |
| 상대 import `from ....home…` / 동적 include `"…"\|add:"…"` / `{% url 'home:home' %}` | 미적중 | — |

## 3 결과 추적
- 도구 안 [실측]: `consumers` 는 `_write_plan`(`:824`) · `PlanData.lists`(`:614-617`) → `--against` 대조(`AGAINST_LISTS` `:155`) · 요약(`:908`)에만. check·check-verdict 의 `Plan`(`:983-`)은 소비자를 읽지 않음 → **편집 허용(`in_scope`)·별도 요청 판정 영향 없음(fail-closed 유지)** · 개명·이동은 `--names` 가 import 줄을 (나)로 잡음. `--against` 는 양쪽 다 소비자가 빠져 «같음».
- 도구 밖(문면): R2 리뷰어 입력(`agents/design-review-web.md:33` · `agents/discipline-reviewer-web.md:38`) · Phase 2 진입 준비(`commands/dddjango-web.md:304` «영향 화면(범위 페이지 · 경계 교차 소비자 · 줄 편집 페이지)의 수정 전 렌더 보존») · `:296` 끝 «경계 교차 소비자 페이지는 G2 영향 화면» · `:308` 시각 대조.
- 이번 레인: 메서드 이름 `redirect_authenticated` 가 로그인과의 관계를 드러내 리뷰어 둘이 M3·M9 로 잡음(`verdict-final.md:7·:13`) → Coordinator 가 `refactor-scope.md:31` 에 «plan.md 경계 교차 소비자 누락분» 기록 · 로그인을 영향 화면에 넣음 → `visual-check.md:7·:29` 로그인 GET 302/200 byte 동일 통과.
- 리뷰어가 못 잡았다면 [추정]: 로그인 화면의 수정 전 렌더 미보존 · G2 전후 대조 제외. 반사실: M4(`home_view_model.py:31·:67` — `:67` 은 `redirect_authenticated` 안)가 ⓐ 였다면 세션 API 실패 때 로그인 GET 응답이 바뀌는데 G2 는 홈만 대조. 기존 테스트도 «인증된 GET → 홈 302» 단언 없음(grep 실측).
- **fail-open: 예** — 누락이 «- 없음» 으로 단언되고 소비자 완전성을 보는 게이트가 없다.
- 규모 [실측]: `web/employee_choice` → 6개 영역 VM(home·chart·consultation·intake·preferences·related_persons) import 전부 탈락 → 소비자 0 · `web/consultation` → `home.html` include 만 잡힘 · 이 저장소 web/ 교차 영역 절대 import 11줄 · 상대 import 0.

## 4 core 대응
- core `cmd_plan`(HEAD `:677-`)은 BC 파일·렌즈·조각·파견만 — 소비자·참조 grep 없음. BC 밖 소비자 grep 은 `design-v3.md:24` B-M4(a) 에서 **보류**(백로그).
- 같은 약점 아님: core 는 소비자에 대해 아무것도 단언하지 않음(거짓 «없음» 없음) · 그물은 G2 기존 테스트 전체 실행. «BC 밖 소비자가 안 보인다»는 같은 뿌리의 공백은 알려진 보류 — 이번 범위 밖.

## 5 plan --names 시간
- 같은 코드 경로 [실측]: `compute_plan` 이 git grep **108회**(범위 파일 13 → 22회 · 정적 파일 43 → 나머지 · `_owners`(`:637`)와 `refs`(`:668`)가 같은 파일을 두 번 grep 해 중복 43회) · 1회 약 1.1초(`--untracked` + 저장소 전역 pathspec 약 7.5k 파일) · `compute_plan` 74·110·123초(부하에 흔들림) · `--names` 는 `cmd_plan` `:889` 에서 plan 전체를 계산한 뒤 `:903` 에서 분기 → 쌍 0 이어도 같은 시간.
- 대조 [실측]: 꼬리 56개를 `-e` 로 묶어 grep 한 번 = 0.84초.

## 6 수리안
| 안 | 내용 | 비용 | 위험 |
|---|---|---|---|
| **A 분류 넓힘** | `:686-696` 에서 범위 밖 `web/` 적중을 모양과 상관없이 소비자로 · 모양 표지(`import`·`템플릿 합성`·`이름 문자열`·`라우트 합산`)는 `_item` note · `_parse_lists` 는 백틱 토큰만 읽어 `--against` 대조 불변 · 설계 v5 §3-3 문구 갱신 · Codex byte 미러 | 코드 약 5줄 + 픽스처 3~4 | `web/urls.py:7` 같은 컨테이너 줄 소음(표지로 «화면 없음» 구분) · 옛 audit 재개(`--against`)는 한 번 «다름» → 새 점검(fail-closed) |
| B A + ast | `web/*.py` Import·ImportFrom 을 상대 level 까지 풀어 범위 모듈과 맞춤 · 파싱 실패 «판정 불가» | 약 40줄 + 픽스처 | 판별이 grep·ast 둘로 · 상대 import 현장 0 이라 지금은 과함 |
| C A + 영향 화면 후보 | 소비자·줄 편집 파일을 화면 폴더로 올려 `## 영향 화면 후보` 절 · `:304` 문면이 이 절을 가리킴 | 약 20줄 + 커맨드 문면·Codex 의미 미러 | 화면 폴더 밖 helper 전이 규칙 필요 · 대신 G2 캡처 집합에서 Coordinator 추론 제거 |
| D(별건 · 같은 함수) | 꼬리 전부를 grep 한 번(-F 한 번 · -w 한 번)으로 묶고 Python 에서 꼬리별 분배(최소안 `_refs` 메모) | 약 20줄 | -w 점 경로 경계를 Python 에서 재현 — W6-T5 `web.a.q`/`web.a.q2` 경계 유지 확인 |

- 프로토타입 A [실측]: 레인 사본 `web/home` → 소비자 `login_view.py:18` · `web/urls.py:7` · plan.md 나머지 같음 · 합성 저장소 Python 모양 9가지 전부 · 기존 `fixtures_refactor_audit.sh` HEAD·프로토 모두 151/151 PASS.
- A 뒤 남는 공백: 상대 import(현장 0) · 동적 include · URL 이름 참조(라우트 불변 전제라 영향 작음).
- **권장: A.** 같은 배치에서 D 를 별 커밋으로. C 는 G2 캡처 누락이 다시 나오면.

시험 사례(A): 1 다른 영역 view `from web.<단위>…view_model… import X` → 소비자(로그인 재현) · 2 `import web.<단위>.… as m` · `from web.<단위>.<화면> import view_model` → 소비자 · 3 함수 안 지역 import · 여러 줄 import 첫 줄 → 소비자 · 4 문자열 점 경로 · `importlib.import_module` → 소비자(표지 «이름 문자열») · 5 다른 영역 `render(…, "<단위>/…html")` → 소비자 · 6 A6 include·extends → 소비자 그대로 · 줄 편집 (가) 그대로 · 7 범위 안 줄 · `web/` 밖(`tests/`) 적중 → 소비자 아님(`outside_refs` 그대로) · 8 표지만 다른 plan.md `--against` → 같음(exit 0) · 9 Python 소비자가 빠진 옛 plan.md `--against` → exit 2 «다름 경계 교차 소비자» · 10 현장 회귀: 레인 사본 `web/home` → `login_view.py:18` 포함 · `web/employee_choice` → VM import 줄 6 · 11 음성 고정: 상대 import 미탐(한계를 픽스처로 명시).
시험 사례(D): 12 묶음 grep 전후 현장 사본 plan.md byte 동일 · 13 `web.a.q` 가 `web.a.q2` 를 잡지 않음 · 14 현장 사본 plan 10초 안.

## 7 판정
- **major.** blocker 아님: 편집 권한 쪽 fail-closed 유지 · 기존 테스트·리뷰어가 부분 그물. minor 아님: G2 동작 보존 증거(수정 전 렌더·전후 대조)의 입력이 조용히 비고 «없음» 으로 단언 · 교차 영역 VM import 는 이 코드베이스의 흔한 모양(employee_choice 6 영역) · 두 레인 연속 재현.
- 배포 전에 고칠 가치: 있다. A 는 수 줄 · 기존 픽스처 회귀 없음(실측). 캠페인에서 employee_choice·client 처럼 많이 import 되는 단위를 돌리면 G2 영향 화면이 통째로 빠진다. D(120초)는 minor 지만 같은 함수라 싸게 함께 닫을 수 있다.
