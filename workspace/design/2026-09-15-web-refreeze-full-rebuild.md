# 설계 v2 — 재동결 = 전량 폐기 후 재동결 (2026-09-15)

진단: `workspace/eval/web-refreeze-completeness/diagnosis.md` (커밋 `10faaff2`)
적대 검토: `workspace/eval/web-refreeze-completeness/design-review/rv-A.md`(규범 정합성 · BLOCKER 5·MAJOR 6·MINOR 4) ·
`rv-B.md`(실행·안전 · BLOCKER 4·MAJOR 2·MINOR 3) — 반영 대조는 §6.
선행 수리: 증거 부채 hook(v1.1.14) · `workspace/design/2026-09-15-web-evidence-debt-hook.md`

> **v1 → v2의 핵심 변경**: 실행 방식을 «기존 동결물을 먼저 치우고 재수집»(v1)에서
> **«staging에 전량 새로 동결한 뒤 원자 교체»**(v2)로 바꿨다. 적대 검토 BLOCKER 9건 중
> 6건이 «치우는 동안 live가 불완전해서» 생긴 문제였고, 순서를 뒤집으면 구조적으로 사라진다.
> 사용자 정의(«완벽하게 삭제하고 다시 동결»)는 교체 시점에 그대로 성립한다.

## 0. 목표와 비목표

**목표** — 사용자 확정 정의를 규범으로 만든다:

> «차이점을 알 필요도 없어. 재동결은 기존에 동결한 파일을 **완벽하게 삭제하고 다시 동결**하는 걸로 해» (2026-09-15)

재동결은 대상 빌드의 **시안 동결물을 전량 새로 만들어 기존 것을 통째로 대체**한다.
기존 동결물과의 대조는 하지 않는다. 그 결과 조작 상태·렌더 실측도 항상 새로 수집되며,
진단의 G-A(축 비대칭)·G-B(요청 자체 기각)·G-C(부채 결정 대리)가 닫힌다.

**비목표**
- 축별 차이 보고(`refreeze-diff.json`)·조작 상태 대조기 — **만들지 않는다**(사용자 기각).
- 보더 잘림(`workspace/eval/web-scroll-clip-fidelity/diagnosis.md` 수리 2·3) — 별건·후순위.
- 백엔드 계약(`openapi-full.json`·`server-contract`) 재동결 — **별도 축**. 새 정의는 시안 축에만 적용한다(rv-A M5).
- 고아 이미지 청소 — `web/static/images/`에 남는 미참조 파일은 이번 범위 밖(§4 우회 2).

## 1. 정의

**재동결** = ① staging에 시안 동결물 **전량**을 처음부터 새로 만든다 → ② 완전성·입력 게이트를
staging에서 통과시킨다 → ③ 기존 동결물을 통째로 지우고 staging 산출물로 **원자 교체**한다.

- 재동결은 **사용자가 요청했을 때만** 실행한다(자동 staleness 감지 없음 — 현행 유지).
- 요청이 있으면 **항상 전량 재실행한다** — 직전 결과 재사용·«이번 세션에 이미 했음» 판단으로
  생략하지 않는다(G-B). 같은 세션에서 두 번 요청받으면 두 번 다 실행한다.
- **재동결의 끝 = `--phase inputs` exit 0으로 `design_status=ready` 복귀까지**다(rv-A M1 경계 확정).
  수집만 끝내고 중단하지 않는다 — 그 상태는 `backstop`이 프로젝트 전체를 막는다(rv-A M2).

## 2. 구성요소

### R1 폐기 집합 — 파일명이 아니라 **포인터**로 정한다

`captures/`에는 원본 증거와 **구현 증거가 함께 산다**(A8 실측: `*-original.png` 11 ·
`*-impl.png` 16 · 관찰/trace 문서 24). 접미 관례(`-original`/`-impl`)는 어디에도 성문화돼
있지 않으므로 파일명으로 가르지 않는다(rv-A B1).

**폐기 집합 S** = 다음 포인터가 가리키는 파일의 합집합 + 고정 산출물:

| 출처 | 항목 |
|---|---|
| `design-input.json` 각 case | `reference_capture.path` · `source_observation.path` |
| 위 `source_observation` 문서 내부 | `capture.path` · `trace.path` · (v2면) `interactions.path` |
| 고정 | `design-ref/**` · `source-manifest.json` · `design-tokens.json` · `asset-manifest.json` · `screen-meta.json` · `render-audit.json` · `design-input.json` · `coverage-review.md` |

**보존**:

| 대상 | 이유 |
|---|---|
| `scope.md` | 사용자 요구·승인 원문·확정 이탈. 포인터·`approval_quote` 대조의 기준 |
| `build-state.json` | 결정 기록(R4가 키만 갱신) |
| `design-spec.md` | architect 산출 |
| `visual-check.md` | 검증 기록 판형 — 해당 절만 갱신 |
| `visual-evidence.json`과 그것이 가리키는 `captures/*` | **구현 증거** — 재동결이 만들지 않는다. 지우면 dangling(rv-A B1) |
| `motion-notes.md` | **폐기하지 않는다** — `check_motion_spec.py:360-366`의 양방향 m-id 전수성이 보존된 `design-spec.md`와 묶여 있어, 재기록하면 id 집합이 어긋나 red가 된다(rv-A B4). 재기록은 architect 반송을 동반해야 하므로 이번 범위 밖 |
| `<screen>-declared.json` | **빌드 루트에 있고 드라이버의 입력이지 산출이 아니다**(`commands:143` `--declared`). 폐기하면 매 재동결마다 소스 검토를 처음부터 다시 해야 한다(rv-A M6) |
| `openapi-full.json` · `server-contract*` · `contract-paths.txt` | 백엔드 계약 축 |
| S에 없는 `captures/*` | 스모크 캡처·비390 뷰포트 구현 캡처 등. 새 `design-input.json`이 가리키지 않으므로 무해 |

### R2 실행 — staging 우선, 원자 교체

도구 `dddjango-web/scripts/refreeze.py`(신설 · Codex byte 미러)가 파괴적 구간을 결정적으로 집행한다.
Coordinator 산문이 포인터 순회·원장·교체를 맡으면 새는 것이 이번 진단의 원인이다.

```
refreeze.py begin  --build <BUILD> --project-root <ROOT>
refreeze.py check  --build <BUILD>
refreeze.py commit --build <BUILD>
refreeze.py abort  --build <BUILD>
```

1. **`begin`** — `<BUILD>/_refreeze-<ts>/`를 만들고 `scope.md`를 복사한다(staging에서 포인터·
   `approval_quote` 해소가 되도록). `<ROOT>/web/static/images/`의 현재 파일 목록을 원장
   `_refreeze-<ts>/journal.json`에 기록한다(`started_at` · `images_before` · `build_state_design_keys`).
   **live 동결물은 이 시점에 손대지 않는다.**
2. **재수집** — Phase 0 step 5의 동결 절차를 **staging 대상**으로 실행한다
   (`--out <BUILD>/_refreeze-<ts>/design-ref` · `--manifest …/source-manifest.json` ·
   드라이버·렌더 실측 산출도 staging 안). 이미지 도구(`extract_dc.py`·`fetch_images.py`)의
   `--assets-root`는 실제 프로젝트 루트이므로 **`web/static/images/`에는 실제로 쓴다** — R3 참조.
3. **`check`** — staging 완전성을 검사한다(`--phase prepare`가 보지 않는 축을 여기서 본다):
   `design-ref/`·`source-manifest.json`·`design-tokens.json`·`asset-manifest.json`·
   `screen-meta.json`·`design-input.json`·`render-audit.json`(`has_render_audit`이면) 실재 +
   `design-input.json`의 모든 case 포인터 해소 + archive 원본이면 case마다 v2 관찰 실재.
   exit 0 = 완전 · exit 3 = 미완(누락 목록 출력) · exit 1 = 오류.
4. **입력 게이트** — staging을 대상으로 `check_design_evidence.py --build <BUILD>/_refreeze-<ts>
   --phase prepare` → 독립 검토(`coverage-review.md` staging에 보존) → `--phase inputs` exit 0.
   **prepare exit 2는 실패가 아니라 `commands:143`의 보완 루프 진입**이다(rv-A B2·rv-B B2) —
   live가 무손상이므로 보완·재실행을 몇 번이든 staging에서 반복할 수 있다.
