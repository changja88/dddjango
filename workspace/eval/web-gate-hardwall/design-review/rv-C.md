# 적대 검토 C — v2의 두 원칙이 코드에 닿는가 (2026-09-15)

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` **v2**
선행: `rv-A.md`(BLOCKER 3·MAJOR 5·MINOR 4) · `rv-B.md`(BLOCKER 6·MAJOR 8·MINOR 5) — 중복 지적 없음.
표기: **[실측]** = 이 검토에서 명령을 실행해 얻은 결과 · **[확인]** = 코드·실물 파일 직독 · **[추론]** = 코드에서 따라 나오는 결론.

등급: **BLOCKER 5 · MAJOR 7 · MINOR 3**

---

### [BLOCKER] 원칙 ②에는 집행 지점이 없다 — «진행 허용»과 «완료 금지»를 가르는 축이 코드에 존재하지 않는다

**무엇이 틀렸나.** §2는 «`level: partial` 이면 진행은 되지만 `build-state.json` 의 완료 전이가 막힌다 ·
마무리 backstop(벽 28)은 그대로 둔다»고 적는다. 그런데 벽 25·26(진행)과 벽 28(완료)은 **같은 함수의 같은 판정**이다.

구체 시나리오: `evidence_scope`를 적어 잔여 153건을 부분 검증 지위로 통과시킨다.
→ coder 호출 직전 `--phase inputs`가 exit 0이 되어야 슬라이스가 돈다(벽 26).
→ 그런데 마무리 backstop도 **같은 `validate_inputs`를 인자 없이** 부른다. 발견이 0이므로 exit 0이다.
→ 완료가 막히지 않는다. 반대로 발견을 남기면 coder 호출이 막혀 «진행은 언제나 가능»이 깨진다.
**둘 중 하나만 가능하고, 설계는 둘 다 주장한다.**

**근거**
- `dddjango-web/scripts/check_design_evidence.py:1398-1403` — `run()`이 `validate_inputs(build, project, require_review=args.phase != 'prepare')`. `--phase`는 `validate_inputs` **안으로 들어가지 않는다**. 발견 집합이 prepare/inputs/visual에서 동일하다 [확인].
- `dddjango-web/scripts/backstop.py:300` — `validate_inputs(build, root, legacy_v1=legacy_v1)`. coder 입장(`agents/coder-web.md:44-45`)·Coordinator freshness(`commands/dddjango-web.md:179`)가 부르는 것과 **같은 함수·같은 발견** [확인].
- `commands/dddjango-web.md:186`(G2 배너 직전)과 `:191`(마무리)의 backstop 명령줄이 **문자 그대로 같다** — `--diff-base <git_snapshot> --design-build <산출물 폴더>`. 인자로 «마무리»를 가려낼 수 없다 [확인].
- 남는 자리는 `build-state.json`뿐인데 `check_design_evidence.py`는 이 파일을 **한 번도 읽지 않는다**(`grep -n "build-state" scripts/check_design_evidence.py` → 0건) [실측].
- 그 파일이 기질이 못 되는 실물 증거: A8 관계인 빌드의 `build-state.json.implementation_visual`이 **스키마 밖 값 `"pass"`**다(정본 enum은 `pending|verified|failed|unverified` — `commands:68`) [실측]. 그 결과 `refreeze.py:626-627`의 «완료 빌드 재동결 → pending 강등»도 이 빌드에서는 발동하지 않는다.

**수정 방향**
1. 완료 전용 축을 **기계 인자로** 만든다: `validate_inputs(..., stage='work'|'done')`을 신설하고 `evidence_scope`는 `stage='work'`에서만 발견을 눌러 준다. backstop에 `--finalize`를 추가해 `commands:191`만 그 인자를 쓰게 하고 `:186`은 쓰지 않는다 — 두 호출의 명령줄이 달라지는 것이 이 설계의 **선결 조건**이다.
2. 대안으로 `validate_visual`(backstop과 `--phase visual`만 부르는 유일한 함수 — `check_design_evidence.py:1282`)에 완료 금지를 둘 수 있으나, `commands:184`가 G2 **전에** `--phase visual`을 돌리므로 «진행 금지»가 된다. 설계가 이 충돌을 먼저 해소해야 한다.
3. 어느 쪽이든 «완료 금지»를 `build-state.json`에 두지 않는다 — 검사기 미독·에이전트 소유·실물에서 이미 값이 오염돼 있다.

---

### [BLOCKER] 실측 — A8 빌드를 v2대로 고쳐도 열리지 않는다. 지금 막는 발견 13건 중 §2·§3이 닿는 것은 0건이다

**무엇이 틀렸나.** 이 수리의 대상 빌드에서 `--phase inputs`가 내는 발견은 **잔여도, 표면 미연결도, 10% 상한도 아니다.**
전부 «조작 상태 관찰 v2 부재»(rv-B 벽 #2)와 «독립 검토 digest 불일치»다. §2의 문은 `_check_exclusions` 안의 상한 위에만 났고,
이 발견들은 그 함수 밖에서 난다.

**근거** [실측] — `/Users/hyun/.herdr/worktrees/spring_dream_server/a8`에서 읽기 전용 실행:

```
$ check_design_evidence.py --build .dddjango-web/20260912-1640-web-related-persons \
                           --project-root . --phase inputs      → exit 2
