결론(2026-10-01 · 리뷰 처분 · C7 행동 리허설 · 의미 마감 확인 · Codex 1회 확인 · K3 재리허설 · 의미 최종 마감 반영판): core 규범 묶음 여섯(K2a · K5 · K2b · K5b · K3 · C7)을 이 워크트리의 커밋 여섯으로 구현했고, 구현 리뷰 둘(의미 «수정 후 승인» · 기계 «조건부 반려»)의 지적을 전부 처분해 묶음 커밋을 다시 지었다(묶음마다 깨끗한 패치 · 고침 커밋 따로 없음). 묶음마다 scratch 복제본에서 봉인을 다시 쓰고 `make verify` 를 돌렸다 — 결과는 아래 표. 가장 큰 고침은 둘이다: ① Claude 리뷰어·architect 는 Bash 가 없어 sha256 을 낼 수 없으므로(B1), 역할은 **1회용 토큰**을 머리·응답에 되풀이하고 sha256 은 Coordinator 가 잰다. ② `ARRANGE_BLOCKED` 는 재리뷰 상한을 풀고 일반 루프로 보낸다(M1). ③ C7 행동 리허설(판 B 1.5/8 미달)의 결함 넷 — 읽기 도구 · «이름만 있으면 계획» 판독 · 판정 대상 행 · sha 재계산 — 과 의미 마감 확인 N1 · N2 · N4 · N5 · N6 · N7 · N9 를 K3 · C7 에 넣었다(아래 «C7 리허설 처분» · «의미 마감 확인 처분»). K2a · K5 · K2b · K5b 는 지금 착지해도 되고(K5b = 지금 배포판의 Codex 동시 슬롯 결함 수리), K3 · C7 은 리허설 뒤에 착지한다(«운영자 할 일»).

# 속도 개선 1순위 core 규범 구현 기록 (2026-10-01)

- 설계: `design-tier1.md` v3 · `design-C7.md` v3 · 마감 확인 `scratch review-t1-proc/closure-v3.md`(n1 · n2 · n4 · nit) · `design-K.md` v2 §3-2(표기 소유 이전).
- 구현 리뷰: 의미 `scratch review-impl-core-sem/review.md`(blocker 1 · major 1 · minor 11 · nit 8) · 기계 `scratch review-impl-core-mech/review.md`(blocker 1(같은 B1) · major 3 · minor 2 · nit 5). 처분은 아래 «구현 리뷰 처분».
- 기준: main `86fc3c24`. 워크트리 `.claude/worktrees/agent-a8f8a7589a3afe3d9`(브랜치 `worktree-agent-a8f8a7589a3afe3d9`).
- 범위 밖: C1(다른 구현자 — `registry_gate.py` · 검사기 둘 · 픽스처) · K2(설계 개정 중) · web 전부. 이 구현은 `dddjango/scripts/*.py` 를 건드리지 않는다 — 바뀌는 실행기 폴더 파일은 `rulepack.json`(두 사본) 뿐이다. 이 파일은 pre-gate 실행 트리 digest(`design_pregate.py` — `rulepack.json` 제외) **밖**이지만, registry_gate 툴체인 digest(`registry_gate.py` — 폴더 `*.json` 전량)에는 **든다**(출력 전용 G2 증거 행이라 stale 판정은 없고, 릴리즈 뒤 G2 증거의 digest 값만 바뀐다).
- 절차: `ontology/rules/*.ttl` rdflib 구조 편집 + canon 재직렬화(왕복 byte 동일 먼저 확인) → ISSUED 채번 → 개정은 새 Expression(같은 날 두 번째 개정은 `@2026-10-01b` — 선례 `@2026-09-03b`) → wiring `delegatedTo a/command-dddjango` → `ontology_gate.py` → `ontology_render.py --apply` → LEDGER 재기준선(새 절은 `baseline:`) → 계수표(`--with-golden --emit`) · q4 골든 → `make rulepack` → Codex 손 미러 → G12 라벨 드리프트 분류 → (frontmatter) `claude plugin validate dddjango --strict` → 커밋 → scratch 복제본 `manifest_seal.py --write` + `make verify VERBOSE=1`.
- 재현 도구(scratch `impl-core-rules/v2/`): 묶음마다 `<묶음>_apply.py`(그래프) · `<묶음>_codex.py`(Codex 미러) · `*_texts.py`(문안 정본 — 두 런타임이 같은 문자열을 쓴다) · `dx_edit.py`(K2a · K5) · `g12_add.py` · `build.sh <묶음>`(위 절차 전부 + 커밋) · `fence_test.py`. `86fc3c24` 위에서 `build.sh k2a … c7` 을 차례로 돌리면 아래 커밋 트리가 다시 나온다.

## 커밋 · 패치 · verify

| 묶음 | 커밋 | 패치(scratch `impl-core-rules/`) | verify(scratch 복제본 · 봉인 재발행 뒤 · `make verify VERBOSE=1`) |
|---|---|---|---|
| K2a | `00115609` | `01-K2a.patch` | 5/5 green — 트리가 첫 판 `94a7d35c` 와 byte 같다(`verify-k2a.log` · 기계 리뷰 재현도 5/5) · 패치 byte 무변 |
| K5 | `5996a104` | `02-K5.patch` | 5/5 green · `verify-v7-k5.log` 04:44~04:56Z(부하 높음) |
| K2b | `0ab73a3c` | `03-K2b.patch` | 5/5 green · `verify-v9-k2b.log` — K3 재리허설 결함 1 + 의미 최종 마감 S1 반영 |
| K5b | `841b7813` | `04-K5b.patch` | 5/5 green · `verify-v10-k5b.log` — Codex 동시 슬롯 초과 규칙(지금 배포판 결함 · 1차 착지) |
| K3 | `5d598899` | `05-K3.patch` | 5/5 green · `verify-v10-k3.log` — K3 재리허설 결함 2·3 + 최종 마감 K3-1 반영 |
| C7 | `6e618398` | `06-C7.patch` | 5/5 green · `verify-v11-c7.log` — 최종 마감 C7-1·2 · C7-3 은 K5b 참조만 · 재리허설(최종판) 남은 결함 1(도구 목록) |

- 패치는 `git format-patch 86fc3c24..6e618398` 여섯이다. 새 복제본에서 `git am` 다섯 → 최종 트리 `efb71543` = C7 커밋 트리(scratch `amtest.sh`). `04`·`05` 도 앞 판과 byte 동일(06 만 다시 뽑음). `01`~`03` 은 앞서 넘긴 파일을 그대로 두었다(같은 커밋 · byte 동일 — 새로 뽑으면 머리의 `[PATCH n/6]` 만 다르다). `01`·`02` 는 앞 판과 byte 같다. 앞 판 패치는 `patches-v1/` 에 남겼다(쓰지 않는다).
- `make verify-mutation`(rulepack 변이 12종) — C7 머리에서 12/12 red. `claude plugin validate dddjango --strict` — C7 머리에서 통과.
- 봉인(`workspace/eval/ab/T2-0b-manifest.json`)은 패치에 없다 — 묶음 커밋 뒤 별도 chore 로 재발행한다(DEVELOPMENT §6). **C1 과 같은 봉인 파일**(`script_trees[source-*]` · harness · graph)을 쓴다 — 어느 쪽이 뒤에 착지하든 그 뒤 봉인은 JSON 병합이 아니라 `manifest_seal.py --write` 재발행으로 만든다. C1 과 파일 교집합은 0 이다(기계 리뷰 결합 시험 5/5). C1 이 Coordinator 문면을 더하게 되면 ttl · ISSUED(다음 R-3617) · LEDGER · rulepack · 계수 · q4 · `DX` 가 겹치므로 뒤에 오는 쪽이 rebase 뒤 render·rulepack·계수를 재생성한다(손 병합 금지).
- 이 기록 파일은 커밋하지 않았다(워크트리 미추적) — 설계 문서들과 함께 main 에 옮길 때 싣는다.

## K2a — C2 개정 pre-gate 를 재리뷰 다발과 같은 응답 백그라운드로

