# 규칙 선검증 — 링 중첩 정적 판정 (2026-09-15)

설계 v3 §5ⓑ의 판정 규칙을 **구현 전에** A8 실물로 실측했다. 원형: 스크래치패드 `fr_proto.py`
(`check_clip_clearance` 모듈을 import 해 씀 — import 가능성 [실측] 확인, 13개 심볼 전부 존재).

## 1차 실측 결과 (A8 `web/`)

```
전역 링 규칙 1건: base.css :: :focus-visible
래퍼 링 규칙 5건: .input-field__control · .textarea-field__control · .choice-pair · .select-field__control · .input-field__control
억제 클래스 2: ['input-field__input', 'textarea-field__input']
발견 11건
```

**목표 결함을 잡았다** [실측]:
```
[FINDING] components.css :: .select-field__control 안의 억제 없는 포커스 대상
  — related_person_editor_step.html '<select class="select-field__select" id="relation_kind" …>'
  · 안쪽 radius 0 vs 바깥 18px — 직각 링
```

## 나머지 10건 판별 — 하나씩 실물로 확인

### ⓐ `.input-field__control` × icon-button — **진짜다** (오탐 아님)

`auth/login/view/login.html:50-56` [확인]:
```html
<div class="input-field__control">
  <i class="input-field__icon icon-lock" …></i>
  <input class="input-field__input" …>          ← 억제 있음(components.css:323) → 면제
  <span class="input-field__trailing">
    {% include "…/button/icon_button.html" … %}  ← 억제 없는 <button> → 이중 링
  </span>
</div>
```
trailing 슬롯의 아이콘 버튼이 전역 `:focus-visible`로 **직각 링**을 받고, 래퍼는
`:focus-within`으로 둥근 링을 받는다. **select와 같은 결함 부류다.**
`signup_step.html:90,118` · `password_reset_step.html:99,128` · `user_info_hour_field.html:20`에도
같은 인라인 판형이 있다 [확인].

### ⓑ `.choice-pair` × `<input class="choice-pair__input">` — **오탐이다**

`components.css:624-633` [확인]:
```css
.choice-pair__input { position: absolute; width: 1px; height: 1px; margin: -1px;
                      padding: 0; overflow: hidden; clip: rect(0, 0, 0, 0); border: 0; }
```
sr-only 판형이다. 1×1px에 `clip: rect(0,0,0,0)`이라 **링이 보일 수 없다.**

→ **판정 규칙에 «시각적 은닉 제외»가 필요하다.** 은닉 신호: `clip: rect(0` · `clip-path` ·
(`width:1px` ∧ `height:1px`) · `opacity: 0`. 하나라도 있으면 그 클래스는 링 대상에서 뺀다.

### ⓒ `.input-field__control`이 2번 나온다 — **중복이다**

`components.css`와 `user_info.css`가 같은 클래스에 각각 링 규칙을 둔다 [확인].
→ **(래퍼 클래스, 템플릿, 요소) 단위로 중복 제거**가 필요하다. CSS 파일 수만큼 부풀면 안 된다.

### ⓓ 태그 표시가 `'<button>'`으로 잘린다 — 표시 결함

여러 줄 태그에서 `find(">")`가 첫 `>`를 잡는다. 판정에는 영향 없고 **보고 문구만** 고친다.

## 판정 규칙 확정 (설계 §5ⓑ 보정)

1. 전역 링 규칙 = `RING_TRIGGER_RE` ∧ 마지막 compound에 타입·클래스·ID 없음 ∧ 바깥 box-shadow
2. 래퍼 링 규칙 = `:focus-within` ∧ 바깥 box-shadow → 대상 클래스 K
3. 억제 = `:focus`류 셀렉터 ∧ `box-shadow: none` → 면제 클래스
4. **은닉 = sr-only 판형 → 면제 클래스** ← 신규(ⓑ)
5. 조인 = `element_span(K)` + `expand`(include/extends) 안의 포커스 가능 요소
6. **중복 제거 = (K, 템플릿, 요소 오프셋) 단위** ← 신규(ⓒ)
7. radius 비교는 발견 줄의 부속 정보(직각 링 / 모서리 불일치)

