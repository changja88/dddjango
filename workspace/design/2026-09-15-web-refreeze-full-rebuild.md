# 설계 v3 — 재동결 = 전량 폐기 후 재동결 (2026-09-15)

진단: `workspace/eval/web-refreeze-completeness/diagnosis.md` (커밋 `10faaff2`)
적대 검토: `design-review/rv-A.md`(규범 정합 · B5·M6·m4) · `rv-B.md`(실행·안전 · B4·M2·N3) ·
`rv-R.md`(v2 재검토 · 신규 B2·M5·m6·미해소 1) — 누적 반영 대조는 §7.
선행 수리: 증거 부채 hook(v1.1.14) · `workspace/design/2026-09-15-web-evidence-debt-hook.md`

> **판형 이력**
> v1 «기존 동결물 선폐기 → 재수집 → prepare exit 0» → BLOCKER 9.
> v2 «staging 우선 → 원자 교체»로 역전 → 구조는 코드로 성립 확인(rv-R §A), 그러나 교체 단계와
> `scope.md` 취급이 미명세 → 신규 BLOCKER 2.
> **v3은 교체를 파일 단위 재개 가능 트랜잭션으로 명세하고, `scope.md`를 교체 대상으로 확정한다.**

## 0. 목표와 비목표

**목표** — 사용자 확정 정의를 규범으로 만든다:

> «차이점을 알 필요도 없어. 재동결은 기존에 동결한 파일을 **완벽하게 삭제하고 다시 동결**하는 걸로 해» (2026-09-15)

**비목표**
- 축별 차이 보고(`refreeze-diff.json`)·조작 상태 대조기 — 만들지 않는다(사용자 기각).
- 보더 잘림(수리 2·3) — 별건·후순위.
- 백엔드 계약(`openapi-full.json`·`server-contract`) 재동결 — 별도 축(rv-A M5).
- `motion-notes.md` 재기록 — m-id 전수성 때문에 범위 밖(§5 우회 4).
- 고아 이미지 청소 — 범위 밖(§5 우회 2).

## 1. 정의

**재동결** = ① staging에 시안 동결물 **전량**을 처음부터 새로 만든다 → ② 완전성·입력 게이트를
staging에서 통과시킨다 → ③ 기존 동결물을 통째로 지우고 staging 산출물로 **교체**한다 →
④ 교체 후 live에서 `--phase inputs` exit 0을 재확인한다.

- 사용자가 요청했을 때만 실행하고(자동 staleness 감지 없음), **요청이 있으면 항상 전량 재실행한다** —
  직전 결과 재사용·«이번 세션에 이미 했음»으로 생략하지 않는다(G-B).
- **재동결의 끝 = ④**(rv-R m-5). ③ 없이 끝내지 않는다.
- **`design_status`는 전 구간 `ready`를 유지한다.** staging 창 동안 live는 여전히 유효한 동결물을
  갖고 있으므로 내릴 근거가 없고, 내리면 부채 hook이 그 폴더를 판정 대상에서 지운다
  (`evidence_debt.py:139-140` — rv-A M3·rv-R RM2).

## 2. 폐기 집합과 보존 (R1)

`captures/`에는 원본 증거와 **구현 증거가 함께 산다**(A8 실측: `*-original.png` 11 ·
`*-impl.png` 16 · 관찰/trace 24). 접미 관례는 성문화돼 있지 않으므로 파일명으로 가르지 않는다.
두 집합이 서로소임은 규범이 보장한다 — `check_design_evidence.py:1310-1314`가 구현 캡처의
원본 재사용(하드링크 포함)을 금지한다.

**폐기 집합 S** — `design-input.json`에서 **3겹**으로 순회한다(rv-R RM1):

| 겹 | 포인터 |
|---|---|
| 1 | case의 `reference_capture.path` · `source_observation.path` |
| 2 | 위 관찰 문서 안의 `capture.path` · `trace.path` · (v2면) `interactions.path` |
| 3 | 위 interactions 문서 안의 `initial.capture.path` · `steps[].after.capture.path` |

