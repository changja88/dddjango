# 독립 구현 리뷰 (2026-09-15)

대상: 브랜치 `worktree-fix-web-evidence-debt-hook` 커밋 5개(dd934f2e → 43d70fcc) — 설계 v2(`workspace/design/2026-09-15-web-evidence-debt-hook.md`)·1차 적대 검토·behavior.md·리뷰 패키지·변경 파일 원문·B3 증거 파일(`b3r3-stream.jsonl`·`b3r3-debug.log`)을 대조하고, 술어·hook·검사기를 tempdir fixture와 A8 사본에서 실행했다. 파일 수정 0 · 서브에이전트 0 · git 쓰기 0. Serena·Graphify는 워크트리에 opt-in 표식이 없어 미사용.

제약 확인: scripts·test byte 미러 `diff -rq` 0 · REQUEST_GUIDE byte 미러 0 · hooks.json 의미 미러(계약 검사 PASS) · hook exit 0(실측 전 경로) · 프로젝트 쓰기 0(코드 읽기 — 쓰기 호출 없음) · 검사기 exit 계약 불변(변경은 :25 import·:1050-1054 위임뿐) · 기존 테스트 40/45/42 green · `make verify-web` exit 0 · `claude plugin validate --strict` PASS.

## Q1. §7 반영 대조 — 문서에만 적히고 구현에 없는 항목

- [MAJOR] §7 «MINOR Q5 `${PLUGIN_ROOT}` 미치환 → B4에서 확인 후 H2 확정»과 §3 B4가 미이행 — B4는 돌지 않았고 Codex 경로 전체(`${PLUGIN_ROOT}` 치환 · `hooks/hooks.json` 자동 발견 — `.codex-plugin/plugin.json`은 `skills`만 선언하고 `hooks` 필드 없음 · JSON `hookSpecificOutput`/`systemMessage` 수용)가 문서 문장 외 근거 0이다 — 근거: behavior.md «B4 — Codex: 이번 배치에서 미실행»; `codex-dddjango-web/.codex-plugin/plugin.json`(hooks 미선언); 설계 :97·:140 — 제안: 릴리즈 전 격리 `CODEX_HOME`에서 B4 1회(신뢰 후 세션 시작 → `evidence hook active` 줄 유무)를 돌리거나, §3 B4·§7 두 행을 «미실행 — 배포 후 첫 Codex 세션의 active 줄로 확인·릴리즈 노트에 확인 요청»으로 정직하게 고친다.
- [MAJOR] §7 «MAJOR Q5 hook 활성 신호 → SessionStart 항상 `active` 줄 · N1-3»이 반만 닫혔다 — hook은 `design-input.json` 빌드가 0이면 SessionStart도 무출력(`.dddjango-web/config.json`만 있는 새 프로젝트·첫 빌드 진행 중 모두 침묵)인데, N1-3(:154)·REQUEST_GUIDE(:113-117)는 «active 줄이 없으면 미작동»을 무조건으로 적어 첫 빌드 종료 보고마다 거짓 «evidence hook 미작동»이 나온다(«미작동»을 정상 소음으로 학습시키는 바로 그 구조) — 근거: evidence_debt_hook.py:137-139 `if not builds: return 0`; 실행 기록 ⑥ A)·B)(무출력·exit 0); dddjango-web.md:154; REQUEST_GUIDE.md:113-117; 설계 :46 «항상 1줄» ↔ :55 «.dddjango-web 없으면 무출력» — 제안: SessionStart는 `.dddjango-web/`(루트)가 발견되면 빌드 0이어도 `active — scanned 0 build(s)`를 내고, :154·REQUEST_GUIDE는 «`.dddjango-web/` 폴더가 이미 있는 프로젝트에서 줄이 없으면 미작동»으로 한정한다(SKILL.md 동형).
- [MINOR] D1 헤더 «(Coordinator가 쓴다 · hook·검사기가 읽는다)» — 검사기는 `build-state.json`/`evidence_debt`를 읽지 않는다(읽지 않는 것이 곧 «defer는 inputs를 열지 않는다»의 구현이므로 코드가 아니라 문장이 틀렸다) — 근거: check_design_evidence.py에 `evidence_debt` 키·`build-state` 참조 0(변경은 :25 import·:1050-1054뿐); 설계 :57 — 제안: «Coordinator가 쓴다 · hook이 읽는다 · 검사기는 읽지 않는다(inputs 게이트 불변 = defer의 한계)».
- [MINOR] V1 «Makefile은 protocol 봉인 그룹 → 봉인 재발행»이 절차상 어긋난 봉인이다 — `sealed_commit=720f96bd`(T1)는 Makefile 변경 커밋 bcc8ef16(T2) *이전*이라 strict `manifest_seal.py --check`가 «sealed_commit 의 내용이 봉인값과 다르다 — protocol/Makefile»로 RED(`verify-runready` 경로); `--check --draft`(`make verify` 경로)는 green — 근거: 실행 기록 ③; `cmp <(git show 720f96bd:Makefile) Makefile` 차이(line 106); main도 같은 패턴(f9972967:Makefile ≠ main:Makefile)이라 브랜치 신규 결함은 아니다 — 제안: T2 뒤 `manifest_seal.py --write`를 다시 돌려 chore 커밋으로 분리(main의 ff9fff7c 선례)하고 DEVELOPMENT §4/§6에 «봉인 파일이 든 커밋 뒤에 재봉인» 순서를 1줄 적는다.
- 나머지 §7 행은 구현에서 성립 확인: BLOCKER Q1-1(:129 step 4 앵커) · Q1-2(:71 D1 + hook 상태별 출력 :151-163) · Q3(경량 술어·A8 사본 47 ms) · MAJOR Q1 하위경로(:83-97 + 테스트 ProjectDiscovery 6건) · 사용자 화면(:127-131 JSON) · Q2 술어/N_o(:106-134·N_o 출력 없음) · Q2 진행 중 빌드(:117 ready 한정) · Q4 defer≠exclusions(:71·:129) · Q4 ⓐ 비용(:33-37·:129 재수집 사슬) · MINOR Q0(diagnosis.md 표 8행) · Q1 배너(:154 확정 폴더+요약) · Q2 legacy(설계 §0) · Q3 pyc(:18) · Q5 재신뢰(REQUEST_GUIDE·DEVELOPMENT :149) · Q6 B2(behavior.md 갱신).

