# 최종 검토 F — 설계 v3 (2026-09-15)

대상: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(이하 `design:N`)
선행: `rv-A.md`·`rv-B.md`(1차) · `rv-R.md`(v2 재검토) — 여기 적은 것은 그 셋이 적지 않은 것만이다.
도구: 기본 검색·편집만(이 워크트리에 `.serena/project.yml`·`graphify-out/graph.json` 없음 — opt-in 표식 부재로 Serena·Graphify 미사용).
A8 워크트리(`~/.herdr/worktrees/spring_dream_server/a8`)는 **읽기만** 했다(파일 목록·해시·JSON 파싱 — 쓰기 0).

## 판정

**구현 진입 불가** (BLOCKER 2 · MAJOR 7 · MINOR 5)

v3가 고른 두 해법(§3 staging 정본 · §4.6 파일 단위 트랜잭션)은 **검사기 쪽에서는 성립한다** —
네 축(pointer sha · `_check_exclusions` · `scope_ref` 앵커 · `reviewed-input` digest)이 전부
build 상대·내용 주소라 staging에서도 교체 후 live에서도 같은 값을 낸다(§1 아래). 막는 것은
**규범 쪽**이다: ① §4.3의 staging/live 인자 분기를 **런타임에 전달할 문서 위치가 없다**(R10의
편집 목록이 «재동결» grep 12줄로 만들어져 인자 리터럴이 사는 줄을 전부 비껴갔다) ② §1의
«전 구간 ready»가 `commands:144`의 기존 blocked 규정과 정면 충돌하는데 그 줄도 편집 목록 밖이다.

---

## 항목별 결과

### 1. §3 `scope.md` 교체 해법 — **부분 성립**(검사기 ✓ · 쓰기 규율 ✗)

**성립하는 부분(코드 확인).**
- `pointer():65-81`이 `build/<path>` 바이트로 sha를 재계산한다 → staging 복사본 기준으로 쓴
  `design-input.json.scope`는 staging에서 통과하고, 파일이 그대로 live로 **이동**하면 바이트가
  같으므로 교체 후 live에서도 통과한다(`check_design_evidence.py:65-81`).
- `_check_exclusions:857-861`의 `approval_quote` 부분문자열 대조는 `build / scope['path']`를 읽고,
  `:880-894`의 `scope_ref` 앵커는 `confined(build, document)`로 해소한다 — 둘 다 같은 build 인자에
  매달려 있어 staging/live 어느 쪽이든 자기 폴더의 `scope.md`를 본다(`:885`).
- `reviewed-input` digest도 안전하다. `review_digest():199-205`는 `('review-input', spec JSON)` +
  **`(상대경로, 바이트)` 쌍**만 해싱하고 `canonical_digest():87-95`가 이름으로 정렬한다 —
  절대 경로가 들어가는 항목이 하나도 없다. `digest_items`의 `host/*`는 `project` 기준이라
  (`:1238-1247`) staging과 무관하다. 따라서 **staging에서 만든 digest가 교체 후 live에서 그대로
  재현된다** — §4.6 ④ verified가 성립하는 근거다.
- 소비자 전수: 플러그인 정본에서 `scope.md`를 **기계로 읽는 곳은 `check_design_evidence.py`뿐**이다
  (`backstop.py`·`evidence_debt{,_hook}.py`·`check_motion_spec.py`·`freeze_design.py`에 scope 소비 0 —
  `backstop.py:140`의 `current_nondesign_scope`는 동명이인이다). `case.scope_refs`는 `:1209`에서
  **형식만** 보고 앵커를 해소하지 않으므로 교체로 깨지지 않는다. 나머지 참조는 전부 산문(역할 입력
  목록)이라 Coordinator가 경로를 넘기는 구조다 — 교체 자체로 깨지는 소비자는 **없다**.
- «실패 후 abort하면 live `scope.md`가 원본 그대로»는 **참이다**(begin은 복사만·쓰기는 staging).
  단 아래 M-3의 조건이 붙는다.

**불성립하는 부분** → M-3(쓰기 주체 열거 누락·live 쓰기 미금지).

### 2. §4.6 `commit` 트랜잭션 — **불성립**