**고정 폐기·교체 대상**: `design-ref/**` · `source-manifest.json` · `design-tokens.json` ·
`asset-manifest.json` · `screen-meta.json` · `render-audit.json` · `design-input.json` ·
`coverage-review.md` · **`scope.md`**(R2 참조) · **`<screen>-declared.json`과 `--excluded-regions`
입력 파일**(R3 참조).

**보존**: `build-state.json`(키만 갱신) · `design-spec.md` · `visual-check.md`(절 갱신) ·
`visual-evidence.json`과 그것이 가리키는 `captures/*` · `motion-notes.md` ·
`openapi-full.json`·`server-contract*`·`contract-paths.txt` · S에 없는 `captures/*`.

## 3. `scope.md`는 교체 대상이다 (rv-R RB1)

규범은 재수집 도중 `scope.md`에 **쓰기를 요구**한다 — `commands:143`의 실행 경계 기록(Playwright
모듈 경로·버전·`--declared` 사용 여부)과 예외 행의 새 승인 원문(R6). 동시에 `commands:129`가
«scope 바이트가 바뀌면 `design-input.json.scope` 포인터·review digest가 어긋난다»를 성문화한다.
live에 쓰면 교체 후 sha 불일치, staging에만 쓰면 기록 증발 — 그래서 **staging을 정본으로 삼고
교체한다**:

1. `begin`이 live `scope.md`를 staging에 복사한다.
2. 재수집 중 실행 경계·새 승인 원문은 **staging 복사본에만** 기록한다(append).
3. `commit`이 staging `scope.md`를 live로 옮긴다 — `design-input.json.scope`의 sha가 staging
   기준으로 만들어졌으므로 교체 후에도 일치한다.
4. **순서 규정**: 독립 검토(`coverage-review.md`)는 `scope.md` 최종 확정 **뒤에** 받는다.
   `coverage_review`의 `reviewed-input` digest가 scope 바이트를 포함하므로
   (`check_design_evidence.py:1250-1258`), 순서를 어기면 inputs가 스스로 red를 낸다 —
   규범 문장 1줄로 명시하고 기계 강제는 기존 검사기에 맡긴다.

승인 이력은 append-only라 교체로도 내용은 보존된다. 재동결 실패 시 live `scope.md`는 원본 그대로다.

## 4. 실행 — `refreeze.py` (R2)

파괴적 구간을 산문 규율에 맡기면 새는 것이 이번 진단의 원인이다. 신설 스크립트
`dddjango-web/scripts/refreeze.py`(Codex byte 미러)가 집행한다.

### 4.1 서브커맨드

| 명령 | 인자 | 하는 일 | exit |
|---|---|---|---|
| `begin` | `--build <BUILD>` `--project-root <ROOT>` | staging 생성 · 입력 복사 · S 계산 · journal 기록 | 0 성공 · 2 선점(기존 staging/`_prev` 존재) · 1 오류 |
| `check` | `--build <BUILD>` `[--staging <경로>]` | staging 완전성 검사 | 0 완전 · 3 미완(누락 목록 출력) · 1 오류 |
| `commit` | `--build <BUILD>` `[--staging <경로>]` `[--resume]` | 파일 단위 교체 트랜잭션 | 0 완료 · 3 중단(재개 필요) · 1 오류 |
| `abort` | `--build <BUILD>` `[--staging <경로>]` | staging·신규 이미지 제거, 교체 중이면 되감기 | 0 완료 · 1 오류 |

- `--staging` 생략 시 `<BUILD>/_refreeze-*`가 **정확히 하나**일 때만 자동 선택하고, 둘 이상이면
  exit 1로 목록을 출력한다(rv-R D-1).
- `begin`은 기존 `_refreeze-*`/`_prev-*`를 **삭제하지 않는다** — exit 2로 거부하고 `commit --resume`
  또는 `abort`를 안내한다(rv-R D-2).

