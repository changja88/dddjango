# 구현 축소 재검토 (2026-09-15)

범위는 **폐쇄 확인 하나**다 — `impl-review.md`의 BLOCKER 1~3 · MAJOR 1~6 · MINOR 1~14 각각을
직접 재현해 닫혔는지 보고, 수정이 **새로 만든** 결함만 보고한다. 새 감사 축은 열지 않았다.

재현 방법은 직전 리뷰와 같다 — 사본 트리(`scratchpad/mut`)에 규범 변이를 주입해 계약 검사 실행 ·
`test_refreeze.Fixture`를 재사용한 tempdir 실험(`_move` 중단 주입 8지점 · `--stop-after` 4지점 재개 ·
단계 도중 크래시 후 abort/resume · BOM · 깨진 JSON · `--staging` 오지정 · 보존물 충돌 · 이미지 차집합).
저장소 파일은 이 문서 외에 수정하지 않았다. A8 워크트리는 읽지 않았다.

## 판정

**수정 필요 (미폐쇄 5 · 신규 BLOCKER 0 · MAJOR 1 · MINOR 4)**

BLOCKER 3건은 전부 실측으로 닫혔다 — 8개 중단 지점 어디서도 파일 소실·바이트 변조가 없고,
`installed`·`verified` 뒤 `--resume`이 exit 0이다. MAJOR 6건 중 5건 닫힘·1건 부분.
`make verify-web` green · `test_refreeze` 33/33 · `dddjango-web/scripts/test` 217/217 · 미러 byte 동일.

그러나 **`installed`에 추가된 «`_prev`로 피신»이 폐기 원본을 덮는 새 경로를 만들었다**(N-1, 실측 재현).
단계 사이 중단 후 live 폐기 경로에 파일이 다시 생기면 `_prev`의 원본이 그 바이트로 교체되고,
이어지는 `abort`는 «재동결 이전 상태다»라고 출력하며 침입 바이트를 live로 되돌린다 —
B-1·B-2가 막 닫은 «성공으로 보고되는 영구 소실»과 같은 실패 모드가 더 좁은 방아쇠로 남아 있다.

## 폐쇄 대조

경로는 모두 `dddjango-web/` 기준(Codex 미러는 byte 동일 — `diff -q` 0).

