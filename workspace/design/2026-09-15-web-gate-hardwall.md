# 설계 v5 — 게이트 하드월 철거와 링 정적 검사

선행 적대 검토 6종 · 누적 **BLOCKER 29 · MAJOR 40 · MINOR 24**
(`design-review/rv-{A,B,C,D,E,F}.md`). v3 원문은 `eval/web-gate-hardwall/design-v3-superseded.md`.

구속 지시(사용자): **«재동결하라고 하고 차이점이 있으면 수정을 하게 하면 된다. 그리고 이게 애초에
무슨 이유로든 불가능해지는 거 자체가 말이 안 된다.»** → **«하드월 걷어내»**

---

## §0. v4가 v3와 결정적으로 다른 한 가지

**집행 지점을 옮긴다.** v3는 `check_design_evidence.py:main()`의 `except Defects`에 원장을 놓았다.
rv-D가 그 선택 하나로 BLOCKER 4건이 난다는 것을 실측으로 보였다:

| v3의 결함 | 근거 |
|---|---|
| `backstop.py`가 `main()`을 안 지난다 | `backstop.py:30` `from check_design_evidence import … validate_inputs …` → `:300` 인프로세스 호출 → `:306` 자체 `except Defects` [확인] |
| 두 digest를 못 낸다 → G2 영구 차단 | `raise`가 `:1256`이라 `run()`의 `:1410-1414`에 도달 못 함 [확인] |
| `validate_visual` 전량 무검증 통과 | 같은 이유 [확인] |
| 한 줄 마스터키 | `:1081`·`:1085`의 조기 `raise Defects([...])`가 다른 모든 검사보다 앞이다 [실측: `_note` 키 하나로 발견 13→1] |

**v4의 자리**: `validate_inputs`의 `if issues: raise Defects(issues)` **직전**(`check_design_evidence.py:1255`).

```python
    if issues:
        issues = ledger.filter(build, issues, phase)   # 등재분 제거 · notice 는 stderr
    if issues:
        raise Defects(issues)
    return spec, canonical_digest(digest_items), digest_items
```

이 한 자리가 네 가지를 동시에 해결한다:
1. **두 소비자가 같은 문을 쓴다** — `main()`도 `backstop.py`도 `validate_inputs`를 지난다.
2. **digest 사슬이 산다** — 함수가 정상 return 하므로 `run()`이 끝까지 간다.
3. **`validate_visual`이 산다** — 건너뛰는 경로가 없다.
4. **조기 `raise Defects([...])` 5곳은 구조적으로 원장 밖이다** — `issues` 묶음이 아니다.
   `design-input.json` unreadable·invalid(`:1081`·`:1085`), `web` 디렉터리 부재(`:1263`),
   심링크 2건(`:1270`·`:1274`). **열거식 거부 목록이 필요 없다**(rv-D MAJOR «열거되지 않은 신뢰
   경계가 기본 개방»도 같이 해소된다).

---

## §1. 불변식

**I** — 어떤 상태에서도 «재동결 → 대조 → 수정»으로 이어지는 행동열이 존재한다.
**II** — 열린 길은 무엇이 미검증인지 지우지 못한다. 원장을 지우면 길이 다시 닫힌다.

phase는 **표면화**만 가른다(판정은 같다): `inputs`·`prepare`는 notice, `visual`은 결과 JSON에
`unverified_ledger` 동봉 → 배너·마무리 보고 1급.

> rv-D 지적대로 `prepare`와 `inputs`의 발견 집합은 `require_review` 한 항목만 다르다
> (`:1403`). **그래서 `prepare`에도 원장을 적용한다** — v3가 «prepare 제외»로 만든 교착
> (`review_digest`를 못 얻어 `coverage_review`를 영영 못 닫는다)을 없앤다.

---

## §2. 원장

### ⓐ 파일 — `<빌드>/evidence-ledger.json`

`ledger.py`만 쓴다(에이전트 직접 편집 금지 — 규범). 행 하나:

```json
{"key":"e1d94f1aabdcff46", "label":"cases[3].interactions: 잔여 38건 — …",
 "magnitude":38, "quote":"<사용자 승인 원문>", "scope_ref":"scope.md#드롭다운-재작성",
 "anchor_sha256":"<앵커 절 본문 sha256>", "approved_at":"2026-09-15T23:40:00+09:00"}
```

