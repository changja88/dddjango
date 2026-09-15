# 설계 v3 — 게이트 하드월 철거와 링 정적 검사

선행: `workspace/eval/web-gate-hardwall/diagnosis.md` · 적대 검토 `design-review/rv-{A,B,C}.md`
(누적 BLOCKER 14 · MAJOR 20 · MINOR 12). v1·v2는 **전량 반려**다 — 아래 §0이 왜인지 적는다.

구속 지시(사용자): **«재동결하라고 하고 차이점이 있으면 수정을 하게 하면 된다. 그리고 이게 애초에
무슨 이유로든 불가능해지는 거 자체가 말이 안 된다.»** → **«하드월 걷어내»** · 범위 **①(16개 전부 한 사이클)**.

추가 목표(2026-09-15 A8 실물 결함 2건): 아래 §5. 이 둘이 **이번 수리의 합격 기준**이다.

---

## §0. v1·v2가 왜 반려됐나 — v3가 다르게 하는 것

| 반려 사유 | v1·v2가 한 것 | v3가 하는 것 |
|---|---|---|
| 벽을 하나씩 열면 **벽이 한 칸 뒤로 밀린다** (rv-B B6·rv-C B5) | `_check_exclusions`의 10% 상한만 열었다 | 검사기의 **단일 종료 지점**에서 연다 — 벽 목록을 세지 않는다 |
| **천장이 없다** (rv-A B1) | «지위 강등»에 상한을 못 걸었다 | 승인 시점의 **규모를 기계가 기억**한다. 규모가 커지면 다시 막힌다 |
| **가장 싼 길이 부정직** (rv-A B2) | 드라이버를 안 이으면 부채까지 해소됐다 | «관찰 자체를 안 했다»는 발견은 **원장이 받지 않는다**(§3) |
| **기록이 에이전트 소유 파일에 산다** (rv-C B1) | `build-state.json`에 적었다 | **원장 파일 자체가 기록**이고 검사기가 읽는다 — 지우면 다시 막힌다 |
| **표 집합이 치환됐다** (rv-C B3) | 16행을 임의로 골랐다 | §6이 rv-B 전수 표와 1:1이다 |
| **수집기 바이트를 바꾸면 기존 증거 전량 무효** (rv-B B2) | `observe_interactions`/`render_audit.js` 개정을 검토했다 | 수집기를 **건드리지 않는다**. §5는 브라우저 없는 정적 검사다 |

---

## §1. 불변식과 집행 축

**불변식 I**: 어떤 상태에서도 «재동결 → 대조 → 수정»으로 이어지는 행동열이 존재한다.
사용자가 사실을 알고 승인하면 길이 있다.

**불변식 II**: 열린 길은 **무엇이 미검증인지 지우지 못한다**. 기록은 검사기가 읽는 곳에 남고,
지우면 길이 다시 닫힌다.

**집행 축은 `--phase`다** (rv-C B1의 «축이 없다»에 대한 답):

| phase | 뜻 | 원장 적용 | 결과 |
|---|---|---|---|
| `prepare` | 검토 지문 | 적용 안 함 | 원장 대상 발견이 없다 |
| `inputs` | **진행 허용** | 적용 | 등재분은 notice, exit 0 |
| `visual` | **마무리** | 적용 + **낙인** | 결과 JSON에 `unverified_ledger` 동봉 — 배너·마무리 보고 1급 |

같은 판정이 같은 메시지를 내고, **막을지 말지는 원장이 결정한다.** phase는 그 결과를 어떻게
표면화할지만 가른다.

---

## §2. 원장 — 단일 기계

### ⓐ 파일

`<빌드 폴더>/evidence-ledger.json`. **`ledger.py`만 쓴다** — 에이전트 직접 편집 금지(규범).

```json
{"version": 1, "entries": [
  {"key": "<정규화 메시지의 sha256 앞 16>",
   "label": "cases[3].interactions: 잔여 N건 — …",
   "check": "design-evidence", "reason": "approved_partial",
   "quote": "<사용자 승인 원문>", "scope_ref": "scope.md#드롭다운-재작성",
   "anchor_sha256": "<앵커 절 본문의 sha256>",
   "magnitude": [38, 114], "approved_at": "2026-09-15T23:10:00+09:00"}]}
```

### ⓑ 키 — 위조할 수 없다

`ledger.py add`는 **직전 검사 실행의 발견 목록에서만** 키를 받는다:

