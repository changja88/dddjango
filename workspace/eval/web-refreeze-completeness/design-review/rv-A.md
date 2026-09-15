# 적대 검토 A — 규범 정합성 (2026-09-15)

대상: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`
실측 표본: `~/Desktop/spring_dream_server/.dddjango-web/20260912-1640-web-related-persons`(A8 · 읽기만)
도구: 기본 검색·편집만 사용(이 워크트리에 `.serena/project.yml`·`graphify-out/graph.json` 없음 — opt-in 표식 부재로 Serena·Graphify 미사용).

## 판정

**구현 진입 불가** (BLOCKER 5 · MAJOR 6 · MINOR 4)

R1의 폐기/보존 경계가 실제 파일 배치·검사기 소비와 어긋나고(B1·B4·B5), R2의 성공/실패
판정이 기존 «보완 루프» 규범과 충돌하며(B2), R3이 v1.1.14 hook의 주입 문구와 정면으로
모순된다(B3). R4의 제거 목록은 정본·미러 합쳐 최소 8곳을 빠뜨렸다(M4).

---

## BLOCKER

### B1 `captures/**` 전량 폐기가 «보존»하기로 한 `visual-evidence.json`의 포인터를 끊는다

- 근거(설계): 설계 §2 R1 폐기표 —
  > `captures/**`(원본 case 캡처 · `<screen>-interactions.json` · 상태 캡처 · `<screen>-declared.json`) | 브라우저 관찰 · `observe_interactions.mjs`

  같은 절 보존표 —
  > `visual-evidence.json` · `render-audit-impl.json` | 구현 증거(G2 산출) — R3이 stale로 표시만 한다
- 근거(규범): `dddjango-web/skills/implementation-ui/references/design-evidence.md:403`
  > `"capture": {"path": "captures/login-implementation.png", "sha256": "2222…"}`

  즉 **구현 캡처도 같은 `captures/`에 산다.**
- 근거(실측): A8 `visual-evidence.json`의 12 case 전부가 `captures/*-impl.png`를 가리킨다
  (`related/list → captures/related-390x844-01-list-impl.png` 등). 같은 폴더 `captures/`에
  `*-original.png` 27장과 `*-impl.png` 28장이 섞여 있다(총 55 파일).
- 근거(검사기): `dddjango-web/scripts/check_design_evidence.py:1324`
  > `captured = pointer(build, row.get('capture'), f'{here}.capture', issues, image=True)`

  `pointer()`는 파일 실재+sha256 일치를 요구한다(`:65-81`).
- 왜 막는가: 재동결이 `captures/**`를 통째로 치우면 «보존» 대상이라던 `visual-evidence.json`은
  **stale이 아니라 dangling**이 된다. R1의 재생성표에는 구현 캡처를 다시 만드는 주체가
  아예 없다(재동결은 §0대로 구현물을 건드리지 않는다). 결과는 `validate_visual` →
  `[DESIGN] BLOCKER … capture: missing`이며, 설계가 의도한 «stale 표시»가 아니라 복구 불가한
  증거 소실이다(git 이력으로만 되살릴 수 있다).
- 확인한 반례: 없음. `captures/` 하위를 원본/구현으로 가르는 규범 문장이나 검사기 로직을
  찾지 못했다 — 파일명 접미(`-original`/`-impl`)는 관례일 뿐 어디에도 성문화돼 있지 않다.

### B2 «prepare exit 0 = 성공, 아니면 롤백»이 기존 «보완 루프» 규범을 지운다

- 근거(설계): §2 R2
  > 3. `check_design_evidence.py … --phase prepare`를 실행한다. **exit 0 = 재동결 성공.**
  > 4. 성공이면 `_prev-<ts>`를 삭제한다. 실패면 새로 생긴 산출물을 지우고 `_prev-<ts>`의 내용을 원위치로 되돌린 뒤 …
- 근거(규범): `dddjango-web/commands/dddjango-web.md:143`
  > **보완**: 잔여·`partial`·연결되지 않은 표면·`outside_root`·`declared_unmatched`·`unclickable`·`discovery_limits`는 네가 실제로 닫는다 — 선언(`--declared`·`--excluded-regions`)과 보완 조작으로 다시 돌리고, 그래도 남으면 case를 추가해 표면을 이으며, 마지막으로 `scope.md` 사용자 승인 원문을 받아 `design-input.json`의 `interaction_exclusions` 행 … 을 단다.
- 근거(코드): `--phase prepare`도 잔여·표면·예외 검사를 전부 돈다 —
  `check_design_evidence.py:1406`
  > `spec, input_value, items = validate_inputs(build, project, require_review=args.phase != 'prepare')`

  `require_review`는 `coverage_review` **포인터 해소만** 건너뛴다(`:1098-1101`). v2 관찰이면
  `validate_interactions`(`:1230`) → `_check_residual`(`:963-975`)·`_check_surfaces`(`:947-961`)가 그대로 돈다.
- 왜 막는가: 조작 상태 첫 수집에서 잔여 0으로 끝나는 일은 규범이 전제하지 않는다(위 «보완»
  문장이 그 전제다). 설계대로면 **첫 prepare exit 2가 곧 «재동결 실패»**여서 방금 수십 분 돌린
  수집물을 지우고 `_prev`를 되돌린다. 보완 조작→재실행 루프로 들어갈 길이 없고, 매 시도가
  같은 지점에서 같은 롤백을 반복한다(A8 12 case 기준 시도당 수십 분).
- 확인한 반례: 없음. 설계 어디에도 «prepare 실패 = 보완 루프 진입»을 실패와 구별하는 문장이 없다.

### B3 부채 결정 게이트에서 재동결을 빼는 것이 v1.1.14 hook 주입 문구와 정면 모순

- 근거(설계): §2 R3 마지막
  > **부채 결정 질문(ⓐ/ⓑ)을 재동결에는 붙이지 않는다** … 결정 게이트는 재동결이 **아닌** 실행(조회·보고·구현 재진입)에만 남는다.
- 근거(hook · 매 프롬프트 주입): `dddjango-web/scripts/evidence_debt_hook.py:36-40`
  > `'(refreeze, inspection, reporting); implementation re-entry requires ⓐ) before any run on that '`
  > `'folder, including refreeze-only or scope-only runs. Quote the folder line verbatim in the banner.'`

  같은 파일 `:132`
  > `'never driven (not a file-format issue) · decision required before any run on this folder'`
- 근거(정본 앵커): `dddjango-web/commands/dddjango-web.md:129`
  > 그 폴더를 읽는 `ls` 이후 **어떤 실행·쓰기(재동결·재수집·조회 포함) 전에** 사용자 결정을 같은 질문에 합류시켜 받는다

  같은 줄
  > **ⓑ defer가 허용하는 것** = 재동결·조회·보고, 그리고 완료 빌드의 G2 승인·마무리 backstop
- 근거(사용자 문서): `dddjango-web/REQUEST_GUIDE.md:115-116`
  > 부채가 있으면 그 폴더로 어떤 작업(재동결·조회 포함)을 하기 전에 «지금 수집 / 유보» 결정을 묻습니다.
  > 유보는 재동결·조회·보고와 완료 빌드의 마무리만 허용하며 …
- 왜 막는가: hook은 **결정적**이고 세션 시작·매 프롬프트마다 이 문구를 컨텍스트에 주입한다.
  설계 R4 제거표에는 `evidence_debt_hook.py`도 `REQUEST_GUIDE.md`도 `commands:129`도 **없다**.
  구현하면 런타임에 «재동결 전에도 결정을 받아라»(hook)와 «재동결에는 붙이지 않는다»(커맨드)가
  동시에 살아 있게 된다 — 진단이 G-C로 지목한 «대리 기록»을 다시 부르는 정확한 조건이다.
  `evidence_debt_hook.py`는 Codex와 byte 미러라 `make verify`의 `diff -rq`(Makefile:96)가
  한쪽만 고치면 red를 낸다 — 즉 «빠뜨리면 조용히 넘어가는» 항목도 아니다.
- 확인한 반례: 설계 R5가 `:154` 종료 보고 인용 의무는 유지한다고 했으나, `:154`는 스스로
  «반복 표기이지 결정 앵커가 아니다(앵커는 step 4)»라고 못박는다 — 앵커(`:129`)를 안 고치면
  모순이 남는다.

### B4 `motion-notes.md`만 폐기하고 `design-spec.md`를 보존하면 모션 전수성 검사가 red가 된다

- 근거(설계): R1 폐기표에 `motion-notes.md`(재생성 주체 «Coordinator(정적 스캔+사용자 문답)»),
  보존표에 `design-spec.md`(«architect 산출 설계 명세»).
- 근거(검사기): `dddjango-web/scripts/check_motion_spec.py:360-366`
  > `# 전수성 — 양방향(상태 행·판형 위반 id 제외 …)`
  > `findings.append(f"전수성: notes {mid} 가 처분 표에 없음(빈칸 0 위반)")`
  > `findings.append(f"전수성: 처분 표 {sid} 가 notes에 없음(관찰 근거 없는 처분)")`

  id 판형은 `ID_RE = re.compile(r"^m\d+$")`(`:37`)로 빌드 내 일련번호이며,
  `commands/dddjango-web.md:142`가 «id는 `m1…mN`(빌드 내 유일)»로 규정한다.
- 왜 막는가: 재기록된 notes의 m-id 집합은 이전과 같다는 보장이 없다(설계 §4 우회 3이
  «사용자 문답이 입력이라 완전 자동이 아니다»라고 스스로 인정한다). 보존된 `design-spec.md`의
  처분 표는 옛 id를 가리키므로 **양방향 전수성이 동시에 깨진다**. 설계에는 id 재발행·재매핑
  절차도, architect 반송 경로도 없다. `commands:44`의 `g2_visual`은 «check_motion_spec 결과
  (발견 N건·red 수락 여부와 사유)도 합류 기록한다»를 의무로 두므로 조용히 넘길 수도 없다.
- 확인한 반례: `check_motion_spec.py:22-23`의 레거시 면제(«헤더 미검출(레거시 산문 판형)은
  [warn]+exit 0»)는 **표 판형이 없을 때만** 열린다. 재기록된 notes는 표 판형이므로 해당 없음.

### B5 전량 재수집이 승인된 `interaction_exclusions`를 끊는데 prepare가 그것을 요구한다 (설계 §6 쟁점 5)

- 근거(설계): R1이 `design-input.json`을 폐기·재생성 대상에 넣는다. §6 쟁점 5는
  > 전량 재수집이 `interaction_exclusions`(사용자 승인 제외 행)를 어떻게 이어받는가 — … 절차 문장이 필요하다.

  로 **열어둔 채** T1~T4 계획으로 넘어간다.
- 근거(코드): 예외 행은 오직 `design-input.json`에만 산다 —
  `check_design_evidence.py:1082-1083`
  > `required = {'version', 'reference_root', 'manifests', 'scope', 'coverage_review', 'cases'}`
  > `allowed = required | {'host_files', 'interaction_exclusions'}`

  그리고 그 행이 없으면 잔여가 그대로 결함이 된다 — `:964-966`
  > `excluded, _surfaces = _exclusion_rows(spec)`
  > `remaining = [unit for unit in interaction_residual(document) if _unit_key(*unit) not in excluded]`

  표면 예외도 같다(`:955-961`). 이 둘은 앞서 본 대로 **prepare에서도 돈다**.
- 현행 계약(질문 6의 답): 예외 행은 ①`design-input.json.interaction_exclusions`의 정확 필드
  집합(`EXCLUSION_UNIT_FIELDS`/`EXCLUSION_SURFACE_FIELDS` — `:225-226`), ②`approval_quote`가
  **보존되는 `scope.md` 본문의 부분문자열**(`_check_exclusions:861·878` — `quote not in approved`면
  결함), ③`scope_ref = <경로>#<앵커>`의 앵커 실재(`:880-892`), ④`len(rows)*10 > active`
  상한(`:893-895`, 분모는 **이번에 새로 수집된** interactions 문서들의 활성 id 합집합)으로
  성립한다. 따라서 **승인 원문 자체(②)는 `scope.md` 보존 덕에 살아남지만, 행(①)은 살아남지
  않고 단위 키(`target`·`action`·`option`)는 새 관찰 문서의 target id에 다시 맞춰야 하며,
  상한(④)의 분모는 새 수집 결과로 바뀐다.** 즉 «scope.md가 있으니 재적용 가능»은 절반만 맞다 —
  기계적 이월이 아니라 **새 문서 기준으로 행을 다시 짓는 작업**이다.
- 왜 막는가: 예외를 쓰던 빌드는 새 design-input.json에 행이 없으면 prepare가 잔여로 exit 2 →
  B2의 롤백에 걸린다. 설계는 이 절차를 쓰지 않은 채 R2-3의 성공 기준을 세웠다.
- 확인한 반례: A8은 `interaction_exclusions`가 `None`이라 이 경로를 안 탄다 — **B1 행동 시험이
  A8 사본에서만 수행되므로 B5는 B1~B5 어디에서도 드러나지 않는다.**

---

## MAJOR

### M1 «재동결의 끝»이 §1·R1·R2·R3에서 서로 다르다

- 근거: §1
  > **재동결** = ① 빌드 폴더의 시안 동결물 전량 폐기 → ② Phase 0 step 5 동결 절차 전체 재실행 → ③ `check_design_evidence.py --phase prepare` exit 0으로 성공 판정.
- 근거: R1은 `coverage-review.md`를 폐기·재생성 대상에 넣고 재생성 주체를 «`design-review-web`
  독립 입력범위 검토 재실행»으로 적는다. 그런데 그 검토는 **step 5-6 안에 있다**
  (`commands/dddjango-web.md:146` — prepare → 독립 검토 → `--phase inputs` → ready).
- 근거: R3은 그 뒤에도 `design_status`가 **blocked**이고 «독립 검토 → inputs exit 0으로만 ready»라고 한다.
- 왜 문제인가: ②가 «step 5 전체»면 5-6(검토+inputs+ready)까지 포함되어 ③(prepare)과 R3(blocked)이
  모순이고, ②가 5-5까지면 R1의 `coverage-review.md` 재생성 주체가 재동결 밖에 있다. T1~T4 어느
  작업도 이 경계를 확정하지 않는다.

### M2 `visual_gate: "stale-after-refreeze"`는 아무도 읽지 않고, 실제 파급은 설계가 말하지 않은 곳에서 터진다

- 근거(무소비): `build-state.json`을 읽는 코드는 세 곳뿐이고 어느 것도 `visual_gate`를 모른다 —
  `evidence_debt.py:99-103`(`evidence_debt`), `:139`(`design_status`),
  `backstop.py:74-77`(`has_design_screen`), `backstop.py:145-170`(`git_snapshot`·`has_design_screen`·
  `phase`·`g2_approved`·`implementation_visual`·`design_status`·`slices`). 스키마 정합 검사도 없다.
- 근거(실제 파급): `backstop.py:288-293`은 발견한 모든 시안 빌드에 대해 **design_status와 무관하게**
  > `design_spec, input_value, _items = validate_inputs(build, root, legacy_v1=legacy_v1)`
  > `implementation_value: str = implementation_digest(root, design_spec)`
  > `validate_visual(build, root, design_spec, input_value, implementation_value)`

  를 돈다. 재동결 직후엔 `coverage-review.md`가 없어 `require_review=True` 경로가
  `pointer()`에서 결함을 내고(`:1098-1101`), `validate_visual`은 `input_digest: stale or incorrect`
  (`:1296-1297`)를 낸다.
- 근거(우회 차단): `backstop.current_nondesign_scope:160-170`은 **모든** 시안 빌드가
  `phase=='finalize' ∧ g2_approved ∧ implementation_visual=='verified' ∧ design_status=='ready'`
  일 때만 생략한다. R3이 design_status를 blocked로 되돌리므로 이 생략 경로가 닫힌다.
- 왜 문제인가: 완료 빌드를 한 번 재동결하면 **그 프로젝트의 이후 모든 dddjango-web 실행**
  (같은 화면이 아닌 별건 작업 포함)의 마무리 backstop이 `[DESIGN] BLOCKER`로 막힌다. 이는
  `commands:129`가 defer에게 명시적으로 허용했던 «완료 빌드의 G2 승인·마무리 backstop»을
  무효화한다. 설계는 이 반경을 어디에도 적지 않고, 대신 소비자 없는 키를 새로 만든다.

### M3 `design_status=blocked`가 그 폴더를 부채 hook의 시야에서 지운다 — B3 시험이 공허하다

- 근거: `dddjango-web/scripts/evidence_debt.py:139-140`
  > `if not isinstance(state, dict) or state.get('design_status') != 'ready':`
  > `    return None`

  docstring(`:129`)도 «None = 판정 대상 아님(design-input 없음 · 정적 시안 · **ready 아님**)».
- 근거: R2 step 1이 `design-input.json`을 `_prev-<ts>/`로 옮기는 동안에도 같다 —
  `evidence_debt_hook.py:114`
  > `return [p for p in folders if (p / 'design-input.json').is_file()]`
- 왜 문제인가: ① 설계 §3의 B3 합격 조건 «그 폴더가 부채 목록에 없음(undecided·deferred 어디에도)»은
  **부채가 해소돼서가 아니라 빌드가 평가 대상에서 빠져서** 통과한다 — 증거 가치 0인 시험이다.
  ② 재동결 후 ready 복귀 전에 세션이 끝나면 그 폴더는 `evidence_debt` 키도 없고(R3이 제거)
  hook 줄도 없는 **완전 침묵 상태**가 된다. v1.1.14가 닫으려던 구멍이 다른 문으로 열린다.
- 부기: R3은 `evidence_debt` 키 제거 시점(수집 전/후, 롤백 시 복원 여부)도 정하지 않는다.
  R2-4 롤백이 파일만 되돌리고 build-state 키는 되돌리지 않으면 부채는 살아나는데 결정 기록은
  사라진다(hook은 다시 undecided로 볼 것이므로 fail-safe 방향이긴 하나, 규정이 없다).

### M4 R4 제거 목록 누락 — 정본·미러 합쳐 최소 8곳

설계 R4 표에 **없는** 소비·언급 위치(전수 grep 결과):

| 위치 | 내용 |
|---|---|
| `dddjango-web/scripts/evidence_debt_hook.py:36-40` (+ byte 미러 `codex-dddjango-web/skills/dddjango-web/scripts/evidence_debt_hook.py`) | `DECISION_LINE`의 «defer = … (refreeze, …) … before any run on that folder, **including refreeze-only** or scope-only runs» |
| `dddjango-web/scripts/evidence_debt_hook.py:132` (+ 미러) | undecided 줄의 «decision required before any run on this folder» |
| `dddjango-web/scripts/test/test_evidence_debt_hook.py:81,90` · `test_evidence_debt.py:164` (+ 미러) | defer 픽스처 quote가 «지금은 재동결만 …» — 재동결이 defer 허용 경로라는 전제 |
| `dddjango-web/REQUEST_GUIDE.md:115-116` (+ byte 미러 `codex-dddjango-web/REQUEST_GUIDE.md`, Makefile:104가 대조) | 사용자 문서의 «어떤 작업(재동결·조회 포함) 전에 … 결정», «유보는 재동결·조회·보고 … 허용» |
| `dddjango-web/commands/dddjango-web.md:129` (+ Codex `SKILL.md:151`) | 결정 앵커 본문 — «재동결·재수집·조회 포함», «ⓑ defer가 허용하는 것 = 재동결·…» |
| `dddjango-web/commands/dddjango-web.md:130` (+ Codex `SKILL.md:152`) | «재동결 staging도 선택한 폴더 안에서 기존 절차를 따른다» — R2가 staging을 `_prev`로 바꾸면 사문 |
| `dddjango-web/agents/design-review-web.md:25` (+ Codex `skills/dddjango-web-design-review-web/SKILL.md:28`) | 리뷰어 감사 목록의 `carried` — `--compare-build` 전용 개념 |
| `dddjango-web/scripts/check_design_evidence.py:1139,1142-1143` (+ byte 미러) · `skills/implementation-ui/references/design-evidence.md:115` | `carried_from` 행 필드 수용·문서화. R4는 `:27·:338·:342`만 적는다 |

추가로 R4 표의 `commands/dddjango-web.md` 행은 `:9`·`:70`·`:137`·`:146`·`:171`·`:205`·`:234`만
적는데, 같은 파일의 «재동결» 출현은 `:9 :70 :129 :130 :134 :137 :146 :154 :171 :205 :227 :234`
12곳이다(Codex `SKILL.md`는 `:8 :123 :151 :152 :156 :159 :169 :177 :194 :228 :250 :258`).

### M5 «재동결»이라는 말이 백엔드 계약 축까지 덮는데 설계가 범위를 좁히지 않는다

- 근거: `dddjango-web/commands/dddjango-web.md:129`
  > **«외부 진실 스냅샷(openapi 동결본·design-ref·motion-notes·render-audit) 재동결 여부» 질문을 같은 선택에 합류**시키고
- 근거: 같은 파일 `:227`
  > **architect가 "동결본에 엔드포인트 없음"을 보고하면**: ⓐ 재동결(URL 재확인·서버가 최근 갱신됐을 수 있다) / ⓑ …
- 근거(설계): §0 비목표 — «백엔드 계약(`openapi-full.json`·`server-contract`) 재동결 — 별도 축·현행 유지».
  그런데 R1은 «재동결 = 시안 동결물 전량 폐기»를 **재동결 일반의 정의**(§1)로 세운다.
- 왜 문제인가: 사용자가 `:129`의 단일 질문에 «재동결»이라고 답하면 새 정의상 openapi까지
  전량 폐기 대상으로 읽힌다. `:129`·`:227`은 R4 제거표·T1 작업 목록 어디에도 없어, 용어가
  두 축에 걸친 채로 남는다.

### M6 `<screen>-declared.json`의 위치와 재생성 주체가 둘 다 틀렸다

- 근거(설계 R1): 폐기표가 «`captures/**`( … · `<screen>-declared.json`) | 브라우저 관찰 · `observe_interactions.mjs`»
- 근거(규범): `dddjango-web/commands/dddjango-web.md:143`
  > 소스 검토로 찾은 비의미 대상은 `<산출물 폴더>/<screen>-declared.json`(행마다 `selector`·`reason`·선택 `value`)에 적어 `--declared`로 준다.

  `:171`의 커밋 목록도 «captures/<screen>-interactions.json과 그 상태 캡처·<screen>-declared.json»으로
  **분리 열거**한다 — 빌드 루트다.
- 근거(주체): `:9`·`:234`
  > **대상 선언(`<screen>-declared.json` — 너는 서기다: 소스 검토로 찾은 selector·사유)**
- 왜 문제인가: ① 경로가 틀려 «captures/** 폐기»를 문자대로 집행하면 declared.json은 살아남는다
  (설계 의도와 반대). ② 그것은 드라이버의 **산출이 아니라 입력**이다(`--declared`) — R1의
  재생성 주체가 «observe_interactions.mjs»면 순환이다. ③ 실제로 폐기하면 매 재동결마다
  소스 검토를 처음부터 다시 해야 하는데 §4 우회 목록에 그 비용이 없다.

---

## MINOR

### m1 `_prev-<ts>`가 이미 존재하는 `_history/vN` 관례와 나란히 생긴다
- 근거(실측): A8 빌드 폴더에 `_history/{v1,v2,v3,v4}`가 실재한다.
- 근거: `dddjango-web/skills/implementation-ui/references/design-acquisition.md:75`
  > `_history/vN` 보존은 규범이 아니다 — 이전 바이트는 커밋된 git 이력이 보존한다.
- 근거: `dddjango-web/scripts/archive_design.py:209` `history_root = build / '_history'` — R4가
  `compare_manifests()`를 지우면 `_history`를 아는 코드가 0이 된다.
- 결과: «규범 아님»인 `_history`가 실재하는데 설계는 세 번째 이름(`_prev-*`)을 들여온다.
  §6 쟁점 1(«완벽하게 삭제»의 위반인가)은 이 맥락 없이 다뤄져 있다.

### m2 B4 시험의 grep 어휘가 실제 잔존물을 못 잡는다
- 근거(설계 §3): «B4 | 잔존 참조 | 정본·미러·테스트에서 `compare-build`·`refreeze-diff` grep 0»
- 근거(실측): A8 `build-state.json`의 실제 키는 `refreeze`가 아니라
  `refreeze_v3`·`refreeze_v4`·`refreeze_v5`다(그 외 비스키마 키 `compact_resume_anchor`·
  `design_input_digest_v5`·`g2_progress`·`g2_complete_pending_orchestrator`도 있다).
- 결과: B4는 `carried`/`carried_from`(M4)도, 실제 런타임이 만든 키 모양도 못 잡는다.
  R4의 «`build-state.refreeze` 키는 사라진다»는 스키마 문장이지 현장 사실이 아니다.

### m3 `_prev-*` 존재 중에는 `legacy_v1_allowed`가 닫힌다
- 근거: `dddjango-web/scripts/backstop.py:112-123` — 빌드 폴더에 untracked/ignored 파일이
  하나라도 있으면 False.
- 결과: 재동결 도중 backstop이 돌면 v1 legacy 통과 경로가 닫힌다. R2가 «어느 경우든 `_prev-*`는
  남지 않는다»로 좁혀두긴 했으나, 설계가 «오염되지 않음»을 확인했다고 적은 두 항목
  (빌드 탐색 · hook 계수)에 이 항목은 빠져 있다.

### m4 R3이 제거하는 `evidence_debt` 키의 «해소» 판정과 R1의 폐기 순서가 맞물리지 않는다
- 근거(설계 R3): «`evidence_debt` **키 제거** — 조작 상태를 새로 수집했으므로 부채가 실제로
  해소된다. hook은 관찰 문서가 v2면 그 폴더를 부채로 세지 않는다.»
- 근거: `evidence_debt.py:121-125` — v2여도 `has_interaction_evidence`의 **정확 필드 집합**
  (`OBSERVATION_V2_FIELDS`, `interactions`는 `{path, sha256}` 정확)을 만족해야 `ok`다.
  하나라도 어긋나면 `malformed`로 다시 부채다.
- 결과: «수집했으니 해소»는 조건부다. 키 제거를 수집 직후에 하면 실제 부채가 남은 채 결정
  기록만 사라질 수 있다. 제거 시점을 `build_debt(...).cases_debt == 0` 확인 뒤로 묶는 문장이 없다.

---

## 확인했으나 문제 없음

- **`_prev-*`의 빌드 탐색 오염 없음** — 설계 R2의 주장 두 개를 코드로 확인했다.
  `backstop.py:65-70`은 `parts[2]`가 marker(`design-ref`·`design-input.json`·`source-manifest.json`·
  `render-audit.json`)일 때만 빌드로 센다 → `.dddjango-web/<빌드>/_prev-*/…`는 `parts[2]='_prev-*'`라
  불발화. `evidence_debt_hook.py:109-114`는 `.dddjango-web` 바로 아래 디렉터리 중
  `design-input.json`이 있는 것만 센다 → 중첩된 `_prev-*`는 무관.
- **`--out`을 `design-ref`로 직접 줘도 되는가(R2-2)** — 맞다. `archive_design.py:157`
  `if {p.relative_to(out)…} != {r['local_path']…}: raise ValueError('output inventory differs; use a fresh output directory')`
  는 **출력 인벤토리 일치**만 요구하므로, `design-ref`를 통째로 치운 뒤 같은 경로로 재실행하면 충족된다.
- **기존 `refreeze-diff.json`·`build-state.refreeze` 잔존은 무해(설계 §R4 하위호환 주장)** —
  `check_design_evidence.validate_inputs`는 선언된 포인터만 읽고 빌드 폴더를 열거하지 않으며
  (archive 인벤토리 대조는 `reference_root`=`design-ref` 안으로 한정 — `:1171-1176`),
  `backstop.project_design_builds:65`의 marker 집합에 `refreeze-diff.json`이 없다.
  build-state.json에 미지 키 금지 검사도 없다. **질문 5의 답: 실제로 무시된다.**
- **`scope.md` 보존이 포인터 체계를 지킨다** — `check_design_evidence.py:1098-1102`가 prepare에서도
  `scope` 포인터(path+sha256)를 해소하므로 보존이 필수이고, 설계는 보존한다.
  `_check_exclusions:850-856`의 `approval_quote` 부분문자열 대조도 `scope.md` 본문 기준이라 유지된다.
- **`design-input.json`은 재생성 시에도 `coverage_review` 키가 있어야 한다** —
  `:1082-1084`의 `required`에 포함되고 이 검사는 `require_review`와 무관하다. 다만 prepare에서는
  포인터 해소를 건너뛰므로(`:1099-1100`), 아직 검토 전이어도 키만 있으면 exit 0이 가능하다.
- **R3의 blocked 복귀 자체는 기존 규범과 정합** — `commands/dddjango-web.md:144`
  > 재기준 승인 직후에도 blocked를 유지하며 새 기준 관찰·독립 범위 재검토·inputs exit 0 뒤에만 ready로 바꾼다.
- **`archive_sha256` 정합** — `check_design_evidence.py:738-744`(비교는 `:742`)가 interactions 문서의
  `archive_sha256`을 **`source-manifest.json` 바이트 sha**와 대조하므로, manifest 재생성 후
  관찰을 수집하는 step 5의 기존 순서를 그대로 따르면 어긋나지 않는다(R2-2의 «정상 경로 그대로»가 이를 담보).

---

## 미확인

- **A8의 2026-09-15 실행 직후 바이트.** 읽은 폴더
  `~/Desktop/spring_dream_server/.dddjango-web/20260912-1640-web-related-persons`는 전 파일 mtime이
  `Sep 13 04:18`로 균일하고 `evidence_debt`가 `null`이다 — 진단이 기록한 «16:27 defer 대리 기록»
  이후 상태가 아닐 수 있다. 따라서 «A8에 실제로 `refreeze-diff.json`·`evidence_debt`가 남아 있는가»는
  확인하지 못했다(현 폴더에는 `refreeze-diff.json` 없음, `refreeze_v3/_v4/_v5` 있음).
  `~/Desktop/kkebi-server`의 `.dddjango-web`에는 A8 폴더 자체가 없다(8월 빌드만 존재).
- **재동결을 실제로 돌린 결과.** 재동결된 폴더가 존재하지 않아 `--phase prepare`·backstop의
  실제 exit를 실행으로 확인하지 못했다. 위 판정은 전부 코드 경로 추적이다.
- **Codex 런타임에서 hook 주입 문구가 실제로 보이는지.** `codex-dddjango-web/hooks` 신뢰 상태에
  의존하며(REQUEST_GUIDE.md:119-121), 이 검토에서 실행하지 않았다.
- **`interaction_exclusions`를 가진 실제 빌드 표본.** `~/Desktop` 이하에서 예외 행이 있는
  `design-input.json`을 찾지 못해, B5의 재작성 비용을 실측으로 가늠하지 못했다.
- **`design-spec.md`의 모션 처분 표 실제 id 집합.** A8 `design-spec.md`(94KB)의 처분 표와
  `motion-notes.md`의 m-id를 대조하지 않았다 — B4는 검사기 로직과 id 규정으로부터의 추론이다.
