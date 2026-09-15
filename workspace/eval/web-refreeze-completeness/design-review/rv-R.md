# 재검토 R — 설계 v2 (2026-09-15)

대상: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(이하 `design:N`)
1차: `rv-A.md`(규범 정합) · `rv-B.md`(실행·안전) · 진단 `diagnosis.md`
도구: 기본 검색·편집만(이 워크트리에 `.serena/project.yml`·`graphify-out/graph.json` 없음 — opt-in 표식 부재로 Serena·Graphify 미사용).
A8 워크트리는 열지 않았다 — 판정은 전부 플러그인 정본 코드 경로 추적이다.

## 판정

**구현 진입 불가** (신규 BLOCKER 2 · MAJOR 5 · MINOR 6 · 1차 미해소 1)

구조 역전(staging 우선) 자체는 **코드로 성립한다** — §A의 4개 전제를 모두 실측 확인했다.
막는 것은 역전이 새로 만든 두 구멍이다: ① `scope.md`가 staging/live 두 벌로 갈리는데 규범이
재수집 도중 그 파일에 쓰기를 **요구**한다(RB1) ② «원자 교체»가 혼재 디렉터리에서 파일 이동이
아니고, 중단 시 복구·재개 규정이 없다(RB2). 1차 지적 중 rv-A M3(부채 hook 침묵)는 시험 문구만
고쳐졌고 실제 침묵은 R7에 위임된 채 그 조건이 적히지 않았다.

---

## A. 구조 변경이 성립하는가 — 코드 확인 결과

**A-1 `check_design_evidence.py --build <staging> --project-root <ROOT>`: 성립.**
`run():1402-1406`이 `--build`와 `--project-root`를 **독립 해소**하고 `validate_inputs(build, project)`에
넘긴다. build 상대로 해소되는 것: `scope`·`coverage_review` 포인터(`:1097-1102`) · `manifests[i]`
(`:1113-1114` `confined(build, …)`) · `reference_root = build / reference_value`(`:1088-1094`, build
안이어야 함) · case `reference_capture`(`:1214`) · `source_observation`(`:1035`) · 그 안의 `capture`·
`trace`(`:1055-1063`) · `interactions`(`:982`) · 그 안의 step/initial 캡처(`:805-810`, `_capture_item`).
`project`가 쓰이는 지점은 `host_files`(`:1245`)와 `implementation_digest(project, …)`(`:1263-1281`)
**뿐**이며 둘 다 프로젝트 루트 기준이라 staging과 충돌하지 않는다.
ⓒ `scope.md` 복사는 sha256까지 통과한다 — `pointer():65-81`이 `build/<path>` 바이트로 sha를
재계산하고, 새 `design-input.json`을 staging 복사본 기준으로 쓰면 일치한다. `_check_exclusions:858-861`
(`approval_quote` 부분문자열)·`:880-892`(`scope_ref` 앵커)도 같은 staging 복사본을 읽는다.
**단 «복사본이 끝까지 live와 동일하다»는 전제가 깨진다 — RB1.**

**A-2 드라이버 출력 경로: 성립. 교체 후 live에서도 유효하다.**
`observe_interactions.mjs:23-26`이 `--out`·`--captures-dir`를 자유 경로로 받는다.
결정적 확인: `assets/observe_interactions.pw.js:99` `capturesDir = opts.capturesDir ? resolve(…) : dirname(out)` ·
`:115` `buildDir: path.dirname(capturesDir)` · `:548` `return { path: relativePosix(ctx.buildDir, file), … }`.
즉 캡처 포인터는 **capturesDir의 부모를 build로 보는 상대 경로**다. `--out <staging>/captures/…`
`--captures-dir <staging>/captures`면 `captures/<screen>-step-N.png`가 기록되고, commit이
`captures/`를 live로 옮긴 뒤에도 같은 상대 경로가 그대로 해소된다.
`archive_sha256`도 안전하다 — `_check_bindings:748-756`이 `source-manifest.json` **바이트 sha**와
대조하므로, staging에서 manifest를 먼저 만들고 그 뒤 관찰을 수집하는 기존 step 5 순서를 지키면 어긋나지 않는다.

