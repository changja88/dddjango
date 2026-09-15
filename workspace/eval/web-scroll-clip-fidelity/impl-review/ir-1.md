# 독립 구현 리뷰 1 — 검사기 코드 (2026-09-15)

대상: `dddjango-web/scripts/check_token_disposition.py` · `check_clip_clearance.py` ·
`scripts/test/fixtures_{token_disposition,clip_clearance}.sh`
기준: `workspace/plan/2026-09-15-web-clip-fidelity-plan.md` T1·T2 · 선례 `check_motion_spec.py`
방식: 실입력 재현 · A8 실트리/실빌드 대조 · 변이(mutation) 시험 34건 · 결정론 2회 실행

**BLOCKER 4 · MAJOR 6 · MINOR 6.** 픽스처 32건은 전건 green 이지만 그 green 은
아래 BLOCKER 를 하나도 잡지 못한다.

---

## [BLOCKER] B1 — `make verify` 가 RED 다 (재동결 계약 D1 위반)

### 재현
```
$ cd /Users/hyun/Desktop/dddjango && make verify-web
…
[verify-web] 재동결 계약(유보·잔존·경로 치환 불변식)
[web-refreeze-contract] self-test green
[web-refreeze-contract] D1 dddjango-web/commands/dddjango-web.md:168: 재동결 중 staging을 가리켜야 한다 — <대상 폴더>로 바꾼다 (<산출물 폴더>/design-tokens.json)
[web-refreeze-contract] D1 codex-dddjango-web/skills/dddjango-web/SKILL.md:191: 재동결 중 staging을 가리켜야 한다 — <대상 폴더>로 바꾼다 (<산출물 폴더>/design-tokens.json)
[web-refreeze-contract] 위반 2건
make: *** [verify-web] Error 1
```

### 관찰 vs 기대
- 기대: 계획 T4 «`make verify` 6/6 green».
- 관찰: `verify-web` 이 exit 1. 이번 변경이 원인임을 확인했다 —
  `git stash push -- dddjango-web/commands/dddjango-web.md codex-…/SKILL.md` 후
  `python3 workspace/tools/web_refreeze_contract.py` → `계약 green (A·B·C·D1~D4)` (RC=0),
  `git stash pop` 후 → 위반 2건 (RC=1). (원복 완료 — `git status` 가 착수 시점과 동일)

### 원인
새 호출줄이 `<산출물 폴더>/design-tokens.json`·`<산출물 폴더>/design-ref`·
`<산출물 폴더>/screen-meta.json` 을 쓴다. `workspace/tools/web_refreeze_contract.py:50-52`
의 `DISCARD_NAMES` 에 **셋 다** 들어 있고(`design-ref`·`design-tokens.json`·`screen-meta.json`),
`check_d1` 은 이들 폐기·교체 대상이 `<대상 폴더>`(재동결 staging)를 가리킬 것을 요구한다.
같은 줄의 `check_motion_spec` 인자 `<산출물 폴더>/motion-notes.md` 는
`PRESERVED_NAMES` 라 합법이다 — 새 줄만 위반이다.

### 수정 방향
양 런타임에서 세 자리표시자를 `<대상 폴더>` 로 바꾼다(`<설계 명세>` 는 그대로):
```
check_token_disposition.py --spec-only <설계 명세> <대상 폴더>/design-tokens.json <대상 폴더>/design-ref --screen-meta <대상 폴더>/screen-meta.json
```
`_placeholder_issues` 는 줄당 첫 히트만 보고하므로 셋 중 하나만 고치면 RED 가 남는다.
고친 뒤 `python3 workspace/tools/web_refreeze_contract.py` 로 green 을 확인한다.

---

## [BLOCKER] B2 — 처분 표 파서가 문서 끝까지 모든 `|` 줄을 먹는다 → 실명세에서 발견 6 이 발견 64 가 된다

