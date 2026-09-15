# 적대 검토 E — §4 재동결 수리와 §6 하드월 전수 표 (2026-09-15)

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` **v3** §4·§6·§7(§8 합격 기준 대조 포함)
선행: `rv-A.md`·`rv-B.md`·`rv-C.md` — 중복 지적 없음. v3가 **선행 지적을 해소했다고 주장하는 자리**는
그 주장 자체를 검증 대상으로 삼았다(§0·§9의 «해소» 주장).
표기: **[실측]** = 이 검토에서 명령을 실행해 얻은 결과 · **[확인]** = 코드 직독.

등급: **BLOCKER 5 · MAJOR 7 · MINOR 5**

---

### [BLOCKER] §4ⓒ «이름만 바꿔 남긴다»가 `_prev`의 «교체 진행 중» 표식 역할을 떼어내 — 재개가 live 빌드를 재폐기하고 복구 명령이 0개가 된다

**무엇이 틀렸나.** `_prev-<ts>/`는 세 역할을 겸한다: ① 되감기 저장소 ② «commit이 진행 중»이라는
유일한 표식(`cmd_commit:498` `_single(build, PREV_PREFIX)`) ③ 완료 표식(`journal.completed_at` ·
`swap-plan.phase`). §4ⓒ는 ①만 보고 «이름만 바꾼다»고 적었다. 이름을 바꾸는 순간 ②③이 함께 사라진다.
그러면 `cmd_commit`은 완료된 재동결을 **새 교체**로 오인하고, `plan['discard']`를 다시 돌려
**방금 설치된 live 산출물을 새 `_prev`로 옮긴다.**

**근거 [실측]** — `test_refreeze.Fixture`에 §4ⓒ를 그대로 구현(`_cleanup` = rmtree(staging) + prev.rename
→ `_discarded-<ts>`)하고 `_finish` 정리 도중 중단을 재현
(`scratchpad/probe_b.py`):

```
기준선(현재 코드) — _cleanup 직전 중단
  잔존: ['_prev-20260915-225317', '_refreeze-20260915-225317']
  resume exit = 0        ← 정상 복구
  잔존 after : []

§4ⓒ 구현 — 개명 직후 중단
  잔존: ['_discarded-20260915-225317', '_refreeze-20260915-225317']
  resume exit = 1   [refreeze] OSError: [Errno 66] Directory not empty:
                    '…/_prev-20260915-225317' -> '…/_discarded-20260915-225317'
  abort  exit = 1   [refreeze] 이미 완료된 재동결이다 — abort 로 되돌리지 않는다
  잔존: ['_discarded-20260915-225317', '_prev-20260915-225317']
  live design-ref  : MISSING
  live design-input: False
