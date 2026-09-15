# 구현 리뷰 (2026-09-15)

독립 구현 리뷰 — 설계 `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(v5) ·
계획 `workspace/plan/2026-09-15-web-refreeze-full-rebuild.md`(v2) 대비. 설계 결정은 재감사하지 않았다.
실행 기록은 읽지 않았고 코드·규범·실주행 실험으로만 판단했다.

## 판정

**수정 필요 (BLOCKER 3 · MAJOR 6 · MINOR 12)**

`make verify-web` green · `test_refreeze` 24 green · 미러 byte 동일 · B9(치환 누락 주입 → D1 red) 실증 성공.
그러나 **중단된 `commit`의 복구 경로가 동결물을 영구 파괴**하고(실험으로 재현),
**§8이 대체하기로 한 «손으로 만든 편집 목록»이 세 번째로 샌 곳**(`<screen>-declared.json`)을
D1이 못 잡는다. 두 축 모두 이번 판형의 핵심 주장(파괴적 구간은 도구가 집행한다 ·
완전성은 검사기가 정의한다)을 직접 무효화하므로 승인하지 않는다.

## 항목별

### 1. `refreeze.py`의 결함

| 축 | 판정 |
|---|---|
| §2.1 3겹 폐기 집합 | 성립(`refreeze.py:83-139`) — 단 예외를 조용히 삼켜 집합이 줄 수 있다(MAJOR 6) |
| §2.1 고정 폐기 목록 | 성립(`:29-35`) — `<screen>-declared.json`·excluded-regions는 이름 규약 가정(MINOR 3) |
| §2.2 고아 보고 | 성립(`:187-196`·`:372-373`) — 단 `installed` 덮어쓰기가 고아를 백업 없이 지운다(MAJOR 2) |
| §3 scope sha 대조 | 성립(`:471-476`) · `--resume`에서 건너뛰는 것도 옳다 |
| §4.1 인자·exit | 대체로 성립 — `--render-audit-skipped` enum 미검증(MINOR 1) · `--staging` 무검증(MINOR 2) |
| §4.2 journal | 전 필드 성립(`:346-362`) |
| §4.6 트랜잭션 | **파일 단위가 아니라 단계 단위** — 단계 도중 중단에서 무너진다(BLOCKER 1·2) |
| §5 이미지 차집합 | 성립(`:547-551`) · `fetch_images.py:35`가 images만 쓰므로 축은 맞다 |
| R7 상태 전이 주체 | `design_status` 무접촉 ✓ · `evidence_debt` begin/done/abort ✓ · **`has_render_audit`은 begin이 build-state에서 상속해 §4.1의 «유일한 주체»를 깬다**(MAJOR 1) |

ⓐ `commit --resume` — `planned`·`discarded`에서만 이어진다. `installed`·`verified` 직후에는 **영구 exit 1**(BLOCKER 2).
ⓑ `verified` 실패 되감기 — install·discard·이미지·`evidence_debt` 전부 되돌린다 ✓. 단 `installed`가 덮어쓴
비폐기 파일은 백업이 없어 복원되지 않는다(MAJOR 2).
ⓒ `done` 순서 — build-state → `completed_at` → staging → `_prev` ✓(`:564-575`). `completed_at` 가드는
journal이 즉시 삭제돼 실질 도달 불가(MINOR 7) · 두 rmtree 사이 중단은 교착(MINOR 8).
ⓓ `_single()` — 자동 선택·다중 exit 1 ✓(`:207-214`), 그러나 `--staging`은 검증 없이 통과(MINOR 2).
ⓔ 데이터 소실 경로 — **3건 실증**(BLOCKER 1·2 · MAJOR 2). 경로 탈출은 `confined()`가 막고,
심링크는 `rglob`가 디렉터리 심링크를 따라가지 않아 현재는 안전하다.

### 2. `web_refreeze_contract.py`의 검출력

변이 주입 12건을 돌려 실측했다(사본 트리 `scratchpad/mut`, 원본 무수정).

| 변이 | 결과 |
|---|---|
| `<대상 폴더>/design-ref` → `<산출물 폴더>/…` (설계 B9) | **D1 red** ✓ |
| `TARGET/design-ref` → `BUILD/…` | **D1 red** ✓ |
| `<산출물 폴더>/motion-notes.md` → `<대상 폴더>/…` | **D2 red** ✓ |
| `` `<대상 폴더>/scope.md` `` → `` `scope.md` `` | **D3 red** ✓ |
| 「산출물 위치」절의 `<대상 폴더>` 제거 | **D4 red** ✓ |
| `carried_from` 재삽입 | **B red** ✓ |
| `cmd_abort` 제거 | **C red** ✓ |
| `ⓑ defer가 허용하는 것 = 재동결·조회…` | **A red** ✓ |
| `유보는 재동결·조회…`(REQUEST_GUIDE) | **A red** ✓ |
| hook `defer = refreeze, inspection…` | **A red** ✓ |
| **`commands:72` `defer = 재동결·비구현 실행만 허용`** | **green — 거짓 음성**(MAJOR 5) |
| **열거 60자 뒤에 «그리고 재동결» 추가** | **green — 거짓 음성**(MAJOR 5) |
| **`--compare-out`·`--carried`·`compare_manifests()` 재삽입** | **green**(MINOR 4 — §8-B의 문자대로이나 §7 제거 목록에 미달) |

추가로: `DISCARD_NAMES`가 §2.1 고정 목록을 다 옮기지 않아 **현재 규범에 실재하는 위반을 green으로 통과**시킨다(BLOCKER 3).
`_collection_region`·`_definition_lines`의 앵커 문자열이 바뀌면 D1·D3가 **빈 구간 = green**으로 조용히 공전한다(MINOR 5).
`--self-test`는 A·D1·D3·D4만 red를 요구하고 **B·C·D2의 검출력을 시험하지 않는다**(MAJOR 4).

### 3. 규범 텍스트

`commands:138`(재동결 절)은 설계 §1·§2.1·§2.2·§3·§4 절차 전체·§5·R6·R7·R8·R9를 담았다 —
누락 없음. `:38`의 `<대상 폴더>` 정의(D4) · `:146`의 재기준 문장 대체 · `:172` ⑤의 잔존 확인 ·
`:228`의 openapi 재동결 분리 모두 반영됐다. `design-acquisition.md` §1 머리(`:8-10`)에 `TARGET` 정의를 두고
§2를 전면 재작성했으며 §2가 설계 §2.1·§2.2·§3·§4.4·§4.6·§5·R6·R7을 모두 포함한다.

모순·누락 3건:
- **`commands:144`(=Codex `SKILL.md:166`)이 여전히 `<산출물 폴더>/<screen>-declared.json`에 쓰라고 지시**(BLOCKER 3).
- `:144`의 `--out captures/<screen>-<w>x<h>-interactions.json`·`--captures-dir`는 **자리표시자 없는 맨 상대경로**라
  재동결 중 어디에 쓰는지 규범이 말하지 않는다(MINOR 6).
- `:146-147`의 «exit 2는 부족/결함으로 blocked를 유지한다»가 `--build <대상 폴더>` 치환 뒤 staging 게이트에도
  걸려 §1의 «전 구간 ready 유지»와 읽히기에 따라 충돌한다(MINOR 9).

Codex 의미 미러는 **일치한다** — 재동결 절·`<대상 폴더>` 정의·Phase 2 ⑤·부채 결정 문단을 문자열 비교한 결과
플랫폼 변수(`${CLAUDE_PLUGIN_ROOT}`↔`${SKILL_DIR}`)와 호출 방식(Agent↔`spawn_agent`)만 다르고 유사도 0.99~1.00,
변경 hunk 수도 16/16으로 같다. 역할 SKILL(`design-review-web`)의 `carried` 제거도 양쪽에 있다.

### 4. 회귀

배포 트리·`docs/`·`README.md` 전체에 `--compare-build`·`--compare-out`·`--carried`·`compare_manifests`·
`carried_from`·`refreeze-diff` 잔존 **0**(`refreeze.py:32`의 폐기 대상 «명명» 1건 제외 — `DEAD_ALLOWED`가 그것만 허용).
`archive_design.py`는 exit 0/1만 남았고 `datetime`·`hashlib` import도 함께 제거됐다.
`test_design_archive.py`는 42→32건(계획대로 10건 제거)이며 남은 32건이 `archive()`·`archive_files()`·
`archive_dependencies()`를 계속 덮는다(green 확인). `test_interaction_evidence.py`는 이름을 `unknown_field`로 바꾸고
단언을 exit 2로 고쳐 §8-B와 충돌하지 않는다. `check_design_evidence.py`의 `carried_from` 수용 제거 ✓.
hook·backstop의 중단 감지는 `design-input.json` 유무·`design_status` ready 게이트 **양쪽 밖**에서 돌며
(`evidence_debt_hook.py:121-135`·`backstop.py:283-294`), backstop은 `current_nondesign_scope` 생략 경로에서도
`discovered` 전체를 돌아 발화한다 ✓.

### 5. 시험의 질

24건이 설계 축을 대체로 고정한다(3겹·고정 목록·보존·고아·journal 전 필드·선점 2·scope drift 1·
네 경우·되감기·`completed_at` 거부·모호성 1·shell-out 인자). 다만 **«통과하도록 쓴 시험»의 징후가 둘** 있다:

- `test_stop_after_discarded_then_resume`은 재개가 멱등인 **유일한 경계**만 고른다. 같은 방식으로
  `--stop-after installed`/`verified`를 넣으면 red다(BLOCKER 2 — 실측).
- `test_installed_overwrites_name_collision`은 고아 `smoke-login.png`의 **소실을 계약으로 고정**한다.
  덮어쓰기 자체는 설계 B4의 요구지만, 백업이 없어 되감기가 불가능하다는 사실은 어떤 시험도 보지 않는다.

빠진 경로: 단계 **도중** 중단(모든 실전 중단이 여기다) · `_prev`가 있는 상태의 `abort`(`cmd_abort:595-597`
분기가 전혀 안 돌아간다) · `--staging` 명시 인자 · `--render-audit-skipped` 뒤 `done`의 build-state 반영 ·
`collection != archive` 분기 · `has_render_audit=false` 빌드의 begin.

## BLOCKER

**B-1 · 단계 도중 중단 뒤 `abort`가 원본을 영구 삭제한다**
`refreeze.py:521-522`(단계 **끝**에서만 phase 기록) + `:532`·`:537`(되감기를 그 phase로 게이트) + `:544`(rmtree).
`discarded` 도중 중단하면 plan은 아직 `planned`이므로 `_rewind`가 복원 루프를 **건너뛰고** `_prev`를 통째로 지운다.
실패 시나리오(실측): 16건 폐기 중 3번째에서 중단 → `abort` **exit 0** + «live 빌드 폴더와 이미지가 재동결 이전
상태다» 출력 → `asset-manifest.json`·`captures/screen-initial.png` **영구 소실**, 사용자에게는 성공으로 보고.
R9가 사용자에게 지시하는 복구 명령이 바로 이것이고, `commit`은 Bash 상한·Ctrl-C·크래시로 언제든 끊긴다.

**B-2 · `installed` 이후 `commit --resume`이 교착하고 `_prev`의 원본을 새 바이트로 덮는다**
`refreeze.py:489-491`의 건너뛰기 조건이 `planned`을 예외로 두어 재개 때 `:521`이 phase를 **`planned`으로 되돌리고**,
이어서 `discarded`가 재실행되며 **이미 설치된 새 산출물을 `_prev`의 원본 위로 이동**시킨다(`shutil.move` 덮어쓰기).
그 다음 `installed`는 staging에도 live에도 없다며 exit 1 — 재시도해도 같다.
실패 시나리오(실측): `--stop-after installed`·`--stop-after verified` 뒤 `--resume` = **exit 1 고정**,
`_prev/asset-manifest.json`이 **새 바이트**로 바뀌고, 이후 `abort`는 그 새 바이트를 live에 되돌리면서
«재동결 이전 상태다»라고 출력한다 — 원본은 어디에도 남지 않는다.
설계 §4.6의 «파일 단위 재개 가능», §4.1 exit 3의 «`--resume`이 필요한 상태», `commands:138`·
`design-acquisition.md:96-99`의 «중단되면 `commit --resume`이 그 단계에서 이어간다»가 모두 거짓이 된다.

**B-3 · 치환이 또 샜고(`<screen>-declared.json`) D1이 그 구멍을 통과시킨다**
규범: `dddjango-web/commands/dddjango-web.md:144`·`codex-dddjango-web/skills/dddjango-web/SKILL.md:166` —
«비의미 대상은 `<산출물 폴더>/<screen>-declared.json`에 적어 `--declared`로 준다».
검사기: `workspace/tools/web_refreeze_contract.py:47-49`의 `DISCARD_NAMES`가 §2.1 고정 목록 중
`<screen>-declared.json`·`--excluded-regions` 입력을 **빠뜨려** 이 줄을 보지 못한다(설계 §8-D1은 «§2.1 고정 목록»).
설계 §4.3은 치환 대상 안내에 `143`의 `--declared`·`--excluded-regions`를 **명시적으로 열거**했다.
실패 시나리오: 재동결의 보완 루프가 live `<screen>-declared.json`을 새로 쓰고 그 선언으로 staging 관찰을 만든다 →
`commit`의 `discarded`가 그 파일을 `_prev`로 보내고 `installed`가 **begin 시점 사본**을 되돌려 놓는다 →
편집이 red 없이 증발하고 live 선언과 staging 관찰이 어긋난 채 동결된다. §3-3이 `scope.md`에 대해 막은 그 사고다.

## MAJOR

**M-1 · `begin`이 `has_render_audit`을 build-state에서 상속한다** — `refreeze.py:356`.
설계 §4.1은 «`check --render-audit-skipped`가 내리는 **유일한** 주체»라고 못박았다.
실측: `build-state.has_render_audit=false`인 빌드를 재동결하면 journal이 false로 시작 →
`render-audit.json` 없는 staging이 `check` **exit 0** · `render_audit_skip_reason`은 `null` →
`_finish:568`이 false를 다시 build-state에 적어 렌더 실측 축이 사유 없이 영구 침묵한다.

**M-2 · `installed`의 덮어쓰기에 백업이 없어 되감기가 보존 규정을 못 지킨다** —
`refreeze.py:506-508`(`dst.unlink()` 후 이동) + `_rewind:532-536`(install 되돌리기는 staging으로만 보낸다).
폐기 집합 **밖**의 live 파일(§2.2 고아 · `visual-evidence.json`이 가리키는 구현 캡처)이 이름 충돌로 덮이면
`_prev`에 사본이 없다. 실측: staging에 `captures/screen-impl.png`(보존 대상과 동명)를 두고 `verified`를 실패시키면
되감기 후 그 경로에 **파일이 아예 없다** — §2.2 보존·§4.6-4 «`_prev` 복원»·행동 시험 B2의 «live 바이트 동일»이 깨진다.

**M-3 · `begin`이 실패하면 아무도 치울 수 없는 staging이 남는다** — `refreeze.py:330-331`(mkdir)과
`:343`(예외 미보호 `load_json`) 사이에서 실패하면 journal 없는 `_refreeze-*`가 남는다.
실측: 이후 `begin`=2 · `abort`=1(«되돌릴 재동결 상태가 없다») · `check`=1 · `commit`=1 —
**네 서브커맨드 전부 거부**하는데 hook과 마무리 backstop은 `interrupted refreeze` BLOCKER를 영구 발화한다.
사용자는 R9가 지시한 두 명령이 모두 실패하는 상태에서 손으로 지우는 수밖에 없다.

**M-4 · `--self-test`가 B·C·D2의 검출력을 시험하지 않는다** — `web_refreeze_contract.py:305-310`은
변이 fixture에서 `A·D1·D3·D4`만 요구하고, `_fixture`는 폐기 어휘도 서브커맨드 결손도 보존 대상 치환도 만들지 않는다.
계획 Task 2 Step 2(«합성 입력으로 **각** 검사가 red/green을 내는지»)에 미달이며,
`DEAD_TOKENS`·`SUBCOMMANDS`·`PRESERVED_NAMES`가 오타로 죽어도 self-test는 green이다.

**M-5 · 검사 A의 앵커가 «defer 정의 정본 줄»을 덮지 않는다** — `web_refreeze_contract.py:32-39`·`:80-87`.
`('defer =', 'refreeze', 80)`은 영어 토큰을 찾는데 `commands:72`·Codex `SKILL.md:125`의 같은 표현은 한국어다.
실측: `commands:72`를 «`defer = 재동결·비구현 실행만 허용`»으로 되돌려도 **green**.
`ⓑ defer가 허용하는 것` 열거의 60자 창 **뒤**에 «그리고 재동결»을 붙여도 green.
R8의 회귀를 막는 그물이 정작 defer의 스키마 정의 줄에는 걸려 있지 않다.

**M-6 · 3겹 순회가 예외를 조용히 삼켜 폐기 집합이 줄고, `check`가 같은 함수를 써서 못 잡는다** —
`refreeze.py:88-91`·`:103-106`·`:125-130`(모두 `except (OSError, ValueError): return`) +
`:400-403`(자기 검사가 `evidence_pointers(build)`를 다시 호출).
실측: `design-input.json`에 BOM만 붙여도 폐기 집합이 16→10건으로 줄고 3겹 포인터가 `[]`가 된다
(`load_json`은 `utf-8`, 같은 트리의 `archive_design.py:68`·`check_design_evidence.py:181`은 `utf-8-sig`).
설계 §4.4의 «폐기 집합 자기 검사»는 같은 유도식을 양쪽에 쓰므로 이 조용한 축소를 구조적으로 볼 수 없다.

## MINOR

1. `--render-audit-skipped`가 enum을 검증하지 않는다(`refreeze.py:623`) — «귀찮아서»도 exit 0. 설계 §4.1의 사유 enum은 규범에만 있다.
2. `--staging`이 검증 없이 그대로 쓰인다(`refreeze.py:208-209`) — 빌드 밖 경로·cwd 기준 상대경로 허용(실측: 상대경로는 raw `FileNotFoundError` exit 1, 빌드 밖 빈 폴더는 전량 폐기 후 되감기).
3. `INPUT_GLOBS`의 `'*excluded-regions*.json'`(`refreeze.py:35`)은 규범에 없는 파일명 규약을 가정한다 — `design-acquisition.md:135`는 `EXCLUDED.json` 자리표시자뿐이라 실제 이름이 다르면 §2.1의 복사·폐기에서 조용히 빠진다.
4. `DEAD_TOKENS`(`web_refreeze_contract.py:42`)에 `--compare-out`·`--carried`·`compare_manifests`가 없다(실측: 되살려도 green). `:109-117`의 `break`는 허용 토큰이 있는 줄의 다른 폐기 토큰도 가린다.
5. D1·D3·D4의 구간 앵커(`'산출물 위치'`·`'화면 디자인 출처 해소'`·`'준비 판정'` — `:134`·`:200-201`)가 개정으로 바뀌면 검사가 **빈 구간 = green**으로 공전한다. self-test fixture가 같은 문자열을 하드코딩해 이 퇴화를 못 본다.
6. `commands:144`의 `--out captures/…`·`--captures-dir`가 자리표시자 없는 맨 상대경로라 재동결 중 기준 폴더가 불명이다(D1의 사각 — 설계 §9-10이 예고한 구멍이 실재한다).
7. `abort`의 `completed_at` 거부(`refreeze.py:592-593`)는 `_finish:574-575`가 journal을 즉시 지우므로 실질 도달 불가다. 행동 시험 B7은 «상태 없음» exit 1로 통과할 뿐 가드를 시험하지 않는다.
8. `_finish`의 두 rmtree 사이에서 중단되면 `completed_at`이 있는 `_prev`가 남아 `commit --resume`·`abort` 모두 exit 1 — R9 메시지가 가리키는 두 길이 다 막힌다.
9. `commands:146-147`의 «exit 2는 부족/결함으로 blocked를 유지한다»가 `--build <대상 폴더>` 치환 뒤 staging 게이트에도 적용돼 §1의 «전 구간 `ready` 유지»와 충돌하게 읽힌다(`:138`은 prepare exit 2만 «보완 루프»로 면제한다).
10. `commit`이 `check` 통과를 전제하지 않는다 — begin 직후 곧장 `commit`하면 전량 폐기 후 `verified` 실패로 되감는다(되감기가 온전해야만 안전하다 → B-1·B-2와 결합하면 위험).
11. 죽은 코드: `_finish(journal_path)` 미사용(`refreeze.py:564`) · `pointer_health(project_root)` 미사용(`:240`) · 도달 불가 `return 0`(`:526`).
12. 조감도 `workspace/design/ontology-adoption-map.html`이 갱신되지 않았다(9/4 그대로 · `refreeze` 0건) — 계획 Task 8 Step 8이자 사용자 상시 지침.
13. (참고) 이미지 되감기는 `web/static/fonts/`·`files/`를 보지 않는다 — `fetch_images.py`가 images만 쓰므로 현재는 무해하나, 규범은 폰트·파일 번들 수집도 허용한다.
14. (참고) 같은 캡처가 `design-input` 3겹과 `visual-evidence.json` 양쪽에 있으면 `discard_set`의 차집합(`:184`)과 `check`의 자기 검사(`:400-403`)가 충돌해 **영구 exit 3**이 된다. 현행 v1 스키마에선 발생하지 않는다(실측으로 재현만 확인).

## 확인했으나 문제 없음

- `make verify-web` green(픽스처 12/12 · `web_refreeze_contract --self-test` + 본 검사 green) · `test_refreeze` 24/24 · `test_design_archive` 32/32.
- 신규 3파일과 Codex 미러가 **byte 동일**(`diff -q` 0) · `fixtures_refreeze.sh`가 `run_fixtures.sh` 글롭에 실제로 잡혀 실행된다.
- 설계 B9 실증 — `commands`의 인자 줄을 `<산출물 폴더>`로 되돌리면 D1이 red(`:138`을 정확히 지목). B·C·D2·D3·D4도 각각 변이에서 red.
- 제거 회귀 0 — 배포 트리·docs 전체에 대조 체계 어휘 잔존 없음. `archive_design.py` exit 0/1 · 미사용 import 제거 · 남은 32건이 `archive*` 3함수를 계속 덮는다.
- 중단 감지 — hook은 `design-input.json` 부재·`blocked` 양쪽에서 발화(시험 4건으로 고정) · backstop은 `discovered` 전체를 돌아 `[DESIGN] BLOCKER`로 낸다(F30/F30b) · R9 문구가 설계와 일치.
- Codex 의미 미러 일치(재동결 절 유사도 0.992 · `<대상 폴더>` 정의 1.000 · 변경 hunk 16/16 · 차이는 플랫폼 변수·`spawn_agent`뿐).
- `scope.md` 3중 규율(§3) — begin 복사·sha 기록·commit 대조·재개 시 대조 생략이 모두 맞다.
- `design-evidence.md`의 exit 체계 재작성이 `refreeze.py`의 실제 exit(0/1/2/3)와 일치한다.
- `docs/master.html`·`…lanes.md`는 이번 변경 밖의 사용자 미커밋 파일이다(`master.html:78`의 꼬리 `2`는 사용자 쪽 내용 — 손대지 않았고 커밋에 섞지 않아야 한다).

## 미확인

- 행동 시험 B1·B2·B5·B6·B10(A8 사본 실주행·합성 픽스처 2종) — 실행 기록을 읽을 수 없고 브라우저 실행을 하지 않았다. 위 BLOCKER 2건은 `--stop-after`가 만드는 **깨끗한 경계**에서도 재현되므로 B3·B4의 green과 무관하게 성립한다.
- `make verify` 6/6 전체(나는 `verify-web`만 실행) · `claude plugin validate dddjango-web --strict`.
- 실제 A8 빌드의 `captures/` 구조에 대한 3겹 순회 적중률 — 합성 픽스처로만 확인했다.
- `_history/`·`legacy_v1_allowed`와 staging 공존(설계 §9-5)의 실제 영향.

---
검증 방법: 사본 트리(`scratchpad/mut`)에 규범 변이 12건 주입 후 계약 검사 실행 · `test_refreeze`의 `Fixture`를
재사용해 `_move` 중단 주입·`--stop-after` 4지점 재개·BOM·`--staging` 오지정·보존물 충돌 실험(모두 tempdir).
저장소 파일은 이 리뷰 문서 외에 수정하지 않았다.