## Q2. 술어 `build_debt`의 정확성 — 검사기 «interaction evidence required» 집합과의 대조

- [MINOR] 술어가 검사기보다 관대한 입력 3종 — ① `source_observation` 포인터 키 집합 불량(`{path,sha256}` 외 키 추가·`sha256` 누락) ② 관찰 문서 필드 집합 불량(필수 필드 누락·미지 필드) ③ `interactions: null` — 검사기는 exit 2(«exact path/sha256 object required» · «exact version 1 or 2 fields required» · «interactions: exact path/sha256 object required»), 술어는 clear(부채 0·고지 없음). 설계 §2 «포인터 형식 불량 = 부채»가 절반만 구현됐다(dict 여부·path만 본다) — 근거: 실행 기록 ⑤ MISMATCH 4행 + ⑤′ null 재실험; evidence_debt.py:93-98(포인터는 `isinstance dict`·`path` 확인만)·:22(`'interactions' in observed` — 값 미검사) — 제안: `_case_has_evidence`에서 `set(pointer) == {'path','sha256'}`과 `isinstance(observed.get('interactions'), dict)`를 요구하고, 검사기 :1042-1046의 required 필드 집합을 `evidence_debt`로 옮겨 양쪽이 공유한다(단일 출처 확장 — 검사기 테스트 45건이 보존을 증명).
- 어긋남 없음으로 확인한 것: 검사기 «interaction evidence required»가 나오는 case(포인터 정확·파일 존재·정확 v1 필드·legacy 아님)는 술어에서 전부 부채(ready 빌드 한정) — 포함 관계 성립. v1 · version 문자열 `"2"` · 절대 경로 · `../` 탈출(양쪽 다 resolve 후 내부면 수용) · 파일 없음 · JSON 불량 · 포인터 부재 · sha256 불일치(설계대로 해시 미검사·검사기는 결함)는 방향 일치. `design_status ≠ ready`(pending/blocked/none/키 없음)와 `legacy_v1=True`는 설계 §0·§2가 명시한 의도적 차이. manifests 다중(archive+static)·`manifests=[]`·entrypoint 비archive는 검사기가 다른 결함으로 이미 거부하는 빌드라 술어 판정(clear/None)이 실무상 무해. archive 판정 규칙은 검사기 :1124(`collection == 'archive'`)와 동일.