| id | 수정 근거(파일:행) | 재현 시도 결과 | 판정 |
|---|---|---|---|
| **B-1** 단계 도중 중단 뒤 `abort`가 원본 영구 삭제 | `scripts/refreeze.py:568-592`(`_rewind`가 phase 무관 — `_prev` 실재 기준) · docstring `:17-18` · `cmd_abort:656-658` | `_move`에 크래시 주입 8지점(discard 0·3·8회 뒤 · install 2·5회 뒤) + `--stop-after` discarded/installed/verified 뒤 `abort` = **전부 exit 0 · 소실 0 · 변조 0**(`build-state.json`만 재직렬화 — 의미 동일, diff=[]) | **닫힘** |
| **B-2** `installed` 이후 `--resume` 교착·`_prev` 원본 덮어씀 | `refreeze.py:507`(`if prev is None`일 때만 plan 생성 — phase 되감기 소멸) · `:532` 재개 지점 | `--stop-after installed`→`--resume` = **exit 0** · `--stop-after verified`→`--resume` = **exit 0** · install 도중 크래시(2·5회)→`--resume` = **exit 0**. 모두 `design-ref/screen.dc.html`=NEW · `captures/screen-impl.png`=impl · 잔존물 0. 시험 `test/test_refreeze.py:363`·`:372` | **닫힘** |
| **B-3** `<screen>-declared.json` 누출 · D1 사각 | 규범 `commands/dddjango-web.md:144`·`codex-…/SKILL.md:166` → `<대상 폴더>/<screen>-declared.json` · 검사기 `workspace/tools/web_refreeze_contract.py:54`(`DISCARD_PATTERNS`) + `:158-159` 결선 | `:144`를 `<산출물 폴더>/…`로 되돌림 → **D1 red 2건**(claude:144 · codex:166). `<산출물 폴더>/screen-excluded-regions.json` 주입 → **D1 red** | **닫힘** |
| **M-1** `begin`이 `has_render_audit`을 상속 | `refreeze.py:380` **그대로** · 완화만 추가: `cmd_check:442-444` 경고 출력 | `build-state.has_render_audit=false` 빌드 → journal false → `render-audit.json` 없이 `check` **exit 0** · `render_audit_skip_reason=null` · `_finish:621`이 false를 build-state로 재기록. 설계 §4.1 «`--render-audit-skipped`가 유일한 주체»는 여전히 깨진다. 달라진 것은 침묵 → 경고 1줄 | **부분** |
| **M-2** `installed` 덮어쓰기에 백업 없음 | `refreeze.py:544-546`(dst를 `_prev`로 피신) + `_rewind:586-589` | staging에 `captures/screen-impl.png`=IMPL2 두고 `verified` 실패 → 되감기 후 live가 `impl` 바이트로 **복원**. 시험 `:379` | **닫힘** |
| **M-3** journal 없는 staging을 아무도 못 치움 | `cmd_begin:396-399`(실패 시 rmtree) · `cmd_abort:643-651`(journal 없는 잔존물 정리) | `_refreeze-broken` 생성 → `begin`=2 · `abort`=**0** · 잔존 0. 시험 `:391` | **닫힘** |
| **M-4** `--self-test`가 B·C·D2를 시험 안 함 | `web_refreeze_contract.py:336`(A·B·C·D1~D4 요구) · dirty `_fixture:314-322`(서브커맨드 결손·폐기 어휘·보존 대상 치환 주입) | `check_b`/`check_c`/`check_d2` 무력화 → 각각 **self-test red** · `DEAD_TOKENS=()`·`SUBCOMMANDS=()`·`PRESERVED_NAMES=()`·`WRITE_VERBS=()` → 전부 red | **닫힘**(단 N-4) |
| **M-5** A의 앵커가 defer 정의 정본 줄을 못 덮음 | `web_refreeze_contract.py:32-41`(`defer =`·`유보는`·`유보(`·`"decision": "observe \| defer"` 추가 · `defer가 허용하는 것` 60→140) | `commands:72`를 «`defer = 재동결·비구현 실행만 허용`»로 되돌림 → **A red**(claude·codex 2건). `commands:130` 열거 끝(60자 뒤)에 «, 그리고 재동결» 추가 → **A red**(창 78자 안) | **닫힘**(잔존 한계 아래 참조) |
| **M-6** 예외를 삼켜 폐기 집합이 줄음 | `load_json:62`(`utf-8-sig`) · `_read_document:91-105` · `evidence_pointers:140-145`(errors 수집) · `cmd_begin:346-351`(오류면 exit 1) | `design-input.json`에 BOM → 폐기 집합 **16건 유지** · `captures/screen-step-1.png` 포함. 깨진 JSON → `begin` **exit 1** + 사유 출력. 시험 `:397` | **닫힘** |
| m-1 `--render-audit-skipped` enum 미검증 | `cmd_check:415-417`·`SKIP_REASONS:49` | `--render-audit-skipped 귀찮아서` → **exit 1**. 시험 `:411` | **닫힘** |
| m-2 `--staging` 무검증 | `_single:222-228` | 빌드 밖 폴더 → exit 1(시험 `:417`) · 상대경로는 빌드 기준으로 해소돼 exit 0 | **닫힘** |
| m-3 `*excluded-regions*.json` 이름 규약 가정 | 변경 없음 — `refreeze.py:38` 그대로 | 규범은 여전히 자리표시자뿐(`skills/implementation-ui/references/design-acquisition.md:135`의 `EXCLUDED.json`) · `:73` 폐기 목록도 이 파일을 이름으로 부르지 않는다 | **안 닫힘** |
| m-4 `DEAD_TOKENS` 누락 · `break` 가림 | `web_refreeze_contract.py:44-45`(`--compare-out`·`--carried`·`compare_manifests` 추가) · `:114-121`(`break`→`continue`) | 폐기 어휘 재삽입 → **B red 3건** · 허용 토큰(`refreeze-diff`)과 `carried_from`을 같은 줄에 두어도 → **B red** | **닫힘** |
| m-5 구간 앵커 공전 | `check_anchors:248-259` + `validate:280` | `## 산출물 위치`→개칭 → **red**(D4 앵커 + D1 오탐 노출) · `화면 디자인 출처 해소`→개칭 → **D3 앵커 red 2건**. 검사기 쪽 상수 오타(`LOCATION_SECTION`·`REGION_START`)는 **clean fixture red**로 잡힌다 | **닫힘** |
| m-6 `--out captures/…` 맨 상대경로 | `commands:144` → `--out <대상 폴더>/captures/<screen>-<w>x<h>-interactions.json` | D1이 보는 형태로 수식됐다. `--captures-dir`는 «같은 `captures/`여도 된다»는 설명문으로만 남아 지시가 아니다 | **닫힘** |
| m-7 `completed_at` 가드 도달 불가 | `_finish:625-632`(completed_at + plan phase='done'을 정리 **전**에 기록) | `_cleanup`을 staging만 지우게 바꿔 중단 주입 → `abort` **exit 1**(«이미 완료된 재동결이다» 가드가 실제로 걸린다) | **닫힘** |
| m-8 두 rmtree 사이 중단이 교착 | `cmd_commit:527-530`(phase=='done'이면 정리만) | 같은 중단 주입 → `commit --resume` **exit 0** · 잔존 0 | **닫힘** |
| m-9 exit 2 충돌 | `commands:147` «**재동결 중에는 다르다** — … exit 2는 보완 루프 진입이고 live `design_status`는 `ready`를 유지한다» | 문면 충돌 해소 | **닫힘** |
| m-10 `commit`이 `check`를 전제 안 함 | `cmd_commit:508-509`(`checked_at` 없으면 exit 1) | `begin`→`fill_staging`→`commit` = **exit 1** · live 무손상. `--resume`로 우회해도 **exit 1**. 정상 흐름은 안 막는다: `check`→`commit --stop-after X`→`--resume` 전부 0 · 되감기 후 재-commit도 재-check 없이 0 | **닫힘**(단 N-3) |
| m-11 죽은 코드 | `pointer_health`는 `cmd_check:431`이 사용 · `_finish`는 `:557`이 호출 | `cmd_commit:565`의 `return 0`은 여전히 도달 불가(루프는 항상 `done`에서 반환) | **부분** |
| m-12 조감도 미갱신 | `workspace/design/ontology-adoption-map.html:638` 2026-09-15 재동결 행 | 갱신됨 | **닫힘** |
| m-13 `fonts/`·`files/` 되감기 없음 | 변경 없음 — `IMAGES_SUBDIR:41` | 참고 항목 그대로 | **안 닫힘** |
| m-14 3겹∩`visual-evidence` 겹침 = 영구 exit 3 | 변경 없음 — `discard_set:199` 차집합 vs `cmd_check:436-437` 자기 검사 | 실측 재현: 같은 캡처를 양쪽에 두면 `check`가 «폐기 집합 자기 검사: 포인터가 빠졌다»로 **영구 exit 3**. 현행 v1 스키마에선 발생 안 함(참고) | **안 닫힘** |