- 파일: `ontology/rules/command-dddjango.ttl`(s006/b9) · `dddjango/commands/dddjango.md` · `DX`(Phase 1 pre-gate 문단) · LEDGER 1행(s006) · 계수표 · rulepack 둘.
- 규범: **R-3432 rev 5**(amendment) — 재리뷰 다발로 보내는 개정은 pre-gate 를 같은 응답 백그라운드로(다발 앞 직렬 금지) · 결과는 다음 architect 반영 입력에 노트와 함께 · **결과 전 반영 호출 금지** · 다발 없는 개정(G1 override · 발주자 답 표기)은 곧바로. C3 언급 없음(설계 m9). `DX`: «리뷰어 전부 spawn → shell pre-gate → wait».
- 어긋남: «확인 리뷰 다발» 대신 Coordinator 에 이미 있는 말 «재리뷰 다발»을 썼다(K2a 시점에 «확인 리뷰»는 정의가 없다).
- 남은 위험: 없음(배치만 바뀐다).

## K5 — W1 core `wait_agent` timeout

- 파일: `DX` «역할 위임» 불릿(`DX:21`) · «대기 정책» 불릿(`DX:26`) · Phase 1 2번(`DX:145`). 그래프 밖(LEDGER·rulepack 무변).
- 문안(web W8e `CX:34` 와 글자 그대로): «`wait_agent` 는 `timeout_ms` 를 300000(5분)으로 준다 — «timeout_ms must be at most …» 오류면 오류 문구의 상한으로 다시 부른다. 역할이 끝나면 timeout 과 무관하게 곧바로 돌아온다. «30분+ 무진행» 실측은 timeout 반환마다 산출물 크기·mtime 으로 한다. 띄운 에이전트의 결과를 모두 받았으면 `wait_agent` 를 다시 부르지 않는다 — 기다릴 에이전트가 없으면 timeout 까지 막힌다. 남은 대상이 있는지 불확실하면 `list_agents` 로 먼저 확인한다.» · 슬롯 해제 = «`close_agent`(도구 목록에 있을 때만)»(`DX:21` · `DX:145`). 런타임 프롬프트에 날짜 메타 표기를 넣지 않는다(web 원칙).
- 근거(운영 세션 Codex 1회 확인 · 0.159.2 `codex exec`): 도구 목록에 `close_agent` 없음 · `wait_agent` 스키마 «Defaults to 30000, min 10000, max 3600000» · 대상 id 인자 없음 · 300000 수락 · 서브 종료 13ms 뒤 반환 · 결과를 다 받은 뒤 재대기는 timeout 까지 막힘(3600000 호출이 17분+ 무반환).
- 재커밋: 조정자는 fixup + 비대화 autosquash 를 권했으나, K3 가 `DX:21` 같은 줄을 고쳐 autosquash 가 충돌하므로 build 스크립트로 K5 → K2b → K3 → C7 을 K2a 위에 다시 지었다(K2a 커밋·패치 무변 · 결과 트리는 autosquash 와 같다).
- 남은 위험: 없음(무엇을 기다리는지·언제 받는지는 같다).

## K2b — C3 재리뷰 상한

- 파일: `command-dddjango.ttl`(s006/b5 · s009/b3) · 리뷰어 넷 ttl·md(입력 절 새 블록 · 발견 형식 블록) · `DX`(Phase 1 4번 · 수정 모드 2번) · Codex 역할 스킬 넷 · ISSUED 7 · wiring 7 · LEDGER 10 · 계수표 · q4 · rulepack · `scope-limit-norms.md` 표 2 N 5행 · `rulepack_smoke.py` 검토 완료 집합 5.
- 새 규범: **R-3590**(Permission · 기준 ①~④ · ③ 은 함께 띄운 pre-gate 결과를 받은 뒤 판별 · 판별 불가면 상한 밖) · **R-3591**(두 갈래 ⓐ/ⓑ · 확인이 «G1 전 닫기: 예» 로 적은 nit 는 배너 별행 · 무확인 G1 없음 · G1 답의 미반영 반영도 ⓑ) · **R-3592**(확인 1회 · 입력은 그 lens 발견만 · 대응표(비활성 lens 영역은 discipline) · 배너 1행) · **R-3593 · R-3594 · R-3595 · R-3596**(리뷰어 확인 모드 입력 — 자기 lens 발견만 · 다른 lens 반영은 diff 로).
- 개정: **R-0230** rev2 · **R-0418** rev2(G1′ 재리뷰에 같은 기준·갈래 — 기준 ① 의 lens = 영향 lens) · **R-3373 · R-2620 · R-3328 · R-0869** rev2(Phase 1 nit 의 `G1 전 닫기: 예 | 아니오` 칸).
- 어긋남(까닭)
  1. «재리뷰 상한»을 새 블록이 아니라 **s006/b5(4번) 아래 하위 불릿**으로 넣었다 — 블록 IRI 서수 = order 가 코퍼스 관례이고 절 중간 삽입 선례가 없다. 하위 불릿 선례는 R-3585. 렌더 위치는 설계와 같다(4번과 5번 사이).
  2. 마감 확인 **n2**: ⓑ 발동 표지를 리뷰어 산출 형식의 정형 칸 `G1 전 닫기: 예 | 아니오` 로 고정했다(K3 가 미뤄져도 혼자 서도록 K2b 에서 발견 형식 규범을 개정). 칸이 없으면 «상한 밖». G1 답의 `미반영` 반영 요구는 ⓑ.
  3. 확인 모드 입력 문안(설계상 K3)을 K2b 에 넣었다 — K2b 가 혼자 서야 한다.
  4. 리뷰어 어휘 통일(minor 추가)은 하지 않았다(설계상 선택 — R-3590 ② 의 닫힌 대응이 흡수).
  5. 설계 밖 필수 조치: 새 라벨이 G12 라벨 드리프트 식(«diff»)에 걸려 첫 verify 가 red 였다 → 절차(N)로 분류해 `scope-limit-norms.md` 표 2 와 `rulepack_smoke.DRIFT_REVIEWED` 에 더했다(K3 · C7 도 같은 절차).
- **C3 역재생 — 8-C-0 노트**(scratch `c11/notes` · `c11/spec` 읽기만 · 스크립트 `c3replay/tabulate.py`·`diffsec.py`)

| 라운드 | 판정(노트) | 열린 B/I | 기준 | 구현 규칙의 결과 |
|---|---|---|---|---|
| R1~R6 | 불가 하나 이상 | 32 · 28 · 13 · 3 · 3 · 2 | 불성립(① · ②) | 지금 규범 그대로 |
| R7(api-7 · db-7 · discipline-7) | 셋 다 가능 · ddd 없음 | 0(minor 2 · nit 3) | **불성립** — ① ddd 직전 노트는 r6 diff 가 대응표로 못 가르는 절을 건드려 인정 불가 · ④ 다음 반영 r7 이 «8-3-1 main 착륙 실물 대조»를 함께 실음 | 지금 규범 |
| **R8**(4 lens) | 넷 다 가능 | 0(nit 2 · «lens 밖 관찰»은 발견 아님) | **성립** | 칸이 있었다면: «G1 전» 표지 0 → **ⓐ** — G1 ≈13:35(실제 14:09) **약 −34분**. «예»를 달았다면 ⓑ — 확인 1회 = 실제 R9 → G1 ≈13:55 **약 −14분** |
| R11(G1′) | discipline-11 불가 | 4 | 불성립 | 지금 규범 |
| **R12**(G1′ 2차) | 셋 다 가능(영향 lens) | 0(minor 1 · nit 6) | 성립 | ⓐ — 실제와 같다. 그 뒤 발주자 «L-1~L-7 표기 개정»(r12 · 무리뷰)은 **n2 로 ⓑ 확인 1회**가 붙는다(품질 순증 · 약 +10~20분 [추정]) |
| R13~R16 | 불가·blocker·important 열림 | 7 · 3 · 10 · 3 | 불성립 | 지금 규범 |

  - 설계 표(§1-3)의 «r7 성립»과 다르다: 문면대로면 r8 에서 선다.
  - 옛 노트에는 `G1 전 닫기` 칸이 없어 문면대로면 상한이 서지 않는다(fail-closed — 지금보다 느려지지 않는다). 이득은 리뷰어가 칸을 쓰기 시작한 레인부터다.
  - 처분 뒤에도 이 표는 그대로다: m4(③ 은 함께 띄운 pre-gate 결과 뒤 판별)는 R8 의 r7 예보가 이미 있었고, M1(arrange 막힘)은 8-C-0 노트에 arrange 가 없어 판정이 바뀌지 않는다. 다만 C7 이 착지한 레인에서는 R8 ⓐ 뒤 ⓘⓘ′ 단독 arrange 가 r9 의 S3 결함(K2·K4·K5)으로 막혔을 것이고[추정], M1 처분대로 상한을 풀고 일반 루프로 간다.
