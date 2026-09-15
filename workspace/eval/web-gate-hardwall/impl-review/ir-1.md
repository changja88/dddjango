# ir-1 — 게이트 하드월 철거 구현 감사 (독립·적대)

등급: BLOCKER 4 · MAJOR 11 · MINOR 8

대상: 작업 트리 `/Users/hyun/Desktop/dddjango` (2026-09-15 23:23~23:35 상태 · 감사 중 무변경 확인 —
`ledger.py` sha `73ea2558…` · `check_focus_ring.py` `1d653564…` · `backstop.py` `5d77fc5d…` ·
`refreeze.py` `de1724c0…` · `check_design_evidence.py` `d9a739bb…`, 시작·종료 시각 동일).
방법: 정본을 **읽기 전용**으로 호출하고, 쓰기가 필요한 공격·변이는 scratchpad 사본에서 했다.
정본 `dddjango-web/`·`codex-dddjango-web/`은 수정하지 않았다. Codex 미러 10개 파일 byte 동일 확인.
표기: **[실측]** = 이번 감사에서 명령을 돌려 얻은 출력 · **[확인]** = 코드 직독.

먼저 **green**부터: `test_ledger.py` 101건 OK · `test_refreeze.py` 42건 OK ·
`fixtures_focus_ring.sh` 18/18 · `fixtures_backstop.sh` 65/65 · `web_refreeze_contract.py` A·B·C·D1~D4 green.
A8 실물 `check_focus_ring.py` → **exit 2 · 발견 3건**(`.select-field__select` ×2 포함 ·
`.input-field__control` 포함 · `input-field__input`·`textarea-field__input`·`choice-pair` 미포함) —
설계 §8 기준 3의 포함/미포함 목록을 **글자 그대로 충족**한다 [실측]. 0.09초.

---

## 0. 선행 BLOCKER 13건 대조

| # | 출처 | 요지 | 판정 | 근거 |
|---|---|---|---|---|
| 1 | rv-G 1 | §0-4 «구조적 배제» 거짓 — `issues` 묶음 안 마스터키 | **안 닫힘** | 허용 목록 전환으로 `ledger.py add` 경로는 막힌다(`cases: []` → add exit 2 [실측]). 그러나 ⓐ 손으로 쓴 원장 1행이 그 발견을 그대로 연다(BLOCKER 1) ⓑ `잔여` 패턴 주입으로 단락 발견이 열린다(BLOCKER 2) — 둘 다 발견 전량 → 0 · exit 0 [실측] |
| 2 | rv-G 2 | §3 천장 열거식 — «관찰 안 함»이 다른 문구로 통과 | **안 닫힘** | `refusal()`(ledger.py:138-148)이 **허용 목록을 천장보다 먼저** 본다. 경로에 «잔여 1건 — »을 심은 `missing path` 발견이 ADMITTED가 되어 `add` exit 0 · 게이트 exit 0 [실측] |
| 3 | rv-G 3 | 원장 경유 exit 0이 `review_digest`·`input_digest`를 오염 | **부분** | 허용 목록 4종은 완주 후 판정이라 정상 경로 오염은 없다. rv-G 수정 방향 ①(digest에 원장 섞기)·②(prepare에도 표식)·③(digest_items 수)은 **하나도** 미이행 — BLOCKER 2 경로에서 `review_digest` 오염 + `prepare` 출력에 원장 표식 0 [실측] |
| 4 | rv-G 4 | 잔여 «구성»이 바뀌어도 규모만 작으면 통과 | **부분** | `observation_sha256` 지문으로 **잔여 축은 닫힘** [실측 — «관찰이 바뀌었다» 무효화]. `예외 상한` 행은 구성이 전부 달라도 같은 키·같은 규모로 유효(MAJOR 7) |
| 5 | rv-G 5 | 따옴표 삭제로 서로 다른 발견이 한 키 | **닫힘** | `새 표면` fold=(COUNT_RE,)로 표면 이름 보존 [확인 ledger.py:82]. `:1221`·`:196`은 허용 목록 밖이라 애초에 원장 대상이 아니다 |
| 6 | rv-G 6 | `validate_visual`이 원장 밖 | **부분(형식만)** | 호출은 배선됐다(check_design_evidence.py:1353). 그러나 visual 발견 전종이 허용 목록 밖이라 **항상 no-op**다 — `visual cases[0].result: pass required` refusal 확인 [실측]. §6 #19 «원장이 대체 채널»은 여전히 거짓(MAJOR 11) |
| 7 | rv-G 7 | 앵커 «파일»을 못 박지 않음 | **부분** | `SCOPE_DOCUMENT='scope.md'` 고정·H2 이상·제목 앵커만(`section_of`가 `<a id>`를 안 본다) [확인·실측 add exit 2]. rv-G ③ «같은 앵커·인용을 두 행 이상이 공유 금지»(인용↔발견 결속)는 미구현 — 같은 quote로 임의의 행을 계속 등재할 수 있다 |
| 8 | rv-H 1 | `legacy_v1_allowed` git 상태 의존 — 원장 파일이 13건을 세운다 | **부분(코드 닫힘·시험 0)** | `_gate_bookkeeping`(backstop.py:132-139)으로 `evidence-ledger.json`·`_discarded-*` 예외 [확인]. **회귀 시험 0건** — `grep -rn "evidence-ledger\|_gate_bookkeeping" scripts/test/` 결과 `test_ledger.py`의 파일 읽기 2줄뿐 [실측] (MAJOR 8) |
| 9 | rv-H 2 | §4ⓐⓑ가 대체 표면 0개 — 불변식 II 위반 | **안 닫힘** | `journal['unreadable']`의 소비자가 여전히 `cmd_check`의 print뿐이다. `grep -rn "unreadable\|판독 실패" backstop.py evidence_debt_hook.py commands/*.md agents/*.md docs/DEVELOPMENT.md` → **해당 0건** [실측]. commit 완료 보고도 `'[refreeze] 교체 완료'` 한 줄(refreeze.py:585) (BLOCKER 4) |
| 10 | rv-H 3 | `abort`의 journal 없는 rmtree가 백업 밖 | **닫힘** | `cmd_abort`에 `_preserve` 삽입(refreeze.py:704) + 회귀 1건. 변이 시험(그 줄 제거) → `test_abort_backs_up_journalless_leftover_before_deleting` red [실측] |
| 11 | rv-H 4 | rv-B #21 — 브라우저 없으면 재동결 자체가 불가 | **안 닫힘** | `_archive_observation_issues`(refreeze.py:475-)가 무변. staging 관찰을 v1으로 두면 `check` exit 3 · `commit` exit 1 · `--render-audit-skipped 브라우저 채널 부재`로도 안 열린다 [실측] (BLOCKER 3) |
| 12 | rv-H 5 | §7에 `web_refreeze_contract.py` 없음 · D1 red | **부분** | `--build <대상 폴더>` 표기로 D1 green [실측]. 그러나 rv-H ②(«원장 파일의 재동결 중 거처»)는 미규정 — `evidence-ledger.json`이 `INPUT_GLOBS`·`FIXED_DISCARD_FILES` 어디에도 없어 재동결이 staging으로 옮기지도 폐기하지도 않는데 규범은 재동결 중 staging을 `--build`로 주라고 한다(MINOR 2 파생) |
| 13 | rv-H 6 | §8에 §4를 재는 행 0개 | **부분** | `HardwallTests` 6건 신설. 그러나 §4ⓒ의 **중심 주장(«개명이 아니라 복사»)을 재는 시험이 없고**, `commit --resume`을 한 번도 안 부르며, 복사 실패 주입 행이 없다 [실측 변이 M2] (MAJOR 10) |