**M-5 잔존 한계**(신규 아님 · 설계된 동작): 창은 문장 경계(`—`·`. `)에서 끊긴다(`:87-88`).
`commands:72`의 `defer = 비구현 실행만 허용(… observe 필수 — ` 뒤에 «재동결도 허용한다»를 붙이면 **green**(실측).

## 신규 발견

**N-1 · MAJOR — `installed`의 «`_prev`로 피신»이 `_prev`의 폐기 원본을 덮는다**
`refreeze.py:544-546`. `_move(dst, prev / rel)`는 `shutil.move`라 `prev/rel`이 **이미 있어도** 조용히 교체한다.
`discarded`가 원본을 `prev/rel`에 넣어 둔 뒤 단계 사이에 중단되고, 그 사이 live 폐기 경로에 파일이 다시
생기면(재개 전 도구 재실행·잘못된 `--build`·손편집) `installed`가 그 파일을 원본 위로 피신시킨다.
**실측**: `commit --stop-after discarded` → live `asset-manifest.json`에 `{"intruder":1}` 쓰기 →
`commit --resume` → `_prev/asset-manifest.json` = `{"intruder":1}`(원본 `{"name": "asset-manifest.json"}` 소멸) →
이어 `abort` **exit 0** + «live 빌드 폴더와 이미지가 재동결 이전 상태다» 출력 + live = `{"intruder":1}`.
`discarded` 루프(`:534-537`)도 같은 형태다(실측 동일) — 그쪽은 기존 형태지만, **피신 추가로 보존·고아
파일까지 같은 위험에 들어왔다**. B-1·B-2와 같은 «성공으로 보고되는 영구 소실»이며, 방아쇠만 좁다.
수리 방향: 옮기기 전에 `(prev / rel).exists()`를 보고, 있으면 거부(exit 1)한다.