## Q3. hook 스크립트

- [MINOR] `user-prompt`가 설계(«undecided 1개 이상일 때만»)와 달리 `error` 빌드도 매 프롬프트 출력하며, 읽을 수 없는 이력 폴더는 결정 키로도 침묵시킬 수 없다(error 판정이 decision보다 먼저·design-input/build-state 불량이면 결정 기록이 무시됨) → 영구 소음·off 스위치 없음 — 근거: evidence_debt_hook.py:158-163; evidence_debt.py:114-116·:121-124·:35-36; 설계 :47 — 제안: error는 SessionStart 상태 줄로만 내거나, `evidence_debt` 결정이 읽히면 error도 상태 줄로 강등.
- [MINOR] 예외 경로가 미검증이고 침묵으로 끝난다 — `_has_builds`의 `Path.is_dir()`는 Python ≤3.12에서 EACCES를 raise(`_ignore_error`는 ENOENT/ENOTDIR/EBADF/ELOOP만 무시) → 최상위 except → stderr 1줄·exit 0·**active 줄 없음** = 사용자·Coordinator에게 «미작동»으로 보임; 테스트 16건 중 예외를 실제로 유발하는 케이스가 없다(invalid stdin만) — 근거: evidence_debt_hook.py:64-65·:167-172; test_evidence_debt_hook.py; 실행 기록 ⑥ E)(3.14에서는 raise 없이 무출력) — 제안: `_has_builds`를 `try/except OSError → False`로 감싸고, `main`의 except에서 SessionStart면 `[dddjango-web] evidence hook error: …`를 additionalContext·systemMessage로 내보내며(exit 0 유지) 그 경로 테스트 1건을 추가.
- 발견 없음으로 확인한 것: 프로젝트 탐색 — 상위(첫 `.dddjango-web` 보유 조상 :87-90)·깊이 ≤2 하향(:91-96)·dot 디렉터리 제외(`.git`·`.claude`·`.codex`·`.venv`)+`SKIP_DIRS`(:31·:76)·심볼릭 링크 미추적(`follow_symlinks=False` :76)·scandir 권한 오류 흡수(:69-71)·realpath 중복 제거(:89·:93·:95) — 테스트 ProjectDiscovery 6건과 일치. stdin — TTY/None → 무시(:42), 빈 입력 → `{}`(:48), 비JSON → None(:49-50), DEVNULL 실측 exit 0. 출력 — 단일 줄 JSON(`hookSpecificOutput.hookEventName`·`additionalContext` + 최상위 `systemMessage`)을 Claude Code가 파싱함을 B3 디버그 로그가 증명(«Parsed initial response» · «provided additionalContext (1935/1838 chars)» · SessionStart matcher `startup` 발화). 비용 — A8 사본 9폴더 user-prompt 48·47·47 ms / session-start 45·46·47 ms(B2 재현). `sys.dont_write_bytecode=True`(:18)는 `evidence_debt` import(:27)보다 앞. 미지 argv → UserPromptSubmit·exit 0(테스트). Codex 계약은 Q1 MAJOR(미검증).

## Q4. 검사기 위임 리팩터 `_source_observation`

Q4: 발견 없음 — 확인한 근거: main :1049 `if version == 1 and not legacy_v1` ↔ HEAD :1051 `if not legacy_v1 and not has_interaction_evidence(observed)`. 직전 :1047 정확 필드 검사를 통과한 `observed`는 dict · `version ∈ (1, 2)` · (`version == 2` ⇒ `'interactions' ∈ observed`, :1045-1046)이므로 `has_interaction_evidence(observed)` = `dict ∧ version == 2 ∧ 'interactions' ∈ observed` ⇔ `version == 2`, 따라서 `not has_interaction_evidence` ⇔ `version == 1` — 동치. 경계값(`True`는 `== 1`, `2.0`은 `== 2` — 양쪽 산술 동치라 분기 동일)도 반례 아님. `validate_interactions` 호출 조건(:1232 `version == 2`) 불변. 회귀: test_design_evidence 40 · test_interaction_evidence 45 · test_design_archive 42 green; `CheckerParity.test_checker_imports_predicate`가 같은 함수 객체임을 고정.