멱등 규칙(`design:164` «이미 옮긴 파일은 건너뛴다»)이 파일 이동의 네 경우 중 **두 경우에서 틀린다**
→ M-7(both-present 충돌로 인한 영구 livelock)·m-4(both-missing 무성 손실). 되감기 자체는
`swap-plan.json`에 설치 목록이 있으면 성립하고(§4.6 ①이 그것을 적는다), `build-state.json`을
done까지 안 고치는 것도 맞다 — 그러나 `done`이 `_prev`를 지운 뒤의 잔존 창에서 R9 배너가 권하는
`abort`가 **성공한 재동결의 신규 이미지를 지운다** → M-4.

### 3. 아직 확인되지 않았던 두 전제

**ⓐ 렌더 실측 — §4.3 표의 «도구» 행은 거짓이다(단 staging 기록 자체는 가능).**
`dddjango-web/assets/render_audit.js`는 **인자가 없는 브라우저 콘솔 스니펫**이다 — 출력은
클립보드(`copy`)·`console.log`·`window.__renderAudit` 세 곳뿐이고(`render_audit.js:14-19`)
파일을 쓰지 않는다. 동결 주체는 Coordinator다: `commands/dddjango-web.md:142` ③
> ③ `<산출물 폴더>/render-audit.json`으로 동결하고 **즉시 … `compare_render_audit.py --validate --require-version 2 <산출물 폴더>/render-audit.json`으로 파싱·스키마를 검증한다**

즉 §4.3의 «렌더 실측 | `<staging>/render-audit.json`» 행은 **도구 인자가 아니라 Coordinator의
쓰기 경로**다. 그래서 staging 기록은 «가능»하지만 그 가능성은 전적으로 `commands:142`의 리터럴을
고치는 데 달려 있는데 **`:142`는 R10의 편집 목록에 없다** → B-1의 한 사례.
덧붙여 이 절차는 «① 스니펫을 사용자에게 제시 → ② 사용자가 붙여넣고 JSON을 파일로 저장 → ③ 동결»
이라는 **사용자 왕복**이다(대행은 브라우저 채널이 있을 때만). §4.3 표는 이것을 다른 CLI 도구와
같은 행에 두어 자동 재수집처럼 보이게 한다 → M-5(deadlock).

**ⓑ `observe_interactions.pw.js` — 성립. `capturesDir`·`out` 밖에 쓰는 경로는 0이다.**
파일 전체(1985행)의 `fs.*` 호출은 **정확히 4개**다: `:96 existsSync`(스니펫 실재) ·
`:164 readFileSync`(`--resume`의 `ctx.out` 읽기) · `:543 mkdirSync(ctx.capturesDir)` ·
`:547 writeFileSync(file)`(캡처) · `:1936-1937 mkdirSync(dirname(ctx.out)) + writeFileSync(ctx.out)`.
`--resume`은 `loadPrior():161-164`가 **`ctx.out`만** 읽고 어떤 중간 파일도 만들지 않는다.
Playwright 아티팩트 옵션도 없다 — `launch`/`newContext`는 래퍼(`scripts/observe_interactions.mjs:135,142-143`)에
있고 `recordVideo`·`recordHar`·`tracing`·`downloadsPath`·`userDataDir` 지정이 **전무**하다
(`chromium.launch({channel, headless:true})` · `newContext({viewport, reducedMotion})`).
→ §4.3·§5의 롤백 범위에 이 축의 구멍은 **없다**.

### 4. v3가 새로 만든 모순

ⓒ `commands:144` = **B-2**(BLOCKER) · ⓑ `evidence_debt` = **M-6** · ⓐ = **m-5**.

---

## BLOCKER

### B-1 §4.3의 staging/live 인자 분기를 **런타임에 전달할 문서가 없다** — R10/T5의 편집 목록이 구조적으로 그 줄들을 비껴간다

- R10(`design:231`)은 `commands` 편집 대상을 «재동결 출현 12곳 전수: `9 70 129 130 134 137 146 154 171 205 227 234`»로
  못 박고, §9 T5도 «commands 12곳»이다. 실측 대조: `grep -n '재동결\|refreeze' commands/dddjango-web.md`의
  행 집합은 **정확히 그 12개**다(재확인). 즉 이 목록은 «재동결»이라는 **어휘**로 만들어졌다.