### 재현 입력 (실제 파일)
```markdown
# 명세

## 9. 토큰 전수 처분

| 축 | 처분 | 토큰 |
|---|---|---|
| colors | 채택 | `--accent`, `--ink` |
| typography | 채택 | `--fs-body` |
| spacing | 채택 | `--space-2`, `--gutter` |
| spacing | 기각 | `--space-1`, `--space-0` |
| borderRadius | 기각 | `--radius-sm` |
| shadows | 채택 | `--shadow-1` |

## 10. 시안 대응 · 시각 연결표

| case_id | 상태 | 캡처(정본) | 시각 근거 |
|---|---|---|---|
| related/list | 목록(4명) | list.png | render-audit 실측 |

## 11. 명세 이탈 표

| # | 이탈 | 사유 |
|---|---|---|
| 1 | scrim 색 | 시안 근사 |
```

### 관찰 vs 기대
기대: 처분이 완전하므로 발견 0. 관찰:
```
[FINDING] 판형 위반 — 셀 4개(헤더 3개): | case_id | 상태 | 캡처(정본) | 시각 근거 |
[FINDING] 판형 위반 — 셀 4개(헤더 3개): | related/list | 목록(4명) | list.png | render-audit 실측 |
[FINDING] 판형 위반 — 축 이름 «#» 은 colors|typography|spacing|borderRadius|shadows 가 아니다
[FINDING] 판형 위반 — 축 이름 «1» 은 colors|typography|spacing|borderRadius|shadows 가 아니다
[token-disposition] 발견 5건   (exit 2)
```
칼럼 수가 같은 표(§11)도 «축 이름» 위반으로 샌다.

### 실명세 규모 (계획 §5 B-1 재현)
A8 `20260912-1640-web-related-persons` 명세 사본에서 §9.1 산문을 **기계 변환**만 해
고정 표로 바꾸고 돌렸다(A8 원본 무수정 — 사본 작업):
- 표 뒤에 남은 마크다운 표 행 62개 → **발견 64건**(그중 58건이 «판형 위반» 잡음).
- 같은 사본에서 §9.2 이후를 잘라내고 재실행 → **발견 6건**, 내용이 계획의 실측 기대값과 정확히 일치:
  `T1a --safe-top` / `T1b --fw-regular`·`--fw-semibold` /
  `T1c --space-1=2px`·`--space-10=40px`·`--space-13=80px`.
→ 계획이 «신호/잡음 1:2 수용»이라고 한 자리에서 실제로는 **6:58** 이 나온다.
architect 는 이번 결함(`--space-1`)을 잡음 58줄 아래에서 찾아야 한다.

### 원인
`check_token_disposition.py:108-130` — 헤더를 만나면 `found = True` 로 두고
루프 **끝까지** `stripped.startswith("|")` 인 모든 줄을 행으로 해석한다. 표 종료 조건이 없다.
선례 `check_motion_spec.py:98-110` 의 `parse_tables` 는 헤더 직후
`while i < len(lines) and lines[i].lstrip().startswith("|")` 로 **연속 블록만** 먹고
비-`|` 줄에서 멈춘다. 계획이 «`check_motion_spec.py` 판형 이식»이라 한 바로 그 부분이 빠졌다.

### 수정 방향
`parse_tables` 의 루프 구조를 그대로 이식한다 — 헤더 앵커 → 구분 행 1줄 건너뜀 →
연속 `|` 블록만 소비 → 블록 끝나면 다시 헤더 탐색(복수 표는 이어 붙임, 선례와 동일).
픽스처에 «표 뒤에 다른 표가 오는 명세 → 발견 0» 케이스(TD13)를 추가한다.

---

## [BLOCKER] B3 — 셀렉터 콤마 목록·`:is()` 목록에서 마지막 하나만 남는다 → 링이 조용히 증발(미탐)

### 재현 입력 — A8 `settings.css:423-425` 과 같은 판형
`web/static/css/app.css`
```css
.rowlink:focus-visible,
.navbtn:focus-visible {
  box-shadow: 0 0 0 3px rgba(208,114,122,.30);
}
.scroll { overflow-y: auto; }
```
`web/page/page.html`
```html
<div class="scroll"><a class="rowlink" href="/x">행</a></div>
```