**닫힘 2 · 부분 6 · 안 닫힘 5.**

---

## 1. BLOCKER

### [BLOCKER] 손으로 쓴 `evidence-ledger.json` 한 줄이 **모든** 발견을 연다 — 허용 목록·천장·앵커·관찰 지문을 전부 우회한다

**무엇이 틀렸나.** 방어는 전부 `ledger.py add`(CLI)에만 있다. 조회 경로인 `filter_issues`
(ledger.py:249-264)는 `admitted()`도 `refusal()`도 **다시 보지 않고**, `valid_entries`
(ledger.py:218-246)는 `scope_ref`·`anchor_sha256`이 **문자열이 아니면 그 검사를 통째로 건너뛴다**
(`if isinstance(reference, str) and isinstance(anchor_hash, str):` — ledger.py:224).
`observation_sha256`도 같은 판형(`:241`)이다. 즉 `{"key": "<16hex>"}` 한 줄이면 승인 근거 0으로
유효 행이 된다. 설계 §2ⓐ의 «`ledger.py`만 쓴다 — 에이전트 직접 편집 금지»는 **규범일 뿐 기제가 없다.**

**근거 [실측]** — 합성 빌드(`test_interaction_evidence` 하네스), 정본 스크립트 그대로:
```
① cases: []  → 발견 1건 «cases: nonempty list required»
   evidence-ledger.json = {"version":1,"entries":[{"key": key_of(그 메시지)}]}
   → --phase prepare  exit 0   {"review_digest": "e87c007a…"}
   → backstop.py --design-build …  «cases: nonempty list required» BLOCKER **소멸**
② 관찰 파일을 치운 뒤 같은 방식
   → 발견 «cases[0].source_observation.path: missing path (…)»  → exit 0 · 발견 0
   stderr: [design-evidence] 미검증(원장): cases[0].source_observation.path: missing path …
```
①은 rv-G BLOCKER 1이 실측한 «발견 13 → 0 · digest_items 49 → 25» 마스터키 그 자체이고,
②는 §3 천장 1행(«관찰 자체를 안 했다»)이다. 둘 다 `ledger.py add`로는 exit 2로 막히지만
(그 점은 시험이 잡는다) **파일을 직접 쓰면 둘 다 열린다.** 사용자 기준 ②(부정직한 길이 가장 싸다) ·
④(검증이 조용히 사라진다)에 정확히 해당한다 — `{"key":…}` 한 줄을 쓰는 것보다 싼 길은 없다.