- 남은 위험: 이득이 리뷰어의 칸 기재에 달렸다. 대응표가 레인 고유 절 제목을 못 가르면 «활성 lens 전부»라 확인 다발이 커진다.

## K5b — Codex 동시 슬롯 초과 다발(지금 배포판 결함 · 1차 착지)

- 파일: `DX` 만(그래프·LEDGER·rulepack 무변 · Claude 쪽 해당 없음). 커밋 `841b7813` · 패치 `04-K5b.patch`.
- 공통 규칙(`DX:27` «Codex 실행 모델» 절 새 불릿 «동시 슬롯»): «이 런타임은 한 번에 살아 있는 에이전트 수에 한도가 있다 — 세션 지시의 «N available concurrency slots … including you»(너를 빼면 N−1). 여럿을 함께 띄우는 다발(Phase 1 리뷰·재리뷰·확인 다발 · 수정 모드 G1′ 다발 · Phase 2 병렬 배차·감사 · 리팩토링 모드 BC 점검 다발)이 그 수를 넘으면 한도까지 먼저 띄우고, 남은 것은 첫 결과를 받은 직후 띄운다. `spawn_agent` 가 `agent thread limit reached` 로 실패하면 그 역할은 띄워지지 않은 것이다 — 결과 하나를 받은 뒤 다시 띄운다(누락으로 두지 않는다). 슬롯 단위로 나눠 띄워도 같은 다발이고 병렬 정의 위반이 아니다. 다발과 겹쳐 돌리는 shell 작업(pre-gate 등)은 첫 몫을 띄운 직후에 돌린다.»
- 참조 한 줄(K5b 판 줄): Phase 1 2번 리뷰 다발 `DX:116` · 재리뷰 상한 확인 1회 `DX:123` · Phase 2 동작 보존 창 병렬 배차 `DX:142` · 슬라이스 병렬 배차·감사 `DX:144` · 수정 모드 G1′ 다발 `DX:217`. 리팩토링 모드 BC 점검(`DX:257`)은 이미 «런타임 동시 슬롯 한도 단위로 다발을 반복하는 것은 위반이 아니다»가 있고, 두 런타임 byte 대조(`runtime_parity_check` «리팩토링 모드» 절)라 손대지 않았다 — 공통 규칙이 이름으로 가리킨다(parity 정합 확인).
- 근거: Codex 0.159.3 바이너리 문구 «… available concurrency slots, meaning that up to … agents can be active at once, including you» · 설정 키 `features.multi_agent_v2.max_concurrent_threads_per_session`(우리 `~/.codex/config.toml` 에 없음 → 기본) · 운영 세션 실측 «4 … including you»(서브 3). 넘친 spawn 은 줄 서지 않고 실패한다.
- **현장 근거**(`~/.codex/sessions` 읽기만 · scratch `v2/slotscan3.py` · `v2/slotscan3.out`): `agent thread limit reached` spawn 실패 **38회 · rollout 10개 · 레인 8곳**(2026-09-20 ~ 09-30).

| rollout | 실패 줄(앞 8) | 횟수 | 레인(cwd) |
|---|---|---|---|
| `2026/09/20/rollout-2026-09-20T12-31-56-01a0bcde…` | 4911 · 5967 · 9351 · 10764 · 11936 · 12228 · 13051 · 17152 … | 11 | lane-fortune-house |
| `2026/09/21/rollout-2026-09-21T07-17-53-01a0c0e5…` | 361 | 1 | lane-fortune-house |
| `2026/09/22/rollout-2026-09-22T17-00-34-01a0c821…` | 1973 · 3349 · 3493 · 9159 · 9227 · 11082 · 11155 · 11592 … | 10 | chat_relay |
| `2026/09/23/rollout-2026-09-23T03-57-37-01a0ca7b…` | 533 | 1 | chat_relay |
| `2026/09/28/rollout-2026-09-28T10-08-37-01a0e58e…` | 19164 · 19776 | 2 | lane-6-3-6 |
| `2026/09/29/rollout-2026-09-29T15-22-46-01a0ebd4…` | 7547 · 7605 · 7629 · 7641 | 4 | lane-6-3-11 |
| `2026/09/29/rollout-2026-09-29T15-27-01-01a0ebd8…` | 13562 · 14106 · 15217 | 3 | lane-8-B-3 |
| `2026/09/30/rollout-2026-09-30T12-18-16-01a0f051…` | 5967 · 6968 · 6988 | 3 | lane-6-3-10 |
| `2026/09/30/rollout-2026-09-30T15-02-50-01a0f0e8…` | 6367 | 1 | lane-5-1-6 |
| `2026/09/30/rollout-2026-09-30T23-10-45-01a0f2a7…` | 8783 · 8805 | 2 | lane-admin-2 |

- 품질·속도: 검사·리뷰는 그대로이고, 지금은 실패한 spawn 을 레인이 즉흥으로 다시 띄우던 것을 규칙으로 고정한다(누락 방지). 슬롯을 넘는 다발은 원래 동시에 돌 수 없었으므로 벽시계 손실이 없다.
- 남은 위험: 한도 값이 설정·버전으로 바뀌면 «N» 은 세션 지시 문구를 따른다(값을 박지 않았다).

## K3 — C4 · C5 · 부속 기록 판형/예외

- 파일: `command-dddjango.ttl`(s002/b10~b13 새 블록 · s006/b3 · s006/b5 · s007/b5) · 리뷰어 넷 ttl·md(frontmatter `tools` 에 `Write` · 산출 · 입력) · `agent-design-architect.ttl`(s006/b2) · `DX` · Codex 역할 스킬 다섯 · ISSUED 10 · wiring 10 · LEDGER 16 · 계수표 · q4 · rulepack · `scope-limit-norms.md`(표 2 N 13행 · 표 1 T 세 행 비고) · 검토 완료 집합 16.
- 새 규범: **R-3597** 부속 기록 판형(① 절대 경로 · 경로마다 1회용 토큰(`openssl rand -hex 8`)은 그 역할 입력에만 ② 역할은 새 파일 · 머리 첫 줄 종류·역할·회차 · 둘째 줄 `토큰 <값>` · 응답 `기록: <경로> · 토큰 <값>` · **역할은 해시를 계산하지 않는다** ③ Coordinator 대조(파일 있음 · 머리 lens · 머리·응답 토큰 · 판정 1행) · 없거나 다르면 반송 · **sha256 은 Coordinator 가 재어** 한 줄 상태에 남김 ④ 울타리 대상 = 리뷰어 넷 · architect 는 밖 ⑤ 판정 근거 아님) · **R-3598** 울타리 창 · **R-3599** 울타리 대조 · **R-3600** 반영 호출에 명세 안 처분 표 요구 금지 · **R-3601** 처분 = architect 부속 기록(토큰) · **R-3602~R-3605** 리뷰어 부속 기록 예외 · **R-3606** architect 부속 기록 예외.
- 개정: **R-0220 · R-0223 · R-0224**(판형 대조 · 파일 없으면 반송) · **R-0282**(울타리 대상 역할의 감사와 병렬 배차 금지) · **R-3370 · R-2617 · R-3325 · R-0863**(산출 — 경로·토큰 받으면 그 한 곳 · 해시 계산 0 · Codex 는 `apply_patch` Add File) · **R-3368 · R-2614 · R-3323 · R-0862**(입력) · **R-1751** rev2 redefinition.
- 울타리 code 블록(s002/b12): ① 스냅숏 — 1행 작업 트리 SHA(`git add -A` + `git add -f -A -- <BF>` · 별도 객체 폴더) · 2행 상태 다이제스트(이 작업 트리의 HEAD · 브랜치 이름 · `find -H .venv venv -maxdepth 4 -name '*.dist-info'` — `git hash-object --stdin`) ② 대조 `git diff-tree -r --name-status` ③ `pregate-report.md` 덧붙이기 확인(`head -c` + `cmp -s` — BSD `cmp -n` 은 앞 파일이 짧으면 EOF 로 실패해 쓰지 않는다 [실측]).
- 허용 = 부속 기록 경로(`A` 만) + 코디네이터 쓰기 목록 + **이번 창에 pre-gate 를 띄웠을 때만** `pregate-report.md`(`A` 또는 덧붙이기 `M`). 상태 다이제스트 변동(HEAD 이동 · 브랜치 전환 · 설치)도 허용 밖.
- 어긋남(까닭)
  1. 울타리를 규범 둘(창 · 대조) + 규범 없는 code 블록으로 나눴다 — 한 규범을 여러 블록이 진술하거나 norm 블록 안에 펜스를 둔 선례가 0 이다(§13).
  2. 판형·울타리를 s002(산출물 위치) 끝에 붙였다 — Phase 1 리뷰와 Phase 2 감사가 함께 쓴다.
  3. 마감 확인 n4: 창을 열 때 작업 트리에 쓰는 백그라운드 작업 0(출력은 `$TMPDIR` 또는 창 전 종료) — 허용 목록에 더하는 길은 세탁 통로라 열지 않았다.
  4. sink 격리는 `DJR_FINDINGS_JSON` 만 — `findings.py` 우선순위 ① 이 있으면 `.dddjango/violations/` 게시가 없다(설계의 «`DJR_VIOLATIONS_DIR` 비움»은 쓸모가 없다).
  5. 공유 ref·stash 는 보지 않는다 — 여러 레인 워크트리가 함께 쓰므로 거짓 STOP 을 내고, stash·reset 으로 바뀐 작업 트리는 트리 대조가 잡는다. `.venv` 는 본다 — 창 안 설치가 G2 mypy·pytest 결과를 바꾸고 레인 발주가 «설치 0»을 걸기 때문이다(다른 레인과 `.venv` 를 공유하는 판형의 거짓 STOP 은 드물고 STOP 은 싸다).
  6. discipline-reviewer frontmatter 블록(s001/b1 — R-0831~R-0833 진술)의 `tools:` 줄은 개정 없이 바꿨다 — 09-05·09-06 Serena 도구 추가 선례(LEDGER 재기준선만 · «규범 불변»)를 따른다.
