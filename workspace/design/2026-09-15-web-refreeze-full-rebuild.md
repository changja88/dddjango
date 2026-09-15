# 설계 v4 — 재동결 = 전량 폐기 후 재동결 (2026-09-15)

진단: `workspace/eval/web-refreeze-completeness/diagnosis.md` (커밋 `10faaff2`)
적대 검토 4기: `design-review/rv-A.md`(규범 정합) · `rv-B.md`(실행·안전) · `rv-R.md`(v2 재검토) ·
`rv-F.md`(v3 최종) — 누적 반영 대조는 §11.

> **판형 이력**
> v1 «선폐기 → 재수집» → BLOCKER 9(치우는 동안 live가 불완전).
> v2 «staging 우선 → 원자 교체» → 구조는 코드로 성립(rv-R §A), 교체 단계·`scope.md` 미명세 → BLOCKER 2.
> v3 «재개 가능 트랜잭션» → 트랜잭션·scope 해법은 검사기 4축 성립 확인(rv-F ①), 그러나
> **편집 대상 목록이 «재동결» 어휘로 만들어져 인자 리터럴 줄을 비껴감** → BLOCKER 2.
> **v4는 경로 치환을 규범 어휘(`<대상 폴더>`)로 일반화하고, 폐기 집합을 여집합 정의로 바꾼다.**

## 0. 목표와 비목표

**목표** — 사용자 확정 정의를 규범으로 만든다:

> «차이점을 알 필요도 없어. 재동결은 기존에 동결한 파일을 **완벽하게 삭제하고 다시 동결**하는 걸로 해» (2026-09-15)

**비목표**: 차이 대조·조작 상태 대조기(사용자 기각) · 보더 잘림(수리 2·3) ·
백엔드 계약 재동결(별도 축) · `motion-notes.md` 재기록(§9 우회 4) · 고아 이미지 청소(§9 우회 2).

## 1. 정의

**재동결** = ① staging에 시안 동결물 **전량**을 처음부터 새로 만든다 → ② 완전성·입력 게이트를
staging에서 통과시킨다 → ③ 기존 동결물을 통째로 지우고 staging 산출물로 **교체**한다 →
④ 교체 후 live에서 `--phase inputs` exit 0을 재확인한다. **끝은 ④다.**

- 사용자가 요청했을 때만 실행하고, **요청이 있으면 항상 전량 재실행한다** — 직전 결과 재사용·
  «이번 세션에 이미 했음»으로 생략하지 않는다(G-B). 같은 세션에서 두 번 요청받으면 두 번 다 실행한다.
- **`design_status`는 전 구간 `ready`를 유지한다.** 근거는 «live가 유효하다»가 아니라
  **부채 hook 가시성**이다 — `evidence_debt.py:139-140`이 `ready`가 아닌 폴더를 판정 대상에서
  지우므로, 내리는 순간 재동결 중인 빌드가 hook의 시야에서 사라진다(rv-A M3 · rv-R RM2 · rv-F m-5).
  이를 위해 `commands:144`의 «재기준 승인 직후에도 blocked 유지» 문장을 재작성한다(§8-B).

## 2. 폐기 집합과 보존

### 2.1 `captures/`는 2분류가 아니다 (rv-F M-1)

A8 9개 빌드 실측: 3겹 포인터 순회(S)와 `visual-evidence.json` 포인터의 **어디에도 없는 파일**이
표적 빌드 55 중 7건, 다른 빌드는 최대 270건 존재한다(스모크 캡처·실패 회차 `attempt-1/*` 원본 증거·
`captures/external/*`). v3의 «S에 없는 `captures/*`는 보존»은 그만큼 «완벽하게 삭제»를 거짓으로 만든다.

**v4의 폐기 집합 정의 — 여집합**:

> `captures/**` 중 **`visual-evidence.json`이 가리키지 않는 모든 파일** + 아래 고정 목록.

`visual-evidence.json`이 없으면 보존 집합은 공집합이고 `captures/**` 전량이 폐기된다.
3겹 포인터 순회(case → `reference_capture`·`source_observation` → `capture`·`trace`·`interactions` →
`initial.capture`·`steps[].after.capture`)는 폐기 계산이 아니라 **`check`의 자기 검사**로만 쓴다:
«3겹 포인터가 모두 폐기 집합에 포함되는가»를 확인해 정의의 완전성을 기계로 보증한다.