**수정 방향.** 조회에서 다시 본다. `filter_issues`가 행마다 ⓐ `admitted(entry['label'])`가 참이고
ⓑ `key_of(entry['label']) == entry['key']`이고 ⓒ `scope_ref`·`anchor_sha256`·`observation_sha256`·
`quote`가 **필수로 실재**하고 ⓓ 인용이 그 앵커 절 본문 안에 있음을 확인한 행만 살린다.
지금처럼 «필드가 있으면 검사»가 아니라 «없으면 무효»(fail-closed)여야 한다. 회귀 2건
(손으로 쓴 최소 행 · 필드를 지운 행)을 `test_ledger.py`에 넣는다.

---

### [BLOCKER] `잔여` 허용 패턴이 무앵커라 **경로 문자열 주입**으로 §3 천장과 구조 단락 발견이 열린다

**무엇이 틀렸나.** `ADMITTED`의 네 판형 중 셋은 앵커가 있는데(`^…$` 또는 `…$`)
`("잔여", re.compile(r"잔여 \d+건 — "), …)`(ledger.py:85)만 **양쪽 무앵커에 `.search`**다.
그리고 `refusal()`(ledger.py:138-148)은 **허용 목록을 천장보다 먼저** 본다:
```python
if admitted(message) is not None:
    return None                    # ← 여기서 끝난다
if "interaction evidence required" in message: ...
if message.startswith("coverage_review:"): ...
```
따라서 메시지 **어디에든** «잔여 N건 — »이라는 글자가 들어가면 그 발견은 허용 목록으로 승격되고
천장 2행도 무력해진다. 검사기 메시지에는 에이전트가 정하는 문자열(포인터 경로·case id·표면 이름)이
그대로 박힌다.

**근거 [실측]** — `design-input.json`의 `cases[0].source_observation.path`를
`"captures/잔여 1건 — none.json"`(없는 파일)으로 바꾼 것 하나:
```
발견 1: admitted=잔여 | cases[0].source_observation.path: missing path ([Errno 2] … '…/잔여 1건 — none.json')
python ledger.py add --index 1 --quote "<scope.md 의 진짜 승인 원문>" --scope-ref scope.md#관계-메뉴
  → rc 0  «등재했다: eedc9e89fabd67d1 · 규모 None»      ← 자기 검증도 통과
--phase prepare → exit 0 · 남은 발견 0건
```
효과는 세 겹이다. ① §3 천장이 지키려던 «관찰 미실시»가 열린다 — `_source_observation`이 `None`을
반환해 그 case의 `validate_interactions` 전량(잔여·표면·미디어·archive 의존성)이 **계산조차 되지 않는다**.
② `규모 None`이라 규모 천장도 없다 — 영구 통행권이다.
③ 같은 상태에서 `digest_items`가 줄어 `review_digest`가 바뀌는데(정상 16항목 → 축소, `e5b60ed4…` →
`59a9ddf6…`) `prepare` 결과 JSON에 **원장 표식이 하나도 없다**(`unverified_ledger` 미포함) [실측] —
그 값을 `coverage-review.md`에 받아 적으면 `inputs`도 닫힌다. rv-G BLOCKER 3이 그대로 산다.

파일 이름을 바꾸는 것이 드라이버를 잇는 것보다 압도적으로 싸다 — 사용자 기준 ②.

**수정 방향.** ① `refusal()`의 순서를 뒤집어 **천장을 먼저** 본다. ② 네 패턴을 전부
«메시지 전체» 앵커로 바꾼다(`잔여`는 `^cases\[.*\]\.interactions\(.*\): (partial\(caps_hit=.*\) 수집인데 )?잔여 \d+건 — `).
③ 더 근본적으로는 문자열 매칭을 그만두고 검사기가 발견을 낼 때 판정 종류 태그(`kind='residual'` 등)를
같이 실어 보낸다 — 그러면 사용자 데이터가 판정을 사칭할 수 없다. ④ 회귀 3건
(경로 주입 · case id 주입 · 표면 이름 주입)을 `test_ledger.py`에 넣는다.

---

### [BLOCKER] 브라우저 채널이 없으면 **재동결이 여전히 불가능**하다 — 구속 지시 정면 위반, rv-H BLOCKER 4가 손도 안 댔다

**무엇이 틀렸나.** `_archive_observation_issues`(refreeze.py:475-)가 `collection=='archive'`인 모든
빌드에서 case마다 `version == 2 and 'interactions' in document`를 **무조건** 요구한다. 코드는 이번
변경에서 한 줄도 바뀌지 않았고, 설계 §6 처분 표 20행에도 없으며 §7 배선표에도 없다.

**근거 [실측]** — staging 관찰을 v1(=드라이버 미연결)로 두고:
```
[refreeze] screen/list: 조작 상태 관찰(v2)이 없다
check  exit = 3
check --render-audit-skipped "브라우저 채널 부재"  exit = 3     ← 탈출구가 안 통한다
commit exit = 1   ([refreeze] check 를 통과하지 않았다 …)
SKIP_REASONS = ('원본 열람 불가', '필요한 인증 상태 접근 불가', '브라우저 채널 부재')
```
같은 원인(브라우저 부재)에 대해 렌더 실측 축에는 합법 탈출구가 있고 조작 상태 관찰 축에는 없다.
원장도 닿지 않는다 — 이 발견은 `refreeze.py` 안에서 나고 `check_design_evidence`를 지나지 않는다.
구속 지시 «재동결하라고 하고 차이점이 있으면 수정을 하게 하면 된다. 이게 무슨 이유로든
**불가능해지는 거 자체가 말이 안 된다**»가 이 축에서 그대로 깨져 있다.

