# 설계 v5 — 재동결 = 전량 폐기 후 재동결 (2026-09-15)

진단: `workspace/eval/web-refreeze-completeness/diagnosis.md` (커밋 `10faaff2`)
적대 검토 5기: `design-review/rv-A.md` · `rv-B.md` · `rv-R.md` · `rv-F.md` · `rv-C.md` — 대조는 §12.

> **판형 이력**
> v1 «선폐기 → 재수집» → BLOCKER 9(치우는 동안 live가 불완전).
> v2 «staging 우선 → 원자 교체» → 구조는 코드로 성립, 교체 단계·`scope.md` 미명세 → BLOCKER 2.
> v3 «재개 가능 트랜잭션» → 검사기 4축 성립 확인, 그러나 편집 목록이 어휘 grep이라 인자 줄을 비껴감 → BLOCKER 2.
> v4 «`<대상 폴더>` 어휘 + 여집합 폐기» → 목록이 또 샜고(`:146`·`design-acquisition`의 자리표시자는 `BUILD`),
> 여집합이 재수집 불가 입력(`captures/external/*`)을 파괴 → BLOCKER 4.
> **v5는 ① 편집 대상 열거를 버리고 기계 불변식으로 바꾸고 ② 폐기를 포인터 기반으로 되돌리며
> 어느 포인터에도 없는 파일은 «고아»로 보고만 한다.**

## 0. 목표와 비목표

**목표** — 사용자 확정 정의를 규범으로 만든다:

> «차이점을 알 필요도 없어. 재동결은 기존에 동결한 파일을 **완벽하게 삭제하고 다시 동결**하는 걸로 해» (2026-09-15)

**비목표**: 차이 대조·조작 상태 대조기(사용자 기각) · 보더 잘림(수리 2·3) ·
백엔드 계약 재동결(별도 축) · `motion-notes.md` 재기록(§9 우회 4) · 고아 청소(§9 우회 7).

## 1. 정의

**재동결** = ① staging에 시안 동결물 **전량**을 처음부터 새로 만든다 → ② 완전성·입력 게이트를
staging에서 통과시킨다 → ③ 기존 동결물을 통째로 지우고 staging 산출물로 **교체**한다 →
④ 교체 후 live에서 `--phase inputs` exit 0을 재확인한다. **끝은 ④다.**

- 사용자가 요청했을 때만 실행하고, **요청이 있으면 항상 전량 재실행한다** — 직전 결과 재사용·
  «이번 세션에 이미 했음»으로 생략하지 않는다(G-B).
- **`design_status`는 전 구간 `ready`를 유지한다.** 근거는 **부채 hook 가시성**이다 —
  `evidence_debt.py:139-140`이 `ready`가 아닌 폴더를 판정 대상에서 지우므로, 내리는 순간
  재동결 중인 빌드가 hook 시야에서 사라진다. 이를 위해 `commands:144`의 «재기준 승인 직후에도
  blocked 유지» 문장을 재동결 절차로 대체한다.

## 2. 폐기 집합과 보존

### 2.1 폐기는 **포인터로만** 정한다 (rv-C N-B4 · rv-F M-1)

v4는 «`captures/**` 중 `visual-evidence.json`이 가리키지 않는 전부»(여집합)로 정의했으나,
A8 실측에서 `captures/` 하위에 `original/`·`impl/`·`external/`·`attempt-1/`이 공존하고
그중 **`captures/external/*`(lucide.css·woff2 등)는 `source-manifest`에 `status:external`·
`local_path:""`로만 남는 재수집 불가 수동 입력**이다. 여집합 규칙은 그것을 파괴한다. 철회한다.

**폐기 집합 S** — `design-input.json`에서 **3겹**으로 순회한다:

| 겹 | 포인터 |
|---|---|
| 1 | case의 `reference_capture.path` · `source_observation.path` |
| 2 | 관찰 문서 안의 `capture.path` · `trace.path` · (v2면) `interactions.path` |
| 3 | interactions 문서 안의 `initial.capture.path` · `steps[].after.capture.path` |