**N-2 · MINOR — `_rewind`가 지워진 staging을 되살리고 `abort`가 그것을 치우지 않는다**
`refreeze.py:582-585`(①이 `staging / rel`로 `_move` — 없는 폴더를 mkdir로 만든다) + `:662-663`
(`if staging is not None` — `_single`이 None을 준 경우엔 지우지 않는다).
**실측**: `--stop-after installed` 뒤 staging 폴더를 지우고 `abort` → **exit 0** + «재동결 이전 상태다» 출력인데
`_refreeze-*`가 설치분을 담은 채 **잔존** → hook·마무리 backstop의 «interrupted refreeze» BLOCKER가 영구 발화하고
`begin`은 exit 2로 거부한다. `abort`를 한 번 더 돌리면 `:643-651`의 «journal 없는 잔존물» 분기가 치운다(복구 가능).

**N-3 · MINOR — `checked_at`는 «시각»만 고정하고 «내용»은 고정하지 않는다**
`cmd_commit:508-509`가 요구하는 것은 journal의 타임스탬프뿐인데, 교체 목록은 `:522`에서
`_staging_payload(staging)`로 **commit 시점에 다시 계산**된다. `check` green 이후 staging에서 산출물이
사라지면 그 rel은 install에서 빠진 채 폐기만 되고 `commit`은 그대로 진행한다.
합성 실측(verify_inputs 대역)에서 live `design-tokens.json`이 **exit 0과 함께 영구 소실**됐다.
`scripts/check_design_evidence.py`에는 `design-tokens` 언급이 **0건**이라 이 축을 못 막지만,
합성 빌드가 실검사기를 통과하지 못해 **실게이트 차단 여부는 미확인**이다(아래 «미확인»).
계획된 install 목록을 journal에 `check` 시점으로 고정하면 닫힌다.

**N-4 · MINOR — self-test가 B-3을 닫은 바로 그 장치를 시험하지 않는다**
`web_refreeze_contract.py:283-322`의 `_fixture`에 `<screen>-declared.json`도 앵커 결손도 없다.
**실측**: `DISCARD_PATTERNS = ()`로 비워도 `--self-test` **green** · `check_anchors` 무력화도 **green**.
(앵커 쪽은 상수 오타면 clean fixture가 red라 일부 보호된다 — `DISCARD_PATTERNS`는 그 보호도 없다.)
M-4가 지적한 «시험되지 않는 상수» 구멍이 신규 상수로 되살아났다.

**N-5 · MINOR — 규범이 새 동작 둘을 말하지 않고, 한 줄은 이제 거짓이다**
① `commit`이 `check` 없이 거부한다는 사실이 `commands:138`·`design-acquisition.md:58-63`·
`design-evidence.md` 어디에도 없다(전 배포 트리 grep 0건) — 도구가 집행하는 선행조건이 규범 밖이다.
② `design-acquisition.md:93-94`의 «`abort`가 **같은 계획으로** 되감는다»는 이제 사실이 아니다 —
`_rewind`는 plan 무관이고 `_prev` 실재가 기준이다(B-1을 닫은 바로 그 변경). `:95`의
«`installed`는 staging 쪽이 있으면 대상 존재와 무관하게 덮어쓴다»도 `_prev` 피신을 말하지 않아
되감기가 왜 보존물을 살릴 수 있는지 규범만 읽어서는 알 수 없다.