**고정 폐기·교체 대상**: `design-ref/**` · `source-manifest.json` · `design-tokens.json` ·
`asset-manifest.json` · `screen-meta.json` · `render-audit.json` · `design-input.json` ·
`coverage-review.md` · `scope.md`(§3) · `<screen>-declared.json`·`--excluded-regions` 입력(§4.3) ·
`refreeze-diff.json`(R10이 생성 도구를 지우므로 고아로 남기지 않는다 — rv-F m-2).

**보존**: `build-state.json`(키만 갱신) · `design-spec.md` · `visual-check.md`(절 갱신) ·
`visual-evidence.json`과 그것이 가리키는 `captures/*` · `render-audit-impl.json` · `motion-notes.md` ·
`design-review.md` 등 빌드 산문 · `openapi-full.json`·`server-contract*`·`contract-paths.txt`.
**열거되지 않은 빌드 폴더 파일은 보존이 기본**이다(`captures/**`만 위 여집합 규칙이 우선한다).

## 3. `scope.md`는 교체 대상이다 (rv-R RB1 · rv-F M-3)

규범은 재수집 도중 `scope.md`에 **세 번** 쓰기를 요구한다 — `commands:143`의 실행 경계 기록,
`commands:142`의 렌더 실측 **생략 사유 1줄**, 예외 행의 새 승인 원문(R6). 동시에 `commands:129`가
«scope 바이트가 바뀌면 포인터·review digest가 어긋난다»를 성문화한다. 그래서 staging을 정본으로 삼는다:

1. `begin`이 live `scope.md`를 staging에 복사하고 그 sha를 journal에 기록한다.
2. 재수집 중 위 세 쓰기는 **staging 복사본에만** 한다.
3. **staging 창 동안 live `scope.md`에 쓰는 것을 금지한다.** 금지가 없으면 그 창에 live에 적힌 줄이
   `commit`의 덮어쓰기로 **red 없이 증발한다**(sha는 staging 기준이라 검사기가 못 본다 — rv-F M-3).
4. `commit`은 교체 직전 live `scope.md`가 journal의 `begin` 시점 sha와 같은지 확인하고,
   다르면 **exit 1**로 멈춘다(무성 손실 방지).
5. `commit`이 staging `scope.md`를 live로 옮긴다 — `design-input.json.scope`의 sha가 staging
   기준이므로 교체 후에도 일치한다(rv-F ①이 검사기 4축 전부 성립 확인).
6. **순서**: 독립 검토(`coverage-review.md`)는 `scope.md` 최종 확정 **뒤에** 받는다.
   `reviewed-input` digest가 scope 바이트를 포함하므로 어기면 inputs가 스스로 red를 낸다.

## 4. 실행 — `refreeze.py`

### 4.1 서브커맨드

| 명령 | 인자 | exit |
|---|---|---|
| `begin` | `--build` `--project-root` `--quote <사용자 재동결 발화>` | 0 · 2 선점(기존 staging/`_prev`) · 1 오류 |
| `check` | `--build` `[--staging]` | 0 완전 · 3 미완(누락 목록) · 1 오류 |
| `commit` | `--build` `[--staging]` `[--resume]` | 0 완료 · 3 중단·되감김(재개/재시도 필요) · 1 오류 |
| `abort` | `--build` `[--staging]` | 0 완료 · 1 오류·거부 |

- `--staging` 생략 시 `_refreeze-*`가 **정확히 하나**일 때만 자동 선택, 둘 이상이면 exit 1 + 목록.
- `begin`은 기존 `_refreeze-*`/`_prev-*`를 삭제하지 않고 exit 2로 거부한다.
- **`abort`는 journal에 `completed_at`이 있으면 거부한다**(exit 1) — 완료된 재동결을 파괴하지
  않기 위함이다(rv-F M-4).

### 4.2 journal (`<staging>/journal.json`)