### ⓑ 키 — 정규화 [실측 검증 완료]

```
따옴표 구간 '…' → …          |  (\d+)\s*(건|행|개) → #\2  |  튜플 나열 접기 → (…)
```
`cases[N]` 인덱스는 **보존한다**(rv-D B6 — 12건이 한 키로 묶이면 승인 1건이 12건을 연다).

| 입력 | 키 동일성 | 실측 |
|---|---|---|
| `cases[3] … 잔여 38건` vs `잔여 51건` | **같아야** | 같음 ✅ |
| `cases[3]` vs `cases[7]` (같은 잔여) | **달라야** | 다름 ✅ |
| `cases[0]` vs `cases[1]` source_observation | **달라야** | 다름 ✅ |
| `partial(caps_hit=…) 수집인데` 접두 유무 | **달라야** | 다름 ✅ |
| `예외 5행…114개` vs `예외 9행…150개` | **같아야** | 같음 ✅ |

### ⓒ 규모 — 계수 단위 앞 첫 정수 하나 (rv-D B5)

`(\d+)\s*(건|행|개)`의 **첫 일치**. rv-D가 «정수열 28개 중 24개가 hex target id 파편»임을 실측했다 —
따옴표를 먼저 지우고 계수 단위로 한정하면 그 파편이 전부 배제된다 [실측 확인].
정수를 여럿 쓰지 않는 이유: `:897`의 둘째 정수(`활성 대상 M개`)는 **커지면 유리한** 값이라
«모든 자리 ≤ 승인치»로 보면 개선에도 재승인을 강요한다.

조회 시 **현재 규모 > 승인 규모면 그 행은 무효**다. 규모가 없는 발견(`magnitude: null`)은
규모 판정 없이 키로만 산다.

### ⓓ 승인 원문 — 앵커 절 안 (rv-A B3 · rv-D B7)

1. `scope_ref`의 앵커가 실재한다.
2. **앵커는 H2 이상 깊이여야 한다** — H1이면 «절 본문 = 파일 전체»라 §2ⓓ가 무력해진다(rv-D B7).
   H1 앵커는 `add`가 거부한다.
3. 원문이 **그 절 본문 안**에 있다(같은 수준 이상의 다음 제목 전까지).
4. `add` 시점 절 본문의 sha256을 박는다. 절이 바뀌면 그 행은 무효다.

### ⓔ 등재 — 위조 불가

```
python ledger.py add --build <빌드> --project-root <루트> --phase <prepare|inputs|visual> \
       --index <발견 번호> --quote "<원문>" --scope-ref "<경로>#<앵커>"
```
`add`가 **스스로 검사기를 돌려** 발견 목록을 만들고 `--index`가 가리키는 발견만 등재한다.
등재 직후 **다시 돌려** 그 발견이 실제로 사라졌는지 확인하고, 사라지지 않으면 행을 철회한다
(rv-D MAJOR «`--index`는 두 실행 사이의 서수» — 자기 검증으로 닫는다).
`ledger.py list`·`drop`도 둔다.

### ⓕ 지워도 소용없다

원장을 지우면 등재가 사라져 발견이 다시 막는다. 기록과 통행권이 같은 파일이다.
`backstop.py`는 원장이 비어 있지 않은 동안 **매 실행 notice 1줄**을 낸다.

### ⓖ 재동결이 `scope.md`를 폐기한다 (rv-D MAJOR)

`INPUT_GLOBS`가 `scope.md`를 staging으로 복사하고 install 로 되돌린다. 바이트가 같으면
`anchor_sha256`은 살아 있다. 바뀌면 그 행은 **무효가 되고 재승인이 필요하다** — 의도된 fail-closed다.
`refreeze commit` 완료 시 원장 행 중 무효가 된 것을 **콘솔에 열거**한다(조용한 소실 금지).

---

## §3. 천장 — 원장이 받지 않는 발견

`issues` 안에서 거부할 것은 **둘뿐**이다(나머지 구조 실패는 §0-4로 자동 배제):