- 울타리 시험(scratch `v2/fence_test.py` — 렌더된 md 의 code 블록을 그대로 뽑아 자리표시만 치환 · linked worktree · 하위 cwd · 심링크 `.venv`). 결과 `v2/fence-test-ignore.log` · `v2/fence-test-noignore.log` — **두 저장소 모두 16/16 기대대로**:
  - 스냅숏 2회: 공통 `.git` 아래 바뀐 파일 0 · 같은 결과.
  - (가) 정직한 기록 넷 → 통과 · Coordinator 가 sha256 측정. (나) 기록 밖 쓰기(추적 새 파일 + 산출물 폴더 명세 수정) → STOP. (다) 창 안 수정+커밋 → STOP. (다′) 미리 dirty 인 변경을 커밋만(트리 같음) → 상태로 STOP. (라) 심링크 `.venv` 에 dist-info 추가 → 상태로 STOP · (라′) `$TMPDIR` 쓰기 → 통과. (마) 백그라운드 로그 → 산출물 폴더 → STOP · (바) → `$TMPDIR` → 통과. (사) pre-gate 덧붙이기(이번 창에 띄움) → 통과 · (사′) 같은 변경인데 안 띄움 → STOP · (사″) 앞부분 고침(처분 행 세탁) → STOP. (아) lens 덮어쓰기(api → ddd 경로) → 머리 lens·토큰 불일치로 반송. (자) 토큰 지어냄 → 반송. (차) 경로 준 호출에 파일 없음 → 반송. (카) 응답 판정 ≠ 파일 판정 → 반송. (타·참고) 미격리 sink — 기본 저장소에서는 잡히고, `.dddjango/` 무시 저장소에서는 안 보인다(규범이 격리를 요구하는 까닭).
- 남은 위험: 울타리는 사후 검출이다(STOP · 자동 되돌림 없음). 창이 배타적이라 Phase 2 «감사 ∥ 다음 슬라이스» 병렬이 줄 수 있다(상한 = 감사 1회 6~14분 [추정]). Claude 리뷰어가 `Write` 를 갖게 됐다 — 울타리가 보증이다. 토큰은 Coordinator 가 그 역할 입력에만 싣는다는 문면에 기댄다.

### K3 «작업 트리 플러그인 리허설» — 운영자가 돌릴 것(착지 전)

- 플러그인: K3(또는 C7) 커밋의 `dddjango/` 를 `claude --plugin-dir <워크트리>/dddjango` 로 · Codex 는 같은 커밋의 `codex-dddjango/` 를 로컬 스킬로(설치본과 동시에 켜지 않는다).
- 재료: scratch git 저장소에 pregate 픽스처 명세(`workspace/eval/fixtures/pregate/*-spec.md` 하나)를 `.dddjango/<폴더>/design-spec.md` 로 두고, 활성 lens 넷 리뷰 다발 1회만 돌린다.
- 통과: 기록 4 · 머리 첫 줄 `# g1-review · <lens> · <n>` · 둘째 줄 `토큰 <값>` = 그 lens 에 준 토큰 · 응답 `기록:` 4행의 토큰 = 준 토큰 · 응답 판정 1행 = 파일 판정 1행 · 울타리 차이 = 기록 4 · 코디네이터 쓰기 0 · Coordinator 가 기록마다 sha256 을 재어 한 줄 상태에 남김 · 노트 전사 0 · 배너 «울타리 차이» 행. **역할이 해시를 계산하려 하지 않는지**(Claude 리뷰어는 Bash 가 없다)를 도구 호출 기록으로 본다.
- 음성 대조(설계 §3 C4): (a) 창 안 추적 파일 수정 뒤 커밋 (b) 이미 수정된 명세 재수정 (c) lens A 가 B 경로에 씀(→ 머리 lens·토큰 대조로 반송) (d) 창 밖 SendMessage 재기동 (e) `.dddjango/` 무시 저장소에서 명세 수정 (f) 창 안 코디네이터 검사기 직접 실행(sink 미격리 → STOP · 격리 → 통과). 스냅숏 기제는 위 scratch 시험이 이미 확인했다 — 리허설은 LLM 이 규범대로 토큰을 싣고 창을 여닫는지·(c)(d) 행동을 본다.
- C5: 위 다발 뒤 한 lens 를 확인 모드로 1회(그 lens 처분 파일 · 직전 자기 노트 · 명세 diff · 그 lens 반영 발견만) — 다른 lens 처분·발견이 입력에 없는지 본다.

## C7 — G1 전 슬라이스 인수 arrange 점검