**수정 방향.** ① `cmd_check`의 이 발견을 `--render-audit-skipped`와 **같은 등급의 명시 사유**로
낮추고(`--observation-skipped <SKIP_REASONS 중 하나>`) journal에 적는다. ② 그 사실을 commit 완료
보고·G0 배너에 1급으로 낸다(아래 BLOCKER 4와 같은 표면). ③ 열지 않기로 한다면 §6에 «X + 사유»로
적고 구속 지시와의 충돌을 §10에 올린 뒤 사용자에게 명시적으로 확인받는다 — 지금은 표에 없어서
«판단했는데 남긴 것»인지 «잊은 것»인지 구별되지 않는다.

---

### [BLOCKER] §4ⓐⓑ가 벽을 없애면서 **대체 표면을 0개** 만든다 — 불변식 II(«열린 길은 무엇이 미검증인지 지우지 못한다») 위반

**무엇이 틀렸나.** `begin`은 판독 실패를 `journal['unreadable']`에 적고 진행하고(refreeze.py:349-352,
366-370), `check`는 경고만 내고 **폐기 집합을 조용히 «보정»**한다(refreeze.py:448-459).
그런데 `unreadable`을 읽는 소비자가 여전히 하나도 없다.

**근거 [실측]**
```
$ grep -rn "unreadable|판독 실패|폐기 집합 미확정" \
    dddjango-web/scripts/backstop.py dddjango-web/scripts/evidence_debt_hook.py \
    dddjango-web/commands/dddjango-web.md dddjango-web/agents/*.md docs/DEVELOPMENT.md
  → 해당 0건 (evidence_debt_hook:156 의 unreadable 은 수집기 카운터로 무관)
$ grep -n "교체 완료" refreeze.py   →  585:  print('[refreeze] 교체 완료')
```
그리고 `_finish`가 journal을 `_prev`에만 쓰고 `_cleanup`이 `_prev`를 지우므로, 커밋 이후 그 사실은
`_discarded-<ts>/journal.json` 안에만 남고 **아무도 읽지 않는다.**

실제 진행을 재현하면 [실측]:
```
begin: unreadable=2 · discard_set=10
check: 경고 2줄 + «폐기 집합을 보정했다» 6줄 → rc 0 · 폐기 16건
commit: [refreeze] 폐기분을 _discarded-…/ 에 … / [refreeze] 교체 완료  → rc 0
```
사용자·다음 세션이 보는 최종 산출물 어디에도 «이 재동결은 그만큼 불완전했다»가 없다.
§2ⓕ가 원장에 대해 «기록과 통행권이 같은 파일»을 세운 것과 정확히 대비된다 — 여기엔 기록이 없다.
사용자 기준 ④(검증이 조용히 사라진다).

**참고(안전한 쪽).** 보정 자체는 위험하지 않다 — commit의 `verified` 단계가 `check_design_evidence`를
다시 돌리므로 잘못 보정하면 `_rewind`로 되감긴다. 위 실측에서 `_discarded-` 18파일 완전본·live 정상 [실측].
문제는 **안전성이 아니라 침묵**이다.

**수정 방향.** ① `journal['unreadable']`·`discard_amended`가 비어 있지 않으면 commit 완료 보고에
«폐기 집합 미확정/보정 N건 — 이 재동결은 그만큼 불완전하다»를 낸다. ② `build-state.json`에 그 사실을
남겨 `backstop.py`가 매 실행 notice 1줄로 낸다(원장 notice와 같은 등급 — MAJOR 6과 한 자리에서 고친다).
③ `_discarded-<ts>/`에 그 목록을 별도 파일로 동봉한다. ④ 회귀 1건(«unreadable 1건을 넣으면 마무리
보고에 1줄이 뜬다»)을 `test_refreeze.py`에 넣는다.

---

## 2. MAJOR

### [MAJOR] `_cleanup`이 멱등하지 않다 — 복사 직후 중단 뒤 `--resume`이 **두 번째 전체 사본**을 만든다

`_preserve`(refreeze.py:640-663)를 `_cleanup`(:666-668) 진입 직후 조건 없이 부르는데,
`cmd_commit`의 done-재개 분기(:550-553)가 `_cleanup`을 다시 부른다.

**근거 [실측]** — `_preserve` 직후 중단 주입:
```
중단 직후 잔존: ['_discarded-20260915-233019', '_prev-…', '_refreeze-…']
commit --resume rc=0
_discarded = [('_discarded-20260915-233019', 20), ('_discarded-20260915-233019-2', 20)]
```
rv-H MAJOR가 예고한 그대로다(A8 최대 빌드 기준 55 MiB). 더 나쁜 것은 `test_preserve_never_collides`가
이 비멱등성을 **단언으로 못 박았다**는 점이다(`self.assertEqual(len(self.discarded()), 2)`).

