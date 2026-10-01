결론: 결함은 `check_design_evidence.py` `validate_inputs()` 의 348행이다. 이 줄은 디스크에서 읽은 archive 이름 집합과 manifest `local_path` 집합을 **문자열 그대로** 비교한다. `archive_design.py` 는 macOS 가 압축을 풀며 NFD 로 만든 디스크 이름(`~/Downloads/춘몽 웹앱/` — zip 안 NFC 43개까지 전부 NFD 로 바뀜)을 manifest 에 그대로 옮긴다. git(`core.precomposeunicode=true`)은 트리와 체크아웃을 NFC 로만 만든다(이력 12,782 경로 중 NFD 0). 그래서 그 빌드를 동결한 워크트리 밖에서는 늘 exit 2 가 난다. HEAD 와 설치본 1.1.25 의 검사기는 바이트가 같고, Codex 미러도 같다. 결함은 1.1.6(`494bff0e` · 09-07)부터 있었다. 지금 main 에서는 시안 빌드 17개 중 **12개**가 이 이유로 inputs exit 2 다. 지금 실행 중인 레인 가운데 막힌 것은 없다. 레인들이 자기 워크트리에서 다시 동결하거나(디스크가 NFD 로 남는다) 발주서가 «NFC 사본» 우회를 지시했기 때문이다. 대신 발주자의 다른 체크아웃에서 G2 를 다시 돌리면 red 가 나고(P1·P2 끝 판에서 재현), 다음에 NFD 폴더를 재사용하는 레인은 G0·첫 coder 입장에서 막힌다. 같은 뿌리의 두 번째 증상도 있다. entry 인자를 NFC 로 치면 `archive_design` 이 exit 0 을 내면서 entrypoint(NFC)와 행(NFD)이 어긋난 manifest 를 쓴다. problem1 이 이 증상을 겪었고, 09-21 상담 3차 레인은 manifest 를 손으로 고쳤다. 권고 수리는 둘이다. ① 검사기는 NFC 로 비교하고 정규화 뒤 중복을 결함으로 둔다. ② `archive_design` 은 이름을 NFC 로 쓴다. 둘 다 digest 를 바꾸지 않는다. 비교할 수 있는 빌드 15개 모두 프로토타입 digest 가 기록된 `visual-evidence.input_digest` 와 같았다. 기존 manifest 이관은 하지 않는다. 이관하면 관찰 34건과 입력범위 검토가 한꺼번에 무효가 된다. 심각도는 플러그인 기준 major 다. 오탐으로 막는 쪽이라 거짓 통과는 없다. 다음 web 릴리즈 전에, W8 보다 먼저 고치기를 권한다.

## §0 쉬운 요약

- 한글 파일 이름은 같은 글자를 두 가지 바이트로 쓸 수 있다(NFC · NFD). 맥의 압축 풀기는 NFD 로, git 은 NFC 로 만든다.
- 시안 동결 도구는 맥이 만든 NFD 이름을 그대로 적는다. 다른 워크트리나 main 에서 받은 파일 이름은 NFC 라 검사기가 «파일 목록이 다르다»(exit 2)고 막는다. 내용(바이트·해시)은 같다.
- main 의 시안 빌드 17개 중 12개가 지금 이 상태다. 동결한 레인 안에서는 통과해서 늦게 드러난다.
- 지금 막힌 레인은 없다. 그러나 발주자가 G2 를 다시 돌리거나, 옛 화면 폴더를 다시 쓰는 다음 레인이 막힌다.
- 고치는 법: 검사기는 비교할 때만 이름 꼴을 맞추고, 동결 도구는 처음부터 NFC 로 쓴다. 기존 승인 지문(digest)은 하나도 안 바뀐다(실측).
- 기존 기록을 NFC 로 고쳐 쓰는 «이관»은 하지 않는다. 승인 증거가 전부 무효가 된다(실측).
- 심각도 major. 다음 web 배포 전에, W8 보다 먼저 넣기를 권한다.

## §1 코드 경로 [실측]

**검사기** — `dddjango-web/scripts/check_design_evidence.py` (HEAD `86fc3c24` = 태그 `dddjango-web--v1.1.25` = 설치본 `~/.claude/.../1.1.25` = `~/.codex/.../1.1.25` 바이트 동일 · Codex 미러 `codex-dddjango-web/skills/dddjango-web/scripts/` 동일)