[design-evidence] defect: cases[0..11].source_observation: interaction evidence required (version 2 with interactions)   (12건)
[design-evidence] defect: coverage_review: reviewed-input does not match current source/cases/observations              (1건)
$ … --phase prepare                                              → exit 2 (같은 12건)
```
- 12 case 전부 `source_observation.version == 1` [실측]. 발화 지점은 `check_design_evidence.py:1048-1051`(`_source_observation` 안) — `_check_exclusions`(`:849`)가 도달하기 전에 이미 issues에 쌓인다. `evidence_scope`는 이 발견을 건드릴 수 없다 [확인].
- v2 §1 처분표에 **rv-B 벽 #2가 없다**. §3은 `refreeze.py` 전용이라 `--phase inputs` 경로를 열지 않는다 [확인, 설계 원문].
- `prepare`도 같은 12건으로 exit 2 → `review_digest`가 나오지 않는다 → `coverage_review` 발견도 닫을 수 없다. **부트스트랩 순환이 실물에서 성립** [실측].

**수정 방향** `evidence_scope.level`에 «관찰 없음»을 넣고 `_source_observation:1048-1051`을 같은 문에 붙이거나(rv-B가 제안한 축),
§1 표에 벽 #2·#3(수집기 sha)·coverage_review 재발급 순환을 명시적으로 올린다. 지금 설계는 **대상 빌드를 열지 못한다.**

---

### [BLOCKER] §1 표의 «16개»는 rv-B가 센 하드월 집합이 아니다 — rv-B의 «예» 17개 중 9개가 빠지고, «아니오» 9개가 들어왔다

**무엇이 틀렸나.** 설계 line 7-8은 «rv-B 의 전수 조사가 실질 하드월 **16개**를 찾았다»고 적는다.
rv-B의 실제 결론은 «행 30 · 실질 하드월 «예» **17** · 조건부 4 · 아니오 9»다. 16이라는 수는 rv-B에 없다.
그리고 §1 표의 16행을 rv-B 판정과 대조하면 **집합이 치환돼 있다**:

| | rv-B 판정 | §1 표 |
|---|---|---|
| 들어온 것 | «아니오» 9행(6·7·10·17·22·28·29·30 …) | 전부 수록 |
| 빠진 것 | «예» 9행 — **#2**(v2 관찰 부재) · **#3**(수집기 sha) · #8(`environment_error`) · **#9**(design-input 미지 최상위 필드) · #11(`web/` 부재) · #13(4096 파일) · #14(빌드 폴더 삭제) · #16(backstop ValueError→exit 1) · #24(journal/plan 손상) | 표에 없음 |

사용자의 «① 16개 전부 한 사이클» 확정이 **이 치환된 집합 위에서** 이뤄졌다. 범위 승인의 근거가 어긋난다.

특히 **#9는 이 설계가 스스로 만드는 벽**이다: `evidence_scope`는 `validate_inputs`의 `allowed` 밖이므로
(`check_design_evidence.py:1083`) 구판 설치본이 신판 산출물을 읽으면
`raise Defects(['design-input.json: invalid top-level fields'])`(`:1084-1085`)로 **다른 발견이 전부 지워진 채** exit 2가 된다 [확인].
메모리 기록상 «설치본 갱신»은 반복 미완 항목이므로 이건 가정이 아니라 예정된 상태다.

**수정 방향** ① 표를 rv-B 판정과 1:1로 다시 맞추고 빠진 9행 각각에 «이번 사이클 포함/제외 + 제외 사유»를 적는다.
② 사용자에게 «승인한 16개는 rv-B의 17개가 아니다»를 고지하고 범위를 재확정한다.
③ #9는 이번 수리가 만드는 벽이므로 같은 사이클에 필수다 — `design-input.json.version`을 2로 올리고 미지 필드 메시지에 판형 스큐 진단을 붙인다.

---

### [BLOCKER] §3의 «폐기 후 기록» × §2의 «부분 검증 통과» = 되돌릴 수 없는 폐기

**무엇이 틀렸나.** §3은 «수집 경로가 없는 출처(이미지 단독 등)는 **폐기 후 그 사실을 기록**한다»고 적는다.
재동결 교체에서 폐기 원본을 지키는 안전핀은 **단 하나**, `verified` 단계의 `verify_inputs`뿐이다.
그리고 §2는 정확히 그 exit를 무르게 만드는 장치다. 둘이 같이 들어가면 안전핀이 풀린 채 폐기가 확정된다.

구체 시나리오: 이미지 단독 빌드에서 «재동결하라». `begin`이 폐기 집합을 잡고, 재수집 경로가 없으므로 §3대로 «없음»을 기록하고 `check`를 통과한다.
`commit`이 `discarded`(원본 → `_prev`) → `installed`(빈약한 staging) → `verified`에서 `--phase inputs`를 돌린다.
여기서 §2의 `evidence_scope`가 «부분 검증 지위»로 exit 0을 내면 → `done` → `_finish` → **`_cleanup`이 `_prev`를 `rmtree`** 한다. 폐기 원본은 영구히 사라진다.

**근거**
- `dddjango-web/scripts/refreeze.py:556-561` — `verified` 실패 시에만 `_rewind`. 통과하면 되감기 경로가 없다 [확인].
- `:624-639` `_finish` → `:619-621` `_cleanup` → `shutil.rmtree(prev, ignore_errors=True)` [확인].
- `:326-334` `verify_inputs`는 `check_design_evidence.py --phase inputs`의 returncode만 본다 — §2가 그 exit를 바꾸면 안전핀이 그대로 바뀐다 [확인].
- 규모 [실측]: A8 관계인 빌드의 진행 중 journal `discard_set` = **67 파일**(원본 캡처·관찰 문서·design-ref 포함).

**수정 방향**
1. `_finish`가 `_prev`를 지우지 말고 `_discarded-<ts>/`로 **한 세대 보존**한다(사용자가 지우기 전까지). backstop의 잔존물 BLOCKER(`backstop.py:286-293`) 접두 목록에서는 제외한다.
2. `verify_inputs`는 `evidence_scope`를 **무시하는 엄격 모드**로 돈다 — 교체 후 검증은 «부분»을 받지 않는다.
3. §3의 «폐기 후 기록»은 «폐기 **보류** 후 기록»으로 바꾼다 — 수집 경로가 없으면 그 산출물은 폐기 집합에서 빼고 journal에 «재동결 대상 아님»으로 남긴다.

---

### [BLOCKER] §3이 `begin`만 고치고 `check`를 고치지 않아 벽이 한 칸 뒤로 밀린다

**무엇이 틀렸나.** §3은 «`begin`의 증거 판독 실패 → 거부가 아니라 «판독 불가 목록»으로 기록하고 진행»만 적는다.
그런데 같은 판독을 `check`가 **live 빌드에 대해 다시 돌린다.** `begin`을 통과시켜도 `check`가 같은 이유로 exit 3을 내고,
`commit`은 `check` 없이는 거부하므로(`:509-511`) 결과는 오늘과 같다 — 사용자는 `abort`밖에 못 한다.

게다가 §3대로 판독 실패 포인터를 `discard_set`에서 빼면 `check`의 «폐기 집합 자기 검사»가
**정확히 그 파일들을 발견으로 올린다**: `set(live) - covered - preserved_set(build)`.

**근거**
- `dddjango-web/scripts/refreeze.py:434-437`
  ```python
  live = [rel for rel in evidence_pointers(build, errors) if (build / rel).is_file()]
  issues.extend(f'증거 문서를 읽을 수 없다: {issue}' for issue in errors)
  issues.extend(f'폐기 집합 자기 검사: 포인터가 빠졌다 ({rel})'
                for rel in sorted(set(live) - covered - preserved_set(build)))
  ```
  `evidence_pointers`가 `begin`과 같은 `_read_document`(`:91-105`)를 쓰므로 같은 오류가 다시 난다 [확인].
- `:438-441` — issues가 하나라도 있으면 exit 3 [확인].

**수정 방향** `journal`에 `unreadable[]`을 신설하고, `check`가 ① 그 rel들을 자기 검사 대상에서 제외하고
② `errors` 중 `unreadable[]`에 이미 기록된 것은 issue로 승격하지 않게 한다. §3의 문장을
«`begin`·`check` 두 곳에서 같은 목록을 쓴다»로 명시하라 — 한 곳만 고치면 벽이 이동할 뿐이다.

---

### [MAJOR] rv-A의 «게으른 길»(B2)이 v2에서도 살아 있다 — «`active` 단조 감소 금지»는 정직한 쪽만 벌한다

설계 line 21-22는 «②가 rv-A 의 BLOCKER 1·2 를 막는다»고 적는다. B2는 막히지 않는다.

**무엇이 틀렸나.** 단조 감소 금지는 **직전 회차가 있을 때만** 작동한다. 첫 관찰 회차를 `--max-minutes 8` 한 번으로 끊으면
그 얕은 값이 **최대치 기준선으로 박힌다.** 이후 늘어나는 것은 허용이므로 벌점이 없다.
반대로 성실하게 전부 연 뒤 범위를 줄인 빌드만 발견을 맞는다. 인센티브의 방향이 여전히 거꾸로다.

그리고 v2 어디에도 `caps_hit`·`partial` 조건이 없다 — rv-A가 지목한 «상한에 걸린 수집은 «못 본 것»이 아니라 «안 돌린 것»»이 그대로 남는다.
증거 부채 술어도 손대지 않는다: `evidence_debt.py:27-29` `version == 2 and 'interactions' in observed` — **8분짜리 절단 관찰이 부채를 0으로 만든다** [확인].

**근거**
- `assets/observe_interactions.pw.js:28` `DEFAULT_LIMITS = { maxSteps: 8000, maxDepth: 24, maxMinutes: 90 }` · `commands:144`가 «호출 1회에 `--max-minutes 8` · exit 3이면 `--resume`»을 지시하지만 잇는 행위를 강제하는 기계가 없다 [확인].
- «최대치»의 저장처로 §2가 지목한 `build-state.json`은 검사기가 읽지 않는 에이전트 소유 파일이다(위 BLOCKER 1의 근거) [실측].

**수정 방향** ① `caps_hit`가 비어 있지 않은 문서는 `evidence_scope`로 덮을 수 없다는 조건을 §2에 명문화한다.
② 부채 술어를 «v2 존재»에서 «v2 + `caps_hit` 없음 + 잔여 0 또는 승인된 부분 지위»로 올린다.
③ 기준선은 `build-state.json`이 아니라 `_history/`의 직전 관찰 문서에서 **검사기가 직접 센다**.

---

### [MAJOR] §2 ⓒ «숫자를 포함해야 한다»는 기계 검사로 거의 무의미하다 — 실측으로 rv-A의 반례가 그대로 통과한다

**무엇이 틀렸나.** «승인자가 규모를 봤다는 증거»로 «숫자 포함»을 요구하는데, 검사는 «10자 이상 · `scope.md`에 실재 · 숫자 1개 이상»일 뿐이다.
아무 숫자나 통과한다 — 커밋 해시·버전 번호·경로의 숫자·날짜 전부.

**근거** [실측] — A8 실물 `scope.md`(13,144 bytes)에 검사기의 `_collapse`를 그대로 적용해 «10자 이상 + 숫자 포함 + 원문 실재» 줄을 세었다:

```
후보 63줄 통과. 표본:
  '- anchor(base 커밋 = 발주서 커밋): `ace3a9ab`'                  (38자)
  '- 적재 플러그인: `dddjango-web@changja88-dddjango` **1.1.10**'   (55자)
  '- 커밋: `git -c core.hooksPath=/dev/null commit` · **push 0**.'  (60자)