```json
{"version": 1, "build": "<abs>", "project_root": "<abs>", "started_at": "<ISO8601>",
 "completed_at": null,
 "quote": "<사용자 재동결 발화>",
 "discard_set": ["design-ref/index.html", "captures/x-original.png", "…"],
 "scope_sha256_at_begin": "<hex>",
 "has_render_audit": true,
 "images_before": ["web/static/images/<name>", "…"],
 "interaction_exclusions": [ … 기존 행 원문 … ],
 "evidence_debt_before": { … 기존 키 원문 또는 null … },
 "copied_inputs": ["scope.md", "…"]}
```

- `discard_set`은 **파일 단위로 전개**해 기록한다 — 디렉터리 항목을 담지 않는다(rv-F m-3).
- `has_render_audit`은 `begin` 시점 live `build-state.json`에서 읽어 **journal에 고정**한다.
  재수집 중 합법 생략(§6 R7)이 확정되면 journal의 값을 false로 내리고 `check`는 journal을 본다
  (live를 보면 영구 exit 3 — rv-F M-2).
- `evidence_debt_before`는 `abort`가 원상 복구하는 데 쓴다(rv-F M-6).

### 4.3 재수집 — 경로 치환은 규범 어휘로 (rv-F B-1)

v3는 staging/live 분기를 **설계 문서에만** 적었다. Coordinator는 `commands`와 `design-acquisition.md`만
읽으므로 그대로 집행하면 재수집이 live에 쓴다 — 구조 역전 전체가 런타임에 발화하지 않는다.

**해법: 규범에 `<대상 폴더>` 어휘를 도입한다.**

> `<대상 폴더>` = 평시에는 `<산출물 폴더>`, **재동결 중에는 그 빌드의 staging(`_refreeze-<ts>`)**.
> 정의는 재동결 절에 한 번만 두고, 수집 인자 줄은 `<산출물 폴더>`를 `<대상 폴더>`로 바꾼다.
> **`--assets-root`는 치환 대상이 아니다** — 언제나 프로젝트 루트다(이미지는 구현 트리에 쓴다 · §5).

치환이 필요한 줄(전수 — rv-F B-1 실측):
`commands:138`(extract_design) · `:140`(freeze_design·extract_design·fetch_images) ·
`:142`(렌더 실측 출력) · `:143`(observe_interactions `--out`·`--captures-dir`·`--declared`·
`--excluded-regions`) · `:145`(«기존 관례를 유지한다») + `design-acquisition.md` **§1 수집 인자**와
**§3 조작 상태 수집 인자(`:113-125`)**.

**렌더 실측은 «도구»가 아니다**(rv-F ③) — 인자 없는 브라우저 콘솔 스니펫이고 Coordinator가 결과를
받아 파일로 적는다. 따라서 §4.3의 치환은 «적는 경로»에 적용된다.

`begin`이 staging에 복사하는 입력: `scope.md` · `<screen>-declared.json` · `--excluded-regions`
입력(있는 것만). **A8 표적 빌드에는 declared/excluded 입력이 0건**이므로 복사 대상은 `scope.md`
하나뿐이고, 드라이버는 `--declared` 없이 돌며 보완 루프가 선언을 새로 만든다(비용은 §9 우회 8).

### 4.4 `check` — `--phase prepare`가 보지 않는 축

staging에서 다음 **실재**를 확인한다: `design-ref/` · `source-manifest.json` · `design-tokens.json` ·
`asset-manifest.json` · `screen-meta.json` · `design-input.json` · `render-audit.json`
(**journal의 `has_render_audit`이 true일 때만**) + `design-input.json`의 3겹 포인터 해소 +
archive 원본이면 case마다 v2 관찰 실재 + **폐기 집합 자기 검사**(3겹 포인터 ⊆ 폐기 집합 — §2.1).
내용 검증은 하지 않는다(수용된 한계).

### 4.5 입력 게이트

`check` exit 0 뒤 staging 대상으로 `--phase prepare` → 독립 검토 → `--phase inputs` exit 0.
**prepare exit 2는 실패가 아니라 `commands:143`의 보완 루프 진입**이다(rv-A B2). live 빌드 폴더가
무손상이므로 몇 번이든 반복한다.

### 4.6 `commit` — 파일 단위 재개 가능 트랜잭션

`captures/`가 혼재 디렉터리이므로 **디렉터리 이동을 금지**한다. `<BUILD>/_prev-<ts>/swap-plan.json`에
계획을 먼저 쓰고 단계별로 진행한다: `planned → discarded → installed → verified → done`.