| 줄 | 하는 일 | 이름 정규형에 민감한가 |
|---|---|---|
| `validate_inputs` 331 `confined(reference_root, local, …)` | manifest 문자열로 파일 연다 | macOS APFS 는 정규형 무시하고 열림 → 통과. 정규형을 가리는 FS(리눅스)면 실패(추정) |
| 332–334 `locals_seen` | manifest 행 중복(정확 문자열) | 아니오 |
| 340–342 | 바이트 크기·sha256 대조 후 `digest_items.append(('source/'+local, data))` | 아니오 — **digest 이름은 manifest 문자열** |
| 343–344 | `manifest.entrypoint ∈ locals_seen` | 예(두 번째 증상 — §1-2) |
| **346–349** | `actual = {archive_files(reference_root) 상대경로}` ≠ `locals_seen` → «archive inventory differs from frozen tree» | **예 — 결함 지점** |
| 362–368 · 386 | case entrypoint `(path, sha)` ↔ manifest 행 | JSON↔JSON 문자열이라 체크아웃과 무관 |
| `_source_observation` 231–236 | observation `archive_sha256` = manifest **파일 바이트** 해시 · entrypoint 일치 | 체크아웃과 무관 |

- `backstop.py --design-build` 는 305행에서 같은 `validate_inputs` 를 부르므로 같이 red 가 된다. HEAD 의 `backstop.py` 는 1.1.25 와 다르지만 바뀐 곳은 빚·치환 모드와 비시안 생략 문구이고, 시안 검사 경로는 같다.
- **digest 구성**: `canonical_digest` 는 (이름, 바이트) 쌍을 정렬해 해시한다. 이름이 `design-input.json` · `evidence/<scope>` · `manifest/<경로>`(manifest 파일 바이트) · `source/<manifest local_path>` · 관찰·캡처 포인터면 **이름과 바이트를 둘 다** 해시한다. 이름은 늘 JSON 안의 문자열이고 디스크 이름이 아니다. 그래서 input_digest 는 체크아웃이 바뀌어도 같고, 바뀌는 것은 집합 비교 결과뿐이다.
- `implementation_digest`(430–445)는 `web/` 아래 **디스크 이름**을 해시한다. spring_dream `web/` 에는 비ASCII 경로가 0개라 지금 영향은 없다. 다만 잠재 위험이다.
- 같은 코드가 `494bff0e`(09-07 · v1.1.6 «preserve Claude Design sources»)부터 있었다.

**§1-2 두 번째 증상(같은 뿌리) — `archive_design.archive()`**
- 133행 `entrypoint = entry.relative_to(source_root)`: 에이전트가 손으로 친 인자는 NFC 다.
- 137·152행 `local_path = source.relative_to(source_root)`: `rglob` 이 준 디스크 이름이라 NFD 다.
- 145행 `if source == entry` 도 서로 다른 꼴이라 맞지 않는다. 그래서 빈 entry 검사를 건너뛴다.
- 결과적으로 archive 는 exit 0 을 내고, 같은 레인의 prepare/inputs 는 «entrypoint: missing successful file row» 로 exit 2 다(재현 §4-3).

## §2 NFD 는 어디서 오나 [실측]