### 관찰 vs 기대
기대: `.scroll` 이 `.rowlink` 의 3px 링을 자르므로 **발견**. 관찰:
```
[clip-clearance] 링 규칙 1 · 클리핑 규칙 1 · 템플릿 1 · 링 클래스 1
[inventory] app.css :: .scroll — 링 보유 요소 없음(자손 범위)
[clip-clearance] 발견 0건 · 인벤토리 1건
```
같은 CSS 로 `.navbtn`(목록 **마지막** 멤버)을 넣으면 정상적으로 발견이 난다 —
즉 마지막 멤버만 살아남는다. 계획이 «조용한 강등은 미탐 통로»라며 금지한 그 형태다.

동형 2건:
- `:is(.abtn, .bbtn):focus-visible` (A8 `conversation.css:212`·`:896` 판형) → `.abtn` 소실, 발견 0.
- 클리핑 셀렉터 `.scrollA,\n.scrollB { overflow-y:auto }` → `target` 이 `scrollB` 하나뿐이라
  `[inventory] … 조인 실패(템플릿에서 «scrollB» 을 못 찾음)` 로 빠지고 실제 컨테이너 `.scrollA` 는
  **한 번도 검사되지 않는다**.

### 원인
`check_clip_clearance.py:117-122`
```python
def last_compound(selector: str) -> str:
    part = re.split(r"[>+~]|\s+", selector.strip())
    return part[-1] if part else selector.strip()
```
콤마를 조합자로 보지 않는다. 정규화된 셀렉터 전체에 `last_compound` 를 한 번 적용하므로
셀렉터 목록의 앞 멤버가 전부 버려진다. `:is(…, …)` 안의 공백도 여기서 쪼개진다.
호출부 3곳(`rings` 수집 `:301`, 클립 `target` 선택 `:309`, 적용 판정 `:322`)이 전부 이 함수를 탄다.
A8 에서 이 미탐이 드러나지 않은 이유는 `base.css:88` 의 클래스 없는 전역 `:focus-visible`(3px)이
`global_ring` 으로 같은 값을 덮어주기 때문이다 — 전역 링이 없는 프로젝트에서는 전손이다.

### 수정 방향
셀렉터를 **먼저 콤마(괄호 깊이 0)로 쪼개** 멤버마다 독립 규칙으로 취급한다
(`split_top` 이 이미 그 일을 한다 — 재사용). 멤버마다 `last_compound` 를 돌리고,
`:is(…)`/`:where(…)` 안쪽도 같은 방식으로 펴서 클래스를 모은다.
클립 쪽은 `target` 하나가 아니라 **멤버별로** 조인·판정한다.
픽스처: 콤마 목록 링(앞 멤버) · `:is()` 목록 · 콤마 목록 클리핑 3건을 추가한다.

---

## [BLOCKER] B4 — 패딩을 «같은 규칙 본문의 물리 단축/롱핸드»에서만 읽는다 → 멀쩡한 빌드를 «확정» 으로 반송

### 재현 입력 5종 (전부 링 3px · `.scroll` 이 컨테이너 · 자손에 `<input>`)
```css
/* X1 — 패딩이 다른 규칙에 (가장 흔하다) */
.scroll { padding: 16px; }
.scroll { overflow-y: auto; }

/* X2 — 패딩은 기본 규칙, overflow 는 @media */
.scroll { padding: 16px; }
@media (max-width: 480px) { .scroll { overflow-y: auto; } }

/* X3 — 논리 속성 */
.scroll { overflow-y: auto; padding-inline: 8px; padding-block: 8px; }

/* X4 — !important */
.scroll { overflow-y: auto; padding: 8px !important; }

/* X5 — calc() */
.scroll { overflow-y: auto; padding: calc(4px + 4px); }
```