```
마지막 줄은 **rv-A가 반례로 든 바로 그 줄**이다 — «push 0»의 `0` 때문에 §2 ⓒ를 그대로 통과한다 [실측].

ⓐ «전용 앵커 절»도 출처를 증명하지 못한다: `scope.md`는 Coordinator가 쓰는 산출물이고(`commands:9`·`:235`),
앵커 절을 만드는 주체와 인용을 고르는 주체가 같다. 그리고 `commands:138`의 재동결 규범
«`approval_quote`·`scope_ref`는 staging `scope.md`에서 **재사용**하고 단위 키만 새 id에 맞춘다»가 그대로라
재동결이 승인을 자동 이월한다 — rv-A B3의 처방 3을 v2가 반영하지 않았다 [확인].

**수정 방향** «숫자 포함»을 «**수치 일치**»로 바꾼다 — 인용문 안의 정수 중 하나가 검사기가 센 `unverified`와 같아야 한다.
그리고 `commands:138`의 재사용 규칙에서 `evidence_scope`와 상한 관련 quote를 명시적으로 **제외**한다(분모가 바뀌면 승인도 새로).

---

### [MAJOR] §2의 «case `scope_ref` 앵커 검증도 함께 메운다»가 바로 이 빌드에 새 벽 12개를 세운다

**무엇이 틀렸나.** §2 마지막 줄이 «기존 예외 행의 `scope_ref` 앵커 검증 누락(case 측 `:1206-1207`)도 함께 메운다»고 적는다.
이 검사를 켜면 A8 관계인 빌드가 **즉시 발견 12건을 추가로 받는다.** 하드월을 걷어내는 작업이 대상 빌드를 더 닫는다.

**근거** [실측] — A8 8개 빌드 전수:

```
20260907-2249-home-bottom-nav      cases=10  앵커불일치 0
… (6개 빌드 모두 0) …
20260912-1640-web-related-persons  cases=12  앵커불일치 12   ← 이번 수리의 대상 빌드
```
- 그 빌드의 case `scope_refs` = `scope.md#related_persons` · `scope.md#preferences`.
- `scope.md`의 실제 앵커 12개는 전부 한글 슬러그(`디자인-출처` · `실행-경계사용자발주서-제약` · `필수-동작발주서-3` …) — 두 값 모두 없다 [실측].