**수정 방향.** 백업 폴더에 출처(`_prev` 이름 또는 `swap-plan.json`의 `prev`)를 한 줄 남기고,
같은 출처의 백업이 이미 있으면 건너뛴다. 시험은 «같은 세대는 한 번만»으로 뒤집는다.

### [MAJOR] Ctrl-C 중 **부분 백업이 완전본과 구별되지 않는다** · 복사 실패 시 `_prev`도 함께 사라진다

`_preserve`는 `except OSError`에서만 부분본을 `rmtree`한다(:659-662). `KeyboardInterrupt`는 안 잡는다.

**근거 [실측]** — copytree 4파일째에서 `KeyboardInterrupt`:
```
_discarded-20260915-233033 = ['asset-manifest.json','captures/screen-initial.png','captures/screen-interactions.json']
  (완전본은 18파일) · «부분»을 알리는 표식 = 없음 · 이름·구조 동일
_prev 는 남아 있다 → 이어서 --resume 하면 완전본 «-2» 가 옆에 생긴다(위 MAJOR)
```
그리고 `OSError(28)` 주입 시 [실측]: `commit rc=0` · `_discarded` **0개**(부분본 삭제) ·
**`_prev`도 삭제됨** · live=NEW — 즉 «한 세대 보존»이 조용히 실패하고 원본도 사라진다.
기준선도 `_prev`를 지웠으므로 회귀는 아니지만, §4ⓒ가 약속한 것이 실패했다는 사실이 남지 않는다.
rv-H MAJOR의 수정 방향 ①(`.partial/` 후 rename)·②(실패 시 `_prev` 보존)는 둘 다 미채택이다.

**수정 방향.** `_discarded-<ts>.partial/`에 복사하고 성공 시에만 rename한다(중단·실패 모두 이름으로
구별된다). 복사가 실패하면 `_prev`를 지우지 않는다. 회귀 2건(OSError 주입 · 중단 주입).

### [MAJOR] 완료 직후 중단 상태에서 `abort`가 **완료된 재동결을 되감는다** — §4ⓓ②의 «journal 유무» 분기가 이 상태를 못 가른다

`cmd_abort`의 journal 탐색이 `staging → prev` 순이고(refreeze.py:695-697) `completed_at`은
`_finish`가 `prev/journal.json`에만 쓴다(:681).

**근거 [실측]** — `_finish` 직후 `_cleanup` 진입에서 중단:
```
잔존: ['_prev-20260915-233019', '_refreeze-20260915-233019']
_prev/journal.completed_at = 2026-09-15T23:30:19+09:00
abort rc = 0 · live design-ref = b'<html>original</html>'   ← 완료본이 통째로 되감겼다 · _discarded 0개
```
선행 결함이지만 v4가 둘을 더했다. ① `_cleanup`의 중단 창이 두 `rmtree`에서 «전량 복사 시간»으로
넓어졌다(A8 3.6~34 MiB). ② 이 상태의 두 폴더는 **모두 journal이 있으므로** backstop이
«commit --resume (완료 전이면 abort)»를 그대로 내고(backstop.py:314-316), 사용자가 abort를 고르면
완료본이 사라진다 — §4ⓓ②가 문구에 넣겠다던 분기가 들어가지 않았다.

**수정 방향.** journal 탐색을 `prev → staging`으로 뒤집거나 두 journal의 `completed_at`을 모두 본다.
backstop 문구의 분기 축을 «journal 유무 · `completed_at` 유무» 2축으로 만든다. 회귀 1건
(«완료 직후 중단에서 `abort`는 exit 1»).

### [MAJOR] `check_focus_ring`이 **주석 안의 태그를 발견으로 낸다** — 그리고 그 가짜가 대표가 되어 진짜 결함 상세를 가린다

`clip.expand`도 `check_focus_ring`도 `{% comment %}`·`<!-- -->`를 제거하지 않는다.

**근거 [실측]** — 합성 최소 판형(scratchpad):
```html
<div class="wrap">
  <!-- <select> 는 쓰지 않는다 -->
  <span>텍스트만 있다</span>
</div>
→ [FINDING] a.css :: .wrap 안의 면제 없는 포커스 대상 — p.html <select> …   exit 2
```
A8에서 **이미 발화 중**이다 [실측] — `.input-field__control` 발견의 대표 요소로 뽑힌
`login.html <button>`은 include된 `icon_button.html`의 `{% comment %}` 안 문장
«hx_get — 지정 시 `<button>` HTMX 트리거»다(blob offset 1296). 진짜 대상은 그 뒤의
`<a class="icon-button …">`·`<button class="icon-button …">` 3건인데, 중복 제거가 (K, 템플릿)이라
전부 «외 N건»으로 접히고 **이름이 안 나온다**. 그래서 출력이
«안쪽 radius 미상(리터럴 클래스 없음 — 모서리는 육안)»이 되어, 설계 §5ⓐ·§10이 예고한 실제 상세
(`.icon-button` = `--radius-pill` vs 래퍼 18px «모서리 불일치»)가 **한 번도 인쇄되지 않는다**.
선검증 문서의 1차 예상 출력(«radius 0 vs 999px — 직각 링»)과도 다르다.
픽스처에 주석 판형이 **0건**이다(`grep -n "comment\|<!--" fixtures_focus_ring.sh` → 없음).