5. **`commit`** — 원자 교체: ① R1의 폐기 집합 S를 `_prev-<ts>/`로 이동 ② staging 산출물을
   live 경로로 이동 ③ `build-state.json` 키 갱신(R4) ④ `_prev-<ts>`와 staging 삭제.
   교체 자체는 파일 이동뿐이라 수초 안에 끝난다.
6. **`abort`** — staging 삭제 + `journal.json`의 `images_before`에 없는 신규 이미지 파일 제거.
   live는 처음부터 손대지 않았으므로 복원할 것이 없다.

**«완벽하게 삭제»의 성립 지점**: 5-①. 그 순간 기존 동결물은 전부 사라지고 새것으로 바뀐다.

### R3 이미지 축 — 재동결은 구현 트리에 **쓴다**

v1의 «구현 트리 무접촉» 전제는 틀렸다(rv-B B1). `fetch_images.py:35,110`이
`<ROOT>/web/static/images/`에 내용 해시 파일명(`{token}_{sha12}.{ext}`)으로 바이트를 쓴다.

- 같은 이미지면 파일명이 같아 **무동작**(멱등).
- 바뀐 이미지면 **새 파일이 추가**되고 옛 파일은 남는다(콘텐츠 주소라 덮어쓰지 않는다).
- 따라서 롤백 대상은 «이번 시도에서 새로 생긴 파일»뿐이고, `journal.json.images_before`와의
  차집합으로 결정적으로 구한다(`abort`가 집행 — rv-B M1의 원장 요구를 이 축에 한정해 충족).
- 미참조가 된 옛 이미지 청소는 범위 밖(§4 우회 2).

### R4 재동결 후 상태 전이

| 키 | 값 | 근거 |
|---|---|---|
| `design_status` | 교체 전 `blocked` → inputs exit 0 후 **`ready`** (같은 라운드에서 복귀) | `commands:144` · rv-A M2(ready 아니면 프로젝트 전체 backstop red) |
| `implementation_visual` | 완료 빌드였으면 **`pending`** | 구현 증거가 옛 동결 기준이다. 새 값을 만들지 않는다(스키마의 기존 4값 사용 — rv-A M2가 지적한 «아무도 안 읽는 키» 회피) |
| `evidence_debt` | **키 제거** — 단 `evidence_debt.build_debt()`가 «부채 없음»을 낼 때만 | rv-A m4(정확 필드 집합을 만족해야 `ok`) |
| `g2_approved` | 유지(되돌리지 않는다) | 재동결은 G2 승인 사실을 지우지 않는다. 재대조 필요는 `implementation_visual`이 표현 |

**완료 빌드를 재동결하면 G2 재대조 전까지 마무리 backstop이 막힌다** — `validate_visual`이
`input_digest: stale`을 내기 때문이다(rv-A M2). 이는 정직한 신호이므로 수용하고, **G0 배너에
«이 재동결은 G2 재대조를 요구한다» 1줄을 의무화**한다. 재동결 요청 자체가 그 비용의 승인이다.

### R5 부채 결정 게이트 정렬 — 재동결 = ⓐ 경로

v1의 «재동결엔 결정을 붙이지 않는다»는 hook 주입 문구와 정면 모순이었다(rv-A B3).
게이트를 없애는 대신 **의미를 정렬**한다:

- 재동결은 조작 상태를 항상 새로 수집하므로 **부채를 해소하는 실행**이다 → ⓐ 경로.
- 따라서 ⓑ defer가 허용하는 것에서 **재동결을 뺀다**: defer = 조회·보고 + 완료 빌드의
  G2 승인·마무리 backstop.
- 사용자가 재동결을 요청하면 그 발화가 곧 ⓐ 결정의 `quote`다 — Coordinator가 대신 고르는
  상황이 사라진다(G-C 해소).
- 문구를 고칠 곳(전부 byte 미러 동반): `evidence_debt_hook.py`의 `DECISION_LINE`(:36-40)과
  undecided 줄(:132) · `REQUEST_GUIDE.md:115-116` · `commands:129` · Codex `SKILL.md:151`.

### R6 제거 대상 (전수 — rv-A M4 반영)

