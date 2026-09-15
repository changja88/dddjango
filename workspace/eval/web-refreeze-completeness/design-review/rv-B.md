# 적대 검토 B — 실행·안전 (2026-09-15)

검토 대상: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(R2 실행 순서·롤백, 3절 행동 시험 중심)

## 판정
**구현 진입 불가** (BLOCKER 4 · MAJOR 2 · MINOR 3)

## BLOCKER

### B1 재동결이 «구현 트리는 건드리지 않는다»는 전제를 스스로 깨고, 롤백은 그 경로를 모른다
- 근거:
  - 설계 §0 비목표 `:20` "구현 트리(`web/**`) 수정 — 재동결은 구현물을 건드리지 않는다."
  - 설계 R1 보존 표 `:58-59` "구현 트리의 시안 자산 번들(`web/static/images|fonts|files`)은 **폐기 대상이 아니다** — 구현물이다."
  - 설계 R4 우회 1 `:122-124` "시안 이미지가 바뀌어도 `web/static/images/`의 구현 복사본은 재동결이 갱신하지 않는다."
  - 그런데 설계 R1 재생성 표 자체가 `:40`에서 "design-tokens.json · asset-manifest.json · screen-meta.json"의 재생성 주체로 **`extract_design.py`·`fetch_images.py`·`extract_dc.py`**를 명시한다.
  - `dddjango-web/scripts/fetch_images.py:2` 독스트링 "Land statically referenced design images in **web/static/images**"·`:35-36` `IMAGES_SUBDIR/IMAGES_PREFIX = "web/static/images"`·`:110` `write_verified(destination, data)` — 이미지 바이트를 `<assets-root>/web/static/images/`에 **실제로 쓴다**(파일명은 `f"{token}_{sha256[:12]}.{ext}"`, `:106`, 내용 해시가 다르면 새 파일 추가).
  - `dddjango-web/scripts/extract_dc.py:9-10` 사용법 `--assets-root <project root>`·`:18` "Status ok/inline means validated bytes landed in **web/static/images**" — A8이 쓰는 `.dc.html` 아카이브 경로(diagnosis.md 확인)의 재생성 주체가 바로 이 도구다.
- 실패 시나리오: A8 사본에서 원본 시안의 이미지 한 장이 바뀐 상태로 재동결을 트리거한다. R2 step 2가 "Phase 0 step 5 그대로" 재실행하며 `extract_dc.py`(또는 `fetch_images.py`)를 다시 부르면 `web/static/images/`에 새 해시 파일명으로 이미지가 **즉시 추가**된다. 이후 step 3 `--phase prepare`가 실패하면 R2 step 4는 `<BUILD>` 안에서 "새로 생긴 산출물"만 지우고 `_prev-<ts>`를 원위치로 되돌리는데, `web/static/images/`에 이미 쓰인 새 파일은 R1의 폐기/이동 대상 목록에도, R2의 롤백 대상에도 없어 그대로 남는다. B2의 합격 조건 "기존 동결물이 바이트 동일로 복원"은 `<BUILD>` 기준으로는 참이어도 **구현 트리 기준으로는 거짓**이 된다. 성공 경로에서도 옛 이미지가 지워지지 않은 채 새 이미지만 누적되므로(콘텐츠 해시 파일명이라 덮어쓰지 않음), 이 표는 자기모순이다.

### B2 `--phase prepare` exit 0은 재동결 «성공»의 충분조건이 아닌데, 그 순간 유일한 복구 수단을 파기한다
- 근거: `check_design_evidence.py` 전체(1445행)에 `render-audit`·`render_audit`·`motion-notes`·`motion_notes`·`design-tokens`·`asset-manifest` 문자열이 **0건**(grep 확인, prepare/inputs/visual 모든 phase 포함). `run()` `:1401-1418`에서 `--phase prepare`는 `validate_inputs(..., require_review=False)`만 호출하고 `{'review_digest': ...}`만 반환한다 — `render-audit.json`·`motion-notes.md`의 존재·내용·최신성은 어느 phase에서도 검사되지 않는다. `screen-meta.json`은 `_check_bindings` `:758-759`에서 **파일이 있을 때만** 선택적으로 대조되고 없으면 조용히 스킵된다(필수 아님).
  설계 R2 `:68-69` "`check_design_evidence.py --phase prepare`를 실행한다. **exit 0 = 재동결 성공.**" → `:70` "성공이면 `_prev-<ts>`를 삭제한다."