### 4.2 journal (`<staging>/journal.json`)

```json
{"version": 1, "build": "<abs>", "project_root": "<abs>", "started_at": "<ISO8601>",
 "discard_set": ["captures/…png", "design-ref", "design-input.json", "…"],
 "images_before": ["web/static/images/<name>", "…"],
 "interaction_exclusions": [ … 기존 행 원문 … ],
 "copied_inputs": ["scope.md", "related-declared.json", "…"]}
```

`discard_set`은 `begin` 시점의 live `design-input.json`에서 계산한 S다 — **commit 재개가 live
design-input에 의존하지 않게 한다**(rv-R RB2). v2의 `build_state_design_keys`는 쓰는 주체가 없어
삭제한다(rv-R D-4).

### 4.3 재수집 — staging/live 인자 분기 (rv-R D-6·RM3)

| 도구 | staging으로 | live 고정 |
|---|---|---|
| `archive_design.py` | `--out <staging>/design-ref` · `--manifest <staging>/source-manifest.json` | — |
| `extract_design.py`·`extract_dc.py`·`fetch_images.py` | `--out`·`--asset-manifest`·`--meta`·`--tokens`·`--asset-base <staging>/design-ref` | **`--assets-root <ROOT>`**(이미지는 구현 트리에 쓴다 — R5) |
| `observe_interactions.mjs` | `--out <staging>/captures/…` · `--captures-dir <staging>/captures` · `--declared <staging>/<screen>-declared.json` · `--excluded-regions <staging>/…` | — |
| 렌더 실측 | `<staging>/render-audit.json` | — |

`begin`이 `scope.md`·`<screen>-declared.json`·`--excluded-regions` 입력을 staging에 복사하므로
staging은 «산출물 폴더»로서 자족한다. 이 입력들은 보완 중 갱신될 수 있으므로 **교체 대상**이다.

관찰 문서의 캡처 포인터는 `capturesDir`의 부모를 build로 보는 **상대 경로**라
(`assets/observe_interactions.pw.js:99,115,548`) 교체 후 live에서도 그대로 유효하다(rv-R A-2).

### 4.4 `check` — `--phase prepare`가 보지 않는 축을 본다

`check_design_evidence.py`에는 `render-audit`·`design-tokens`·`asset-manifest` 문자열이 0건이고
`screen-meta.json`은 선택적이다(rv-B B2). `check`는 staging에서 다음 **실재**를 확인한다:
`design-ref/` · `source-manifest.json` · `design-tokens.json` · `asset-manifest.json` ·
`screen-meta.json` · `design-input.json` · `render-audit.json`(live `build-state.json`의
`has_render_audit`이 true일 때 — `check`는 build-state를 **live에서** 읽는다, rv-R D-5) +
`design-input.json`의 모든 case 포인터 3겹 해소 + archive 원본이면 case마다 v2 관찰 실재.
내용 검증은 하지 않는다(수용된 한계).

### 4.5 입력 게이트 — staging에서 보완 루프를 돈다

`check` exit 0 뒤 staging을 대상으로 `check_design_evidence.py --build <staging>
--project-root <ROOT> --phase prepare` → 독립 검토 → `--phase inputs` exit 0.
**prepare exit 2는 실패가 아니라 `commands:143`의 보완 루프 진입**이다(rv-A B2). live 빌드
폴더가 무손상이므로 몇 번이든 반복할 수 있다.

### 4.6 `commit` — 파일 단위 재개 가능 트랜잭션 (rv-R RB2)

`captures/`가 혼재 디렉터리이므로 **디렉터리 이동을 금지**한다. `commit`은 `<BUILD>/_prev-<ts>/`에
`swap-plan.json`을 먼저 쓰고 단계별로 진행한다:

```
phase: planned → discarded → installed → verified → done
```

