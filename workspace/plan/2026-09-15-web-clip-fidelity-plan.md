# 계획 — 절단 충실도 수리 A+B (2026-09-15)

설계 정본: `workspace/design/2026-09-15-web-clip-fidelity.md` (v2).
적대 검토: `workspace/eval/web-scroll-clip-fidelity/design-review/{rv-A,rv-B,rv-C,rv-D,verified}.md`.
사용자 범위 확정: «둘다해» — 수리 A + 수리 B 둘 다.

## 0. 불변 제약

- **A8 워크트리는 읽기 전용**([[a8-final-testbed]]) — 플러그인을 고치고 배포한 뒤 A8 이 스스로 잡는지가 최종 시험.
- 작업 트리 그대로 · 사용자 미커밋 변경(`docs/master.html` · `lanes.md`) 보존 · 브랜치 커밋 금지.
- `scripts/`·`assets/` 는 Codex **byte 동일 미러**(`Makefile:96-97` `diff -rq` 가 자동 검출).
  커맨드·에이전트·references 는 **수동 의무**(references 3종은 `cmp -s` byte 미러).
- **새 산출물 없음 · `audit_version` 불변 · `Makefile` 무편집** → 봉인 재발행·재동결 폐기 집합·
  `web_refreeze_contract.py`·`backstop.py` 마커를 **건드리지 않는다**(설계 v2 §4).
- 릴리즈는 `make release-web` 만. 커밋·릴리즈는 사용자 승인 뒤에만.

## T1 — `check_token_disposition.py` 신설 (수리 A · 본 수리)

### 파일
- 신설 `dddjango-web/scripts/check_token_disposition.py`
- 신설 `dddjango-web/scripts/test/fixtures_token_disposition.sh` (글롭 자동 수집 — Makefile 배선 불요)
- 미러 `codex-dddjango-web/skills/dddjango-web/scripts/check_token_disposition.py` (byte 동일)
- 미러 `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_token_disposition.sh` (byte 동일)
  — **`Makefile:96` `diff -rq` 는 `scripts/test/` 까지 재귀한다. 기존 픽스처 23개가 이미 미러돼 있고
  (정본 23 ↔ 미러 23 · 내가 직접 확인), 신규 픽스처를 미러하지 않으면 `make verify` 가 RED 다**(pr-1 B1).

### 계약
```
python check_token_disposition.py --spec-only <design-spec.md> <design-tokens.json> <design-ref 경로>
exit 0 = 발견 0 · 2 = 발견 ≥1(architect 반송 근거) · 1 = 사용법·파싱(미실행 취급 — 통과 아님)
```

**파스 앵커(byte 고정)** — `check_motion_spec.py` 판형 이식:
```
| 축 | 처분 | 토큰 |
```
축 ∈ `colors|typography|spacing|borderRadius|shadows` · 처분 ∈ `채택|기각` · 토큰은 백틱 인용 목록.
**탈출구 대칭 가드**(pr-2 B2 — 선례 `check_motion_spec` 에는 있고 계획 v1 에는 없었다):
- `design-spec.md` 에 «토큰 전수 처분» 계열 절 heading 이 **있는데** 고정 헤더가 없으면 → **FINDING**(판형 위반).
- 절 자체가 없으면 → `[warn] 레거시 산문 판형 — 미검증` + exit 0 (합법 재빌드 비차단).
무조건 warn 탈출은 금지한다 — 그러면 검사가 영구 미발동한다.
*왜 고정 앵커인가*: A8 실명세 9개에 관용 파서를 돌린 결과 **5개가 절 미검출**, 커버리지 0/24/87/100%
로 흩어졌다(판형 3종 공존). 관용 파스는 조용한 미검증을 낳는다.

**검사 3종**
- **T1a 전수성** — `design-tokens.json` 의 dict 절(`colors`·`typography`·`spacing`·`borderRadius`·
  `shadows`) 키 합집합이 풀이다. `풀 − (채택 ∪ 기각)` 이 비지 않으면 발견(미처분).
