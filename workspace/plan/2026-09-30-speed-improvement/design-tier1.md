결론(v3 · 2026-10-01): 재검토 두 편(절차 major 4 · 도구 major 3)을 받아 모두 고쳤고 반박한 지적은 없다. ① **C3** 는 기준이 서면 정확히 두 갈래로 닫힌다 — ⓐ «반영 0 → 남은 minor·nit 를 배너에 적고 G1»(기본 · 오늘보다 반영 사이클 하나가 빠르다) · ⓑ «반영 → 확인 정확히 1회 → G1»(리뷰어가 «G1 전에 닫기»를 적은 항목이 있을 때만). 검토 안 된 명세 변경이 G1 에 닿는 길은 없다. 확인은 «diff 에서 출발해 교차 절까지 보는» 모드이고 통과 조건은 «판정 가능 ∧ 새 blocker·important 0»이다. ② **C3 과 C7 을 떼어 냈다** — arrange 판정은 C3 기준에 들지 않고 G1 배너의 전제다. C7 점검은 ⓑ 의 확인 다발에 합류하거나, ⓐ·기준 불성립이면 배너 직전 단독 1회(임계 15~35분)로 돌며, 배너 판정의 명세 sha 는 G1 명세 sha 와 같아야 한다. ③ **쓰기 울타리**는 리뷰어 넷·acceptance-tester Phase 1 에만 친다(architect 는 명세 전속 작성자라 밖). 스냅숏은 무시된 산출물 폴더도 강제로 담고(`git add -f -A -- <산출물 폴더>`), 별도 객체 폴더를 써 `.git` 에 아무것도 쓰지 않는다[실측]. ④ **W4** 는 `uv run --frozen --no-sync` 와 «Phase 2 진입 때 mypy 기준선 파일»로 바꿨다(옛 판 worktree 는 재제출 때 exit 128). W3 는 응답 원문을 셸 인자로 끼우지 않는다. **C1 은 설계를 바꾸지 않고 두 가지만 확정했다**(§8 «C1 확정»). 사용자 판단이 필요한 쟁점은 없다.

# 속도 개선 1순위 구현 설계 — core · web (v3 · 2026-10-01)

- 입력: `roadmap-v1.md` · 사용자 결정 «1순위 + C7 설계 병행» · «목표는 속도 개선 · 퀄리티는 양보할 수 없다» · C3·C4 채택(C3 의도 «리뷰어 전원 집행 가능이고 minor·nit 만 남으면 전체 재리뷰 루프를 더 돌지 않는다») · «K2 만 이번에»(K1·K3 보류).
- 검토: 1차 scratch `review-t1-proc/review.md` · `review-t1-tool/review.md`(처분 §8-1) · 재검토 `review-t1-proc/rereview.md` · `review-t1-tool/rereview.md`(처분 §8-2).
- 기준: HEAD `3555f5fc`. web Coordinator 줄 번호는 8e 적용 전·후가 같다(8e 덩어리는 줄 수 무변 [실측]). 구현 때는 인용 문장으로 찾는다.
- 표기: `CX` = `codex-dddjango-web/skills/dddjango-web/SKILL.md` · `CL` = `dddjango-web/commands/dddjango-web.md` · `D` = `dddjango/commands/dddjango.md` · `DX` = `codex-dddjango/skills/dddjango/SKILL.md`. 규범 블록 `s006/b9` = `ontology/rules/command-dddjango.ttl` 의 `<…/dddjango.md/s006/b9>`.
- **[실측]** = scratch 실험(`speed-t1/`)·파일·로그·검토 재현에서 셌다 · **[추정]** = 실측을 해석한 계산.
- C7 설계는 `design-C7.md`(v3).

## 0. 쉬운 말 요약 — 지금 → 바꾸면 → 품질 안전장치

| id | 지금 | 바꾸면 | 품질 안전장치 |
|---|---|---|---|
| **C1⑴** | 빚 스캔·G2 직접 실행에서 검사기 둘이 파일 수천 개마다 git 에 «바뀌었나?»를 묻는다(한 번 5분) | 문제 후보가 있는 폴더의 파일만 git 에 묻는다(13~33초) | git 에 묻는 방법은 그대로다. 저장소가 망가지면 «분석 불능»으로 멈추는 것도 그대로다(경계 사례 81쌍 exit 동일) |
| **C1⑵** | registry_gate 가 검사기 27개를 한 줄로 차례차례, 앵커 쪽 끝나면 현재 쪽을 돈다 | 빈 코어 수만큼(최대 8) 동시에, 두 쪽도 동시에 돈다 | 결과를 원래 순서·원래 바이트로 다시 모은다(옛 게이트와 직접 대조 3,511건 동일). 기계가 바쁘면 스스로 1개씩으로 돌아간다 |
| **C2** | 명세를 고칠 때마다 pre-gate 를 먼저 끝내고 나서 리뷰어를 부른다 | pre-gate 를 리뷰어와 같은 때 뒤에서 돌리고 결과를 다음 수정에 넣는다 | 실행 횟수·판정이 같다. red 면 여전히 반송이고, 배너는 여전히 최종본 검사 통과가 근거다 |
| **C3** | 리뷰어 모두 «집행 가능»이고 사소한 지적만 남아도 전체 재리뷰를 또 돌거나(8-C-0 76분), 고친 뒤 아무도 안 보고 G1 으로 간다(다른 레인들) | 둘 중 하나로만 끝낸다 — **고치지 않고** 남은 지적을 G1 배너에 적어 바로 G1(기본), 또는 리뷰어가 «G1 전에 닫자»고 한 지적만 고친 뒤 **그 리뷰어가 한 번만** 확인하고 G1 | 고친 곳은 반드시 누군가 다시 본다. 확인은 바뀐 줄에서 시작해 명세의 다른 자리와 맞는지까지 본다. 기준이 안 서면 지금 그대로다 |
| **C4** | 리뷰어가 노트를 답으로 주면 코디네이터가 38만 자를 손으로 옮겨 적는다 | 리뷰어가 받은 경로 한 곳에 노트를 직접 쓴다 | 호출 앞뒤로 작업 트리 지문(트리 해시)을 떠서 노트 밖 변경 0 을 기계로 본다 — 중간 커밋도, git 이 무시하는 산출물 폴더 안 변경도 잡고, `.git` 에는 아무것도 쓰지 않는다. 어기면 그 노트 무효·정지 |
| **C5** | 리뷰 처분 표가 명세 안에 쌓여 명세가 부푼다(개정 15 에서 83KB · 15.7%) | 처분을 lens 별 파일로 옮기고, 확인 리뷰어에게 자기 lens 처분·명세 diff 만 준다 | 처분 정보는 그대로 남는다. 다른 lens 처분을 안 보니 독립성은 오히려 좋아진다 |
| **C6** | coder 가 registry_gate 를 스스로 돌리고 코디네이터가 또 돈다 | **바꾸지 않는다** | coder 자기 실행이 #647 둘을 미리 잡았다 [실측] |
| **W1** | Codex 코디네이터가 서브에이전트를 30초마다 확인한다(모델 분 P1 65 · P2 44) | 한 번에 5분까지 기다린다(끝나면 즉시 돌아온다) | 무엇을 기다리는지·언제 받는지가 같다 |
| **W2** | 시안의 기기 틀·상태줄이 앱 화면인지 장식인지 가리는 절차가 없다 | 원본 수집과 입력범위 리뷰에 «미리보기 장식 판별 · 제품 모드 캡처가 비교 기준»을 넣는다 | 장식이라고 하려면 근거(원본 설정 · 발주서·사용자 문장)를 대야 한다. 이미지 한 장뿐인 시안이면 G0 에서 한 번 묻는다 |
| **W3** | coder 부르기 전마다 inputs 검사를 돌리고 `visual-check.md` 를 손으로 고쳐 적는다 | 검사와 기록을 명령 한 번으로(로그 한 줄 · input digest 포함) | 검사 두 번(코디네이터·coder)은 그대로다. 명령은 검사기 실패를 그대로 돌려주고, 에이전트 답 글을 셸 명령에 끼워 넣지 않는다 |
| **W4** | «기존 린트가 있으면 신규 위반도 검사»가 명령 없이 적혀 있어 레인이 안 돌렸다 | G2 전 변경 파일(빌드 폴더 포함)에 프로젝트 린트·포맷을 프로젝트 설정 그대로 돌리고, 타입 검사는 Phase 2 시작 때 남긴 기준선과 견준다 | 검사를 더하는 쪽이다. 검사 단계가 `uv.lock` 같은 제품 파일을 바꾸지 않는다. 프로젝트가 뺀 파일을 억지로 검사해 가짜로 막지 않는다 |
| **O1** | 발주가 빚 방침을 안 적으면 G0 에서 반드시 묻고 기다린다 | 발주서에 «빚 방침: ⓐ 먼저 정리» 한 줄(플러그인 변경 없음) | 결정 내용이 B1(09-26)과 같다 |

## 1. 실측으로 바뀐 전제

### 1-1. registry_gate 는 검사기를 비-git 사본에서 돈다

- `registry_gate.main` 은 현재 트리를 `_snapshot_current`(:166 — `.git`·`.*` 제외 복사)로, 앵커를 `anchor_diff.snapshot_anchor`(git archive)로 떠서 **둘 다 git 밖**(`$TMPDIR`)에서 검사기를 돈다. pre-gate 도 격리 사본에서 같은 registry_gate 를 부른다(`design_pregate.run_gate` :2380) [실측 · 검토 재확인].
- 그래서 그 안에서는 파일별 git 비용이 없다. 로드맵 §7 의 379·257초는 **git 클론에 직접** 돌린 값이다 — G0 빚 스캔(`g0-scan-run.sh` [실측])과 G2 직접 실행 계열(`D` s007/b46 R-0365)의 비용이다.