1. **planned** — journal의 `discard_set`과 staging 산출물 목록으로 계획을 쓴다.
2. **discarded** — S의 **각 파일**을 `_prev-<ts>/`로 이동한다(경로 구조 보존).
3. **installed** — staging 산출물을 **각 파일** live 경로로 이동한다(`captures/`는 병합).
4. **verified** — `check_design_evidence.py --build <BUILD> --phase inputs` exit 0을 확인한다.
   실패면 계획을 역순으로 되감아 `_prev-<ts>`를 복원하고 exit 1.
5. **done** — `build-state.json` 키 갱신(R7) → `_prev-<ts>`·staging 삭제.

각 단계는 멱등이다 — 이미 옮긴 파일은 건너뛴다. 중단 후 `commit --resume`이 `swap-plan.json`의
`phase`에서 이어가고, `abort`는 같은 계획으로 되감는다. **`abort`가 «복원할 것이 없다»고 말할 수
있는 것은 phase가 `planned` 이전일 때뿐이다**(v2 문장 정정).

## 5. 이미지 축 — 재동결은 구현 트리에 쓴다 (R5 · rv-B B1)

`fetch_images.py:35,110`이 `<ROOT>/web/static/images/`에 내용 해시 파일명으로 바이트를 쓴다.

- 소스명이 있는 이미지는 멱등이지만 **인라인(`data:`) 이미지는 아니다** — 토큰이
  `f"{doc_slug}_{n}"`이고 `n`이 문서 내 순번이라, 이미지가 하나 추가·삭제되면 이후 토큰이 밀려
  같은 바이트가 새 파일명으로 떨어진다(rv-R m-1).
- 따라서 «live 무손상»은 **빌드 폴더에 한한다**. `web/static/images/`는 재수집이 파일을 추가할 수
  있고, 그 순간 완료 빌드의 `implementation_digest`가 stale이 되어 다른 작업의 backstop이
  `[DESIGN] BLOCKER`를 낸다(`check_design_evidence.py:1263-1276` — rv-R RM4).
- 그러므로 **실패 시 `abort`는 선택이 아니라 의무**다. `abort`는 `journal.images_before` 차집합만
  제거한다(동시에 다른 빌드가 같은 디렉터리에 쓰면 그 파일도 지울 수 있다 — 재동결 중 병행
  실행을 금지하는 문장으로 막는다).

## 6. 부수 규정

### R6 `interaction_exclusions` 이월 (rv-A B5)

`begin`이 기존 행을 journal에 보존한다. 재수집 후 Coordinator가 **새 관찰 문서의 target id
기준으로 행을 다시 짓는다** — `approval_quote`·`scope_ref`는 staging `scope.md`에서 재사용하고
단위 키(`target`·`action`·`option`)만 새 id에 맞춘다. 10% 상한은 새 분모로 재검증한다.
대응 단위를 못 찾은 행은 버리지 않고 배너에 올려 사용자 확인을 받는다.

### R7 상태 전이

| 키 | 값 |
|---|---|
| `design_status` | **`ready` 유지**(§1) |
| `implementation_visual` | 완료 빌드였으면 **`pending`** — 구현 증거가 옛 동결 기준이다. 새 값을 만들지 않는다 |
| `evidence_debt` | `commit` done 단계에서 **`build_debt()`가 부채 없음을 낼 때만** 키 제거. `build_debt()`는 `design_status=='ready'`를 요구하므로 이 순서에서만 호출 가능하다(rv-R m-6) |
| `g2_approved` | 유지 — 재동결은 승인 사실을 지우지 않는다. 재대조 필요는 `implementation_visual`이 표현한다 |

완료 빌드를 재동결하면 G2 재대조 전까지 마무리 backstop이 막힌다(`validate_visual`의
`input_digest: stale`). 정직한 신호이므로 수용하고 **G0 배너에 «이 재동결은 G2 재대조를 요구한다»
1줄을 의무화**한다.

### R8 부채 결정 게이트 정렬 — 재동결 = ⓐ 경로 (rv-A B3)