**A-3 `_refreeze-<ts>`는 `archive_design.py`가 실제로 허용한다.**
`archive():122-133`의 경로 검사는 ⓐ entry가 `--source-root` 안 ⓑ `--out`과 `--source-root` 서로소
ⓒ `--manifest`가 `out.parent` 안·`out` 밖 — **세 가지뿐이고 staging 이름 규칙이 없다.**
`--out BUILD/_refreeze-<ts>/design-ref --manifest BUILD/_refreeze-<ts>/source-manifest.json`은 ⓒ를
충족한다. `_staging-<ts>` 제약은 산문(`design-acquisition.md:47`)과 `compare_manifests():210-212`의
auto-carried glob에만 있고, 후자는 R6이 통째로 지운다. **제거의 부작용도 없다** — `archive()`와
`compare_manifests()`는 코드상 완전히 분리돼 있고, `_staging-*` glob·`_history`를 아는 코드는
`compare_manifests()` 밖에 0이다.

**A-4 교체는 «경로가 build 상대라서» 성립한다 — 단 «파일 이동만»은 아니다.**
`design-input.json`·`visual-evidence.json`·관찰/interactions 문서의 포인터는 전부 build 상대다(A-1·A-2).
`source-manifest.json`의 `source`/`source_root`는 절대 경로지만 EXPORT를 가리키고, archive 경로에서
검사기가 쓰는 것은 `frozen.as_uri()`(`:1163`)라 교체와 무관하다.
**문제는 `captures/`가 폐기·보존 혼재 디렉터리라는 점이다 — RB2.**

---

## B. 1차 지적 해소 대조