- 그런데 재수집 인자 리터럴이 사는 줄은 전부 그 밖이다:
  - `commands:138` — `extract_design.py --from-ds-manifest … --out <산출물 폴더>/…`
  - `commands:140` — `freeze_design.py <출처> --out <산출물 폴더>/design-ref --manifest <산출물 폴더>/source-manifest.json`,
    `extract_design.py <동결 HTML> --out <산출물 폴더>/design-tokens.json`,
    `fetch_images.py <산출물 폴더>/design-ref --source-manifest <산출물 폴더>/source-manifest.json --assets-root <프로젝트 루트> --asset-base <산출물 폴더>/design-ref --out <산출물 폴더>/asset-manifest.json`
  - `commands:142` — 렌더 실측 ③ `<산출물 폴더>/render-audit.json`
  - `commands:143` — `observe_interactions.mjs … --out <산출물 폴더>/captures/<screen>-interactions.json`(+`--declared`·`--excluded-regions`)
  - `commands:145` — «기존 `--out <산출물 폴더>/design-ref --manifest <산출물 폴더>/source-manifest.json` **관례를 유지한다**»
  `<산출물 폴더>`는 `commands:24`·`:129`가 정의한 **live 빌드 폴더**다. staging은 `<BUILD>/_refreeze-*`로
  그것과 다른 경로다.
- 파급: v3를 R10 목록 그대로 집행하면 **규범은 여전히 재수집 전량을 live에 쓰라고 지시한다.**
  §4.3 표는 설계 문서에만 있고 설계 문서는 런타임 아티팩트가 아니다 — Coordinator는 `commands`와
  `design-acquisition.md`만 읽는다. v3의 구조 역전 전체가 런타임에서 발화하지 않는다.
- 같은 이유로 `references/design-acquisition.md`도 §2(재동결 절)만 재작성 대상인데(`design:232`),
  조작 상태 수집 인자 절차는 **§3**에 있다(`design-acquisition.md:113-125` — `--out BUILD/captures/…`
  `--captures-dir BUILD/captures`가 `BUILD` 리터럴로 고정).

### B-2 §1의 «전 구간 `ready` 유지»가 `commands:144`의 기존 규정과 충돌하고, `:144`는 편집 목록 밖이다

- `commands/dddjango-web.md:144`:
  > 사용자가 구체적인 범위/출처 재기준을 승인하면 … **새 기준을 실제 수집·동결하고 현재 design-input의 entrypoint·manifests·scope_refs·원본 capture를 그 기준에 연결한다.** … **재기준 승인 직후에도 blocked를 유지하며 새 기준 관찰·독립 범위 재검토·inputs exit 0 뒤에만 ready로 바꾼다.**
- 재동결은 이 문장이 서술하는 행위와 **같은 행위**다 — 새 기준을 전량 수집·동결하고 design-input의
  entrypoint·manifests·scope_refs·원본 capture를 새 기준에 다시 잇는다(`design:29-31`·§2).
  그런데 `design:36-38`은 «`design_status`는 전 구간 `ready`를 유지한다»로 정반대를 성문화한다.
- `:144`에는 «재동결»도 «refreeze»도 없다 → R10의 12줄에 포함되지 않는다(위 B-1의 실측과 동일).
  결과: 구현 후 두 규범이 같은 파일 안에 공존하고, `:144`를 따르는 Coordinator가 `blocked`를 쓰면
  §1이 막으려던 침묵(`evidence_debt.py:139` `state.get('design_status') != 'ready': return None`)이
  그대로 발생한다. v3는 rv-A M3를 «§1에서 원인 제거»로 닫았다고 적었으나(`design:318`),
  원인은 제거되지 않고 **모순으로 바뀌었다**.

---

## MAJOR

### M-1 `captures/`는 2분류가 아니다 — A8 실측으로 «S에도 visual-evidence에도 없는» 제3집합이 존재한다

