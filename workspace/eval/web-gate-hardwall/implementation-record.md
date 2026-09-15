# 구현 기록 — 게이트 하드월 철거와 링 중첩 검사 (2026-09-15)

설계 정본: `workspace/design/2026-09-15-web-gate-hardwall.md` v4
적대 검토 8종: `design-review/rv-{A,B,C,D,E,F,G,H}.md` · 누적 **BLOCKER 42 · MAJOR 55 · MINOR 32**

## 절차 기록 (정직하게)

관례 절차([[web-repair-procedure]])는 «진단→설계→적대 검토→**계획→계획 리뷰**→구현→행동 시험→구현 리뷰→verify»다.
이번에는 **계획서와 계획 리뷰 단계를 건너뛰었다.** 대신:

- 설계를 **네 번** 고쳐 쓰고(v1·v2·v3·v4) 그때마다 **독립 적대 검토 3기씩**을 붙였다.
- 각 검토자에게 «설계 문서를 읽고 판단하라»가 아니라 **«원형을 만들어 실측하라»**를 요구했다.
  그 결과 검토가 계획 리뷰가 잡았을 것을 먼저 잡았다 — rv-E는 `_prev` 개명안의 데이터 소실을
  `test_refreeze.Fixture`로 **재현**했고, rv-G는 마스터키 공격을 **실행**해 발견 13→0을 측정했다.
- 구현자(나)도 검사기를 만들기 전에 **원형으로 A8 실물과 경계 판형 19종을 측정**했다.

계획서가 있었다면 설계 §의 재서술이 됐을 것이고, 이번 결함들은 문서를 읽어서는 안 나왔다.
다음 수리에서 같은 판단을 할지는 별개다 — **이 생략은 기록으로 남긴다.**

## 구현 내역

### 수리 A — 미검증 원장 (`ledger.py` 신설 · 349행)

| 결정 | 왜 |
|---|---|
| 집행 지점 = `validate_inputs`의 발견 확정 자리 | `main()`의 `except`는 `backstop.py`가 안 지나고(`backstop.py:30`이 `validate_inputs`를 직접 import), 거기서 exit 0을 내면 두 digest와 `validate_visual`이 통째로 사라진다 [rv-D 실측] |
| **허용 목록**(거부 목록 아님) | 거부 목록이면 `cases: []` 한 줄로 전부 열린다(발견 13→0 · digest_items 49→25). 단락 경로가 `validate_inputs` 안에만 25곳이라 열거가 불가능하다 [rv-G 실측] |
| 받는 판정 넷 | 잔여(`:974`) · 예외 10% 상한(`:897`) · 새 표면(`:960`) · partial/caps_hit(`:717`) — **검사기가 끝까지 계산한 뒤의 판정**만 |
| 규모 = 계수 단위 앞 첫 정수 | 모든 정수를 쓰면 hex id 파편 24/28이 섞이고, 둘째 정수(`활성 대상 M개`)는 커질수록 유리해 개선에도 재승인을 강요한다 |
| 키 정규화가 판정마다 다르다 | `잔여`는 튜플 목록을 접어야 안정되고, `새 표면`은 이름을 **남겨야** 승인 1건이 그 문서의 모든 표면을 열지 않는다 |
| 승인은 `scope.md` **H2 이상 절 본문** 안 | H1이면 절 본문 = 파일 전체다. 다른 문서 앵커는 거부 — 에이전트가 쓰는 문서로 승인을 위조할 수 없다 |
| 관찰 지문 | 규모 38→30이어도 **구성이 다르면** 승인이 아니다 |
| `add`의 자기 검증 | 등재 직후 재실행해 그 발견이 사라졌는지 확인하고, 안 사라지면 행을 철회한다 |
| 원장을 지우면 다시 막힌다 | 기록과 통행권이 같은 파일이다 |

**`legacy_v1_allowed`의 예외**(`backstop.py`): 원장·`_discarded-`를 「untracked 0」 판정에서 뺀다.
빼지 않으면 **원장을 적는 행위 자체가** legacy v1 유예를 뒤집어 «원장이 100% 거부하는 발견 13건»을
새로 세운다 [rv-H 실측]. 기록을 남길수록 길이 닫히면 아무도 남기지 않는다.