**수정 방향.** `read`/`expand` 단계에서 `{%\s*comment\s*%}…{%\s*endcomment\s*%}`와 `<!-- … -->`를
제거한다(`check_clip_clearance`와 공유). FR 픽스처 2건(템플릿 주석 · HTML 주석) 추가.

### [MAJOR] «외 N건»이 **CSS 규칙 수만큼 부풀고**, 선검증이 확정한 중복 제거 키가 후퇴했다

선검증 §«판정 규칙 확정» 6은 «중복 제거 = (K, 템플릿, **요소 오프셋**)»인데 구현은
`key = (name, template.name)`(check_focus_ring.py:252)이다. 그리고 바깥 루프가
`sorted(set(wrappers))`(:234)를 도는데 `wrappers`의 원소는 `(css 파일, member, 클래스)`라
**같은 클래스가 두 CSS 규칙에 있으면 같은 템플릿을 두 번 훑는다.**

**근거 [실측]** — A8:
```
wrappers = … ('components.css','.input-field__control:focus-within','input-field__control')
            ('user_info.css','.user_info__field .input-field__control:focus-within','input-field__control')
login.html 실제 미면제 대상 = 4건, 출력 = «외 7건» (= 4 × 2 − 1)
```
선검증 1차 원형의 출력은 «외 3건»(정확)이었다 — 구현에서 되레 나빠졌다.
선검증 §ⓒ가 «CSS 파일 수만큼 부풀면 안 된다»고 못 박은 바로 그 항목이다.

**수정 방향.** 바깥 루프를 클래스 집합(`wrapper_names`)으로 돌고, `seen` 키에 요소 오프셋을 넣는다.
DET 픽스처에 «같은 클래스 2규칙 → 건수 불변» 단언을 추가한다.

### [MAJOR] `backstop.py`가 설계 §2ⓕ의 **원장 notice를 내지 않는다** — 규범이 «1급 의무 표기»라고 적은 줄의 유일한 기계 근거가 없다

설계 §2ⓕ: «`backstop.py`는 원장이 비어 있지 않은 동안 **매 실행 notice 1줄**을 낸다».
`commands/dddjango-web.md`: «그 줄과 `ledger.py list`의 유효 행 수는 G0·G1·G2 배너와 마무리 보고의
**1급 의무 표기**다». 구현에서 `backstop.py`의 원장 언급은 `GATE_BOOKKEEPING` 상수뿐이다
(`grep -n ledger backstop.py` → :132 한 줄) [실측].

**근거 [실측]** — 원장에 유효 행 1개를 두고 지금은 그 발견이 없는 상태:
```
prepare rc=0  stdout={"review_digest": …}                  · stderr 원장 줄 0
inputs  rc=0  stdout=… "unverified_ledger": "[{…}]"        · stderr 원장 줄 0
backstop rc=2 · 출력에 '원장'·'ledger'·'미검증' 0건
```
지금 backstop이 원장을 언급하는 유일한 경우는 **이번 실행에서 실제로 행이 발견을 열었을 때**
`_ledgered`가 stderr로 내는 `[design-evidence] 미검증(원장): …`뿐이다. 즉 «과거에 승인받은 미검증
부채가 아직 남아 있다»는 사실은 마무리 backstop에서 보이지 않는다.

**수정 방향.** `main()`의 design 구간에서 `ledger.valid_entries(build)`를 불러
`ctx.notices.append('[info] 미검증 원장 N행 — …')`을 무조건 낸다(0행이면 침묵 또는 «없음»).
`fixtures_backstop.sh`에 회귀 1건.

### [MAJOR] `예외 상한` 행은 **구성이 전부 바뀌어도** 같은 키·같은 규모로 살아 있다 — 관찰 지문이 이 축에 닿지 않는다

`("예외 상한", r"^interaction_exclusions: 예외 \d+행은 활성 대상 \d+개의 10% 상한을 넘는다$", (COUNT_RE,))`
는 정규화 후 **상수 문자열** 하나가 된다.

**근거 [실측]**
```
key_of('… 예외 5행은 활성 대상 60개 …') == key_of('… 예외 5행은 활성 대상 90개 …')  → True (6922fca2a75855c1)
magnitude 5 == 5
```
`observation_sha256`는 `cases[*].source_observation` 하위의 sha만 접으므로
`interaction_exclusions`(design-input.json의 다른 가지)가 통째로 교체돼도 **지문이 안 바뀐다**.
완화 요인은 `_check_exclusions`가 행마다 `approval_quote`의 scope.md 실재를 요구한다는 점이지만,
그 검사가 보는 것은 **scope.md 파일 전체**이지 원장 행이 박은 앵커 절이 아니다(check_design_evidence.py:861·878).

**수정 방향.** 원장 행에 «그 판정이 본 입력의 지문»을 판정별로 싣는다 —
`예외 상한`이면 `sha256(sorted(_unit_key(*u) for u in 예외 행))`. rv-G BLOCKER 4의 수정 방향을
잔여뿐 아니라 네 판정 전부에 적용한다.

### [MAJOR] rv-H BLOCKER 1의 수리(`_gate_bookkeeping`)에 **회귀 시험이 0건**이다