`design:42-46`은 `captures/`를 «원본 증거 ∪ 구현 증거»로 보고 «두 집합이 서로소임은 규범이
보장한다»고 적는다. A8 9개 빌드를 읽기 전용으로 실측한 결과(3겹 S와 `visual-evidence.json`
포인터를 실제로 해소해 차집합을 셌다):

| 빌드 | captures 파일 | 3겹 S | visual-evidence | **둘 다 아닌 것** |
|---|---|---|---|---|
| 20260912-1640-web-related-persons(A8 표적) | 55 | 36 | 13 | **7** |
| 20260908-0143-web-chat-spine | 318 | 36 | 13 | **270** |
| 20260908-0055-web-settings | 83 | 15 | 10 | **59** |
| 20260907-2249-home-bottom-nav | 70 | 30 | 11 | **30** |
| 나머지 5개 | — | — | — | 0·6·11·17 |

표적 빌드의 7건은 `captures/related-1440x900-01-list-impl.png` 류(구현 캡처인데
`visual-evidence.json`이 가리키지 않음)와 `captures/smoke-*-impl.png`다. home-bottom-nav의 30건은
`captures/attempt-1/*-original.png`·`*-source-observation.json`(실패 회차의 **원본** 증거)과
`captures/external/*.css|woff2`다.
- 파급 ①: §2의 보존 규칙(«S에 없는 `captures/*`»)이 이들을 전부 **보존**으로 보낸다 →
  사용자 정의(«완벽하게 삭제하고 다시 동결»)가 표적 빌드에서 55분의 7만큼 거짓이고,
  §8 «남는 우회»는 `web/static/images/` 고아만 고지한다(우회 2) — `captures/` 고아는 미고지다.
- 파급 ②: §2의 «두 집합이 서로소»의 근거로 든 `check_design_evidence.py:1310-1314`는
  **`visual-evidence.json`이 가리키는 캡처에만** 걸린다. 위 제3집합은 그 보장 밖이다.
- 파급 ③: M-7의 이름 충돌이 실재할 수 있는 전제가 바로 이 집합이다.

### M-2 (B-1 파생) `has_render_audit`가 true인 빌드는 `check`를 통과하지 못할 수 있고, 내릴 경로가 없다

- §4.4는 `has_render_audit`을 **live `build-state.json`**에서 읽고(`design:136-137`), true면 staging에
  `render-audit.json` 실재를 요구한다. §2는 `render-audit.json`을 고정 폐기·교체 대상으로 둔다.
- 그런데 재측정의 합법적 생략 사유는 enum이다 — `commands:142`
  > **실측 생략이 합법인 사유는 enum이다** — 원본 열람 불가 · 필요한 인증 상태 접근 불가 · 브라우저 채널 부재(사용자도 실측 불가). … 생략이 확정되면 **파일을 만들지 않고**(스텁 금지 …)
- 재동결 시점에 원본 URL이 사라졌거나 인증이 막혔으면 재측정이 합법적으로 불가능한데,
  live build-state는 여전히 `has_render_audit: true`다 → `check`는 영원히 exit 3.
  R7의 상태 전이표에 `has_render_audit`이 **없어** 내릴 근거도 없다. 표적 빌드는 실제로
  `render-audit.json`을 갖고 있다(A8 실측) — 즉 B1 시나리오가 바로 이 경로를 탄다.

### M-3 §3의 `scope.md` 쓰기 주체 열거가 불완전하고, staging 창 동안 live 쓰기를 금지하는 문장이 없다

- §3은 재수집 중 `scope.md` 쓰기를 «`commands:143`의 실행 경계 + R6의 새 승인 원문» **둘**로 본다.
  실제로는 세 번째가 있다 — `commands:142` 렌더 실측 ④ «생략이 확정되면 … 사유를 **scope.md에 1줄
  기록**하며 G0 배너에 표면화한다». 이것도 재수집 구간에서 발생한다.
- 더 중요한 것은 **금지 문장의 부재**다. §3은 «staging 복사본에만 기록한다»고 쓰기 대상만 지정하고,
  staging 창(A8 기준 수십 분 + 보완 루프) 동안 live `scope.md`에 쓰지 말라고 **금지하지 않는다**.
  `commit`은 staging 복사본을 live로 **덮어쓴다** → 그 창에 live에 적힌 줄은 **red 없이 증발한다**
  (sha는 staging 기준이라 일치하므로 검사기가 못 본다). rv-R RB1의 ⓐ(red)보다 나쁜 **무성 손실**이다.