| 발견 | 거부 사유 |
|---|---|
| `… interaction evidence required (version N with interactions)` | 관찰 자체를 안 했다 — 열면 «드라이버 미연결»이 가장 싼 길이 된다(rv-A B2) |
| `coverage_review: … does not match` | 검토 문서 재생성으로 **항상** 닫힌다 — 원장이 필요 없다 |

**`no_observable_surface` 예외는 v4에서 뺀다.** rv-D가 기계 조건 두 개가 «둘 다 평가 불가»임을
보였다. «관찰할 DOM이 없는 빌드» 축은 별건으로 남긴다(§6 X-목록).

---

## §4. 재동결

### ⓐ `cmd_begin` 판독 실패에 막히지 않는다 (`refreeze.py:346-352`)

`discard_set`의 `errors`로 `return 1` 하던 것을 **journal의 `unreadable`에 적고 진행**으로 바꾼다.

### ⓑ `cmd_check`도 같이 (`refreeze.py:435-437`)

`증거 문서를 읽을 수 없다: …`를 `issues`가 아니라 **경고**로 낸다. begin만 고치면 벽이 한 칸 밀린다(rv-C B5).

### ⓒ `_prev` 한 세대 보존 — **개명이 아니라 복사** (rv-C B4 · rv-E B1)

rv-E가 개명 방식을 `test_refreeze.Fixture`에 구현해 **데이터 소실을 재현**했다:
`commit --resume` exit 1(ENOTEMPTY) · `abort` exit 1 · live `design-ref/`·`design-input.json` 소실.
원인: `_prev-`는 되감기 저장소이면서 **«commit 진행 중» 표식**이다(`cmd_commit:498`
`_single(build, PREV_PREFIX)`). 개명하면 표식이 사라져 재개가 live 를 재폐기한다.

**v4**: `_cleanup`이 `_prev`를 지우기 **직전에 `copytree`로 `_discarded-<ts>/`를 만든다.**
`_prev`의 생성·소멸 시점과 의미는 **전혀 바뀌지 않는다.**
- 이름 충돌 시 접미 카운터(`_discarded-<ts>-2`).
- 복사 실패는 **경고만** 내고 정리를 계속한다(백업은 차단 사유가 아니다).
- `_cleanup` 호출처는 **두 곳**이다 — `refreeze.py:530`(`plan['phase']=='done'`)과 `:639`(`_finish`) [확인].
  복사는 `_cleanup` 안에 두어 두 경로가 같은 코드를 쓴다.
- `backstop.py:288-289`의 잔존물 접두는 `('_refreeze-','_prev-')` 포함형이라 `_discarded-`는
  **애초에 안 걸린다** [확인] — 목록 수정 불필요.

### ⓓ 잔존물 BLOCKER의 실제 문을 말한다 (rv-E B2)

A8에서 **지금 2건 발화 중**이고, 하나는 대상 빌드도 아니다(`backstop.py:283`의 잔존물 루프가
`builds`가 아니라 `discovered`를 돈다) [실측]. 그리고 `_prev-20260907-2302/`에는 `journal.json`도
`swap-plan.json`도 없어 `begin`=2·`check`=1·`commit --resume`=1이고 **오직 `abort`만 exit 0**인데,
메시지는 «commit --resume (완료 전이면 abort)»라 그 사실을 말하지 않는다 [실측].

**v4**: ① `journal.json`이 없는 `_prev-*`는 BLOCKER가 아니라 **notice**로 내린다(되감을 계획이
없으므로 «중단된 재동결»이 아니다) ② 남는 BLOCKER의 메시지에 **실제로 여는 명령**을 적는다
(`journal` 유무로 갈리는 분기를 문구에 넣는다) ③ 잔존물 루프를 `--design-build`가 주어지면
그 빌드로 한정한다.

### ⓔ `no_measurable_dom`은 v4에서 뺀다 (rv-E B4)

`cmd_check`의 enum 분기(`:442`)는 `missing` 게이트(`:421-441`) **뒤**다. 겨눈 부류는 그 앞에서
이미 exit 3이다 — enum만 늘리면 아무것도 안 열린다. **설계 내부 모순이라 삭제한다.**

---

## §5. 링 정적 검사 — `check_focus_ring.py` 신설

**구현 전 실측이 끝났다** — `eval/web-gate-hardwall/ring-overlap-prevalidation.md`.
A8 발견 3건 · 오탐 0 · 미탐 0 · 경계 판형 7종 회귀 통과.