**수정 방향** 이 보강은 **별건으로 분리**한다. 같은 사이클에 넣을 거면 기존 빌드의 이행 절차(앵커 추가 또는 grandfather 조건)를 §2에 함께 적고,
그 이행 자체가 «여는 행동»으로 이름이 붙어야 한다.

---

### [MAJOR] §4 부분 상환은 §1이 열지 않은 벽(#2)에 의존한다 — 혼합 판형 빌드는 case 단위로 막힌다

**무엇이 틀렸나.** §4는 «이번에 만질 case만 관찰하고 나머지는 부채로 남긴다»고 한다.
그런데 v2 관찰 요구는 **case마다** 발화하고(`_source_observation`), 레거시 허용은 **빌드 단위 bool**이다.
12 case 중 4개만 상환하면 나머지 8개가 그대로 exit 2를 낸다 — 부분 상환한 빌드는 어떤 coder 호출도 통과하지 못한다.

**근거**
- `check_design_evidence.py:1048-1051` — case 루프 안에서 case마다 발화 [확인].
- `backstop.py:95-123` `legacy_v1_allowed` → `validate_inputs(..., legacy_v1=...)`는 빌드 하나에 bool 하나. checker CLI에는 그 인자가 아예 없다(`main:1419-1424`의 파서는 `--build`·`--project-root`·`--phase`·`--fingerprint`뿐) — 즉 coder·Coordinator가 부르는 `--phase inputs` 경로에는 레거시 문이 **없다** [확인].