### 관찰 vs 기대
기대: 5건 모두 여유 8~16px ≥ 확장 3px → **발견 0**. 관찰: **5건 모두** 동일하게
```
[FINDING] app.css :: .scroll (overflow auto) — top 여유 0px < 확장 3px [확정] · right … · bottom … · left …
```
즉 실재하는 패딩을 «0px» 이라고 단언하고 최고 등급 «확정» 을 붙인다.

### 원인
- `padding_of(body, …)` 는 **그 규칙 본문**만 본다(`:308` 에서 `clips` 원소의 `pad` 를 그대로 씀).
  같은 셀렉터의 다른 규칙·@media 오버라이드는 합쳐지지 않는다. 미선언은
  `have = 0.0 if have is None else have`(`:331-332`)로 **0 으로 단정**된다.
- `PADDING_RE = r"(?<![-\w])padding(-(?:top|right|bottom|left))?\s*:\s*([^;]+)"` —
  `padding-inline`·`padding-block`(-start/-end 포함) 미지원.
- `padding_of:157-160` — 값 조각 중 하나라도 `px()` 가 None 이면 **선언 전체를 버린다**.
  `!important`·`calc(…)` 가 여기 걸린다.

### 파급
`dddjango-web/agents/discipline-reviewer-web.md:62` 는 이번 변경으로
«패딩이 링 확장(spread + |offset|)보다 작으면 **blocker**» 를 규범화했다.
위 5형태는 전부 정상 CSS 이므로, 이 검사기는 정상 빌드에 blocker 를 만들어 준다.

### 수정 방향
1. 셀렉터 단위로 패딩을 **누적 병합**한다 — 규칙 순회에서 (정규화 셀렉터 → 축별 패딩) 맵을
   뒤 규칙이 덮도록 쌓고, 판정 때 그 맵을 쓴다(선언 순서 = 파일 정렬 순서라 결정적이다).
2. `padding-inline`/`padding-block`(및 `-start`/`-end`)을 좌우/상하로 매핑한다.
3. `!important` 를 값에서 떼고, 파스 불가 값(`calc()`·`var()` 미해소)은 **0 이 아니라 «미상»** 으로
   두고 그 후보를 인벤토리(사유: 패딩 미상)로 내린다 — 조용한 0 단정을 없앤다.
4. 픽스처: X1~X5 를 그대로 negative-control(발견 0)로 넣는다.

---

## [MAJOR] M1 — `var(--토큰)` 인용을 사용으로 세지 않는다(계약 T1c 명문) · 게다가 «대조» 로 계수한다

재현: 기각 `--space-1: 2px`, 시안 `<div style="padding: var(--space-1)"></div>`
```
[token-disposition] 기각 정당성 커버리지 — 판정 1 중 대조 1 · 비변별 제외 0 · 귀속 불가 제외 0 · 복합 미대조 0
[token-disposition] 발견 0건
```
기대: 계획 T1c «`var(--토큰)` 직접 인용도 사용으로 본다» → 발견 1.
원인: `body_index:233` 의 토큰 정규식이 `#hex|rgba?()|길이` 뿐이고
`used_in_design` 도 값만 본다 — `var(--…)` 경로가 코드에 아예 없다.
더 나쁜 것은 «복합 미대조» 가 아니라 **«대조 1»** 로 세어서 커버리지 줄이 미탐을 감춘다는 점이다.
수정: `body_index` 에 `var\(\s*(--[\w-]+)` 를 추가해 인용 토큰 집합을 만들고
`used_in_design` 이 이름 일치도 사용으로 판정한다.

## [MAJOR] M2 — «blur>0 은 판정 제외» 라고 출력하면서 실제로는 판정에 쓴다