포인터는 build 상대 경로이므로 `captures/original/x.png` 같은 **하위 디렉터리 배치도 그대로 잡힌다**
(A8의 `original/`·`impl/` 분리 빌드에서 확인).

**고정 폐기·교체 대상**: `design-ref/**` · `source-manifest.json` · `design-tokens.json` ·
`asset-manifest.json` · `screen-meta.json` · `render-audit.json` · `design-input.json` ·
`coverage-review.md` · `scope.md`(§3) · `<screen>-declared.json`·`--excluded-regions` 입력 ·
`refreeze-diff.json`(생성 도구가 사라지므로 고아로 남기지 않는다).

### 2.2 고아 — 지우지 않고 **보고한다**

`captures/**` 중 S에도 `visual-evidence.json` 포인터에도 없는 파일을 **고아**라 한다.
A8 실측: 표적 빌드 7건(`smoke-*-impl.png`·비390 구현 캡처), 다른 빌드 최대 270건
(`attempt-1/*` 실패 회차 원본 · `external/*` 수동 입력).

- `begin`이 고아를 `journal.orphans`에 기록한다. **폐기하지 않는다.**
- G0 배너와 종료 보고에 «미참조 `captures/` 파일 k건 — 지우지 않음» 1줄을 낸다.
- 근거: 고아는 «동결한 파일»의 포인터 어디에도 없어 동결물이라 단정할 수 없고, 실제로
  재수집 불가 입력(`external/`)·규범이 보존을 요구하는 실패 회차 이력(`commands:144`)·
  등록되지 않은 구현 캡처가 섞여 있다. 침묵하지 않고 사용자에게 돌려주는 것이 정직하다.

**보존**: `build-state.json`(키만 갱신) · `design-spec.md` · `visual-check.md`(절 갱신) ·
`visual-evidence.json`과 그것이 가리키는 `captures/*` · `render-audit-impl.json` ·
`motion-notes.md` · 빌드 산문 · 고아 · `openapi-full.json`·`server-contract*`·`contract-paths.txt`.
**열거되지 않은 파일은 보존이 기본이다.**

## 3. `scope.md`는 교체 대상이다

규범은 재수집 도중 `scope.md`에 **세 번** 쓰기를 요구한다 — `commands:143`의 실행 경계 기록,
`commands:142`의 렌더 실측 **생략 사유 1줄**, 예외 행의 새 승인 원문(§6 R6). 동시에 `commands:129`가
«scope 바이트가 바뀌면 포인터·review digest가 어긋난다»를 성문화한다.

1. `begin`이 live `scope.md`를 staging에 복사하고 그 sha를 journal에 기록한다.
2. 위 세 쓰기는 **staging 복사본에만** 한다. 규범의 해당 문장을 «`<대상 폴더>`의 `scope.md`»로
   수식한다 — **무수식 리터럴로 두면 규범이 live에 쓰라고 지시해 4의 sha 대조가 매 회차
   exit 1이 된다**(rv-C N-B3).
3. **staging 창 동안 live `scope.md`에 쓰는 것을 금지한다.** 금지가 없으면 그 창에 live에 적힌
   줄이 `commit`의 덮어쓰기로 **red 없이 증발한다**.
4. `commit`은 교체 직전 live `scope.md`가 journal의 `begin` 시점 sha와 같은지 확인하고,
   다르면 **exit 1**로 멈춘다.
5. `commit`이 staging `scope.md`를 live로 옮긴다 — `design-input.json.scope`의 sha가 staging
   기준이므로 교체 후에도 일치한다(rv-F ①이 검사기 4축 전부 성립 확인).
6. **순서**: 독립 검토는 `scope.md` 최종 확정 **뒤에** 받는다(`reviewed-input` digest가 scope
   바이트를 포함하므로 어기면 inputs가 스스로 red를 낸다).