**수정 방향** §4를 쓰려면 «부분 상환 중인 빌드의 미상환 case는 `evidence_scope`가 덮는다»를 §2와 **한 문장으로 묶어야** 하고,
그 덮개는 벽 #2에 닿아야 한다. 지금 설계에는 그 연결이 없다.

---

### [MAJOR] §5의 «차단 지점 정적 수집»은 오탐·미탐이 동시에 크고, `web_refreeze_contract.py` 판형과 다른 종류의 도구다

**무엇이 틀렸나.** «검사기들의 차단 지점을 정적 수집하고 각 지점이 «여는 행동»을 문자열로 명시하는지 검사한다.
명시 없는 차단이 1건이라도 있으면 red»는 지금 코드베이스에서 **첫날 red 200건대**를 낸다. 그리고 red의 대부분은 벽이 아니다.

**근거** [실측] — `dddjango-web/**/*.py`를 AST로 훑어 `issues/design_defects/messages.append`와 `Defects`·`RefreezeError` 생성 인자의 문자열 리터럴을 수집(프로토타입: `scratchpad/doors_probe.py`):

```
정적 수집된 차단 발화 지점: 213
  그중 조치 플래그(--)·문서 앵커(#/.md) 포함:   8  (3%)
  명시 없음(= 신설 검사가 red를 낼 건수):     205
     check_design_evidence.py 191 · refreeze.py 13 · backstop.py 1
표본: 'nonempty relative path required' · 'path escapes root' · 'design-input.json: invalid top-level fields'
```