- `~/Downloads/춘몽 웹앱.zip` 은 Claude 앱으로 받은 파일이다(quarantine agent `Claude`). zip 안의 비ASCII 이름은 **NFC 43**(Claude Design 이 만든 `.dc.html` · `내보내기/…`)과 **NFD 16**(사용자가 올린 macOS 스크린샷 `uploads/스크린샷 …` · `Codex 이미지 …`)이다. macOS 스크린샷 이름은 처음부터 NFD 다.
- 풀어 놓은 `~/Downloads/춘몽 웹앱/` 은 비ASCII 이름 **65개가 모두 NFD** 다. macOS 압축 풀기(Archive Utility 계열 Cocoa 경로 — 추정)가 NFC 를 NFD 로 바꿨다. `춘몽 관리자.zip`(admin-2 원천)도 같다.
- `archive_design.py` 는 그 디스크 이름을 정규화하지 않고 manifest 와 `design-ref/` 에 그대로 쓴다. 절단 도구(`extract_*`)·`freeze_design`(정적)은 archive 이름을 만들지 않는다.
- **git 저장 꼴**: `git ls-tree -rz HEAD -- .dddjango-web` 의 비ASCII 경로 1,266개가 모두 NFC 다. `.dddjango-web` 이력 전체(경로 12,782개)에도 NFD 는 0개다. manifest 바이트는 `AI \xe1\x84\x8f…`(조합형 자모), 트리는 `AI \xec\xba\x90…` 다. 저장소·워크트리·스크래치 클론 모두 `core.precomposeunicode=true` 다.
- **런타임·버전과 무관하다**: 도구가 디스크 이름을 그대로 넘기는 것은 Claude·Codex 가 같다(스크립트 바이트 동일). NFD 빌드는 1.1.10(09-09) ~ 1.1.25(09-30) 전 구간과 두 런타임에서 나왔다(6-3-11·8-B-3 = Codex gpt-6-sol · 1.1.25 / 상담 3차 ai-character-chat 재동결 = Claude Opus 4.8 · 1.1.24). NFC 빌드 4개(09-24~26 · 8-B-2·6-3-1·5-1-1·6-3-3 · 모두 Claude Opus 5.5 · 1.1.24~25)는 **발주서가 지시했거나 레인이 직접 만든 «NFC 이름 사본» 우회** 결과다(`GATE-web-8b2-0:14` · `GATE-web-631-0:23-26` · `GATE-web-511-1:14` · `HANDOFF-web-633-compact:157`). 도구가 낸 결과가 아니다.

| 빌드 | manifest 커밋(첫/끝) | 원천 | NFD 행 | main inputs |
|---|---|---|---:|---|
| home-bottom-nav | 09-08 | Downloads/웹앱 로그인 화면 디자인 | 8/58 | 2 |
| user-info-input | 09-08 → 09-29 | Downloads/춘몽 웹앱 | 53/135 | 2 |
| web-settings | 09-08 | 웹앱 로그인 화면 디자인 | 9/59 | 2 |
| web-chat-spine | 09-08 | 같음(NFC 행만) | 0/59 | 0 |
| web-chart | 09-08 → 09-29(6-3-11 재동결) | 춘몽 웹앱 | 53/135 | 2 |
| chart-app-bar · settings-update | 09-09 | 춘몽 웹앱(2) | 16/70 | 2 |
| related-persons | 09-12 → 09-28 | 춘몽 웹앱 | 49/128 | 2 |
| employee-choice | 09-21 · 09-30 재동결(`source-manifest-20260930-nfd.json`) | 춘몽 웹앱 | 55/137 | 2(+무관 결함 2) |
| ai-character-chat | 09-21 → 09-28 | 춘몽 웹앱 | 49/128 | 2 |
| teller-detail-sheet | 09-22 → 09-29(8-B-3 재동결) | 춘몽 웹앱 | 53/135 | 2 |
| conversation-drawer | 09-23(NFC 인자 시도본 `*-nfc-attempt` 보존) | 춘몽 웹앱3 | 26/98 | 2 |
| teller-content-price · settings-nickname · room-open-signal · settings-birth-change | 09-24~26 | scratch `export-nfc`(NFC 사본) | 0 | 0 |
| chart-unknown-hour | 09-30(6-3-11) | scratch `export_0255` | 55/137 | 2 |

(리뷰어가 적은 «13/17» 과 다르다. 현재 main `b6f0ef25b` 에서 이 이유로 실패하는 빌드는 **12**개다. `web-auth-screens` 는 design-input 이 없어서 따로 실패하고, 17개에 넣지 않았다.)

## §3 현장 영향 [실측 + 추정 표기]

**3-1. 체크아웃별 노출** — 디스크 이름만 읽어 집합 비교를 그대로 흉내 냈다(`nfd_scan.py`).
- main `~/Desktop/spring_dream_server`: 12/17 실패. 디스크의 NFD 는 0이다.
- herdr 워크트리는 자기가 (다시) 동결한 빌드만 통과한다. 그 디스크에만 NFD 가 남기 때문이다.
  - lane-5-1-6 11 실패(자기 ai-character-chat 통과) · lane-6-3-11 9(web-chart·chart-unknown-hour 통과) · lane-8-B-3 10(teller-detail-sheet 통과)
  - lane-6-3-15 · 8-C-0 · admin-1 11(employee-choice 가 옛 판이라 통과) · lane-admin-2 11 + 자기 새 빌드 `operator-guide-screens` 통과(NFD 1행)
- 새 워크트리(`git worktree add`)와 새 클론은 NFD 빌드마다 실패한다. 동결한 레인 안이라도 git 이 파일을 다시 만들면(체크아웃 왕복 · `checkout -- .` · rebase) 실패한다(§4-2 재현).