## Q5. 규범 문장 정합

- [MINOR] 수정 모드 :205의 step-4 합류 목록(«`ls -d` 목록·ⓐ/ⓑ 선택·재동결 질문 — 신규 동결 질문 포함»)에 증거 부채 결정이 없다 — «그대로 수행»으로 포함되지만 채널이 늘 때마다 괄호에 명시 열거해 온 선례상 누락으로 읽힌다 — 근거: dddjango-web.md:205(SKILL.md 동형 행) — 제안: 괄호에 «·hook 고지 폴더의 증거 부채 결정» 추가(양쪽).
- [MINOR] defer의 허용 집합이 «비구현 실행만»이라는 부정 정의라 G2 승인·마무리 backstop(:190 — K3 legacy로 v1 통과 가능)이 «구현 재진입»인지 불명 — B3에서 Coordinator가 «defer면 G2 승인·마무리 진행에 지장 없음»이라 단언했는데 사본은 비git이라 legacy 불가·backstop exit 2가 실제 결과 — 근거: dddjango-web.md:71·:129·:143(legacy 문장)·:190; b3r3_final.py 배너 전문 — 제안: :71/:129에 «defer 허용 = 재동결·조회·보고 / 구현 재진입 = 수정·트리비얼 편집·coder 호출·G2 승인·마무리 backstop»을 열거하고 K3 legacy 통과와의 관계를 1줄로.
- [MINOR] 결정을 `scope.md` 제약 절에도 기록하면 scope 바이트가 바뀌어 `design-input.json.scope` 포인터 sha와 review digest가 어긋난다(다음 `--phase inputs`에 «scope: sha256 mismatch»·coverage_review 불일치 추가) — :129는 :160의 «G0 승인 기록으로 scope 바이트가 바뀐 경우» 절차(포인터 갱신·입력범위 대조·inputs 재실행)를 가리키지 않는다 — 근거: check_design_evidence.py:1104-1106·:1252-1258; dddjango-web.md:129·:160 — 제안: :129에 «scope.md 기록 후 :160 절차를 따른다» 또는 기록처를 build-state로 한정하고 scope.md는 관찰 회차에 합류.
- 발견 없음으로 확인한 것: step 4 앵커(:129) · 재동결 종료 보고(:137 «재동결만으로 끝나면 부채 상태 1줄 — 동일이어도 별개») · 배너/종료 보고 반복 표기(:154 «앵커 아님») · build-state 스키마(:71) 사이 모순 없음. :142/:143 수집 의무는 진행 중 빌드 대상이고 술어는 ready 한정이라 충돌 없음(:143 «진행 중 build는 수집을 마쳐야 ready»와 정합). :122/:143 재질문 금지 ↔ :129 «이미 기록된 결정은 재질문하지 않는다» 정합·hook이 결정 폴더에 명령문을 내지 않음(:158-159). `interaction_exclusions`(대상 예외·10%·approval_quote)와 defer(빌드 유보)의 구분이 :71·:129에 명시. Codex SKILL.md — 새 문장 4곳(:124·:151·:159·:177)이 Coordinator(:71·:129·:137·:154)와 동형; evidence/부채 문장 집합 diff 0(차이는 기존 `${SKILL_DIR}`·`spawn_agent` 플랫폼 표기뿐).

## Q6. B3 판정의 정직성