## 4. 실행 — `refreeze.py`

### 4.1 서브커맨드

| 명령 | 인자 | exit |
|---|---|---|
| `begin` | `--build` `--project-root` `--quote <사용자 재동결 발화>` | 0 · 2 선점 · 1 오류 |
| `check` | `--build` `[--staging]` `[--render-audit-skipped <enum 사유>]` | 0 완전 · 3 미완 · 1 오류 |
| `commit` | `--build` `[--staging]` `[--resume]` `[--stop-after <phase>]` | 0 완료 · 3 중단·되감김(`--stop-after`의 의도적 중단 포함 — `--resume`이 필요한 상태를 뜻한다) · 1 오류 |
| `abort` | `--build` `[--staging]` | 0 완료 · 1 오류·거부 |

- `--staging` 생략 시 `_refreeze-*`가 정확히 하나일 때만 자동 선택, 둘 이상이면 exit 1 + 목록.
- `begin`은 기존 `_refreeze-*`/`_prev-*`를 삭제하지 않고 exit 2로 거부한다.
- `abort`는 journal에 `completed_at`이 있으면 **거부**한다(완료된 재동결 파괴 방지).
- **`check --render-audit-skipped <사유>`가 journal의 `has_render_audit`을 false로 내리는
  유일한 주체다**(사유는 `commands:142`의 enum — rv-C MAJOR 3 · rv-F M-2).

### 4.2 journal (`<staging>/journal.json`)

```json
{"version": 1, "build": "<abs>", "project_root": "<abs>", "started_at": "<ISO8601>",
 "completed_at": null, "quote": "<사용자 재동결 발화>",
 "discard_set": ["design-ref/index.html", "captures/original/x.png", "…"],
 "orphans": ["captures/external/lucide.css", "captures/smoke-login-390-impl.png", "…"],
 "scope_sha256_at_begin": "<hex>",
 "has_render_audit": true, "render_audit_skip_reason": null,
 "images_before": ["web/static/images/<name>", "…"],
 "interaction_exclusions": [ … ], "evidence_debt_before": { … | null },
 "copied_inputs": ["scope.md", "…"]}
```

`discard_set`·`orphans`는 **파일 단위로 전개**한다(디렉터리 항목 금지).

### 4.3 재수집 — 경로 치환 (rv-F B-1 · rv-C N-B1·N-B2)

v3는 분기를 설계 문서에만 적었고(런타임 미발화), v4는 편집 대상을 손으로 열거해 또 샜다.
**v5는 열거를 버리고 규칙 + 기계 불변식으로 간다.**

**치환 규칙**

> 재동결 중에는 **폐기·교체 대상 산출물(§2.1)의 경로**가 그 빌드의 staging(`_refreeze-<ts>`)을
> 가리킨다. 규범의 자리표시자는 두 가지다 — `commands`의 `<산출물 폴더>`, `design-acquisition.md`의
> `BUILD`. 이 둘이 **폐기·교체 대상을 가리킬 때만** 각각 `<대상 폴더>`·`TARGET`으로 바꾼다.
>
> - **치환 제외 ①**: `--assets-root`는 언제나 프로젝트 루트다(이미지는 구현 트리에 쓴다 · §5).
> - **치환 제외 ②**: **보존 대상**(`motion-notes.md` · `build-state.json` · `visual-check.md` ·
>   `design-spec.md` · `visual-evidence.json`)의 경로는 그대로 둔다. 치환하면 staging에 쓰이고
>   §4.6-3의 덮어쓰기가 보존 규정을 위반한다(rv-C MAJOR 2 — `commands:142`가 같은 줄에서
>   `render-audit.json`과 `motion-notes.md`를 함께 지시한다).
> - `<대상 폴더>`의 **정의는 `commands`의 «산출물 위치» 절(`:22~`)에 둔다.**