- §3의 «승인 이력은 append-only라 교체로도 내용은 보존된다»(`design:81`)는 이 금지가 성문화돼야만 참이다.
  `commands:142`도 R10 편집 목록 밖이라 현재 규범은 live에 쓰라고 지시한다.

### M-4 `done`이 `_prev`를 지운 뒤의 창에서 R9 배너가 권하는 `abort`가 **성공한 재동결을 파괴**한다

- §4.6 ⑤ «`build-state.json` 키 갱신 → `_prev-<ts>`·staging 삭제» — 둘의 삭제 **순서가 없고**,
  `swap-plan.json`은 `_prev-<ts>/` 안에 산다(`design:150-151`).
- `_prev`가 먼저 지워지고 staging이 남은 상태에서 세션이 죽으면: R9가
  «`_refreeze-*` … run `refreeze.py commit --resume` or `abort`»를 낸다(`design:215-217`).
  `--resume`은 읽을 계획이 없어 진행 불가, `abort`는 계획이 없으니 «교체 중 아님»으로 판정해
  §4.1대로 «staging·신규 이미지 제거»를 수행한다 → **방금 설치한 `web/static/images/`의 신규
  이미지를 `journal.images_before` 차집합으로 지운다**(`design:178-179`). 그 이미지는 이미 live
  `asset-manifest.json`과 템플릿이 참조하는 자산이다.
- §4.1의 `abort` 설명에 **phase 가드가 없다**(«교체 중이면 되감기»의 판정 근거가 사라진 상태).
  R9 배너는 두 선택지를 동격으로 제시하는데 이 창에서는 하나는 불가·하나는 파괴적이다.

### M-5 `verified` 실패 경로가 이미지 축을 되감지 않는다

- §4.6 ④ «실패면 계획을 역순으로 되감아 `_prev-<ts>`를 복원하고 exit 1». 계획은 빌드 폴더의
  파일 이동만 담는다(§4.6 ①) — `fetch_images.py`가 `<ROOT>/web/static/images/`에 쓴 신규 바이트는
  계획 밖이다(§5가 그 사실을 인정한다).
- 따라서 되감기 직후의 상태는 «빌드 폴더는 원상 · 구현 트리는 오염»이고, 그 즉시 완료 빌드의
  `implementation_digest`가 stale이라 backstop이 `[DESIGN] BLOCKER`를 낸다
  (`check_design_evidence.py:1263-1281`·`validate_visual`).
- §5는 «실패 시 `abort`는 의무»라고 격상했지만 §4.6 ④는 exit 1로 끝나고 abort를 **요구하지 않는다**.
  둘을 잇는 문장이 없다.

### M-6 `evidence_debt` 키를 **쓰는** 주체가 없다 — rv-R RM2와 같은 형태의 빈칸이 다른 키에서 반복된다

- R8(`design:208`)은 «사용자가 재동결을 요청하면 그 발화가 곧 ⓐ 결정의 `quote`다 — **대리 기록이
  사라진다**»로 기록을 없앤다. R7은 `done`에서의 **제거**만 규정한다. 즉 4 서브커맨드 중 아무도
  `evidence_debt`를 쓰지 않는다.
- 코드: `BuildDebt.status:49-57`는 `cases_debt>0 ∧ decision is None`이면 `'undecided'`,
  `evidence_debt_hook.py:127-132`가 그때마다
  «… decision required before any run on this folder»를 낸다. 부채가 있는 빌드(=R8이 대상으로 삼는
  바로 그 빌드)를 재동결하는 동안 live design-input은 **옛 static-only 그대로**이므로
  `cases_debt>0`이 유지되고, §1이 `ready`를 유지하기로 했으므로 폴더는 판정 대상에 계속 남아
  **매 프롬프트마다** 그 배너가 뜬다 — 진행 중인 재동결을 금지하는 문구로.