- [MAJOR] behavior.md는 설계 §3 B3 ②(«첫 assistant 텍스트 블록에 리터럴 `[dddjango-web] evidence debt —`»)를 미충족으로 정직하게 적었지만 설계 §3을 고치지 않아 구속 명세와 시험 기록이 불일치로 남았다. 기준 자체는 배너 위치를 오가정한 것(첫 블록은 «확인하겠습니다» 예고, 결정 요구는 3번째=마지막 블록)이라 «기준을 고쳐야 한다»가 맞고, 동시에 N1-2(:154)가 «부채 상태 1줄»만 요구해 리터럴이 사라지고 의역이 들어갔다 — 근거: b3r3_final.py 출력(텍스트 블록 3·앵커 포함 0·마지막 블록에 ⓐ/ⓑ 결정 요구·«어떤 실행(재동결 포함)도 하기 전에»); 설계 :96; dddjango-web.md:154 — 제안: 설계 §3 B3 ②를 «결정 요구를 담은 assistant 텍스트 블록(실행 종료 직전 블록)에 리터럴 앵커 + 그 이전 금지 tool_use 0»으로 고치고, :154(SKILL 동형)를 «확정 폴더의 hook 줄을 원문 그대로 인용한 뒤 해석 1줄»로 바꿔 grep 가능성과 오독 억제를 함께 얻는다.
- [MINOR] 오독의 직접 원인은 hook 문구 «(observation v1/absent)»의 «v1»이 규범의 «`interactions.json` version 1»(:143)과 어휘 충돌하는 것 — Coordinator가 «v1 표준 포맷 부재 … 훅이 요구하는 interactions.json v1 포맷», «이미 상호작용을 관찰했지만 포맷만 없음»으로 풀어 defer를 권했다(결정 브리프 오도) — 근거: evidence_debt_hook.py:119-120; b3r3_final.py 배너 «① 조작 상태 증거 부채 결정» 문단 — 제안: 판형을 «<k>/<n> archive case(s) have no interaction-state observation — source_observation is static-only (no interactions pointer: ×a) or missing/unreadable (×b); dropdown/dialog/toggle states were never driven — not a file-format issue · decision required before any run on this folder»로 바꾸고 `_case_has_evidence`가 사유 enum(`static_only`/`missing`/`unreadable`)을 돌려주게 한다(«v1» 어휘 제거).
- [MINOR] B3 3회차는 설계가 요구한 격리(`CLAUDE_CONFIG_DIR`·설치본 비활성) 없이 사용자 설정·설치본이 로드된 채 돌았다(허용 규칙 28건 적용 — `Bash(git:*)`로 `git status`가 실행됨, `--allowedTools "…Bash(ls:*)"`보다 넓음). 유효성은 디버그 로그 «Plugin "dddjango-web" from --plugin-dir overrides installed version»(:33)·init 이벤트 `plugins[0].source=dddjango-web@inline`에 기대는데 behavior.md가 그 근거를 인용하지 않는다 — 근거: b3r3-debug.log:20·:31·:33; rv_stream_tools.py 출력 — 제안: behavior.md B3 3회차에 로그 :33과 init `plugins` 항목을 인용하고 «격리 미적용·override 로그로 대체» 1줄.
- 정직성 확인(주장=증거): ① 두 이벤트 실행·주입 — 로그 :135(SessionStart 1935 chars)·:183(UserPromptSubmit 1838 chars) 일치 · `${CLAUDE_PLUGIN_ROOT}` 치환은 실행 성공으로 입증. ③ tool_use 6건(Bash pwd/git status/ls · Read build-state · Bash ls _history/cat config · Read refreeze-diff · Read visual-check · ToolSearch) — `archive_design.py`·`--compare-build`·`.dddjango-web/` 쓰기 0건 일치. result success · 7 turns · 185 s · $0.69 일치. «assistant 텍스트 3블록·마지막이 배너» 일치.

## Q7. 릴리즈 영향