### ⓐ 사실 (v3의 «select만 누락»을 실측으로 교체 — rv-F B1)

A8에서 전역 링(`base.css:88-91` `:focus-visible{box-shadow:var(--focus-ring)}`)을 억제 없이 받는
자손은 **두 계열**이다:
1. `.select-field__control > select.select-field__select` — radius 0 vs 18px **직각 링**
2. `.input-field__control > .input-field__trailing > .icon-button` — radius 999px vs 18px **모서리 불일치**
   (`login.html:50-56` · `signup_step.html:118-123`)

`.input-field__input`·`.textarea-field__input`만 억제가 있다(`components.css:323`·`:392`).
**즉 이번 수리는 A8 CSS 수정 «2계열»을 낳는다** — 계획서가 그 비용을 적는다.

### ⓑ 판정 (확정 — 7단계)

1. **셀렉터 분류(괄호 인식)** — `last_compound`는 `re.split(r"[>+~]|\s+")`라 괄호를 모른다.
   `:where(a, button, input)`이 `input)`으로 잘린다 [실측]. **새 모듈이 자체 분류기를 갖는다**:
   `global`(타입·클래스·ID 없음) / `types`(`:is/:where` 타입 나열 포함) / `narrow`(클래스로 좁힘).
   `:not()` 인자의 클래스는 **면제**로 수확하고, 조상 스코프가 있으면 발견 줄에 **표기**한다.
2. **래퍼 링** = `:focus-within` ∧ 바깥 box-shadow → 대상 클래스 K
3. **면제** = ⓐ `:focus*` 규칙의 `box-shadow: none` ⓑ sr-only 은닉(`clip: rect(0`·`clip-path`·
   `opacity:0`·`1px×1px`) ⓒ `:not()` 예외
4. **인벤토리(발견 아님)** = 자손이 자기 `:focus` 그림자를 **명시 선언**한 경우 — 교체이지 누락이 아니다(rv-F MAJOR 1)
5. **조인** = `element_span(K)` + `expand` · 타입 링이면 해당 태그만
6. **중복 제거** = (K, 템플릿) — **면제 판정 뒤에** 한다(순서 함정 실측: 앞에 두면 발견이 사라진다)
7. **radius 비교**는 발견 줄 부속(직각 링 / 모서리 불일치)

**전역·타입 링 0건이면 exit 0이되 «이 프로젝트에서는 이중 링 판정을 수행하지 않았다»를
명시 출력한다**(rv-F B2 — 무증상 통과 금지). 조인 한계 1줄도 항상 낸다.

### ⓒ 계약과 배너

```
python check_focus_ring.py <web 루트>      exit 0 = 발견 0 / 2 = 발견 ≥1(판단 자료·비차단) / 1 = 미실행
```
배너는 **«링 정적 검사» 한 항목**에 두 명령을 싣되 **종료 코드를 각각 적는다**(rv-F MAJOR 4 —
«clip exit 2 · focus_ring exit 1»이 발견 건수에 묻히면 안 된다):
`링 정적 검사: 절단 N건(exit 2) · 이중 링 M건(exit 2)` / 미실행은 «미실행+사유»로 분리 표기.
**기존 «절단 여유» 문구는 개명하지 않는다** — 개명은 4곳 문안을 흔들 뿐 얻는 게 없다(rv-F B3).

---

## §6. 하드월 처분 — rv-B 전수 표 기준

rv-B가 «예»로 판정한 17개에 rv-C·rv-D·rv-E가 더한 것을 합쳐 적는다.
**L**=원장 · **R**=재동결 수리 · **A**=이미 행동으로 열림 · **X**=별건(사유 명시).