재현:
```css
.cb__input:checked + .cb__box { box-shadow: 0 8px 16px rgba(31,28,24,.06); }
.scroll { overflow: hidden; }
```
```
[clip-clearance] blur>0 그림자 1건은 판정 제외(인벤토리): app.css :: .cb__input:checked + .cb__box
[FINDING] app.css :: .scroll (overflow hidden) — bottom 여유 0px < 확장 8px [확정]
```
바로 다음 줄에서 그 그림자로 발견을 낸다. 계획 T2①은 «blur>0 그림자는 값을 기록해
**인벤토리로만** 낸다» 이고 모듈 docstring 도 같은 말을 한다.
원인: `:286-290` — `worst_blur > 0` 이면 `blurred` 에 기록만 하고,
`if not any(v > 0 for v in best.values())` 로 **확장이 전부 0 일 때만**(순수 blur) 판정에서 뺀다.
오프셋/스프레드가 있으면 그대로 `rings` 에 들어간다.
A8 실트리 확인: `components.css :: .checkbox__input:checked + .checkbox__box`
(`--shadow-1 = 0 1px 2px …, 0 3px 10px …`)가 `blur=10.0 · ext bottom 3.0 · 판정사용=True` 다 —
계획이 «장식 고도 그림자가 임계를 지배하면 안 된다»고 못 박은 바로 그 규칙이 판정에 들어 있다.
A8 에서는 전역 링도 3px 이라 우연히 가려졌을 뿐이다.
수정: `blur > 0` 이면 `rings` 에 넣지 말고 `blurred` 인벤토리로만 보낸다(출력 문면과 일치시킨다).
픽스처: 위 입력(오프셋 있는 blur 그림자 → 발견 0)을 CC8b 로 추가한다.

## [MAJOR] M3 — 링 귀속이 «문자열 포함» 이라 남의 클래스·본문 글자에 붙는다

재현 ①
```css
.btn:focus-visible { box-shadow: 0 0 0 9px red; }
.avatar { overflow: hidden; }
```
```html
<div class="avatar"><span class="btn-group-label">글자</span></div>
```
→ `[FINDING] .avatar … 확장 9px [확정]`. `.btn-group-label` 은 `.btn` 이 아니다.

재현 ② `<div class="avatar"><p>이 field 는 그냥 글자다</p></div>` + `.field:focus-within` 링
→ 본문 텍스트 «field» 에 걸려 발견.

A8 실증: `[FINDING] conversation.css :: [data-conversation-mount] .conversation-room-row__portrait`
— 아바타 원판이다. 자손에 `class="conversation-room-row__name"` 이 있어
링 클래스 `conversation-room-row` 가 **접두 부분문자열**로 걸렸다. 계획이 «아바타는 인벤토리로
빠진다»고 한 항목이 발견으로 올라온다.
원인: `:321-322` `if any(c in blob for c in CLASS_RE.findall(last_compound(sel)))` — 경계 없는 `in`.
수정: `blob` 에서 `class="…"` 속성값만 뽑아 토큰 집합으로 만들고 **정확 일치**로 판정한다
(`element_span` 이 이미 쓰는 `(?<![\w-])…(?![\w-])` 판형을 재사용).

## [MAJOR] M4 — `--screen-meta` 를 무조건 넘겨 실제 빌드 1/9 가 exit 1(미실행)로 떨어진다

Coordinator(`commands/dddjango-web.md:168`)는 `has_design_tokens ∧ design-ref 존재` 면
`--screen-meta <…>/screen-meta.json` 을 **항상** 붙인다. A8 실빌드 9개 조사:
`20260905-2018-web-auth-screens` 는 `tokens=T ref=T screenmeta=(없음)`.
표가 있는 명세 + screen-meta 부재로 재현하면
```
[token-disposition] 파일 없음: …/screen-meta.json      (EXIT=1)
```
exit 1 = 미실행이라 통과로 새지는 않지만, 그 빌드에서는 검사가 **영구 미발동**한다.
(현재 그 빌드가 exit 0 으로 보이는 건 산문 판형이라 `design_bodies` 전에 반환하기 때문이다 —
표 판형으로 바뀌는 순간 exit 1 이 된다.)
수정: `--screen-meta` 대상 파일이 없으면 `die` 대신 `[warn] screen-meta 없음 — 전 파일로 대조` 로
낮춘다(이미 sha 불일치 때 같은 완화를 한다). 또는 Coordinator 가 존재할 때만 붙이도록 조건화한다.