```
python ledger.py add --build <빌드> --project-root <루트> \
    --index <발견 번호> --quote "<원문>" --scope-ref "<경로>#<앵커>" [--reason <enum>]
```

`add`는 **스스로 `check_design_evidence.py --phase inputs`를 실행해** 발견 목록을 만들고,
`--index`가 가리키는 발견만 등재한다. 에이전트가 문자열을 지어낼 자리가 없다.

**정규화**: 메시지에서 숫자열과 따옴표 안 목록을 지운 뒤 sha256. 관찰을 다시 해도 같은 벽이면
같은 키다. 검사기 메시지 문구가 개정되면 키가 어긋나 **다시 막힌다** — fail-closed가 옳은 방향이다.

### ⓒ 천장 — 규모를 기계가 기억한다 (rv-A B1)

`magnitude`는 승인 시점 메시지에서 뽑은 정수열이다. 조회 때 **현재 정수열의 각 자리가 승인 규모
이하일 때만** 등재로 인정한다. 잔여가 38 → 51로 늘면 그 행은 **무효**가 되고 다시 막힌다.
사용자는 커진 규모를 보고 다시 승인한다.

### ⓓ 승인 원문 — 앵커 절 안이어야 한다 (rv-A B3)

기존 `interaction_exclusions`는 «원문이 `scope.md` **어디에든** 있으면» 통과였다. rv-A는 «네»
같은 흔한 문자열이 통과함을 실측으로 보였다. 원장은 다르게 한다:

1. `scope_ref`의 앵커가 실재해야 한다(기존과 같음).
2. 원문이 **그 앵커 절 본문 안에** 있어야 한다(다음 동급 이상 제목 전까지).
3. `add` 시점에 그 절 본문의 sha256을 `anchor_sha256`에 박는다. 절이 나중에 바뀌면 **무효**다.

### ⓔ 집행 지점 — 단 한 곳

`check_design_evidence.py:main()`의 `except Defects` 한 자리다.

```python
except Defects as error:
    blocking, ledgered = partition_by_ledger(build, error.messages, phase)
    for message in ledgered:
        print(f'[design-evidence] unverified(원장): {message}', file=sys.stderr)
    if blocking:
        for message in blocking:
            print(f'[design-evidence] defect: {message}', file=sys.stderr)
        return 2
    print(json.dumps(ledger_result(build, phase), sort_keys=True))
    return 0
```

**벽을 세지 않는다.** 이 검사기의 모든 발견이 같은 문을 쓴다 — rv-B B6·rv-C B2·rv-C B5가
지적한 «한 칸 뒤로 밀림»이 구조적으로 불가능하다.

### ⓕ 지워도 소용없다 (불변식 II)

원장을 지우면 등재가 사라져 **발견이 다시 막는다**. 기록과 통행권이 같은 파일이라
«기록만 지우고 통과»가 성립하지 않는다. `backstop.py`는 원장이 비어 있지 않은 동안
**매 실행 notice 1줄**을 낸다.

---

## §3. 천장 — 원장이 받지 않는 발견 (rv-A B2 · rv-B B1)

`ledger.py add`가 **거부**하는 발견 부류:

| 부류 | 거부 사유 | 유일한 예외 |
|---|---|---|
| `interaction evidence required (version N with interactions)` | 관찰 자체를 안 했다 — 열면 드라이버 미연결이 가장 싼 길이 된다 | `--reason no_observable_surface` |
| `usage/error` · `internal error` (exit 1) | 발견이 아니라 미실행이다 | 없음 |
| `coverage_review: … does not match` | 검토 문서 재생성으로 항상 닫힌다 | 없음 |

**`no_observable_surface`** 는 «관찰할 DOM이 없다» 축이다(rv-B B1). 기계 검증 조건:
`build-state.json.has_design_screen`이 false이거나, `screen-meta.json`의 시안 출처가
이미지·PDF 계열일 때만 `add`가 허용한다. 에이전트 주장만으로는 안 열린다.

---

## §4. 재동결 — 세 자리 (rv-B B3·B5 · rv-C B4·B5)

### ⓐ `cmd_begin`: 판독 실패에 막히지 않는다 (`refreeze.py:346-352`)