`backstop.py:117-139`의 예외는 이번 변경의 핵심 수리인데 `scripts/test/` 어디에도 단언이 없다
(`grep -rn "evidence-ledger\|_gate_bookkeeping" scripts/test/` → `test_ledger.py`의 파일 읽기 2줄뿐) [실측].
`test_ledger.py`의 합성 빌드는 git 저장소가 아니라 `design_commit`이 None →
`legacy_v1_allowed`가 항상 False라 **구조적으로 재현 못 한다**. 반면 `fixtures_backstop.sh`는
`mkproj`가 git 저장소를 만들므로 재현 가능하다.

또한 예외 목록의 폭에도 결정이 안 적혀 있다 — `parts[-1] in GATE_BOOKKEEPING`이라
**빌드 아래 어느 깊이의** `evidence-ledger.json`도 면제되고, `_discarded-`는 **경로 어느 성분이든**
면제된다. `_refreeze-*`·`_prev-*`는 면제가 아니다(rv-H 수정 방향 ①과 다른 선택인데 사유가 없다).

**수정 방향.** `fixtures_backstop.sh`에 3건 — ⓐ 빌드에 `evidence-ledger.json`만 untracked → legacy v1
통지 유지 ⓑ `_discarded-x/` untracked → 유지 ⓒ 관계없는 untracked 파일 1개 → 뒤집힘. 예외 폭의
선택 사유를 주석 한 줄로 남긴다.

### [MAJOR] `_discarded-*`가 **규범 어디에도 없다** — 커밋 전 확인 목록에서 빠졌고 backstop 예외라 안 걸린다

`grep -rn "_discarded" commands/ agents/ docs/DEVELOPMENT.md` → **0건** [실측].
반면 같은 성격의 잔존물에 대해 commands:172는 «커밋 전에 각 산출물 폴더에 `_refreeze-*`·`_prev-*`가
없음을 확인한다 … (그대로 커밋하면 git 이력에 섞인다)»라고 못 박는다. `_discarded-*`는
ⓐ 그 목록에 없고 ⓑ `backstop.py`의 untracked 검사에서 **명시적으로 면제**되며(위 MAJOR)
ⓒ `refreeze.py`에 정리 명령도 세대 상한도 없다(`grep -n "_discarded" refreeze.py` → 생성 코드뿐).
남는 안내는 commit 시 콘솔 «확인 뒤 직접 지운다» 한 줄뿐이다.
rv-H MINOR의 실측으로 A8 9빌드 1세대 = 724파일 207 MiB다.

**수정 방향.** commands:172의 확인 목록에 `_discarded-*`를 넣되 «치우는 방법»을 함께 적는다
(`refreeze.py`에 `discard-prune` 서브커맨드를 두거나, 최소한 «확인 후 `rm -rf`»를 규범에 명시).
`docs/DEVELOPMENT.md`의 `refreeze.py` 항목에 백업 폴더의 지위·수명을 한 줄로 적는다.

### [MAJOR] 시험이 §4ⓒ의 **중심 주장을 재지 않는다** — «개명이 아니라 복사»를 되돌려도 관련 시험 2건이 그린이다

**근거 [실측 변이]** — 정본 사본에서 `shutil.copytree(folder, target)` → `shutil.move(...)`
(= rv-E가 데이터 소실을 재현한 방식) 한 줄만 바꾸고 `test_refreeze.py` 실행:
```
FAIL: test_preserve_never_collides            ← 이름 충돌 시험이 «우연히» 잡는다
OK  : test_commit_preserves_one_generation_and_stays_resumable
OK  : test_discarded_leftover_does_not_block_the_next_refreeze
Ran 42 tests … FAILED (failures=1)
```
`test_commit_preserves_one_generation_and_stays_resumable`은 이름에 `stays_resumable`이 있는데
**`commit --resume`을 한 번도 부르지 않는다.** `HardwallTests` 6건 어디에도 `--resume`이 없다
(`grep -n "resume" test_refreeze.py`의 해당 클래스 구간 → 0건). 사용자 기준 ⑤에 해당한다.

**참고**: 나머지 변이는 정상적으로 red가 된다 — `validate_inputs`의 원장 조회 제거 → 5건 red ·
원장을 v3 자리(`main()`의 `except Defects`)로 옮김 → `test_backstop_passes_through_the_same_door`
red · `cmd_abort`의 `_preserve` 제거 → 해당 1건 red [실측]. **그 세 시험은 자기가 주장하는 것을 잰다.**

**수정 방향.** `test_commit_preserves_…`에 «`_prev` 이름이 `_discarded-`로 바뀐 것이 아니라
**복사**임»을 직접 단언한다(복사 직후 `_prev`가 아직 존재하는 시점을 잡거나, `_preserve` 단위로
`source.is_dir()`을 확인). `--resume` 경로 회귀를 최소 2건(폐기 직후 · 복사 직후) 넣는다.

### [MAJOR] `validate_visual`의 `_ledgered`는 사실상 **죽은 코드**다 — §6 #19 «원장이 대체 채널»은 여전히 거짓