| 실험 | 대상 | 값 [실측] |
|---|---|---|
| E1 비-git 스냅숏 1벌(부하 10~19) | field-clone 스냅숏 | 27종 직렬 288.8초 · 병렬(8) 118.5초 · 27종 exit·출력 해시 동일 |
| └ 느린 검사기(직렬) | | domain-model 107.6 · port-adapter-pairing 47.4 · context-isolation 15.1 · business-vocabulary 13.6 · composition-root 13.2 · 나머지 ≤12.5 |
| E2 git 워크트리 직접 · ⑴ A/B | §3 C1 | 옛 260~467초 → 새 3~33초 · 7/7 byte 동일 |
| E4 pre-gate 현장 재생(8-C-0 run 2·11·13 · 부하 10~22) | scratch 복제본 | 1,553 → 732초(−53%) · 3/3 byte 동일 |
| E5 같은 격리 사본 registry_gate(run 13 판 · 부하 7~12) | scratch | 옛 170·153초 → 8워커 91 · 자동 88 · 2워커 104 · 옛 게이트와 stdout·`introduced.json`(레코드 3,511) 동일 |
| 검토 재현(도구 · 부하 20~33 · v1 고정 8) / (재검토 · v2 자동 · 시작 부하 29.6) | run 2 | 442.3 → 402.5초(−9%) / 442.3 → 438.4초(−1%) · 둘 다 byte 동일 |

- 결론: pre-gate·registry_gate 의 지렛대는 ⑵ 이고 **이득은 빈 코어에 달렸다**. ⑴ 은 G0 빚 스캔·G2 직접 실행·coder 의 직접 검사기 호출에서 부하와 무관하게 효과가 난다.

### 1-2. 현장 증거로 모양을 바꾼 두 항목

- **C6**: 8-C-0 `s2-coder-report.md:20` «coder 첫 자기 실행의 #647 둘은 `JsonValue` 로 고쳐 0» [실측]. #647 은 ⓓ 후보(R-0284 · exit 불산입)라 빠졌다면 슬라이스 감사 입력의 ⓓ 후보로 가서 감사 반송 1회가 됐을 것이다. coder 자기 실행은 레인 명세 §15 가 시킨 것(명세 재량)이다. C1⑵ 뒤 중복 비용은 슬라이스당 약 1.5~3분이라 넣지 않는다.
- **W3**: coder 의 «첫 변경 전 직접 inputs» 는 `d90aa901`(2026-09-07)의 의도된 이중 확인이다(설계 `2026-09-06-web-design-source-integrity.md:59`) → 빼지 않는다. digest 를 알려면 검사기를 돌려야 하므로 «digest 같으면 생략»도 절감이 없다. 줄이는 것은 기록 부기다.

### 1-3. C3 역재생 — 보관 레인 6곳 + 8-C-0 [실측]

- 재료: scratch 복제본 `origin/main:.dddjango/<폴더>/g1-review-*.md` · 결과 `speed-t1/c3-replay/result.md`·`lane-*.md`. «엄격» = 규칙 문면 · «완화» = 다시 불리지 않은 lens 의 직전 노트를 인정.

| 레인 | 기준 성립 | 성립 뒤 실제 재리뷰 | 새 blocker·important | v2(확인 의무) 비용 | v3(ⓐ 기본) |
|---|---|---|---|---|---|
| 8-B-4 fortune-house(25) | 엄격 불성립 · 완화 r8 = 마지막 라운드 | 0 | 0 | 0 ~ +9분(확인 1회가 더해짐) | 0 이하(ⓐ 면 반영 사이클이 빠짐) |
| 8-B-9 showcase-server(20) | 엄격 불성립 · 완화 r3 | 1(r4 · 노트 1 · nit 1) | 0 | −0~2분 | 0 이하 |
| 6-3-5 birth-input-check(19) | 엄격 불성립 · 완화 r4 = 마지막(추가 구간 넷) | 0 | 0 | **0분(문면대로면 최대 +29분 — 구간 넷마다 확인 1회)** `lane-birth-input.md:73` | 0 이하 |
| 8-B-5 price-room(17) | 엄격 전 구간 불성립 | 0 | 0 | 0분 | 0(기준 밖 — 지금 규범) |
| 8-B-1 contents-books(16) | 엄격 불성립 · 완화 r6 = 마지막 | 0 | 0 | 0분 | 0 이하 |
| 6-2-2 video-poster(15) | 불성립(db-4 important) | 0 | 0 | 0분 | 0(기준 밖) |
| 8-C-0 | r7(12:53~12:55) | 3(r8~r10 · 노트 8) | 0 | 약 −34분 | ⓑ 약 −34분(discipline-7 «minor 1은 G1 전에 한 구절로 닫기를 권한다» [실측 `:3`]) |

- 성립 뒤 재리뷰 4라운드·노트 9개에서 놓친 blocker·important 는 0 이다 — 표본이 작아 «반례 없음»이지 안전의 증거는 아니다.
- v2 는 기준이 서면 확인 1회를 의무로 붙여 birth-input 같은 레인을 느리게 할 수 있었다. v3 는 기본 갈래 ⓐ 가 반영 사이클을 덜어 오늘보다 빠르거나 같고, ⓑ 는 리뷰어가 G1 전 닫기를 적었을 때만이다(§3 C3 «시간»).
- 설계에 반영한 관찰: 다시 불리지 않은 lens 의 열린 important(birth-input db · price-room ddd · showcase db) · 자문으로 붙은 lens 노트(fortune-house db) · lens 사이 심각도 불일치(video `g1-review-db-4.md:21` important ↔ `g1-review-discipline-4.md:42` nit) · nit 반영 개정도 블록 해시를 바꿈(price-room · birth-input · contents-books).
- G1 을 지나간 흠 하나(C3 과 무관 · 실제 절차에서도 놓침): birth-input DE4 기대 본문의 `"missing":[]` 누락(개정 3 `26199c578` design-spec L637) — Phase 2 반송이 잡았다.

## 2. 공통 절차 — 구현·커밋 규약

- **core 규범(graph-owned)**: `ontology/rules/<doc_key>.ttl` rdflib 구조 편집 + canon 재직렬화 → 새 규범은 `ontology/ISSUED` 채번(규범 하나 = 클래스 하나) · 개정은 새 Expression(revision n+1 · revisionKind) → **새 규범은 `ontology/wiring/<doc_key>.ttl` 에 `delegatedTo` 또는 `enforcedBy` 등재**(`ontology/shapes/djr-shapes.ttl` :119-121 `NormShape` 요구) → `ontology_gate.py` → `ontology_render.py --apply <doc_key>` → 재투영 절마다 `ontology/LEDGER.tsv` 재기준선 → `target-counts.json`·q4 골든 → `make rulepack` → `DX`·역할 SKILL 손 미러 → `make verify` → 커밋 → 봉인 별도 chore. agent frontmatter 를 바꾸면 `claude plugin validate dddjango --strict`. 절차 정본 = `docs/DEVELOPMENT.md` §3.
- **core 검사기·도구**: `dddjango/scripts/*.py` ↔ `codex-dddjango/skills/dddjango/scripts/` byte 미러 → 골든은 바뀌면 안 된다 → `make verify` → 커밋 → 봉인 chore.
- **web**: 산문 정본. Claude md ↔ Codex SKILL 손 미러 · `design-acquisition.md` 는 byte 미러 → `make verify-web`(수동) → 커밋.
- **릴리즈 창**: `dddjango/scripts/` 가 바뀌면 진행 중 레인의 마지막 예보가 «툴체인 stale» 이 된다 — **C1 이 든 core 릴리즈는 8-C-0 착륙 뒤**. 규범 커밋은 `rulepack.json` 이 digest 에서 빠지므로 digest 에 닿지 않는다.

### 2-1. 공유 판형 — «부속 기록 판형»(Coordinator) · «부속 기록 예외»(역할)

C4(리뷰어 노트) · C5(lens 별 처분 파일) · C7(arrange 노트) · K 설계의 기록 파일은 «역할이 명세·코드가 아닌 기록 파일을 쓴다»는 같은 모양이다. 지금 규범과 부딪치는 곳은 architect **R-1568**(«그 밖 산출물 생성 금지») · 리뷰어 넷의 읽기 전용 규범(ddd R-3367·R-3398 · db R-3322·R-3361 · api R-2609·R-2707 · discipline R-0834·R-1135)이다. 선례는 **R-3572**(`djr:Exception` — `verdict.md` 는 «다른 산출물 금지»의 예외 · wiring `delegatedTo command-dddjango`)다.

- **부속 기록 판형**(Coordinator · `D` 산출물 위치 절 새 블록 · Obligation 1):
  1. 경로는 Coordinator 가 정한다 — `<산출물 폴더>/<종류>-<역할|lens>-<회차>.md`, 호출마다 새 이름. 한 호출에 경로가 여럿일 수 있다(architect 의 lens 별 처분).
  2. 역할은 받은 경로에만 **새 파일로** 쓴다(이미 있으면 쓰지 않고 보고). 응답 안에 경로마다 `기록: <경로> · sha256 <값>` 행을 둔다(응답의 다른 본문 — 판정 1행 · 보고 항목 · Z 옵션 — 은 그대로 둔다). Coordinator 는 파일 sha256·머리의 역할/lens 가 응답·경로와 같은지 본다.
  3. **울타리 대상 역할**(리뷰어 넷 · acceptance-tester Phase 1 arrange 모드)의 호출은 쓰기 울타리 창(§3 C4) 안에서만 한다. architect 는 명세 전속 작성자라 울타리 밖이다 — 2번의 `기록:` 행을 응답에 싣고 Coordinator 가 sha256 을 파일과 대조한다. architect 의 그 밖 쓰기는 지금처럼 R-1568(«그 밖 산출물 생성 금지»)이 막는다. 울타리 창 동안에는 architect 를 파견하지 않는다(§3 C4 «창은 배타적»).
  4. 부속 기록은 명세의 현재 상태가 아니고 판정 근거도 아니다(처분 파일의 «까닭»도 확인 리뷰의 판정 근거가 아니다 — 닻 효과 가드).