1. **planned** — journal의 `discard_set`과 staging 산출물 목록으로 계획을 쓴다.
   같은 단계에서 §3-4의 live `scope.md` sha 대조를 수행한다(불일치면 exit 1).
2. **discarded** — 각 파일을 `_prev-<ts>/`로 이동(경로 구조 보존).
   규칙: src 있음 → 이동 · src 없고 dst 있음 → 건너뜀 · **둘 다 없음 → 오류**(rv-F m-4).
3. **installed** — staging 산출물을 각 파일 live 경로로 이동(`captures/` 병합).
   규칙: **staging 쪽이 있으면 대상 존재와 무관하게 덮어쓴다** · staging 쪽이 없고 live에 있으면
   건너뜀 · 둘 다 없음 → 오류. «건너뛴다»를 두 단계에 같이 적용하면 이름 충돌에서 새 산출물이
   버려져 verified가 sha mismatch로 되감고 resume이 같은 실패를 반복하는 **livelock**이 된다(rv-F M-7).
4. **verified** — `check_design_evidence.py --build <BUILD> --phase inputs` exit 0 확인.
   실패면 계획을 역순으로 되감아 `_prev-<ts>`를 복원하고, **이어서 `abort`와 동일한 이미지 되돌리기**
   (`journal.images_before` 차집합 제거)를 수행한 뒤 exit 3(rv-F M-5). 빌드 폴더만 되감고 끝내면
   구현 트리가 오염된 채 남아 backstop이 red를 낸다.
5. **done** — `build-state.json` 키 갱신(R7) → **journal에 `completed_at` 기록** →
   staging 삭제 → `_prev-<ts>` 삭제. 순서를 이 방향으로 고정해 «`_prev`가 먼저 사라져 `abort`가
   성공한 재동결을 파괴하는» 창을 없앤다(rv-F M-4).

## 5. 이미지 축 — 재동결은 구현 트리에 쓴다

`fetch_images.py:35,110`이 `<ROOT>/web/static/images/`에 내용 해시 파일명으로 쓴다.

- 소스명이 있는 이미지는 멱등이지만 **인라인(`data:`)은 아니다** — 토큰이 문서 내 순번이라
  이미지가 하나 추가·삭제되면 이후 토큰이 밀려 같은 바이트가 새 파일명으로 떨어진다(rv-R m-1).
- «live 무손상»은 **빌드 폴더에 한한다**. 이미지가 추가되는 순간 완료 빌드의
  `implementation_digest`가 stale이 되어 다른 작업의 backstop이 `[DESIGN] BLOCKER`를 낸다.
- 따라서 **실패 시 `abort`(또는 `commit`의 verified 실패 경로)는 의무**이고, 둘 다 같은
  `images_before` 차집합 제거를 수행한다.
- 재동결 중 같은 프로젝트의 **병행 실행을 금지한다** — 차집합 롤백이 남의 파일을 지울 수 있다.

## 6. 부수 규정

### R6 `interaction_exclusions` 이월

`begin`이 기존 행을 journal에 보존한다. 재수집 후 Coordinator가 **새 관찰 문서의 target id 기준으로
행을 다시 짓는다** — `approval_quote`·`scope_ref`는 staging `scope.md`에서 재사용하고 단위 키만
새 id에 맞춘다. 10% 상한은 새 분모로 재검증한다. 대응 단위를 못 찾은 행은 버리지 않고 배너에 올려
사용자 확인을 받는다.

### R7 상태 전이 — **쓰는 주체를 명시**

| 키 | 값 | 쓰는 주체 |
|---|---|---|
| `design_status` | `ready` 유지 | 아무도 안 쓴다(§1) |
| `evidence_debt` | `{decision:"observe", quote:<journal.quote>, at, reason:"재동결 = 조작 상태 전량 재수집", cases:<현재 부채 수>}` — 기존 키가 `defer`여도 덮어쓴다 | **`begin`**(rv-F M-6) |
| `evidence_debt` | `build_debt()`가 부채 없음을 내면 **키 제거** | `commit` done |
| `evidence_debt` | journal의 `evidence_debt_before`로 복원 | `abort`·verified 실패 되감기 |
| `implementation_visual` | 완료 빌드였으면 `pending` | `commit` done |
| `has_render_audit` | 재측정이 `commands:142`의 enum 사유로 합법 생략되면 `false`(사유는 staging `scope.md` 1줄) | `commit` done(journal 값 반영 · rv-F M-2) |
| `g2_approved` | 유지 | — |