**완전성은 사람이 아니라 §8의 검사기가 보증한다.** 아래는 구현자를 위한 안내일 뿐이며,
빠뜨려도 `verify-web`이 red를 낸다:
`commands` — `137`(freeze_design) · `138`(extract_design) · `140`(freeze_design·extract_design·
fetch_images) · `142`(렌더 실측 출력) · `143`(observe_interactions `--out`·`--captures-dir`·
`--declared`·`--excluded-regions`·scope 기록) · `145` · **`146`(입력 게이트 `--build`)** ·
`design-acquisition.md` — **`:27`(archive 수집)** · `:30` · §2 재작성 · **`:116`(조작 상태 수집)**.

**렌더 실측은 «도구»가 아니다** — 인자 없는 브라우저 콘솔 스니펫이고 Coordinator가 결과를
파일로 적는다. 치환은 «적는 경로»에 적용된다.

`begin`이 staging에 복사하는 입력: `scope.md` · `<screen>-declared.json` · `--excluded-regions`
입력(있는 것만). A8 표적 빌드에는 declared/excluded가 0건이라 복사 대상이 `scope.md` 하나뿐이고,
드라이버는 `--declared` 없이 돌며 보완 루프가 선언을 새로 만든다(비용은 §9 우회 8).

### 4.4 `check`

staging에서 다음 **실재**를 확인한다: `design-ref/` · `source-manifest.json` ·
`design-tokens.json` · `asset-manifest.json` · `screen-meta.json` · `design-input.json` ·
`render-audit.json`(journal의 `has_render_audit`이 true일 때만) + `design-input.json`의 3겹
포인터 해소 + archive 원본이면 case마다 v2 관찰 실재 + **폐기 집합 자기 검사**(3겹 포인터 ⊆
`discard_set`). 내용 검증은 하지 않는다(수용된 한계).

### 4.5 입력 게이트

`check` exit 0 뒤 **staging을 `--build`로** 주어 `--phase prepare` → 독립 검토 → `--phase inputs`
exit 0. `commands:146`이 `--build <산출물 폴더>`로 고정돼 있으면 **무손상 live에서 exit 0이 나는
false green**이 되고 staging은 검증되지 않는다(rv-C N-B1) — §8-D가 이를 막는다.
**prepare exit 2는 실패가 아니라 `commands:143`의 보완 루프 진입**이다. live가 무손상이므로
몇 번이든 반복한다.

### 4.6 `commit` — 파일 단위 재개 가능 트랜잭션

`<BUILD>/_prev-<ts>/swap-plan.json`에 계획을 먼저 쓰고 진행한다:
`planned → discarded → installed → verified → done`. **디렉터리 이동 금지.**

1. **planned** — `discard_set`과 staging 산출물 목록으로 계획을 쓴다. 같은 단계에서 §3-4의
   live `scope.md` sha 대조(불일치 → exit 1).
2. **discarded** — 각 파일을 `_prev-<ts>/`로 이동(경로 구조 보존).
   src 있음 → 이동 · src 없고 dst 있음 → 건너뜀 · **둘 다 없음 → 오류**.
3. **installed** — staging 산출물을 각 파일 live 경로로 이동(`captures/` 병합).
   **staging 쪽이 있으면 대상 존재와 무관하게 덮어쓴다** · staging 쪽이 없고 live에 있으면 건너뜀 ·
   둘 다 없음 → 오류. 두 단계에 같은 «건너뛴다»를 적용하면 이름 충돌에서 새 산출물이 버려져
   verified가 sha mismatch로 되감고 resume이 같은 실패를 반복하는 **livelock**이 된다.
4. **verified** — `check_design_evidence.py --build <BUILD> --phase inputs` exit 0 확인.
   실패면 계획을 역순으로 되감아 `_prev-<ts>`를 복원하고, **이어서 `abort`와 동일한 이미지
   되돌리기**(`journal.images_before` 차집합 제거)와 `evidence_debt_before` 복원을 수행한 뒤 exit 3.