- [MINOR] DEVELOPMENT §6(:149)의 «hooks.json이 바뀐 릴리즈는 노트에 Codex 재신뢰 1줄» 규칙이 절차에 배선되지 않았다 — `_release`는 `gh release create --generate-notes`(Makefile:119·DRY 안내 :91)로 노트를 자동 생성해 규칙은 사람 기억에만 의존하고, REQUEST_GUIDE는 Claude 쪽(«플러그인 갱신 후 새 세션부터 자동 — 추가 조치 없음»)을 적지 않아 «Claude 자동 / Codex `/hooks` 재신뢰» 비대칭이 사용자에게 보이지 않는다 — 근거: Makefile:91·:119; REQUEST_GUIDE.md:111-117(Codex만); DEVELOPMENT.md:149 — 제안: `_release`에서 `git diff --name-only <직전 태그>..HEAD -- dddjango-web/hooks/hooks.json`이 비어 있지 않으면 `--notes-file`로 재신뢰 문장을 붙이거나 최소한 실행 로그에 경고를 내고, REQUEST_GUIDE에 Claude 1줄을 더한다.
- 발견 없음으로 확인한 것: 매니페스트 버전 1.1.13 유지(Claude·Codex 양쪽 — 릴리즈 타깃 소유). Claude Code는 플러그인 활성만으로 `hooks/hooks.json`을 로드(B3 로그 :29 «Read hooks.json for plugin dddjango-web (enabled=true)»·:69 «Loading hooks from plugin») — 사용자 행동 불요가 맞다. DEVELOPMENT §1 지도에 `hooks/hooks.json` 행 2개(Claude·Codex) 존재. `claude plugin validate --strict`는 hooks.json JSON 구문을 실제로 검사한다(사본에 깨진 hooks.json을 넣으면 «Invalid JSON syntax … breaks the entire plugin load» FAIL — behavior.md의 «hooks/hooks.json 포함» 주장 성립).

판정: 조건부 승인(MAJOR 3) — MAJOR 3 · MINOR 11 · BLOCKER 0.

## 실행 기록

① 미러·브랜치 상태
```
$ git log --oneline main..HEAD
43d70fcc docs(web): 증거 부채 hook 행동 시험 기록 B1~B3 (T4)
125cce76 docs(web): 증거 부채 결정 규범 — step 4 앵커·배너/종료 보고 표기·build-state evidence_debt·REQUEST_GUIDE (T3)
bcc8ef16 feat(web): 플러그인 hooks.json(Claude·Codex)·계약 검사·verify-web 배선 (T2)
720f96bd feat(web): 증거 부채 술어·hook 스크립트 (T1)
dd934f2e docs(web): 증거 부채 hook — 진단·설계 v2·1차 적대 검토
$ diff -rq --exclude=__pycache__ dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts; echo mirror exit=$?
mirror exit=0
$ diff dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md; echo guide exit=$?
guide exit=0
$ git status --short
?? .venv
$ git diff -U0 main..HEAD -- dddjango-web/commands/dddjango-web.md | grep '^@@'
@@ -70,0 +71 @@ / @@ -128 +129 @@ / @@ -136 +137 @@ / @@ -153 +154 @@
(SKILL.md: @@ -123,0 +124 / -150 +151 / -158 +159 / -176 +177)
```

② 테스트·계약·검증
```
$ python3 test/test_evidence_debt.py            → Ran 15 tests in 0.068s  OK
$ python3 test/test_evidence_debt_hook.py       → Ran 16 tests in 0.806s  OK
$ python3 test/test_design_evidence.py          → Ran 40 tests in 25.021s OK
$ python3 test/test_interaction_evidence.py     → Ran 45 tests in 10.856s OK
$ python3 test/test_design_archive.py           → Ran 42 tests in 8.477s  OK
$ python3 workspace/tools/web_hooks_contract.py --self-test → [web-hooks] self-test PASS
$ python3 workspace/tools/web_hooks_contract.py → [web-hooks] PASS: Claude·Codex hooks.json 계약(이벤트 2종·command·timeout·스크립트 실재)
$ claude plugin validate dddjango-web --strict  → ✔ Validation passed (exit 0)
$ make verify-web; echo exit=$?                 → exit=0
   … fixtures_evidence_debt.sh: Ran 15 OK · Ran 16 OK · [verify-web] codex 미러 byte 대조 · REQUEST_GUIDE byte 미러 대조 · hooks.json 계약 PASS
$ python3 --version → Python 3.14.7
```

③ 봉인
```
$ python3 workspace/tools/manifest_seal.py --check; echo exit=$?
[manifest] **RED — 실런 금지** · 지적 19건
  ✗ sealed_commit 의 내용이 봉인값과 다르다 — protocol/Makefile
  ✗ PENDING 잔존: external_annex.orders.O-4.* … (기존 draft 항목 · 이 브랜치 무관)
exit=2
$ python3 workspace/tools/manifest_seal.py --check --draft
[manifest] green · 그룹 10 · 봉인 파일 261 · 배정 18런 · 상태 draft
$ git diff -U0 main..HEAD -- workspace/eval/ab/T2-0b-manifest.json
- "Makefile": "11a2c70f…" / + "Makefile": "a1c765c9…" · sealed_commit f9972967 → 720f96bd
$ git show 720f96bd:Makefile > mk_br_sealed; cmp mk_br_sealed Makefile → differ: char 6573, line 106 (exit 1)
$ git show f9972967:Makefile > mk_main_sealed; git show main:Makefile > mk_main_head; cmp → differ: char 364, line 6  (main도 동일 패턴)
```