**3-2. 레인이 다른 레인의 archive 빌드를 읽는 때** (Coordinator `commands/dddjango-web.md`)
- **폴더 재사용**(같은 화면 재빌드·수정 모드 — `:46`, G1′ 경로 `:241-246`, 트리비얼 `:252`): G0 freshness · **모든 coder 호출 직전 inputs 입장**(`:211-212`, W3 대상) · `--phase visual --fingerprint` · G2/Phase 3 `backstop --design-build <재사용 폴더>`(`:221·226`)가 모두 그 폴더를 검사한다. 이 경로가 바로 막힌다. 실제 레인들은 재사용하면서 자기 워크트리에서 다시 동결해 이 결함을 가렸다. 6-3-11 은 web-chart, 8-B-3 은 teller-detail-sheet, 5-1-6 은 ai-character-chat 을 그렇게 했다. 그 결과 main 의 실패 빌드가 늘었다.
- **`backstop` 을 `--design-build` 없이 돌릴 때**(현재 비시안 판정에 실패한 경우): 발견된 과거 빌드를 모두 검사한다. NFD 빌드는 inventory 결함으로, 나머지는 원래 `implementation_digest: stale` 로 red 다. 레인들은 이를 기저로 보고 제외한다(`GATE-web-511-1:21` «NFD inventory 8» · `GATE-web-633-1:104`). 결과는 원래 red 라 NFC 수리로 바뀌지 않는다.
- **빚 스캔 · `--debt-residual` · `--subst-check` · refactor_audit**: 시안 증거를 읽지 않는다(`src/*.py` 에 `validate_inputs` 호출 없음). 영향이 없다.
- **G1′ 매핑**: 재사용 폴더의 명세를 읽을 뿐이다. 검사기 영향은 위 재사용 경로와 같다.
- **G0 inputs(새 빌드)**: 자기 빌드라 디스크가 NFD 로 남아 레인 안에서는 통과한다. 결함은 착륙 뒤 main 과 남의 워크트리로 넘어간다.
- **발주자 G2 재확인**: 9-30 측정에서 P1·P2 끝 판을 새 클론에서 `backstop --diff-base <git_snapshot> --design-build <자기 빌드>` 로 돌리자 blocker 1건, 곧 «archive inventory differs» 만 나왔다(`problem-lanes/meas/p1end-backstop-head.1.out` · `p2end-…`). 레인 자신의 워크트리에서는 green 이었다.

**3-3. problem1 · problem2 · 다른 레인**(세션 jsonl · 기록 — 읽기만)
- **problem1 = lane-6-3-11**(Codex · 1.1.25): 런타임에서 inventory 결함을 만나지 않았다. web-chart 와 chart-unknown-hour 를 레인 안에서 다시 동결했기 때문이다. 대신 두 번째 증상을 겪었다. 09-30 03:08 `--phase prepare` 가 «entrypoint: missing successful file row» 로 exit 2 였다(NFC entry 인자). 레인은 archive 소스를 읽고, 덮어쓰기 거절(«destination collision»)을 한 번 겪은 뒤 새 폴더에 다시 archive 해서 03:08:38 에 풀었다(약 1분). 전역 backstop 출력의 과거 빌드 inventory 줄은 기저 노이즈로 보았다(09-29 21:54).
- **problem2 = lane-8-B-3**(Codex · 1.1.25): teller-detail-sheet 를 다시 동결한 뒤 검사했다. 세션에서 inventory 결함은 0회였다.
- **09-21~22 상담 3차 레인**(ai-character-chat 재동결 · Claude Opus 4.8 · 1.1.24): entrypoint 증상을 만나 manifest 를 **손으로 NFD 로 고쳤다**(`REPORT-web-consultation-3:47` «dddjango-web 도구 버그 보고 대상» · 새 sha `449eca16`). 보고된 도구 결함이 처리되지 않은 상태다.
- **09-23 drawer 레인**: NFC 인자로 한 첫 시도를 활성 증거에서 빼 `*-nfc-attempt` 로 남기고, NFD entrypoint 로 다시 동결했다(`GATE-web-drawer-0:24-25`).
- **09-24~26 Claude 레인 넷**: inventory 불일치를 «앞 빌드 inputs exit 2 재현»으로 확인하고, NFC 이름 사본을 따로 만들어 동결했다(`REPORT-web-8b2:47-55`). 발주서에도 이 우회가 규칙처럼 들어갔다(`orders/2026-09-24-web-8b2…:156` · `…6-3-1…:10`).
- **lane-5-1-6 · lane-admin-2**(실행 중 · Codex): 세션의 «inventory differs» 4건은 검사기 소스를 읽은 것이고 실행 결과가 아니다. 자기 빌드는 지금 통과한다.