- **부속 기록 예외**(`djr:Exception` · 같은 이름): «Coordinator 가 부속 기록 판형으로 준 경로의 <종류> 파일은 <충돌 규범>의 예외다».
  - architect: 종류 `review-disposition-<lens>-<n>.md`(C5) · 대상 R-1568. **K 는 이 목록에 자기 기록 종류를 한 줄 더하는 amendment 로 재사용한다**(새 예외를 따로 채번하지 않는다).
  - 리뷰어 넷: 종류 `g1-review-<lens>-<n>.md`(C4) · 대상 = 각자의 읽기 전용 규범(위 ID).
  - acceptance-tester: **예외 불필요** — C7 의 새 모드 규범이 처음부터 «부속 기록 한 파일 말고 쓰기 0»으로 쓰인다.
- 이름을 «부속 기록 판형 / 부속 기록 예외»로 고정해 K 설계가 그대로 부른다.

## 3. 항목별 설계

### C1 — 검사기 git 질의 순서(⑴) · registry_gate 병렬(⑵) — **확정(구현 시작 · §8 «C1 확정»)**

**⑴ 바꾸는 것**(두 파일 · byte 미러)

- `check-composition-root.py::_filtered_di_findings`(HEAD :624-661): BC 마다 발견 후보(`composition_root.py` 이름 · 실재 파일 · `composition/` 밖)를 먼저 모은다. **후보가 0 이면 `_git_tree_has_tracked_changes`(BC 단위 트리 질의 1회 — 옛 코드가 BC 마다 늘 하던 질의 :645)만 돌리고 파일별 `_git_path_is_touched` 는 건너뛴다.** 후보가 있으면 옛 코드와 똑같이 판정한다. 트리 질의를 남겨 루트 트리 결손이 옛 코드처럼 exit 1(«분석 불능» — `D` :209 G2 차단)이 된다.
- `check-idempotency-scope-creep.py::_idempotency_artifacts`(HEAD :159-174): 멱등 신호(이름 → 본문)를 먼저 보고 신호가 있는 파일에만 `_is_new_or_modified` 를 부른다. 목록의 원소·순서 무변.
- **바꾸지 않는 것**: 세 git 질의 함수의 명령·pathspec·에러 처리 전부. 같은 판형 검사기 넷(mechanism-ownership · synthetic-infra-exc · transient-overmapping · openapi `_scan_is_new_or_modified` :719)은 이미 후보에만 git 을 부른다 → 무변.
- 대조 [실측]: E2(설계자 7쌍 + 함수 1건 byte 동일) · 검토 ab1 81쌍을 v2 프로토로 — **exit 81/81 · stdout 81/81 · 레코드 81/81 동일**, stderr 만 다른 곳은 HEAD 없음 + 스테이징(git 잡음)과 루트 트리 결손(문구의 경로가 파일 → BC · 둘 다 exit 1)뿐(재검토가 같은 묶음 7쌍으로 재확인).

**⑵ 바꾸는 것**(`registry_gate.py` · byte 미러 · 검토 `fix/` 판 + 워커 수)

- `_run_registry`: 작업을 모듈 공용 `ThreadPoolExecutor` 에 `submit` 으로 올리고 `concurrent.futures.wait` 로 전부 끝난 뒤 REGISTRY 순서로 `result()` 를 거둔다(첫 예외 = REGISTRY 순서 첫 실패 · 임시 폴더 누수 0). sink 는 작업 인덱스 `i` 로 `<sink>.<i:02d>.part` 를 따로 주고 끝나면 REGISTRY 순서로 **바이트 그대로** 이어 붙인다.
- `main`: 앵커·현재 두 벌을 두 스레드로 동시에(같은 공용 풀).
- **워커 수**: `DJR_REGISTRY_WORKERS`(양의 정수)가 있으면 그 값, 없으면 빈 코어 수 `max(1, min(8, int(cpu_count − loadavg_1분)))`. **`os.getloadavg` 가 없거나 실패하면(`AttributeError` · `OSError` — Windows 등) `cpu_count // 2`** 로 둔다(§8 «C1 확정» ②). 출력은 워커 수와 무관하다. 설정은 필요 없고, 발주자가 몫을 고정하고 싶으면 레인 발주 템플릿 실행 환경 줄에 `DJR_REGISTRY_WORKERS=<n>`(선택).
- ⑶(G0 빚 스캔 병렬 러너)은 보류: ⑴ 뒤 빚 스캔 약 4.5분 · 병렬 추가 절감 스캔당 약 2.5~3분 — 한 레인 측정 뒤 다시 본다.

**fail-closed · 품질 보존**: ⑴ 저장소 결손은 후보 유무와 무관하게 exit 1(루트 트리) · 후보가 있는 BC 는 옛 코드 그대로. ⑵ 작업 예외는 전부 끝난 뒤 REGISTRY 순서 첫 예외 · 조각은 바이트 병합 · 뒤 읽기는 옛 코드 그대로(`errors="replace"`). 검사기끼리 쓰는 파일이 없고(쓰기는 sink 뿐) 판정은 집합 차분이라 순서와 무관하다.

**검증 계획**

1. 이번 설계·검토에서 수행 [실측]: E1 · E2 · E4 · E5 · 검토 ab1 81쌍 · 검토 ab2(옛 게이트 vs 새 · 레코드 463 · 워커 1/3/8/기본 · 결함 주입 — 수정본에서 옛과 같음) · 재검토 재실행(v2 프로토 · 같은 결과).
2. 구현 검증(커밋 전 — `make verify` 등재)
   - `make verify` 전부 green · 골든 무변.
   - **새 스모크 `workspace/tools/git_touched_smoke.py`**(verify-base-core) — 임시 git 저장소 시나리오 × 세 호출: ① 깨끗 ② 미추적 후보 ③ 커밋된 후보 + 같은 BC 다른 파일 수정 ④ staged 삭제 ⑤ 미스테이징 삭제된 후보 ⑥ BC 를 넘는 staged rename(멱등 산출물 포함) ⑦ 커밋된 후보를 다른 BC 로 `git mv` ⑧ HEAD 없음(스테이징 있음·없음) ⑨ 서브디렉터리 TARGET ⑩ 글롭 메타문자·공백·비-ASCII·`*.py` 이름 · 글롭이 인벤토리 밖 시험 파일만 잡는 경우 ⑪ 비-git TARGET ⑫ 서브모듈(BC 자체 · BC 안 · 서브모듈 안 수정·미추적 후보 · `application/` 자체) ⑬ 심볼릭 링크 BC·링크 후보 ⑭ `.gitignore` 된 후보 ⑮ 대소문자만 바꾼 후보 ⑯ linked worktree ⑰ staged 뒤 재수정 ⑱ off-tree `composition/` 안 파일 ⑲ 멱등: 미요청 scope + 신규/수정/무변 산출물 + G1 채택 배너 면제 ⑳ **루트 트리 결손(후보 유/무) → exit 1 기대** · **하위 트리 결손은 «같은 폴더에 파일 하나를 스테이징해 cache-tree 를 무효로 한» 변형만 → exit 1 기대**(cache-tree 가 유효하면 `git diff --quiet HEAD` 가 하위 트리를 읽지 않아 옛·새 모두 exit 0 이라 결정적 재료가 아니다 — §8 «C1 확정» ①). 기대값은 바꾸기 전 코드로 `--emit` 해 커밋에 싣고, stderr 는 ⑧·⑳ 에서 비교하지 않는다. 검토 `ab1.py` 가 시나리오 구현 판형이다.
   - `registry_gate_smoke.py` 에 옛 게이트 직접 대조: 판례 `_pre_repair_gate`(P0′)처럼 바꾸기 전 `registry_gate.py` 를 현행 검사기 트리에 덮어쓴 사본과 새 게이트를 같은 픽스처(검토 `ab2.py` 판형 · 수백 건)에서 돌려 stdout(툴체인·sidecar 경로 행 제외)·`introduced.json`·`contract.json`(휘발 필드 제외) 동일. 새 게이트는 워커 1·3·8·기본. 결함 주입 둘: ⓐ sink 에 깨진 바이트 한 줄 → 옛·새 exit 2 · 판정 동일 ⓑ 검사기 stdout 비-UTF-8 → 옛·새 traceback 1 · exit 1 · 임시 폴더 누수 0.
   - 변이: 조각 순서 뒤집기 → 옛 대조 red · 텍스트 strict 병합 → 주입 ⓐ red · `map` 복귀 → 주입 ⓑ 누수 red · 후보 필터 «항상 건너뜀» → 스모크 ②③④⑥ red · 트리 질의 생략(v1 프로토) → ⑳ 루트 트리 결손 red.
3. 현장 재생(커밋 전 · scratch): 8-C-0 pre-gate 21판 전부 옛/새 byte 동일 · 벽시계와 `uptime` 부하를 함께 적는다. 빚 스캔도 G0 커밋에서 27종 직접 실행 옛/새 동일.

**기대 이득 — 부하에 따라 [실측 해석]**

| 기계 상태 | registry_gate 한 번 | pre-gate 한 번 | 근거 |
|---|---|---|---|
| 빈 코어 있음(1분 부하 ≤ 약 12/20) | −32~−48% | −20~−55%(고정비 약 150초가 남는다) | E5 · E4 · 나눔(run 13: 새 241초 = registry 92 + 사본·스텁·실존 약 150) |
| 코어 꽉 참(부하 ≥ 20) | 0~−10% | 0~−10% | 검토 −9% · 재검토 −1% |