5. **done** — `build-state.json` 키 갱신(§6 R7) → **journal에 `completed_at` 기록** →
   staging 삭제 → `_prev-<ts>` 삭제. 이 순서로 «`_prev`가 먼저 사라져 `abort`가 성공한 재동결을
   파괴하는» 창을 없앤다.

## 5. 이미지 축 — 재동결은 구현 트리에 쓴다

`fetch_images.py:35,110`이 `<ROOT>/web/static/images/`에 내용 해시 파일명으로 쓴다.

- 소스명이 있는 이미지는 멱등이지만 **인라인(`data:`)은 아니다**(토큰이 문서 내 순번).
- «live 무손상»은 **빌드 폴더에 한한다**. 이미지가 추가되는 순간 완료 빌드의
  `implementation_digest`가 stale이 되어 다른 작업의 backstop이 `[DESIGN] BLOCKER`를 낸다.
- 따라서 **실패 시 `abort`(또는 verified 실패 경로)는 의무**이고, 둘 다 같은 차집합 제거를 한다.
- 재동결 중 같은 프로젝트의 **병행 실행을 금지한다**.

## 6. 부수 규정

### R6 `interaction_exclusions` 이월

`begin`이 기존 행을 journal에 보존한다. 재수집 후 Coordinator가 새 관찰 문서의 target id 기준으로
행을 다시 짓는다 — `approval_quote`·`scope_ref`는 staging `scope.md`에서 재사용하고 단위 키만
새 id에 맞춘다. 10% 상한은 새 분모로 재검증한다. 대응 단위를 못 찾은 행은 버리지 않고 배너에 올린다.

### R7 상태 전이 — 쓰는 주체 명시

| 키 | 값 | 쓰는 주체 |
|---|---|---|
| `design_status` | `ready` 유지 | 아무도 안 쓴다(§1) |
| `evidence_debt` | `{decision:"observe", quote:<journal.quote>, at, reason:"재동결 = 조작 상태 전량 재수집", cases:<현재 부채 수>}` — 기존 키가 `defer`여도 덮어쓴다 | **`begin`** |
| `evidence_debt` | `build_debt()`가 부채 없음을 내면 키 제거 | `commit` done |
| `evidence_debt` | `evidence_debt_before`로 복원 | `abort` · verified 실패 |
| `implementation_visual` | 완료 빌드였으면 `pending` | `commit` done |
| `has_render_audit` | journal 값 반영(`check --render-audit-skipped`가 내린 값) | `commit` done |
| `g2_approved` | 유지 | — |

`begin`이 `evidence_debt`를 쓰지 않으면, 부채 빌드를 재동결하는 내내 live design-input이 옛
static-only 그대로라 hook이 매 프롬프트마다 «decision required before any run» 배너를 낸다 —
진행 중인 재동결을 금지하는 문구로. `decision:"observe"`는 기존 계약과 충돌하지 않는다
(`evidence_debt.py:17,49-57,99-101`이 받고 hook이 «observation pending»을 낸다 — rv-C가 코드로 확인).

완료 빌드를 재동결하면 G2 재대조 전까지 마무리 backstop이 막힌다.
**G0 배너에 «이 재동결은 G2 재대조를 요구한다» 1줄을 의무화**한다.

### R8 부채 결정 게이트 정렬 — 재동결 = ⓐ 경로

ⓑ defer가 허용하는 것에서 **재동결을 뺀다**(= 조회·보고 + 완료 빌드의 G2 승인·마무리 backstop).
사용자가 재동결을 요청하면 그 발화가 `begin --quote`로 들어가 ⓐ 결정의 `quote`가 된다.
고칠 곳: `evidence_debt_hook.py`의 `DECISION_LINE`·undecided 줄 · `REQUEST_GUIDE.md` ·
`commands:129` · Codex `SKILL.md`(전부 미러 동반).