| 위치 | 제거·수정 |
|---|---|
| `scripts/archive_design.py` (+미러) | `--compare-build` · `--compare-out` · `--carried` · `compare_manifests()` · exit 3/4 · `_history` 자동 carried 판정 |
| `scripts/test/test_design_archive.py` (+미러) | `RefreezeCompareTests` 10건(잔여 32건이 비-compare 기능을 계속 덮음 — rv-B 확인) |
| `scripts/check_design_evidence.py` (+미러) | `carried_from` 행 필드 수용(`:1139,1142-1143`) |
| `commands/dddjango-web.md` (+Codex `SKILL.md` 의미 미러) | 재동결 출현 12곳 전수: `:9 :70 :129 :130 :134 :137 :146 :154 :171 :205 :227 :234` (Codex `:8 :123 :151 :152 :156 :159 :169 :177 :194 :228 :250 :258`). `:227`은 백엔드 축이므로 «openapi 재동결»로 어휘를 분리(M5) |
| `references/design-acquisition.md` (+byte 미러) | §2 «재동결» 전면 재작성 |
| `references/design-evidence.md` (+byte 미러) | `:27`·`:115`(`carried_from`)·`:338`·`:342` |
| `agents/design-review-web.md` (+Codex 역할 SKILL) | `:25` 감사 목록의 `carried` |
| `REQUEST_GUIDE.md` (+byte 미러) | `:115-116` 부채 문구(R5) |
| `scripts/test/test_evidence_debt{,_hook}.py` (+미러) | defer 픽스처 quote의 «재동결만» 전제 |

`refreeze-diff.json`·`build-state.refreeze` 키는 사라진다. 기존 폴더에 남은 것(A8은 `refreeze`
외에 `refreeze_v3/_v4/_v5`도 있다 — rv-A m2)은 **무시된다**: 검사기는 선언된 포인터만 읽고
build-state 미지 키 금지 검사가 없다(rv-A가 코드로 확인).

### R7 중단 감지 — hook 확장

staging 방식이라 중단돼도 live는 온전하다(rv-B B4 해소). 남는 위험은 **staging 잔존**이다
(rv-B B3: 잔존을 감지할 결정적 장치가 없고 `commands:171`이 «있는 것 전부»를 커밋한다).

- `evidence_debt.py`/`evidence_debt_hook.py`에 1줄 추가: 빌드 폴더에 `_refreeze-*` 또는
  `_prev-*`가 있으면 `[dddjango-web] interrupted refreeze — <폴더>: staging left behind ·
  run refreeze.py abort or commit before any other work`를 낸다.
- 이 판정은 `design-input.json` 유무와 **무관**해야 한다(현행 `_builds()`는 그것을 요구한다).

### R8 `interaction_exclusions` 이월 절차 (rv-A B5)

예외 행은 폐기되는 `design-input.json`에만 살고, prepare가 그 행이 없으면 잔여를 결함으로 낸다.
`scope.md`(보존)의 승인 원문은 살아남지만 행 자체는 기계적으로 이월되지 않는다.

- `begin`이 기존 `design-input.json.interaction_exclusions`를 `journal.json`에 보존한다.
- 재수집 후 Coordinator가 **새 관찰 문서의 target id 기준으로 행을 다시 짓는다** —
  `approval_quote`·`scope_ref`는 보존된 `scope.md`에서 그대로 재사용하고, 단위 키
  (`target`·`action`·`option`)만 새 id에 맞춘다. 10% 상한은 새 분모로 재검증한다.
- 새 관찰에서 대응 단위를 못 찾은 행은 **버리지 않고** 배너에 올려 사용자 확인을 받는다
  (승인이 사라진 게 아니라 대상이 사라진 것일 수 있다).

## 3. 행동 시험