- 8-C-0 판형 [추정]: pre-gate 합 135분 → 빈 코어 약 60~110 · 꽉 참 약 120~135. G0 빚 스캔 10.2 → 약 3~4.5분(부하 무관).

**커밋**: K1a(⑴ + 스모크 + 미러 → 봉인) · K1b(⑵ + 옛 게이트 대조·주입 + 미러 → 봉인). 규범 변경 0.

### C2 — 개정마다의 pre-gate 를 리뷰 다발과 병렬로

**바꾸는 것**: `D` s006/b9 **R-3432**(현재 revision 4) revision 5 · amendment:

> 리뷰 반영·개정 수신마다 — 그 개정을 확인 리뷰 다발에 보내면 pre-gate 를 **같은 응답에서 백그라운드로** 함께 띄우고(병렬 정의 R-0214 — 따로 앞세운 직렬 실행 금지), 결과는 다음 architect 반영 입력에 노트와 함께 싣는다(red 의 반송 의무·처분 기재는 그대로). 다발을 보내지 않는 개정(G1 override 반영 · 발주자 답 표기 반영)은 곧바로 돌린다.

- (v2 의 «재리뷰 멈춤 기준의 확인 1회와도 …» 구절은 K2a 에 두지 않는다 — 아직 없는 규범을 가리키므로 C3 규범 문안(K2b)이 «확인 1회 다발과 pre-gate 를 같은 응답에서» 를 스스로 적는다.)
- 배너 근거(최종본 `--check-report` exit 0) · 캐시 skip(R-3445) · 차단 모드 무변. `DX` :123 미러(«리뷰어 전부 spawn → shell pre-gate → wait»).
- **fail-closed**: red 인 판은 배너·dispatch 근거가 될 수 없다. 백그라운드 결과 전 architect 반영 호출 금지.
- **품질 보존**: 실행 횟수·판정 경로·반송 의무가 같고 배치만 바뀐다.
- **검증**: 세션 기록 반사실 — 8-C-0 run 6~12(다발 앞 직렬 · 임계 48.4분)의 red 는 전부 같은 #188 filtered 1건이었다. 문면 리뷰.
- **절감(부하별)**: «남은 pre-gate 시간 × 다발 앞 직렬 횟수»라 기계가 바쁠수록 크다 — 8-C-0 판형 7회 × (빈 코어 약 3.5 · 꽉 참 약 7.5) = **약 25~50분** [추정]. C3 과 약 10분 겹친다.
- **울타리**: 병렬 pre-gate 산출(`pregate-report.md` · `pregate-run-<n>.txt`)은 C4 허용 목록에 이름으로 있다. pre-gate 는 sink 를 스크래치로 격리하므로(`run_gate` `DJR_FINDINGS_JSON`) 작업 트리에 다른 파일을 쓰지 않는다.
- **커밋**: K2a(지금).

### C3 — Phase 1 재리뷰 상한

**바꾸는 것**: `D` s006 에 새 블록 «4′ 재리뷰 상한»(b5 R-0230~R-0233 와 b6 R-0234 사이) — 새 규범 3(ISSUED · 기준 Permission · 두 갈래 Obligation · 확인 모드 Obligation) + 수정 모드·반송 G1′(s009/b3 **R-0418**)에 «같은 기준·갈래» 한 구절(revision n+1) + R-0230 에 «재리뷰 상한 ⓐ 는 이 반영 의무의 예외» 한 구절(revision n+1).

> **재리뷰 상한 — 기준**: 한 다발을 받은 뒤 다음이 모두 서면 아래 두 갈래 가운데 하나로만 G1 에 간다.
> ① 활성 lens(G0 승인 lens · 자문으로 붙은 노트 포함) 리뷰어와 discipline lightweight 의 가장 최근 노트가 전부 «집행 가능»(«가능»)이다. «조건부»·판정 1행 없음·«불가»는 불성립. 이번 다발에 없던 lens 의 직전 노트는 그 뒤 개정 diff 가 그 lens 영역(대응표)에 닿지 않았을 때만 인정한다. **arrange 점검(C7)은 이 기준에 들지 않는다**(G1 배너의 전제다).
> ② 열린 발견의 등급이 minor·nit 뿐이다 — 닫힌 대응: blocker·important·major → 불성립 · minor·nit → 후보 · 등급 미기재 → 불성립 · 같은 흠을 lens 마다 다르게 적었으면 가장 높은 등급.
> ③ 마지막 pre-gate 예보가 red 가 아니거나 red 전건이 처분 기재돼 수정할 것이 없다.
> ④ 이번 반영에 새 입력(발주자 답·발주서 개정·main 착륙·STOP 답)이 함께 들어가지 않는다.
>
> **두 갈래(정확히 하나)**
> - **ⓐ 반영 0(기본)**: architect 를 부르지 않는다(R-0230 의 예외). 열린 minor·nit 를 G1 배너에 `미반영 minor·nit k건(목록 · 노트 위치)`으로 싣고 G1 으로 간다. 명세 변경 0 이라 pre-gate 는 캐시 skip 판형이다.
> - **ⓑ 반영 → 확인 정확히 1회**: 열린 항목 가운데 노트가 «G1 전에 닫기»를 적은 것이 하나라도 있을 때만. architect 에 **그 항목들만** 준다 — «입장 표 decision·기계 블록·API/DB 결정·슬라이스 계획을 바꾸지 않는다 — 바꿔야 끝나는 항목은 반영하지 말고 보고». 보고가 오면 상한 밖(그 항목으로 일반 루프). 반영 뒤 **확인 1회**: 반영된 발견을 낸 lens + 반영 diff 가 닿은 영역의 lens + (블록 해시가 바뀌었으면) discipline 을 **확인 모드**로 한 다발에 부르고, 같은 응답에서 pre-gate 와 arrange 점검(C7 ⓘⓘ)을 띄운다. 통과 = 각 확인 노트의 **판정 «가능» ∧ 새 blocker·important 0** 이다. 통과하면 **더 반영하지 않고** G1 으로 간다 — 확인이 낸 minor·nit 와 반영하지 않은 나머지 항목은 배너 `미반영 …`에 싣는다. 통과하지 못하면(판정 «불가»·«조건부» · 새 blocker·important · pre-gate red — R-3432 반송) 상한을 풀고 일반 루프로 돌아간다.
>
> **확인 모드**(리뷰어 입력에 싣는 문안 — 리뷰어 넷 입력 규범 K3): «반영 diff 가 출발점이다 — diff 가 바꾼 이름·값·결정·표 행이 **명세의 다른 자리**(다른 절의 표·Literal·symbols·입장 표·12-slot)와 맞는지까지 본다. diff 밖의 옛 흠을 새로 찾는 것은 몫이 아니다. 판정 1행과 등급을 적는다.» — 8-C-0 api-R2-3(§4.5 산문 표의 `planning` ↔ 다른 자리 `_FailureStage` Literal · `c11/lens-api.md:36`)은 이 «교차 절» 대조로 잡히는 모양이다.
>
> **배너 1행**: `재리뷰 상한 — 다발 <n> · 갈래 ⓐ|ⓑ · (ⓑ) 확인 lens <목록> · 판정 가능 · 새 blocker·important 0 · 미반영 minor·nit k건 · 반영 diff <전>..<후> 또는 <산출물 폴더>/g1-nit-<n>.diff`.

- **영역 → lens 대응표**: 도메인 판정·애그리거트·불변식·이벤트 → ddd · 계약·HTTP·오류 응답·12-slot → api · 스키마·인덱스·제약·트랜잭션·마이그레이션 → db · 입장 표·패키지/테스트 구조·물리 소유권·기계 블록 → discipline. diff 덩어리가 속한 `##` 절 제목으로 가르고, 못 가르면 활성 lens 전부. **R-0258 은 api·discipline 두 행만 소유한다** — db·ddd 행은 이 규범이 새로 정한다. arrange 는 이 표에 없다(C7 재사용 규칙만 따른다 — `design-C7.md` §3-3).
- 블록 해시는 생략 조건이 아니라 확대 조건(바뀌면 discipline 추가)으로만 쓴다.
- 리뷰어 어휘(blocker/important/nit)와 레인 노트의 minor·major·«조건부»는 위 닫힌 대응이 흡수한다. 리뷰어 규범에 minor 를 더하는 통일은 선택(K3).
- **규범의 성격**: 기준이 서면 «ⓐ 또는 ⓑ» 가운데 하나만 허용된다 — «반영 → 확인 없이 G1»은 기준이 선 다발에서 더는 허용되지 않는다. 기준이 안 서면 지금 규범 그대로다.
- **시간 — 오늘보다 느려지지 않는 근거**: ⓐ 는 반영 사이클(architect 호출 + pre-gate · 8-C-0 개정 8·9 각 약 10~20분) 하나를 통째로 던다 — 오늘 레인(반영 뒤 바로 G1 · 또는 반영 뒤 전체 재리뷰)보다 빠르거나 같다. ⓑ 는 리뷰어가 «G1 전 닫기»를 적은 때만이고, 확인은 G1 직전에 어차피 도는 최종 pre-gate·arrange 점검과 같은 응답에서 병렬이라 더하는 시간은 «확인 − 그 둘 중 긴 것»(약 0~10분)이다. 그 대가로 «검토 안 된 변경이 G1 에 닿는» 길(재검토 major 1 · B1)이 닫힌다. 8-C-0 은 ⓑ 로 약 34분 빨라진다.
- **fail-closed**: ①~④ 판별 불가면 상한 밖(지금 규범). 확인 다발은 C4 울타리 창 안. 확인 응답에 판정 1행이 없으면 통과가 아니다.
- **품질 보존**: G1 에 닿는 명세 변경은 모두 그 발견을 낸 lens 가 교차 절까지 본 것이다. 결정이 바뀌는 반영은 architect 보고로 상한 밖이 된다. ⓐ 에서 남는 minor·nit 는 배너에 목록으로 보여 G1 결정자가 본다(지금은 반영된 채 아무도 안 본다).
- **검증**: 역재생(§1-3 · 7레인 · 반례 없음) · 구현 뒤 같은 판정 규칙을 노트 파서로 고정해 다음 레인마다 «기준 성립 다발 · 갈래 · 확인 lens · 확인 새 발견»을 기록한다.
- **측정**: «전원 집행 가능 → G1 제출 분»(8-C-0 76.0 → 약 40) · 갈래 분포.
- **절감**: 8-C-0 약 −34분(ⓑ · 사이클 19.8 + 14.5 [검토]) · 보관 레인 여섯 0 이하(ⓐ 면 반영 사이클이 빠짐 — 레인별 값은 재지 않았다). 겹침: C2 약 10 · C4 약 7 · C11 K1 ≤8(K1 보류로 지금은 0).
- **커밋**: K2b — 리뷰어 어휘 통일·확인 모드 입력 문안(K3)과 함께 묶거나 K3 뒤.