## [MAJOR] M5 — typography 토큰이 중첩 dict 라 전 축이 영구 미대조 + 메시지에 파이썬 repr

`extract_design.py:47` `typography: Dict[str, Dict[str, str]]` — 값이 `{"size": "14px"}` 다.
`load_pool:148` 은 `pool[name] = str(raw).strip()` 이라 `"{'size': '14px'}"` 가 된다.
```
[FINDING] T1a 미처분 — 채택·기각 어느 쪽에도 없다: --fs-body = {'size': '14px'}
```
A8 실측: 기각 134 중 typography 30 건이 전부 «복합 미대조» 로 빠지고,
그중 **8건**(`--fs-body`·`--fs-display-1`·`--fs-display-2`·`--fs-label`·`--fs-micro`·
`--fs-title-1`·`--ls-display`·`--ls-wide`)은 중첩만 풀면 길이로 대조 가능한 값이다.
즉 «기각한 글자 크기를 시안이 쓴다» 는 이번 결함과 **같은 종류**를 typography 축에서 통째로 놓친다.
수정: `load_pool` 에서 값이 dict 면 `size`(또는 유일 값)를 꺼내 문자열로 쓴다.

## [MAJOR] M6 — 픽스처 검출력 결손: 변이 34건 중 9건이 살아남는다

정본을 건드리지 않고 `scripts/` 사본에 변이를 넣고 해당 픽스처를 돌렸다
(사본: scratchpad · 정본 `git status` 무변동).

| 변이 | 결과 | 의미 |
|---|---|---|
| N8 `global_ring` 경로 삭제 | **SURVIVED** | 클래스 없는 전역 `:focus-visible` 경로 — A8 발견 13건 중 12건을 만드는 **지배 경로**가 무시험 |
| N9 `FOCUSABLE_RE` 가드 삭제 | **SURVIVED** | 같은 경로. 픽스처의 링은 전부 클래스 보유라 이 분기를 한 번도 타지 않는다 |
| N11 심각도 2단 폐기(항상 「확정」) | **SURVIVED** | 계획 T2③ 의 «확정/경미» 를 검증하는 단언이 없다(CC6 은 등급 문자열을 안 본다) |
| N13 「조인 실패」 를 조용한 강등으로 | **SURVIVED** | 계획이 «조용한 강등은 미탐 통로»라 명시한 항목이 무시험 |
| N16 `COLORFN_RE` 제거 | **SURVIVED** | **CC7 이 이걸 잡으라고 있는데 못 잡는다** — 아래 상술 |
| M2/M16 `used_in_design` 의 TRIVIAL 분기 삭제 | **SURVIVED** | 그 분기가 도달 불가(본 루프가 먼저 거른다) = 죽은 코드 |
| M10 색 정규화(`rgb()`→hex) 삭제 | **SURVIVED** | **기각된 «색» 토큰을 판정하는 픽스처가 0건** — T1c 색 경로 전체가 무시험 |
| M17 3자리 hex 확장 삭제 | **SURVIVED** | 위와 같은 구멍 |
| N19 findings/inventory 정렬 제거 | SURVIVED | 실해는 없음(순회가 이미 결정적) — 참고만 |

나머지 25건(N2·N3·N4·N5·N6·N7·N14·N15·N17·N18·M1·M2b·M3·M5·M6·M7·M8·M9·M13·M14·M18·M19 등)은
정상 DETECTED — 픽스처의 뼈대는 건강하다.