### 수리 B — 재동결 (`refreeze.py` · `backstop.py`)

- `begin`: 증거 판독 실패로 `return 1` 하던 것을 **journal `unreadable`에 적고 진행**.
  구현 중 **같은 이유의 두 번째 벽**(예외 목록 `load_json`)이 뒤에 숨어 있었고 시험이 잡았다.
- `check`: 같은 판정을 경고로 내리고, **폐기 집합을 보정한다**. 보정 없이 통과만 시키면
  «포인터가 빠졌다»가 세 번째 벽이 된다(시험이 잡았다).
- `_cleanup`·`abort`: 폐기분을 `_discarded-<ts>/`로 **복사** 보존. 개명안은 `_prev`의
  «commit 진행 중» 표식을 없애 재개가 live를 재폐기한다 [rv-E 재현]. 이름 충돌은 접미 카운터,
  복사 실패는 부분본을 지우고 경고만(백업은 차단 사유가 아니다).
- 잔존물 BLOCKER: `journal.json`이 없으면 **되감을 계획이 없다** → notice로 강등(유일한 문이
  `abort`인데 메시지는 `commit --resume`을 안내하고 있었다). 판정 범위를 `--design-build`로 한정.

### 수리 C — 링 중첩 (`check_focus_ring.py` 신설 · 267행)

사용자가 화면에서 본 **직각 이중 링**을 잡는다. 판정 7단계는 설계 §5ⓑ.
구현 전 원형으로 A8 실물 + 경계 판형 19종을 측정해 rv-F의 BLOCKER 2건(`:where` 타입 나열 미탐 ·
sr-only 오탐)을 먼저 닫았다.

## 시험

| 스위트 | 건수 | 무엇을 재는가 |
|---|---|---|
| `test_ledger.py` | **100** | 원장 개폐(검사기·backstop 양쪽) · 마스터키 거부 · 관찰/규모/절 무효화 · 키 분리. 부모 45건 상속으로 **기존 판정 무변경**도 함께 보증 |
| `test_refreeze.py` | 42 (신설 7) | 판독 실패 진행 · check 비차단 · `_discarded-` 보존과 재시작 · abort 백업 · 이름 충돌 |
| `fixtures_focus_ring.sh` | 18 | 이중 링·억제·은닉·타입 링·스코프·`:not`·자기 선언·«판정 안 함»·순서 함정 |
| `fixtures_backstop.sh` | 65 (신설 1·갱신 1) | 잔존물 두 갈래(journal 유/무) |
| 전체 `run_fixtures.sh` | **16파일 실패 0** | |

**시험이 잡은 실제 결함 3건**: ① 예외 목록 판독의 두 번째 벽 ② 폐기 집합 자기 검사의 세 번째 벽
③ 잔존물 루프의 `relative_to` 크래시(내가 `--design-build` 한정을 넣다 만든 것).

## 남긴 것 (별건)

설계 §6의 X 9건 — 대상 빌드에서 발화하지 않고 이번 합격 기준에 닿지 않는다.
안 쓰는 문을 여는 것은 게이트 완화이지 수리가 아니다. 진단서 «별건 대기 목록» 참조.

## 합격 기준 측정 (설계 §8) — 저장소 측

| # | 명령 | 기대 | 실측 |
|---|---|---|---|
| 1 | `run_fixtures.sh` | green | **16파일 실패 0** ✅ |
| 2 | `check_clip_clearance.py <A8 web>` | `.rpe-scroll` 4변 «확정» | 12건 · 4변 전부 «확정» ✅ |
| 3 | `check_focus_ring.py <A8 web>` | `select-field__select` 포함 · `input-field__input`·`textarea-field__input`·`choice-pair` 미포함 | 발견 3건(`select-field__control`×2 · `input-field__control`) · 미포함 **0건** ✅ |
| 4 | 같은 관찰 상태에서 원장만 토글 | 0행→exit 2 / N행→exit 0 · backstop 동조 | `test_ledger.py` 2건이 검사기·backstop 양쪽에서 재현 ✅ |
| 5 | `make verify` | green | **6/6 green (237초)** ✅ |

3번의 `.input-field__control`은 오탐이 아니다 — `login.html:50-56`의 trailing 아이콘 버튼이
억제 없이 전역 링을 받는다. A8 수정 대상은 **1계열이 아니라 2계열**이다(rv-F BLOCKER 1).