| # | 벽 | 위치 | 처분 |
|---|---|---|---|
| 1 | 잔여 단위 발견 | `check_design_evidence:974` | **L** |
| 2 | 예외 10% 상한 | `:897` | **L** |
| 3 | 표면 예외가 단위 잔여를 못 닫음 | `:955-960` | **L** |
| 4 | `approval_quote` 미검증 통과 | `:876-880` | **L**(§2ⓓ가 오히려 조인다) |
| 5 | partial/caps_hit 발견 | `:717` | **L** |
| 6 | `case source_observation` v2 요구 | `validate_inputs` | **A** — 부분 관찰로 닫힌다(§8 순서) |
| 7 | `coverage_review` 불일치 | `validate_inputs` | **A** — prepare digest 재생성 |
| 8 | `refreeze begin` 판독 실패 exit 1 | `refreeze:346-352` | **R**(§4ⓐ) |
| 9 | `refreeze check` 같은 판정 | `refreeze:435-437` | **R**(§4ⓑ) |
| 10 | `_finish`의 `_prev` 삭제 = 되돌릴 수 없는 폐기 | `refreeze:_cleanup` | **R**(§4ⓒ) |
| 11 | 잔존물 → 프로젝트 전역 BLOCKER | `backstop:283-293` | **R**(§4ⓓ) |
| 12 | 렌더 실측 생략 enum 부족 | `refreeze:SKIP_REASONS` | **X** — §4ⓔ, 모순 |
| 13 | `REQUIRED_STAGING`이 비 dc 빌드를 막음 | `refreeze:39-40` | **X** — 별건 |
| 14 | 재동결이 `.dc.html` 경로 전용 | `refreeze` 출처 판정 | **X** — 별건 |
| 15 | 설계 빌드 0 + config 有 | `backstop:294-296` | **X** — 별건 |
| 16 | `implementation_digest`의 `web/` 필수 | `check_design_evidence:1263` | **X** — 별건 |
| 17 | 진행 중 설계 빌드가 다른 실행을 막음 | `backstop` | **X** — 별건 |
| 18 | `archive_files` 4096 상한 | `refreeze` | **X** — 별건 |
| 19 | `visual-evidence.json`에 이탈 칸 없음 | 스키마 | **X** — 원장이 대체 채널 |
| 20 | `environment_error` → exit 1 | `run()` | **X** — 미실행이지 발견이 아니다 |

**X 9건은 전부 «대상 빌드에서 발화하지 않고 이번 합격 기준에 닿지 않는다»가 사유다.**
진단서 «별건 대기 목록»에 옮긴다.

---

## §7. 배선표

| 파일 | 변경 |
|---|---|
| `scripts/ledger.py` | **신설** — `add`·`list`·`drop`·`filter`(모듈 API) |
| `scripts/check_design_evidence.py` | `validate_inputs:1255` 직전 원장 조회 · `run()`의 `visual` 결과에 `unverified_ledger` |
| `scripts/check_focus_ring.py` | **신설**(§5) |
| `scripts/refreeze.py` | §4ⓐⓑⓒ · commit 완료 시 무효 원장 행 열거 |
| `scripts/backstop.py` | 원장 notice 1줄 · 잔존물 §4ⓓ 3가지 |
| `commands/dddjango-web.md` | 배너 «미검증 원장 N행» 1급 · 링 정적 검사 2명령 종료코드 분리 표기 · 패스트트랙 ③ 합류 · `ledger.py` 절차 |
| `agents/design-architect-web.md` | 원장 등재는 Coordinator 전속 |
| `agents/design-review-web.md` | 원장 행을 리뷰 대상으로 |
| `agents/discipline-reviewer-web.md` | 이중 링 감사 트리거 |
| `skills/architecture-web/references/final.md` | 원장 절 |
| `skills/implementation-ui/references/final.md` | 전역 링이 있는 프로젝트의 자손 억제 의무 |
| `docs/DEVELOPMENT.md` | 원장 파일 지위 |
| `workspace/design/2026-08-23-…-spec.md` | D15 행 |
| `codex-dddjango-web/**` | 전량 미러 |
| `scripts/test/fixtures_{ledger,focus_ring}.sh` + `test_ledger.py` | **신설** |
| `scripts/test/test_refreeze.py` | §4 회귀 4건 (rv-E: 기존 스위트는 §4 변경을 **하나도 안 잡는다**) |

**Makefile 변경 없음** — `run_fixtures.sh`가 `fixtures_*.sh`를 글롭한다 [확인].
따라서 **봉인 재발행 불요**(`manifest_seal` protocol 군에 `Makefile`만 해당) [확인].

---

## §8. 합격 기준 — 측정 명령과 기대 출력 (rv-F B3)