- **오탐**: 위 표본은 «네가 쓴 JSON 모양이 틀렸다»이지 하드월이 아니다. 여기에 조치 문구를 다는 것은 규범 개선이 아니라 문자열 채우기다.
- **미탐 ①**: `_exact`(`check_design_evidence.py:425-432`) **한 자리**가 수십 개의 서로 다른 사용자 대면 발견을 만든다. 그 한 줄에 조치 문구를 달면 수십 개 벽이 «명시됨»으로 green이 된다.
- **미탐 ②**: 원칙 ②가 기대는 벽 #25·#26·#27·#28은 **md 산문**이고 #30은 js다. 파이썬 정적 수집이 못 본다 — `commands/dddjango-web.md`에 «exit 0» 요구 9곳, `agents/coder-web.md`에 3곳 [실측].
- **판형 불일치**: `workspace/tools/web_refreeze_contract.py`는 «모든 차단»을 수집하지 않는다. 6~8개 파일 위의 **이름 붙은 불변식 7종**(A 유보↔재동결 · B 폐기 어휘 잔존 0 · C 서브커맨드 실재 · D1~D4 자리표시자 치환)과 구간 앵커 생존 검사(`:248-259`), 합성 픽스처 self-test(`:283-300`)다 [확인].

**수정 방향** 같은 판형을 쓰려면 대상을 바꾼다 — «모든 차단이 문을 명시하는가»가 아니라
**«이번에 연 16개 문이 닫히지 않았는가»**를 이름으로 고정한다(예: `_check_exclusions`의 상한 줄 위에 `evidence_scope` 분기가 실재하는가 ·
`cmd_begin`에 `unreadable` 기록 경로가 실재하는가 · `commands`의 «inputs exit 0» 요구 옆에 부분 지위 예외 문장이 실재하는가).
그리고 md·js도 대상에 넣는다 — 그러지 않으면 원칙 ②가 사는 파일들이 불변식 밖이다.

---

### [MAJOR] §1 «A» 재심 — 4·5의 «고쳐 재수집»은 브라우저가 있을 때만 문이다. 없으면 «여는 행동»이 위조뿐이다

**무엇이 틀렸나.** #4(`outside_root.count > 0`)·#5(`root.found ≠ true`)의 처분이 «A — 손대지 않음(문이 이미 있다)»인데,
그 문은 **드라이버 재실행**이다. `outside_root`·`root`는 사람이 쓰는 값이 아니라 수집기가 문서에 쓰는 필드이고,
`--excluded-regions`를 고쳐도 **다시 관찰해야** 반영된다.

`commands:144`는 브라우저 부재를 **정상 상태로 이미 인정한다** — exit 1 사유 enum에 «playwright 모듈 부재 · 브라우저 기동 불가»가 있고
«플러그인은 Playwright·브라우저를 설치하지 않고 경로만 받는다»고 적는다 [확인]. 그 상태에서 #4·#5의 문은 존재하지 않는다.

문서를 손으로 고치는 길은 **기계적으로는 열려 있다**(interactions.json sha → 관찰 문서 → `design-input.json`의 3겹 재봉인이 전부 Coordinator 소유다 — `refreeze.py:108-129`가 도는 바로 그 사슬) [추론].
즉 브라우저 없는 환경에서 «여는 행동»은 **증거 위조뿐**이다. 원칙 ①의 «이름으로 댈 수 있는 행동»이 이것이면 원칙이 무너진다.

**수정 방향** 표의 A 칸에 «(브라우저 가용 시)»를 명시하고, «환경상 재수집 불가»를 §2의 부분 검증 지위가 받는 축에 포함시킨다.
§3이 벽 21에 대해 이미 그렇게 적었으므로(«재수집이 불가능한 환경이면 §2의 부분 검증 지위로 진행») 같은 문장을 #4·#5에도 적용하면 된다 — 지금은 안 적혀 있다.

---

### [MAJOR] §1 «A»인 #15의 실제 문은 «사용자 지시의 취소»뿐이다 — 실물에서 그 상태가 지금 성립해 있다

**무엇이 틀렸나.** #15(`_refreeze-*`/`_prev-*` 잔존 → 프로젝트 전역 BLOCKER)의 처분이 «A — `commit --resume`/`abort`»인데,
재수집이 미완인 staging에서 `commit`은 불가능하다. 남는 행동은 `abort` = **재동결을 버리는 것**이다.
사용자 지시가 «재동결하라»인데 유일하게 실행 가능한 행동이 «재동결을 취소하라»면 그 문은 지시를 충족하지 않는다.