- **T1b 양방향** — `(채택 ∪ 기각) − 풀` 발견(풀 밖 토큰) · `채택 ∩ 기각` 발견(중복 처분).
- **T1c 기각 정당성** — **기각한 토큰의 값이 동결 시안에 실제로 쓰이면 발견.**
  - 시안 본문 = `design-ref/**/*.html` 의 인라인 `style="…"` 선언 전체.
  - 길이 값(`^-?[\d.]+px$`): `(?<![\d.\w-])값(?![\d\w-])` 로 대조(`2px` 가 `12px` 에 걸리지 않게).
    `rem`/`em` 은 16 배로 환산해 양방향 대조한다.
  - 색 값: `#hex` 는 대소문자 무시 직접 대조, `rgb()/rgba()` 는 `#rrggbb` 로 정규화해 양방향 대조
    (`compare_render_audit.py` 의 색 정규화 판형 재사용). `color-mix()`·gradient 는 **미대조**로 계수한다 —
    A8 색 값 분포는 `#hex 66 · color-mix 39 · 기타 22 · rgb 6 · gradient 4` 로 **43% 가 미대조**이고
    그 사실을 커버리지 줄이 드러내야 한다(pr-2).
  - `var(--토큰)` 직접 인용도 사용으로 본다.
  - **가드 ① 비변별 값 제외**: `0·0px·none·auto·transparent·inherit·initial·1·100%`
    (`--space-0: 0px` 는 `margin: 0` 수백 건에 걸려 발견을 폭발시킨다).
  - **가드 ② 귀속 불가 제외**(pr-2 B1 — v1 최대 결함): 기각 토큰의 값을 **채택된 토큰이 공유**하면
    그 시안 사용을 기각 토큰에 귀속할 수 없다 → 제외. A8 풀에서 채택·기각이 값을 공유하는 경우가
    **13건**(`--radius-sm`=12px ↔ 채택 `--space-5`/`--stack` 등). 이 가드가 없으면 발견 6건 중 5건이 오탐이다.
  - **가드 ③ 화면 범위 한정**: 시안 본문은 `screen-meta.json` 이 지목한 **이번 화면의 dc 만** 읽는다
    (A8 `--radius-xl`=28px 는 범위 밖 `설정.dc.html` 에서만 쓰인다).
  - 복합 값(그림자·폰트 스택 등)은 **미대조**로 계수한다.
  - **커버리지 1줄을 반드시 출력한다**: `기각 N 중 대조 가능 M · 미대조 K` — 미대조를 숨기지 않는다.

**실측 기대값(A8 `20260912-1640-web-related-persons` · 가드 3종 적용 후 · 내가 직접 재현)**

| 검사 | 발견 | 내용 |
|---|---|---|
| T1a 미처분 | **1** | `--safe-top` |
| T1b 중복(채택∩기각) | **2** | `--fw-regular` · `--fw-semibold` |
| T1c 기각 정당성 | **4** | **`--space-1`=2px ← 이번 결함** · `--fs-label`=14px · `--space-10`=40px · `--space-13`=80px |
| | **합 7** | 기각 132 · 대조 59 · 비변별 제외 3 · 귀속 불가 제외 19 · 복합 미대조 51 |

*구현 리뷰(ir-1) 반영으로 기대값이 6 → 7 로 올랐다*: ① 중첩 dict 언랩(A8 typography 50개가 전부
`{"size": …}` 판형이라 **영구 미대조**였다)로 `--fs-label` 이 처음 대조돼 발견 1건 추가 ②
`var(--토큰)` 직접 인용도 사용으로 계수 ③ 처분 표 파서를 **연속 블록으로 한정**(그 전에는 문서 끝까지
모든 `|` 줄을 먹어 하류 표에서 «판형 위반» 잡음 58줄이 나왔고 이번 결함이 그 아래 묻혔다).

→ 이 발견은 **판단 자료가 아니라 반송 근거**다: «기각 사유가 사실인가»를 architect 가 다시 답해야 한다.
  A8 의 실제 사유는 «미사용 space 단계»였고 그것이 거짓이었다.
  잔여 2건(`--space-10`·`--space-13`)은 디자인 캔버스 래퍼 등 **프레임 밖** 사용이라 기각이 옳다 —
  검사는 «기각이 틀렸다»가 아니라 «사유를 사실로 대라»를 요구하므로 이는 정상 동작이다.
  **신호/잡음 1:2 를 수용한다**(G1 에서 3줄을 확인하는 비용).

**발동 조건**(pr-1 B3): `has_design_tokens` ∧ `design-ref` 존재일 때만 돈다. 아니면 «토큰 처분 점검:
해당 없음(시안 없음)» 1줄. **exit 1 은 백스톱과 동일하게 미실행 취급**(통과 간주 금지 — stderr 를 배너 사유로).