보정 후 A8 예상 발견: `.input-field__control` × icon-button 계열 + `.select-field__control` × select.
`.choice-pair`와 `.textarea-field__control`(억제 있음)은 **뜨지 않아야 한다** — 합격 기준이다.

## 선례

v1.1.16 절단 수리에서 «진단이 제안한 방향 2개를 적대 검토가 둘 다 뒤집은» 일이 있었다
([[web-clip-fidelity-repair]]). 그래서 이번에는 **설계 검토와 병행해 규칙을 먼저 실측했다.**

## 2차 실측 — 보정 후 (확정)

```
전역 링 규칙 1건: base.css :: :focus-visible
래퍼 링 규칙 5건 · 억제 클래스 8(은닉 6 합류)
[FINDING] components.css :: .input-field__control … 외 3건 — login.html '<button>' · radius 0 vs 999px — 직각 링
[FINDING] components.css :: .select-field__control … — select_field.html '<select class="select-field__select" …>' · radius 0 vs 18px — 직각 링
[FINDING] components.css :: .select-field__control … — related_person_editor_step.html '<select … id="relation_kind" …>' · radius 0 vs 18px — 직각 링
발견 3건
```

| 대상 | 기대 | 실측 | |
|---|---|---|---|
| `.select-field__select` (사용자가 본 화면) | 발견 | 발견 | ✅ |
| `.select-field__select` (DS 부품) | 발견 | 발견 | ✅ |
| `.input-field__control` trailing 아이콘 버튼 | 발견 | 발견 | ✅ 같은 결함 부류 |
| `.input-field__input` | 면제(억제) | 없음 | ✅ |
| `.textarea-field__input` | 면제(억제) | 없음 | ✅ |
| `.choice-pair__input` | 면제(은닉) | 없음 | ✅ |
| `user_info.css` 중복 | 1건으로 접힘 | 접힘 | ✅ |

**오탐 0 · 미탐 0.** 설계 §8 합격 기준 2가 구현 전에 이미 성립함을 보였다.

## 구현 함정 — 원형에서 실제로 밟은 것

**중복 제거를 억제 판정 *앞*에 두면 안 된다.** `login.html`의 `.input-field__control`은
억제 대상(`input-field__input`)이 억제 없는 아이콘 버튼보다 **먼저** 나온다. 중복 키를
먼저 찍으면 억제 대상이 자리를 차지하고 **진짜 발견이 통째로 사라진다**(실제로 발견 3→2로
사라졌다가 순서를 고쳐 복구). 순서: 태그 추출 → **억제/은닉 면제** → 중복 제거 → 발견.

## 남은 다듬기 (판정 무관)

- 여러 줄 태그에서 보고 문구가 `'<button>'`으로 잘린다 — 표시만 고친다.

## 경계 판형 5종 — 합성 사례 시험 [실측]

| 사례 | CSS | 기대 | 실측 |
|---|---|---|---|
| E1 | `*:focus-visible` | 전역 링 | 전역 1건 · 발견 1 ✅ |
| E2 | `a:focus-visible` | 전역 아님(타입 한정) | 전역 0건 · 발견 0 ✅ |
| E3 | `:where(:focus-visible)` | 전역 링 | 전역 1건 · 발견 1 ✅ |
| E4 | `inset 0 0 0 3px` 만 | 바깥 링 아님 | 전역 0건 · 발견 0 ✅ |
| E5 | 안팎 radius 일치 | 이중 링이되 «직각» 아님 | 발견 1 · 직각 표기 없음 ✅ |

이 5종을 `fixtures_focus_ring.sh`의 회귀로 그대로 옮긴다.

### 의도한 판정 한계 — 고지 줄로 낸다