`begin`이 `evidence_debt`를 쓰지 않으면, 부채가 있는 빌드를 재동결하는 내내 live design-input이
옛 static-only 그대로라 hook이 **매 프롬프트마다** «decision required before any run» 배너를 낸다 —
진행 중인 재동결을 금지하는 문구로(rv-F M-6).

완료 빌드를 재동결하면 G2 재대조 전까지 마무리 backstop이 막힌다. **G0 배너에 «이 재동결은 G2
재대조를 요구한다» 1줄을 의무화**한다.

### R8 부채 결정 게이트 정렬 — 재동결 = ⓐ 경로

ⓑ defer가 허용하는 것에서 **재동결을 뺀다**(= 조회·보고 + 완료 빌드의 G2 승인·마무리 backstop).
사용자가 재동결을 요청하면 그 발화가 `begin --quote`로 들어가 ⓐ 결정의 `quote`가 된다.
고칠 곳: `evidence_debt_hook.py:36-40`·`:132` · `REQUEST_GUIDE.md:115-116` · `commands:129` ·
Codex `SKILL.md:151` (전부 미러 동반).

### R9 중단·잔존 감지

- **hook**: 빌드 폴더에 `_refreeze-*`/`_prev-*`가 있으면
  `[dddjango-web] interrupted refreeze — <폴더>: staging left behind · refreeze.py commit --resume (or abort if not completed)`.
  이 판정은 `design-input.json` 유무와 `design_status` ready 게이트 **양쪽 바깥**에서 돌아야 한다 —
  `build_debt()` 안에 넣으면 영원히 발화하지 않는다(rv-R RM2).
- **backstop**: 같은 조건에서 `[DESIGN] BLOCKER interrupted refreeze`. hook은 SessionStart·
  UserPromptSubmit에서만 발화해 `commands:171` ⑤의 같은 턴 커밋 창을 막지 못한다(rv-R RM5).
- **규범**: Phase 2 진입 준비 ⑤ 커밋 **전에** 잔존 없음을 확인한다.

## 7. 제거 대상 (rv-A M4 · rv-R m-3 · rv-F B-1·B-2)

편집 대상 목록을 **어휘 grep이 아니라 기능으로** 만든다.

| 위치 | 제거·수정 |
|---|---|
| `scripts/archive_design.py` (+미러) | `--compare-build`·`--compare-out`·`--carried`·`compare_manifests()`·exit 3/4·`_history` 자동 carried |
| `scripts/test/test_design_archive.py` (+미러) | `RefreezeCompareTests` 10건(잔여 32건이 비-compare 기능을 계속 덮음) |
| `scripts/check_design_evidence.py` (+미러) | `carried_from` 수용(`:1140-1143`) |
| `commands/dddjango-web.md` (+Codex `SKILL.md` 의미 미러) | **①재동결 어휘 12줄** `9 70 129 130 134 137 146 154 171 205 227 234`(`:227`은 «openapi 재동결»로 분리) · **②수집 인자 리터럴 5줄** `138 140 142 143 145`(`<산출물 폴더>`→`<대상 폴더>`) · **③`:144`**(재기준 blocked 유지 → 재동결 절차로 대체 · §1) |
| `references/design-acquisition.md` (+byte 미러) | §2 «재동결» 전면 재작성 · **§1·§3의 수집 인자에 `<대상 폴더>` 적용** |
| `references/design-evidence.md` (+byte 미러) | `carried_from`·exit 체계 — **절 단위 재작성**(행 지정 집행 금지) |
| `agents/design-review-web.md` (+Codex 역할 SKILL) | 감사 목록의 `carried` |
| `REQUEST_GUIDE.md` (+byte 미러) | 부채 문구(R8) |
| `scripts/test/test_evidence_debt{,_hook}.py` (+미러) | defer 픽스처 quote의 «재동결만» 전제 |

## 8. 회귀 그물 (rv-R m-4)