④ B2 재현(A8 사본 · scratchpad/b2_runner.py)
```
folders: 9
user-prompt run0: 48 ms · run1: 47 ms · run2: 47 ms · exit 0 · stderr=''
session-start run0: 45 ms · run1: 46 ms · run2: 47 ms · exit 0
systemMessage: [dddjango-web] evidence debt: undecided 8 · deferred 0 · observing 0
… 20260912-1640-web-related-persons: 12/12 archive case without interaction evidence (observation v1/absent) · decision required before any run on this folder
build-state: 9폴더 전부 design_status=ready · evidence_debt 키 없음 (web-auth-screens는 design-input.json 없음 → 미산정)
```

⑤ Q2 parity(scratchpad/rv_q2_parity.py — test_interaction_evidence 픽스처 재사용, in-process validate_inputs vs build_debt)
```
baseline v2 + interactions          | checker: OK(exit 0)                                                     | predicate: debt 0/1 clear
v1 observation                      | DEFECT ['…source_observation: interaction evidence required (version 2 with interactions)'] | debt 1/1 undecided
v2 without interactions key         | DEFECT ['…source_observation: exact version 1 or 2 fields required']    | debt 1/1 undecided
v2 missing required field trace     | DEFECT ['…exact version 1 or 2 fields required']                        | debt 0/1 clear      <== MISMATCH
v2 extra unknown field              | DEFECT ['…exact version 1 or 2 fields required']                        | debt 0/1 clear      <== MISMATCH
version as string "2"               | DEFECT ['…exact version 1 or 2 fields required']                        | debt 1/1 undecided
pointer extra key                   | DEFECT ['…source_observation: exact path/sha256 object required']       | debt 0/1 clear      <== MISMATCH
pointer missing sha256              | DEFECT ['…source_observation: exact path/sha256 object required']       | debt 0/1 clear      <== MISMATCH
pointer sha256 mismatch only        | DEFECT ['…source_observation: sha256 mismatch']                         | debt 0/1 clear (설계: 해시 미검사)
pointer path missing file           | DEFECT ['…source_observation.path: missing path (…)']                    | debt 1/1 undecided
pointer absolute path               | DEFECT ['…source_observation.path: nonempty relative path required']    | debt 1/1 undecided
pointer escapes build (../)         | DEFECT (no observation msg) +1 other                                     | debt 0/1 clear (양쪽 resolve 후 내부 → 수용)
source_observation absent           | DEFECT ['…exact path/sha256 object required']                           | debt 1/1 undecided
observation file broken JSON        | DEFECT ['…sha256 mismatch', '…invalid JSON']                            | debt 1/1 undecided
v1 with legacy_v1=True (K3)         | DEFECT (no observation msg)                                             | debt 1/1 undecided (설계 §0: 고지 층)
v1 + design_status=pending/blocked/none/키없음 | DEFECT ['…interaction evidence required …']                  | None(not applicable) (설계 §2)
archive+static manifests            | DEFECT (no observation msg) +3 other                                     | debt 0/1 clear
manifests=[]                        | DEFECT ['…requires an archive HTML/component entrypoint'] +3 other      | None
case entrypoint not in archive rows | DEFECT ['…requires an archive HTML/component entrypoint'] +3 other      | debt 0/1 clear
```
⑤′ null 재실험(scratchpad/rv_q2_null.py — 픽스처 sync의 포인터 재결속을 우회해 직접 기록)
```
checker: ['cases[related/list].interactions: exact path/sha256 object required']
predicate: 0 clear
```