**3-4. 지금 막고 있는가** — 실행 중인 레인 가운데 막힌 것은 없다(위 디스크 스캔 · 세션 기준). 막히는 곳은 셋이다.
- ⓐ 발주자나 리뷰어가 다른 체크아웃에서 레인 G2 를 다시 돌릴 때(이미 재현됨)
- ⓑ 12개(5-1-6·admin-2 착륙 뒤 13~14개) NFD 폴더를 재사용하는 다음 레인. 다시 동결하지 않으면 G0 freshness 와 첫 coder 입장에서 exit 2 다.
- ⓒ 레인 안에서 git 이 시안 파일을 다시 만들 때

비용은 오진 시간·불필요한 재동결·손으로 고친 manifest·발주서의 수동 NFC 절차다. 측정값: 리뷰·구현 재현에서 53개 이름 맞추기가 두 번, problem1 에서 약 1분.

## §4 재현 [실측 — scratch 만]

환경: `git clone --shared /Users/hyun/Desktop/spring_dream_server diag-nfc/clone`(main `b6f0ef25b`, `core.precomposeunicode=true`). 검사기 넷:
- HEAD — `git archive HEAD dddjango-web/scripts`
- 1.1.25 — `git archive dddjango-web--v1.1.25 …`
- proto-head · proto-v1125 — 각 판의 346–349행만 NFC 비교와 정규화 뒤 중복 결함으로 바꾼 판(`proto_patch.py` · `proto-nfc.diff`)

**4-1. 17개 빌드 `--phase inputs` exit**(`runs/matrix-clone.txt`)

| 빌드 군 | HEAD | 1.1.25 | proto-head | proto-1.1.25 | proto digest vs 기록 `visual-evidence.input_digest` |
|---|---|---|---|---|---|
| NFD 11개(employee-choice 제외) | 2(inventory) | 2 | **0** | **0** | 10개 **같음** · drawer 는 visual-evidence 없음 |
| employee-choice | 2(inventory + 무관 2: `private/` trace 없음 · coverage_review 불일치) | 2 | 2(무관 2만) | 2 | 판정 불가 |
| NFD 0 개 5개 | 0 | 0 | 0 | 0 | 5개 같음(HEAD digest = proto digest) |

→ 비교할 수 있는 15개 모두 프로토타입 digest 가 기록된 digest 와 같다. 기존 승인 증거(입력범위 검토 `reviewed-input` 포함 — inputs exit 0 이 이를 검사한다)가 그대로 묶여 있다.

**4-2. 종단 재현**(`repro_e2e.py` · `runs/e2e-{head,v1125}.txt` · 두 판 결과 같음)
1. NFD 이름 export → NFD entry 로 archive → 동결 체크아웃 inputs: HEAD 0 · proto 0
2. git 커밋 → 트리 NFC → 새 클론(디스크 NFC): **HEAD 2(inventory)** · proto 0 · digest(동결 HEAD) = digest(클론 proto) **True**
3. 같은 체크아웃에서 git 이 파일 하나를 다시 만든 뒤: **HEAD 2** · proto 0
4. 세탁 시도 — NFC 와 같은 행 하나 추가(같은 디스크 파일): HEAD 2(inventory) · proto 2(«archive names collide after Unicode NFC normalization»)

**4-3. 두 번째 증상과 archive 수리 프로토타입**(`repro_entry.py` · `repro_archive_fix.py` · `proto-archive.diff` 27줄)
- 원래 archive + NFC entry 인자: archive exit 0 → 동결 레인 prepare **2**(entrypoint · case entrypoint), 새 체크아웃 prepare **2**(+ inventory). 검사기 프로토만으로는 이 증상이 고쳐지지 않는다.
- archive 프로토(NFC 로 쓰기 · 정규화 뒤 중복 거절 · 자기 검사 NFC): manifest·디스크 모두 NFC. 동결 레인 prepare 0, 새 체크아웃 prepare 0, review_digest 같음 — **수정하지 않은 HEAD 검사기로**.
- 두 프로토를 합친 판(`proto-both`)에서 기존 `test_design_archive.py` 32개와 `test_design_evidence.py` 33개가 모두 OK 다(`runs/proto-both-tests.txt`).