## 확인했으나 문제 없음

- `make verify-web` **green**(픽스처 12개·실패 0 · `web-refreeze-contract self-test green` + 본 검사 green).
- `test_refreeze` **33/33**(직전 24 → RegressionTests 9건 추가) · `dddjango-web/scripts/test` 전체 **217/217**.
- 미러 byte 동일 — `refreeze.py`·`test_refreeze.py`·`fixtures_refreeze.sh`·`references/design-acquisition.md` 모두 `diff -q` 0.
- Codex 의미 미러 일치 — 재동결 절 0.992 · `:144` 대응 줄 0.996 · 「재동결 중에는 다르다」 0.889(플랫폼 변수 차).
- `DISCARD_PATTERNS`·`check_anchors`·확장 `ALLOW_WINDOWS`의 **거짓 양성 0** — 현 규범 전체에 대해 검사 green.
  `--declared`·`--excluded-regions`가 자리표시자 없이 쓰인 자리(`:144`·`:147`)는 접두가 없어 D1이 안 문다.
- `_rewind`의 순서(① install 되돌리기 → ② `_prev` 되돌리기)는 충돌하지 않는다 — ①은
  `not back.is_file()`로 게이트돼 **install이 아직 안 돈 rel의 live 파일을 staging으로 끌고 가지 않는다**
  (보존물 동명 충돌 시나리오로 확인). `installed` 중 크래시 8지점 모두에서 소실·변조 0.
- `checked_at`는 정상 흐름을 막지 않는다 — `--resume`(prev 있음)은 요구하지 않고, prev 없는 `--resume`은
  일반 commit과 같게 요구한다. `verified` 실패 되감기 뒤 staging을 고쳐 재-commit도 재-check 없이 exit 0.
- 이미지 차집합 되감기·`evidence_debt` 복원이 `abort`·`verified` 실패 양쪽에서 정확(`build-state.json` 의미 동일).
- `--stop-after planned`는 멈추지 않고 그대로 완주한다(루프가 `discarded`부터라 사문 — 무해).
- 조감도 `ontology-adoption-map.html` 갱신됨(`:638`).

## 미확인

- 행동 시험 B1·B2·B5·B6·B10(A8 사본 실주행) — 브라우저를 실행하지 않았다. 위 판정은 모두
  `--stop-after` 경계와 주입 크래시라는 **합성 경계**에서 나왔다.
- N-3이 실게이트(`check_design_evidence.py --phase inputs`)에 막히는지 — 합성 빌드가 실검사기를
  통과하지 못해 격리하지 못했다. 격리 실험은 `verify_inputs` 대역으로만 성립한다.
- `make verify` 전체 6/6(나는 `verify-web`만) · `claude plugin validate dddjango-web --strict`.
- 실제 A8 빌드의 `captures/` 구조에 대한 3겹 순회 적중률 · `_history/`·`legacy_v1_allowed`와 staging 공존.
- N-1·N-2가 실제 A8 재동결에서 얼마나 자주 밟히는지(방아쇠 빈도).

---
검증 방법: 사본 트리 `scratchpad/mut`에 규범 변이 8건 주입 후 계약 검사 · 검사기 사본에 상수/함수 변이
11건 주입 후 `--self-test` · `test_refreeze.Fixture` 재사용 tempdir 실험 26회(`_move` 크래시 주입 8지점 ·
`--stop-after` 4지점 재개 · 4지점 abort · BOM·깨진 JSON · journal 없는 staging · 보존물 충돌 ·
`_finish` 중단 · staging 소멸 · PLAN 없는 `_prev` · 단계 사이 외부 쓰기 · 이미지 차집합).
저장소 파일은 이 리뷰 문서 외에 수정하지 않았다.