| # | 명령 | 기대 |
|---|---|---|
| 1 | `bash dddjango-web/scripts/test/run_fixtures.sh` | green (신설 2종 포함) — **저장소 red 채널** |
| 2 | `check_clip_clearance.py <A8 web>` | exit 2 · `.rpe-scroll` 4변 «확정» 포함(건수 비고정) |
| 3 | `check_focus_ring.py <A8 web>` | exit 2 · 발견에 `select-field__select` **포함** · `.input-field__control` **포함**(정상) · `input-field__input`·`textarea-field__input`·`choice-pair` **미포함** |
| 4 | 같은 관찰 상태에서 원장만 토글 | 원장 0행 → exit 2 / 원장 N행 → exit 0 · `backstop.py`도 같이 바뀐다 |
| 5 | `make verify` | green |

4번이 핵심이다 — **관찰을 바꾸지 않고 원장만 토글**해야 원장의 효과가 분리 측정된다.
합성 빌드(`test_ledger.py`)로 측정한다.

**A8 최종 검증은 배포 후다**(순서를 못 박는다 — rv-D B1):
`부분 관찰(드라이버) → 12건 닫힘 → prepare exit 0 → coverage-review.md 재작성 → inputs 에서
잔여·상한 발견 → 사용자 승인 원문으로 원장 등재 → inputs exit 0 → backstop 도 exit 0`.
**A8은 원장만으로 열리지 않는다** — 관찰이 선행 조건이다. 그게 §3 천장의 의도다.

---

## §9. BLOCKER 29건 대조

| 출처 | 요지 | v4 처분 |
|---|---|---|
| rv-A 1 | 천장 없음 | §2ⓒ 규모 + §3 |
| rv-A 2 | 가장 싼 길 = 드라이버 미연결 | §3 1행 |
| rv-A 3 | `approval_quote` 식별 불가 | §2ⓓ |
| rv-B 1 | «관찰 불가» 축 | §6 X — 별건(rv-D가 기계 조건 불가 실측) |
| rv-B 2 | 수집기 바이트 변경 | §5 — 수집기 미변경 |
| rv-B 3 | dc 경로 전용 | §6 #14 X |
| rv-B 4 | 렌더 enum | §4ⓔ 삭제 |
| rv-B 5 | `begin` 거부 | §4ⓐ |
| rv-B 6 | 상한만 열고 잔여 안 염 | §0 — issues 묶음 전체 |
| rv-C 1 | 진행/완료 축 없음 | §1 — 판정은 같고 표면화만 가른다 |
| rv-C 2 | A8에 안 닿음 | §8 순서 명시 |
| rv-C 3 | 표 치환 | §6 재작성 |
| rv-C 4 | 되돌릴 수 없는 폐기 | §4ⓒ |
| rv-C 5 | `begin`만 고침 | §4ⓑ |
| rv-D 1 | 13건 전부 거부 → 안 열림 | §3에서 `no_observable_surface` 제거 · §1 prepare 포함 · §8 순서 |
| rv-D 2 | backstop 미포함 | **§0 집행 지점 이전** |
| rv-D 3 | digest·visual 소실 | **§0** |
| rv-D 4 | 한 줄 마스터키 | **§0-4 구조적 배제** |
| rv-D 5 | 규모가 hex 파편 | §2ⓒ [실측] |
| rv-D 6 | 12건이 한 키 | §2ⓑ [실측] |
| rv-D 7 | H1 앵커 = 파일 전체 | §2ⓓ-2 |
| rv-E 1 | 개명이 데이터 소실 | §4ⓒ **복사 방식** |
| rv-E 2 | #11 처분 거짓 | §4ⓓ 실제 수리 |
| rv-E 3 | backstop 미연결 | §0 |
| rv-E 4 | enum이 안 열림 | §4ⓔ 삭제 |
| rv-E 5 | 표 불일치 | §6 |
| rv-F 1 | «select만 누락» 거짓 | §5ⓐ [실측 교체] |
| rv-F 2 | 전역 링 정의 미탐 | §5ⓑ1 [실측 7종] |
| rv-F 3 | 합격 기준이 red 불가 | §8 표 |

---

## §10. 남는 위험