```python
    errors: list[str] = []
    discard = discard_set(build, errors)
```
지금은 `errors`가 있으면 `return 1`이다 — **재동결이 고칠 대상이 재동결을 막는다**.
v3: 판독 실패를 **journal의 `unreadable`에 적고 진행**한다. 되감기 안전성은 `_prev`가 지므로
폐기 집합이 불완전해도 되돌릴 수 있다.

### ⓑ `cmd_check`: 같은 판정을 같이 고친다 (rv-C B5)

`refreeze.py:435-440`의 `증거 문서를 읽을 수 없다: …`도 같은 이유로 **경고로 내리고 통과**한다.
begin만 고치면 벽이 check로 한 칸 밀린다.

### ⓒ `_finish`: `_prev`를 한 세대 보존한다 (rv-C B4)

`_cleanup(staging, prev)`이 `_prev`를 지운다. §2가 «부분 검증으로 진행»을 허용하는 순간
**되돌릴 수 없는 폐기**가 된다. v3: `_prev` → `_discarded-<ts>/`로 이름만 바꿔 남긴다.
`backstop.py:286-293`의 잔존물 BLOCKER 접두 목록에서는 제외한다(사용자가 지울 때까지 방해 없음).

### ⓓ 렌더 실측 생략 enum (rv-B B4)

`SKIP_REASONS`에 `no_measurable_dom`을 추가한다 — 이미지 시안·자체 설계 빌드가 영구 exit 3이 되는
자리를 연다.

---

## §5. 링 정적 검사 — `check_focus_ring.py` 신설

A8 실물 결함 2건 중 **직각 이중 링**을 잡는 기계다. 브라우저·수집기 불요(rv-B B2 회피).

### ⓐ 실측된 결함

```css
/* base.css:88-91 — 요소 무관 전역 규칙 */
:focus-visible { outline: none; box-shadow: var(--focus-ring); }
/* components.css:835-839 — 래퍼가 링을 소유 */
.select-field__control:focus-within { box-shadow: var(--focus-ring), var(--field-flat); }
```
`.select-field__control` 안의 `<select class="select-field__select">`가 전역 규칙을 **또** 받는다.
그 요소는 `border-radius` 선언이 없어 `0px`다 → **직각 링이 둥근 링 안에 겹쳐 그려진다**.
`.input-field__input`은 `components.css:323`에 억제(`box-shadow: none`)가 있어 면제된다 —
**select만 누락**이다. Chrome 실측: 마우스 클릭만으로 `<select>`가 `:focus-visible`을 매치한다.

시안에는 없다: 시안 번들 `styles.css`에 `focus` 0건이고, 시안 `Select`는 native `<select>`를
쓰지 않으며(`createElement("select")` 0건) `Dropdown` 트리거 **한 요소**에만
`borderRadius: t.radius` + `boxShadow: 'var(--focus-ring), …'`를 얹는다.

### ⓑ 판정

전제 — `check_clip_clearance.py`의 CSS·템플릿 기계를 **import 해서 쓴다**(중복 구현 금지).

1. **전역 링 규칙**: `RING_TRIGGER_RE`에 걸리고 마지막 compound에 타입·클래스·ID가 없는 규칙
   (`:focus-visible`, `*:focus-visible`). 대상 = 포커스 가능한 모든 요소.
2. **래퍼 링 규칙**: `:focus-within`으로 **바깥** box-shadow를 얹는 규칙. 대상 클래스 K.
3. **억제**: 셀렉터에 `:focus`류가 있고 본문이 `box-shadow: none`인 규칙의 클래스 집합.
4. **발견**: 전역 링 규칙이 존재하고, K의 템플릿 서브트리(`element_span`+`expand`) 안에
   억제되지 않은 포커스 가능 요소가 있으면 — **이중 링**.
   그 요소의 `border-radius`가 K와 다르면 «직각 링» 또는 «모서리 불일치»를 같은 줄에 덧붙인다.

### ⓒ 계약

```
python check_focus_ring.py <web 루트>
exit 0 = 발견 0 / 2 = 발견 ≥1(판단 자료·비차단) / 1 = 미실행
```
`check_clip_clearance.py`와 동일 판형이다. 배너에서는 두 명령을 **«링 정적 검사» 한 항목**으로
묶어 표기한다(배너 줄 수 증가 0 — rv-B MAJOR «배너가 결정 자료로 무너진다»).

### ⓓ 결함 1(좌우 절단)은 수리 대상이 아니다