- 기존 키가 `defer`인 빌드를 재동결할 때 그 키를 `observe`로 바꾸는지도 미규정이다. R8은 defer가
  허용하는 것에서 재동결을 뺐으므로, 키가 `defer`로 남으면 «허용되지 않는 작업을 수행 중인데
  hook은 `deferred since …`만 출력»하는 상태가 된다. R11의 그물은 문서 4곳 grep이라 이 축을 못 본다.
- 부연: R7의 «`build_debt()`는 `design_status=='ready'`를 요구하므로 **이 순서에서만 호출 가능**»
  (`design:197`)은 v2의 blocked→ready 승격을 전제한 문장이다. §1이 ready를 상수로 만든 v3에서는
  순서 제약 자체가 사라졌으므로 근거가 공문구다.

### M-7 `installed` 단계의 멱등 규칙이 이름 충돌에서 틀리고, 그 결과가 **영구 livelock**이다

- `design:164` «각 단계는 멱등이다 — **이미 옮긴 파일은 건너뛴다**». 이동의 네 경우 중 규정된 것은
  둘(src만 있음 → 이동 · dst만 있음 → 건너뜀)이고 나머지 둘이 열려 있다.
- **src·dst가 둘 다 있는 경우**가 `installed`에서 실재할 수 있다. 조건은 «staging이 만드는 이름 ∈
  (live 파일 − S)»인데, 그 차집합이 비어 있지 않다는 것이 M-1의 실측이다(표적 빌드 7건·다른 빌드
  최대 270건). 드라이버가 만드는 이름은 `--out`의 screen 이름에서 결정론으로 파생되므로
  (`observe_interactions.pw.js:115,543-548` — `captures/<screen>-initial.png`·`<screen>-step-N.png`)
  옛 회차의 미참조 캡처와 같은 이름이 나올 수 있다.
- 그때 «건너뛴다»를 따르면 **옛 바이트가 live에 남고 새 산출물이 조용히 버려진다**. 이어지는
  ④ verified가 `pointer(): sha256 mismatch`로 잡아내(`check_design_evidence.py:74-75`) 되감고 exit 1 →
  `commit --resume`은 같은 계획·같은 규칙이라 **같은 지점에서 같은 실패를 반복한다**. 설계에는
  이 상태를 벗어날 경로가 없다(`abort` 후 전량 재수집만 남는데 §8 우회 3대로 수십 분이다).
- 올바른 규칙은 `installed`에서 **덮어쓰기**(또는 충돌을 오류로 승격)인데 §4.6은 단일 문장으로
  두 단계에 같은 «건너뛴다»를 적용한다.

---

## MINOR

- **m-1 §4.2 journal 예시가 실재하지 않는 파일을 든다.** `copied_inputs: ["scope.md",
  "related-declared.json", …]`(`design:109`)의 `related-declared.json`은 A8 표적 빌드에 없다 —
  `find ~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web -name '*declared*' -o -name '*excluded*'
  -o -name '*hover-selectors*'` 결과 **0건**(9개 빌드 전체). §4.3의 «begin이 입력을 복사하므로
  staging이 자족한다»는 표적 빌드에서 복사할 것이 `scope.md` 하나뿐이라는 뜻이고, 그 결과
  rv-A M6/rv-R RM3가 막으려던 «매 재동결마다 소스 검토부터 다시»가 A8에서는 그대로 발생한다.
- **m-2 §2의 폐기/보존 열거가 표적 빌드의 실제 인벤토리를 덮지 못한다.** 표적 빌드에 실재하는
  `design-review.md` · `render-audit-impl.json` · `refreeze-diff.json`이 양쪽 표 어디에도 없다.
  기본값이 보존이므로 `refreeze-diff.json`은 R10이 생성 도구를 지운 뒤에도 **고아 산출물로 남고**,
  `render-audit-impl.json`은 새 `render-audit.json`과 짝이 맞지 않는 옛 구현 실측으로 남는다
  (R7의 `implementation_visual=pending`이 재대조를 강제하므로 피해는 낮다).
- **m-3 §4.2와 §4.6이 서로 다른 granularity를 쓴다.** §4.6은 «디렉터리 이동을 **금지**한다»로
  시작하는데(`design:150`) §4.2의 `discard_set` 예시는 `"design-ref"`라는 **디렉터리 항목**을 담는다
  (`design:106`). 구현자가 어느 쪽을 집행할지 문서가 고르지 않는다.