- 실패 시나리오: 재동결 중 `render_audit.js` 실행이 조용히 깨지거나(예: 브라우저 미가용), Coordinator가 `motion-notes.md` 재문답 단계를 빠뜨려도 `prepare`는 이를 검사하지 않으므로 exit 0을 낸다. 설계는 이를 "재동결 성공"으로 판정해 `_prev-<ts>`(유일한 복구본)를 즉시 삭제한다. 이후 `--phase inputs`·`visual`도 이 두 파일을 검사하지 않으므로(같은 grep 결과), G2까지 가지 않는 «재동결만 실행» 세션에서는 영구히 아무도 이 결함을 못 본다 — 사용자가 요구한 "다시 동결"이 이 두 축에서는 조용히 실패한 채 "성공"으로 보고된다. `render-audit.json`은 진단(diagnosis.md)이 이미 "대조 도구는 G2용 — 배선만 하면 됨"이라고 명시한 축이라, prepare가 G2 전에 이를 메꾸지 못하면 이번 수리의 핵심 동기(G-A) 중 절반이 다시 구멍으로 남는다.

### B3 `_prev-*` 잔존을 막는 장치가 산문 규율뿐이고, 잔존을 감지할 결정적 장치가 전혀 없다
- 근거: 설계 R2 `:74-76`이 스스로 인용한 근거를 코드로 재확인함 — `backstop.py:70` `if len(parts) >= 3 and parts[0] == '.dddjango-web' and parts[2] in markers:`와 `evidence_debt_hook.py:111-114` `folders = sorted(p for p in (root / '.dddjango-web').iterdir() ...)` 둘 다 정확히 인용대로 동작한다(직접 확인 — B1 판형 "확인했으나 문제 없음" 참조). **그런데 이 "오염시키지 않음"이 바로 "감지도 못 함"과 동전의 양면이다**: `_prev-*`를 build-defect·evidence-debt 어느 쪽에서도 걸러내는 코드가 없으므로, 잔존해도 아무 도구도 경고를 내지 않는다.
  `commands/dddjango-web.md:171` "⑤ `.dddjango-web/` 산출물(...)**[있는 것 전부**; 민감 raw 증거는 공개 커밋 제외])... 커밋한다(**미추적 산출물이 남으면 중단 복구가 명세를 쓸어낼 수 있다**)."
  설계 R2 `:72` "어느 경우든 `_prev-*`는 남지 않는다. **남으면 Phase 2 진입 준비 ⑤의 산출물 커밋에 섞인다.**" — 설계 스스로 이 경로를 인지만 하고 막지는 않는다.
- 실패 시나리오: 재동결이 exit 0으로 "성공"했지만 Coordinator가 `_prev-<ts>` 삭제(R2 step 4의 성공 분기)를 깜빡하거나, 삭제 직후 같은 세션이 곧장 Phase 1→Phase 2로 진행하다가 그 **이전** 실수를 인지하지 못한 채 Phase 2 진입 준비 ⑤에 도달하면, "있는 것 전부"를 커밋하는 그 단계는 `_prev-*`가 남아 있는지 검증할 수단이 없으므로 그대로 git 이력에 커밋한다. 사용자의 명시적 정의("완벽하게 삭제")가 깨진 상태가 **영구히, 아무 경고 없이** 저장소에 남는다. target 프로젝트 쪽에 `_prev-*`/`_staging-*`를 막는 `.gitignore` 관례도 확인되지 않는다(이 저장소 자체의 `.gitignore`에는 그런 패턴이 없음 — 참고용, target 프로젝트는 별도이므로 미확인으로도 분류 가능하나 최소한 이 저장소의 관례상 존재하지 않는다).

### B4 재동결 중단(세션 사멸) 시 증거 부채 hook이 그 빌드를 완전히 놓친다 — hook의 존재 이유를 재동결이 직접 뚫는다
- 근거: `evidence_debt.py:131-133`
  ```
  input_path = build / 'design-input.json'
  if not input_path.is_file():
      return None
  ```
  `evidence_debt_hook.py:109-114`의 `_builds()`도 `(p / 'design-input.json').is_file()`인 폴더만 후보로 삼는다. 설계 R1 재생성 표 `:44`는 `design-input.json`을 폐기 대상(Coordinator가 재생성)으로 명시한다 — 즉 R2 step 1에서 `_prev-<ts>`로 옮겨진 뒤 step 2가 끝나기 전까지 `<BUILD>/design-input.json`은 **존재하지 않는다**.