v1.1.16이 이미 `check_clip_clearance.py`로 잡는다 — A8 실측에서 `.rpe-scroll` 4변 확정 포함
**12건**을 낸다. 배선도 4곳(`commands:187`·`commands:220`·`agents/discipline-reviewer-web.md:62`·
`skills/implementation-ui/references/final.md:214`) 완료다. **합격 기준으로만 쓴다.**

---

## §6. 하드월 전수 표 — rv-B 집합과 1:1 (rv-C B3)

rv-B의 «하드월 전수 표»에서 **«예»로 판정된 17개**를 그대로 싣고, 각 행에 v3 처분을 적는다.
표기: **L**=원장으로 열림(§2) · **R**=재동결 수리로 열림(§4) · **A**=이미 행동으로 열림(수리 불요) ·
**X**=이번 사이클 제외(사유 명시).

| # | 벽 | 위치 | v3 처분 |
|---|---|---|---|
| 1 | 잔여 단위가 남으면 발견 | `check_design_evidence:963-975` | **L** |
| 2 | case별 `source_observation` v2 요구 | `:validate_inputs` | **L**(단 §3 — `no_observable_surface` 한정) |
| 3 | 예외 10% 상한 | `:895-897` | **L** |
| 4 | 표면 예외가 단위 잔여를 못 닫음 | `:955-960` | **L** |
| 5 | `approval_quote` 미검증 통과 | `:876-880` | **L** + §2ⓓ가 오히려 조인다 |
| 6 | `coverage_review` 불일치 | `validate_inputs` | **A** — 검토 문서 재생성 |
| 7 | `refreeze begin` 판독 실패 exit 1 | `refreeze:346-352` | **R** |
| 8 | `refreeze check` 같은 판정 | `refreeze:435-440` | **R** |
| 9 | `_finish`의 `_prev` 삭제 | `refreeze:639` | **R** |
| 10 | 렌더 실측 생략 enum 부족 | `refreeze:SKIP_REASONS` | **R** |
| 11 | `_refreeze-*`/`_prev-*` 잔존 → 프로젝트 전역 BLOCKER | `backstop:286-293` | **R** — §4ⓒ가 접두를 분리 |
| 12 | 재동결이 `.dc.html` 경로 전용 | `refreeze` 출처 판정 | **X** — 대상 빌드가 dc 경로다. 별건(근거: 이번 합격 기준에 닿지 않음) |
| 13 | 설계 빌드 0 + config 有 → 영구 BLOCKER | `backstop:294-296` | **X** — 별건. 대상 빌드에 빌드 폴더가 있다 |
| 14 | `implementation_digest`의 `web/` 필수 | `check_design_evidence` | **X** — 별건 |
| 15 | 진행 중 설계 빌드가 다른 실행을 막음 | `backstop` | **X** — 별건 |
| 16 | `archive_files` 4096 상한 | `refreeze` | **X** — 대상 빌드 716파일. 별건 |
| 17 | `visual-evidence.json`에 이탈 칸 없음 | 스키마 | **X** — §2 원장이 대체 채널이다 |

**제외 5건(12~16)은 전부 «대상 빌드에서 발화하지 않고 합격 기준에 닿지 않는다»가 사유다.**
이번 사이클의 합격 기준(§5 결함 2건 + A8 진행 재개)에 필요한 것만 연다 — 안 쓰는 문을 여는 것은
게이트 완화이지 수리가 아니다. 다섯 건은 진단서에 **별건 대기 목록**으로 남긴다.

---

## §7. 배선표

| 파일 | 변경 |
|---|---|
| `scripts/ledger.py` | **신설** |
| `scripts/check_design_evidence.py` | `main()` 원장 조회(§2ⓔ) · `run()`의 `visual` 결과에 `unverified_ledger` |
| `scripts/check_focus_ring.py` | **신설**(§5) |
| `scripts/refreeze.py` | §4 ⓐⓑⓒⓓ |
| `scripts/backstop.py` | 원장 notice 1줄 · `_discarded-` 접두 제외 |
| `commands/dddjango-web.md` | G0/G1/G2 배너에 «미검증 원장 N행» 1급 줄 · 링 정적 검사 항목에 `check_focus_ring` 합류 · 패스트트랙 ③ 합류 · `ledger.py` 사용 절차 |
| `agents/design-architect-web.md` | 원장 등재는 architect 권한 아님(Coordinator 전속) |
| `agents/design-review-web.md` | 원장 행을 리뷰 대상으로 |
| `agents/discipline-reviewer-web.md` | 이중 링 감사 트리거 추가 |
| `skills/architecture-web/references/final.md` | 원장 절 |
| `skills/implementation-ui/references/final.md` | 링 억제 규율(전역 `:focus-visible`가 있는 프로젝트는 래퍼 소유 시 자손 억제 의무) |
| `docs/DEVELOPMENT.md` | 원장 파일 지위 |
| `workspace/design/2026-08-23-…-spec.md` | D15 행 |
| `codex-dddjango-web/**` | 전량 미러(scripts byte · 규범 의미) |
| `scripts/test/fixtures_ledger.sh` | **신설** |
| `scripts/test/fixtures_focus_ring.sh` | **신설** |
| `scripts/test/fixtures_refreeze*.sh` | §4 회귀 추가 |