허용 목록 4종은 전부 `validate_inputs`/`validate_interactions` 계열이 내는 메시지다.
`validate_visual`이 내는 메시지(`input_digest: stale…` · `visual cases: exact unique design case set
required` · `visual cases[N].result: pass required` · 미디어 계열)는 **하나도 허용 목록에 없다**.

**근거 [실측]**
```
ledger.refusal('visual cases[0].result: pass required')
  → '원장이 받는 것은 … 판정(잔여·예외 상한·새 표면·partial)뿐이다 …'
183개 issues.append 판형 전수 스캔 → ADMITTED 에 걸리는 것은 정확히 4종(:717 :897 :960 :974)뿐
```
즉 check_design_evidence.py:1353의 호출은 어떤 입력에도 아무것도 바꾸지 않는다. 형식적으로
rv-G BLOCKER 6을 닫은 것처럼 보이지만 §6 #19의 처분(«X — 원장이 대체 채널»)은 그대로 거짓이고,
읽는 사람은 «visual 발견도 원장으로 열 수 있다»고 오해한다.

**수정 방향.** 둘 중 하나. ① 열 생각이면 허용 목록에 visual 판정을 명시적으로 추가한다
(어떤 것을 열지는 별도 결정 — 최소한 «사용자가 승인한 이탈» 칸이 스키마에 없다는 문제와 함께 본다).
② 열지 않을 거면 그 호출을 **지우고** §6 #19를 «별건 — 원장은 닿지 않는다»로 정직하게 고친다.

---

## 3. MINOR

1. **`prepare` 결과 JSON에 `unverified_ledger`가 없다** — `run()`이 `if args.phase == 'prepare': return
   {'review_digest': …}`로 먼저 돌아간다(check_design_evidence.py:1431-1432). `inputs`·`visual`에만 붙는다.
   설계 §1대로면 문제없지만 rv-G B3②는 prepare도 요구했고, BLOCKER 2의 실측에서 그 부재가
   «digest는 바뀌었는데 표식은 없다»로 나타났다 [실측].
2. **`ledger.py add --phase visual`은 영구히 성립 불가**인데 규범(`commands:144`)이 선택지로 제시한다 —
   위 MAJOR 11의 따름. `--phase`가 조회에 쓰이지 않는다는 사실(감사 정보일 뿐)도 어디에도 안 적혀 있다.
3. **`skills/architecture-web/references/final.md`에 원장 절이 없다**(§7 배선표 미이행) —
   `grep -c "원장\|ledger"` → **0** [실측]. 설계·리뷰 에이전트가 읽는 스킬에 원장의 존재가 없다.
   (`implementation-ui`의 링 소유권 절은 들어갔다.)
4. **§2ⓖ·§7의 «commit 완료 시 무효 원장 행 열거»가 미구현** — `grep -c "ledger\|원장" refreeze.py` →
   **0** [실측]. 재동결이 `scope.md`를 바이트째 바꾸면 그 앵커 행들이 죽는데, commit은 아무 말도 하지
   않는다. 다만 다음 게이트 실행에서 `[design-evidence] 원장 행 무효: …`로 나오므로 조용한 소실은 아니다.
5. **잔여 20건 경계에서 키가 바뀐다** — `_check_residual`이 `len>20`에서만 «외 N건»을 붙이므로
   `key_of(잔여 20건…) != key_of(잔여 21건…)` [실측]. fail-closed 방향이라 위험하진 않으나
   «규모가 줄었는데 재승인을 요구한다»는 혼란이 생긴다. rv-G MINOR가 «§2ⓒ 옆에 한 줄»을 권했고 반영 안 됐다.
6. **깨진 `evidence-ledger.json`이 조용히 «0행»이 된다** — `load()`의 `except (OSError, ValueError)`
   (ledger.py:204-206)가 빈 원장을 돌려준다. fail-closed지만 `ledger.py list`가 «유효 0행 · 무효 0행»만
   내서 «파일이 깨졌다»를 말하지 않는다. 사용자는 승인했는데 길이 닫힌 이유를 모른다.
7. **`test_preserve_never_collides`가 비멱등성을 단언으로 못 박는다**(위 MAJOR 1) — 같은 출처를
   두 번 백업하는 것이 «정상»이라는 계약이 되어 버렸다.
8. **`cmd_check`가 같은 판독 실패 경고를 2번 낸다** — `begin`이 `discard_set` 실패와
   `interaction_exclusions` 실패를 같은 `JSONDecodeError` 문자열로 2행 적기 때문 [실측]. 표시만의 문제.

---

## 재현 자료

- 공격 스크립트: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/5d88d7d2-4bb6-412e-83fa-56580ac7b33b/scratchpad/attack/`
  (`atk.py` 손으로 쓴 행 · `atk2.py` backstop · `atk4.py`·`atk5.py` 문자열 주입 · `atk6.py` digest 축소 ·
  `rf.py`·`rf2.py`·`rf3.py`·`rf4.py` 재동결 중단·복구)
- 변이 사본: `…/scratchpad/mut`(원장 자리) · `mut2`(copytree→move) · `mut3`(abort `_preserve` 제거)
- 링 오탐 최소 판형: `…/scratchpad/fr/web`
- 정본 무변경: 감사 시작·종료 시 `dddjango-web/scripts/*.py` sha 동일 · `git status` 항목 수 동일.