**근거** [실측] — A8 관계인 빌드에 재동결이 **지금 진행 중**이다:
```
_refreeze-20260915-222208/   captures/ · design-ref/ · journal.json · scope.md · source-manifest.json
journal: checked_at=None · discard_set=67 · orphans=7 · quote='native 없이 커스텀으로만 진행 — 4개 Select 공용 부품 커스텀화'
staging 부재: design-tokens.json · asset-manifest.json · screen-meta.json · design-input.json  (REQUIRED_STAGING 5종 중 4종)
```
- `check` → `refreeze.py:425-427`이 그 4종을 missing으로 올려 exit 3 [확인].
- `commit` → `:509-511` `journal.checked_at` 없음 → RefreezeError exit 1 [확인].
- 그동안 `backstop.py:286-293`이 **프로젝트 전역** BLOCKER를 내므로 트리비얼 패스트트랙(`commands:220`)까지 같이 막힌다 [확인].

**수정 방향** #15를 A에서 C로 올린다 — 잔존물 BLOCKER를 «미완 재동결 진행 중»이라는 **notice**로 내리고,
차단은 «커밋·마무리 시점»에만 건다. 지금은 조회·트리비얼까지 같은 벽 뒤에 있다.

---

### [MINOR] #10의 «A — 재동결·파일 정리»가 서로 다른 두 벽을 한 칸에 덮었다

`manifests: exactly one full-tree archive manifest`(`check_design_evidence.py:1122-1123`)는 `design-input.json` 편집으로 닫히지만,
`archive inventory differs from frozen tree`(`:1170-1172`)는 동결 트리 자체와의 불일치라 **재동결이 유일한 문**이고,
그 재동결은 §3 수리 전에는 `REQUIRED_STAGING`·`begin` 판독 벽을 지난다(rv-B BLOCKER 3·5). 즉 후자는 A가 아니라 §3 의존이다 [확인].
표에 의존 관계를 적어야 계획 단계에서 두 벽이 분리되지 않는다.

---

### [MINOR] #17의 «CLI 플래그 신설(사용자가 못 켠다)»가 마스터키가 될 수 있다 — 설계가 AND인지 대체인지 적지 않았다

`legacy_v1_allowed`(`backstop.py:95-123`)는 git 추적·diff-base 대비 무변경·untracked/ignored 0을 모두 요구한다.
새 플래그가 이 조건을 **대체**하면 아무 빌드나 v1 관찰로 통과한다 — 벽 #2가 전면 무력화된다.
플래그가 조건에 **AND로만** 붙는다는 것을 §1 표 각주에 못 박아야 한다 [확인 — 설계 원문에 없음].

---

### [MINOR] #22 «A — `check` 통과»는 #21·추가 2·3이 §3으로 실제 열린 뒤에만 참이다

`cmd_commit:509-511`의 문은 `cmd_check` 통과인데, `cmd_check`는 `REQUIRED_STAGING`(`:425-427`) ·
`_archive_observation_issues`(`:454-480`) · 렌더 실측 enum(`:442-446`)을 모두 지나야 한다 — 그 셋이 §3의 수리 대상이다.
표가 의존 순서를 적지 않아, 계획이 항목별로 병렬 분해되면 #22가 red로 남는다 [확인].

---

## v2가 실제로 해소한 것 / 못 한 것 (선행 검토 대조)

| 선행 지적 | v2 처분 | 검증 결과 |
|---|---|---|
| rv-A B1 «천장 없음» | §2 «완료 금지»로 대체 | **미해소** — 집행 지점 없음(BLOCKER 1) |
| rv-A B2 «게으른 길» | §2 «active 단조 감소 금지» | **미해소** — 첫 회차 기준선·`caps_hit` 무조건(MAJOR 1) |
| rv-A B3 «approval_quote» | §2 ⓐⓑⓒ 강화 | **부분** — ⓒ는 실측 무력, 재동결 이월 미차단(MAJOR 2) |
| rv-A MAJOR «H2 정당성 반증» | §6에서 **H2 기각** | **해소** — `owner_items_hash` 집행 사실을 정확히 반영 |
| rv-A MAJOR «접기 분모/부담» | H2 기각으로 소멸 | **해소** |
| rv-A MAJOR «design-review-web 배선 누락» | — | **미해소** — v2에도 배선표가 없다(§2 신설 필드에 대한 리뷰어 charge 부재) |
| rv-B B1 «관찰 불가 축» | 표에서 제외 | **미해소** — 대상 빌드가 정확히 이 축(BLOCKER 2) |
| rv-B B3 «.dc 전용» | §3 일반화 | **부분** — `design-ref/` 요구(`:422-424`)는 discard_set 밖이라 남는다 |
| rv-B B4 «렌더 enum» | §3 enum 추가 | **해소 가능** — 구현 시 `SKIP_REASONS`(`:49`) 한 줄 |
| rv-B B5 «begin 거부» | §3 «기록하고 진행» | **부분** — `check`가 다시 막는다(BLOCKER 5) |
| rv-B MAJOR «설치본 스큐» | 표에서 제외 | **미해소** — 이 설계가 만드는 벽(BLOCKER 3) |
| 진단 H1 «10% 상한» | §2 부분 검증 지위 | 방향은 유효하나 대상 빌드에서 이 벽은 **발화조차 하지 않는다**(BLOCKER 2) |