---

## §8. 합격 기준 (이번 수리의 검증)

배포 후 A8 재실행에서:

1. **절단 12건**이 G2 배너에 «링 정적 검사» 항목으로 뜬다 *(이미 성립 — 회귀 확인용)*
2. **직각 이중 링**(`.select-field__select`)이 `check_focus_ring.py` 발견으로 뜨고,
   `.input-field__input`은 **뜨지 않는다**(억제 면제가 작동)
3. A8이 «재동결 → 관찰 → 원장 승인 → inputs exit 0»으로 **진행 가능**해진다
4. 원장을 지우면 3이 **다시 막힌다**

1·2는 이 저장소에서 A8 사본으로 즉시 측정한다. 3·4는 배포 후 A8에서 최종 검증한다
([[a8-final-testbed]]).

---

## §9. rv-A·rv-B·rv-C BLOCKER 14건 대조

| 출처 | BLOCKER | v3 처분 |
|---|---|---|
| rv-A 1 | 지위 강등에 천장이 없다 | §2ⓒ 규모 기억 + §3 거부 부류 |
| rv-A 2 | 가장 싼 길 = 드라이버 미연결 | §3 — 그 발견은 원장이 안 받는다 |
| rv-A 3 | `approval_quote`가 승인을 식별 못 함 | §2ⓓ 앵커 절 한정 + `anchor_sha256` |
| rv-B 1 | «관찰 불가» 축에 문이 없다 | §3 `no_observable_surface`(기계 검증) |
| rv-B 2 | 수집기 바이트 변경 = 기존 증거 무효 | §5 — 수집기를 안 건드린다 |
| rv-B 3 | 재동결이 `.dc.html` 전용 | §6 #12 — **X(별건)** · 사유 명시 |
| rv-B 4 | 렌더 실측 생략 enum 부족 | §4ⓓ |
| rv-B 5 | `begin`이 증거 깨짐으로 거부 | §4ⓐ |
| rv-B 6 | 상한만 열고 잔여를 안 염 | §2ⓔ 단일 지점 — 벽을 세지 않는다 |
| rv-C 1 | 진행/완료를 가르는 축이 없다 | §1 표 — `--phase`가 축이다 |
| rv-C 2 | A8 실측에 §2·§3이 닿는 게 0건 | §6 #2 — 현재 발화 중인 벽이 표 1행이다 |
| rv-C 3 | 표 집합이 치환됐다 | §6 — rv-B 전수와 1:1 |
| rv-C 4 | 되돌릴 수 없는 폐기 | §4ⓒ `_discarded-` 한 세대 보존 |
| rv-C 5 | `begin`만 고쳐 벽이 뒤로 밀림 | §4ⓑ `check` 동시 수리 |

---

## §10. 열린 위험

- **원장이 «만능 열쇠»로 쓰일 위험**: §3 거부 부류 + §2ⓒ 규모 + §2ⓓ 앵커가 방어다.
  그래도 «사용자가 전부 승인하면 전부 열린다»는 참이다 — **그게 사용자 지시다.**
  방어의 목표는 «사용자 모르게 열리는 것»을 막는 것이지 «사용자가 아는데도 막는 것»이 아니다.
- **메시지 문구 개정 = 원장 무효**: fail-closed. 규범에 «검사기 메시지를 고치면 원장 재승인이
  필요하다»를 적는다.
- **`no_observable_surface` 오용**: 기계 조건 두 개로 막지만, 시안이 이미지인 빌드는 실제로
  전부 열린다. 그 부류는 애초에 관찰 대상이 없으므로 의도된 동작이다.