**4-4. `backstop --diff-base HEAD --design-build <빌드>`**(클론 · `runs/bs-*.out`)
- web-chart · chart-unknown-hour: HEAD·1.1.25 = inventory 1건. proto = `implementation_digest: stale` 1건. main 의 `web/` 이 그 뒤로 바뀌었으니 정상인 red 다.
- teller-content-price: 세 판 모두 stale 1건.
- 즉 과거 빌드의 `--design-build` 는 수리 뒤에도 원래대로 stale 이다. 수리가 바꾸는 것은 «지금 레인의 폴더»(재사용 폴더 포함) 판정이다.

**4-5. 이관 시험**(`mig_demo.py` · scratch worktree · web-chart · `runs/migration-demo.txt`): manifest·case 의 이름만 NFC 로 바꿔도 inputs 가 exit 2 다.
- observation 34개 `archive_sha256: stale`(관찰이 manifest 파일 바이트에 묶여 있다)
- observation 34개 `entrypoint: does not match case`
- `coverage_review: reviewed-input does not match`
- observation 까지 고치면 그 파일 바이트가 바뀌어 `input_digest` 와 G2 승인 기록이 무효가 된다.

## §5 수리 선택지

| 안 | 내용 | 기존 digest | 고치는 증상 | 대가·위험 |
|---|---|---|---|---|
| **A. 검사기 NFC 비교**(권고) | 346–349: 양쪽을 `unicodedata.normalize('NFC')` 해서 비교하고, 정규화 뒤 **어느 쪽이든 중복이면 결함**으로 둔다. digest 항목은 manifest 문자열 그대로 | 불변(15/15 실측) | 기존 12개 + 앞으로 동결될 NFD 빌드의 inventory | 약 6줄. 중복 검사를 빼면 §4-2④ 세탁 구멍이 생긴다(HEAD 는 지금 우연히 막고 있다) |
| **B. archive NFC 로 쓰기**(권고) | `local_path`·`entrypoint`·대상 파일 이름을 NFC 로 쓴다. 정규화 뒤 원천 이름 중복이면 거절한다. 자기 inventory 검사와 entry 비교도 NFC 로 | 새 빌드부터(기존 무관) | 두 번째 증상(entrypoint) + 새 빌드의 inventory | 약 10줄. `source`(원본 절대 경로)는 출처 기록이라 원문 그대로 둔다. HFS+ 처럼 NFD 로 강제하는 FS 에서도 자기 검사를 NFC 로 비교하므로 깨지지 않는다 |
| C. 기존 manifest 이관 | 12개 manifest·case·observation 을 NFC 로 고쳐 쓴다 | **무효**(§4-5) | — | 관찰·입력범위 검토·G2 승인을 다시 해야 한다. 동결 증거를 손으로 고치는 일이라 무결성 원칙에도 어긋난다 → **하지 않는다**. A 가 있으면 필요도 없다 |
| D. digest 를 NFC 이름으로 | `canonical_digest` 이름을 정규화 | NFD 12개 무효 | — | 하지 않는다. digest 는 JSON 문자열이라 이미 체크아웃과 무관하다 |
| E. 파일 열기를 디스크 이름으로(선택) | archive 행을 `NFC → 실제 디스크 경로` 표로 연다 | 불변 | 리눅스·정규형을 가리는 FS | macOS 현장에서는 할 일이 없다. 리눅스 CI 계획이 없으면 미룬다(원칙 05) |
| F. `implementation_digest` 이름 NFC(선택) | `web/` 경로 이름을 정규화 | spring_dream `web/` 비ASCII 0개라 불변(다른 프로젝트는 확인 안 함) | 앞으로 생길 한글 `web/` 파일 | 지금 노출 0. A·B 와 같은 묶음에 넣을지는 설계 단계에서 정한다 |