| id | v2 주장 | 실제 | 판정 |
|---|---|---|---|
| A-B1 captures 전량 폐기 | 포인터 기반 S | `validate_visual:1310-1314`가 구현 캡처의 원본 재사용을 금지(`original file/hardlink reuse forbidden`)하므로 두 집합은 **구조적으로 서로소**다. 겹치는 파일 없음 | 닫힘 — 단 **빠지는 파일 있음**(RM1)·교체 시 병합 필요(RB2) |
| A-B2 prepare exit 0 = 성공 | check/게이트 분리 | `run():1406-1411`이 prepare에서 `review_digest`만 반환. staging 대상 반복 실행에 코드 제약 없음 | 닫힘 |
| A-B3 부채 게이트 모순 | 문구 5곳 정렬 | defer 허용 문구 전수 = `commands:129` · `REQUEST_GUIDE.md:115-116` · `evidence_debt_hook.py:36-40`·`:132` (+각 미러). **R5 목록이 전수 맞다.** `commands:71`은 스키마 문자열이라 불필요 | 닫힘 — 회귀 그물 0(m-4) |
| A-B4 motion-notes m-id | 보존으로 이동 | `check_motion_spec.py:360-366` 전수성은 notes↔spec 양방향이라 둘 다 보존이면 불변. `--audit` 계수 게이트(`:370-374`)는 **warn**이지 finding이 아니라 render-audit만 재수집해도 red 아님 | 닫힘 |
| A-B5 `interaction_exclusions` 이월 | R8 신설 | `_check_exclusions:849-895`의 4조건(정확 필드·quote 부분문자열·앵커 실재·10% 상한)과 R8이 대응. **새 승인 원문이 필요하면 `scope.md`를 써야 하는데 그 경로가 RB1에 걸린다** | 부분 |
| A-M1 «재동결의 끝» | §1에서 확정 | `design:37`은 «inputs exit 0 = 끝»인데 v2 순서상 inputs는 **교체(R2-5) 앞**이다. 끝이 교체보다 앞서는 문장이 남았다 | 부분(m-5) |
| A-M2 `visual_gate` 무소비 | 기존 키 사용 | `backstop.py:288-293`이 design_status 무관하게 `validate_visual`을 돈다는 사실과 R4가 정합 | 닫힘 |
| A-M3 blocked가 hook 시야를 지움 | B3 합격 조건에 «ready» 추가 | **시험 문구만 고쳤다.** `evidence_debt.py:139-140`의 ready 게이트는 그대로고, R7은 `design-input.json` 유무만 언급하고 ready 게이트를 언급하지 않는다 | **미해소(RM2)** |
| A-M4 제거 목록 8곳 | R6 전수표 | 실측 대조: `commands`의 재동결·refreeze 합집합 = `{9,70,129,130,134,137,146,154,171,205,227,234}` — **R6 목록과 정확히 일치**. Codex도 `{8,123,151,152,156,159,169,177,194,228,250,258}` 일치 | 닫힘 — `design-evidence.md` 행번호만 부정확(m-3) |
| A-M5 openapi 축 | §0 비목표 + `:227` 분리 | `:129`의 단일 질문(«openapi 동결본·design-ref·motion-notes·render-audit 재동결 여부»)도 R6 수정 대상에 들어 있어 처리 가능 | 닫힘(문구 작업 잔여) |
| A-M6 declared.json 위치·주체 | R1 보존으로 이동 | 위치·주체 정정은 정확(`commands:143`·`:171`). **그러나 staging 실행 시 `--declared` 입력을 live 루트에서 읽어야 한다는 분기가 없다** | 부분(RM3) |
| A-m1 `_history` | §4 우회 5 | `archive_design.py:209`가 유일 소비자·제거 후 0 | 닫힘 |
| A-m2 grep 어휘 | B7 확장 | 기존 폴더 잔존 키가 무해하다는 주장 재확인: `validate_inputs`는 build-state를 읽지 않고 `backstop.py:145-170`·`evidence_debt.py:99-103,139`도 미지 키를 거부하지 않는다 | 닫힘 |
| A-m3 `legacy_v1_allowed` | «창이 교체 수초로 축소» | **거짓.** `legacy_v1_allowed:112-123`은 빌드 폴더의 untracked 0을 요구하는데 `_refreeze-<ts>/`는 begin~commit 내내 untracked다(v1 `_prev-*`와 동일 길이) | 부분(m-2) |
| A-m4 `evidence_debt` 키 제거 시점 | `build_debt()` 뒤로 묶음 | `build_debt()`는 `design_status=='ready'`여야 판정한다(`:139-140`) → **ready 승격이 먼저여야 호출 가능**. 그 순서가 R4에 없다 | 부분(m-6) |
| B-B1 구현 트리 쓰기 | R3 신설 | 쓰기 사실은 수용. **멱등 전제는 인라인 이미지에서 거짓(m-1)**, **«live 무손상» 전제는 거짓(RM4)**, 차집합 롤백이 남의 파일을 지울 수 있다는 한계 미기재 | 부분 |
| B-B2 prepare가 축을 안 봄 | `refreeze.py check` | `check_design_evidence.py`에 render-audit·design-tokens·asset-manifest 문자열 0, `screen-meta.json`은 `:758` 선택적 — 확인. check가 **실재만** 본다(design:91-93)는 것도 설계가 스스로 적음 | 닫힘(내용 검증은 여전히 없음 — 수용된 한계) |
| B-B3 staging 잔존 감지 | R7 hook | hook은 SessionStart/UserPromptSubmit에서만 발화(`evidence_debt_hook.py:32`). `commands:171` ⑤는 **같은 턴 안**이라 끼어들 지점이 없다 | 부분(RM5) |
| B-B4 중단 시 hook이 놓침 | 구조적 해소 | staging 창에서는 live `design-input.json`이 남으므로 `_builds()`가 찾는다 ✓. 그러나 ⓐ blocked면 `build_debt`가 None(RM2) ⓑ commit ①~② 사이 중단이면 live design-input.json이 사라져 **정확히 같은 침묵**(RB2) | 부분 |
| B-M1 원장 | 이미지 축 한정 | RM4·m-1 참조 | 부분 |
| B-M2 주입 지점 | §3 B2에 명시 | `observe_interactions.mjs:17`의 env 폴백(`DDDJANGO_WEB_PLAYWRIGHT_MODULE`)이 실재하고 부재면 `CliError` → exit 1. case마다 별도 프로세스라 «3번째 case» 주입도 실행 가능 | 닫힘 |
| B-N1 backstop 메시지 | 부분 수용 | 그대로 | 닫힘(수용된 한계) |
| B-N2 `<BUILD>` 밖 스테이징 | 기존 규율 위임 | 그대로 | 닫힘 |
| B-N3 Codex byte-parity | `make verify` 위임 | `Makefile:95-96`(scripts·assets `diff -rq`) · `:98-101`(references `cmp`) · `:103-104`(REQUEST_GUIDE `cmp`) 실재 확인 | 닫힘 — **단 `commands` ↔ Codex `SKILL.md`는 의미 미러라 어떤 기계 대조도 없다**(m-4) |