**CC7 이 왜 못 잡나**: `0 0 0 3px color-mix(in srgb,#D0727A 30%,transparent)` 에서
`COLORFN_RE` 를 지워도 `HEX_RE` 가 `#D0727A` 를 지우고, 남은 숫자열의 **앞 4개만** 쓰는
`(list(nums) + [0.0]*4)[:4]`(`:111`) 때문에 `30` 이 잘려 나간다. 통과가 우연이다.
변별력 있는 입력은 **색이 먼저 오는** 유효 CSS 다:
```css
.field:focus-within { box-shadow: rgba(208,114,122,.30) 0 0 0 3px; }
```
현행 코드는 옳게 3px 로 읽지만, `COLORFN_RE` 를 지우면
`확장 208.3px · 114.3px` 이 나온다. CC7 의 입력을 이 형태로 바꿔야 한다.

수정 방향(픽스처): ① 클래스 없는 `:focus-visible` 전역 링 + 포커스 요소 유무 2케이스
② 등급 문자열 `[확정]`/`[경미]` 단언 ③ 조인 실패 메시지 단언
④ CC7 을 색-선행 그림자로 교체 ⑤ 기각된 **색** 토큰 2케이스(`rgb()`↔`#hex` 양방향, 3자리 hex).

---

## [MINOR] m1 — 절단 풀을 5개 축이 아니라 «모든 dict 절» 에서 만든다

계획 T1a: «`design-tokens.json` 의 dict 절(colors·typography·spacing·borderRadius·shadows)».
`load_pool:145-148` 은 `AXES` 를 쓰지 않고 top-level dict 전부를 넣는다. `AXES` 는 축 칼럼
검증에만 쓰인다. 재현 — tokens.json 에 `"meta":{"generator":"extract_design","version":"2"}` 추가:
```
[FINDING] T1a 미처분 — … : generator = extract_design
[FINDING] T1a 미처분 — … : version = 2
```
현행 `extract_design.py` 산출은 6키 고정이라 잠복이지만 계약 위반이다.
수정: `for section in AXES:` 로 좁히고, 그 밖의 dict 절은 warn 1줄로 고지.

## [MINOR] m2 — 귀속 불가 가드가 «원문 문자열» 비교라 단위·표기가 다르면 안 먹는다

`adopted_values = {pool[n].strip().lower() …}` (`:289`) 후 `value.strip().lower() in adopted_values`.
재현: 채택 `--space-2: 0.125rem`, 기각 `--space-1: 2px`, 시안 `padding: 2px`
→ 귀속 불가 제외 0 · `[FINDING] T1c … --space-1 = 2px` (오탐).
시안 대조는 px 정규화·색 정규화를 하는데 가드만 원문 비교라 비대칭이다.
수정: `px_of`/`norm_color` 로 정규화한 값 집합으로 비교(둘 다 None 이면 원문 비교로 폴백).

## [MINOR] m3 — 시안 인라인 style 수집 정규식

`INLINE_STYLE_RE = r'style\s*=\s*"([^"]*)"'`.
① 작은따옴표 `style='padding: 2px'` 는 수집되지 않는다(재현: 발견 0).
② 왼쪽 경계가 없어 `data-style="…"`·`foo-style="…"` 도 시안 본문으로 빨아들인다.
수정: `(?<![\w-])style\s*=\s*("([^"]*)"|'([^']*)')`.

## [MINOR] m4 — 죽은 코드·중복 읽기

- `check_clip_clearance.py`: `template_graph` 가 만드는 `includes` 그래프가 **한 번도 읽히지 않는다**
  (`expand` 는 `span` 에서 `INCLUDE_RE` 를 다시 찾고 `by_name` 을 **파일명만으로** 되돈다).
  그 결과 `resolve_ref` 의 «경로 접미사 일치» 정밀 해소가 사장되고,
  같은 이름 템플릿이 둘이면 `expand` 가 엉뚱한 쪽을 편다. `includes` 파라미터도 미사용.