- 파일: `command-dddjango.ttl`(s006/b12 새 블록 · s006/b5 · s006/b6 · s007/b3 · s002/b10·b11) · `agent-design-architect.ttl`(s005/b39·b40) · `agent-acceptance-tester.ttl`(s001/b2 · **새 절 s006**) · `agent-discipline-reviewer.ttl`(s002/b2) · md 넷 · `DX` · Codex 역할 스킬 셋 · ISSUED 10 · wiring 10 · LEDGER 7(새 절 `baseline:`) · 계수표(Section +1) · q4 · rulepack · G12 N 3.
- 새 규범: **R-3607**(언제 ⓘ · ⓘⓘ · ⓘⓘ′ · ⓘⓘⓘ G1′ 재리뷰 다발 · 울타리 · 막힘 = architect 반송 + **재리뷰 상한 해제·일반 루프**(막힘이 풀릴 때까지 매 재리뷰 다발 합류) · 이견은 1회 재호출 뒤 STOP · 이번 실행 명세의 계획 누락은 반송 · 구형만 «해당 없음» · 배너 1행) · **R-3608**(재사용 ㉠~㉤ — 기준선 인용 시험 쪽 파일 · approved-merges 해시 포함) · **R-3609**(판정 명세 sha — 파견 입력의 Coordinator 측정값 = 기록 값 = 근거로 쓰는 때의 값 · 무배너 진입·재진입 포함) · **R-3610**(슬라이스 계획 절 · `# S<n>` · `# S<처음>→S<끝>` · 슬라이스 0 은 `# S0`) · **R-3611**(arrange 자기 차례 + 제품 쪽 import 차례) · **R-3612~R-3616**(acceptance-tester `PHASE1_ARRANGE_CHECK` — G1 전 또는 Phase 2 재진입 전 · 입력에 Coordinator 측정 sha · 토큰 · 읽기 닫힘 · 기록 한 파일(Write) 말고 쓰기 0 · Edit·Bash 0 · **아무것도 계산하지 않는다 — sha 는 입력값을 옮긴다** · 제품 쪽 차례 행 · `ARRANGE_BLOCKED`).
- 개정: **R-3591 · R-3592** rev2 `@2026-10-01b`(ⓑ 통과에 «같은 다발 arrange 막힘 아님» · 불통과 목록에 arrange 막힘) · **R-0234** rev2(배너 추가 행·전제 가리킴) · **R-0269** rev2 redefinition · **R-0840** rev2 · **R-3232** rev2 · **R-3597 · R-3598** rev2 `@2026-10-01b`(울타리 대상 += arrange · 배타 대상 = acceptance-tester Phase 2).
- 어긋남(까닭)
  1. **표기 소유 이전**(설계 K v2 §3-2 · 조정자 지시): 파일 단위 표기는 C7 의 R-3610 이 소유하고 입장 행 배정은 계획 절 표가 진다. K2 · `slice-plan` · 교차 예보 참조 0. 파서 무변(`_parse_file_plan` 이 `#` 뒤를 버린다 — 실측).
  2. architect 규범 둘을 블록 둘(s005/b39 · b40)로 뒀다.
  3. 마감 확인 n1 · nit: sha 일치를 무배너 진입·재진입까지 넓히고, Coordinator 가 파견 직전에 재어 입력으로 준다.
  4. «arrange 는 상한 기준 ① 밖 · 대응표에 없음»은 C7 블록에 두고, ⓑ 통과 조건만 R-3591·R-3592 를 개정해 C3 문면 안에 보이게 했다(의미 M1).
  5. 블록 번호: Coordinator `s006/b12` 를 C7 이 썼다 — K2 의 새 Coordinator 블록은 다음 빈 번호(`s006/b13`)다(블록 번호도 커밋 차례).
- 남은 위험: ⓘⓘ′ 단독 1회는 G1 직전 임계에 15~35분을 얹는다(결함 없는 레인 −0~+35). C7 행동 리허설은 옛 판 `e2bcb118` 로 돌았다(판 A 통과 · 판 B 1.5/8 미달 · 판 C 부분 · 음성 0/25) — 위 «C7 리허설 처분» 뒤 판 `6e618398` 로 다시 돌려야 한다(특히 판 B 의 M2~M7). 읽기 명령 목록은 문면 규칙이라 지켰는지는 도구 호출 감사로만 보인다. 막힘이 상한을 풀어 리뷰 사이클이 하나 느는 대신 리뷰 없는 반영은 없다. 제품 쪽 import 차례 판정은 LLM 이 명세 boundary-imports 로만 본다(K2 X2 착륙 전까지).

## 구현 리뷰 처분

### 의미 리뷰(`review-impl-core-sem/review.md`)

| 지적 | 처분 | 묶음 · 규범 |
|---|---|---|
| **B1** 리뷰어·architect 가 sha256 을 못 냄 · acceptance-tester Bash 모호 | 받음: 1회용 토큰(그 역할 입력에만) · 머리 둘째 줄 · 응답 `기록: … · 토큰` · 역할 해시 계산 0 · Coordinator 가 대조하고 sha256 을 잼 · arrange 는 입력의 sha 를 옮김 · 두 런타임 같은 판형 | K3 R-3597 · R-0224 · R-3601 · R-3370/R-2617/R-3325/R-0863 · R-1751 · R-3606 / C7 R-3609 · R-3613 · R-3615 · R-3616 |
| **M1** `ARRANGE_BLOCKED` × 재리뷰 상한 | 받음: 막힘이면 상한을 풀고 일반 루프(막힘이 풀릴 때까지 매 재리뷰 다발 합류) · ⓑ 통과·불통과에 arrange 막힘 · 선택 ⑤ 는 넣지 않음(막힘 문장이 같은 일을 한다) | C7 R-3607 · R-3591/R-3592 rev2 |
| m1 `pregate-report.md` 상시 허용 | 받음: 이번 창에 pre-gate 를 띄웠을 때만 · `A` 또는 덧붙이기 `M`(앞부분 고침은 허용 밖) · pre-gate 표준 출력은 `$TMPDIR`(`pregate-run-<n>.txt` 허용 삭제) | K3 R-3599 · code 블록 |
| m2 `.venv`·HEAD·ref | 받음: HEAD·브랜치·`.venv`/`venv` dist-info 다이제스트 · 공유 ref·stash 는 까닭과 함께 뺌 | K3 R-3598 · R-3599 |
| m3 기록 파일이 없을 때 | 받음: 경로 준 호출에 파일 없으면 반송 · `--name-status` 로 `A` 확인 | K3 R-3597 ③ · R-0224 · R-3599 |
| m4 ③ 판별 시점 | 받음: 함께 띄운 pre-gate 결과를 받은 뒤 판별 — 기다림은 판별 불가가 아님 | K2b R-3590 |
| m5 확인의 «예» nit | 받음: 배너 별행 `확인이 G1 전 닫기로 적은 nit k건 — 기본 수락이면 반영 없이 Phase 2` | K2b R-3591 |
| m6 재사용 키 ④ | 받음: 기록이 기준선으로 인용한 시험 쪽 파일 전부 + `approved-merges.txt` 해시 | C7 R-3608 |
| m7 계획 누락이 «해당 없음»으로 꺼짐 | 받음: 이번 실행 명세면 architect 반송 · 구형만 해당 없음 | C7 R-3607 |
| m8 확인 입력의 다른 lens 발견 | 받음: 그 lens 발견만 · 다른 lens 반영은 diff 로 | K2b R-3592 · R-3593~R-3596 |
| m9 G1′ 의 lens · ⓘⓘⓘ 이름 | 받음: G1′ 기준 ① lens = 영향 lens · ⓘⓘⓘ = «G1′ 재리뷰 다발» | K2b R-0418 · C7 R-3607 |
| m10 거짓 막힘 출구 | 받음: architect «막힘 아님 — 근거» → 1회 재호출 → 그래도 막힘이면 STOP | C7 R-3607 |
| m11 제품 쪽 차례 | 받음(판정 쪽): arrange 판정에 «Sn 파일이 뒤 슬라이스 모듈을 import» 행 · architect 자기 차례에 제품 쪽 문장 · R-0269 하위 분할 정의는 그대로(계획 슬라이스가 단일 근거) | C7 R-3611 · R-3616 |
| n1 배너 단계 교차 참조 | 받음 | C7 R-0234 rev2 |
| n2 Codex 문면 셋 | 받음: ⓘⓘ′ «arrange spawn → shell 최종 pre-gate → wait» · R-0282 «울타리 대상 역할의 감사»(두 런타임) · acceptance-tester «셸·`apply_patch`» | K3 · C7 Codex |
| n3 Codex 쓰기 수단 | 받음: «새 파일은 `apply_patch`(Add File) · 셸로는 그 밖 쓰기·git 쓰기 0» | K3 Codex 역할 다섯 |
| n4 루틴 코디네이터 쓰기 | 받음: 넘길 파일(`g1-nit-<n>.diff`)은 before 전 · 창 안 출력(`--check-report` 등)은 `$TMPDIR` | K3 R-3598 |
| n5 슬라이스 0 표기 | 받음: `# S0` | C7 R-3610 |
| n6 모드 문안 · 재진입 | 받음: «G1 전(또는 Phase 2 재진입 전) · 판정 대상 명세» | C7 R-3612 · R-3613 |
| n7 «창» 두 뜻 | 받음: 울타리 문단은 «울타리 창» | K3 R-3598 · R-3599 · R-0224 · R-0282 |
| n8 원번호 · 비활성 lens | 받음: 재사용 키 ㉠~㉤ · 대응표가 비활성 lens 를 가리키면 discipline | C7 R-3608 · K2b R-3592 |

### 기계 리뷰(`review-impl-core-mech/review.md`)