### 픽스처(negative ↔ positive-control 짝 · `fixtures_audit.sh` 판형)
- `TD1` 정상(전수·기각 정당) → exit 0
- `TD2` 미처분 토큰 1개 → exit 2 + 토큰명 발화
- `TD3` 풀 밖 토큰 → exit 2 · `TD4` 채택∩기각 중복 → exit 2
- `TD5` 기각한 `2px` 가 시안 `padding: 2px 2px 4px` 에 쓰임 → exit 2 **(이번 결함의 회귀)**
- `TD6` 기각한 `12px` 가 시안에 없음 → exit 0 (오탐 없음 대조)
- `TD7` `--space-0: 0px` 기각 + 시안 `margin: 0` 다수 → exit 0 (비변별 값 제외 대조)
- `TD8` `0.125rem` ↔ `2px` 환산 대조 → exit 2
- `TD9` 헤더 미검출(레거시 산문) → `[warn]` + exit 0
- `TD10` 사용법 오류·JSON 파싱 실패 → exit 1
- `DET` 결정론 — 같은 입력 2회 byte 동일 출력

## T2 — `check_clip_clearance.py` 신설 (수리 B)

### 파일
- 신설 `dddjango-web/scripts/check_clip_clearance.py` + Codex byte 미러
- 신설 `dddjango-web/scripts/test/fixtures_clip_clearance.sh` + **Codex byte 미러**(pr-1 B1)

### 계약
```
python check_clip_clearance.py <web 루트>
exit 0 = 발견 0 · 2 = 발견 ≥1(판단 자료·비차단) · 1 = 사용법·읽기 실패
```
**브라우저를 쓰지 않는다.** CSS 와 템플릿 텍스트만 읽는다 — rv-A 의 기하 BLOCKER 5·MAJOR 10 은
전부 런타임 기하에 걸린 것이라 이 경로에 해당하지 않는다.

**4단계**
1. **링 확장 수집 — 전역 최대가 아니라 «규칙별»** (pr-2 B3 — v1 최대 결함).
   `:focus`·`:focus-visible`·`:focus-within`·`:checked` 규칙의 바깥 `box-shadow`(첫 토큰이 `inset` 아님).
   - `--focus-ring` 하드코딩 금지(rv-A) — `var()` 는 `:root` 선언에서 해소(깊이 6).
   - 색 함수·`#hex` 를 **먼저 제거**한 뒤 순서대로 `offset-x offset-y [blur] [spread]` 를 읽고
     **단위 없는 `0` 도 길이로 받는다**(내 프로토타입이 실제로 여기서 틀려 좌측 확장이 −3px 이 됐다).
   - **판정 확장 = `spread + |offset|` — `blur` 는 제외한다.**
     *왜*: 실제 Chrome 픽셀 측정 결과 `0 0 20px 0` 의 페인트 확장은 **29px**(= spread + 1.45×blur)이라
     `spread+blur/2`(10)도 `spread+blur`(20)도 맞지 않는다 — blur 그림자는 «어디까지가 잘린 것인가»가
     연속적이라 결정적 판정에 부적합하다. blur>0 그림자는 값을 기록해 **인벤토리로만** 낸다.
     이 수리의 대상인 링은 전부 `0 0 0 3px`(blur 0)이라 판정에 영향이 없다.
     (측정 원문: `workspace/eval/web-scroll-clip-fidelity/rule-prevalidation.md` 추가 실측 절.)
   - **전역 최대 금지**: pr-2 가 A8 에서 전역 최대를 취하면 `components.css:793` 의 장식 고도 그림자
     `--shadow-1` 이 섞여 S=[5,5,3,8] 이 되고, **동결 시안이 준 `2px 2px 4px` 도 계획의 양성 대조
     `3px 3px 4px` 도 반송된다**는 것을 측정으로 보였다. 링 12건 중 11건은 3px 다.
     → 확장은 **그 후보에 실제로 적용되는 규칙에서만** 취한다.
2. **클리핑 규칙 수집** — `overflow(-x|-y)\s*:\s*(auto|scroll|hidden|clip)`.
   **`hidden`·`clip` 을 반드시 포함한다**(rv-A BLOCKER 2 — 가장 단단한 클립이다).
   A8 실측 **34건**.