### C4 — 리뷰어 노트 직접 기록 · 쓰기 울타리

**바꾸는 것(Claude)**

- 리뷰어 넷 `tools:` 에 `Write`. ddd·api·db 는 규범 없는 블록 `s001/b3` · discipline 은 규범 블록 `s001/b1`(R-0831~R-0833) 안 — 규범 문장이 바뀌지 않으므로 revision 없이 렌더·LEDGER 만. `claude plugin validate dddjango --strict`.
- 부속 기록 예외(§2-1) 넷 · 산출 규범 개정 ddd **R-3370** · api **R-2617** · db **R-3325** · discipline **R-0863**:
  > 부속 기록 경로를 받으면 노트를 그 경로 한 곳에만 새 파일로 쓰고 `기록: <경로> · sha256 <값>` 과 `집행성 판정: <…>` 을 답한다. **경로를 받지 않은 호출(모드 불문)에서는 어떤 파일도 쓰지 않는다** — 노트는 응답으로 낸다. git 쓰기 명령 0. 스크래치는 입력의 `$TMPDIR/<폴더명>-<lens>/` 만 쓴다.
- Coordinator `D` s006/b3 **R-0223**·**R-0224** 개정 + 새 블록 «쓰기 울타리»(Obligation 1):
  > **쓰기 울타리**: 울타리 대상 역할(리뷰어 넷 · acceptance-tester Phase 1 arrange 모드)의 **모든 호출** — 모드 불문 · 첫 호출 · 형식 반송 재호출 · SendMessage 이어 부르기 — 은 울타리 창 안에서만 한다. 창 = 그 호출 **앞 응답**에서 before 스냅숏을 끝내고, 호출이 돌아온 뒤 after 스냅숏으로 닫는다. architect·coder 호출은 울타리 밖이다(§2-1 3번).
  > 스냅숏(작업 트리 루트에서 · 산출물 폴더 = `<BF>`):
  > ```sh
  > cd "$(git rev-parse --show-toplevel)"; idx="$TMPDIR/<폴더명>-fence-<n>.idx"; objs="$TMPDIR/<폴더명>-fence-objs"; mkdir -p "$objs"
  > cp "$(git rev-parse --git-path index)" "$idx"
  > env GIT_INDEX_FILE="$idx" GIT_OBJECT_DIRECTORY="$objs" GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects" \
  >   sh -c 'git add -A && git add -f -A -- "$0" && git write-tree' "<BF>"
  > ```
  > 출력 트리 SHA 를 before/after 로 적는다. 대조 = 같은 `env` 로 `git diff-tree -r --name-only -z <before> <after>`. `git add -f -A -- <BF>` 는 `.dddjango/` 를 무시하는 저장소(`D:26` 허용)에서도 산출물 폴더를 담는다. 객체는 `$TMPDIR` 의 별도 폴더에만 쓰여 `.git`(linked worktree 면 주 저장소 공통 `.git`) 쓰기가 0 이다.
  > 허용 = 이번 창의 부속 기록 경로 + 병렬 pre-gate 산출(`pregate-report.md` · `pregate-run-<n>.txt`) + 코디네이터 쓰기 목록(창 열 때 적음 · 되도록 창 뒤로 미룬다). **창 안에서는 작업 트리에 쓰는 코디네이터 명령(검사기 직접 실행 · 시험 · 커밋 · stash) 0** — 검사기를 꼭 돌려야 하면 `DJR_FINDINGS_JSON=$TMPDIR/<폴더명>-findings-<n>.jsonl` 로 sink 를 저장소 밖에 두고 `DJR_VIOLATIONS_DIR` 를 비운다(직접 실행은 `.dddjango/violations/*.jsonl` 을 원자 게시한다 — `findings.py` `_publish`). 그 밖의 경로가 나오면 그 창의 기록을 무효로 하고 멈춰 `STOP_FOR_USER_APPROVAL`(«쓰기 울타리 위반 — <경로>»)로 올린다(자동 되돌림 없음).
  > 기록 확인: 응답의 sha256 = 파일 sha256 · 머리의 lens = 경로의 lens(다르면 lens 간 덮어쓰기 — 반송 · 새 창). 배너 다발 크기 행에 `울타리 차이 = 기록 k개 · 코디네이터 쓰기 j개`.
  > **창은 배타적이다**: 창 동안 같은 워크트리에 다른 쓰기 역할(coder · acceptance-tester Phase 2 · architect)을 파견하지 않는다.
- **R-0282**(«감사 범위와 다음 슬라이스 작업 파일이 겹치면 감사 완료 후 배차» — 같은 블록의 «겹치지 않으면 병렬 배차 가능»)에 «단 쓰기 울타리 창(Write 를 가진 감사)과는 병렬 배차하지 않는다»(revision n+1). R-0278 무변. 손실: 8-C-0 은 0(S1 감사가 S1 창 안에서 끝남 [실측]) · 다른 레인 감사 1회 길이(약 6~14분)가 상한 [추정].

**바꾸는 것(Codex)**: 역할 스킬 `dddjango-design-review-{ddd,api,db}`·`dddjango-discipline-reviewer` 산출 절에 같은 문장(«git 쓰기 명령 0» 명시) · `DX` Phase 1 step 2·Phase 2 감사에 울타리 미러.

**울타리가 보는 범위**: 작업 트리의 추적·미추적(무시 안 된) 파일 + **산출물 폴더 전부(무시돼도)**. 그 밖의 무시 경로(`.venv/` 등)와 저장소 밖 쓰기는 보지 않는다 — 리뷰어 스크래치를 `$TMPDIR/<폴더명>-<lens>/` 로 정해 준다.

- 스냅숏 시험 [실측 scratch `speed-t1/fence-test`·`fence-test3`]: linked worktree · `.gitignore` 에 `.dddjango/` · 하위 폴더 cwd 에서 before → 창 안에서 허용 기록 새로 씀 · 무시된 `.dddjango/b/design-spec.md` 에 한 줄 · 추적 파일 수정 뒤 **커밋** · `.venv/` 에 씀 → after. `diff-tree` = `.dddjango/b/design-spec.md` · 기록 · `a.txt`(커밋분) 셋, `.venv/z` 없음. 스냅숏 한 번 동안 주 저장소 `.git` 아래 바뀐 파일 **0**(객체는 별도 폴더에 6개). 재검토는 field 크기 복제본(2.5G)에서 스냅숏 0.93초를 쟀다.
- **fail-closed**: 기록 파일이 없거나 sha256·lens·판정이 응답과 다르면 반송(새 창). 스냅숏을 못 뜨면 호출하지 않는다.
- **품질 보존**: 노트 내용·작성자·독립성·«명세·코드 수정 금지»가 같다. 리뷰어 넷의 `mcp__serena__*` 에는 오늘도 편집 도구가 들어 있으므로(§7-2(b)) 울타리는 오늘보다 순증이다.
- **검증(리허설)**: 작업 트리 플러그인(Claude `--plugin-dir <repo>/dddjango` · Codex 로컬 스킬)으로 pregate 픽스처 명세 다발 1회 → 기록 4 · 울타리 차이 = 기록 4 · 전사 0 · sha256·lens 일치. 음성 대조: (a) 창 안 추적 파일 수정 뒤 커밋 (b) 이미 수정된 명세 재수정 (c) lens A 가 B 경로에 씀 (d) 창 밖 SendMessage 재기동 (e) `.dddjango/` 무시 저장소에서 명세 수정 (f) 창 안 코디네이터 검사기 직접 실행(sink 미격리 → STOP · 격리 → 통과).
- **절감**: 약 −35분(8-C-0 메인 전사 38.7) − C3 겹침 7 = 약 −28.
- **커밋**: K3(C5 와 함께) — 리허설 뒤.

### C5 — 리뷰 처분을 명세 밖 lens 별 파일로

