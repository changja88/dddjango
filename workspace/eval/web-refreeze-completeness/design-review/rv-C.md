# 폐쇄 확인 C — 설계 v4 (2026-09-15)

대상: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(이하 `v4:N`) · 직전 `design-review/rv-F.md`
범위: rv-F 항목의 **본문 집행 가능성**과 v4가 **새로 만든** 문장(§2.1 여집합 · §4.3 `<대상 폴더>` ·
§4.6 단계별 규칙 · R7 쓰는 주체 · §8 그물 D)만. 새 감사 축은 열지 않았다.
도구: 기본 검색·편집만(이 워크트리에 `.serena/project.yml`·`graphify-out/graph.json` 없음 — opt-in 표식 부재로
Serena·Graphify 미사용). A8 워크트리는 **읽기만** 했다(파일 목록·JSON 파싱 — 쓰기 0).

## 판정

**구현 진입 불가** (신규 BLOCKER 4 · MAJOR 3 · MINOR 3 · 미폐쇄 3)

v4가 고른 두 해법은 방향이 맞다 — §2.1 여집합·§4.6 단계별 규칙·R7 쓰는 주체는 rv-F가 지적한
빈칸을 실제로 메운다. 막는 것은 **여전히 규범 반영 경로**다. v4는 B-1을 «`<산출물 폴더>` 리터럴
치환»으로 정의했는데, ① 그 리터럴이 사는 줄의 열거가 «전수»가 아니고(`:137`·`:146` 누락)
② 집행 대상 파일 하나(`design-acquisition.md`)는 애초에 `<산출물 폴더>`를 쓰지 않아 치환 규칙도
그물 D도 **공허**하며 ③ M-3이 지목한 `scope.md` 쓰기는 무수식 리터럴이라 치환 대상이 아니다.
즉 rv-F가 «어휘 grep으로 만든 목록이 샌다»고 한 실패가 **다른 어휘로 한 번 더 반복된다**.

## rv-F 폐쇄 대조

| id | v4 주장 | 본문 근거(행) | 판정 |
|---|---|---|---|
| B-1 인자 리터럴 | §4.3 `<대상 폴더>` 도입 · ②5줄 · 그물 D | `v4:117-139` · `:242`(②) · `:243` · `:258` | **부분** — N-B1·N-B2 |
| B-2 `commands:144` | §7 ③ + §1 근거 재작성 | `v4:34` · `:242`(③) | **닫힘**(상호참조 오기 → n-1) |
| M-1 제3집합 | §2.1 여집합 · 3겹은 자기 검사로 강등 | `v4:38-61` · `:146` | **닫힘**(규정 존재) — 단 정의가 틀림 → N-B4 |
| M-2 `has_render_audit` | journal 고정 · 합법 생략 시 false | `v4:112-114` · `:206` | **부분** — «내리는» 주체·시점 미지정 |
| M-3 scope 3번째·금지 | §3 1~6 · live 쓰기 금지 · sha 대조 | `v4:65-78` | **부분** — 규범 반영 경로 없음 → N-B3 |
| M-4 `_prev` 선삭제 창 | 삭제 순서 고정 · `completed_at` · abort 거부 | `v4:93` · `:172-174` · B7 `:282` | **닫힘** |
| M-5 verified 이미지 미되감기 | §4.6-4에 이미지 되돌리기 포함·exit 3 | `v4:168-171` | **닫힘** |
| M-6 `evidence_debt` 쓰는 주체 | `begin`이 observe 기록 · `abort` 복원 | `v4:202-204` · `:209-211` | **닫힘**(코드 대조 완료 — 아래) |
| M-7 installed livelock | 단계별 규칙 분리(덮어쓰기) + B4 | `v4:164-167` · `:279` | **닫힘** |
| m-1 declared 0건 | §4.3 말미 · §9 우회 8 | `v4:137-139` · `:269` | **닫힘** |
| m-2 인벤토리 미덮음 | 보존표 보강 · `refreeze-diff.json` 폐기로 | `v4:56` · `:58-60` | **닫힘** |
| m-3 granularity | 파일 단위 전개 | `v4:102`(예시도 파일) · `:111` | **닫힘** |
| m-4 둘 다 없음 | `discarded` 오류 | `v4:163` | **닫힘** |
| m-5 §1 근거 | 부채 hook 가시성으로 교체 | `v4:31-33` | **닫힘** |