**타입 한정 전역 규칙**(`a:focus-visible` 같은)은 «전역»으로 보지 않는다(E2). 그 태그만
이중 링이 되는 좁은 판형은 잡히지 않는다. A8에는 그런 규칙이 없고(전역은 bare `:focus-visible`
하나뿐 [실측]), 실물에서 나타나기 전에 분기를 미리 만들지 않는다. `check_clip_clearance.py`의
«조인 한계» 줄과 같은 판형으로 **한계를 출력에 명시**한다.

---

# 3차 — rv-F 반영본 (원형 v2) [실측]

rv-F가 BLOCKER 2로 지적한 «전역 링 정의가 실무 최빈 판형 2종을 놓친다»는 참이다.
`check_clip_clearance.last_compound`는 `re.split(r"[>+~]|\s+", …)`라 **괄호를 모른다**.
→ **괄호 인식 셀렉터 분류기**를 새 모듈이 자체 보유한다(`last_compound` 재사용 불가).

## 분류기 검증 — rv-F 표 전건

| selector | kind | targets | 제외 | scoped |
|---|---|---|---|---|
| `:focus-visible` | global | — | — | |
| `*:focus-visible` | global | — | — | |
| `:where(a, button, input):focus-visible` | **types** | a·button·input | — | |
| `:is(a, button):focus-visible` | **types** | a·button | — | |
| `input:focus-visible` / `select:focus-visible` | **types** | 각 태그 | — | |
| `.theme-dark :focus-visible` | global | — | — | **✓ 스코프 표기** |
| `:focus-visible:not(.no-ring)` | global | — | **no-ring** | |
| `[data-conversation-mount] :is(.standard-button, .round-button):focus-visible` | narrow | — | — | ✓ (클래스 소실 없음) |
| `.select-field__control:focus-within` | narrow(래퍼) | — | — | |

## 경계 판형 7종 회귀 [실측]

| | 판형 | 기대 | 실측 |
|---|---|---|---|
| F1 | `:where(a,button,input):focus-visible` | 타입 링 → 발견 | 타입 링 1 · 발견 1 ✅ |
| F2 | `select:focus-visible`만 (대상에 select 없음) | 발견 0 | 발견 0 ✅ |
| F3 | `.theme-dark :focus-visible` | 발견 + 스코프 고지 | 고지 포함 발견 1 ✅ |
| F4 | `:focus-visible:not(.b):not(.i)` | 예외가 면제로 | 면제 2 · 발견 0 ✅ |
| F5 | 자손이 자기 `:focus` 그림자 명시 선언 | 인벤토리(발견 아님) | 인벤토리 1 · 발견 0 ✅ |
| F6 | 링 규칙 0건 | **무증상 exit 0 금지** | «판정을 수행하지 않았다» 명시 ✅ |
| F7 | `:is(.x,.y):focus-visible` | 전역 아님 | 전역 0 ✅ |

## A8 재실측 (원형 v2)

```
[focus-ring] 전역 링 1 · 타입 링 0 · 래퍼 링 4 · 면제(억제/은닉) 8 · 명시선언 13
[inventory] 전역 링 base.css :: :focus-visible
[FINDING] components.css :: .input-field__control … 외 7건 — login.html <button> · radius 0 vs 999px — 직각 링
[FINDING] components.css :: .select-field__control … — select_field.html <select class="select-field__select"> · radius 0 vs 18px — 직각 링
[FINDING] components.css :: .select-field__control … — related_person_editor_step.html <select class="select-field__select"> · radius 0 vs 18px — 직각 링
[focus-ring] 조인 한계 — include/extends 만 따라가고 템플릿당 첫 일치만 본다(동적 클래스·부품 단독 사용은 못 본다)
[focus-ring] 발견 3건 · 인벤토리 1건
```

**`.input-field__control`은 오탐이 아니다** — rv-F BLOCKER 1과 내 1차 실측이 같은 결론이다.
`login.html:50-56`의 trailing 아이콘 버튼이 억제 없이 전역 링을 받는다. 설계 §5ⓐ의
«select만 누락» 문장을 **실측으로 교체해야 한다**(설계 v4).

## 확정된 판정 규칙 (설계 v4 §5ⓑ가 될 것)