- `check_token_disposition.py`: `used_in_design(value, body, …)` 의 `body` 인자 미사용 ·
  같은 함수의 `if v.lower() in TRIVIAL` 분기는 본 루프(`:294-296`)가 먼저 걸러 도달 불가
  (변이 M16 이 살아남아 확인) · `parse_disposition` 이 돌려준 `has_section` 을 `:273` 에서 버리고
  `:264` 에서 명세 파일을 **두 번째로 읽어** 재계산한다. 그 재계산은 `SECTION_RE.search` 라
  **코드 펜스를 건너뛰지 않아** 파서와 규칙이 다르다(펜스 안 예시 heading 만 있으면 false FINDING).
  `:181` 은 자리표시자 없는 f-string.

## [MINOR] m5 — 판형 엄격도와 생산자 프롬프트의 간극

- `| **colors** | 채택 | … |` → `[FINDING] 판형 위반 — 축 이름 «**colors**»`.
- `| colors | 기각 | (없음) |` → `[FINDING] 판형 위반 — 토큰 칸이 비었거나 백틱 인용이 없다`.
`agents/design-architect-web.md:48` 은 헤더 리터럴·축/처분 어휘·«백틱 인용 목록» 만 싣고,
**강조 금지**나 **기각 0건 축의 표기**를 말하지 않는다. architect 가 자연스럽게 쓸 표기가 red 가 된다.
수정: 파서에서 셀의 `**`/`__` 를 벗기고, 토큰 0건은 행 자체를 생략하도록 프롬프트에 1구 추가.

## [MINOR] m6 — 자잘한 한계

- `element_span` 은 템플릿당 **첫 등장 1개**만 본다 — 같은 클래스가 여러 번 나오면 뒤쪽은 미검사.
- `open_end = text.find(">", m.end())` 는 속성값 안의 `>`(`title="a > b"`)에서 어긋난다.
- `design_bodies` 가 `die` 하면 이미 모은 T1a/T1b findings 가 출력 없이 사라진다(exit 1).
- `.app-frame__content` 처럼 같은 요소가 규칙 3개에 걸리면 발견도 3줄로 중복된다(A8 실측).

---

## 확인했고 결함이 아닌 것

- **exit 규율**: `die→1`, `main→0/2`. `compare_render_audit.py:35`·`check_motion_spec.py:25` 와
  문면·의미가 동일. 미실행(1)이 통과(0)로 새는 경로는 찾지 못했다.
- **결정론**: A8 실트리·실빌드로 각 2회 실행 → `cmp` byte 동일(clip·token 모두).
  파일 순회 `sorted(rglob)`, 출력 전 `sorted()`, set 은 멤버십 전용.
- **인코딩**: 명세 BOM+CRLF 혼합 입력에서 정상 파스(`utf-8-sig` + `splitlines()`).
- **코드 펜스**: 펜스 안 판형 예시가 실표로 오파스되지 않음(S3 확인).
- **`@media` 중첩**: `RULE_RE` 가 백트래킹으로 내부 규칙을 정확히 집는다(셀렉터도 정상 정규화).
- **`padding` 축약 2/3/4값**, **단위 없는 `0`**, **`0 0 0 3px` 네 변 3px**: 정상.
- **Codex byte 미러**: 검사기 2 + 픽스처 2 모두 `cmp -s` 일치.
- **계획 §5 B-3 양성 대조**: A8 web 사본의 `.rpe-scroll` 에 `padding: 3px 3px 4px` 를 넣으면
  발견 13 → 12 로 그 항목만 사라진다(정상).
- **성능**: A8 (CSS 규칙 수천·템플릿 95)에서 0.11s. O(n²) 위험은 실측 범위에서 문제 없음.

## 원복 증명

정본 파일은 한 번도 수정하지 않았다. 변이 시험은 `scripts/` 전체를 scratchpad 로 복사해
사본에서만 수행했고, B1 확인의 `git stash push/pop` 은 즉시 복원했다.
리뷰 종료 시점 `git diff --stat` = 착수 시점 스냅샷과 동일(15 files changed, 32 insertions(+), 15 deletions(-)),
`git status --porcelain` 의 M 15줄·?? 16줄도 동일. 검사기·픽스처 4종은 여전히 `??`(신규 미추적).
A8 워크트리는 `git status --porcelain web` 무출력(무수정).