---

## 신규 BLOCKER

### RB1 `scope.md`가 두 벌로 갈리는데, 재수집 단계가 바로 그 파일에 쓰기를 요구한다

- 설계: `design:82-83` «`begin` — … `scope.md`를 복사한다» · `design:60` 보존표의 `scope.md` ·
  `design:99-100` «② staging 산출물을 live 경로로 이동» — 복사된 `scope.md`가 «산출물»인지 불명.
- 규범(쓰기 요구): `dddjango-web/commands/dddjango-web.md:143`
  > **실행 경계**: Playwright 모듈 경로(`--playwright-module` 또는 env)·그 `package.json`의 실제 버전·기동 방식(…)과 `--declared`·`--excluded-regions` 사용 여부를 `scope.md`에 기록한다.

  이 문장이 사는 step 5-4는 **재동결이 통째로 재실행하는 단계**다. R8(`design:177-182`)의 새 승인
  원문 확보도 같은 경로를 탄다.
- 규범(위험을 이미 성문화): 같은 파일 `:129`
  > 결정은 `build-state.json.evidence_debt`에만 기록한다(… `scope.md`에는 적지 않는다: **scope 바이트가 바뀌면 `design-input.json.scope` 포인터·review digest가 어긋난다**)
- 코드: `check_design_evidence.py:1097-1102`(scope 포인터 path+sha256 — prepare에서도 돈다) ·
  `:858-861`(`approval_quote`가 `build/scope['path']` 본문의 부분문자열) ·
  `:1250-1258`(`coverage_review`의 `reviewed-input`이 **scope 바이트를 포함한** digest와 일치해야 함).
- 실패 시나리오:
  ⓐ **live에 기록하면** — staging `design-input.json`은 staging 복사본 sha를 담고, commit이
  `scope.md`를 옮기지 않으므로(보존 대상) 교체 직후 live `scope.md` 바이트 ≠ 기록된 sha →
  `scope: sha256 mismatch`로 inputs·backstop이 red. 재동결이 끝나자마자 프로젝트 전체가 막힌다.
  ⓑ **staging 복사본에 기록하면** — commit 시 staging이 삭제되면서 규범이 요구한 실행 경계 기록이
  증발하고, live `scope.md`는 여전히 옛 바이트라 ⓐ와 같은 sha 불일치.
  ⓒ **staging 기록 + commit이 scope.md도 옮기게 하면** 정합하지만, 그러면 `scope.md`는 «보존»이
  아니라 폐기·교체 대상이며 R1 보존표·R2-5 어디에도 그 문장이 없다. 세 해석 중 옳은 하나를
  설계가 고르지 않았다.
- 파급: `coverage-review.md`는 staging에서 만들어지고 그 `reviewed-input` digest가 scope 바이트를
  포함하므로, 검토 **뒤에** scope가 한 번이라도 바뀌면 `coverage_review: reviewed-input does not
  match`로 다시 red다 — 순서 규정도 없다.

### RB2 «원자 교체»가 혼재 디렉터리에서 파일 이동이 아니고, 중단 복구·재개 규정이 없다

- 설계: `design:99-101`
  > **`commit`** — 원자 교체: ① R1의 폐기 집합 S를 `_prev-<ts>/`로 이동 ② staging 산출물을 live 경로로 이동 … 교체 자체는 파일 이동뿐이라 수초 안에 끝난다.
- 근거 ①(혼재): `captures/`에는 폐기 대상(원본 캡처·관찰·trace·`*-interactions.json`·상태 캡처)과
  **보존 대상**(`visual-evidence.json`이 가리키는 `*-impl.png`)이 같은 디렉터리에 산다 — rv-A B1이
  A8 실측으로 확인했고 `design-evidence.md:403`이 구현 캡처 경로를 `captures/`로 규정한다.
  따라서 ②는 **디렉터리 이동이 아니라 파일 단위 병합**이어야 한다. `mv <staging>/captures <BUILD>/captures`
  로 구현하면 보존 대상 `*-impl.png`가 통째로 사라진다 — rv-A B1이 닫았다고 한 사고가 교체
  단계에서 그대로 재발하며, 검사기는 `validate_visual`의 `capture: regular file required`로만 운다.
  설계는 ①만 «폐기 집합 S»로 파일 단위임을 명시하고 ②에는 같은 단서가 없다.