| 지적 | 처분 |
|---|---|
| B1 | 위 의미 B1 처분과 같다(권고안 (a) 에 토큰을 더한 판 — 머리 lens 대조만으로는 lens 가 자기 lens 이름을 남의 경로에 쓰는 경우를 못 가르므로 토큰을 둔다). |
| M1 G12 이중 분류 | 받음: R-2614 · R-3323 · R-3368 은 표 2 N 행을 빼고 표 1(T) 비고에 «속도 개선 K3 rev 라벨 개정으로 식 적중(«diff») — 분류 T 그대로». 머리 bullet 을 K2b 5(379) → K3 13(392 — T 셋은 비고만) → C7 3(395) 차례로. `DRIFT_REVIEWED` 는 T∪N 이라 셋도 등재(그대로). 실제 N 행은 21(5 · 13 · 3). |
| M2 arrange 해시 실행 허용 | 받음: R-3615 «Edit·Bash 0» · «이 모드에서 너는 아무것도 계산하지 않는다 — `판정 명세 sha256` 은 입력값을 옮기고 해시 명령을 돌리지 않는다» · 응답 `기록:` 은 토큰. |
| M3 착지 순서 | 받음: «운영자 할 일»을 K2a · K5 · K2b 먼저 → 리허설 → K3 · C7 차례로 고쳤다. |
| m1 «digest 밖» 표현 | 받음: 머리 «범위 밖» 줄을 «pre-gate digest 밖 · registry_gate 툴체인 digest 에는 듦(출력 전용)»으로 고쳤다. |
| m2 C1 과 봉인 공유 | 받음: «커밋 · 패치 · verify» 절에 적었다. |
| n1 Codex «Edit·Write·Bash» | 받음(의미 n2 와 같음). |
| n2 frontmatter 무개정 | 받음: K3 어긋남 6 에 «선례 따름». |
| n3 K2b 의 «슬라이스 계획» 낱말 | 기록만: K2b 단독 착지 동안은 일반어로 읽힌다(무해) · C7 착지로 정합. |
| n4 부속 기록 경로 절대 경로 | 받음: 판형 ① «절대 경로로 준다». |
| n5 머리 bullet 역순 | 받음(M1 과 함께). |

## C7 행동 리허설 처분(scratch `rehearsal-core/report.md` · 판 `e2bcb118`)

| 결함 | 처분 | 바뀐 문면(`6e618398` 기준) |
|---|---|---|
| 1 읽기 도구 — «실존만(Glob)» ↔ «Bash 다른 용도 금지». 이 런타임에선 Bash 를 가진 역할에 Glob·Grep 이 없어 4/4 가 Bash 로 읽음 · 제품 본문 grep 2회 | **닫힌 읽기 명령 목록**을 택했다: Read·Grep·Glob 가 있으면 그것, 없으면 Bash 읽기 명령만 — 명세·시험 쪽 파일에 `cat` · `sed -n` · `head` · `tail` · `wc` · `grep`·`rg`(재귀는 시험 쪽 폴더만) · `ls` · `find -name`(시험 쪽 폴더만), 제품 경로에 `test -e` · `ls -d`(실존만). `python` · `git` · 해시 · 시험 · 설치 · 리다이렉트 쓰기 · Edit 0. 시험 쪽 파일 정의는 R-0269 의 0T 판정과 같은 경로 조각. **까닭**: Coordinator 는 역할의 도구를 파견마다 바꿀 수 없고(Claude 는 frontmatter `tools:` 고정 · 새 역할 문서를 만들면 문서·그래프·Codex 가 한 벌 더 는다), Codex 역할은 셸뿐이다 — 두 런타임이 같은 규칙으로 지킬 수 있는 것은 명령 목록이다. 집행: 쓰기는 울타리가 보고, 읽기는 리허설의 도구 호출 감사(`toolaudit.py`)로 본다 | `dddjango/agents/acceptance-tester.md:67`(읽기 범위) · `:69`(도구·쓰기) · Codex `dddjango-acceptance-tester/SKILL.md:61` · `:63` · R-3614 · R-3615 라벨 |
| 2 «이름만 있으면 계획» 판독(판 B M2~M5 놓침) | 받음: «출처 `S<k≤n> 계획` 은 명세가 그 재료를 arrange 에 쓸 수 있을 만큼 — 입력 꼴(필드·타입) · 상수 값 · 함수·생성자 시그니처 · 기록·데이터의 내용 · 붙는 gate·ID — 적었을 때만 · 이름만 나오고 그 값·꼴·시그니처가 없으면 `명세 없음`(이름이 명세에 있다는 것은 계획의 근거가 아니다) · `기준선` 은 시험 쪽 파일이 그 꼴로 쓰고 있거나 명세가 기준선 꼴을 적었을 때만» | `acceptance-tester.md:71` · Codex `:65` · R-3616 라벨 |
| 3 판정 대상 행 — owner 칸이 역할을 안 적으면 «외부 add/update 행»의 근거 없음(판 C G-F) | 받음: architect 의 슬라이스 계획 표를 `슬라이스 \| 목적 \| 인수 행 \| 내부 행 \| 완료 조건` 으로 바꿔 **인수 행**(acceptance-tester 몫 — 외부 HTTP·event·사용자 관찰·공개 계약의 `add/update`)을 architect 가 가른다. arrange 입력·판정 대상 = 인수 행뿐. 가르지 않은 명세는 계획 누락과 같이 architect 반송 — Coordinator 가 대신 가르지 않는다 | `dddjango/agents/design-architect.md:98` · Codex `:92` · `dddjango/commands/dddjango.md:148`(arrange 점검 입력 · 반송) · `:155`(R-0269) · `acceptance-tester.md:65` |
| 4 sha 재계산(파견에 sha 가 있어도 다시 잼) | 받음: «이 모드에서 너는 아무것도 계산하지 않는다 — `판정 명세 sha256` 은 입력의 값을 그대로 옮긴다 · 입력에 없으면 재지 말고 `판정 명세 sha256 입력 없음`» + 해시 명령은 허용 목록 밖 · Coordinator 는 sha 를 반드시 입력에 싣고, `입력 없음` 이거나 다르면 그 기록은 무효 | `acceptance-tester.md:69` · `:71` · `dddjango.md:148` |
| 5 열쇠 K4·K5(행 단위 입력 밖) | 기록만 — 리허설 채점 열쇠 조정 몫(규범 아님) | — |

## 의미 마감 확인 처분(scratch `review-impl-core-sem/closure.md` — 판정 «닫힘»)