`commands` ↔ Codex `SKILL.md`는 의미 미러라 기계 대조가 없고, 기존 시험에 «defer가 재동결을
허용한다»를 검증하는 단언이 0이다. R8을 한 곳이라도 빠뜨리면 red가 나지 않는다.
→ `workspace/tools/web_refreeze_contract.py` 신설(선례 `web_hooks_contract.py`), `verify-web` 배선:

- **A** 4곳(hook 스크립트·REQUEST_GUIDE·commands·Codex SKILL)의 defer 허용 목록에 «재동결»이 **없음**
- **B** `--compare-build`·`refreeze-diff`·`carried_from` 잔존 0
- **C** `refreeze.py` 4 서브커맨드 실재
- **D** `commands`·`design-acquisition.md`의 수집 인자 줄에 `<산출물 폴더>` 잔존 0(= `<대상 폴더>` 치환 완료)

## 9. 남는 우회 (명시)

1. **시안 자산 staleness의 침묵** — 구현 템플릿이 옛 이미지 경로를 계속 쓰면 재동결만으로는 안 드러난다. G2 재대조에서 드러난다.
2. **고아 이미지** — 미참조가 된 옛 이미지는 남는다. 청소 도구 없음.
3. **전량 재수집 비용** — 매 재동결이 드라이버를 통째로 돌린다(A8 12 case 기준 수십 분).
4. **`motion-notes.md`는 재기록하지 않는다** — m-id 양방향 전수성이 보존된 `design-spec.md`와 묶여 있다.
5. **`legacy_v1_allowed`·`current_nondesign_scope`가 staging 전 구간 닫힌다** — `_refreeze-*`가 untracked이기 때문이다(rv-R m-2). 재동결 중 다른 마무리를 돌릴 이유가 없어 실질 피해는 낮다.
6. **`_history/`** — 손대지 않는다.
7. **`visual-evidence.json`에 등록되지 않은 `captures/` 파일은 사라진다** — 스모크 캡처·실패 회차 잔재·`captures/external/*`. 증거로 등록되지 않은 파일이라 규범상 의미가 없고, 사용자 정의(«완벽하게 삭제»)를 따른 결과다(rv-F M-1).
8. **선언 재작성 비용** — A8 표적 빌드에 `<screen>-declared.json`이 없어 복사할 입력이 `scope.md`뿐이다. 매 재동결마다 보완 루프가 선언을 새로 만든다(rv-F m-1).
9. **디스크** — staging 창 동안 동결물이 2벌 존재한다.

## 10. 행동 시험