- 근거 ②(중단): ①과 ② 사이에서 세션이 죽으면 live에 동결물이 **하나도 없고** `_prev-<ts>`와
  staging에 나뉜다. `abort`는 `design:103` «live는 처음부터 손대지 않았으므로 복원할 것이 없다»를
  전제하므로 이 상태를 복구하지 못한다. `commit` 재실행도 불가능하다 — S는 live
  `design-input.json`의 포인터에서 계산되는데(`design:48-54`) 그 파일이 이미 `_prev`로 옮겨졌다.
  journal에 S를 적는다는 문장도 없다(`design:84`의 journal 필드 = `started_at`·`images_before`·
  `build_state_design_keys`뿐).
- 근거 ③(그 순간의 침묵): 그 상태의 live는 `design-input.json`이 없으므로
  `evidence_debt_hook.py:113-114`의 `_builds()`가 후보에서 제외한다 — rv-B B4가 «구조적 해소»라고
  적힌 바로 그 침묵이 commit 창에서 되살아난다. R7의 `_prev-*` 감지가 유일한 안전망인데,
  그 판정 자체가 `_builds()` 밖에서 돌아야 한다는 조건이 R7에 없다(RM2와 같은 원인).

---

## 신규 MAJOR

### RM1 폐기 집합 S가 한 단계 얕다 — `interactions.json` 안의 상태 캡처가 빠진다

- 설계 `design:50-53` 표는 관찰 문서에서 `capture.path`·`trace.path`·`interactions.path`만 뽑는다.
- 코드: `check_design_evidence.py:805-810`(`_check_initial` → `initial.capture`)·`:1003`
  (`_check_steps` → `steps[].after.capture`)가 **interactions 문서 안의 또 한 겹 포인터**를 build
  상대로 해소한다. 생성 주체는 `assets/observe_interactions.pw.js:542-548`
  (`captures/<screen>-initial.png` · `captures/<screen>-step-N.png`).
- 규범도 이를 별도 항목으로 센다 — `commands:171` ⑤ «`captures/<screen>-interactions.json`과 **그 상태 캡처**».
- 실패: A8 12 case 규모에서 수십~수백 장이 S 밖에 남는다. 새 수집이 같은 이름을 덮어쓰지만
  step 수가 줄면 옛 `step-N.png`가 미참조로 잔존한다 → 사용자 정의(«완벽하게 삭제») 위반이고,
  R1의 «포인터가 가리키는 파일의 합집합»이라는 주장이 사실이 아니게 된다. §4 우회 목록의
  «고아»는 `web/static/images/`만 다룬다.

### RM2 `design_status` 전이를 수행하는 주체·시점이 R2 어디에도 없다 → rv-A M3의 침묵이 그대로

- 설계 `design:122` R4 표: «교체 전 `blocked` → inputs exit 0 후 `ready`». `design:37` §1도 같은 취지.
- 그런데 R2의 4 서브커맨드 중 `build-state.json`을 쓰는 것은 `commit` ③(`design:100`)뿐이고
  `begin`(`design:82-84`)은 journal만 쓴다. **`blocked`를 쓰는 주체가 설계에 없다.**
- 두 해석 모두 구멍:
  ⓐ 아무도 안 쓰면 R4 표가 사문이고 §1의 «ready 복귀»도 무의미(애초에 ready였다).
  ⓑ `begin`이 blocked로 내리면 staging 창(A8 기준 수십 분 + 보완 루프) 내내
  `evidence_debt.py:139-140`
  > `if not isinstance(state, dict) or state.get('design_status') != 'ready': return None`

  가 그 폴더를 **판정 대상에서 지운다** — rv-A M3가 지적한 침묵 그대로다. v2 §6은 M3를
  «B3 합격 조건에 ready 추가»로 닫았다고 적었으나 그것은 **시험 문구**일 뿐이다.