| 지적 | 처분 | 바뀐 문면(`5d598899`·`6e618398` 기준) |
|---|---|---|
| N1 대조·sha 측정 시점 | 받음: 판형 ③ 대조와 sha256 측정은 울타리 창을 닫은 뒤(after 스냅숏·경로 대조 뒤 · architect 는 돌아온 뒤) 다발 전체에 한 번 — 응답을 하나씩 받을 때는 형식 구문 검사만. 기록을 가리키기 직전(재리뷰 입력 · architect 반영 입력 · 배너)마다 다시 재어 다르면 `STOP_FOR_USER_APPROVAL`(«기록 변조 — <경로>») | `dddjango.md:32`(판형 ③) · `:126`(R-0224) · `:131`(C5 — architect 돌아온 뒤) · `DX:86` · `DX:145` · R-3597 · R-0224 · R-3601 라벨 |
| N2 Codex 역할 spawn 의 대화 상속 | 받음 — 범위는 조정자 지시대로 **리뷰어 넷 spawn 만**(모드 불문 · 확인 모드 · Phase 2 감사 포함): «리뷰어 넷의 spawn 은 `fork_turns="none"`(v1 이면 `fork_context` 를 주지 않는다) — message 에 그 리뷰어의 입력(명세 · diff · 처분 파일 · 직전 자기 노트 경로 · 기록 경로와 기록 토큰 · 모드 · 플러그인 루트)을 빠짐없이 · 다른 역할의 spawn 은 지금 그대로». 근거: 0.159.2 스키마 문구(«Defaults to `all`» · «`fork_turns="none"` will not pass any surrounding context») + 운영 세션 실측(«Full-history forks … set `fork_turns` to "none"» · 동시 슬롯 4 — 서브 3). 우리 Codex SKILL 은 model·effort 를 지정하지 않아 «none» 과 충돌하지 않는다. 파견문 자족성: 리뷰어 입력은 Coordinator 문면이 이미 낱낱이 정한다(위 목록) — 그 목록을 message 에 싣게 문장으로 못 박았다. **후속(속도·비밀 후보)**: acceptance-tester `PHASE1_ARRANGE_CHECK`(기록 토큰을 받음) · architect · coder spawn 도 «none» 이면 대화 상속 비용과 토큰 노출이 준다 — 이번엔 바꾸지 않았다 | `DX:21` |
| N4 `<BF>` 절대 경로 | 받음: «`<BF>` = 산출물 폴더의 작업 트리 루트 기준 상대 경로 `.dddjango/<폴더>` — 절대 경로면 덧붙이기 대조가 거짓으로 실패» | `dddjango.md:34` · `DX:88` · code 블록 `dddjango.md:44` · `DX:98` |
| N5 캐시 skip 행 | 받음: «이번 울타리 창에서 네가 pre-gate 를 띄웠을 때만(캐시 skip 판정과 skip 행 append 도 띄운 것이다)» — K3 문면(K2a 무변) | `dddjango.md:60` · `DX` 같은 문단 |
| N6 공유 `.venv` 거짓 STOP | 한계만 문면에: 상태 줄을 `head=… ref=… venv=…` 칸으로 나눠 STOP 문구에 바뀐 칸을 적고, «다른 레인과 심링크로 함께 쓰면 다른 레인 설치가 `venv` 칸 STOP 을 낼 수 있다 — 빼면 창 안 설치를 못 보므로 빼지 않고, 사용자가 판단한다». 제외 목록은 세탁 통로라 두지 않았다 | `dddjango.md:44`(code 블록 상태 줄) · `:60` |
| N7 «토큰» 두 뜻 | 받음: 판형의 것은 «기록 토큰»(머리 `기록 토큰 <값>` · 응답 `기록: <경로> · 기록 토큰 <값>`) · arrange 의 막힘은 «막힘 판정 이름 `ARRANGE_BLOCKED`» | `dddjango.md:32` · 리뷰어 넷 산출(`design-review-ddd.md:22` · `design-review-api.md:41` · `design-review-db.md:23` · `discipline-reviewer.md:41`) · `design-architect.md:106` · `acceptance-tester.md:65` · `:71` |
| N9 같은 회차 재호출 이름 | 받음: «`<회차>` = 그 종류·역할의 호출 일련번호 — 반송 재호출도 새 번호 · 무효가 된 옛 기록 파일은 남기되 가리키지 않는다» | `dddjango.md:32` ① |
| N3 · N8 | 처리하지 않음(조정자 지시 — N3 은 N2 로 노출이 줄고 고의만 · N8 은 새 무한 루프 없음) | — |

## K3 재리허설 처분(scratch `rehearsal-core/report.md` 끝 · 판 `210f11b2` — 다발 1 기준 전부 통과 · 결함 셋)

| 결함 | 처분 | 바뀐 문면(`0ab73a3c`·`5d598899` 기준) |
|---|---|---|
| 1 «가능 — STOP 승인 전제»를 «조건부»로 읽어 상한이 서지 않음(확인 모드 미출현 · 리허설 L2370) — **K2b** | 받음: 상한 기준 ① «막는 것이 사용자 결정(STOP · G1 결정 항목)뿐인 «집행 가능 — 사용자 결정 전제: <항목>»은 «가능»으로 보고 그 항목은 G1 배너의 결정 항목으로 넘긴다(확인 통과의 «집행 가능»도 같다)». 리뷰어 넷 판정 1행 규범에 «집행을 막는 것이 사용자 결정뿐이면 «집행 가능 — 사용자 결정 전제: <항목>»으로 적는다 — 조건부가 아니다» — **R-3376 · R-2623 · R-3331 · R-0845 rev2**(amendment). 같은 묶음에서 반영 전 명세 사본도 `mktemp` 로 | `dddjango.md:133`(①) · `DX:152` · `design-review-ddd.md:29` · `design-review-api.md:48` · `design-review-db.md:30` · `discipline-reviewer.md:20` · Codex 역할 스킬 넷 같은 문장 · R-3590 라벨 |
| 2 울타리 명령의 `"$0"` 이 커맨드 렌더 때 인자로 바뀜(«billing») — **K3** | 받음: 위치 매개변수를 걷고 이름 있는 변수 `BF`(`env … BF="$BF" sh -c '… -- "$BF" …'`) · 덧붙이기 대조도 `"$BF/…"`. 렌더된 `commands/*.md` 의 `$<숫자>` 0(실측 grep). **재발 방지 검사**: 자리는 `corpus_lint.py`(verify-base-core · `commands/*.md` 를 이미 읽음)이나 새 검사 함수와 self-test red/green 판형이 함께 들어가야 해 «한 줄»이 아니다 — 넣지 않았다(조정자 지시). 넣는다면 ⑦ «커맨드 본문 `$[0-9]` 금지(`$ARGUMENTS` 제외)» + self-test 미니 루트에 bad/good 커맨드 한 쌍 | `dddjango.md:41` · `:56` · `DX:95` · `:110` |
| 3 `$TMPDIR/<폴더명>-…` 이 같은 폴더명 병렬 세션끼리 겹침 — **K3** | 받음: 울타리 창을 열 때 첫 명령 `mktemp -d "${TMPDIR:-/tmp}/<폴더명>-fence-XXXXXX"` 로 **울타리 폴더**를 만들고 그 경로를 적어 이 창의 뒤 명령에 `<울타리 폴더>` 로 그대로 쓴다(index 사본 `idx-$$` · 객체 `objs/` · 덧붙이기 대조 사본 · 검사기 sink `findings.jsonl` · 역할 스크래치 `<울타리 폴더>/<역할|lens>/` 전부 그 아래). 리뷰어 산출 규범의 스크래치는 «입력이 준 스크래치 폴더» | `dddjango.md:34` · `:38` · `:63` · `DX:88` · `:92` · 리뷰어 넷 산출 문단 · R-3598 · R-3599 · R-3370/R-2617/R-3325/R-0863 라벨 |

## C7 재리허설(최종판) 남은 결함 1 처분(scratch `rehearsal-core/report.md` «재리허설(최종판)» · 결함 6항 2번 · 남은 결함 1번)

- 결함: 4판 모두 닫힌 Bash 목록 밖 명령을 썼다 — `awk`(출력만) · `cut` · `sort` · `uniq` · `test -e` 를 쓰는 `if/then`·`for` 존재 확인 반복 · `python3 -c`(fixture JSON 읽기 1) · 자기 기록 Edit 1. 쓰기·제품 본문 열람은 0.
- 처분(문면 최소 · C7 커밋만 · R-3615 블록 `agent-acceptance-tester.ttl` s006/b4 — 렌더 · LEDGER s006 재기준선 · rulepack · Codex 미러). 결함 2(M-A «명세 모순» 범주)는 고치지 않았다(조정자 지시 — 품질 묶음 후보).
- **전**(Claude `acceptance-tester.md` «도구·쓰기»): «… · `ls` · `find -name`(시험 쪽 폴더에만), 제품 경로에 `test -e` · `ls -d`(실존 확인만). 그 밖의 명령(`python` · `git` · 해시 명령 · 시험 실행 · 설치 · 리다이렉트 쓰기 포함)과 Edit 는 쓰지 않는다. 쓰기는 받은 부속 기록 경로에 새 파일 한 개를 Write 로 쓰는 것뿐이다(이미 있으면 쓰지 않고 보고한다).»
- **후**: «… · `ls` · `find -name`(시험 쪽 폴더에만) 과 그 출력에 거는 읽기 전용 필터 `cut` · `sort` · `uniq` · `awk`(표준 출력만 — 리다이렉트·`system()`·파일 쓰기 금지), 제품 경로에 `test -e` · `ls -d`(실존 확인만 — 이것을 쓰는 셸 조건·반복 `if`·`for` 포함). 그 밖의 명령(`python`·`python3` · `git` · 해시 명령 · 시험 실행 · 설치 · 리다이렉트 쓰기 포함)은 쓰지 않는다. 쓰기는 받은 부속 기록 경로 한 파일만 Write·Edit 로 한다(처음은 새 파일 — 이미 있으면 쓰지 않고 보고한다).»
- Codex(`dddjango-acceptance-tester/SKILL.md` «도구·쓰기») 같은 목록 · 쓰기 «받은 부속 기록 경로 한 파일만 `apply_patch` 로 한다(처음은 Add File — 이미 있으면 쓰지 않고 보고한다 · 그 뒤 고침은 같은 파일 Update File)».
- 검증: `make verify-ontology` 11/11 · `rulepack_smoke` 15/15 · `runtime_parity_check` 정합 · `ontology_ledger_check` · `claude plugin validate dddjango --strict` · `verify-mutation` 12/12 · 재봉인 클론 전체 `make verify`(아래 «verify 갱신»).