**M-6 코드 대조(요청 항목)** — 충돌 없음. `evidence_debt.py:17` `DECISIONS = ('observe','defer')` ·
`:99-101` `_decision()`이 `decision ∈ DECISIONS`인 dict만 채택(여분 키 거부 없음) ·
`:49-57` `status`가 `observe` → `'observing'` · `evidence_debt_hook.py:_line()`이 그때
«observation pending since …»를 낸다(«decision required before any run» 아님).
`commands/dddjango-web.md:71`이 이미 `{"decision":"observe|defer","at","quote","reason","cases"}` 판형을
성문화하고 있어 R7이 쓰는 dict와 **키가 일치**한다. 소비자는 hook 하나뿐이다
(`check_design_evidence.py`는 `evidence_debt`를 읽지 않는다 — import는 관찰 필드 집합만).

## 신규 발견

### BLOCKER

**N-B1 (B-1 잔여) 입력 게이트 줄 `commands:146`이 치환 목록 밖이라 §4.5가 live를 검사한다.**
`v4:151` §4.5는 «`check` exit 0 뒤 **staging 대상으로** `--phase prepare` → 독립 검토 → `--phase inputs`
exit 0»을 요구한다. 그 게이트의 리터럴이 사는 줄은 `commands/dddjango-web.md:146`이고
(`check_design_evidence.py --build <산출물 폴더> … --phase prepare` · 같은 줄에 `--phase inputs`)
`<산출물 폴더>`가 2회 있다. 그런데 `v4:242` ②의 5줄(`138 140 142 143 145`)에 `:146`이 없다.
`:146`은 ① 12줄 목록(`9 70 129 130 134 137 146 154 171 205 227 234`)에는 있으나 그 편집 지시는
«재동결 어휘»이고 `:146`의 재동결 어휘는 «(재동결을 실행했으면) `refreeze-diff.json`» 한 조각뿐이다 —
`--build` 경로를 고칠 근거가 아니다. 그물 D(`v4:258`)도 «**수집 인자** 줄»로 한정돼 게이트 줄을 못 본다.
결과: 재동결 중 Coordinator가 게이트를 **무손상 live**에 돌린다 → 옛 동결물이 그대로 exit 0을 내
**false green**이 되고, staging은 한 번도 검증되지 않은 채 §4.6 commit으로 들어간다.

**N-B2 (B-1 잔여) `design-acquisition.md`는 `<산출물 폴더>`를 쓰지 않는다 — 치환 규칙도 그물 D도 공허하고,
archive 수집 인자는 편집 절 밖에 있다.**
- 실측: `design-acquisition.md`의 `<산출물 폴더>` 출현 **0회**. 경로 자리표시자는 `BUILD`다
  (`:27 :30 :47 :52 :53 :56 :66 :67 :116 :184`). `v4:125`의 규칙(«수집 인자 줄은 `<산출물 폴더>`를
  `<대상 폴더>`로 바꾼다»)은 이 파일에 **적용되지 않고**, `v4:258` 그물 D의 «`design-acquisition.md`의
  수집 인자 줄에 `<산출물 폴더>` 잔존 0»은 오늘도 이미 참이라 **영원히 green인 공허한 검사**다.
- 절 번호도 틀렸다. `v4:131`·`:243`은 «§1 수집 인자»를 편집 대상으로 든다. 실제 §1(`:6-17`
  «현재 원본 확보»)에는 **경로 리터럴이 하나도 없다**. archive 수집의 실제 인자 줄은 **§2**
  (`:18` «정적 수집과 원본 보관 선택»)의 `:27`이다:
  `python PLUGIN/scripts/archive_design.py EXPORT/screen.dc.html --source-root EXPORT --out BUILD/design-ref --manifest BUILD/source-manifest.json`
  (그리고 `:30`의 «`EXPORT`와 `BUILD/design-ref`는 겹치지 않는 폴더다»). v4의 `design-acquisition`
  편집 지시는 «§2 **«재동결»** 전면 재작성»인데 그 소절은 `:44`부터고 `:27`은 그 **밖**이다.