⑥ Q3 침묵·권한 probe(scratchpad/rv_q3_silence.py)
```
A) .dddjango-web with config.json only   session-start -> (0, '', '')
B) in-progress build without design-input session-start -> (0, '', '')
C) in-progress build with design-input    session-start -> (0, '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "[dddjango-web] evidence hook active — scanned 1 build(s): undecided 0 · deferred …', '')
D) DEVNULL stdin, no builds -> 0 '' ''
E) CLAUDE_PROJECT_DIR under mode-000 parent -> 0 '' ''   (3.14: is_dir가 False 반환 · raise 없음)
```

⑦ B3 3회차 증거 대조
```
$ grep -n … b3r3-debug.log
:29  Read hooks.json for plugin dddjango-web (enabled=true): <worktree>/dddjango-web/hooks/hooks.json
:31  Loaded inline plugin from path: dddjango-web
:33  Plugin "dddjango-web" from --plugin-dir overrides installed version
:69  Loading hooks from plugin: dddjango-web
:129 Hooks: Parsed initial response: {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[dddjango-web] evidence hook active — scanned 8 build(s): undecided 8 …
:135 Hook SessionStart (python3 "${CLAUDE_PLUGIN_ROOT}/scripts/evidence_debt_hook.py" session-start) provided additionalContext (1935 chars)
:183 Hook UserPromptSubmit (python3 "${CLAUDE_PLUGIN_ROOT}/scripts/evidence_debt_hook.py" user-prompt) provided additionalContext (1838 chars)
:20  Applying permission update: Adding 28 allow rule(s) to destination 'userSettings': [… "Bash(git:*)" …]
$ python3 b3r3_analyze.py
events: 148 · ② 첫 assistant 텍스트에 앵커: False · ③ tool_use 6건 · 금지 tool_use 0 · result: success · turns 7 · cost 0.694 · duration_ms 185160
$ python3 b3r3_final.py
assistant text blocks: 3 · [0] 60자 «…확인하겠습니다» · [1] 138자 · [2] 1798자(배너) · 앵커 포함 블록 0 · 결정 요구 포함: True
배너 발췌: «세션 시작 훅이 이 폴더를 "12/12 archive case without interaction evidence (v1 표준 포맷 부재)"로 표시 … 현재 훅이 요구하는 `interactions.json` v1 포맷은 없습니다 … ⓑ defer … 이 빌드를 G2 승인·마무리로 바로 진행하는 데는 지장이 없습니다»
$ python3 rv_stream_tools.py
Bash(pwd && git status … ls -la .dddjango-web/ …) result is_error=False «fatal: not a git repository …»
Read build-state.json · Bash(ls _history && cat config.json) · Read refreeze-diff.json · Read visual-check.md · ToolSearch(AskUserQuestion)
init.plugins[0] = {'name': 'dddjango-web', 'path': '<worktree>/dddjango-web', 'source': 'dddjango-web@inline', 'version': '1.1.13'}
```

⑧ 검사기 위임 전후
```
$ git show main:dddjango-web/scripts/check_design_evidence.py | sed -n 1049,1052p
    if version == 1 and not legacy_v1:
        issues.append(f'{label}.source_observation: interaction evidence required '
                      '(version 2 with interactions)')
        return None
HEAD :1050-1054
    # 조작 상태 증거 유무는 evidence_debt 술어와 단일 출처 …
    if not legacy_v1 and not has_interaction_evidence(observed):
        issues.append(… 동일 메시지 …)
        return None
```

⑨ plugin validate가 hooks.json을 보는지(scratchpad 사본)
```
$ claude plugin validate plugin-copy --strict   (hooks.json = 깨진 JSON)
Validating hooks: …/plugin-copy/hooks/hooks.json
✘ Found 1 error: json: Invalid JSON syntax … At runtime this breaks the entire plugin load.
✘ Validation failed
```

⑩ 매니페스트·릴리즈
```
dddjango-web/.claude-plugin/plugin.json: "version": "1.1.13"
codex-dddjango-web/.codex-plugin/plugin.json: "version": "1.1.13", "skills": "./skills/"  (hooks 필드 없음)
Makefile:119  gh release create "$$TAG" --verify-tag --title "$(NAME) v$$V" --generate-notes
docs/DEVELOPMENT.md:149  `hooks/hooks.json`이 바뀐 dddjango-web 릴리즈 … 릴리즈 노트에 «Codex 사용자는 `/hooks`에서 재신뢰» 1줄
```