- Coordinator `D` s006/b5 새 규범 2(Prohibition: 반영 호출에 명세 안 처분 표·이력 절 요구 금지 · Obligation: 처분은 architect 가 부속 기록 `review-disposition-<lens>-<n>.md` 에 쓴다 — 발견 ID · 반영/거절/받아들임 · 명세 위치 · 까닭 한 줄. 확인 리뷰에는 명세 + **그 lens 의** 처분 파일 · 직전 자기 노트 · 명세 diff 를 준다).
- architect **R-1751** revision 2 · redefinition: 괄호 «결정 이력은 Coordinator 대화·게이트 배너가 가짐» → «결정 이력은 게이트 배너와 부속 기록(lens 별 처분 파일)이 가진다 — 명세 밖».
- architect 부속 기록 예외(§2-1 · 대상 R-1568). architect 는 울타리 밖이고 응답에 `기록:` 행(처분 파일마다)을 싣는다.
- Coordinator **R-0220** 개정: «확인 리뷰에서는 그 lens 처분 파일 · 직전 자기 노트 · 명세 diff 를 더 준다 — 다른 lens 것은 주지 않는다».
- 리뷰어 입력 규범 ddd R-3368 · api R-2614 · db R-3323 · discipline R-0862 에 같은 구절 + 닻 효과 가드 + (C3) 확인 모드 문안.
- **품질 보존**: 처분 정보는 옮길 뿐 남는다 · lens 별 파일이 독립성(R-0220)에 더 맞는다 · 명세 diff 로 다른 lens 반영 변경도 본다.
- **검증**: C4 리허설 판에서 확인 리뷰 1회. 크기: 개정 15 §17 = 82,953B · 2.87만 토큰(15.7%).
- **절감**: −15~−35분(로드맵 승계). **커밋**: K3.

### C6 — 규범 변경 없음

- §1-2 근거.

### W1 — Codex `wait_agent` timeout 권장값

- `CX:34` · `DX:26` «대기 정책»에 한 문장: «`wait_agent` 는 `timeout_ms` 를 300000(5분)으로 준다 — «timeout_ms must be at most …» 오류면 오류 문구의 상한으로 다시 부른다. 끝나면 timeout 과 무관하게 곧바로 돌아온다. «30분+ 무진행» 실측은 timeout 반환마다 산출물 크기·mtime 으로 한다».
- 근거: Codex 0.159.2 `features.multi_agent_v2.{min,max,default}_wait_timeout_ms` · 상한 검증 · «returned due to timeout before any agent reached a final status» 필드 [실측 `strings`].
- 검증: 구현 전 Codex 세션 1회(상한 · 즉시 반환). 절감: 모델 분 P1 약 65 · P2 약 44 가운데 대부분 · 벽시계는 작다.
- 커밋: `DX` K5(지금) · `CX` W8e.

### W2 — 시안 미리보기 장식 판별 · 제품 모드 캡처 기준

**지금 가능**

- `design-acquisition.md` §3 4번(:55-57) 뒤 한 단락(Codex byte 미러):
  > 원본 렌더에 앱 화면이 아닌 **미리보기 장식**(기기 틀·노치·상태줄·홈 막대·캔버스 배경·목업 그림자)이 있는지 판별해 기록한다. 장식이라고 판정하려면 근거를 인용한다 — 원본의 미리보기 전용 컴포넌트·프레임 설정·런타임 옵션(예: P2 의 미리보기 전용 `AppFrame fit=device`), 또는 발주서·사용자 지목 문장. **이미지 단독 시안**(정상 입력 — `CX:190`)은 원본 설정 근거가 없으므로, 기기 틀로 보이는 요소가 있으면 G0 에서 한 번 «장식인가»를 묻고 그 답을 근거로 쓴다. 근거가 없으면 그 요소는 앱 요소로 보고 비교 기준에 남긴다. 원본에 장식 없는 **제품 모드**가 있으면 그 모드의 캡처가 비교 기준이다. 없으면 장식을 뺀 앱 콘텐츠 경계로 크롭하고 장식 영역·근거·크롭 경계·«제품 모드 없음»을 `visual-check.md` 에 남긴다. 장식을 구현 대상으로 옮기지 않는다.
- design-review-web «G0 입력범위 모드»(:25)와 Codex 같은 절에 1구절: «원본 캡처·렌더에 미리보기 장식이 섞였는지, 장식 판정에 근거(원본 설정 · 발주서·사용자 문장 · 이미지 단독이면 G0 답)가 있는지, 비교 기준이 제품 모드 캡처(없으면 앱 경계 크롭 기록)인지 대조한다 — 섞였거나 근거·기준 기록이 없으면 입력 부족».

**8e 뒤**: `CX:188` · `CL:166` 에 «미리보기 장식 판별(근거)과 비교 기준도 남긴다(`implementation-ui` design-acquisition §3 4번)».