3. **여유 부족 후보 — 축 전파를 반드시 적용한다** (pr-2 B4 — 이 결함의 기전 그 자체).
   CSS 규칙상 한 축이 `visible` 이 아니면 **다른 축도 `auto` 로 계산된다** — pr-2 가 실제 Chrome 에서
   `overflow-y:auto` 만 준 스크롤러의 computed `overflowX = "auto"` 임을 측정했다.
   `overflow-y: auto` 선언만 보고 `축={y}` 로 읽으면 **가로 절단을 통째로 놓치고**, 시안이 준
   가로 2px 의 존재 이유를 설명하지 못한다. → **어느 축이든 비-visible 이면 양축을 검사한다.**
   **심각도 2단**: 여유 0 = «확정» · `0 < 여유 < 확장` = «경미»(시안 자신이 1px 잘린 사례가 실재한다).
   A8 실측 **30건**(계획 v1 의 27 은 오기 — pr-2 재현).
4. **노이즈 절단** — 후보 셀렉터의 클래스명이 나오는 템플릿을 찾고, 그 요소 서브트리에
   링을 지는 요소(`<input>`·`<button>`·`<select>`·`<a href>`·`[tabindex]`·링 보유 컴포넌트 include)가
   있는 것만 **발견**. 나머지는 인벤토리 줄로 남긴다(아바타·텍스트 말줄임·sr-only 입력이 여기로 빠진다).
   - **`{% include %}` 뿐 아니라 `{% extends %}`·`{% block %}` 도 따라간다**(pr-2) — 안 따라가면
     앱 전역 스크롤러 `.app-frame__content`(`base/base.html:22` + `app_shell.css:44` · 패딩 0)가
     조용히 인벤토리로 강등된다.
   - **조인 실패는 «강등» 이 아니라 «조인 실패» 로 명시 출력한다** — 조용한 강등이 미탐 통로다.

**실측 기대값(A8 · 구현 후 실측)**: 링 규칙 **13** · 클리핑 **34** · 발견 **12** · 인벤토리 **20** · 발견에
`related_persons.css :: .rpe-scroll`(서브트리 select·input·pair_choice·checkbox)과
`app_shell.css :: .app-frame__content`(extends 추적 후)가 **둘 다** 올라와야 한다.
알려진 경미 발견: `.conversation-rooms`(top 2px < 3px — 진짜 1px 절단이라 «경미» 등급으로 남긴다) ·
`.chart-major-fortunes__strip`(sticky 좌열 제약 — 인벤토리 사유와 함께).

**발동 조건**: `web/` 트리가 있으면 항상. **exit 1 은 미실행 취급.**

### 픽스처
- `CC1` 정상(패딩 충분) → 0 · `CC2` `.x{overflow-y:auto}` + 패딩 0 + 서브트리 input → 2 **(이번 결함 회귀)**
- `CC3` `overflow:hidden` + 패딩 0 + 서브트리 input → 2 (rv-A B2 회귀)
- `CC4` 패딩 0 이지만 서브트리에 포커스 요소 없음 → 0 (노이즈 절단 대조)
- `CC5` `box-shadow: inset …` 만 있는 포커스 규칙 → 링 아님 → 0
- `CC6` `0 0 0 3px rgba(…,.30)` 파싱 — 좌·우 모두 3px 로 나오는지 (내 프로토타입 버그 회귀)
- `CC7` `color-mix(in srgb,#D0727A 30%,transparent)` 의 `30` 이 길이로 새지 않는지
- `CC8` `blur` 만 있는 그림자 → 확장 `blur/2` · `DET` 결정론

## T3 — 규범 편집 (양 런타임)