**A8 최종 검증은 배포 후다** — 설계 §8의 순서(부분 관찰 → 12건 닫힘 → prepare → coverage-review
재작성 → 잔여·상한 발견 → 원장 등재 → exit 0)를 A8 실물에서 밟는다. 원장만으로는 열리지
않는다. 그게 §3 천장의 의도다([[a8-final-testbed]]).

---

## 구현 감사 반영 (ir-1 · BLOCKER 4건)

감사가 **v4의 방어를 실제로 우회했다.** 넷 다 실측이고, 넷 다 «규범은 있는데 기제가 없다»였다.

| # | 감사가 연 것 | v5 |
|---|---|---|
| 1 | 손으로 쓴 `{"key": …}` 한 줄이 전부 열었다 — 방어가 `add`에만 있고 조회는 다시 안 봤다 | `valid_entries` **fail-closed** — 7필드 필수·키 재계산·앵커/원문/관찰 지문 매 조회 재확인 |
| 2 | 관찰 경로를 `captures/잔여 1건 — none.json`으로 두니 «관찰 미실시»가 «잔여»로 승격 | 문자열 매칭 폐기 — 검사기가 `verdict(kind, …)`로 **종류를 실어 보낸다**. 키 = `sha256(kind ∥ 정규화)` |
| 3 | 브라우저 없으면 재동결 자체가 불가 — 렌더 실측 축엔 탈출구가 있는데 조작 상태 축엔 없었다 | `check --observation-skipped <enum>` 신설(같은 등급·같은 enum) |
| 4 | 벽을 없앤 자리에 표면 0개 — journal은 완료와 함께 `_discarded-`로 들어간다 | `build-state.refreeze_unverified`로 승격 + `backstop`이 매 실행 고지 |

**#2가 가장 중요한 교훈이다.** 검사기 메시지에는 에이전트가 정하는 문자열이 그대로 박힌다 —
경로·case id·표면 이름. 그 메시지를 **문자열로 분류하면 사용자 데이터가 판정을 사칭한다.**
판정은 그것을 내린 자리에서 태깅해야 한다.

최종 회귀: 원장 **103** · 재동결 **45** · 링 18 · backstop 65 · `run_fixtures` 16파일 실패 0.

---

## 후속 — 검사기 주석 오탐 (2026-09-16 · v1.1.18)

배포 다음 날 A8 세션이 보고했다: `check_focus_ring`·`check_clip_clearance`가 **Django 주석
속 리터럴 태그를 실제 요소로 셌다**. A8은 통과시키려고 부품 docstring을 훼손했다.

```diff
-    href      — 지정 시 <a> 링크로 렌더 (glass back email 단계)
-    hx_get    — 지정 시 <button> HTMX 트리거 (glass back code/password 단계)
+    href      — 지정 시 a 링크로 렌더 (glass back email 단계)
+    hx_get    — 지정 시 button HTMX 트리거 (glass back code/password 단계)
```

**내 결함이다.** 오탐 자체보다 나쁜 건 그 오탐이 **소스를 도구에 맞춰 훼손하게 만들었다는
것**이다 — 도구가 산문을 코드로 읽으면 사람은 산문을 지운다. 진단 때 나는 같은 자리를
`login.html`의 무클래스 `<button>`으로 보고 «표시 문제»로 넘겼다. 동료 보고가 그걸 뒤집었다.

수리: `template_graph`가 본문을 읽는 **한 자리**에서 `strip_comments()`를 통과시킨다
(`{% comment %}`·`{# … #}` · 줄 수 보존). `check_focus_ring`이 `template_graph`를
import하므로 두 검사기가 한 수리로 낫는다.

| 확인 | 결과 |
|---|---|
| A8 web 사본 + **원래 주석 복원**(`git show HEAD:…/icon_button.html`) | `[focus-ring] 발견 0건 · exit 0` ✅ |
| 회귀 FR14(주석 속 `<a>`·`<button>`·`<select>`) | PASS · 링 19건 ✅ |
| 회귀 CC11(주석 속 `<input>` 리터럴) | PASS · 절단 24건 ✅ |
| `run_fixtures.sh` 16파일 | 실패 0 ✅ |
| `make verify` | **6/6 green (237초)** ✅ |