- 실패 시나리오: R2 step 1(이동) 직후, step 2(재수집, A8 12 case 기준 수십 분) 도중 세션이 죽는다. 다음 세션의 SessionStart에서 hook이 다시 스캔하지만, 그 빌드는 `design-input.json`이 없으므로 `_builds()` 후보 목록에서부터 빠진다 — `[dddjango-web] evidence debt — ...` 줄도, `evidence hook active` 상태 줄의 카운트에도 이 빌드는 **아예 등장하지 않는다**(에러로도, undecided로도 안 뜬다). v1.1.14로 갓 배포된 증거 부채 hook의 존재 이유("판정 불가 빌드도 상태 줄을 낸다")가 재동결이 만든 이 중간 상태에서 정확히 무력화된다. 반면 `backstop.py`는 같은 상태에서 `build-state.json.has_design_screen=True`(R1상 보존 대상이라 그대로 남음)를 근거로 그 빌드를 여전히 build로 잡아 `validate_inputs`가 `Defects(['design-input.json: unreadable ...'])`로 **크게 실패**시킨다 — 침묵(hook)과 폭발(backstop)이 같은 원인에서 갈라지고, 어느 쪽도 "`_prev-<ts>`에서 복구하라"는 처방을 가리키지 않는다. 설계 문서에는 이 시나리오에 대한 문장이 R2 `:72` 한 줄("남으면 섞인다")을 빼고는 전혀 없다.

## MAJOR

### M1 롤백에 "이번 시도에서 새로 쓴 파일" 원장이 없다
- 근거: R2 step 2가 "재실행"하는 절차는 `archive_design.py`(1회) → `observe_interactions.mjs`(case×viewport마다 별도 호출, design-acquisition.md §3.6) → `extract_dc.py`/`fetch_images.py` → `render_audit.js` → `motion-notes.md`(Coordinator 서기) 순의 **여러 독립 도구·여러 호출**이다. R2 step 4 "실패면 새로 생긴 산출물을 지우고"는 이 경계를 코드가 아니라 Coordinator의 그때그때 판단에 맡긴다 — 읽은 5개 스크립트 어디에도 "이번 실행분 파일 목록"을 남기는 매니페스트/트랜잭션 로그가 없다.
- 실패 시나리오: 12 case 중 7번째 도중 실패하면, `<BUILD>/captures/`에는 새로 쓴 1~6번 문서와 아직 손대지 않은(즉 `_prev-<ts>`에만 있는) 7~12번 원본이 뒤섞인 상태다. "새로 생긴 산출물"을 mtime 등으로 골라내는 것은 가능은 하지만 설계에 그 식별 방법이 없고, 코드 지원도 없다 — 사람(또는 LLM Coordinator)의 그날그날 판단에 의존한다.

### M2 B2(실패 주입) 행동 시험이 실행 가능한 정의가 아니다
- 근거: 설계 §3 `:113` "B2 | 수집 중 실패 주입(출처 미가용) | 기존 동결물이 바이트 동일로 복원 · `_prev-*` 잔존 0 · 배너에 실패 지점" — 이것이 B2에 대한 설계의 전부다. 어느 시점(DesignSync `get_project`/`get_file` 전 단계 vs `archive_design.py`의 의존성 누락 vs `observe_interactions.mjs` 도중 브라우저/네트워크 차단)에서 "출처 미가용"을 재현하는지 구체적 방법이 없다.
- 실패 시나리오가 아니라 시험 자체의 결함: 주입 지점에 따라 `<BUILD>` 안에 남는 부분 산출물의 모양이 전혀 다르고(M1), 어떤 지점은 B1의 BLOCKER(구현 트리 오염)까지 함께 트리거할 수도 있는데 설계가 지점을 특정하지 않으므로 구현자·시험자마다 다른 경로를 검증하게 된다. "없으면 시험이 아니다"라는 검토 기준에 정확히 해당한다.

## MINOR

### N1 backstop의 실패 메시지가 `_prev-*` 복구를 가리키지 않는다
- 근거: B4에서 확인한 `Defects(['design-input.json: unreadable (...)'])`는 일반 파일-누락 오류로만 뜬다. 중단된 재동결이 원인이라는 것과 `_prev-<ts>`에서 복원하면 된다는 처방이 메시지에도, 설계 문서에도 없다.