### R9 중단·잔존 감지

- **hook**: 빌드 폴더에 `_refreeze-*`/`_prev-*`가 있으면
  `[dddjango-web] interrupted refreeze — <폴더>: staging left behind · refreeze.py commit --resume (or abort if not completed)`.
  이 판정은 `design-input.json` 유무와 `design_status` ready 게이트 **양쪽 바깥**에서 돌아야 한다.
- **backstop**: 같은 조건에서 `[DESIGN] BLOCKER interrupted refreeze`. hook은 SessionStart·
  UserPromptSubmit에서만 발화해 `commands:171` ⑤의 같은 턴 커밋 창을 막지 못한다.
- **규범**: Phase 2 진입 준비 ⑤ 커밋 전에 잔존 없음을 확인한다.

## 7. 제거 대상

| 위치 | 제거·수정 |
|---|---|
| `scripts/archive_design.py` (+미러) | `--compare-build`·`--compare-out`·`--carried`·`compare_manifests()`·exit 3/4·`_history` 자동 carried |
| `scripts/test/test_design_archive.py` (+미러) | `RefreezeCompareTests` 10건(잔여 32건이 비-compare 기능을 계속 덮음) |
| `scripts/check_design_evidence.py` (+미러) | `carried_from` 수용 |
| `scripts/test/test_interaction_evidence.py:626-641` (+미러) | `carried_from` **리터럴을 제거**한다 — 그 시험의 의도(«미지 필드는 exit 2»)는 일반 이름(`unknown_field`)으로 보존하고, `carried_from`이라는 이름을 남기지 않는다. 남기면 §8-B의 «잔존 0»과 충돌한다. **상시 검증 경로**(`fixtures_interactions.sh:9` → `run_fixtures.sh` → `verify-web`)라 함께 고치지 않으면 red |
| `commands/dddjango-web.md` (+Codex `SKILL.md` 의미 미러) | 재동결 절 재작성(§1~R9) · `:144` 재기준 문장 대체 · `:227` «openapi 재동결» 분리 · `<대상 폴더>` 정의 추가 · **치환(완전성은 §8이 보증)** |
| `references/design-acquisition.md` (+byte 미러) | §2 «재동결» 전면 재작성 · `BUILD`→`TARGET` 치환 |
| `references/design-evidence.md` (+byte 미러) | `carried_from`·exit 체계 — **절 단위 재작성** |
| `agents/design-review-web.md` (+Codex 역할 SKILL) | 감사 목록의 `carried` |
| `REQUEST_GUIDE.md` (+byte 미러) | 부채 문구(R8) |
| `scripts/test/test_evidence_debt{,_hook}.py` (+미러) | defer 픽스처 quote의 «재동결만» 전제 |

## 8. 회귀 그물 — 열거를 대체하는 불변식

`workspace/tools/web_refreeze_contract.py` 신설(선례 `web_hooks_contract.py`), `verify-web` 배선.
**이것이 v3·v4가 두 번 샌 «손으로 만든 편집 목록»을 대체한다.**

| id | 검사 |
|---|---|
| A | 4곳(hook 스크립트·`REQUEST_GUIDE`·`commands`·Codex `SKILL.md`)의 defer 허용 목록에 «재동결»이 **없음** |
| B | `--compare-build`·`refreeze-diff`·`carried_from` 잔존 0 |
| C | `refreeze.py` 4 서브커맨드 실재 |
| **D1** | `commands`·`design-acquisition.md`의 **코드 조각 안**에서 자리표시자(`<산출물 폴더>`·`BUILD`)가 **폐기·교체 대상**(§2.1 고정 목록 + `captures`·`--build`)을 가리키는 곳이 **0**. 남아 있으면 red — 내가 줄을 빠뜨려도 잡힌다 |
| **D2** | 같은 문서에서 **보존 대상**(`motion-notes.md`·`build-state.json`·`visual-check.md`·`design-spec.md`·`visual-evidence.json`)의 경로가 `<대상 폴더>`·`TARGET`으로 치환돼 **있으면** red |
| **D3** | `scope.md` 쓰기를 지시하는 문장이 **무수식 리터럴**로 남아 있으면 red(§3-2) |
| **D4** | `<대상 폴더>` 정의 줄이 `commands`의 «산출물 위치» 절에 실재 |