```

**live 빌드가 비었고 `commit --resume`·`abort` 둘 다 exit 1이다.** 남은 행동은 손으로 `mv` 하는 것뿐이며
그 절차는 규범 어디에도 없다. 사용자 구속 지시(«재동결이 어떤 이유로든 불가능해지면 안 된다»)의
정반대 상태다.

경로 분해 [확인]:
- `refreeze.py:498` `prev = _single(build, PREV_PREFIX)` → 개명 뒤 **None**.
- `:509-525` `if prev is None:` → `checked_at`이 있고 live `scope.md` sha가 staging 사본과 같으므로
  (begin이 INPUT_GLOBS로 복사한 바이트가 install로 되돌아왔다) **통과** → 새 `_prev-<ts>`와 새 plan
  (`phase='planned'`)을 만든다.
- `:534-541` `discarded` 재실행 → 설치된 live 파일이 `src.is_file()`이므로 그대로 `_prev`로 이동.
  (이 재폐기를 막으려고 쓴 회귀가 `test_refreeze.py:363` `test_resume_after_stop_at_installed_does_not_redo_discard`인데,
  그 시험은 `_prev`가 살아 있는 경우만 본다.)
- `:562-563` `done` → `_finish` → `_cleanup` → 같은 초의 `_discarded-<ts>`가 이미 있어 `Path.rename`이
  ENOTEMPTY로 죽는다(POSIX는 비어 있지 않은 디렉터리 위로 rename 불가).
- `cmd_abort:660-661` — `_finish`가 journal에 쓴 `completed_at` 때문에 거부.

**수정 방향** «이름만 바꾼다»로는 부족하다. 최소 네 가지를 설계가 못 박아야 한다:
① 개명 대상 이름의 **유일성**(기존 `_discarded-*`가 있으면 접미 카운터) ② `_cleanup`은 staging 제거를
먼저, 개명을 **마지막**에 하고 그 둘이 한 함수 안에서만 일어난다는 것 ③ `cmd_commit`이 «완료된
재동결의 잔재»(staging journal의 `checked_at`과 같은 `_discarded-*/journal.json`에 `completed_at`이 있다)를
발견하면 새 교체를 시작하지 말고 «정리만» 경로로 가는 것 ④ `cmd_commit:529`의
`if plan['phase'] == 'done': _cleanup(...)` 분기도 같은 함수를 쓴다는 것(현재 설계는 `_finish`만 언급해
이 두 번째 호출처를 빠뜨렸다 — `refreeze.py:530`과 `:639`가 같은 `_cleanup`을 부른다 [확인]).

---

### [BLOCKER] §6 #11의 처분 «R — §4ⓒ가 접두를 분리»는 거짓이다 — 잔존물 BLOCKER는 §4ⓒ와 무관하고, 대상 프로젝트에서 지금 2건 발화 중이다

**무엇이 틀렸나.** #11의 벽은 «`_refreeze-*`/`_prev-*`가 **남아 있으면**»이다. §4ⓒ가 만드는 `_discarded-`는
**commit이 성공적으로 끝난 뒤에만** 생긴다. 즉 §4ⓒ는 «이 벽을 더 나쁘게 만들지 않는» 조치일 뿐
**여는 조치가 아니다.** 표가 이 행을 «R(재동결 수리로 열림)»으로 적은 탓에, 계획 단계에서 이 벽이
«처리됨»으로 분류된다.

**근거**
- [확인] `backstop.py:288-289`
  ```python
  leftovers = sorted(item.name for item in build.iterdir()
                     if item.is_dir() and item.name.startswith(('_refreeze-', '_prev-')))
  ```
  포함형 allowlist다. `_discarded-`는 애초에 걸리지 않으므로 «접두를 분리»할 목록 자체가 없다.
- [실측] A8 프로젝트에서 `--design-build`를 **주고도** 이 BLOCKER가 2건 난다 — 하나는 **대상 빌드가
  아닌 다른 빌드**다(잔존물 루프가 `builds`가 아니라 `discovered`를 돈다 — `backstop.py:283`):
  ```
  $ python3 backstop.py …/a8 --design-build …/20260912-1640-web-related-persons
  [DESIGN] BLOCKER — .dddjango-web/20260907-2302-user-info-input: interrupted refreeze — _prev-20260907-2302 …
  [DESIGN] BLOCKER — .dddjango-web/20260912-1640-web-related-persons: interrupted refreeze — _refreeze-20260915-222208 …
  EXIT=2 · blocker 18건 (구조 3 · 시안 15)
  ```
- [실측] `_prev-20260907-2302/`에는 `journal.json`도 `swap-plan.json`도 없다(내용물은 `사용자 정보.dc.html`·
  `captures/`·`design-tokens.json`·`motion-notes.md`·`render-audit.json`·`screen-meta.json`·`source-manifest.json`).
  이 상태에서 `begin`=2 · `check`=1 · `commit --resume`=1이고 오직 `abort`만 exit 0으로 **rmtree** 한다
  (`refreeze.py:650-658`). 즉 이 벽의 유일한 문은 «재동결 산출물을 통째로 지우기»이며, 메시지는
  «commit --resume (완료 전이면 abort)»라 그 사실을 말하지 않는다.

**수정 방향** #11의 처분을 «R»에서 실제 조치로 바꾼다 — 잔존물 발견을 **notice로 내리고 차단은
커밋·마무리 시점에만** 걸거나(rv-C가 지적한 축), 최소한 `--design-build`가 주어지면 잔존물 점검도
그 빌드로 좁힌다(`backstop.py:283`의 `discovered` → `builds`). 어느 쪽도 §4ⓒ가 대신하지 못한다.

---

### [BLOCKER] §7 배선표가 `backstop.py`를 원장 조회에 잇지 않는다 — §2ⓔ의 «단일 종료 지점»이 게이트의 절반에 닿지 않는다

**무엇이 틀렸나.** §2ⓔ는 집행 지점을 `check_design_evidence.py:main()`의 `except Defects` **한 자리**로
정했다. 그런데 G2 직전(`commands:186`)·마무리(`commands:191`)·패스트트랙(`commands:220`)이 부르는
`backstop.py`는 `main()`을 거치지 않는다 — `validate_inputs`를 **직접 부르고 `Defects`를 스스로 잡는다.**
§7 배선표의 `backstop.py` 칸은 «원장 notice 1줄 · `_discarded-` 접두 제외»뿐이라 조회가 배선되지 않는다.

**근거**
- [확인] `backstop.py:300-307`
  ```python
  design_spec, input_value, _items = validate_inputs(build, root, legacy_v1=legacy_v1)
  …
  except Defects as error:
      design_defects.extend(f'{build}: {message}' for message in error.messages)
  ```
  `check_design_evidence.main()`(`:1427-1430`)과 완전히 별개의 종료 지점이다.
- [실측] 그래서 원장이 12건을 덮더라도 backstop 출력은 그대로다. 현재값:
  ```
  --design-build 有 : 시안 blocker 15건 = v2요구 12 + coverage_review 1 + 잔존물 2
  --design-build 無 : 시안 blocker 23건 (다른 빌드 8건 추가)
  ```
- 결과: §8 합격 기준 3(«A8이 inputs exit 0으로 진행 가능해진다»)을 만족해도 `commands:191`의
  «명령 전체의 실제 exit 0»은 성립하지 않는다 — **진행은 열리고 마무리는 안 열린다**가 아니라
  둘 다 backstop 뒤에 있으므로 완주가 불가하다.

**수정 방향** §7에 `backstop.py`의 **원장 조회 배선**을 명시한다 — `partition_by_ledger`를 backstop의
`except Defects`에도 적용하고(그쪽 phase는 `visual`에 준함), 등재분은 `[DESIGN] BLOCKER`가 아니라
notice + «미검증 원장 N행»으로 낸다. 배선하지 않을 거면 §2ⓔ의 «단일 종료 지점» 문장을
«검사기 CLI 한정»으로 축소하고 그 한계를 §8 합격 기준에 반영해야 한다.

---

### [BLOCKER] §4ⓓ는 자기가 열겠다고 적은 자리를 열지 못한다 — `missing` 게이트가 먼저 exit 3을 내고, 그 벽은 §6 #12에서 **X(제외)**다

**무엇이 틀렸나.** §4ⓓ는 «`SKIP_REASONS`에 `no_measurable_dom`을 추가한다 — **이미지 시안·자체 설계
빌드가 영구 exit 3이 되는 자리를 연다**»라고 적는다. 그런데 `cmd_check`에서 렌더 실측 enum 분기는
`missing` 검사 **뒤**에 있고, 이미지·자체 설계 빌드는 그 앞에서 이미 죽는다.

**근거 [확인]** `refreeze.py:421-446` — 순서가 결정적이다.
```python
    missing: list[str] = []
    design_ref = staging / 'design-ref'
    if not design_ref.is_dir() or not any(design_ref.rglob('*')):   # :422-424
        missing.append('design-ref/')
    for name in REQUIRED_STAGING:                                    # :425-427
        if not (staging / name).is_file(): missing.append(name)
    …
    if issues:                                                       # :438-441
        …
        return 3
    if not journal.get('has_render_audit') and journal.get('render_audit_skip_reason') is None:  # :442