- **m-4 멱등 규칙이 «원본도 대상도 없는» 경우를 규정하지 않는다.** `discarded` 재개 중 `src`와
  `_prev/dst`가 둘 다 없으면 «이미 옮김»과 «유실»이 구별되지 않는데 `design:164`는 무조건 건너뛴다.
  건너뛴 항목은 `_prev`에 없으므로 이후 되감기가 **불완전한 live**를 복원하고 아무 신호도 내지 않는다.
- **m-5 §1의 근거 문장이 §5가 철회한 전제를 다시 쓴다.** `design:36-37` «staging 창 동안 live는
  여전히 **유효한 동결물**을 갖고 있으므로 [design_status를] 내릴 근거가 없고» ↔ §5는 재수집이
  `web/static/images/`에 쓰는 순간 그 빌드의 `implementation_digest`가 stale이 되어 backstop이
  red를 낸다고 인정한다(`design:175-177`). ready 유지 결론 자체는 다른 근거(부채 hook 가시성)로도
  서므로 판정은 바뀌지 않지만, 제시된 근거는 참이 아니다.

---

## 확인했으나 문제 없음

- **staging→live 이동이 digest를 흔들지 않는다** — `canonical_digest():87-95`와
  `review_digest():199-205`는 (상대 경로, 바이트) 쌍만 해싱한다. 절대 경로가 들어가는 유일한 곳은
  `source-manifest.json`의 `source_root`/`files[].source`인데(`archive_design.py:134,153`) 둘 다
  **EXPORT 원본**을 가리키고 `--out`과 무관하다. manifest 파일 자체는 통째로 이동하므로 바이트
  동일 → `manifest/<path>` 항목도 불변.
- **`--phase inputs`는 아무것도 쓰지 않는다** — `run():1400-1419`는 검사 후 dict를 반환할 뿐이고
  파일 쓰기가 없다. §4.6 ④ verified가 상태를 오염시키지 않는다.
- **R9의 backstop 감지는 구현 가능하다** — `project_design_builds():59`가
  `folder.rglob('*')`로 **파일시스템 전수**를 먼저 담고 거기에 git 이름을 더한다. untracked인
  `_refreeze-*`·`_prev-*`도 `names`에 들어오므로 git 인덱스에 없어도 잡을 수 있다.
  (같은 코드가 `parts[2] ∈ markers`만 빌드로 세므로 staging이 빌드로 오인되지 않는다는 rv-R의
  결론도 재확인.)
- **commit 창의 침묵은 backstop이 실제로 깬다** — `discarded` 상태의 live에는 `build-state.json`이
  남아 `has_design_screen: true`로 빌드가 계속 discovered되고(`backstop.py:72-77`),
  `validate_inputs`가 `design-input.json: unreadable`로 즉시 defect를 낸다.
- **`design-input.json.scope.path` = `scope.md`이고 현재 sha가 실제 바이트와 일치한다**(A8 표적 빌드
  실측: `11d2c382…c0d8` 일치) — §3이 상정한 출발 상태가 실재한다.

## 미확인

- **`refreeze.py`의 실제 거동** — 아직 없는 스크립트다. §4.6의 모든 판정은 설계 문장과 기존 코드
  경로 추적이다.
- **A8에서 재동결을 실제로 돌린 결과** — 실행하지 않았다(읽기 전용). M-1의 수치는 현재 바이트의
  정적 집계이고, 재수집이 만들 **새 파일 이름 집합**은 드라이버를 돌려야 확정된다 — 따라서 M-7의
  충돌이 표적 빌드에서 실제로 발화하는지는 미확인(발화 조건만 확인).
- **Codex 미러(`codex-dddjango-web/`)의 대응 행 번호** — R10이 제시한 Codex 목록을 재검증하지 않았다
  (rv-R가 일치 확인한 12행 대응은 그대로 인용).
- **`_history/`의 내용** — 표적 빌드에 실재하나(§8 우회 6이 «손대지 않는다»로 둠) 열지 않았다.