- 품질: 검사를 더한다 · 근거 없는 장식 판정을 막아 앱 요소 누락이 통과하지 않는다. 검증: P2 G0 캡처 사본 리허설(정답 = 반송1 #1·#2 · 음성 = 앱 머리·탭) · `make verify-web`. 절감: P2 약 −50~−65분 · P1 0.

### W3 — inputs 검사 기록 한 줄화(검사 두 번 유지)

**8e 뒤** — 기록을 읽고 쓰는 줄 전부(Claude·Codex):

- `CX:234` · `CL:211`(Coordinator 호출 전 inputs) → 한 명령(에이전트 답 글 없음 — 검사기 출력은 파일에서 읽어 printf 의 **인자**로만 들어가고 서식 문자열은 고정이다):
  ```sh
  out="$TMPDIR/<산출물 폴더명>-inputs-$$.out"; <Python> <checker> --build <산출물 폴더> --project-root <루트> --phase inputs > "$out" 2>&1; ec=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "coordinator" "<슬라이스>/<회차>" "$ec" "$(tr '\t\n' '  ' < "$out")" >> <산출물 폴더>/inputs-log.tsv
  cat "$out"; echo "inputs-log 행 $(wc -l < <산출물 폴더>/inputs-log.tsv | tr -d ' ')"; rm -f "$out"; (exit "$ec")
  ```
- `CX:235` · `CL:212`(코더 반환 대조) → «코더 반환의 칸(시각 · `coder` · 슬라이스/회차 · exit · input_digest · 첫 변경 전 순서 준수/위반 요지)을 **Write 도구로** `$TMPDIR/<산출물 폴더명>-coder-row-<n>.txt` 에 한 칸 한 줄로 쓰고(칸 안 탭·줄바꿈 없음), `paste -sd '\t' "$TMPDIR/<산출물 폴더명>-coder-row-<n>.txt" >> <산출물 폴더>/inputs-log.tsv` 로 붙인 뒤 자기 행 digest 와 대조한다» — 응답 원문(백틱·`$`·`%`·따옴표)이 셸 인자로 해석되는 길이 없다. 이 문단은 8e 뒤 `verify-web` 이 Claude·Codex 문단 byte 를 대조하므로 치환 둘(`${CLAUDE_PLUGIN_ROOT}`→`${SKILL_DIR}` · `Bash로`→`네이티브 셸로`)만 다르게 미러한다.
- `CX:202` · `CL:179`(검증 기록 판형 ②) → «매 coder 호출의 Coordinator inputs·코더 반환 inputs 실행 기록은 `inputs-log.tsv`(호출마다 1행 · 칸 = 시각·실행자·슬라이스/회차·exit·출력)에 둔다».
- coder-web `coder-web.md` `:26`(입력 «`inputs-log.tsv:<행>`») · `:45`(«인계된 `inputs-log.tsv` 행을 직접 읽어» — 부재 반송 그대로) · `:46-47`(자기 inputs 실행 무변) · `:48`(주어 Coordinator 유지: «Coordinator 가 자기 현재 호출 기록과 대조해 `inputs-log.tsv` 에 coder 행으로 싣는다. `inputs-log.tsv` 작성 소유는 Coordinator 다» — coder 는 쓰지 않는다) + Codex `dddjango-web-coder-web/SKILL.md` 같은 줄. coder 는 반환에 자기 `input_digest` 를 싣는다.
- 품질: 검사 두 번·순서 의무 그대로 · digest 대조 추가 · exit 보존 · 응답 원문 셸 해석 0. 검증: 검토 `w3/` 판형 재현(exit 2 → 2 · 동시 두 레인 분리 · 탭 든 출력 5칸 · 백틱·`$`·`%` 든 coder 칸이 글자 그대로 들어감) → `make verify-web` → P1 기록 재생. 절감: P1 약 −7 · P2 약 −12~−20분. 커밋: W8e.

### W4 — G2 전 린트·포맷·타입 고정 절차(빌드 폴더 포함)

**8e 뒤**: `CX:241` · `CL:218` «대상 프로젝트의 기존 타입/린트 검사가 있으면 변경 범위의 신규 위반도 검사한다» →

> **설정 감지(도구마다)**: ruff = `pyproject.toml [tool.ruff]` · `ruff.toml` · `.ruff.toml` · mypy = `mypy.ini` · `.mypy.ini` · `pyproject.toml [tool.mypy]` · `setup.cfg [mypy]`. 한 도구의 설정이 없으면 «<도구> 설정 없음 — 생략» 1행(다른 도구는 그대로).
> **실행기**: 이미 있는 환경만 쓴다 — `uv run --frozen --no-sync <도구>`(uv 프로젝트 · lock·sync 를 하지 않아 `uv.lock`·`.venv` 무변) → 없으면 `.venv/bin/<도구>`. 첫 줄에 버전 기록. 설정은 있는데 이 형태로 실행이 안 되면 **STOP**(생략 금지).
> **mypy 기준선(Phase 2 진입)**: `pre_run_head` 를 적는 바로 그 순간(작업 트리 = 진입 상태) 프로젝트가 정한 mypy 명령(pre-commit 훅 · Makefile · pyproject 주석이 정한 대상 — 현장 예 `mypy spring_dream_server framework`)을 위 실행기로 한 번 돌려 `<산출물 폴더>/mypy-baseline.txt` 에 남긴다(명령 · 버전 · exit 포함). G2 전에는 같은 명령을 한 번 돌려 (파일 · 오류 코드 · 메시지 — 메시지 안 `line <숫자>` 는 `line N` 으로 정규화) **개수 차**가 신규다. 기준선 파일이 없는 실행(이 규칙 전에 시작한 재개 등)은 `git archive <pre_run_head> | tar -x -C "$TMPDIR/<폴더명>-prerun"` 에 레인 실행기(`.venv/bin/mypy`)를 그 폴더 cwd 로 돌리고(`uv run` 금지 · 끝나면 폴더 삭제) 그 결과를 기준선으로 쓴다. `pre_run_head` 도 기준선도 없으면 결과 전부를 신규로 보고 배너에 «mypy 기준선 없음 — 전부 신규»로 올린다. 정한 명령이 없으면 «mypy 대상 미정 — 생략».
> **ruff**: 대상 = `git diff --name-status --diff-filter=d -M <pre_run_head> -- '*.py'`(삭제 제외 · rename 은 옛 경로와 짝) ∪ 미추적 `.py`(빌드 폴더 포함). 명령 = `ruff check --force-exclude --output-format json <대상>` · `ruff format --check --force-exclude <대상>`. 옛 판 = `git show <pre_run_head>:<옛 경로> | ruff check --force-exclude --output-format json --stdin-filename <새 경로> -`. **신규** = 파일마다 (code · message) 개수 차 · 새 파일은 전부 · format 은 파일 단위(옛 통과·새 불통과 또는 새 파일 불통과). `pre_run_head` 가 없으면 대상 = 이번 실행 슬라이스 보고 파일 ∪ 빌드 폴더 `.py` · 결과 전부 신규(fail-closed).
> 신규 0 이 G2 배너 조건이다. 명령·실행기 버전·exit·신규 수를 `visual-check.md` 에 남긴다.

- **mypy 판형 선택 근거**: 옛 판 `git worktree add` 는 G2 재제출 때 같은 경로에 두 번째로 `fatal: … already exists` · exit 128 이고 등록이 공통 `.git/worktrees/` 에 쌓인다[재검토 실측 `w4uv/`] · 미추적 `.env` 같은 설정이 없어 Django mypy 플러그인 결과가 뒤틀린다 · G2 시도마다 strict mypy 두 번(옛 판은 캐시 없음). «진입 때 기준선»은 같은 환경·같은 미추적 설정에서 한 번 돌고, G2 마다 한 번만 더 돈다. 선례: core 레인 8-C-0 은 G0 에 이미 `baseline-static.sh` 로 mypy·ruff 기준선 파일을 남겼다(`baseline-mypy.txt` — «Found 8 errors in 2 files (checked 7409 source files)» [실측]). `git archive` 는 기준선이 없을 때의 대체만 맡는다(등록 0 · pre-gate 와 같은 판형).
- `uv run` 판형 근거: 기본 `uv run` 은 실행 전에 lock·sync 를 해 추적 파일 `uv.lock` 을 다시 쓴다[재검토 실측 — 해시 `3567e96325db` → `d12ce07d4d47` · `git status` 에 ` M uv.lock`] · `--frozen` 은 lock 무변.
- 품질: 검사를 더한다 · 제외 설정을 지켜 가짜 신규로 막지 않는다(검토 `w4/` 재현 0건) · 검사 단계가 제품 파일을 바꾸지 않는다.
- 검증: 검토 `w4/`·`w4uv/` 판형 재현(제외 0 · 다중집합 · 삭제·rename · 실행기 부재 STOP · `uv.lock` 무변 · 재제출 두 번 성공) → P1·P2 정적 반송 직전 G2 제출 커밋 scratch 재생(ruff 48·225 · format 32·17).
- 절감: 레인당 coder 정리 약 13~15분 − G2 시도당 mypy 1회 + 진입 기준선 1회(레인 프로젝트 크기에 따라 수 분) = 약 −5~−13분 [추정]. «반송 회피»는 주장하지 않는다.

### O1 — 발주서 빚 방침 한 줄(플러그인 변경 없음)

- 발주 템플릿에 `빚 방침: ⓐ 먼저 정리(B1 · 2026-09-26)` 한 줄 — 규칙은 이미 `발주 고정 ⓐ <발주서:행>` 을 받는다(`D:84` · `D:221` · `CX:175`). 측정: G0 결정 줄 `출처 = 발주 고정 ⓐ` · 빚 질문 대기 0.

## 4. 커밋 묶음

| 묶음 | 내용 | 언제 | 검증 |
|---|---|---|---|
| **K1a** | C1⑴ + `git_touched_smoke.py` + 미러 | **지금(구현 시작)** · `Makefile` hunk 는 8e 와 다름 | verify · 스모크 · 변이 |
| **K1b** | C1⑵(빈 코어 워커 · `getloadavg` 대체 포함) + 옛 게이트 대조·주입 + 미러 | K1a 뒤 | verify · 현장 재생 21판 |
| **K2a** | C2(R-3432 rev 5 · C3 언급 없음) · `DX` | 지금 | verify · rulepack |
| **K2b** | C3(새 규범 3 · R-0418 · R-0230) · `DX` | K3 와 함께 또는 뒤(확인 모드 입력 문안이 리뷰어 규범에 들어간다) | verify · 노트 재생 |
| **K3** | C4 + C5 + 부속 기록 판형·예외 — 리뷰어 넷 ttl · architect(R-1751 rev 2 · 예외) · Coordinator(R-0220·R-0223·R-0224 · 울타리 블록 · s006/b5 새 규범 2 · 부속 기록 판형 · R-0282) · 역할 SKILL·`DX` | 작업 트리 플러그인 리허설 뒤 | verify · validate --strict · 리허설 |
| **K5** | W1 core(`DX:26`) | 지금 | 문면 리뷰 · Codex 확인 1회 |
| **Wn** | W2 참조 문서 · design-review-web | 지금 | verify-web · P2 리허설 |
| **W8e** | W1 web · W2 Coordinator 줄 · W3 · W4 | 8e 커밋 뒤 | verify-web · `w3/`·`w4/`·`w4uv/` 재현 · P1/P2 재생 |
| (C7) | `design-C7.md` — K3·K2b 뒤 · 리허설 뒤 · K2(설계 K)와 표기 동기 | | 리허설 |

- 모든 규범 묶음은 §2 체크리스트(wiring 등재 포함) · 묶음마다 봉인 chore. core 릴리즈는 8-C-0 착륙 뒤 · web 릴리즈는 W8e 뒤.

## 5. 절감 — 정직한 수치와 겹침

| 항목 | 8-C-0 판형 [추정] | 다른 레인 | 비고 |
|---|---|---|---|
| C1⑴ 빚 스캔 | −6~7분 | 같은 크기 | G2 직접 실행도 비슷 |
| C1⑵ pre-gate | 빈 코어 −25~−75 · 꽉 참 −0~−15 | web registry_gate 같은 비율 | 부하 기록 필수 |
| C2 | 빈 코어 약 −25 · 꽉 참 약 −50 | 다발 앞 직렬 횟수에 비례 | C3 과 약 10 겹침 |
| C3 | −34(ⓑ) | 0 이하(ⓐ) | C2 10 · C4 7 겹침 |
| C4 | −35 | 전사량에 비례 | C3 7 겹침 · Phase 2 배타 손실 8-C-0 0 |
| C5 | −15~−35(로드맵 승계) | | |
| W1 | 모델 분 P1 약 65 · P2 약 44 | | 벽시계 작다 |
| W2 | — | P2 −50~−65 | W4 와 이중 주장 안 함 |
| W3 | — | P1 −7 · P2 −12~−20 | |
| W4 | — | 레인당 −5~−13 | mypy 실행 비용 뺌 |
| C7(2순위) | −50~−200 | 결함 없는 레인 −0~+35(단독 1회가 임계에 얹힐 때) | `design-C7.md` §5 |

- core 1순위 합(8-C-0 판형 · 겹침 뺌): 빈 코어 약 **120~190분** · 꽉 참 약 **120~155분**(C1⑵ 몫이 줄고 C2 몫이 는다).

## 6. 열린 쟁점(사용자 판단만)

- 없음. C3 의 두 갈래와 선택 규칙(ⓐ 기본 · ⓑ 는 노트가 «G1 전 닫기»를 적었을 때만)은 사용자 의도(«전체 재리뷰 루프를 더 돌지 않는다»)·«품질 양보 불가»·재검토 지시(«오늘보다 느리지 않게»)에서 답이 나왔다.

## 7. 후속 · 설계 밖 발견

### 7-1. 후속(이번 설계 밖)

- domain-model 검사기 자체 속도 · pre-gate 격리 사본 고정비(약 150초) · C1⑶ · C9.
- C7 의 결정적 슬라이스-import 검사는 K2(X2)가 소유한다(`design-C7.md` §7).

### 7-2. 설계 밖 발견(고치지 않음 · 기록만)

- **(a) registry_gate·pre-gate 안에서 idempotency 검사기는 발화하지 않는다.** `_snapshot_current` 가 `.*` 를 빼서(`_IGNORE_COPY` `".*"` · :166) 현재 스냅숏에 `.dddjango/*/scope.md` 가 없다 → 늘 exit 0. 앵커 스냅숏(`git archive`)에는 추적된 `.dddjango/` 가 있어 앵커 쪽만 발화할 수 있다(L 에만 실려 «해소»로 보인다). 재현: 미요청 scope + 미추적 `idempotency_record.py` → 직접 실행 exit 2 · 같은 트리 registry_gate 표 `0 | 0` [검토 실측 `repos3/idem`]. G2 직접 실행(`D` :163)이 막으므로 게이트 구멍은 아니다.
- **(b) 읽기 전용 리뷰어의 `mcp__serena__*` 에 편집 도구가 들어 있다.** `replace_symbol_body`·`replace_in_files` 등 — 8-C-0 리뷰어 세션 56/56 에 정의가 실렸다(사용은 읽기뿐) [검토 실측]. 대상 저장소·레인 워크트리에 `.serena/project.yml` 이 있다. 같은 모양: 8-C-0 Phase 2 acceptance-tester 가 제품 코드에 `find_symbol` 16회(R-3242 흐림).
- **(c) G1 직전 «반영 뒤 무확인» 길(기준 밖).** 보관 레인 다섯은 important·«조건부»가 열린 채 반영 한 번 뒤 확인 없이 G1 으로 갔다(`c3-replay/result.md` 관찰 1). C11 진단의 «막는 발견의 63~69% 가 개정이 만든 흠»과 겹치면 이 길의 위험이 C3 영역보다 크다. C3 은 기준 안만 닫는다 — «G1 직전 마지막 반영의 확인 1회» 일반화는 K1 과 함께 품질 과제로 남긴다.

## 8. 처분

### 8-0. C1 확정(구현 시작 — v2 설계 + 두 수정)

C1 은 v2 설계 그대로 구현한다. 재검토(도구)가 짚은 두 곳만 고친다.
- ① **스모크 ⑳ 기대값**(재검토 N5): «하위 트리 결손 → exit 1»은 틀렸다 — cache-tree 가 유효하면 `git diff --quiet HEAD -- <경로>` 가 하위 트리를 읽지 않아 옛·새 모두 exit 0 이다[재검토 실측 `repos4/`]. ⑳ 은 «루트 트리 결손(후보 유/무) → exit 1» 과 «하위 트리 결손 + 같은 폴더 스테이징(cache-tree 무효) → exit 1» 둘로 좁힌다. 변이 «트리 질의 생략 → ⑳ red» 는 루트 트리 결손 사례로 판정한다.
- ② **`os.getloadavg` 대체**(재검토 N7): `_workers()` 는 `except (OSError, AttributeError)` 로 받고 그때 `cpu_count // 2`(최소 1)를 쓴다 — Windows 등에서 registry_gate 가 시작 전에 죽지 않는다.

### 8-1. v1 → v2 처분(1차 검토)

**절차 검토(`review-t1-proc/review.md`)**

| 지적 | 처분 | 근거 |
|---|---|---|
| B1 블록 해시 판별 · 절감 76→15 | 받음 → v3 에서 두 갈래로 닫음(8-2) | api-R2-3 · 해시 변화[실측] |
| M1 표본 1레인 | 받음: 6레인 추가 | §1-3 |
| M2(a)~(d) 울타리 넷 | 받음: 트리 스냅숏 · 범위 · sha256·lens · 모든 호출 새 창 | `fence-test` |
| M3 모든 모드 | 받음 | — |
| M4 Phase 2 병렬 | 받음(창 배타 · R-0282 — 재검토가 R-0282 가 맞다고 확인) | — |
| M5 R-1568·R-1751 | 받음: 부속 기록 예외 · R-1751 rev 2 redefinition | §2-1 |
| M6·M7 (C7) | 받음 | `design-C7.md` |
| M8 W3 누락 줄 | 받음 | §3 W3 |
| m1~m20 · nit 셋 · 절감 표 · 차례 | 전부 받음 | v2 본문 |

**도구 검토(`review-t1-tool/review.md`)**: F1~F13 전부 받음(바이트 병합 · W4 교체 · W3 명령 · C7 재사용 키 · exit 보존 · submit+wait · 옛 게이트 대조 · 빈 코어 워커 · 스모크 보강 · 울타리 범위 · ⑶ 수치 · 설정 목록 · 인덱스 키) · 관찰 idempotency → §7-2(a). 반박 0.

### 8-2. v2 → v3 처분(재검토)

**절차 재검토(`review-t1-proc/rereview.md`)**

| 지적 | 처분 | 근거 |
|---|---|---|
| major 1 C3 허가/의무 모호 · 일부 레인 느려짐 · §1-3 birth-input 비용 누락 | 받음: 두 갈래 ⓐ(기본)/ⓑ(G1 전 닫기 적은 항목 있을 때만 · 확인 정확히 1회) · R-0230 예외 · §1-3 «최대 +29분» 복원 · 시간 근거 | `lane-birth-input.md:73` · discipline-7 `:3` |
| major 2 C3 ① ↔ C7 ⓘⓘ 서로 기다림 | 받음: arrange 를 ① 에서 뺌 · C7 ⓘⓘ = ⓑ 확인 다발 · ⓘⓘ′ = 배너 직전 단독 1회 · 배너 판정 sha = G1 명세 sha | `design-C7.md` §3-3 |
| major 3 판형이 architect 에 안 맞음 | 받음: 울타리 대상 역할만 · architect 는 밖(응답 `기록:` 행 sha256 대조 · 그 밖 쓰기는 R-1568 · 창 동안 파견 0) · 판형 2번을 경로 목록·`기록:` 행(들)로 | §2-1 |
| major 4 `.dddjango/` 무시 저장소 | 받음: `git add -f -A -- <BF>` | `fence-test3` 재현 — 무시된 명세 수정을 잡음 |
| m1 확인 모드 정의 | 받음: «diff 출발 · 교차 절 대조» 문안(리뷰어 입력 규범 K3) | api-R2-3 = 교차 절 흠 |
| m2 확인 통과에 판정 «가능» | 받음 | — |
| m3 공유 `.git` 객체 쓰기 | 받음: `GIT_OBJECT_DIRECTORY` 별도 · 대체 경로 | `fence-test3` — `.git` 변경 파일 0 |
| m4 코디네이터 자신의 쓰기 | 받음: 창 안 작업 트리 쓰기 명령 0 · 필요하면 sink 를 `$TMPDIR` 로 | `findings.py` `_publish` |
| m5 W4 옛 판 worktree | 받음: 기준선 파일 · 대체는 `git archive` | 재검토 실측 |
| m6 W2 이미지 단독 | 받음: 발주서·사용자 문장 근거 · 이미지 단독이면 G0 한 번 질문 | `CX:190` |
| m7 C7↔K2 문면 동기 | 받음: 표기 소유 = K2 N+1 · 계획 절은 산문 · 한 블록 · 동기 목록 | `design-C7.md` §9 |
| m8 C7 이름·응답 표기 | 받음: `g1-arrange-acceptance-<n>.md` · `기록:` | `design-C7.md` |
| m9 K2a 문안이 C3 를 가리킴 | 받음: 구절을 K2b(C3 문안)로 옮김 | §3 C2 |
| m10 C2 절감 고정값 | 받음: 부하별(25~50) · 꽉 참 합계 상향 | §5 |
| m11 wiring 등재 | 받음: §2 체크리스트 | `djr-shapes.ttl` :119-121 |
| m12 acceptance-tester 예외 불필요 | 받음: 뺌 | C7 새 규범이 «부속 기록 한 파일 말고 쓰기 0» |
| nit discipline revision-clarification 불필요 | 받음: 렌더·LEDGER 만 | — |
| nit coder-web `:48` 주어 | 받음: Coordinator 유지 · 작성 소유 명시 | — |
| nit 확인 뒤 pre-gate red | 받음: 통과 조건에 R-3432 반송 명시 | — |
| 관찰 «반영 뒤 무확인» 일반화 | 기록: §7-2(c) | — |
| §5 K1 보류 → C7 이중 경고는 K2 몫만 | 받음 | `design-C7.md` §5 |

**도구 재검토(`review-t1-tool/rereview.md`)**

| 지적 | 처분 | 근거 |
|---|---|---|
| N1 `uv run` 이 `uv.lock` 재기록 | 받음: `uv run --frozen --no-sync` · 실패면 STOP | 재검토 실측 |
| N2 prerun worktree 재시도 exit 128 | 받음: 진입 기준선 파일 · 대체 `git archive` | 재검토 실측 · 8-C-0 `baseline-mypy.txt` 선례 |
| N3 옛 판 mypy 환경 · 비용 | 받음: 같은 환경 기준선 · 비용을 W4 절감에서 뺌 | §5 |
| N4 C3 ① 가 C7 재사용 우회 · ⓘⓘ 결정 불능 | 받음: major 2 와 같은 처분 · 대응표에서 arrange 뺌 | — |
| N5 스모크 ⑳ 기대값 | 받음: §8-0 ① | 재검토 실측 `repos4/` |
| N6 W3 응답 원문 셸 보간 | 받음: Write 도구로 칸 파일 → `paste -sd '\t'` · 작성 소유 Coordinator | — |
| N7 `getloadavg` · W4 도구별 생략 · ruff json · mypy `line N` · C7 기준선 ③ · E5 로그 | 받음: §8-0 ② · W4 문안 · `design-C7.md` §3-3 · E5 로그의 `exit=$?` 는 날짜 치환 뒤라 검사기 exit 가 아님(결론 무변 — 문서 인용 없음) | — |

반박한 지적: 없다.

## 9. 자료(scratch `speed-t1/`)

- v1: `meas/`(E1·E2·E4·나눔) · `proto/` · `design-tier1-v1.md`
- v2: `proto2/`(⑴ⓑ · idempotency 순서 · 검토 `fix/` registry_gate + 빈 코어 워커) · `meas/ab1v2.py` → `ab1-result.json`(81쌍) · `meas/e5_load.sh` → `e5.log`·`replay/e5/` · `c3-replay/` · `fence-test/` · `design-tier1-v2.md`
- v3: `fence-test3/`(무시된 산출물 폴더 · 별도 객체 폴더 · linked worktree)
- 검토 재료: `review-t1-proc/{review,rereview}.md` · `review-t1-tool/{review,rereview}.md` · `ab1.py` · `ab2.py` · `fix*/` · `new2*/` · `w3/` · `w4/` · `w4uv/` · `repos3/idem` · `repos4/`