```
`REQUIRED_STAGING`(`:39-40`)은 `screen-meta.json`을 **무조건** 요구하는데, 규범은 그것을
«(`.dc.html`이면)»으로 한정한다(`commands/dddjango-web.md:28` [확인]) — 생산 주체도 `extract_dc.py --meta`
하나뿐이다(저장소 전수 grep 결과 `--meta` 인자는 그 파일에만 있다 [실측]). `design-ref/` 비어 있지 않음도
이미지 단독 빌드에는 해당이 없다. 즉 §4ⓓ가 겨눈 부류는 **enum 이전에** exit 3이고, 그 벽(rv-B #19)은
§6 #12에서 **X(별건)**으로 밀려 있다. **설계 내부 모순이다.**

**수정 방향** ① §4ⓓ의 목적 문장을 사실에 맞게 줄이거나(«상속된 false를 가진 dc 빌드만 연다»),
② #12를 이번 사이클에 포함시켜 `REQUIRED_STAGING`·`design-ref/`를 **출처 종류별로 분기**한다.
둘 중 하나가 없으면 §4ⓓ는 아무 문도 열지 않는 한 줄 변경이다.

---

### [BLOCKER] §6이 «rv-B 전수 표와 1:1»이라는 주장이 성립하지 않는다 — rv-B의 «예» 17개 중 **8개만** 실렸고 9개가 빠졌다

**무엇이 틀렸나.** §0 표는 «§6이 rv-B 전수 표와 1:1이다»라고, §6 line 219는 «rv-B의 …«예»로 판정된
17개를 **그대로** 싣고»라고 적는다. 대조하면 집합이 다시 치환돼 있다. rv-C BLOCKER 3이 v2에 대해 낸
지적이 **v3에서 해소됐다는 주장만 있고 실제로는 해소되지 않았다** — 그래서 중복이 아니라 재발이다.

**근거 [확인]** rv-B 30행 중 «예» 17행 = #1·#2·#3·#8·#9·#11·#13·#14·#16·#18·#19·#20·#21·#24·#25·#26·#27
(«조건부» 4 = #4·#5·#15·#23 · «아니오» 9 = #6·#7·#10·#12·#17·#22·#28·#29·#30). §6 17행과의 대조:

| | 목록 |
|---|---|
| 실린 «예» **8** | #1(§6 3) · #2(§6 2) · #18(§6 7) · #20(§6 10) · #19(§6 12·X) · #14(§6 13·X) · #11(§6 14·X) · #13(§6 16·X) |
| **빠진 «예» 9** | **#3**(수집기 sha `:1006-1010`) · **#8**(`environment_error` `:995-997`) · **#9**(design-input 미지 최상위 필드 `:1084-1085`) · **#16**(backstop ValueError→exit 1 `:308-310`) · **#21**(`refreeze:477-479` staging case v2 요구) · **#24**(journal/plan 손상 `:503-506·526`) · **#25**(`commands:147·152`) · **#26**(`commands:179`) · **#27**(`commands:130` 부채 래칫) |
| 대신 들어온 9행 | §6 1(rv-B #6 «아니오») · 4(#7 «아니오») · 5(rv-B에 없음) · 6(rv-B에 없음) · 8(rv-C B5) · 9(rv-C B4) · 11(#15 «조건부») · 15(rv-B MINOR) · 17(rv-B MINOR) |

특히 **#21은 내 담당 축의 한복판**이다 — `refreeze.py:454-480` `_archive_observation_issues`가
staging의 case마다 `version == 2 and 'interactions' in document`를 **원장과 무관하게** 요구한다 [확인].
§2ⓔ의 단일 지점은 `check_design_evidence`이고 이 검사는 `refreeze.py` 안에 있으므로 원장이 닿지 않는다.
브라우저가 없으면 «재동결하라»가 `check` exit 3에서 끝나고, 그 벽이 표에 없다.
**#25·#26·#27은 md 산문 벽**이라 코드 수리로는 아예 안 열리는데 표에도 없고 §7 배선표의
`commands/dddjango-web.md` 칸(배너 3줄 + 패스트트랙 + ledger 절차)에도 없다.

**수정 방향** ① 표를 rv-B 판정과 실제 1:1로 다시 짓고 빠진 9행에 각각 «포함/제외 + 사유»를 적는다.
② «①(16개 전부 한 사이클)» 승인이 또 다른 집합 위에서 이뤄졌음을 사용자에게 고지하고 범위를 재확정한다.
③ #21·#25·#26·#27은 A8 진행 재개(§8 기준 3)에 직접 걸리므로 제외 사유를 «합격 기준에 닿지 않는다»로
적을 수 없다.

---

### [MAJOR] §4ⓐ·ⓑ는 ⓒ 없이 배포하면 데이터 소실이다 — 설계가 이 순서 의존을 적지 않았다

**무엇이 틀렸나.** §4는 ⓐⓑⓒⓓ를 대등한 네 항목으로 나열한다. 실제로는 ⓐ·ⓑ가 **폐기 집합이 불완전한
채로 교체를 완주시키는 변경**이고, 그 불완전분을 지키는 유일한 그물이 ⓒ다. 계획이 항목별로 병렬
분해되면 ⓐ·ⓑ만 먼저 들어갈 수 있다.

**근거 [실측]** 중첩 증거 문서 1건(`captures/screen-interactions.json`)이 사라진 빌드에서:
```
errors      = ['captures/screen-interactions.json: 파일이 없다']
discard 누락 = ['captures/screen-initial.png', 'captures/screen-step-1.png', 'captures/screen-interactions.json']
orphans     = ['captures/external/lucide.css', 'captures/screen-initial.png',
               'captures/screen-step-1.png', 'captures/smoke-login.png']   ← 상태 캡처 2건이 고아로 강등