1. **셀렉터 분류**(괄호 인식): 전역 / 타입 / 좁힘 · `:not()` 예외 수확 · 조상 스코프 표기
2. **래퍼 링** = `:focus-within` ∧ 바깥 box-shadow → K
3. **면제** = ⓐ `:focus*` 규칙의 `box-shadow: none` ⓑ sr-only 은닉 ⓒ `:not()` 예외 클래스
4. **인벤토리(발견 아님)** = 자손이 자기 `:focus` 그림자를 **명시 선언**한 경우(교체이지 누락이 아니다)
5. **조인** = `element_span(K)` + `expand` · 타입 링이면 해당 태그만
6. **중복 제거** = (K, 템플릿) — 단, **면제 판정 뒤에** 한다(순서 함정)
7. **전역·타입 링 0건** → exit 0 이되 «판정을 수행하지 않았다»를 **명시 출력**(무증상 통과 금지)
8. 조인 한계 1줄 항상 출력(`check_clip_clearance`와 같은 판형)

---

# 4차 — 구현 완료 (2026-09-15)

`dddjango-web/scripts/check_focus_ring.py` 신설 + Codex byte 미러.
회귀 `fixtures_focus_ring.sh` **18/18 PASS** · 전체 `run_fixtures.sh` **15개 파일 실패 0**.

A8 실물 최종 출력:
```
[focus-ring] 전역 링 1 · 타입 링 0 · 래퍼 링 4 · 면제 8 · 자기 선언 13
[inventory] 전역 링 base.css :: :focus-visible
[FINDING] components.css :: .input-field__control … 외 7건 — login.html <button> · 안쪽 radius 미상(리터럴 클래스 없음 — 모서리는 육안)
[FINDING] components.css :: .select-field__control … — select_field.html <select class="select-field__select"> · 안쪽 radius 0 vs 바깥 18px — 직각 링
[FINDING] components.css :: .select-field__control … — related_person_editor_step.html <select class="select-field__select"> · 안쪽 radius 0 vs 바깥 18px — 직각 링
[focus-ring] 판정 한계 — … [focus-ring] 발견 3건 · 인벤토리 1건   (exit 2)
```

## 규범 배선 4곳 + Codex 미러 4곳

| 파일 | 내용 |
|---|---|
| `commands/dddjango-web.md` G2 배너 | «링 정적 검사» 항목에 합류 · **종료 코드 분리 표기**(rv-F MAJOR 4) · «판정 안 함»은 «발견 0»과 다르다 명시 |
| `commands/dddjango-web.md` 패스트트랙 ③ | `check_focus_ring` 합류 |
| `agents/discipline-reviewer-web.md` | 링 중첩 감사 **의무** 트리거 + 기계가 못 보는 축 인계 |
| `skills/implementation-ui/references/final.md` | «링 소유권» 규율 — 래퍼가 링을 소유하면 **모든** 포커스 가능 자손에 억제 |
| Codex `SKILL.md` ×2 · `dddjango-web-discipline-reviewer-web/SKILL.md` · `implementation-ui/references/final.md` | 의미/byte 미러 |

계약 검사 3종(`request_guide_contract`·`web_hooks_contract`·`web_refreeze_contract`) green.

## 절차 기록 (정직하게)

§5는 «진단 → 설계 → 적대 검토(rv-F) → **규칙 선검증 실측** → 구현 → 회귀»로 갔다.
별도 «계획서 → 계획 리뷰» 단계를 **건너뛰었다** — 검사기 한 개짜리 자족 산출물이라 계획서가
설계 §5ⓑ의 재서술이 됐을 것이고, 대신 **구현 전에 원형으로 A8 실물과 경계 판형 12종을 측정**했다.
그 측정이 rv-F의 BLOCKER 2건(오탐·미탐)을 구현 전에 잡았다. 나머지(§2 원장·§4 재동결)는
계획서를 정식으로 쓴다 — 거기는 검사기 하나가 아니라 게이트 위상을 건드린다.