## 의미 최종 마감 처분(scratch `review-impl-core-sem/closure-final.md` — K2a·K5 가 · K2b 세 구절 뒤 가)

| 지적 | 처분 | 바뀐 문면(`0ab73a3c`·`5d598899`·`6e618398` 기준) |
|---|---|---|
| **S1(가)** 전제 항목이 실제 사용자 결정인지 확인 없음 — K2b | 받음: «사용자 결정 전제 «가능»은 그 항목이 명세의 Y·Z·STOP 항목(architect 가 배너 override 항목·미해결 옵션·STOP 으로 낸 것) 가운데 하나일 때만 «가능» — 아니면 «조건부»». 리뷰어 넷 판정 규범도 «명세가 Y·Z·STOP 으로 올린 항목뿐이면 … 그런 항목으로 올리지 않은 결손은 «조건부» 또는 «불가»» | `dddjango.md:133`(①) · `DX:152` · `design-review-ddd.md:29` · `design-review-api.md:48` · `design-review-db.md:30` · `discipline-reviewer.md:20` · Codex 역할 스킬 넷 · R-3590 · R-3376/R-2623/R-3331/R-0845 라벨 |
| **S1(나)** G1 에서 답이 강제되지 않음 — K2b | 받음: «그 항목은 G1 배너에 `사용자 결정 필요 <항목>` 으로 싣고, 그 답이 없는 승인은 Phase 2 진입으로 해석하지 않는다(아래 5 의 `pending` 과 같다 — 그 결정만 묻는다)» | `dddjango.md:136` · `DX:155` · R-3591 라벨 |
| **S1(다)** 결정 반영이 리뷰를 건너뜀 — K2b | 받음: «`사용자 결정 필요` 항목의 답이 명세를 바꾸면 발주자 답 표기 반영·G1 override 로 처리하지 않고 ⓑ 판형(그 항목만 반영 → 확인 1회)» | `dddjango.md:136` · `DX:155` |
| K3-1(nit) 역할 스크래치가 울타리 증거 폴더 안 · after·대조 실패 처리 없음 — K3 | 받음: 역할 스크래치는 울타리 폴더 밖에 따로 `mktemp -d "${TMPDIR:-/tmp}/<폴더명>-<역할\|lens>-XXXXXX"` · «after 스냅숏·대조·덧붙이기 대조 명령이 실패해도(exit ≠ 0 · 객체 없음) 허용 밖» · 리뷰어 산출 «울타리 폴더는 건드리지 않는다» | `dddjango.md:63` · `DX:117` · 리뷰어 넷 산출 문단 · R-3599 라벨 |
| C7-1 인수 행 분류 미대조 — C7 | 받음: «파견 전에 슬라이스 계획을 입장 표와 대조 — 입장 표의 `add/update` 행은 모두 인수 행·내부 행 가운데 정확히 한 칸 · owner/path 나 계약이 acceptance-tester 몫(Phase 2 행 배정과 같은 자)인 행은 인수 행 — 어긋나면 architect 반송» | `dddjango.md:151` · `DX:170` · R-3607 라벨 |
| C7-2 Codex arrange 역할의 대화 상속 — C7 | 받음: `DX:21` 의 `fork_turns="none"` 대상에 «`dddjango-acceptance-tester` 의 `PHASE1_ARRANGE_CHECK` spawn» 을 더했다(다른 리뷰어의 기록 토큰 · 재진입 때 대화에 쌓인 coder diff 를 보지 않게 — R-3242) | `DX:21` |
| C7-3 Codex 동시 슬롯 | 받음 → **별도 커밋 K5b 로 분리**(조정자 지시 — 지금 배포판 결함이라 1차 착지). C7 에는 ⓘ 의 참조 «슬롯을 넘으면 «Codex 실행 모델» 절 «동시 슬롯» 규칙»만 남겼다. 근거·규칙은 아래 «K5b» 절 | `DX:171`(C7 판 ⓘ) |

## verify 갱신

- K5 `5996a104`: 5/5 green(`verify-v7-k5.log`). K2b `0ab73a3c`: 5/5 green(`verify-v9-k2b.log`). K5b `841b7813` · K3 `5d598899`: 5/5 green(`verify-v10-{k5b,k3}.log`). C7 `6e618398`: 5/5 green(`verify-v11-c7.log`)
- 울타리 시험(`v2/fence_test.py` — 렌더된 code 블록 그대로: `mktemp -d` 울타리 폴더 · 이름 있는 변수 · 기록 토큰 머리 · 상태 줄 칸 · 블록 안 `$<숫자>` 0 단언) 두 저장소 16/16 · `claude plugin validate dddjango --strict` 통과 · `verify-mutation` 12/12 — 최종 C7 머리 `6e618398` 에서 돌렸다(`runtime_parity_check` 정합 포함).
- 버린 중간 판: `cb9427d8`·`764269db` · `bbc784fd`·`d56e8bee` · `0b01f596`·`43545b75` · `c7204670`·`39e4bb49` · `89b37c5a`·`210f11b2`(K3·C7 1차 처분판 — 5/5 green 이었으나 리허설·마감 확인 앞) · `6556ba28`(C7 리허설 처분만) · `038ccf7f`·`0f67ed83`(마감 확인 처분 · Codex 확인 앞) · `2652450f`·`6f44f0af`(K5·K2b 앞 판 — 5/5 green 이었으나 Codex 확인 앞) · `7047ed05`~`3362c465`(W1 문장 web 맞춤 앞) · `93acb37c`·`37206c60`·`5c46abd8`(K3 재리허설 앞 — 5/5 green 이었다 · `verify-v7-{k2b,k3,c7}.log`) · `1df90d32`·`2434cc05`·`277ad9fc`(의미 최종 마감 앞 — 5/5 green · `verify-v8-*` · C7 리허설이 `277ad9fc` 로 돌았다) · `b2bf759e`·`b0ea2ca4`(K5b 분리 앞 — 5/5 green · `verify-v9-{k3,c7}`) · `7e1110a5`(C7 도구 목록 결함 앞 · verify 중단). green 로그(`verify-v4-*`)는 근거로 쓰지 않는다.

## 운영자 할 일(차례)

1. **K2a · K5 · K2b · K5b 착지**: 패치 `01~04` 를 main 에 적용 → 묶음마다 `manifest_seal.py --write` 봉인 chore(C1 과 같은 봉인 파일 — 뒤에 오는 쪽이 재발행).
2. ~~K5 Codex 확인~~ — 끝났다(운영 세션 · 0.159.2 실측 — 위 K5 절 근거). 그 결과로 K5 문면을 보강하고 K3 의 N2 를 리뷰어 spawn 으로 한정했다.
3. **K3 «작업 트리 플러그인 리허설»**(위 절 · 판 `210f11b2` 로 다발 1 통과 · 결함 셋은 위 «K3 재리허설 처분») — 수리 판 `5d598899` 로 확인 모드(재리뷰 상한 ⓑ)와 «사용자 결정 필요» 길까지 다시 본다. 통과해야 K3 를 착지한다.
4. **C7 리허설 재실행**(처분 뒤 판 `6e618398` — `277ad9fc` 리허설과의 차이는 최종 마감 C7-1·2 와 K5b 참조 · scratch `rehearsal-core` 하네스 그대로 · 판 A/B/C · 음성 N — 판 B 의 M2~M7 · 판 C 의 M-D · 읽기 명령이 허용 목록 안인지 · `판정 명세 sha256` 을 재지 않고 옮기는지) — 통과해야 C7 을 착지한다.
5. K3 · C7 착지: 패치 `05 · 06` → 봉인 chore.
6. 릴리즈: 규범이 바뀌므로 진행 중 레인의 G2 착륙 뒤에 낸다(릴리즈 창). `rulepack.json` 이 registry_gate 툴체인 digest 에 들어 G2 증거 digest 값이 바뀐다(stale 판정 없음).