begin exit  = 1                       ← 오늘. §4ⓐ는 이걸 0으로 만든다
(§4ⓐ만 적용한 뒤) check exit = 3      ← [refreeze] 증거 문서를 읽을 수 없다: …
```
[확인] 그 뒤 `commit`의 `installed` 단계(`:542-553`)가 staging의 동명 파일로 live의 고아를 덮으면서
원본을 `_prev`로 피신시키고, `_finish`(`:639`)의 `_cleanup`이 `_prev`를 `rmtree` 한다 —
**폐기 집합에 없던 파일이 조용히 영구 삭제된다.** ⓒ가 있어야 한 세대가 남는다.

**수정 방향** §4에 «ⓐ·ⓑ는 ⓒ가 먼저 들어간 뒤에만 유효하다»를 못 박고, 계획서의 커밋 단위를
«ⓒ → ⓐ·ⓑ» 순으로 고정한다.

---

### [MAJOR] §4ⓐ가 «고아는 지우지 않는다»는 규범 약속과 실제 동작의 간극을 키운다

**무엇이 틀렸나.** `commands:138`은 «**고아**(`captures/` 중 어느 포인터에도 없는 파일)는 **지우지 않는다**»를
사용자에게 약속하고 배너 1줄로 보고한다. 그런데 교체는 동명 충돌 시 고아를 덮어쓴다 —
그것이 의도된 동작이라고 회귀가 못 박고 있다(`test_refreeze.py:320-325`
`test_installed_overwrites_name_collision` — 고아 `smoke-login.png`가 staging 바이트로 바뀌는 것을 단언).
§4ⓐ는 «판독 실패한 문서가 가리키던 증거 캡처»를 통째로 고아 집합으로 옮기므로(위 실측), 이 약속과
실제 동작의 간극이 **증거 캡처 전체로 넓어진다.**

**근거** [확인] `refreeze.py:202-211` `orphan_set` = `captures/**` − (discard ∪ preserved) ·
`:546-553` install 충돌 처리 · [실측] 위 항목의 orphans 목록.

**수정 방향** ⓐ가 만드는 «판독 실패 유래 미해소 포인터»를 고아와 **다른 이름**으로 journal에 남기고
(`unreadable_pointers`), 배너에서 «지우지 않음»이 아니라 «재수집 산출물이 같은 이름을 쓰면 교체된다»로
고지한다. 또는 install 충돌 시 고아를 덮지 않고 이름 충돌을 발견으로 올린다.

---

### [MAJOR] §4ⓓ의 값 형식과 정본이 어긋난다 — enum 정본은 `commands:143`의 한글 산문이고 §7 배선표에 그 줄이 없다

**무엇이 틀렸나.** 설계는 `SKIP_REASONS`에 **`no_measurable_dom`**(영문 snake_case)을 넣는다.
그런데 이 enum의 정본은 코드가 아니라 규범이고, 표기는 한글 산문이다.

**근거 [확인]**
- `refreeze.py:48-49`
  ```python
  # 렌더 실측 생략이 합법인 사유 — commands 의 enum 과 같은 닫힌 목록.
  SKIP_REASONS = ('원본 열람 불가', '필요한 인증 상태 접근 불가', '브라우저 채널 부재')
  ```
- `commands/dddjango-web.md:143` / `codex-…/SKILL.md:165` — «**실측 생략이 합법인 사유는 enum이다** —
  원본 열람 불가 · 필요한 인증 상태 접근 불가 · 브라우저 채널 부재(사용자도 실측 불가).
  **그 외 사유는 생략으로 받지 말고 배너에서 재질문한다.**»
- §7 배선표의 `commands/dddjango-web.md` 칸에 **이 줄이 없다**. 코드만 고치면 규범은 여전히
  «그 외 사유는 받지 말라»이므로 Coordinator는 새 값을 쓰지 않는다 — 문이 코드에만 생기고
  집행 규범에는 안 생긴다.

**수정 방향** §7에 `commands:143`·`SKILL.md:165`·`design-acquisition.md:84`를 배선 대상으로 올리고,
새 값의 표기를 기존 세 값과 같은 한글 산문으로 맞춘다(예: «측정할 DOM 없음»).

---

### [MAJOR] `_discarded-<ts>`의 수명·거처가 규정되지 않았다 — 매 재동결마다 A8 기준 7.8 MiB가 git에 들어가고, 지우는 명령이 없다

**무엇이 틀렸나.** §4ⓒ는 «사용자가 지울 때까지 방해 없음»만 적는다. 그런데 이 폴더는
① gitignore 대상이 아니고 ② 커밋 전 확인 목록에 없으며 ③ `refreeze.py`의 어느 서브커맨드도 지우지 않는다.

**근거**
- [실측] `git check-ignore …/_refreeze-20260915-222208` → exit 1(무시 대상 아님).
- [확인] `commands/dddjango-web.md:172` 5단계 — «커밋 전에 각 산출물 폴더에 `_refreeze-*`·`_prev-*`가
  없음을 확인한다». `_discarded-*`가 목록에 없으므로 그대로 커밋된다. 같은 줄이 `.dddjango-web/` 산출물
  일괄 커밋을 지시한다.
- [실측] A8 대상 빌드의 `discard_set` = 67 파일 · **7.8 MiB**(빌드 전체 62 MiB · staging 14 MiB).
- [확인] 부수 효과 — 커밋 전까지 `_discarded-*`는 untracked이므로 `backstop.py:117-122`의
  «untracked/ignored 0» 조건이 깨져 `legacy_v1_allowed`가 False가 된다. legacy v1로 통과하던 빌드에
  새 발견이 생긴다.

**수정 방향** ① `_discarded-*`를 `.gitignore` 대상으로 규정하거나 `commands:172`의 확인 목록에 넣는다
② `refreeze.py`에 `discard-prune`류의 명시적 정리 경로(또는 `abort`의 journal 없는 잔존물 처리와 같은
등급의 정리)를 둔다 ③ 세대 상한(직전 1세대만 보존)을 기계가 강제한다.

---

### [MAJOR] §6 #6의 처분 «A — 검토 문서 재생성»이 실측상 도달 불가다

**무엇이 틀렸나.** `coverage_review` 불일치를 닫으려면 `review_digest`가 필요하고, 그 값은
`--phase prepare`의 stdout으로만 나온다(`check_design_evidence.py:1408-1409`). 그런데 `prepare`도
같은 `validate_inputs`를 지나므로 다른 발견이 있으면 stdout이 없다. §1 표는 `prepare`에 원장을
**적용하지 않는다**고 정했으므로 v3 이후에도 그대로다.

**근거 [실측]** A8 대상 빌드:
```
--phase prepare → EXIT=2 · defect 12건(cases[0..11] v2 요구) · review_digest 출력 없음
--phase inputs  → EXIT=2 · 위 12건 + coverage_review: reviewed-input does not match …
```
[확인] `run()`은 `validate_inputs` 성공 뒤에야 `{'review_digest': …}`를 반환한다.

**수정 방향** #6의 처분을 «A»에서 «#2 의존»으로 바꾸거나, §1 표에 «`prepare`는 원장 적용 대상 발견이
있어도 `review_digest`를 낸다»는 예외를 명문화한다(그 예외가 없으면 부트스트랩 순환이 v3에도 남는다).

---

### [MAJOR] 원장 파일이 재동결 중 어디에 사는지 §4가 정하지 않았다 — step ④가 안 열리거나, 재동결이 승인을 자동 이월한다

**무엇이 틀렸나.** §2ⓐ는 `<빌드 폴더>/evidence-ledger.json`이라고만 적는다. 재동결 중에는
«빌드 폴더»가 둘이다 — live(`<산출물 폴더>`)와 staging(`<대상 폴더>`).

**근거 [확인]**
- 규범 step ④(`commands:138`)는 «**staging을 `--build`로 주어** 입력 게이트를 통과시킨다». 따라서
  그 시점의 원장은 **staging 안**에 있어야 `partition_by_ledger`가 본다. live에 쓰면 step ④가 안 열린다.
- 반대로 staging에 쓰면 `_staging_payload`(`:485-488`)가 그것을 install 대상으로 잡아 live로 옮기므로
  `verified`(`:556-561`)까지는 일관된다.
- 어느 쪽이든 **`evidence-ledger.json`은 `FIXED_DISCARD_FILES`(`:32-36`)에 없다.** 즉 재동결이 원장을
  폐기하지 않는다. `begin`이 live `scope.md`를 staging으로 **바이트 그대로** 복사하므로(`:356-360`)
  §2ⓓ의 `anchor_sha256`도 그대로 일치한다 → **직전 승인이 새 관찰에 자동 이월된다.** 이는
  `commands:138`이 `interaction_exclusions`에 대해 명시적으로 규정한 이월과 같은 성질인데,
  원장은 «규모가 커지면 무효»(§2ⓒ)만 막을 뿐 «분모가 바뀐 새 관찰»은 막지 못한다.

**수정 방향** ① §4에 원장의 재동결 중 거처를 한 줄로 못 박는다(staging 소유 + install로 이월).
② `FIXED_DISCARD_FILES`에 `evidence-ledger.json`을 넣을지, journal의 명시적 이월 대상으로 둘지
결정하고 §7 배선표에 `refreeze.py`의 그 변경을 추가한다(현재 §7의 `refreeze.py` 칸은 «§4 ⓐⓑⓒⓓ»뿐이다).

---

### [MAJOR] §6 line 243의 «제외 5건은 전부 대상 빌드에서 발화하지 않는다»가 실측으로 거짓이다

**무엇이 틀렸나.** 5건 중 **#12가 대상 빌드에서 지금 발화 중**이고, **#15는 `--design-build` 없는
실행에서 8건을 낸다.**

**근거 [실측]** — A8 대상 빌드의 사본(`scratchpad/a8copy/build`)에서 `refreeze.py check` 실행:
```
[refreeze] design-tokens.json
[refreeze] asset-manifest.json
[refreeze] screen-meta.json
[refreeze] design-input.json
[refreeze] render-audit.json
[refreeze] design-input.json: 없다
check EXIT=3
```
이 6건은 전부 `REQUIRED_STAGING`/`pointer_health` — 곧 §6 #12가 가리키는 자리다.
(#12의 사유 «대상 빌드가 dc 경로다»는 «산출물을 만들 수 있다»는 뜻이지 «벽이 안 선다»는 뜻이 아니다.)

#15 [실측] — `--design-build` 없이 돌린 backstop:
```
design-input.json: unreadable (…20260905-2018-web-auth-screens)
manifests[0]: archive inventory differs from frozen tree  ×5 (다른 빌드들)
implementation_digest: stale or incorrect                 ×2 (다른 빌드들)
[backstop] 검사 26종 — blocker 26건 (구조 3 · 시안 23)
```
나머지 3건(#13·#14·#16)은 확인 결과 실제로 발화하지 않는다 [실측] — `discovered` 8건 비어 있지 않음,
`web/` 존재(`implementation_digest` 통과), 4096 미도달.

**수정 방향** line 243을 사실로 고친다 — «#13·#14·#16은 발화하지 않는다 · #12는 **현재 발화 중이며**
재수집으로 닫는다(행동 명시) · #15는 `--design-build`가 필수인 경로에서는 발화하지 않는다».
근거 없는 일괄 문장이 사용자 범위 승인의 입력이 되면 안 된다.

---

### [MINOR] §4ⓒ의 «backstop 접두 목록에서 제외»는 무작업이고, 같은 목록이 두 곳에 중복돼 있다는 사실을 설계가 모른다

**근거 [확인]** `backstop.py:289`의 `startswith(('_refreeze-', '_prev-'))`는 포함형 allowlist다 —
«제외»할 대상이 없다. 같은 목록이 `evidence_debt_hook.py:34` `STAGING_PREFIXES = ('_refreeze-', '_prev-')`
(사용처 `:133-134`)에도 있고, 설계 §7은 hook을 언급하지 않는다. 지금은 두 곳 다 무변경이 정답이지만,
«제외한다»는 문장을 읽은 구현자가 목록에 `_discarded-`를 **추가**하면 `fixtures_backstop.sh:499`
(`_refreeze-…` 고정 픽스처)로는 그 오류가 잡히지 않는다.

**수정 방향** §7의 `backstop.py` 칸에서 «`_discarded-` 접두 제외»를 «변경 없음 — 목록이 allowlist라
새 접두는 자동 제외(회귀 픽스처로 못 박는다)»로 바꾼다.

---

### [MINOR] §6의 «위치» 칸에 행 번호 오류 3건

**근거 [확인]**
- #7 `refreeze:346-352` → 실제 게이트는 **346-351**(`:352`는 `staging = build / …`로 게이트 밖이다).
- #13 «설계 빌드 0 + config 有 → 영구 BLOCKER | `backstop:294-296`» → 설명한 조건의 코드는
  **`backstop.py:281-282`**(`elif configured and not discovered:`)다. `:294-296`은 «빌드 디렉터리/증거가
  없음»으로 다른 발견이다. rv-B는 #14를 `:281-282`로 정확히 적었다.
- #9 «`_finish`의 `_prev` 삭제 | `refreeze:639`» → 실제 `rmtree`는 `_cleanup`(`:619-621`)이고
  호출처가 **둘**이다(`:530`의 done-재개 분기 · `:639`). 한 줄 인용이 두 번째 호출처를 가린다
  (그 결과가 위 BLOCKER 1이다).

---

### [MINOR] §6 #5는 하드월이 아니라 과허용이다 — «하드월 전수 표»의 행수를 채우는 데 쓰였다

**근거 [확인]** `check_design_evidence.py:875-879`는 `approval_quote`가 10자 미만이거나 `scope.md`에
없으면 **발견을 낸다**. 즉 그 자리는 «열리지 않는 벽»이 아니라 «너무 헐겁게 열리는 문»(rv-A B3의 축)이다.
그런데 §6은 이 행에 «**L**(원장으로 열림) + §2ⓓ가 오히려 조인다»라는 **서로 반대 방향의 두 처분**을
한 칸에 적었다. 표의 정의(«하드월 전수»)와 행의 성질이 어긋나며, 17이라는 수의 근거를 흐린다.

---

### [MINOR] §7의 `fixtures_refreeze*.sh` 복수형이 실체와 다르다

**근거 [확인]** `dddjango-web/scripts/test/fixtures_refreeze.sh`는 **7줄짜리 러너**로
`python3 test_refreeze.py`만 부른다. 단언은 전부 `test_refreeze.py`에 있다. §7이 «`fixtures_refreeze*.sh`
§4 회귀 추가»로 적으면 구현자가 셸 픽스처에 단언을 쓰게 되고, 그것은 이 저장소의 판형이 아니다.
(`verify-web`은 `run_fixtures.sh` → 각 `fixtures_*.sh` → 파이썬 시험 순이다 — `Makefile:91-95` [확인].)

---

### [MINOR] 회귀 답 — §4의 네 변경이 깨는 기존 단언은 **0건**이다. 그것이 곧 BLOCKER 1의 위험이다

**근거 [확인/실측]** `test_refreeze.py`(520행)·`fixtures_refreeze.sh` 전수 대조:

| §4 | 접촉하는 기존 단언 | 결과 |
|---|---|---|
| ⓐ `begin` 판독 실패 진행 | 판독 실패의 exit 1을 못 박은 시험 **없음**(`test_bom_in_design_input_is_not_silently_swallowed:397`은 `discard_set` 내용만 본다) | 깨지지 않음 |
| ⓑ `check` 경고 강등 | `test_self_check_discard_covers_pointers:264`는 **자기 검사** 줄만 본다(판독 실패 줄이 아니다) | 깨지지 않음 |
| ⓒ `_prev` 개명 | `test_full_swap:298` · `test_resume_after_stop_at_verified:377` · `test_install_backup_never_overwrites_an_existing_prev_original:425` 모두 `glob('_prev-*')`가 **비었는지**만 단언 — 개명해도 통과 [실측] | 깨지지 않음 |
| ⓓ enum 추가 | `test_render_audit_skip_reason_must_be_enum:411`은 enum 밖 값만 본다 | 깨지지 않음 |

즉 **BLOCKER 1에서 재현한 «live 빌드 소실» 상태를 잡는 그물이 현재 스위트에 하나도 없다.**
§7이 예고한 «§4 회귀 추가»는 최소 다음 세 시험을 포함해야 한다: ① `_discarded-*`가 남은 상태에서
`commit`이 **새 교체를 시작하지 않는다** ② `_discarded-<ts>` 이름 충돌에서 `_cleanup`이 죽지 않는다
③ 개명 직후 중단 뒤 `commit --resume`이 exit 0으로 정리만 한다.

---

## 요약 — 사용자 구속 지시 대비 판정

«재동결하라 → 차이 있으면 고치게 하라»가 §4 구현 후 A8에서 어떻게 되는지 [실측 기반 추적]:

| 단계 | 결과 |
|---|---|
| `begin` | 이미 staging이 있어 재실행 불가(exit 2). 현행 staging으로 이어가야 한다 |
| 재수집 | dc 경로이므로 가능 — 단 `design-tokens.json`·`asset-manifest.json`·`screen-meta.json`·`design-input.json`·`render-audit.json`을 staging에 새로 만들어야 한다 |
| `check` | **지금 exit 3(6건)** — §4ⓐⓑⓒⓓ 어느 것도 이 6건에 닿지 않는다(§6 #12는 X) · 재수집 완료 후엔 `_archive_observation_issues`(§6 미수록, 원장 밖)가 12 case의 v2를 요구한다 |
| step ④ inputs | 원장이 열 수 있다 — **단 원장 파일이 staging에 있어야 한다**(§4 미규정) |
| `commit` | verified 통과 → `_finish` → §4ⓒ. **그 자리에 BLOCKER 1이 있다** |
| G2·마무리 backstop | **열리지 않는다** — backstop이 원장을 보지 않고(BLOCKER 3), 다른 빌드의 `_prev-20260907-2302` 잔존물이 프로젝트 전역 BLOCKER다(BLOCKER 2) |

**§4·§6·§7만으로는 «재동결 → 대조 → 수정»의 행동열이 완결되지 않는다.**

<!-- 도구 사용: 워크트리 루트에 `.serena/project.yml`·`graphify-out/graph.json`이 없어 Serena·Graphify 미사용(기본 읽기·검색 도구와 읽기 전용 실행으로 확인). A8 워크트리는 읽기 전용 조회와 read-only 검사기 실행만 수행(쓰기 0) — `refreeze.py check`는 scratchpad 사본에서 실행했다. -->