- **원장은 사용자가 승인하면 전부 연다.** 그게 지시다. 방어의 목표는 «사용자 모르게 열리는 것»을
  막는 것이다 — §0-4(구조적 배제) · §2ⓓ(앵커) · §2ⓒ(규모) · §3(천장) · §2ⓕ(지우면 닫힌다).
- **메시지 문구 개정 = 원장 무효.** fail-closed. 규범에 적는다.
- **`.input-field__control` 발견은 A8에 CSS 수정 부담을 만든다.** 결함이 맞으므로 그대로 낸다.

---

## §11. v5 개정 — 구현 감사(`impl-review/ir-1.md`)가 뒤집은 것

구현을 마친 뒤 독립 감사가 **v4의 방어를 실제로 우회**했다. 넷 다 실측이다.

### ⓐ 조회가 방어를 다시 보지 않았다 — 손으로 쓴 한 줄이 전부 열었다

v4의 방어는 전부 `ledger.py add`(CLI)에 있었고 조회 경로(`filter_issues`)는 다시 보지 않았다.
`valid_entries`가 «필드가 **있으면** 검사»였으므로 `{"key": "<16hex>"}` 한 줄이면 승인 근거 0으로
유효 행이 됐다 — 허용 목록·천장·앵커·관찰 지문이 전부 우회됐다.
«`ledger.py`만 쓴다»는 규범일 뿐 **기제가 아니었다.**

**v5**: `valid_entries`는 **fail-closed**다 — `key`·`label`·`kind`·`quote`·`scope_ref`·
`anchor_sha256`·`observation_sha256` 중 하나라도 없거나 어긋나면 그 행은 없는 것이다.
키가 `label`·`kind`에서 재계산돼야 하고, 앵커 절·원문·관찰 지문을 **조회 때마다** 다시 확인한다.

### ⓑ 문자열로 판정을 식별하면 사용자 데이터가 판정을 사칭한다

허용 목록을 정규식으로 맞췄더니, 검사기 메시지에 박히는 **에이전트 제어 문자열**(포인터 경로·
case id·표면 이름)로 판정을 훔칠 수 있었다. 실측: 관찰 경로를 `captures/잔여 1건 — none.json`으로
두면 «관찰 미실시» 발견이 «잔여» 판정으로 승격돼 §3 천장이 뚫렸다(규모도 `None`이라 영구 통행권).

**v5**: 문자열 매칭을 버린다. `check_design_evidence`가 **발견을 내는 그 자리에서**
`verdict(kind, message)`로 종류를 실어 보내고(`residual`·`exclusion_cap`·`surface`·`partial`),
원장은 그 종류만 받는다. 키도 `sha256(kind ∥ 정규화된 메시지)`다. 발견 출력은
`defect[<kind>]:`로 찍혀 `ledger.py add`가 같은 종류를 받는다.

### ⓒ 브라우저 채널이 없으면 재동결이 여전히 불가능했다

`_archive_observation_issues`가 `collection=archive`인 빌드에서 case마다 v2 관찰을 **무조건**
요구한다. 같은 원인(브라우저 부재)에 렌더 실측 축에는 합법 탈출구(`--render-audit-skipped`)가
있는데 조작 상태 축에는 없었다. 원장도 안 닿는다 — 이 발견은 `refreeze.py` 안에서 나고
검사기를 지나지 않는다. **구속 지시 정면 위반이다.**

**v5**: `check --observation-skipped <SKIP_REASONS enum>`을 둔다(렌더 실측과 같은 등급·같은 enum).

### ⓓ 벽을 없앤 자리에 표면이 0개였다

`begin`·`check`의 판독 실패를 journal에만 적었는데 journal은 완료와 함께 `_discarded-`로 들어간다.
불변식 II(«열린 길은 무엇이 미검증인지 지우지 못한다») 위반이다.

**v5**: `_finish`가 판독 실패·폐기 집합 보정·두 생략 사유를 `build-state.json`의
**`refreeze_unverified`**로 승격하고, `backstop.py`가 그 빌드에서 **매 실행 고지**한다.
미검증 원장 행 수도 같은 자리에서 고지한다.

### 회귀

`test_ledger.py` 103건(신설: 손으로 쓴 행 2종 · 경로 주입 · 단락 발견의 종류 부재 4종) ·
`test_refreeze.py` 45건(신설: 조작 상태 생략 2종 · `refreeze_unverified` 승격).