- 파급: A8 표적 빌드는 `collection=archive`이고 `commands:137`이 archive 경로를 이 파일로 위임한다.
  즉 **재수집의 첫 명령이 여전히 live `BUILD/design-ref`를 덮어쓴다** — v2 이후 구조 전체가 서 있는
  «live 무손상» 전제가 표적 빌드에서 첫 단계에 무너진다. 같은 이유로 `commands:137`의
  `freeze_design.py … --out <산출물 폴더>/design-ref --manifest <산출물 폴더>/source-manifest.json`
  (정적 HTML 경로)도 ② 목록 밖이다 — `:137`은 ① 12줄에 있으나 그 편집 지시는 재동결 어휘 제거다.
  ⇒ `v4:128`의 «치환이 필요한 줄(**전수** — rv-F B-1 실측)»은 거짓이다.

**N-B3 (M-3 잔여) `scope.md` 쓰기를 staging으로 돌릴 규범 문장이 없다 — §4.6-1의 sha 대조가 매 회차 exit 1.**
§3(`v4:70-74`)은 «재수집 중 위 세 쓰기는 staging 복사본에만» + «live 쓰기 금지» + «다르면 exit 1»을
설계에 적었다. 그러나 그 세 쓰기를 지시하는 규범 줄의 리터럴은 전부 **무수식 `scope.md`**다 —
`commands:142`(«사유를 scope.md에 1줄 기록») · `commands:143`(«… `--excluded-regions` 사용 여부를
`scope.md`에 기록한다», «마지막으로 `scope.md` 사용자 승인 원문을 받아»). `<산출물 폴더>` 접두가
없으므로 §7 ②의 치환이 **닿지 않고**, 그물 D도 못 본다. 규범을 그대로 따르면 Coordinator가 live
`scope.md`에 쓰고, `v4:161`의 «§3-4 live `scope.md` sha 대조»가 **planned 단계에서 exit 1**을 낸다.
즉 «실행 경계 기록»(`commands:143`이 의무로 규정)을 수행한 모든 재동결이 commit에서 막힌다.

**N-B4 (M-1 파생) 여집합 정의가 «재수집이 다시 만들지 않는 입력»을 지운다 — `captures/external/*`.**
A8 읽기 전용 실측:
- `20260907-2249-home-bottom-nav/captures/external/`: `lucide.css`(79KB) · `lucide.woff2`(238KB) ·
  `gowun-batang.css` / `20260908-0055-web-settings/captures/external/`: `blocked-sheet-1.css` ·
  `blocked-sheet-2.css`.
- 이들은 **보존 집합이 인용하는 실바이트**다: `design-spec.md`(«`captures/external/lucide.css`·woff2»,
  «`blocked-sheet-1.css`·`blocked-sheet-2.css`는 …») · `motion-notes.md`(«captures/external로») ·
  `visual-check.md` · `build-state.json`(«captures/external/lucide.css:1655:») · `scope.md`.
  `design-spec.md`·`motion-notes.md`는 `v4:59`·`v4:265`(우회 4)가 **재기록하지 않는다**고 못 박은 문서다.
- **재수집이 다시 만들지 않는다**: `source-manifest.json`에서 이 자원들은 `status:"external"`,
  `local_path:""`로 기록돼 archive가 바이트를 가져오지 않는다(«original browser response required; not
  acquired»). `observe_interactions`는 `--out`/`--captures-dir`의 캡처만 쓰고, `freeze_design`·
  `fetch_images`는 `design-ref/`·`web/static/images/`에 쓴다. 이 파일들은 `commands:142` ⓐ
  («누락된 참조는 원래 URL/문서 기준으로 **보완한다**»)를 사람이 curl로 수행한 산물이다 —
  **수집 인자가 없는 축**이라 전량 재수집의 대상이 아니다.