### N2 원본 사전 스테이징(`<BUILD>` 밖)은 R1/R2 어디에도 포함되지 않는다
- 근거: `design-acquisition.md:24` "허용된 staging 폴더에 원본 수집을 마친 뒤" — 이 pre-archive 스테이징은 `archive_design.py`가 아니라 그 앞 단계(DesignSync 원본 다운로드)가 쓰는, `<BUILD>` 밖의 별도 폴더다. R1 폐기 목록·R2 롤백 어느 쪽도 이 경로를 언급하지 않으므로, 실패한 재동결 시도의 사전 스테이징 잔재는 청소 대상에서 빠진다(빌드 폴더 정합성을 해치지는 않지만 디스크에 계속 남는다).

### N3 Codex 미러 byte-parity는 이번 검토에서 실행 확인하지 않음
- 근거: R4가 `archive_design.py`·`test_design_archive.py`·`design-acquisition.md`·`design-evidence.md`에 대해 "+ Codex byte 미러"를 요구하지만, 이번 검토는 `codex-dddjango-web/` 쪽 파일을 열어보지 않았다. `make verify`/`corpus_mirror_sync` 계열 검증에 위임.

## 확인했으나 문제 없음

- **`backstop.py:54-70`의 marker 매칭** — `_prev-<ts>`는 `<BUILD>` 안에 한 단계 더 중첩되므로(`.dddjango-web/<build>/_prev-<ts>/design-ref/...`) `parts[2]`가 항상 `_prev-<ts>` 자신이 되어 `markers` 집합과 절대 일치하지 않는다. 코드로 직접 확인함 — 설계의 인용(행 번호까지) 정확하다.
- **`evidence_debt_hook.py:111-114`의 `_builds()`** — `.dddjango-web`의 **1단계** `iterdir()`만 보므로 `<build>` 아래 2단계로 중첩된 `_prev-<ts>`는 후보에 들지조차 않는다. 설계 인용 정확함.
- **`archive_design.py:156-158`의 "새 출력 디렉터리" 요구** — `archive_files(out)`가 실제로 쓴 파일 집합과 정확히 일치하는지 사후 대조하는 방식이며, `_prev-<ts>`로 옮겨 `out`을 실질적으로 비우면 이 대조가 그대로 통과한다는 설계 R2 step 2의 주장은 코드와 일치한다.
- **`test_design_archive.py`의 compare 계열 시험 수** — `RefreezeCompareTests`(491~666행)에 `def test_` 정확히 10개, `ArchiveTests`(24~490행)에는 `compare` 언급이 전혀 없는 별도 32개 시험. 설계 R4의 "10건" 표기가 정확하고, 제거 후 남는 32건이 `archive()`/`archive_files()`/`archive_dependencies()`의 비-compare 기능(바이트 보존·의존성 closure·symlink 거부·manifest 게이트·observation 게이트 등)을 계속 덮는다.
- **`visual_gate: "stale-after-refreeze"` 신설과 `current_nondesign_scope()`의 충돌 여부(쟁점 3)** — `backstop.py:140-178`의 이 스킵 최적화는 `design_status != 'ready'`면 이미 무력화되는데, R3 첫 문장(`:81`)이 재동결마다 `design_status`를 `blocked`로 내리므로 새 키가 없어도 이 경로는 안전하다. 단 두 필드 갱신의 원자성은 보장되지 않음(M1과 동류의 미세한 잔여 위험, 확률 낮음).

## 미확인

- `render_audit.js`·`observe_interactions.mjs`·motion-notes.md 재기록 Coordinator 절차 자체의 소스 코드는 이번 검토 지정 범위 밖이라 읽지 않았다 — 이 도구들이 `<BUILD>` 밖에 추가로 쓰는 경로가 더 있는지는 미확인(단 `fetch_images.py`/`extract_dc.py`는 확인함 — B1).
- target 프로젝트(A8 등 실제 `/dddjango-web` 실행 대상) 쪽 `.gitignore` 관례는 미확인 — 이 저장소(플러그인 개발 저장소) 자체의 `.gitignore`에 `_prev-*`/`_staging-*`류 패턴이 없다는 것만 확인함.
- 재동결 절차가 실제 운용에서 한 Coordinator 턴 안에 끝나는지, 여러 턴·긴 세션에 걸치는지의 경험적 빈도 — 세션 사멸 시나리오(B4)의 구조적 가능성은 코드로 확인했으나 실제 발생 확률은 운용 데이터가 없어 미확인.
