# 적대 검토 H — v4 §4 재동결 · §6 처분 표 · §7 배선표 · §8 합격 기준 · §10 (2026-09-15)

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` **v4**
선행: `rv-{A,B,C,D,E,F}.md` — 중복 지적 없음. v4가 **해소했다고 주장하는 자리**(§9 대조표)는 그 주장
자체를 검증 대상으로 삼았다. 표기: **[실측]** = 이번 검토에서 명령을 실행해 얻은 결과 ·
**[확인]** = 코드 직독.

원형: `dddjango-web/scripts/refreeze.py`를 scratchpad(`rvH/scripts/refreeze.py`)로 복사해 §4ⓐⓑⓒ를
그대로 구현하고, `test_refreeze.Fixture` 하네스를 재사용해 측정했다. **정본은 수정하지 않았다.**
A8(`~/Desktop/spring_dream_server`)은 읽기 전용으로만 열었고, 쓰기가 필요한 측정은 scratchpad 사본에서 했다.

등급: **BLOCKER 6 · MAJOR 7 · MINOR 5**

---

## 0. 설계가 맞힌 것 — 실측으로 확인

1. **§4ⓒ의 «복사 방식»은 rv-E B1(개명 → 데이터 소실)을 실제로 닫는다.** [실측] 원형에서
   `_prev`의 생성·소멸 시점이 그대로다. 정상 `commit` exit 0 · `_discarded-<ts>` 18파일 완전본 ·
   live `design-ref/screen.dc.html` = `<html>NEW</html>` · `design-input.json` 실재.
   rv-E가 재현한 «`commit --resume` exit 1(ENOTEMPTY) · `abort` exit 1 · live 소실»은 **재현되지 않는다.**
2. **`_discarded-` 접두가 어디에도 새지 않는다.** [실측] `_discarded-*`가 남은 빌드에서
   `discard_set`·`orphan_set`·`evidence_pointers`·`preserved_set` 모두 유입 0건,
   `_single(build, PREV_PREFIX)` = None, `_single(build, STAGING_PREFIX)` = staging 정상,
   `cmd_begin`의 `existing` 게이트 통과(exit 0), 이어지는 `check`·`commit` 모두 exit 0.
   [확인] `backstop.py:289`·`evidence_debt_hook.py:34` 둘 다 포함형 allowlist라 §4ⓒ의
   «목록 수정 불필요» 주장이 맞다.
3. **이름 충돌 카운터는 실제로 필요하고 실제로 동작한다.** [실측] 같은 초에 두 사이클이 끝나
   `_discarded-20260915-225946` · `_discarded-20260915-225946-2`가 나란히 생겼다.
4. **복사를 `_cleanup` 안에 둔 결정이 옳다.** [실측] `:530`(`plan['phase']=='done'` 재개)에서도
   18파일 완전본이 나온다 — 두 호출처가 같은 코드를 쓴다는 §4ⓒ 주장 성립.
5. **§4ⓒ가 rv-E MAJOR(«ⓐ·ⓑ는 ⓒ 없이 배포하면 데이터 소실»)를 실제로 막는다.** [실측] 판독 실패로
   고아가 된 `captures/screen-initial.png`·`screen-step-1.png`가 install 충돌로 staging 바이트에
   덮였지만, 원본이 `_discarded-`에 남았다(18파일에 포함).
6. **§4ⓓ③은 A8에서 실제로 작동한다.** [실측] 오늘 A8 backstop의 잔존물 BLOCKER는 1건이고
   그것이 **대상 아닌 빌드**(`20260907-2302-user-info-input`)다 — `discovered`→`builds` 한정이
   이 1건을 그대로 닫는다.
7. **§7의 «Makefile 변경 없음 → 봉인 재발행 불요»는 맞다.** [확인] `run_fixtures.sh`가
   `"$HERE"/fixtures_*.sh`를 글롭한다 · `manifest_seal.GROUPS` 어디에도 `dddjango-web/**`가 없다
   (`protocol` 군은 `Makefile`만 해당).
8. **§7의 나머지 배선 대상 파일은 실재한다.** [실측] 현재 `web_refreeze_contract.py`는 green이고
   기존 `test_refreeze.py` 36건도 **정본·원형 양쪽에서 OK**다 — 기준선이 깨끗하다.

---

### [BLOCKER] §8의 A8 순서와 §6 #6·#7의 «A(이미 열림)» 판정이 **git 상태에 의존**한다 — 원장 파일을 만드는 행위 자체가 «원장이 절대 못 여는 발견 13건»을 세운다

**무엇이 틀렸나.** §8은 «부분 관찰(드라이버) → **12건 닫힘** → prepare exit 0 → … → inputs exit 0»을
A8의 사실로 놓고, §6 #6·#7은 그 12건과 `coverage_review` 1건을 **A(이미 행동으로 열림)**로 처분한다.
실측하면 두 전제가 모두 틀렸다. 그 13건은 `validate_inputs`의 **관찰 내용**이 아니라
`legacy_v1_allowed`의 **git 판정**에 달려 있고, v4가 새로 도입하는 파일(`evidence-ledger.json` ·
`_discarded-*`)이 바로 그 판정을 뒤집는다.

**근거 — 4단 체인, 전부 [실측]**

① A8 대상 빌드는 지금 git-clean이라 발견이 **0건**이다.
```
$ git -C ~/Desktop/spring_dream_server ls-files -z --others --exclude-standard -- \
      .dddjango-web/20260912-1640-web-related-persons        → untracked 0
$ validate_inputs(build, root, legacy_v1=True)   → 발견 0
$ validate_inputs(build, root, legacy_v1=False)  → 발견 13
     cases[0..11].source_observation: interaction evidence required (version 2 with interactions)
     coverage_review: reviewed-input does not match current source/cases/observations
$ backstop.py <A8> --design-build <대상 빌드>
     [info] legacy v1 observation: .dddjango-web/20260912-1640-web-related-persons
     blocker 5건 (구조 3 · 시안 2)      ← 시안 2 = 다른 빌드 잔존물 1 + implementation_digest 1
```
rv-D·rv-E가 잰 «12건»은 그때 빌드 폴더에 `_refreeze-20260915-222208`이 **untracked로 있었기 때문**이다.

② 빌드 폴더에 **untracked 파일이 하나라도** 생기면 `legacy_v1_allowed`가 뒤집힌다 — 합성 git 저장소 실측:
```
기준선 legacy_v1_allowed = True
_discarded-* 생성 후      = False       ← 파일 1개로 뒤집힌다
_discarded 를 커밋한 뒤   = True
```
[확인] `backstop.py:117-122` — `git ls-files --others [--ignored] --exclude-standard`가 비어 있지
않으면 즉시 `return False`. `backstop.py:299-300`이 그 값을 `validate_inputs(legacy_v1=…)`에 넘긴다.

③ v4가 만드는 파일이 정확히 그 조건을 깬다. [확인] `ledger.py:48,131,144` — `LEDGER_NAME =
"evidence-ledger.json"`을 `build / LEDGER_NAME`에 쓴다. §4ⓒ의 `_discarded-<ts>/`도 같다.

④ 그렇게 선 13건을 원장은 **한 건도 받지 못한다.** [실측]
```
$ ledger.filter_issues(build, <위 13개 메시지>)
  → 남는 발견 13 · 등재 가능 0 · notice 0
  REFUSED = ('interaction evidence required', 'coverage_review: reviewed-input does not match')
```
§3 천장 두 줄이 A8 발견의 **100%**다.

**결론.** «원장을 등재해 길을 연다»는 행위가 그 자체로 등재 불가능한 발견 13건을 세운다. §8 기준 4
(«같은 관찰 상태에서 원장만 토글»)는 실제 빌드에서 성립하지 않는다 — 원장 파일을 만드는 것은
관찰 상태가 아니라 **git 상태**를 바꾸고, 그 부작용이 발견 집합을 0 → 13으로 늘린다. §6 #6·#7의
«A»도 «git-dirty일 때만 서는 벽»이라는 사실을 적지 않아 범위 판단의 입력으로 쓸 수 없다.

**수정 방향** ① `legacy_v1_allowed`의 untracked 조건에서 도구 소유 이름
(`evidence-ledger.json`·`_discarded-*`·`_refreeze-*`·`_prev-*`)을 제외하고, 그 변경을 §7 배선표에
`backstop.py:117-122`로 명시한다. 또는 ② 원장 파일과 폐기 백업을 빌드 폴더 **밖**에 둔다.
③ §8 기준 4를 «합성 빌드»가 아니라 **git-추적된 실제 빌드**에서 재도록 고치고(합성 tempdir은
git 저장소가 아니라 `design_commit`이 None → `legacy_v1_allowed`가 **항상 False**라 이 조건을
재현하지 못한다), §8의 A8 순서에 «측정 시 빌드 폴더의 git 상태»를 명시한다.

---

### [BLOCKER] §4ⓐⓑ가 벽을 없애면서 대체 표면을 **0개** 만든다 — 설계 자신의 불변식 II(«열린 길은 무엇이 미검증인지 지우지 못한다») 위반

**무엇이 틀렸나.** §1 불변식 II는 «열린 길은 무엇이 미검증인지 지우지 못한다»이고, §2ⓕ는 원장에
대해 «기록과 통행권이 같은 파일»이라는 장치를 둔다. §4ⓐⓑ에는 그 장치가 **하나도 없다.**
판독 실패를 journal에 적고 진행하는데, `journal.unreadable`을 읽는 소비자가 존재하지 않는다.

**근거 [실측]** — 원형에 §4ⓐⓑ를 구현하고 `captures/screen-interactions.json`을 깨뜨린 빌드:
```
begin  exit = 0   [refreeze] 경고 — 증거 문서를 읽을 수 없다(폐기 집합이 불완전하다): … JSONDecodeError …
   journal.unreadable  = ['captures/screen-interactions.json: JSONDecodeError: …']
   journal.discard_set = 14건   (정상 16건)
   journal.orphans     = 4건    (정상 2건 — 상태 캡처 2건이 고아로 강등)
check  exit = 0   ← 경고 1줄만. 발견 0.
commit exit = 0   ← 완주
```
`check`의 마지막 그물인 «폐기 집합 자기 검사»가 **동어반복이 된다** [확인]
`refreeze.py:433-437`: `covered`는 begin이 같은 깨진 순회로 만든 집합이고 `live`는 지금 같은
깨진 순회로 만든 집합이다. 문서가 계속 깨져 있으면 두 집합이 같은 만큼 짧아져 차집합이 항상 공집합이다.
§4ⓑ가 그 유일한 잔여 신호(`errors` → `issues`)를 print로 내린다.

**소비자 전수 [확인]** — `journal` 문자열 grep 결과 `backstop.py` 0건 · `evidence_debt_hook.py` 0건 ·
`commands/dddjango-web.md`는 «`journal.json`도 `refreeze.py`가 쓴다»라는 소유권 문장뿐이다.
§7 배선표의 `backstop.py` 칸(«원장 notice 1줄 · 잔존물 §4ⓓ 3가지»)과 `commands` 칸(배너 3항목)
어디에도 `unreadable`이 없고, §8에 이를 재는 행이 없다.

**수정 방향** ① `journal.unreadable`이 비어 있지 않으면 `commit` 완료 보고와 G0 배너에
«폐기 집합 미확정 N건 — 이 재동결은 그만큼 불완전하다»를 1급으로 낸다(§2ⓕ의 원장 notice와
같은 등급). ② `_discarded-` 백업 폴더에 그 목록을 동봉한다. ③ §7에 `backstop.py`·`commands` 칸을
추가하고 §8에 «unreadable 1건을 넣으면 마무리 보고에 1줄이 뜬다» 행을 만든다.

---

### [BLOCKER] §4ⓒ의 백업이 **`abort`의 journal 없는 잔존물 rmtree 경로를 덮지 않는다** — §4ⓓ①의 notice 강등과 겹쳐 A8에 지금 있는 «유일본 9개·2.1 MiB»가 조용히 지워진다

**무엇이 틀렸나.** §6 #10의 벽은 «`_prev` 삭제 = 되돌릴 수 없는 폐기»이고 처분은 **R(§4ⓒ가 수리)**다.
그런데 §4ⓒ는 `_cleanup` **안에만** 복사를 넣는다. `_prev`를 지우는 경로는 둘이고, 나머지 하나는
`_cleanup`을 부르지 않는다.

**근거 [확인]** `refreeze.py:650-658` — `cmd_abort`의 journal 없는 분기:
```python
        for leftover in (staging, prev):
            if leftover is not None:
                shutil.rmtree(leftover, ignore_errors=True)
        print('[refreeze] journal 없는 잔존물을 치웠다 — live 빌드 폴더와 이미지는 손대지 않았다')
```
평범한 `rmtree`다. `_cleanup`도 `_discarded_dir`도 지나지 않는다.

**그 경로가 A8에 지금 있다 [실측]** — `20260907-2302-user-info-input/_prev-20260907-2302/`:
```
14파일 · 2.1 MiB · journal.json 없음 · swap-plan.json 없음
live 에 같은 이름이 없는 «유일본» 9개:
  사용자 정보.dc.html
  captures/uii-01-name-390x844.png … uii-07-done-toast-390x844.png · uii-04b-hour-sheet-390x844.png
```
rv-E가 실측한 대로 이 상태에서 `begin`=2·`check`=1·`commit --resume`=1이고 **`abort`만 exit 0**이다.
즉 이 폴더의 유일한 문은 위 `rmtree`이며, §4ⓒ의 백업은 그 문 밖에 있다.

**§4ⓓ①이 이것을 더 나쁘게 만든다.** §4ⓓ①은 «`journal.json`이 없는 `_prev-*`는 BLOCKER가 아니라
notice»로 내린다. 근거는 «되감을 계획이 없으므로 중단된 재동결이 아니다»인데, 실측한 실물은
**되감을 계획이 없는 것이 아니라 계획을 잃은 채 유일본을 쥐고 있는 폴더**다. 차단을 풀면서
백업을 안 붙이면, 정리를 권하는 notice + 백업 없는 rmtree = 데이터 소실 경로가 완성된다.

**수정 방향** ① `cmd_abort`의 journal 없는 분기도 `_discarded-<ts>`로 복사한 뒤 지운다(같은
`_discarded_dir` 헬퍼를 쓴다 — §4ⓒ의 «두 경로가 같은 코드를 쓴다» 원칙을 세 번째 경로로 확장).
② §4ⓓ①의 notice 문구에 «이 폴더에 live에 없는 파일 N개가 있다»를 계산해 싣는다(`_prev` 내용과
live 이름 대조는 결정적이다). ③ §6 #10의 «R»에 어느 경로를 덮는지 적는다.

---

### [BLOCKER] rv-B #21(`_archive_observation_issues`)이 v4 §6 20행에도 없다 — 브라우저가 없으면 **`check` exit 3 · `commit` exit 1로 재동결 자체가 불가능**하고 원장이 닿지 않는다

**무엇이 틀렸나.** §9 대조표는 «rv-E 5 | 표 불일치 | §6(재작성)»으로 해소를 주장한다. rv-E가
«내 담당 축의 한복판»으로 지목한 rv-B #21이 20행 표에 **여전히 없다.** 이 벽은 구속 지시
(«재동결이 어떤 이유로든 불가능해지면 안 된다»)를 정면으로 깬다.

**근거 [실측]** — 원형에서 staging 관찰을 v1(=드라이버 미연결)로 만들고:
```
[refreeze] screen/list: 조작 상태 관찰(v2)이 없다
check  exit = 3
[refreeze] check 를 통과하지 않았다 — 전량 폐기 전에 staging 완전성을 먼저 본다
commit exit = 1
```
[확인] `refreeze.py:454-480` `_archive_observation_issues` — `source-manifest.collection == 'archive'`인
모든 빌드에서 case마다 `version == 2 and 'interactions' in document`를 **무조건** 요구한다.
A8의 9빌드는 전부 archive 경로다.

**원장이 닿지 않는다.** §0이 정한 집행 지점은 `check_design_evidence.py:1255`다. 이 발견은
`refreeze.py` 안에서 나고 `check_design_evidence`를 거치지 않는다. §7의 `refreeze.py` 칸은
«§4ⓐⓑⓒ · 무효 원장 행 열거»뿐이라 배선도 없다.

**결과.** 브라우저 채널이 없는 환경에서 «재동결하라»는 `check` exit 3에서 끝난다. 렌더 실측은
`--render-audit-skipped 브라우저 채널 부재`라는 합법 탈출구가 있는데(`SKIP_REASONS`), **조작 상태
관찰에는 그런 탈출구가 없다.** 같은 원인(브라우저 부재)에 대해 한 축은 열리고 한 축은 닫힌다.

**수정 방향** ① §6 표에 이 행을 «#21 — staging case v2 요구 · `refreeze.py:454-480`»로 올리고
처분을 정한다. ② `check`의 이 발견을 `--render-audit-skipped`와 같은 등급의 명시 사유
(예: «브라우저 채널 부재»)로 낮추고 journal에 적는다 — 그러면 §8의 «부분 관찰이 선행 조건»
논리와도 어긋나지 않는다(부분 관찰조차 못 하는 환경을 재동결에서만 구분한다).
③ 열지 않기로 한다면 §6에 «X + 사유»로 적고, 구속 지시와의 충돌을 §10에 올린다.

---

### [BLOCKER] §7 배선표에 `workspace/tools/web_refreeze_contract.py`가 없다 — §7이 요구한 `commands` 변경이 §8 기준 5(`make verify` green)를 red 로 만들고, 정확한 규범 문장을 쓸 방법이 없다

**무엇이 틀렸나.** §7은 `commands/dddjango-web.md`에 «`ledger.py` 절차»를 넣으라고 적는다. 그런데
`make verify`의 `verify-web`이 돌리는 재동결 계약 검사(D1)는 **`refreeze.py`만** 예외로 두고,
`<산출물 폴더>`가 폐기·교체 대상을 가리키거나 `--build <산출물 폴더>`가 나오면 red를 낸다.

**근거 [실측]** — 정본 `commands/dddjango-web.md` 사본에 §2ⓔ의 절차 한 줄을 붙이고
`web_refreeze_contract.check_d1`을 돌렸다(기준선은 D1 0건):
```
A) "… ledger.py add --build <산출물 폴더> … --scope-ref \"<산출물 폴더>/scope.md#앵커\""
   D1 = ['… 재동결 중 staging을 가리켜야 한다 — <대상 폴더>로 바꾼다 (<산출물 폴더>/scope.md)']
C) "원장 등재 근거는 `<산출물 폴더>/scope.md` 의 앵커 절이다."
   D1 = [동일 red]
E) "… ledger.py add --build <산출물 폴더> --index N"            (경로 표기 없음)
   D1 = ['… (--build <산출물 폴더>)']
B) "… ledger.py add --build <대상 폴더> --index N"              → D1 = []  (통과)
F) "refreeze.py commit --build <산출물 폴더> 뒤 ledger.py list --build <산출물 폴더>"  → D1 = []
```
[확인] `_placeholder_issues`의 예외는 `if 'refreeze.py' in line[start-60:start]` 한 줄뿐이다 —
`ledger.py`는 예외를 못 받는다. 그래서 **F처럼 `refreeze.py`를 60자 안에 끼워 넣는 우회만 통과한다.**

**더 나쁜 것: 정확한 규범을 쓸 수가 없다.** 원장은 평시에는 live 빌드(`<산출물 폴더>`)에, 재동결
step ④에서는 staging(`<대상 폴더>`)에 있어야 한다(`commands:138`이 step ④에서 staging을 `--build`로
준다). 두 경우를 다 적는 문장은 `<산출물 폴더>`를 반드시 포함하므로 **D1이 반드시 red다.**
§7이 이 파일을 배선 대상으로 올리지 않았으므로 구현자는 red를 만나고 나서야 알게 되고,
가장 싼 해법(«`<대상 폴더>`로만 적는다»)은 평시 사용법을 규범에서 지우는 오답이다.

**수정 방향** ① §7에 `workspace/tools/web_refreeze_contract.py`를 올리고, `_placeholder_issues`의
예외 목록을 «도구 스크립트 이름» 집합(`refreeze.py`·`ledger.py`)으로 넓힌다. ② 동시에 §4/§2에
**원장 파일의 재동결 중 거처**를 한 줄로 못 박는다(rv-E MAJOR 미해소 — staging 소유 + install 이월인지,
`FIXED_DISCARD_FILES` 대상인지). 거처가 정해져야 어느 자리표시자가 옳은지 정해진다.
③ §8 기준 5 앞에 «`web_refreeze_contract.py --self-test`도 green» 조건을 적는다.

---

### [BLOCKER] §8 합격 기준에 §4를 재는 행이 **0개**다 — §4ⓐⓑⓒ 전량 구현본에서 기존 회귀 36건이 **그대로 OK**다

**무엇이 틀렸나.** §8은 5행 중 2·3을 링 검사에, 4를 원장에, 1·5를 저장소 채널에 쓴다.
설계에서 가장 큰 행동 변경인 §4(재동결)를 재는 행이 하나도 없다. 그리고 기준 1은 §4를 구별하지 못한다.

**근거 [실측]** — §4ⓐⓑⓒ를 전부 구현한 원형과 정본을 같은 스위트로 돌린 결과:
```
원형(§4 전량 구현): Ran 36 tests … OK
정본(§4 미구현)   : Ran 36 tests … OK
```
rv-E가 «기존 스위트는 §4 변경을 하나도 안 잡는다»를 예고했고, v4 §7이 «test_refreeze.py §4 회귀
4건»으로 응답했다. 그런데 **§8 기준 1의 괄호는 «신설 2종 포함»이라 적어 그 2종을
`fixtures_{ledger,focus_ring}.sh`로 한정한다.** §7도 «§4 회귀 4건»이라고만 하고 무엇을 단언할지
정하지 않는다. 따라서 기준 1은 «구현자가 쓰기로 한 무언가가 통과한다»는 항진명제다.

**같은 자리의 파생 문제.** §8 어디에도 다음을 재는 행이 없다 — ⓐ 정상 commit 뒤 `_discarded-`가
완전본인가 ⓑ 복사 실패 시 무슨 일이 나는가 ⓒ `_prev`가 없는 빌드에서 `begin`이 판독 실패로
멈추지 않는가 ⓓ 잔존물 BLOCKER가 `--design-build`로 좁혀지는가. ⓓ는 [실측] 지금 A8에서
1건 발화 중이라 배포 전/후 대조가 가능한데도 행이 없다.

**수정 방향** §8에 §4 행 4개를 명령·기대 출력까지 적는다. 최소한:
`_cleanup` 정상 → `_discarded-` 파일수 = `plan['discard']` + install 충돌 피신분 + 2(bookkeeping) /
`copytree` 실패 주입 → exit 0이되 «부분 백업» 표식 존재 / 판독 실패 빌드 `begin` exit 0 ·
`journal.unreadable` 1건 · 마무리 보고 1줄 / `--design-build` 지정 시 잔존물 발견이 그 빌드로 한정.

---

### [MAJOR] §4ⓒ가 `_cleanup`의 중단 창을 두 syscall에서 «전량 복사 시간»으로 넓히고, 그 창에서 `abort`가 exit 0으로 **완료된 재동결을 되감는다** — §4ⓓ②의 «journal 유무» 판별자가 이 상태를 가르지 못한다

**근거 [실측]** — 복사 직후 중단:
```
잔존 = ['_discarded-…', '_prev-…', '_refreeze-…']
_prev/journal.completed_at     = 2026-09-15T23:00:22+09:00
_refreeze/journal.completed_at = None
abort exit = 0
  [refreeze] 되돌렸다 — live 빌드 폴더와 이미지가 재동결 이전 상태다
abort 후 live design-ref = b'<html>original</html>'     ← 완료된 재동결이 통째로 되감겼다
```
[확인] 원인은 `cmd_abort:647-649` — journal을 `staging → prev` 순으로 찾는데 `_finish`는
`completed_at`을 **`prev/journal.json`에만** 쓴다. 그래서 `completed_at` 가드가 무력화된다.

**기준선 대조 [실측]** — 정본에서 같은 지점에 중단을 넣어도 `abort` exit 0 · live가 되감긴다.
**따라서 이 결함 자체는 선행한다.** v4의 책임은 둘이다:
① `_cleanup`이 두 `rmtree` 호출에서 «`_prev` 전량 복사»로 바뀌므로 중단 창이 A8 기준
3.6~34 MiB 복사 시간으로 넓어진다 — Ctrl-C가 현실적으로 들어가는 구간이 된다.
② §4ⓓ②는 «남는 BLOCKER의 메시지에 실제로 여는 명령을 적는다(**journal 유무**로 갈리는 분기)»라고
적는다. 이 상태는 두 폴더 모두 journal이 있으므로 그 분기가 «commit --resume 또는 abort»를
그대로 내고, 사용자가 `abort`를 고르면 완료본이 사라진다. **판별자는 journal 유무가 아니라
`_prev/journal.completed_at`이어야 한다.**

**수정 방향** ① `cmd_abort`의 journal 탐색을 `prev → staging` 순으로 뒤집거나 두 journal의
`completed_at`을 모두 본다. ② §4ⓓ②의 분기 축을 «journal 유무 · `completed_at` 유무» 2축으로 적는다.
③ §8에 회귀 1건(«완료 직후 중단 상태에서 `abort`는 exit 1»).

---

### [MAJOR] 복사 실패 시 **부분 백업이 완전본과 구별되지 않고** `_prev`는 그대로 삭제된다 — «경고만 낸다»가 곧 «침묵한 데이터 소실»

**근거 [실측]** — `copy_function`이 5번째 파일부터 `OSError(28, No space left on device)`를 내도록 주입:
```
[refreeze] 경고 — 폐기분 백업 실패(Error: [(…14쌍의 (src,dst,사유) 튜플…)]) — 정리는 계속한다
[refreeze] 교체 완료
commit exit = 0
부분 백업 파일수 = 4  (완전본은 18)
부분 백업 내용   = ['captures/screen-interactions.json','captures/screen-step-1.png',
                    'captures/screen-trace.json','screen-declared.json']
«부분»임을 알리는 표식 = 없음 (폴더 안에 journal.json 도 swap-plan.json 도 없다)
_prev 남아 있나 = []      ← 그대로 삭제됐다
```
남은 폴더는 이름·구조상 완전본과 똑같다. 며칠 뒤 «차이점을 확인해 수정하겠다»며 열면
14/18이 조용히 없다. 경고는 4 KB짜리 `shutil.Error` 덩어리라 배너·보고에 실을 수 없는 형식이다.

**수정 방향** ① 복사는 `_discarded-<ts>.partial/`에 하고 성공 시에만 최종 이름으로 rename한다
(실패분은 이름으로 즉시 구별된다). ② 실패 시 `_prev`를 **지우지 않고** 그대로 둔다 — 정리 실패는
차단 사유가 아니지만 «백업도 원본도 없는 상태»를 만들 이유는 없다(잔존물은 `--design-build`
한정 notice로 이미 다뤄진다). ③ 경고를 «백업 실패 N/M 파일 · 원본을 `_prev-<ts>`에 남겼다» 1줄로
요약하고 상세는 파일에 적는다.

---

### [MAJOR] `_cleanup`이 멱등하지 않다 — 복사 후 중단 → `--resume`이 **두 번째 전체 사본**을 만든다

**근거 [실측]**
```
복사 직후 중단 → 잔존 ['_discarded-…', '_prev-…', '_refreeze-…']
commit --resume exit = 0
_discarded = [('_discarded-20260915-230022', 18), ('_discarded-20260915-230022-2', 18)]
```
[확인] `cmd_commit:529-532`의 done-재개 분기가 `_cleanup`을 다시 부르고, `_cleanup`은 `_prev`가
있으면 조건 없이 복사한다. 즉 §4ⓒ가 «두 경로가 같은 코드를 쓴다»를 얻은 대가로 «같은 세대를
두 번 뜬다»를 얻었다. A8 최대 빌드(`20260908-0143-web-chat-spine` 폐기 27.6 MiB) 기준 55 MiB다.

**수정 방향** `_discarded_dir`를 부르기 전에 «이 `_prev`의 백업이 이미 있는가»를 본다 —
`_prev/swap-plan.json`의 `prev` 이름을 백업 폴더에 남기고(또는 백업 폴더 안에 `source` 1줄) 같은
출처의 백업이 있으면 건너뛴다. §8 회귀 1건으로 못 박는다.

---

### [MAJOR] §6 #20의 위치와 사유가 둘 다 틀렸다 — `environment_error`는 `ValueError`로 **원장 지점 앞에서 새고 backstop 전체를 exit 1로 죽인다**

**무엇이 틀렸나.** §6 #20은 «`environment_error` → exit 1 | 위치 `run()` | **X** — 미실행이지
발견이 아니다»로 처분한다. 실제 위치도 성질도 다르다.

**근거 [확인]**
- `check_design_evidence.py:995-997` — `validate_interactions` 안에서
  `raise ValueError(f'{label}: environment_error — …')`. `Defects`가 아니다.
- `validate_inputs:1227`이 그 함수를 **try 없이** 부른다. 따라서 §0이 정한 원장 지점
  (`:1255` `if issues: issues = ledger.filter(...)`)에 **도달하지 못한다.** §0-4의
  «조기 `raise Defects` 5곳만 구조적으로 원장 밖»이라는 열거에 이 탈출구가 빠져 있다.
- `backstop.py:266`의 `try:` … `:310-312` `except Exception: traceback … return 1`,
  `:334` `sys.exit(main(...))`. 즉 그 빌드 하나가 아니라 **backstop 프로세스 전체**가 exit 1이고
  발견 목록은 한 줄도 출력되지 않는다.

**수정 방향** #20의 위치를 `check_design_evidence.py:995-997`로 고치고, 처분을 «X — 미실행»이 아니라
«§0의 구조적 배제 열거에 추가 + backstop이 Defects와 같은 등급으로 받도록 수리»로 바꾼다.
최소한 §0-4의 문장을 «5곳»에서 «5곳의 `Defects` + 1곳의 `ValueError`»로 정정해야 한다.

---

### [MAJOR] §8 기준 3이 §5ⓐ·§10이 예고한 «A8 CSS 2계열 수정»과 충돌한다 — 고치는 순간 기준 3은 영구 red

**무엇이 틀렸나.** §8 기준 3은 `check_focus_ring.py <A8 web>` **exit 2**와 `select-field__select`·
`.input-field__control` **포함**을 요구한다. 그런데 §5ⓐ는 «이번 수리는 A8 CSS 수정 2계열을 낳는다»,
§10은 «결함이 맞으므로 그대로 낸다»고 적는다. A8 CSS를 고치면 그 두 발견이 사라져 exit 0이 되고
기준 3이 red가 된다. 순서가 못 박히지 않았다.

**근거** §8은 «A8 최종 검증은 배포 후다»를 **기준 4·순서 절에만** 적용한다(원장·관찰 순서).
기준 3은 A8 현 상태를 직접 재는 행인데 «언제의 A8인가»가 없다. 기준 2도 같은 성질이다
(`check_clip_clearance`는 v1.1.16에서 이미 배포됐고 A8 수정이 진행되면 건수가 바뀐다 —
«건수 비고정»이 그 완충이지만 기준 3에는 그 완충이 없고 오히려 **포함/미포함 목록이 고정**이다).

**수정 방향** 기준 3을 «A8 CSS 수정 **전** 스냅샷에서 1회 측정하고, 그 출력 원문을
`eval/…/ring-overlap-prevalidation.md`에 봉인한다»로 바꾸거나, 회귀는 `fixtures_focus_ring.sh`의
합성 판형(이미 FR1~FR13 존재)에 맡기고 A8 행은 «배포 전 1회 관찰»로 등급을 내린다.

---

### [MAJOR] §8 기준 4의 측정 절차가 구체적이지 않고, 합성 빌드로는 재현 자체가 안 된다

**무엇이 틀렸나.** 기준 4는 «같은 관찰 상태에서 원장만 토글 → 원장 0행 exit 2 / N행 exit 0 ·
`backstop.py`도 같이 바뀐다 · 합성 빌드(`test_ledger.py`)로 측정한다»가 전부다. 다음이 비어 있다.

1. **어느 명령의 exit인가** — `check_design_evidence.py --phase inputs`인가 `prepare`인가 `visual`인가.
   §1은 phase마다 표면화가 다르다고 했으므로 행이 셋이어야 한다.
2. **«토글»의 조작 정의** — `ledger.py drop`인가 파일 삭제인가. §2ⓕ는 «지우면 닫힌다»를
   장치로 삼으므로 둘이 같은지 자체가 측정 대상이다.
3. **중복 측정** — §2ⓔ가 `add`에 «등재 직후 다시 돌려 그 발견이 사라졌는지 확인»을 이미 넣었다.
   기준 4의 «N행 → exit 0»은 `add`의 자기 검증과 같은 것을 두 번 재며, «filter가 맞다»와
   «add의 자기 검증이 맞다»를 구별하지 못한다.
4. **합성 빌드로는 안 되는 것** [실측] — tempdir은 git 저장소가 아니라 `design_commit`이 None →
   `legacy_v1_allowed`가 **항상 False**다. 위 BLOCKER 1의 조건(«원장 파일이 git 상태를 바꿔 13건을
   세운다»)을 구조적으로 재현하지 못한다. 또 «`backstop.py`도 같이 바뀐다»를 합성 빌드에서
   돌리려면 `config.json`·`design_source`·`web/`·git 초기화가 필요한데 아무것도 적혀 있지 않다.

**수정 방향** 기준 4를 3행으로 쪼갠다 — ⓐ `filter` 단위 시험(순수 함수, 합성) ⓑ 검사기 CLI
phase 3종(합성 빌드) ⓒ **git 초기화된 합성 빌드에서 `backstop.py`** — 그리고 ⓒ에 «원장 파일을
추가해도 다른 발견이 늘지 않는다»를 단언으로 넣는다(BLOCKER 1의 회귀).

---

### [MAJOR] §6 표가 여전히 rv-B «예»와 1:1이 아니다 — §9의 «rv-E 5 | 표 불일치 | §6» 해소 주장이 성립하지 않는다

**근거 [확인]** rv-E가 «빠진 «예» 9»로 열거한 #3·#8·#9·#16·#21·#24·#25·#26·#27 중 v4 §6이
새로 실은 것은 **#8 하나뿐**이다(§6 #20 — 그것도 위 MAJOR대로 위치·사유가 틀렸다).
여전히 표 밖인 것:

| rv-B | 벽 | 위치 |
|---|---|---|
| #3 | 수집기 sha 불일치 | `check_design_evidence:1006-1010` |
| #9 | `design-input` 미지 최상위 필드 | `:1084-1085` |
| #16 | backstop `ValueError` → exit 1 | `backstop:310-312` |
| #21 | staging case v2 요구 | `refreeze:454-480` (위 BLOCKER) |
| #24 | journal/plan 손상 | `refreeze:503-506·526` |
| #25·#26·#27 | `commands:147·152·179·130` 산문 벽 | md |

특히 **#25·#26·#27은 코드 수리로 열리지 않는 md 산문 벽**인데 §7의 `commands` 칸(배너 3항목 +
패스트트랙 + `ledger.py` 절차)에도 없다. §6 마지막 문장 «X 9건은 전부 대상 빌드에서 발화하지 않고
이번 합격 기준에 닿지 않는다»는 표에 **없는** 행에는 적용조차 되지 않는다.

**수정 방향** rv-E의 수정 방향(«표를 rv-B 판정과 1:1로 다시 짓고 빠진 행에 각각 포함/제외 + 사유»)이
아직 유효하다. 최소한 #21·#24는 §4가 손대는 파일 안이므로 이번 사이클에서 판정해야 한다.

---

### [MINOR] §6 #15의 위치가 여전히 틀렸다

[확인] «설계 빌드 0 + config 有»의 코드는 `backstop.py:281-282`
(`elif configured and not discovered:`)다. `:294-296`은 «design build 디렉터리/증거가 없음»으로
다른 발견이다. rv-E가 v3 #13에 대해 같은 지적을 했고 v4 §6 재작성에서 반영되지 않았다.

---

### [MINOR] §4ⓓ의 «A8에서 지금 2건 발화 중»이 오늘 실측과 다르다 — 1건이다

[실측] `backstop.py <A8> --design-build <대상 빌드>` → 잔존물 BLOCKER **1건**
(`20260907-2302-user-info-input: _prev-20260907-2302`). rv-E가 잰 두 번째 건
(`20260912-1640-…: _refreeze-20260915-222208`)은 이미 치워졌다. 같은 이유로 그 빌드의
`legacy_v1_allowed`가 True로 돌아와 시안 blocker가 15건 → 2건으로 줄었다(BLOCKER 1 참조).
설계가 인용하는 수치가 «측정 시점의 git 상태»에 달려 있다는 것이 그 자체로 §8의 문제다.

---

### [MINOR] §7의 «신설» 3종이 이미 작업 트리에 있다 — 배선표가 현재 트리와 어긋난다

[실측] `git status --porcelain`:
```
?? dddjango-web/scripts/check_focus_ring.py          (281행)
?? dddjango-web/scripts/ledger.py                    (325행 · LEDGER_NAME · REFUSED · filter_issues)
?? dddjango-web/scripts/test/fixtures_focus_ring.sh  (FR1~FR13 · U1·U2 · DET)
?? codex-dddjango-web/skills/dddjango-web/scripts/{check_focus_ring.py,ledger.py,test/fixtures_focus_ring.sh}
 M dddjango-web/commands/dddjango-web.md  (2줄 — ledger 절차는 아직 없다)
```
§7의 «신설»이 세 파일에 대해 사후 기술이 된다. 계획서가 «무엇이 이미 있고 무엇이 남았는가»를
다시 세지 않으면 범위·검증 대상이 어긋난다. (`refreeze.py`·`backstop.py`는 미변경 — §4는 미구현.)

---

### [MINOR] §7의 «`codex-dddjango-web/**` 전량 미러» 한 줄이 두 개의 기계 계약을 감춘다

[확인] ① `web_refreeze_contract.check_c`가 `dddjango-web/scripts/refreeze.py`와
`codex-dddjango-web/skills/dddjango-web/scripts/refreeze.py` **둘 다**에 4 서브커맨드 실재를 요구한다.
② `Makefile:95` `verify-web`이 «codex 미러 byte 대조(scripts·assets)»를 돌린다.
따라서 §4의 `refreeze.py` 변경은 미러를 **byte 동일**로 갱신하지 않으면 `make verify`가 red다.
§7의 한 줄로도 논리적으로는 충분하지만, §8 기준 5의 red 원인을 구현자가 예측하지 못한다.

---

### [MINOR] §10이 §4ⓒ의 위험을 하나도 적지 않는다

§10은 원장 축 위험 3줄과 A8 CSS 부담 1줄뿐이다. 위 실측이 드러낸 §4ⓒ 고유 위험이 없다 —
부분 백업의 비가시성 · `_cleanup` 비멱등 · `abort` 경로 미보호 · 그리고 **수명·거처 미규정**
(rv-E MAJOR 미해소): [실측] A8 9빌드 1세대 백업 = **724파일 207 MiB**
(빌드별 3.6~34 MiB), `.dddjango-web`은 gitignore 대상이 아니고 이미 1727파일이 추적 중이며,
`commands:172`의 커밋 전 확인 목록은 «`_refreeze-*`·`_prev-*`»뿐이라 `_discarded-*`는
**그대로 커밋된다**(그 줄의 명시 사유가 «그대로 커밋하면 git 이력에 섞인다»다). `refreeze.py`에
정리 명령도 세대 상한도 없다.