- R7(`design:167-170`)이 유일한 대체 안전망인데 «`design-input.json` 유무와 무관해야 한다»만 적고
  **`design_status` ready 게이트를 우회해야 한다는 조건을 적지 않는다**. 구현자가 R7의 «1줄»을
  `build_debt()`/`_line()` 안에 넣으면 그 줄은 영원히 발화하지 않는다.

### RM3 staging 대상 재수집에서 드라이버 **입력** 파일이 live 루트에 있다는 분기가 없다

- 설계 `design:86-89` R2-2는 `--out`·`--manifest`만 staging으로 지정하고 «드라이버·렌더 실측
  산출도 staging 안»이라고만 적는다. `design:66`은 `<screen>-declared.json`을 «빌드 루트에 있고
  드라이버의 **입력**»이라며 보존으로 옮겼다.
- 규범은 그 경로를 고정한다 — `commands:143` «소스 검토로 찾은 비의미 대상은
  `<산출물 폴더>/<screen>-declared.json` … `--declared`로 준다». staging을 «산출물 폴더»로 읽으면
  `begin`이 복사하지 않은 파일(begin은 `scope.md`만 복사 — `design:82`)을 찾게 된다.
- `--excluded-regions`·`--hover-selectors`도 같다(`design-acquisition.md:117`은 경로를 고정조차
  하지 않는다).
- 실패: `--declared` 없이 조용히 돌면 `declared_unmatched`·`unclickable` 잔여가 늘어
  `_check_residual:963-975`가 결함을 내고, 보완 루프가 매 재동결마다 소스 검토부터 다시 시작된다
  — R1이 declared.json을 보존으로 옮겨 막으려던 비용(rv-A M6)이 경로 분기 누락으로 되살아난다.

### RM4 «live 무손상» 전제가 이미지 축에서 거짓이고, R2-6이 자기모순이다

- 설계 `design:98` «live가 무손상이므로 보완·재실행을 몇 번이든 staging에서 반복할 수 있다» ·
  `design:103` «live는 처음부터 손대지 않았으므로 **복원할 것이 없다**» ↔ 바로 위 `design:102`
  «`abort` — staging 삭제 + … `images_before`에 없는 신규 이미지 파일 **제거**»(= 복원할 것이 있다).
- 코드: `check_design_evidence.py:1263-1276` `implementation_digest`가 `project/web/**`를 전수
  해싱한다. `fetch_images.py:104-111`이 `<ROOT>/web/static/images/`에 새 바이트를 쓰는 순간
  완료 빌드의 `visual-evidence.json.implementation_digest`가 stale이 되어
  `validate_visual:1295-1297`이 red다.
- 실패: staging 창 중간에 사용자가 다른 작업을 지시해 backstop이 돌면 «live는 온전하다»는 전제와
  달리 `[DESIGN] BLOCKER implementation_digest: stale` 이 뜬다. 즉 `abort`는 선택이 아니라
  **의무**이며, 설계는 그 의무를 «복원할 것이 없다»로 부정한다.

### RM5 `commands:171` ⑤ 커밋 창은 R7로 닫히지 않는다

- 설계 `design:164-169`가 rv-B B3를 hook 1줄로 닫는다고 적는다.
- 코드: `evidence_debt_hook.py:32` `EVENTS = {'session-start': …, 'user-prompt': …}` — hook은
  세션 시작과 프롬프트 제출에서만 발화한다. `commands:171`의 Phase 2 진입 준비 ⑤는 **같은 턴
  안에서** 일어나므로 hook이 끼어들 지점이 없다. 잔존 `_refreeze-*`는 다음 프롬프트에서야 잡힌다.
- 악화 요인: v2의 staging은 `design-ref` **전량 사본**이라 v1의 `_prev-*`보다 커밋 오염 규모가 크다
  (A8 기준 archive 전체 트리 1벌 추가).
- 파생: 같은 이유로 «디스크·중복 저장 비용»(재수집 창 내내 동결물 2벌)이 §4 우회 목록에 없다.

---

## 신규 MINOR