| 파일 | 편집 | 근거 |
|---|---|---|
| `commands/dddjango-web.md:168` | «같은 시점 — 모션 처분 표 기계 점검» 옆에 **토큰 처분 기계 점검** 1문장 추가(`--spec-only` · FINDING 은 architect 반송 · [warn] 은 배너 표면화) — `check_motion_spec` 문면과 같은 판형 | rv-B B4 |
| `commands/dddjango-web.md:187` | G2 배너에 `check_clip_clearance.py <web 루트>` 실행 + **배너 1급 의무 표기** + 발견 0 이면 «절단 여유: 발견 0» 1줄 · exit 1 은 미실행 취급 | rv-B B5 |
| `agents/design-architect-web.md:48` | ① 토큰 전수 연결 문장에 **기각 사유의 사실성 의무** — «미사용»을 쓰려면 그 값이 동결 시안에 없어야 한다 ② **byte 고정 표 판형 리터럴 `\| 축 \| 처분 \| 토큰 \|` 을 생산자 프롬프트에 그대로 싣는다** — 모션 판형이 4곳에 리터럴로 실려 있는 선례를 따른다. 안 실으면 architect 가 그 판형을 쓸 이유가 없어 **검사가 상시 warn 으로 영구 미발동**한다(pr-1 B2) | 설계 §0② · pr-1 B2 |
| `agents/design-review-web.md:45` ⓑ | 기각 정당성 리뷰 항목 1구 추가 | rv-B |
| `agents/discipline-reviewer-web.md:61` | **기존 «고정 배치 무력화» 트리거를 확장**: 감사 범위 CSS 에 바깥 `box-shadow` 를 붙이는 포커스/`:checked` 규칙이 grep 히트하면 **조상 사슬 overflow 대조가 의무**이고 여유 부족은 **blocker**. 이미 이 판형·등급이 선 유일한 차단 경로다 | rv-B 부수 발견 |
| `commands/dddjango-web.md:221` | 트리비얼 패스트트랙 공통 절차 ③ 의 `backstop.py` 옆에 `check_clip_clearance.py <타깃 프로젝트 루트>/web` 1개 추가 — 패스트트랙은 «토큰 값 수정»을 포함하므로 padding/overflow 변경이 두 검사 모두 없이 통과하던 구멍이다. 빌드 폴더·브라우저 불요라 패스트트랙 제약에 맞는다 | rv-B 부수 · pr-1 MAJOR |
| `skills/architecture-web/references/final.md:142` | 「크기 전수 연결」에 ① 기각 정당성 ② byte 고정 표 판형 ③ 집행 검사기 이름을 1문장씩 | 설계 §0② |

Codex 미러: `codex-dddjango-web/skills/dddjango-web/SKILL.md`(의미 미러) ·
`agents` 대응 SKILL · `skills/architecture-web/references/final.md`(**byte 동일** — `cmp -s`).

## T4 — 문서·검증

- `docs/DEVELOPMENT.md` §1 파일 지도에 새 스크립트 2종 행 추가.
- **빌드 스펙 정본 `workspace/design/2026-08-23-web-presentation-layer-spec.md` 의 D 결정 대장에
  이번 결정 행을 추가한다**(pr-1 MAJOR — 규범 변경은 그 대장이 정본이다).
- `workspace/design/ontology-adoption-map.html` 에 2026-09-15 타임라인 행 추가([[always-update-adoption-map]]).
- `bash dddjango-web/scripts/test/run_fixtures.sh` — 신규 2종 포함 전건 green.
- `make verify` 6/6 green.

## 5. 행동 시험 (구현 리뷰 전)

- **B-1** `cp -R` 로 A8 빌드를 scratchpad 에 복사하고(**원본 무수정 — 복사 뒤 원본 sha 대조**),
  사본의 `design-spec.md` 토큰 절만 고정 헤더 판형으로 **기계 변환**(채택/기각 이름 목록은 그대로 옮긴다 —
  손으로 고르면 동어반복이다). 그 사본에 `check_token_disposition.py` 를 돌려
  **T1a 1 + T1b 2 + T1c 3 = 발견 6건**과 그 안에 `--space-1` 이 있음을 재현한다.
- **B-2** A8 `web/` 트리(읽기 전용)에 `check_clip_clearance.py` 를 돌려 `.rpe-scroll` 이 발견에 뜨고,
  아바타·말줄임 류가 인벤토리로 빠지는지 확인한다.
- **B-3** `.rpe-scroll` 에 `padding: 3px 3px 4px` 를 넣은 사본으로 돌려 **발견 0** 을 확인한다(양성 대조).

## 6. 순서와 게이트

T1 → T2 → T3 → T4 → 행동 시험 → **독립 구현 리뷰(적대 2인)** → `make verify` →
**사용자 승인** → 커밋 → `make release-web`.

봉인 재발행은 **불요**(`Makefile` 무편집). 릴리즈 뒤 사용자 `/plugin` 갱신 필요.