재동결은 조작 상태를 항상 새로 수집하므로 **부채를 해소하는 실행**이다.
ⓑ defer가 허용하는 것에서 **재동결을 뺀다**(= 조회·보고 + 완료 빌드의 G2 승인·마무리 backstop).
사용자가 재동결을 요청하면 그 발화가 곧 ⓐ 결정의 `quote`다 — 대리 기록이 사라진다(G-C).

고칠 곳(전수 · 미러 동반): `evidence_debt_hook.py:36-40`·`:132` · `REQUEST_GUIDE.md:115-116` ·
`commands:129` · Codex `SKILL.md:151`.

### R9 중단·잔존 감지 (rv-B B3 · rv-R RM2·RM5)

- **hook**: 빌드 폴더에 `_refreeze-*` 또는 `_prev-*`가 있으면
  `[dddjango-web] interrupted refreeze — <폴더>: staging left behind · run refreeze.py commit --resume or abort`
  를 낸다. 이 판정은 `design-input.json` 유무와 **`design_status` ready 게이트 양쪽 모두의 바깥**에서
  돌아야 한다 — `build_debt()`/부채 줄 생성 안에 넣으면 영원히 발화하지 않는다.
- **backstop**: 빌드 폴더에 `_refreeze-*`/`_prev-*`가 있으면 `[DESIGN] BLOCKER interrupted refreeze`.
  hook은 SessionStart·UserPromptSubmit에서만 발화해 `commands:171` ⑤의 같은 턴 커밋 창을 막지
  못한다(rv-R RM5) — backstop이 커밋 후에라도 확실히 잡는다.
- **규범**: Phase 2 진입 준비 ⑤ 커밋 **전에** 잔존 없음을 확인한다.

### R10 제거 대상 (rv-A M4 전수 · rv-R m-3)

| 위치 | 제거·수정 |
|---|---|
| `scripts/archive_design.py` (+미러) | `--compare-build`·`--compare-out`·`--carried`·`compare_manifests()`·exit 3/4·`_history` 자동 carried |
| `scripts/test/test_design_archive.py` (+미러) | `RefreezeCompareTests` 10건(잔여 32건이 비-compare 기능을 계속 덮음) |
| `scripts/check_design_evidence.py` (+미러) | `carried_from` 수용(`:1140-1143`) |
| `commands/dddjango-web.md` (+Codex `SKILL.md` 의미 미러) | 재동결 출현 12곳 전수: `9 70 129 130 134 137 146 154 171 205 227 234`(Codex `8 123 151 152 156 159 169 177 194 228 250 258`). `:227`은 «openapi 재동결»로 어휘 분리 |
| `references/design-acquisition.md` (+byte 미러) | §2 «재동결» 전면 재작성 |
| `references/design-evidence.md` (+byte 미러) | `carried_from`(`:115`·`:336`·`:338`)·exit 체계(`:27-28`·`:343-346`) — **절 단위로 재작성**(행 지정 집행 금지) |
| `agents/design-review-web.md` (+Codex 역할 SKILL) | `:25` 감사 목록의 `carried` |
| `REQUEST_GUIDE.md` (+byte 미러) | `:115-116` 부채 문구(R8) |
| `scripts/test/test_evidence_debt{,_hook}.py` (+미러) | defer 픽스처 quote의 «재동결만» 전제 |

### R11 회귀 그물 (rv-R m-4)

`commands` ↔ Codex `SKILL.md`는 의미 미러라 기계 대조가 없고, 기존 시험 어디에도
«defer가 재동결을 허용한다»를 검증하는 단언이 없다. R8을 한 곳이라도 빠뜨리면 red가 나지 않는다.
→ `workspace/tools/web_refreeze_contract.py` 신설(선례: `web_hooks_contract.py`), `verify-web`에 배선:
① 4곳(hook 스크립트·REQUEST_GUIDE·commands·Codex SKILL)의 defer 허용 목록에 «재동결»이 **없음**
② `--compare-build`·`refreeze-diff`·`carried_from` 잔존 0 ③ `refreeze.py` 4 서브커맨드 실재.

## 7. 행동 시험