| id | 시나리오 | 합격 조건 |
|---|---|---|
| B1 | A8 **사본**에서 «재동결» 발화 | staging에 전 축 생성 → `check` exit 0 → inputs exit 0 → `commit` 후 `design-ref`·`captures`의 원본 증거·`render-audit.json`·`design-input.json`이 전부 새 바이트 · `visual-evidence.json`이 가리키는 `*-impl.png` **전부 온존** · `_refreeze-*`·`_prev-*` 잔존 0 · `design_status=ready` |
| B2 | 실패 주입 — **`observe_interactions.mjs` 3번째 case에서 브라우저 실행 실패**(주입 지점 특정: 드라이버 호출 직전 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`을 부재 경로로 치환) | `abort` 후 live 동결물이 **바이트 동일**(재동결 전 sha 목록과 대조) · `web/static/images/` 파일 목록이 `images_before`와 동일 · staging 잔존 0 |
| B3 | B1 직후 hook 발화 | 그 폴더가 부채 목록에 없고 **`design_status=ready`인 상태에서** 그렇다(빌드가 평가 대상에서 빠져서가 아님을 확인 — rv-A M3) |
| B4 | staging 잔존 상태에서 hook 발화 | `interrupted refreeze` 줄이 나온다(R7) |
| B5 | `interaction_exclusions` 1행을 가진 **합성 빌드**에서 재동결 | 새 `design-input.json`에 행이 재작성되고 prepare가 exit 0 (A8엔 예외가 0이라 B1으로는 안 드러남 — rv-A B5) |
| B6 | 같은 세션 두 번 요청 | 두 번 다 전량 재실행 |
| B7 | 잔존 참조 grep | 정본·미러·테스트에서 `compare-build`·`carried_from`·`refreeze-diff`·`build-state`의 `refreeze*` 키 언급 0 |

B1·B2·B5는 A8 **사본**(또는 합성 픽스처)에서만 수행한다 — A8 본체는 최종 테스트 베드다.

## 4. 남는 우회 (명시)

1. **시안 자산 staleness의 침묵** — 시안 이미지가 바뀌면 새 해시 파일이 추가되고
   `asset-manifest.json`이 그것을 가리키지만, 구현 템플릿이 옛 경로를 계속 쓰면 재동결만으로는
   드러나지 않는다. G2 재대조에서 드러난다(R4가 `implementation_visual=pending`으로 강제).
2. **고아 이미지** — 더 이상 참조되지 않는 옛 이미지는 `web/static/images/`에 남는다. 청소 도구 없음.
3. **전량 재수집 비용** — 매 재동결이 드라이버를 통째로 돌린다(A8 12 case 기준 수십 분).
4. **`motion-notes.md`는 재기록하지 않는다**(R1) — 시안의 동적 표현이 바뀌어도 재동결이
   갱신하지 않는다. m-id 전수성 때문이며, 갱신은 architect 반송을 동반하는 별건이다.
5. **`_history/`** — 이 수리는 손대지 않는다. `compare_manifests()` 제거로 그것을 아는 코드는
   0이 되고, 실재하는 `_history/vN`은 그대로 남는다(rv-A m1).

## 5. 계획 초안 (Task 6)

| Task | 내용 |
|---|---|
| T1 | `scripts/refreeze.py` 신설(begin/check/commit/abort) + Codex byte 미러 + 단위 시험 |
| T2 | `evidence_debt{,_hook}.py` 중단 감지 1줄(R7) + 미러 + 시험 · 부채 문구 정렬(R5) |
| T3 | `archive_design.py` compare 경로 제거 + `check_design_evidence.py` `carried_from` 제거 + 미러 + 시험 정리(R6) |
| T4 | 규범 — `commands/dddjango-web.md` 12곳 + Codex `SKILL.md` 의미 미러(R1~R8) |
| T5 | reference·문서 — `design-acquisition.md` §2 · `design-evidence.md` 4곳 · `agents/design-review-web.md` · `REQUEST_GUIDE.md` + byte 미러 |
| T6 | 행동 시험 B1~B7 · `make verify` · 릴리즈 게이트 보고 |

작업 트리 그대로 진행하고(브랜치 금지 — web 관례) 커밋은 최종 승인 뒤 한 번.

**범위 변경 고지**: v1은 «신규 도구 0 · Task 3~4»였다. 적대 검토가 파괴적 구간을 산문 규율에
맡기는 위험(rv-B B1·B3·M1)을 실증해, **신규 스크립트 1종(`refreeze.py`)**을 들인다.
Task 6 · 수리 1과 비슷한 규모다. 이 변경은 사용자 승인 게이트(계획 리뷰 후)에서 보고한다.

## 6. 적대 검토 반영 대조

### rv-A (규범 정합성)

| id | 반영 |
|---|---|
| B1 `captures/**` 전량 폐기가 구현 증거를 끊는다 | **수용** — R1을 포인터 기반 폐기 집합으로 재정의. A8 실측으로 재확인(원본 11·구현 16·문서 24 혼재) |
| B2 prepare exit 0 = 성공이 보완 루프를 지운다 | **수용** — R2-3/4 분리. 완전성은 `refreeze.py check`, 게이트는 staging에서 보완 루프 허용 |
| B3 부채 게이트에서 재동결 제외가 hook과 모순 | **수용** — R5. 게이트를 없애지 않고 «재동결 = ⓐ»로 정렬, 문구 5곳 동시 수정 |
| B4 motion-notes 재기록이 m-id 전수성을 깬다 | **수용** — R1에서 보존으로 이동, §4 우회 4로 명시 |
| B5 `interaction_exclusions` 이월 절차 부재 | **수용** — R8 신설 + 행동 시험 B5(합성 픽스처) |
| M1 «재동결의 끝»이 절마다 다르다 | **수용** — §1에서 «inputs exit 0 = ready 복귀»로 확정 |
| M2 `visual_gate` 키는 무소비 · 실제 파급은 backstop | **수용** — 새 키 폐기, 기존 `implementation_visual=pending` 사용. 프로젝트 전체 차단을 §R4에서 명시 수용 + 배너 의무 |
| M3 blocked가 폴더를 hook 시야에서 지운다 | **수용** — B3 합격 조건에 «ready 상태에서» 추가 |
| M4 제거 목록 누락 8곳 | **수용** — R6을 전수 표로 교체 |
| M5 «재동결»이 openapi 축까지 덮는다 | **수용** — §0 비목표 + R6에서 `:227` 어휘 분리 |
| M6 `declared.json` 위치·주체 오류 | **수용** — R1 보존으로 이동(빌드 루트·드라이버 입력) |
| m1 `_prev` vs 기존 `_history` | **부분** — §4 우회 5로 명시. 이름은 `_refreeze-*`/`_prev-*` 유지 |
| m2 B4 grep 어휘가 실제 키를 못 잡는다 | **수용** — B7에 `refreeze*` 키·`carried_from` 추가 |
| m3 `_prev` 중 `legacy_v1_allowed` 닫힘 | **수용** — staging 방식이라 창이 «교체 수초»로 축소. R2-5 |
| m4 `evidence_debt` 키 제거 시점 | **수용** — R4에서 `build_debt()==부채 없음` 확인 뒤로 묶음 |

### rv-B (실행·안전)

| id | 반영 |
|---|---|
| B1 재동결이 구현 트리에 실제로 쓴다 | **수용** — R3 신설(멱등·추가만·`journal.json` 차집합 롤백). §0 비목표에서 «구현 트리 무접촉» 삭제 |
| B2 prepare가 render-audit·motion-notes·tokens·asset-manifest를 안 본다 | **수용** — `refreeze.py check`가 그 축의 실재를 본다(R2-3). motion-notes는 폐기 대상에서 빠져 해당 없음 |
| B3 staging 잔존을 감지할 장치가 없다 | **수용** — R7 hook 확장 + 행동 시험 B4 |
| B4 중단 시 hook이 빌드를 놓친다 | **구조적 해소** — live가 항상 온전하므로 `design-input.json`이 사라지는 창이 없다. R7이 추가 안전망 |
| M1 «이번 시도 신규 파일» 원장 부재 | **수용** — staging 방식이라 신규 산출물 = staging 전체. 원장은 이미지 축에만 필요(R3) |
| M2 B2 시험의 주입 지점 불특정 | **수용** — §3 B2에 주입 지점·방법 명시 |
| N1 backstop 메시지가 복구를 안 가리킨다 | **부분** — R7의 hook 줄이 처방을 낸다. backstop 메시지는 수정하지 않는다(경로가 넓다) |
| N2 `<BUILD>` 밖 사전 스테이징 잔재 | **수용** — `abort`/`commit`이 자신이 만든 staging만 지운다는 한계를 §4에 두지 않고, Coordinator가 scratchpad를 정리하는 기존 규율(`commands:137`)을 따른다 |
| N3 Codex byte-parity 미확인 | **위임** — `make verify`의 `diff -rq`·`cmp`가 대조(Makefile:96·98-104) |