- 따라서 `v4:268`(우회 7)의 «증거로 등록되지 않은 파일이라 **규범상 의미가 없고**»는 거짓이다.
  여집합 규칙은 이 축에서 «다시 만들 수 있는 것을 지우는 것»이 아니라 **복구 불가 입력 삭제**다.
  §10 B1은 표적 빌드(= `captures/external` 없음)에서만 돌므로 이 손실은 행동 시험에도 안 걸린다.

### MAJOR

- **`<대상 폴더>`가 `commands`에서 미정의 어휘가 된다.** `v4:124-125`는 «정의는 재동결 절에 한 번만
  두고»라 하는데 `commands`에는 재동결 전용 절이 없다(절차는 `design-acquisition.md` §2). 자리표시자
  정의는 `commands:36`(«`<산출물 폴더>`는 `.dddjango-web/<생성일>-<화면-slug>/`다»)에 있고 이 줄은
  ①②③ 어느 목록에도 없다. 치환된 `:138·140·142·143·145`가 정의 없는 어휘를 참조하게 된다.
- **행 단위 치환이면 `commands:142`의 `motion-notes.md`까지 staging으로 간다.** `:142`에는
  `<산출물 폴더>`가 3회(`motion-notes.md` · `render-audit.json` · compare_render_audit 인자) 있고
  `v4:128`의 괄호는 «렌더 실측 출력»만 가리키지만 `v4:125`의 규칙은 줄 단위다. staging에
  `motion-notes.md`가 생기면 `v4:165`(«staging 쪽이 있으면 대상 존재와 무관하게 덮어쓴다»)가
  `v4:59` 보존·`v4:265` 우회 4를 이겨 live를 교체한다 → 보존된 `design-spec.md`와 m-id 짝이 깨져
  `check_motion_spec.py` 전수성이 red가 된다.
- **M-2의 빈칸 재발** — `v4:113-114`는 «합법 생략이 확정되면 journal의 값을 false로 **내리고**»라고만
  적는다. journal은 `refreeze.py` 소유 파일인데 4 서브커맨드 중 누가 언제 쓰는지 없다
  (R7 표는 `commit` done의 **build-state 반영**만 담당 주체를 적는다). M-6에서 닫은 «쓰는 주체» 결함이
  같은 형태로 남아 있다.

### MINOR

- `v4:34`의 «§8-B»는 §7 표 ③의 오기(§8-B는 `--compare-build` 잔존 그물이다). §12의 «R7 표에 ②…»
  (`v4:312`)·«R7 표 ③»(`v4:313`)도 §7 표의 오기 — 대조표가 가리키는 절이 본문에 없다.
- §4.4의 자기 검사(«3겹 포인터 ⊆ 폐기 집합»)를 기계 보증으로 쓰지만, 검사기의 disjoint 보장은
  `check_design_evidence.py:1326-1330`의 `reference_capture` 대 visual capture **한 겹**뿐이다.
  나머지 두 겹은 무보장이라 겹침이 생기면 `check`가 빠져나갈 길 없이 exit 3이 된다(표적 빌드는
  12 case 전부 `captures/` 아래·겹침 0으로 확인 — 현재는 발화하지 않는다).
- `begin --quote`가 `commands:71`의 «사용자 인용 ≥10자» 규약을 강제한다는 문장이 없다.

## 미확인

- `refreeze.py`·`web_refreeze_contract.py`의 실거동(아직 없는 스크립트 — 전부 설계 문장과 기존 코드 추적).
- Codex 미러(`codex-dddjango-web/`)의 대응 행 번호 — 재검증하지 않았다.
- 재수집이 만들 **새 파일 이름 집합**(드라이버 미실행) — B4가 겨냥한 충돌의 실제 발화 여부.
- `captures/external`이 없는 나머지 7개 빌드의 제3집합 구성(스모크·`attempt-1`)은 이번에 다시 세지 않았다.