- **m-1 R3의 «멱등»이 인라인 이미지에서 거짓** — `design:112`. `fetch_images.py:70-79`
  `assign_token`은 소스명이 있으면 slug가 안정적이지만 `data:` 등은 `f"{doc_slug}_{n}"`이고
  `n`은 `len(images)+1`(`extract_dc.py:234`)이라, 문서에서 이미지 하나가 추가·삭제되면 이후
  인라인 토큰이 전부 밀린다. 바이트가 같아도 새 파일명으로 다시 떨어진다. 롤백(차집합)은 여전히
  정확하므로 안전성 문제는 아니나, R3이 «구현 트리에 써도 무해»의 근거로 든 멱등성이 반만 참이다.
- **m-2 rv-A m3 «교체 수초로 축소»는 거짓** — `design:246`. `backstop.py:112-123`
  `legacy_v1_allowed`는 빌드 폴더의 untracked/ignored 0을 요구하므로 `_refreeze-<ts>/`가 사는
  begin~commit 전 구간이 창이며 v1과 길이가 같다. 같은 이유로 `current_nondesign_scope:167-173`
  (다른 빌드 밑 untracked가 있으면 skip 불가)도 그 기간 내내 닫힌다. 실질 피해는 낮다(R4가
  design_status를 내리면 두 경로 모두 어차피 닫힘) — 문제는 §6의 «수용» 근거가 사실이 아니라는 점.
- **m-3 `design-evidence.md` 제거 대상 행번호 부정확** — `design:153`은 `:27`·`:115`·`:338`·`:342`를
  적지만 실제 `carried_from`은 `:115`·`:336`·`:338`, `--compare-build` exit 체계는 `:27-28`·`:343-346`이다.
  절 단위로 재작성하면 흡수되나 행 지정 그대로 집행하면 `:336`·`:343`이 남는다.
- **m-4 R5/R6의 의미 미러에 기계 대조가 없고, defer 의미 변경을 잡을 회귀 시험이 0이다** —
  `Makefile:95-104`의 byte 대조 대상은 scripts·assets·references·REQUEST_GUIDE뿐이고
  `commands/dddjango-web.md` ↔ Codex `SKILL.md`는 대조하지 않는다(`workspace/tools/`에도 해당 도구 없음).
  R6의 시험 정리 대상인 `test_evidence_debt.py:164`·`test_evidence_debt_hook.py:81,90`은
  **quote 문자열**일 뿐 어떤 단언도 «defer가 재동결을 허용한다»를 검증하지 않는다 —
  즉 R5를 한 곳이라도 빠뜨리면 red가 나지 않는다. B7 grep이 유일한 그물이다.
- **m-5 §1의 «재동결의 끝»이 교체보다 앞선다** — `design:37`(inputs exit 0 = 끝) vs
  `design:99-101`(commit이 마지막). rv-A M1이 요구한 경계 확정이 v1 순서 기준으로 쓰인 채 남았다.
- **m-6 `evidence_debt` 키 제거 순서 미정** — `design:124`는 `build_debt()`가 «부채 없음»을 낼 때만
  제거하라는데, `build_debt()`는 `design_status=='ready'`여야 판정한다(`evidence_debt.py:139-140`).
  즉 commit ③ 안에서 **ready 승격 → build_debt 호출 → 키 제거** 순서가 강제되는데 R4에 그 문장이 없다.

---

## D. 설계 명세로서의 충분성 — `refreeze.py`

`design:76-80`의 4 서브커맨드는 구현자에게 다음이 **모호하다**:

1. **staging 지시 인자가 없다.** `check`/`commit`/`abort`가 모두 `--build <BUILD>`만 받는데
   `_refreeze-*`가 둘 이상일 때(= R7이 상정하는 잔존 상태) 무엇을 고르는지 규칙이 없다.
2. **`begin`의 선점 처리 없음** — 기존 `_refreeze-*`/`_prev-*`를 만나면 거부인지 삭제인지 승계인지.
3. **exit 체계가 `check`에만 있다**(`design:94` 0/3/1). `begin`·`commit`·`abort`의 exit 값,
   부분 실패 시 동작, 재실행 가능 여부가 없다.