## 9. 남는 우회

1. **시안 자산 staleness의 침묵** — G2 재대조에서 드러난다.
2. **고아 이미지** — 미참조가 된 옛 이미지는 `web/static/images/`에 남는다.
3. **전량 재수집 비용** — 매 재동결이 드라이버를 통째로 돌린다(A8 12 case 기준 수십 분).
4. **`motion-notes.md`는 재기록하지 않는다** — m-id 양방향 전수성이 보존된 `design-spec.md`와 묶여 있다.
5. **`legacy_v1_allowed`·`current_nondesign_scope`가 staging 전 구간 닫힌다**(`_refreeze-*`가 untracked).
6. **`_history/`** — 손대지 않는다.
7. **`captures/` 고아는 남는다** — 지우지 않고 보고만 한다(§2.2). 사용자 정의 «완벽하게 삭제»는
   **포인터가 가리키는 동결물**에 대해 성립하며, 어디서도 참조되지 않는 파일은 그 정의의 밖이다.
   청소를 원하면 별건으로 지시한다.
8. **선언 재작성 비용** — A8 표적 빌드에 `<screen>-declared.json`이 없어 매 재동결마다 보완 루프가 선언을 새로 만든다.
9. **디스크** — staging 창 동안 동결물이 2벌 존재한다.
10. **§8-D1의 사각** — D1은 자리표시자 + 폐기 대상 이름의 **리터럴 인접**(`<산출물 폴더>/design-ref` ·
    `--build <산출물 폴더>` · `BUILD/captures` …)만 잡는다. 산문으로 «산출물 폴더의 design-ref를»처럼
    풀어 쓴 지시는 놓친다. 현행 규범의 수집 인자는 전부 코드 조각 안 리터럴이라 실효가 있지만
    (rv-F B-1·rv-C N-B2의 실측 목록이 모두 리터럴), 이후 개정에서 산문으로 바뀌면 그물이 헐거워진다.

## 10. 행동 시험