**보안·세탁**:
- APFS 는 정규형만 다른 두 이름을 한 폴더에 둘 수 없다. 그래서 macOS 디스크 쪽 충돌은 생기지 않는다.
- manifest 쪽 «NFC 와 같은 행 두 개»는 같은 파일을 두 번 적은 것이다. A 의 중복 검사가 막는다(실측).
- 리눅스라면 디스크에 두 파일이 있을 수 있다. 중복 검사가 없으면 기록 안 된 파일 하나가 같은 이름 뒤에 숨는다. 그래서 디스크 쪽 중복도 결함으로 둔다.
- NFKC·대소문자 접기는 쓰지 않는다. 서로 다른 이름(전각·원문자 등)을 합쳐 세탁할 틈을 넓힌다.
- 바이트·sha256 대조는 그대로라 내용을 바꿔치기하는 경로는 새로 생기지 않는다.

**고정할 픽스처**(`dddjango-web/scripts/test/test_design_archive.py` `ArchiveTests` — verify-web 자동 경로 · Codex 쪽은 byte 미러):
1. NFD export(NFD entry)를 동결·검토한 뒤 디스크 이름을 NFC 로 rename(체크아웃 흉내) → inputs exit 0, `--fingerprint` input_digest 가 rename 전과 같다(digest 안정성 고정).
2. 반대 방향(NFC manifest · NFD 디스크) → exit 0.
3. NFC 와 같은 행 추가 → exit 2, «collide».
4. (B) NFD export + NFC entry 인자 → manifest 행·entrypoint·디스크가 모두 NFC, prepare exit 0.
5. (B) 정규화 뒤 원천 이름 충돌은 거절. APFS 에서는 만들 수 없으니 `archive_files` 를 대체하는 단위 시험이나, 정규형을 가리는 FS 에서만 도는 `skipUnless`.
- 기존 «missing/extra/modified 탐지» 시험(`test_archive_detects_missing_extra_and_modified_files`)이 진짜 불일치 탐지가 살아 있음을 계속 고정한다.

## §6 심각도 · 릴리즈 · 다른 설계와의 관계

- **심각도: major**(플러그인 기준). 매 coder 입장과 G2 에 들어가는 검사가 오탐으로 막는 결정적 결함이다. 오류 문구가 원인과 무관해 오진·재동결·manifest 수기 수정을 낳았고, 증거 무결성까지 위협했다. blocker 는 아니다. 거짓 통과·digest 손상이 없고, 우회가 있고, 지금 막힌 레인이 없다.
- **다음 web 릴리즈 전에 수리 — 권고.**
  - A·B 합쳐 검사기와 동결 도구 두 파일 약 16줄 + 시험 4~5개다. digest 가 바뀌지 않으니 진행 중인 레인이 플러그인을 갱신해도 기록이 깨지지 않는다.
  - W 시리즈와 섞지 않는 별도 수리 커밋으로 한다(web 수리 관례 절차). 착륙하면 발주서의 «NFC 사본» 우회 절과 `*-nfc-attempt` 류 관행이 필요 없어진다.
- **W3(inputs-log · input digest)**: 상호작용이 없다. A·B 는 출력 digest 를 바꾸지 않으므로, 레인 도중 수리판으로 갈아도 coordinator 행과 coder 행의 digest 가 같다. 지금은 NFD 재사용 폴더에서 W3 로그가 exit 2 행만 쌓고 green 을 막는다. 구현 재현도 53개 rename 우회가 필요했다(`impl-web-t1.md:173,335`). 수리 뒤에는 그냥 클론에서 재현된다.
- **W8(계산 스타일 대조 · G2 차단)**: 순서가 걸린다. W8 은 `--phase inputs` 에 «원본 census 있음»을 더하고 G2 를 차단 게이트로 만든다(`design-W8.md:359`). 이 수리 없이 W8 을 켜면 NFD 재사용 폴더의 오탐이 새 차단 게이트로 이어진다 → **이 수리를 W8 앞에** 둔다. census 지문은 URL·쪽 정보를 뺀다(`:182`). 그래서 브라우저 URL(퍼센트 인코딩된 디스크 꼴)과 manifest 문자열을 비교하지 않는 한 같은 결함은 생기지 않는다. W8 설계 리뷰에서 «경로 비교는 JSON↔JSON 이거나 NFC 양쪽» 조건 하나를 확인하면 된다.
- **공식 SDK 설계**: 직접 관계는 없다(SDK `verify` 는 `check_design_evidence` 를 부르지 않는다 — `design-sdk.md` v2 기준 · v3.1 에서 줄 번호 바뀜). 이미 «경로·문구는 NFC 로 정규화한 뒤 대조»(같은 문서 레지스트리 비교 절)를 쓰고 있어 같은 규칙이다. 공용 헬퍼로 묶을 필요는 없다(파일마다 몇 줄).