| id | 시나리오 | 합격 조건 |
|---|---|---|
| B1 | A8 **사본**에서 «재동결» 발화 | staging 전 축 생성 → `check` 0 → inputs 0 → `commit` done · 원본 증거·`render-audit.json`·`design-input.json`·`scope.md` 새 바이트 · `visual-evidence.json`이 가리키는 `*-impl.png` **전부 온존** · 3겹 S의 상태 캡처까지 교체 · 잔존 0 · `design_status=ready` |
| B2 | 실패 주입 — `observe_interactions.mjs` 3번째 case에서 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`을 부재 경로로 치환(`observe_interactions.mjs:17` env 폴백 · case마다 별도 프로세스라 주입 가능) | `abort` 후 live 빌드 폴더 **바이트 동일** · `web/static/images/`가 `images_before`와 동일 · 잔존 0 |
| B3 | `commit`을 `discarded` 단계에서 강제 중단 | `commit --resume`이 완주하고 결과가 B1과 동일 · 중간 상태에서 hook·backstop이 `interrupted refreeze`를 낸다 |
| B4 | B1 직후 hook 발화 | 부채 목록에 없고 **`design_status=ready`인 상태에서** 그렇다(빌드가 평가 대상에서 빠져서가 아님 — rv-A M3) |
| B5 | `interaction_exclusions` 1행을 가진 **합성 빌드** 재동결 | 새 `design-input.json`에 행이 재작성되고 inputs exit 0 |
| B6 | 같은 세션 두 번 요청 | 두 번 다 전량 재실행 |
| B7 | `web_refreeze_contract.py` | R11의 3항목 green |

B1~B3·B5는 A8 **사본** 또는 합성 픽스처에서만 수행한다 — A8 본체는 최종 테스트 베드다.

## 8. 남는 우회 (명시)

1. **시안 자산 staleness의 침묵** — 구현 템플릿이 옛 이미지 경로를 계속 쓰면 재동결만으로는
   드러나지 않는다. G2 재대조에서 드러난다(R7이 `implementation_visual=pending`으로 강제).
2. **고아 이미지** — 미참조가 된 옛 이미지는 남는다. 청소 도구 없음.
3. **전량 재수집 비용** — 매 재동결이 드라이버를 통째로 돌린다(A8 12 case 기준 수십 분).
   staging 창 동안 동결물이 **2벌** 존재해 디스크를 쓴다(A8 archive 1벌 추가 · rv-R RM5 파생).
4. **`motion-notes.md`는 재기록하지 않는다** — m-id 양방향 전수성(`check_motion_spec.py:360-366`)이
   보존된 `design-spec.md`와 묶여 있다. 갱신은 architect 반송을 동반하는 별건이다.
5. **`legacy_v1_allowed`·`current_nondesign_scope`가 staging 전 구간 닫힌다** — `_refreeze-*`가
   untracked이기 때문이다(`backstop.py:112-123`·`:167-173`). v2가 «교체 수초로 축소»라고 한 것은
   거짓이었다(rv-R m-2). 실질 피해는 낮다(재동결 중 다른 마무리를 돌릴 이유가 없다).
6. **`_history/`** — 손대지 않는다. `compare_manifests()` 제거로 그것을 아는 코드는 0이 된다.
7. **재동결 중 병행 실행 금지** — 이미지 차집합 롤백이 남의 파일을 지울 수 있다(R5).

## 9. 계획 초안 (Task 7)

| Task | 내용 |
|---|---|
| T1 | `scripts/refreeze.py` 신설(begin/check/commit/abort · journal · swap-plan) + Codex 미러 + 단위 시험 |
| T2 | `evidence_debt{,_hook}.py` 중단 감지(R9 — ready 게이트 밖) + 부채 문구 정렬(R8) + 미러 + 시험 |
| T3 | `backstop.py` 잔존 감지 1건(R9) + 미러 + 픽스처 |
| T4 | `archive_design.py` compare 제거 · `check_design_evidence.py` `carried_from` 제거 + 미러 + 시험 정리(R10) |
| T5 | 규범 — `commands/dddjango-web.md` 12곳 + Codex `SKILL.md` 의미 미러(§1~R9) |
| T6 | reference·문서 — `design-acquisition.md` §2 · `design-evidence.md` 절 재작성 · `agents/design-review-web.md` · `REQUEST_GUIDE.md` + byte 미러 · `web_refreeze_contract.py` + `verify-web` 배선 |
| T7 | 행동 시험 B1~B7 · `make verify` · 릴리즈 게이트 보고 |

작업 트리 그대로 진행하고(브랜치 금지 — web 관례) 커밋은 최종 승인 뒤 한 번.

**범위 고지**: v1 «신규 도구 0 · Task 3~4» → v3 **신규 스크립트 2종(`refreeze.py` ·
`web_refreeze_contract.py`) · 기존 스크립트 4종 수정 · Task 7**. 적대 검토 3기가 파괴적 구간을
산문 규율에 맡기는 위험을 반복 실증했다(rv-B B1·B3·M1 · rv-R RB1·RB2). 수리 1보다 약간 크다.

## 10. 누적 적대 검토 반영 대조

### rv-R (v2 재검토)

| id | 반영 |
|---|---|
| RB1 `scope.md` 두 벌 | **수용** — §3. 해석 ⓒ 채택(staging 정본 + commit이 교체) + 검토 순서 규정 |
| RB2 원자 교체 미성립 | **수용** — §4.6. 파일 단위 · `swap-plan.json` 단계 기록 · `--resume` · 되감기. `discard_set`을 journal에 기록해 재개가 live design-input에 의존하지 않게 함 |
| RM1 S가 한 겹 얕다 | **수용** — §2에서 3겹 순회 |
| RM2 `design_status` 주체 부재 · M3 미해소 | **수용** — §1에서 «전 구간 ready 유지»로 확정(blocked 창 자체를 없앰) + R9가 ready 게이트 밖에서 돌아야 함을 명시 |
| RM3 드라이버 **입력** 경로 분기 | **수용** — §4.3 표 + `begin`이 입력을 staging에 복사 + declared/excluded-regions를 교체 대상으로 이동 |
| RM4 «live 무손상» 거짓·자기모순 | **수용** — §5에서 빌드 폴더로 한정, `abort`를 의무로 격상, v2의 «복원할 것이 없다» 문장 정정 |
| RM5 커밋 창을 hook이 못 막음 | **수용** — R9에 backstop 감지 추가 + 규범 문장 |
| m-1 멱등이 반만 참 | **수용** — §5에 인라인 토큰 밀림 명시 |
| m-2 «수초로 축소»는 거짓 | **수용** — §8 우회 5에 사실대로 |
| m-3 `design-evidence.md` 행번호 | **수용** — R10에서 절 단위 재작성 명시 |
| m-4 회귀 그물 0 | **수용** — R11 신설(`web_refreeze_contract.py`) |
| m-5 «끝»이 교체보다 앞섬 | **수용** — §1에서 ④로 확정 |
| m-6 `evidence_debt` 제거 순서 | **수용** — R7에 ready→build_debt→제거 순서 명시 |
| D-1~D-7 도구 명세 부족 | **수용** — §4.1 인자·exit 표 · §4.2 journal 스키마 · §4.3 분기표 · §4.4 build-state 출처 · §4.6 파일 단위 |

### rv-A / rv-B (1차) — rv-R가 «닫힘»으로 확인한 항목

rv-A B1·B2·B3·B4·M2·M4·M5·m1·m2 · rv-B B2·M2·N1·N2·N3 = **닫힘**(rv-R §B가 각각 코드로 재확인).
rv-A B5·M1·M6·m3·m4 · rv-B B1·B3·B4·M1 = v2에서 부분, **v3에서 위 표로 닫음**.
rv-A M3 = v2 미해소, **v3 §1에서 원인 제거**(blocked 창 자체를 없앰).