---

## §7 열린 질문에 대한 답

**Q1 — `evidence_scope`는 빌드 1건인가 문서별인가.**
**문서별로 기록·승인하고 빌드 라벨은 문서 라벨의 최댓값.** 다만 지금 코드로는 문서별 분모가 없다 —
`_check_residual`·`_check_surfaces`는 문서마다 돌지만(`:1011-1012`) `_active_targets`(`:840-846`)는
**빌드 전체 인벤토리의 합집합**이고 `_check_exclusions`는 `validate_inputs` 말미에 한 번만 돈다(`:1234`).
문서별로 가려면 `_active_targets(items, document_name)`로 쪼개는 선행 수리가 필요하고, 그 전에는 «문서별»이 구현 불가다.

**Q2 — «완료 금지»가 기존 전이·backstop과 어떻게 맞물리나.**
**지금은 맞물리지 않는다.** backstop과 coder 입장이 같은 `validate_inputs`를 부르고(`backstop.py:300` · `coder-web.md:44-45`),
`--phase`는 그 함수에 들어가지 않으며(`:1398-1403`), G2 직전과 마무리의 backstop 명령줄이 동일하다(`commands:186`·`:191`).
검사기는 `build-state.json`을 읽지 않고, 실물 A8의 그 파일에는 이미 스키마 밖 값이 들어 있다.
→ **`validate_inputs(..., stage=)` + backstop `--finalize`를 신설해 두 호출의 명령줄을 갈라놓는 것이 이 설계의 선결 조건**이다.

**Q3 — `active` 단조 감소 금지가 합법적 축소를 오판하지 않나.**
**오판한다.** 분모는 «이번 실행에서 포인터가 해소된 문서들의 활성 identity 합집합»이라, case 삭제·viewport 축소·
`--excluded-regions` 선언 추가·시안 개정·재동결(시안을 새로 수집하므로 분모가 정당하게 바뀐다)에서 모두 줄어든다.
게다가 다른 발견을 고치는 라운드마다 값이 흔들린다(rv-B MINOR가 지적한 축). 기준값 저장처가 에이전트 소유 파일이라
낮추려는 주체가 곧 기록 주체다. → **차단이 아니라 «감소 사유 1줄 의무 + 배너 표면화»로 바꾸고,
분모는 `design-input.json`이 선언한 문서 집합으로 고정**한다.

**Q4 — 재동결 일반화가 기존 `.dc` 경로 동작을 바꾸지 않는다는 보장.**
**보장 없다.** ① `REQUIRED_STAGING`을 `journal.discard_set` 기준으로 동적화하면, live에 `screen-meta.json`이 없던 구판 dc 빌드는
그 요구가 사라져 **오늘 exit 3이던 것이 조용히 통과**한다(약화). ② `design-ref/` 요구(`refreeze.py:422-424`)는 `discard_set`과 무관한 별도 조건이라
동적화 대상 밖이고 이미지 단독 빌드에서는 그대로 벽이다. ③ `FIXED_DISCARD_FILES`(`:32-36`)는 dc 산출물 이름의 고정 목록이라
«출처 종류와 무관»이라는 문장과 정면으로 어긋난다.
→ 보장을 만들려면 **ⓐ 출처 종류를 `journal`의 명시 필드로 남기고 종류별 필수 집합을 분기**,
**ⓑ `_finish`가 `_prev`를 한 세대 보존**(BLOCKER 4), **ⓒ dc 경로 회귀 픽스처를 `verify-web`에 추가**한다.

<!-- 도구 사용: 워크트리 루트에 `.serena/project.yml`·`graphify-out/graph.json`이 없어 Serena·Graphify 미사용(기본 읽기·검색 도구와 읽기 전용 실행으로 확인). A8 워크트리는 읽기 전용 조회·검사기 실행만 수행(쓰기 0). -->