## §7 확인하지 못한 것

- 압축을 푼 주체가 Archive Utility 인지, Claude 앱의 자동 풀기인지 확정하지 못했다. zip 의 NFC 가 디스크에서 NFD 로 바뀐 것만 실측했다.
- 리눅스(정규형을 가리는 FS)에서 NFD `local_path` 로 열기가 실패하는지는 돌려 보지 않았다(추정).
- `extract_dc.py`·`fetch_images.py` 의 `source`·`local_path` 사전 조회가 NFD archive 에서 한글 이름 이미지를 놓치는지는 확인하지 않았다. 6-3-3 재추출이 NFC·NFD 판에서 바이트까지 같았다(`daac65222`)는 점으로 보아 현장 영향은 관측되지 않았다.
- 09-24 이전 일부 빌드(home-bottom-nav 등)의 런타임은 기록에서 찾지 못했다.

## §8 이 진단의 쓰기·접근 공개

- 모든 쓰기는 `scratchpad/diag-nfc/` 아래다(클론 `clone/` · 그 worktree `mig/` · `e2e/` · 프로토 판 · `runs/`). 플러그인 파일은 수정하지 않았다.
- spring_dream 은 `git -C <main>` 의 `log`·`ls-tree`·`worktree list`·`rev-list`·`diff --name-only` 와 파일 읽기만 했다. herdr 워크트리에서는 git 을 돌리지 않았고 파일만 읽었다. 판 입력은 보내지 않았다.
- `~/.codex/sessions`·`~/Downloads`·플러그인 캐시는 읽기만 했다. 파이썬은 `PYTHONDONTWRITEBYTECODE=1` 로 돌려 캐시 디렉터리에 `__pycache__` 를 쓰지 않았다.
- Serena·Graphify 는 쓰지 않았다(지시).
- 산출물: `diag-nfc/{nfd_scan.py, run_matrix.py, proto_patch.py, proto_archive_patch.py, repro_e2e.py, repro_entry.py, repro_archive_fix.py, mig_demo.py, sess_scan.py, sess_ctx.py, sess_cmds.py, proto-nfc.diff, proto-archive.diff, runs/}`.

## §9 정정(10-01 · 적대 검토 `review-R8f/review.md` 반영 · 운영 세션)

- **verify-web 경로**: §5 «verify-web 자동 경로»는 틀렸다. 09-16 부터 `make verify-web` 은 `make verify` 밖의 수동 전용이다. 수리 커밋 전에 직접 돌린다.
- **F 를 미루는 근거**: «다른 프로젝트 digest 를 바꿀 수 있다»는 실측이 아니다. spring_dream·kkebi-server 모두 `web/` 비ASCII 경로 0 · `core.precomposeunicode=true` 라, F 가 지금 바꾸는 digest 는 0개다. 미루는 근거는 노출 0 과, `fetch_images` 가 파일명을 ASCII slug 로만 만든다는 점이다(원칙 05).
- **A 단독의 안전 범위**: APFS·ext4 에서는 안전하다. HFS+·FAT 에서는 정규화 비교만으로 기록 안 된 파일이 숨을 수 있다(검토 실측 · proto exit 0 / HEAD 2). 그래서 행마다 `(st_dev, st_ino)` 유일성 검사를 함께 둔다.
- **B 만으로는 디스크가 NFC 가 되지 않는 경우**: 기존 out 에 같은 바이트의 NFD 파일이 있을 때와 HFS+ 일 때다. 그래서 A·B 를 한 커밋으로 한다.
- **§7 미확인 → 실제 결함**: `fetch_images`·`extract_dc` 가 NFC 로 참조된 한글 이미지를 `source is missing …` 으로 놓친다(시끄러운 실패 · 거짓 통과 없음). `asset_io` 조회 쪽 NFC 로 고친다(8f 두 번째 커밋).
- **B 의 덤**: HEAD 는 entry 인자 꼴(정규형·대소문자)이 다르면 entrypoint 행 없이 exit 0 으로 통과시킨다. B 와 «entrypoint ∈ 행» 단언이 이것을 막는다.
- **세탁 설명 보강**: 리눅스에서 B 의 NFC 이름 쓰기는 파일 안 상대 참조(NFD 로 적힌 `src`)를 끊을 수 있다. macOS 현장 밖이라 한계로 적는다.