A8은 주석을 원복했다.

---

## 후속 2 — 재동결 중단의 보존 누락 (2026-09-16 · v1.1.19)

A8이 «정상 abort 경로엔 `_discarded-` 복사가 없더라»를 보고했다. 내 첫 반응은 «staging은
사본이라 잃을 게 없다»였고 **그것도 틀렸다.**

| | |
|---|---|
| `cmd_begin`이 staging에 넣는 것 | `INPUT_GLOBS` 3종뿐 |
| `cmd_check`가 staging에서 **찾는** 것 | `REQUIRED_STAGING` 5종 · `design-ref/` · `render-audit.json` · 관찰 문서 |

즉 staging은 백업이 아니라 **재동결 산출물이 쌓이는 자리**다. `_rewind`도 설치분을 staging으로
되돌린 뒤 지우므로 같은 성질이다. **완료 폐기(`_cleanup`)와 journal 없는 잔존물은 보존하는데
가장 많이 버리는 이 자리만 보존하지 않았다.** 원인은 범위 착오 — 설계 §ⓒ 제목이
«**`_prev`** 한 세대 보존»이라 rv-E가 재현한 «개명이 표식을 없앤다»만 고치고 멈췄다.

### 재현 (코드 독해가 아니라 실측)

`RefreezeTestCase`를 그대로 써서 begin → staging에 산출물 3개 작성 → abort:

```
abort 직전 staging 파일 6개
staging 존재?  False
_discarded-*:  없음          ← R1
살아남은 산출물: 0개
```

수리 뒤 같은 재현: `_discarded-20260916-024636` · **살아남은 산출물 6개.**

### 적대 검토 — «기록을 남기는 행위가 새 벽을 세우는가»

v1.1.17에서 나를 문 함정(빌드 폴더 untracked가 `legacy_v1_allowed`를 뒤집는다)을 같은 자리에서
다시 봤다. 넷 다 통과:

| 물은 것 | 답 |
|---|---|
| `orphan_set`이 `_discarded-` 안을 고아로 세는가 | 아니다 — `build/captures`만 훑는다(`:203-212`) |
| `legacy_v1_allowed`의 «untracked 0»을 깨는가 | 아니다 — `GATE_BOOKKEEPING_DIRS = ('_discarded-',)` |
| 잔존물 BLOCKER를 새로 세우는가 | 아니다 — 접두가 `('_refreeze-','_prev-')`뿐(`backstop:335`) |
| 다음 `begin`을 «진행 중»으로 막는가 | 아니다 — glob이 `_refreeze-*`·`_prev-*`뿐 |

자기 정정: `backstop.py:348`의 «내용은 `_discarded-<ts>/`로 한 세대 보존된다»를 **거짓 약속으로
의심했으나 아니었다** — 그 문구는 journal 없는 분기의 것이고 그 분기는 실제로 보존한다.

### 같이 고친 것 — 재동결 중 승인 절의 자리 (R2)

원장은 승인 원문을 `build/scope.md`의 H2 앵커에서 읽고(`ledger.py:222-226`), `cmd_commit`은
**live** `scope.md`가 begin 이후 바뀌면 교체를 거부한다(`refreeze.py:547-550`). 그래서 재동결
중에 live를 고치면 교체가 막히고, staging에만 쓰면 교체 전까지 행이 무효다 — **순서가 서로를
막는다.** 깨지지 않는 길(staging에 쓰고 `--build <staging>`으로 등재)이 어디에도 문서화돼
있지 않았다. `design-evidence.md`·`design-acquisition.md`에 명문화했다.

### 후보에서 뺀 것

**v2 case 계약 문서화 부족** — A8이 `source_observation`의 2단 간접을 틀렸기에 문서 결함을
의심했으나, `design-evidence.md:162-177`이 관찰 문서 구조를 **정확히** 싣고 있었다. 참조
미열람이지 결함이 아니다. 고치지 않았다.

### 시험

`test_refreeze` **45 → 47**(정상 abort 보존 · `_rewind` 경로 보존) · `run_fixtures` 16파일 실패 0 ·
Codex 미러 4파일 byte 동일.