| id | 시나리오 | 합격 조건 |
|---|---|---|
| B1 | A8 **사본**에서 «재동결» 발화 | staging 전 축 → `check` 0 → inputs 0(**staging 대상**) → `commit` done · 폐기 집합 전부 새 바이트 · `visual-evidence.json`이 가리키는 캡처 **온존** · **고아 온존 + 배너에 k건 보고** · 잔존 0 · `design_status=ready` |
| B2 | 드라이버 3번째 case에서 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`을 부재 경로로 치환 | `abort` 후 live 빌드 폴더 **바이트 동일** · `web/static/images/`가 `images_before`와 동일 · `evidence_debt` 복원 · 잔존 0 |
| B3 | `commit`을 `discarded`에서 강제 중단 | `commit --resume` 완주 · 중간 상태에서 hook·backstop이 `interrupted refreeze` |
| B4 | `installed` 이름 충돌 주입 | 덮어쓰기로 통과 · livelock 없음 |
| B5 | B1 직후 hook | 부채 목록에 없고 `design_status=ready`인 상태에서 그렇다 |
| B6 | `interaction_exclusions` 1행 합성 빌드 | 행 재작성 후 inputs exit 0 |
| B7 | `done` 이후 `abort` | exit 1 거부 · 신규 이미지 온존 |
| B8 | `web_refreeze_contract.py` | §8 A~D4 green |
| **B9** | **치환 누락 주입** — `commands`의 인자 줄 하나를 `<산출물 폴더>`로 되돌린다 | D1이 red · 즉 §8이 열거를 실제로 대체함을 확인 |
| **B10** | `captures/external/*`를 가진 **합성 빌드** 재동결 | 그 파일이 고아로 온존 · 배너 보고 |

B1~B4·B6~B7·B10은 A8 **사본** 또는 합성 픽스처에서만 수행한다.

## 11. 계획 초안 (Task 8)

| Task | 내용 |
|---|---|
| T1 | `scripts/refreeze.py`(begin/check/commit/abort · journal · swap-plan · 고아) + 미러 + 단위 시험 |
| T2 | `evidence_debt{,_hook}.py` 중단 감지(ready 게이트 밖) + 부채 문구 정렬 + 미러 + 시험 |
| T3 | `backstop.py` 잔존 감지 + 미러 + 픽스처 |
| T4 | `archive_design.py` compare 제거 · `check_design_evidence.py` `carried_from` 제거 + 미러 + 시험 정리 |
| T5 | **`web_refreeze_contract.py` + `verify-web` 배선 먼저 만든다** — 그 다음 규범을 고쳐 D1~D4를 green으로 만든다(열거가 아니라 검사기가 완전성을 정의하도록) |
| T6 | 규범 — `commands` 재동결 절·`:144`·`:227`·`<대상 폴더>` 정의·치환 + Codex `SKILL.md` 의미 미러 |
| T7 | reference — `design-acquisition.md` §2 재작성·`BUILD`→`TARGET` · `design-evidence.md` 절 재작성 · `agents` · `REQUEST_GUIDE` + byte 미러 |
| T8 | 행동 시험 B1~B10 · `make verify` · 릴리즈 게이트 보고 |

**T5를 T6·T7보다 먼저** 두는 것이 이번 판형의 핵심이다 — 검사기가 먼저 서면 규범 편집의 완전성을
사람이 보증하지 않아도 된다. 작업 트리 그대로(브랜치 금지) · 커밋은 최종 승인 뒤 한 번.

**범위 고지**: v1 «신규 도구 0 · Task 3~4» → v5 **신규 2종 · 기존 5종 수정 · 규범 6파일 + 미러 ·
Task 8**. 적대 검토 5기가 «파괴적 구간을 산문 규율에 맡기면 샌다»와 «손으로 만든 편집 목록은
샌다»를 반복 실증했다. 수리 1보다 크다.

## 12. 누적 적대 검토 반영 대조

### rv-C (v4 폐쇄 확인)

| id | 반영 |
|---|---|
| N-B1 `commands:146` 입력 게이트가 목록 밖 | **수용** — §4.5 명시 + §8-D1이 `--build`를 대상에 포함 |
| N-B2 `design-acquisition`은 `BUILD`를 쓰고 archive 인자는 `:27` | **수용** — §4.3에 자리표시자 2종 명시·`BUILD`→`TARGET` · §8-D1이 두 문서 모두 검사 |
| N-B3 `scope.md` 쓰기가 무수식 리터럴 | **수용** — §3-2 수식 의무 + §8-D3 |
| N-B4 여집합이 `captures/external/*`를 파괴 | **수용** — §2.1 포인터 기반으로 환원 · §2.2 고아 보고 · 행동 시험 B10 |
| MAJOR `<대상 폴더>` 미정의 | **수용** — §4.3에 정의 위치 + §8-D4 |
| MAJOR `:142`의 motion-notes까지 치환 | **수용** — §4.3 치환 제외 ② + §8-D2 |
| MAJOR journal `has_render_audit` 내리는 주체 | **수용** — §4.1 `check --render-audit-skipped` |
| M-6 폐쇄 확인(코드) | 반영 불필요 — §6 R7에 근거 인용 |

### rv-A · rv-B · rv-R · rv-F

v2~v5에 걸쳐 전건 반영. 각 판형의 대조표는 git 이력
`e42263c1`(v2) · `d104571f`(v3) · `6653fffb`(v4) 참조.