4. **journal 스키마가 부분적**이다 — `started_at`·`images_before`·`build_state_design_keys`
   (`design:84`) + `interaction_exclusions`(`design:177`)뿐. `build_state_design_keys`의 **용도가
   어디에도 없고**(아무도 build-state를 바꾸지 않으므로 abort가 되돌릴 것도 없다), commit 재개에
   필요한 **폐기 집합 S의 기록**은 없다(RB2).
5. **`check`가 읽는 `build-state.json`이 어느 쪽인지 없다** — `has_render_audit`(`design:92`)은
   live에만 있고 begin은 `scope.md`만 복사한다.
6. **R2-2의 «staging 대상 실행» 인자 목록이 불완전**하다 — `--out`·`--manifest`만 예시하고
   `--captures-dir`·`--declared`·`--excluded-regions`(RM3) · `render_audit.js` 출력 ·
   `extract_dc.py`의 `--tokens/--asset-manifest/--meta/--asset-base`(`extract_dc.py:8-10`)와
   `--assets-root`(live 고정)의 staging/live 분기를 적지 않는다.
7. **`commit`의 ①②가 파일 단위인지 디렉터리 단위인지**가 없다(RB2).

---

## 확인했으나 문제 없음

- **`_refreeze-*`가 빌드로 오인되지 않는다** — `backstop.py:69-70`은 `parts[2]`가 marker일 때만
  빌드로 센다. `.dddjango-web/<빌드>/_refreeze-<ts>/design-ref/…`는 `parts[2]='_refreeze-<ts>'`라 불발화.
  `evidence_debt_hook.py:111-114`는 `.dddjango-web` 1단계만 본다. `implementation_digest`는
  `project/web/**`만 걸어 `.dddjango-web`과 무관하다. (rv-A·rv-B의 `_prev-*` 확인과 동형 — 재확인함.)
- **`archive_design.py`가 같은 `--out`을 재사용해도 된다** — `:157`의 인벤토리 일치 요구는
  staging이 빈 새 디렉터리면 자동 충족.
- **`--compare-build` 제거가 `archive()` 경로 검사에 부작용을 내지 않는다** — `_staging-*` glob은
  `compare_manifests():210-212`에만 있고 `archive():122-133`의 세 검사와 코드상 분리돼 있다.
- **`carried_from` 수용 제거의 파급 범위** — `check_design_evidence.py:1140-1143`의
  `set(row) - required_row - {'requested_source', 'carried_from'}`와 `_is_sha` 검사 한 쌍뿐.
  다른 소비자는 없다.
- **`render-audit.json` 재수집과 보존된 `motion-notes.md`의 충돌 없음** — `check_motion_spec.py:370-374`의
  `--audit` 계수 게이트는 `warns`에 담기고 `findings`가 아니다(`:383-385`) → exit 2가 되지 않는다.
- **기존 빌드의 `refreeze_v3/_v4/_v5` 같은 미지 build-state 키는 실제로 무시된다** — build-state를
  읽는 세 곳(`evidence_debt.py:99-103,139` · `backstop.py:74-77,145-170`) 어디에도 스키마 정합 검사가 없다.

## 미확인

- **A8 실제 폴더의 현재 바이트** — 지시대로 워크트리를 열지 않았다. `captures/` 혼재 비율·상태
  캡처 장수·`interaction_exclusions` 유무는 rv-A의 실측 보고를 그대로 인용했다.
- **재동결을 실제로 돌린 결과** — `refreeze.py`가 아직 없으므로 staging 대상 prepare/inputs의
  실제 exit를 실행으로 확인하지 못했다. §A의 4개 결론은 전부 코드 경로 추적이다.
- **`observe_interactions.pw.js`가 `capturesDir`·`out` 밖에 쓰는 경로** — `:99,115,543-548`만
  읽었고 파일 전체(≈2000행)를 훑지 않았다. `--resume` 경로의 중간 산출물 위치는 미확인.
- **`render_audit.js`의 출력 경로 인자** — 콘솔 스니펫이라 Coordinator가 결과를 받아 쓰는 구조로
  보이나 호출 규범을 확인하지 않았다. staging 기록 가능성은 미확인.
- **Codex 런타임에서 R5 문구가 실제로 주입되는지** — `/hooks` 신뢰 상태 의존, 실행하지 않았다.