| id | 시나리오 | 합격 조건 |
|---|---|---|
| B1 | A8 **사본**에서 «재동결» 발화 | staging 전 축 → `check` 0 → inputs 0 → `commit` done · 원본 증거·`render-audit.json`·`design-input.json`·`scope.md` 새 바이트 · `visual-evidence.json`이 가리키는 `*-impl.png` **전부 온존** · **그 외 `captures/*`는 사라짐**(여집합 정의 확인) · 잔존 0 · `design_status=ready` |
| B2 | 실패 주입 — 드라이버 3번째 case에서 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`을 부재 경로로 치환 | `abort` 후 live 빌드 폴더 **바이트 동일** · `web/static/images/`가 `images_before`와 동일 · `evidence_debt`가 이전 값으로 복원 · 잔존 0 |
| B3 | `commit`을 `discarded`에서 강제 중단 | `commit --resume` 완주 · 중간 상태에서 hook·backstop이 `interrupted refreeze` |
| B4 | `installed` 이름 충돌 주입(폐기 집합 밖 `captures/` 파일과 같은 이름을 staging이 생성) | 덮어쓰기로 통과 · livelock 없음(rv-F M-7) |
| B5 | B1 직후 hook | 부채 목록에 없고 **`design_status=ready`인 상태에서** 그렇다 |
| B6 | `interaction_exclusions` 1행을 가진 **합성 빌드** | 행 재작성 후 inputs exit 0 |
| B7 | `done` 이후 `abort` 시도 | exit 1 거부 · 신규 이미지 온존(rv-F M-4) |
| B8 | `web_refreeze_contract.py` | §8의 A~D green |

B1~B4·B6~B7은 A8 **사본** 또는 합성 픽스처에서만 수행한다.

## 11. 계획 초안 (Task 8)

| Task | 내용 |
|---|---|
| T1 | `scripts/refreeze.py`(begin/check/commit/abort · journal · swap-plan) + 미러 + 단위 시험 |
| T2 | `evidence_debt{,_hook}.py` 중단 감지(ready 게이트 밖) + 부채 문구 정렬 + 미러 + 시험 |
| T3 | `backstop.py` 잔존 감지 + 미러 + 픽스처 |
| T4 | `archive_design.py` compare 제거 · `check_design_evidence.py` `carried_from` 제거 + 미러 + 시험 정리 |
| T5 | 규범 — `commands` ①재동결 12줄 ②인자 5줄 ③`:144` + Codex `SKILL.md` 의미 미러 |
| T6 | reference — `design-acquisition.md` §1·§2·§3 · `design-evidence.md` 절 재작성 · `agents` · `REQUEST_GUIDE` + byte 미러 |
| T7 | `web_refreeze_contract.py` + `verify-web` 배선 |
| T8 | 행동 시험 B1~B8 · `make verify` · 릴리즈 게이트 보고 |

작업 트리 그대로 진행(브랜치 금지 — web 관례) · 커밋은 최종 승인 뒤 한 번.

**범위 고지**: v1 «신규 도구 0 · Task 3~4» → v4 **신규 2종(`refreeze.py`·`web_refreeze_contract.py`) ·
기존 5종 수정 · 규범 6파일 + 미러 · Task 8**. 적대 검토 4기가 «파괴적 구간을 산문 규율에 맡기면
샌다»를 반복 실증했다. 수리 1보다 크다.

## 12. 누적 적대 검토 반영 대조

### rv-F (v3 최종)

| id | 반영 |
|---|---|
| B-1 인자 리터럴 줄이 편집 목록 밖 | **수용** — §4.3 `<대상 폴더>` 어휘 도입 · R7 표에 ②수집 인자 5줄·`design-acquisition` §1·§3 추가 · §8-D 그물 |
| B-2 `commands:144` 충돌 | **수용** — R7 표 ③에 `:144` 추가, §1 근거로 재작성 |
| M-1 제3집합 | **수용** — §2.1 여집합 정의로 교체 · 3겹은 `check` 자기 검사로 강등 · §9 우회 7 고지 |
| M-2 `has_render_audit` 영구 exit 3 | **수용** — journal에 고정·합법 생략 시 false로 내림(R7) |
| M-3 scope 쓰기 주체 3번째·금지 부재 | **수용** — §3에 `commands:142` 추가 · live 쓰기 금지 · `commit` sha 대조 |
| M-4 `done`의 `_prev` 선삭제 창 | **수용** — §4.6-5 삭제 순서 고정 + `completed_at` + `abort` 거부(B7) |
| M-5 verified 실패가 이미지 미되감기 | **수용** — §4.6-4에 이미지 되돌리기 포함·exit 3 |
| M-6 `evidence_debt` 쓰는 주체 부재 | **수용** — R7에서 `begin`이 observe 기록·`abort`가 복원 |
| M-7 installed 멱등이 livelock | **수용** — §4.6-3 단계별 규칙 분리(덮어쓰기) + 행동 시험 B4 |
| m-1 declared 실재 0건 | **수용** — §4.3 말미·§9 우회 8 |
| m-2 인벤토리 미덮음 | **수용** — §2 보존표에 `render-audit-impl.json`·산문 추가, `refreeze-diff.json`은 폐기로 |
| m-3 granularity 불일치 | **수용** — §4.2 «파일 단위 전개» |
| m-4 둘 다 없는 경우 | **수용** — §4.6-2 오류 |
| m-5 §1 근거가 철회된 전제 | **수용** — §1 근거를 hook 가시성으로 교체 |

### rv-A · rv-B · rv-R

rv-A B1~B5·M1~M6·m1~m4 · rv-B B1~B4·M1~M2·N1~N3 · rv-R RB1~RB2·RM1~RM5·m-1~m-6·D-1~D-7 =
v2·v3·v4에 걸쳐 전건 반영(각 판형의 대조표는 git 이력 `e42263c1`·`d104571f` 참조).
rv-A M3(부채 hook 침묵)는 v3에서 «원인 제거»로 적었다가 rv-F B-2가 모순으로 남았음을 지적해
**v4에서 `commands:144` 재작성으로 실제로 닫는다.**
