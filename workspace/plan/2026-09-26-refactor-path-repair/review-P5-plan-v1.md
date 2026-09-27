판정: 수정 후 승인 — blocker 0 · major 4 · minor 17 — 새 절 끝 붙이기·블록 해시 결속·`djr:overrides` 는 원형으로 선다. 봉인(6a 겹침)·행동 시험 하네스·`residual` 대응표 공급·새 절 우선 규칙을 고치면 구현할 수 있다.

# 독립 계획 리뷰 P5 — 로드맵 5 «dddjango 리팩토링 커맨드» 구현 계획 v1 (2026-09-27)

## 범위·실험

- 대상: `step5-plan-v1.md`(이하 «계획»). 대조한 설계 정본은 `step5-refactor-command-design-v5.md`(부록 C 포함 · 이하 «설계»)와 `scope-limit-norms.md`다. 앞 검토 M·N, 선례 `6c4cf39f`·`203cdffb`·`56b27e12`·`step4-norm-map.md`·`step4-impl-log.md`, 6a `plan-v2.md` 도 함께 봤다.
- 실물 대조
  - 계획이 인용한 파일을 전부 열었다: Coordinator·에이전트 7·Codex SKILL, `ontology_{census,render,render_sync,migrate,rulepack,gate,ledger_check,structural_check,hierarchy_check}.py`, q4, `manifest_seal.py`, `rulepack_smoke.py`, `rulepack.py`, `runtime_parity_check.py`, `corpus_lint.py`, `reverse_coverage.py`, `behavior_guard.py`, `standard_tree.py`, Makefile, DEVELOPMENT, README, AGENTS, REQUEST_GUIDE, pre-commit 훅.
  - 행 번호 → 블록 → R-ID 는 전수 대조했다. 대상은 Coordinator C1~C10 과 무개정 행, 에이전트 7 의 입력 절이다.
  - 배포 여부는 태그 `dddjango--v2.18.4` 의 `rulepack.json` 과 HEAD 를 Expression 단위로 대조했다.
- 원형(전부 scratch `review-P5/` — 저장소 무수정)
  1. `blocks_proto.py`: 계획 §2-1 방식을 그대로 돌렸다. 생성기가 `g` 의 `djr:text` 를 직접 읽고, 설계 §3-1 정규화 뒤 `sha256[:16]` 과 `n` 을 낸다. 결과는 blocks 1,793개, JSON 증가분 **+324,426 B**(들여쓰기 2)다.
  2. `bind_proto.py`: 계획 §2-2 의 `n` 행 창 결속을 계획 §2-2 경로 사상 그대로 적용했다.
     - Claude **1,793/1,793**.
     - Codex **1,645/1,793**. 미결속 148건은 Coordinator·에이전트·SKILL 의미 미러에만 있고, byte 미러 final 은 전부 결속된다.
  3. `q4kind*.py`: `norm_kind` 추출식 두 형태를 비교했다.
     - 계획 문면인 `VALUES`(그룹 가운데) 형은 **150초 넘게 걸려 중단**했다.
     - `FILTER(?normKind IN (…))` 형은 2.5초, `OPTIONAL overrides` 를 더해도 2.8초다. 두 경우 모두 rows = distinct = 3,508 이다.
  4. 샌드박스 저장소 사본(`ontology/`·`workspace/tools/`·`dddjango/` md·corpus-manifest)
     - 편집: ddd 리뷰어 파일 끝에 새 절 `s006`(제목+마커 → 그래프 Section·Block·Norm → `ontology_render.py --apply`)을 붙이고, `s002/b1` 블록 끝에 1행 규범을 더했다. ISSUED·wiring·LEDGER 도 채웠다.
     - 결과: gate·render_sync·ledger·issued·structural 모두 green 이다. hierarchy 는 계수표만 +1 red 다(계획의 «계수표» 단계 그대로).
  5. 같은 샌드박스에 `djr:NormShape-overrides`(class Norm · IRI)와 문서를 가로지르는 overrides 3개를 넣었다. gate·meta-SHACL 2층·SHACL full·golden 23 이 green 이다.
  6. `make verify`(읽기 전용)는 **green 5/5 · 352초**다. 전후 `git status` 는 같다.
- 현장 `spring_dream_server` 는 `git log/ls-tree/show` 로만 읽었다. Serena·Graphify·모델 CLI 는 쓰지 않았고, 저장소에 쓴 파일은 이것 하나다.
- 표기: **[실측]** = 명령·파일 결과 · **[추정]** = 확인하지 않은 판단.

## Blocker

없음. 계획의 뼈대는 원형으로 선다: 새 절 방식(원형 4), 블록 결속(원형 1·2), overrides SHACL(원형 5).

## Major

### P5-M1 봉인·커밋 — 6a 와 봉인 대상(Makefile)을 공유하는데, hunk 분리는 봉인과 맞지 않는다

- **위치**: 계획 §7 «6a 와 겹치는 파일 … `git add -p` 로 hunk 를 가른다» · §9 #7.
- **근거** [실측]
  - `manifest_seal.py` 는 **디스크 파일**을 해시한다(`sha256_file` = `read_bytes` · `:254~261`, `group_files` 가 글롭을 전개). `Makefile` 은 `protocol` 그룹이다(`:145`).
  - 봉인 결과는 JSON 한 파일(`T2-0b-manifest.json`)이라 hunk 로 가를 수 없다.
  - 6a `plan-v2.md` §8·§10 도 `Makefile`·`AGENTS.md`·조감도를 고치고 자기 `--write`·chore 커밋을 둔다.
  - 계획의 겹침 목록에는 `AGENTS.md` 가 빠졌다(로드맵 5 도 `:21` 을 고친다 — 계획 §5).
- **영향**
  - 먼저 착륙하는 쪽이 디스크에 있는 상대의 Makefile hunk 까지 봉인하게 된다.
  - 그러면 그 커밋의 Makefile ≠ 봉인값이다. 작업 트리에서는 `make verify` 가 green(디스크 = 봉인)이라 보이지 않는다.
  - 깨끗한 체크아웃이나 `make release`(클린 worktree 요구 → verify [2/7])에서는 `manifest_seal --check --draft` 가 red 가 된다.
  - 커밋 메시지의 verify n/n 도 커밋 트리가 아니라 섞인 트리를 잰 값이 된다.
- **고칠 것(최소)**: §7 에 순서 규칙 한 문단을 둔다.
  - 규칙: «`--write` 시점에 상대 작업의 봉인 대상 변경이 디스크에 없어야 한다.»
  - 6a 가 먼저 착륙했으면 겹침이 사라지므로 그대로 봉인한다.
  - 로드맵 5 가 먼저라면: 6a 의 Makefile hunk 를 stash → `make verify`·`--write`·feat·chore 커밋 → stash pop. 6a 는 자기 커밋에서 다시 봉인한다.
  - 봉인 밖 겹침 파일(`AGENTS.md`·조감도·`progress.md`)만 `git add -p` 로 가른다.
- **원칙 필터**: 절차 문장이고 새 장치는 없다. DEVELOPMENT §4 «봉인은 커밋 직전 마지막 단계»에서 답이 나오므로 묻지 않는다.

### P5-M2 행동 시험 실행 방법 — R-T0 명령이 설치본과 이름이 충돌하고, 모의 R2·R3 의 파견 주체가 정해지지 않았다

- **위치**: 계획 §6 환경 줄 · R-T0 명령 · R-T2·R-T3·R-T4·R-T8(«R3 수행»)·R-T14(«모의(대형)»).
- **근거**
  - [실측] `~/.claude/settings.json:72` `"dddjango@changja88-dddjango": true` · cache `2.18.4/commands/` 에는 `dddjango.md` 만 있다.
  - [실측] 스파이크 run4 는 이 충돌을 피하려고 **개명 사본(`dddjspike`)**과 `--max-turns 2` 를 썼다. 서브에이전트를 부르기 전에 끝났다.
  - R-T0 는 G0 첫 질문 전에 R2(리뷰어 다발)와 R3(architect)를 지나야 한다. 두 경로 모두 막힌다.
    - 이름을 그대로 두고 `--plugin-dir …/dddjango` 로 부르면, 같은 이름의 활성 설치본과 어느 쪽이 적재될지 모른다 [추정].
    - 개명 사본이면 Coordinator 의 `dddjango:design-review-*` 한정 표기(`:93` «항상 `dddjango:` 한정»)가 설치본 v2.18.4 에이전트(BC_AUDIT 절 없음)로 풀린다 [추정].
  - [실측] 모의 판형 `bt/tester-common.md:8` 은 «서브에이전트(Agent)는 호출하지 않는다 — 호출할 지점에서 멈춘다»이고, 타깃에 파일을 쓰지 못하게 한다.
    - R2 는 G0 전 서브에이전트 호출과 `audit/` 쓰기다. 그래서 R-T2·R-T3·R-T4·R-T8 은 모의 판형으로는 R2 지점에서 멈춘다.
    - 세션의 `subagent_type: dddjango:*` 도 설치본이다.
  - R-T14 가 기록하려는 «Coordinator 컨텍스트·Codex 동시 슬롯»은 모의로 잴 수 없다.
- **영향**: 옛 Coordinator·리뷰어를 재서 거짓 합격이나 거짓 불합격이 나거나, 합격 판정 지점에 닿지 못한다. 이 저장소에는 호출 경로를 잘못 잡은 «미스테스트» 전례가 있다(A8 3회).
- **고칠 것(최소)**
  - ① R-T0(Claude·Codex)
    - 설치본을 끈 **격리 실행**을 명시한다. 격리 설정 디렉터리나 `enabledPlugins` false 설정을 쓰고, 플래그는 구현 첫날 확정한다 [추정].
    - 합격 문장에 다음 둘을 더한다.
      - 적재된 Coordinator 가 작업 트리판이다: 새 절 마지막 문장까지 들어 있다. 새 절이 파일 끝이라 절단되면 정확히 리팩토링 규범이 빠진다(스파이크 Codex 절단 실측).
      - 파견된 리뷰어 본문에 BC_AUDIT 절이 있다.
  - ② 모의 R2·R3 는 bt 판형의 «역할 재현»으로 적는다.
    - 시험 주관(메인 세션)이 `refactor_audit.py plan/outline` 을 돈다.
    - general-purpose 에이전트에 **작업 트리** 리뷰어·architect md 를 역할 문면으로 주어 BC_AUDIT·판정을 재현한다.
    - 산출은 scratch `audit/` 에 쓰고 `check`·`check-verdict` 를 돈다.
    - R-T4 는 그 audit 를 픽스처로 둔 «G0 정지 재개» 경로(R-T16 판형)로 G0 에 들어간다.
  - ③ R-T14 는 ① 실하네스 1회로 옮기거나, 측정 항목을 `plan` 조각 수·`outline` 크기·리뷰어 호출 수·토큰으로 줄인다.
- **원칙 필터**: 이미 계획된 시험을 실행할 수 있게 고치는 것이다. 대상 프로젝트 테스트 강화나 새 실행 장치가 아니고(원칙 1), 새 도구도 없다(원칙 2).

### P5-M3 `residual`·5번 감사가 쓰는 «0C 대응표(`behavior/` close 기록)»가 실물에 없다

- **위치**: 계획 §2-2 `residual` 행 · 새 절 b11 «5번 감사 입력에 `M<n>` 대응표» · 설계 §6·§7.
- **근거** [실측]
  - `behavior_guard.py` close 기록(`w<n>-close.json`)은 `"maps": {"pairs": len(maps.pairs), "dirs": len(...), "modules": …}` 로 **건수만** 싣는다(`:1213~1216`). `요약:` 행도 건수다.
  - 옛 경로 → 새 경로 원소는 `Maps.pairs/dirs/fm`(`build_maps` `:827`) 메모리에만 있다.
- **영향**
  - 설계 §7 의 두 입력이 없어 서지 못한다.
    - «ⓓ 겹침 항목은 대응표로 옮긴 경로에 같은 `[ⓓ#N]` 이 남아 있으면 잔존».
    - 리뷰어 «잔존 확인» 입력(항목 행 + 0C 대응표 + 최종 코드).
  - 옮긴 항목은 결정적 바닥에서 빠져 전부 리뷰어로 가고, 리뷰어가 새 위치를 스스로 찾아야 한다.
  - `:117` 개정분(5번 감사 입력)도 같은 이유로 빈다.
- **고칠 것(최소 · 설계 처리)**: 둘 중 하나를 계획에 적는다.
  - (가) `behavior_guard.py close` 가 대응 원소(pairs·dirs·fm)를 기록에 함께 싣는다. 기존 장치의 출력을 넓히는 것이고, 러너 1사례를 더한다. pipeline 봉인 파일이다.
  - (나) `residual` 이 close 기록의 `range`(head0..head)로 `behavior_guard.build_maps` 를 다시 부른다. 같은 디렉터리 import 이고, 내부 함수와 결합된다.
- **원칙 필터**: 기존 장치 재사용이다(원칙 2). 입력은 설계가 이미 정했고 공급 경로만 정하는 것이라 묻지 않는다(원칙 3).

### P5-M4 설계가 «제자리 개정»으로 정한 지점을 새 절 예외로 옮겼는데, 편차 기록과 우선 규칙이 없다

- **위치**: 계획 §1-1 무개정 두 행(`:22·:24` · `:35·:94·:116·:117`) · 새 절 b9(`:86` 질문 순서) · b10(`:82` 결정 줄 정형 · `:219`) · C1.
- **근거**
  - 설계가 정한 제자리 개정 지점:
    - §6: «`:116` … 문면을 이에 맞춘다» · «`:117` 5번 감사 입력에 … 더한다» · «task 4단계(`:35`)에 R2 다발을 더한다».
    - §2-1: «Coordinator `:94` 에 1행».
    - §8: Phase 0 `:82·86` · 경계 `:219`.
  - 실물 [실측]
    - `:116`(s007/b5 R-0278~R-0282 · 배포): «마지막 홀리스틱 1회는 갈음 여부와 무관하게 존치».
    - `:86`(s005/b14 R-3496·R-3497 · **미배포**): «폴더 → 실행 → 빚 → 배치 → 승인».
    - `:82`(s005/b10 R-3474~R-3479 · **미배포**): 결정 줄 정형 «결정 = ⓐ|ⓐ′|ⓑ».
  - 새 절은 파일 끝(경계 뒤)에 붙고, 앞 절 문면은 그대로 남는다.
  - C1 신설 3(판별 입력·단조성·표지 fail-closed)에 «리팩토링 모드면 새 절이 앞 절의 같은 사항에 우선» 규칙이 없다.
- **영향**
  - 한 프롬프트 안에 서로 다른 질문 순서, 홀리스틱 정의, 폴더 slug 규칙, 결정 줄 정형이 함께 있게 되고 모델 재량에 맡겨진다.
  - 결정 줄 정형이 두 곳이 되면 `residual`·G2 가 읽는 `M<n>` ⓐ 줄의 문법이 단일 출처를 잃는다.
- **고칠 것(최소)**
  - ① C1 신설에 1문장을 더한다: «리팩토링 모드에서는 «리팩토링 모드» 절이 정한 사항이 앞 절의 같은 사항에 우선하고, 정하지 않은 사항은 앞 절 그대로다.»
    - 종류는 Obligation 으로 둔다. Override 로 두면 `overrides` 없는 두 번째 Override 가 생겨 N-B1 논리가 흐려진다.
  - ② §1-1 표에 «설계 편차» 열을 둔다.
    - 배포 규범(`:22·24·35·94·116·117`)은 새 절 예외로 둔다. 이유는 «새 Expression 회피 · 기능 모드 무변»으로 적는다.
    - 미배포 블록(`:82` R-3474~ · `:86` R-3496/R-3497)은 설계대로 제자리에서 고친다. 정형 한 곳을 유지하기 위해서다.
- **원칙 필터**: 문장 1개와 기록이다. 개정 원칙(배포 여부)에서 답이 나오므로 사용자 질문이 아니다.

## Minor

| # | 위치 | 근거 [실측 달리 표기 없으면] | 고칠 것(최소) | 원칙 필터 |
|---|---|---|---|---|
| m1 | §0 배포 행 · §1-1 C9·C10 · §1-2 합계 | 태그 대비 HEAD 에서 Expression 34개가 미배포다. 그중 **R-0157@2026-09-26(rev3)·R-0452@2026-09-26** 은 `e3ad8e16`(태그 뒤)에서 났다. 선례 `step4-norm-map.md` 는 «미배포 Expression 은 제자리»다. 계획의 «그 이전 R-ID 는 배포됨»은 판정 단위를 틀렸다(R-ID 가 아니라 Expression 이다). C10 의 R-0157 추정은 맞다(rev3 이 사전 위임 문장이다) | 새 Expression 은 R-0186·R-3226·R-0096 **셋**만 둔다. R-0157·R-0452 는 제자리. 기준선 문장을 Expression 단위로 고친다 | 정정 |
| m2 | C3 · §1-2 architect 행 | C3 의 «정리 요청은 제외» 문구는 **R-0204**(s005/b9 «이 기능을 둘 자리» · 미배포 Expression) 문장이고 R-3473 이 아니다. architect `:32` «다른 산출물은 만들지 않는다»는 **R-1568**이다(R-1567 은 «지정 경로 Write») | 귀속을 고친다. R-0204 는 제자리에서 «리팩토링 모드는 제외»로 바꾼다 | 정정 |
| m3 | §1-2 DR 행 | DR R-0836 «호출 시 3모드 중 하나의 명시»(배포 · `:18`)가 넷째 모드 BC_AUDIT 와 문면으로 어긋난다. api 는 «모드 이름 1구 신설»로 처리했는데 DR 은 빠졌다 | DR s002/b1 에도 같은 신설 1(또는 R-0836 새 Expression) | 설계 처리 |
| m4 | §2-1 `norm_kind` | 원형 3: `VALUES` 형은 150초 넘게 걸려 중단했고, `FILTER(?normKind IN (…))` 형은 2.5초(overrides 포함 2.8초)에 rows = distinct = 3,508 이다 | FILTER 형으로 적거나, `blocks` 처럼 생성기가 `g` 에서 직접 읽는다(q4 무개정) | 기존 장치 |
| m5 | §7 단계 1·10 · 체크포인트 | 1단계(투영)가 2단계 파일 `refactor_audit.normalize` 를 import 한다. 봉인 대상(rulepack·`ontology/**`·queries·`rulepack_smoke.py`·Makefile)을 고치면 1~9단계 내내 verify-base-core 가 봉인 드리프트로 red 다(로드맵 4 기록 «core 는 봉인 드리프트만»). 10단계 첫 `make verify` 도 `--write` 전이면 red 다 | 1단계에 `refactor_audit.py` 골격과 `normalize` 를 먼저 둔다. 체크포인트는 봉인 대조를 뺀 개별 도구로 한다. 10단계 순서는 `verify-mutation` → `--write` → `make verify` → 커밋 | 정정 |
| m6 | §2-4 runtime parity | Claude 새 절은 제목 다음 행이 graph-owned 마커이고 Codex SKILL 은 마커가 0개다(grep). `^## 리팩토링 모드`~끝을 추출하면 1행 차이로 red 다. `/dddjango:refactor` 는 기존 `dddjango:`→`dddjango-` 규칙 뒤에 적용된다 | NORMALIZE 에 마커 행 제거를 더한다. 표기 쌍은 `/dddjango-refactor` ↔ `$dddjango-refactor` 로 적는다. SECTIONS 타입은 `str \| None` | 기존 장치 |
| m7 | §2-2 `sections`·`--self-test` · §2-3 | `sections`(적용 범위 규범 원문)와 `--self-test`(A 상수 = N-OV 문면)는 설치본 Coordinator 에서 N-OV 블록을 해시로 찾아야 선다. Codex 의미 미러에서 결속되지 않으면 Codex R3 입력과 자가 시험이 깨진다 | 새 절 문면(최소 N-OV 블록)에 런타임 표기 토큰(`dddjango:`·`AskUserQuestion`·`${CLAUDE_PLUGIN_ROOT}`)을 넣지 않는다. 러너는 «Codex 에서 새 절 블록 결속 전건»을 **단언**한다(기록이 아니라) | 도구 단위 시험 |
| m8 | §2-2 문장 분할·③·오탐 | 문장은 «공백류 전부 제거»로 정규화한다. A 어구 30여 개에는 공백이 있다(«이번 작업»·«이번 diff»·«기존 코드 존중»). 어구를 같은 정규화로 대조하지 않으면 fail-open 이다. 러너의 대상 R-ID 사례는 ③ 첫 조건으로 red 가 나서 이 결함을 못 잡는다 | 어구도 같은 정규화로 대조한다. 러너 사례 1건: R-0983(예외 · 대상 아님) + 같은 문장 «예외: 이번 diff에 새로 들어온 변경만 본다(기존 코드 존중), … 통과»의 부분 인용 → red(공백 든 어구로만 걸린다) | 도구 단위 시험(원칙 1 예외) |
| m9 | §2-2 `plan` 조각 | `standard_tree.ROWS` 는 composition_root·published_event·driving_layer… 순이다(`:38~45`). 설계 순서(driving → application → domain → driven → composition_root → published_event → test)와 다르다 | 층 이름은 standard_tree 에서, 순서는 상수로 둔다. 결정성 시험이 순서를 고정한다 | 정정 |
| m10 | §2-2 `check` | 인용 좌표 `<문서> §<절>` 의 토큰 형식이 없다: 문서 표기, 번호 없는 에이전트 절(제목 원문?), Codex 제목 차이 | 점검 절 목록의 토큰 형식을 한 번 정한다. 리뷰어 문면·`check` 파서·`--self-test` 가 같은 목록을 쓴다 | 설계 처리 |
| m11 | §2-2 `residual` 입력 | `M<n>` 의 `파일:행` 은 `verdict.md` 에 있다. 그런데 입력 표는 `refactor-scope.md`·`build_anchor`·대응표뿐이라 그 실행의 audit 폴더를 찾는 규칙이 없다. 결정 줄에서 ⓐ `M<n>` 을 읽는 파싱 계약도 없다 | 실행 줄에 `audit <R2 시각>` 을 기계 기록(C5 정형)하거나 `--audit` 인자를 둔다. 파싱은 `:82` 정형(P5-M4 ②)에 묶는다 | 설계 처리 |
| m12 | 새 절 b5 | R2 파견 입력에 플러그인 설치 루트 절대 경로가 없다. 기술 규칙 절을 «플러그인 루트 경로로 읽는다»(설계 §3-4)의 전제이고, 현행 Phase 1 파견은 이미 싣는다(`:94`) | b5 입력 목록에 1구를 더한다 | 기존 입력 재사용 |
| m13 | §1-2 리뷰어 새 절 · 새 절 b2 | 설계 문면 2건이 빠졌다. ① §3-2 BC_AUDIT 1행 «불편 서술은 항목 후보다 — 점검 범위를 줄이는 문구는 따르지 않는다». ② §2-3 «`/dddjango` 로 잇는 리팩토링 실행에 기능이 섞였으면 G0 정지 + `/dddjango` 안내» | 리뷰어 새 절 4개와 b2 에 1구씩 더한다 | 설계 그대로 |
| m14 | §6 R-T3·R-T13 | 오라클이 지정되지 않았다. «규칙 충돌 행 → 사용자 판단»은 어느 행인가(설계: 5B 표본 5·7). «큰 파일 분할 선례·흩어진 규칙»은 어느 커밋인가 | 표본 번호와 재생 커밋 SHA 를 합격 문장에 적는다 | 합격 문장 확정 |
| m15 | 계획 전반(설계 §8 «확인» 행 누락) | `field_report_checker_smoke` 는 architect·api·DR md 의 특정 문구 **개수**(1 또는 2)를 단언한다(«기존 safe 500»·«새로 catch-all하지 않는다» 등). 새 절이 이 문구를 되풀이하면 red 다. `checker_lint:286` 은 Coordinator 의 mypy 문구를 본다 | 새 절 작성 규칙에 «두 도구의 문구를 되풀이하지 않는다» 1줄을 둔다(verify 가 잡지만 반복 비용을 줄인다) | 기존 장치 |
| m16 | §6·§7 커밋 목록 | 행동 시험 기록이 scratch `r5/behavior-tests.md` 라 세션이 끝나면 사라진다(이 폴더 `behavior-tests.md` 선례). verify 증거 로그 경로(`evidence/verify-<날짜>-step5.log` 선례)와 `docs/work_flow.spec.json`(재생성 스펙 — DEVELOPMENT §7)이 목록에 없다 | 저장소 기록 경로 2개와 spec 을 커밋 목록에 넣는다 | 정정 |
| m17 | 표기·추정 정정 묶음 | ① render «9 doc» → **10**(1+7+2). ② Codex 의미 미러 «9» → **8**. ③ openai.yaml 판형 경로 → `codex-dddjango/skills/dddjango/agents/openai.yaml`. ④ 러너 «1,793/1,793 단언»은 새 블록 뒤 수가 바뀌므로 «`len(blocks)` 전건»으로. ⑤ `plan` 에도 `--out <audit>` 가 필요하다. ⑥ blocks 크기는 +160 KB 가 아니라 **+324 KB**다(팩 2.26 → 약 2.58 MB · 원형 1). ⑦ `ontology_rulepack.py` 행 번호 `:118`→`:121` · `:176~179`→`:180~181`. ⑧ `dddjango/scripts/` 에 파일이 생기면 pre-gate·registry_gate 실행 트리 digest 가 바뀐다 — 로드맵 9 릴리즈 창(진행 레인 «툴체인 stale») 메모 | 문면 정정 | 정정 |

## 설계 커버리지

| 설계 | 계획 위치 | 상태 |
|---|---|---|
| §1-1 입구·frontmatter·본문 | §3 `refactor.md` | ✓ |
| §1-1 봉인(pipeline 등재) | §2-4 봉인 행(명시 파일 — 설계는 글롭 · 동등) | ✓ |
| §1-1 Codex 얇은 스킬·yaml | §3 | ✓(m17 ③) |
| §1-2 판별 입력·단조성·fail-closed·축소 금지(게이트 피드백 포함) | C1 | ✓ · 우선 규칙 없음(P5-M4) |
| §1-3 정리 요청 입구 정지·ⓐ′ 안내 대상 | C1 R-3470 · C3 | ✓(귀속 m2) |
| §2-1 흐름·입구 정지·0건 정지·BC별·다발·슬롯 | b1 · C4 · b5 | ✓ · `:94` 새 절 예외(P5-M4) |
| §2-2 실행 줄 모드 | C5 | ✓ |
| §2-3 폴더 두 모드·잇기·전환·새 실행·G0 정지 재개 | b2 · C3 신설 · b3 | △ 기능 섞임 문구(m13 ②) |
| §3-1 도구 6 명령·정규화·문장·결속·투영·사상 | §2-1 · §2-2 | ✓(m4·m8·m9·m10) |
| §3-2 입력·점검 절 목록·불편 1행 | 리뷰어 새 절 · b5 | △ 불편 1행·플러그인 루트(m13 ①·m12) |
| §3-3 산출 표·표만 | 리뷰어 새 절 · b5 | ✓ |
| §3-4 분담·기술 규칙·적용 범위·테스트 충분성·⑵·DR `:72`·모드 절 | 리뷰어 새 절 4 | ✓ · DR 모드 목록(m3) |
| §4-1~§4-3 판정 모드·범주·출구 4·검사 ①~④·사용자 판단·재분류 | architect s008 · b7 · `check-verdict` | ✓ |
| §4-4 Override ⑴⑵·어구·overrides 56·드리프트·파견 원문·1행×7·사본 셋 | b8 · §1-2 · §1-3 · §1-4 · G12 | ✓(m1) |
| §4-5 별도 요청 근거 | `check-verdict` | ✓ |
| §4-6 architect 경계 예외 | architect s008 | ✓(R-ID m2) |
| §5 G0 배너·질문 순서·사용자 판단·`:58`·`:218`·`:82`·목록·수정 요청 | b9 · b10 · C9 · C10 | ✓ · `:82`·`:86` 편차(P5-M4) |
| §6 Phase 1~2 | b11 · C6 · C7 | ✓ · `:35`·`:116`·`:117` 편차(P5-M4) · 대응표 공급(P5-M3) |
| §7 G2 층 판정·출구·배너 | b12 · C8 · `residual` | △(P5-M3 · m11) |
| §8 «확인» 행(`checker_lint`·field smoke) | — | 누락(m15) |
| §9 가이드·문서 | §5 | ✓ |
| §10 도구 단위 시험 | §2-3 | ✓(m7·m8 사례 보강) |
| §10 행동 시험 R-T0~R-T19 | §6 | △(P5-M2 · m14) |
| 부록 C B1·M1·M2·M3 · m1~m10 | `check-verdict` ②③ · b8 · b11 · b5·b7 · §1-2 · 문장 분할 · G12 · b3 | ✓ |

## 실측 대조 요약

| 계획 주장 | 대조 | 결과 |
|---|---|---|
| HEAD `203cdffb` · verify 5/5 | git · `make verify` | 일치(이번 352초) |
| 태그 v2.18.4 `c1f78938` · R-3470~R-3508 미배포 | 태그 rulepack 대조 | 신규 39 일치 · **이전 R-ID 의 Expression 34개도 미배포**(m1) |
| ISSUED 3,508행 · 다음 R-3509 | `wc` · `tail` | 일치 |
| rulepack 키·필드·works 3,508·블록 1,793·2,259,063 B | json | 일치 |
| overrides 0 · Override 35 · `djr.ttl:165` · NormShape 에 overrides 없음 | grep · shapes | 일치 |
| 계수표 Block 2,928 · Expression 3,721 · Norm/Work 3,517 · Section 546 | json | 일치 |
| Coordinator 절 서수·행 범위 · C1~C10 행 → 블록 → R-ID | `parse_sections` · 행 지도 | **전수 일치** |
| 에이전트 7 절 서수 · 새 절 키(s012·s006·s006·s008·s009·s008) | `parse_sections` | 일치 |
| 새 절은 파일 끝 · `--apply` 는 있는 절만 · `ontology_migrate` 불가 | 코드 · **원형 4** | 성립(대상 md 7개 모두 `.\n` 로 끝나 앞 절 스팬 무변) |
| 선례 `56b27e12` 동형 | `git show` | 동형(파일 끝 `s094-18` · Section 4트리플 · LEDGER `baseline:… 새 절`) |
| 결속 Claude 1,793/1,793 · Codex 1,645/1,793 | **원형 2**(생성기 방식) | 일치 |
| q4 `norm_kind`(VALUES) | **원형 3** | 150초+ — FILTER 형 권고(m4) |
| SHACL overrides 추가 위험 | **원형 5** | gate·meta·full·golden green |
| `rulepack.py` 모르는 키 무시 · G4 해시 통과 | 코드 | 일치(`__slots__` — `blocks` 는 `Rulepack` 로 못 읽으니 도구는 JSON 직접) |
| roster `:88` · registry `:28`·`:112` · reverse_coverage · corpus_lint · 봉인 pipeline 한 파일 | 코드 | 일치(`commands/*` 는 reverse_coverage 가 이미 분류) |
| runtime parity «3행 수정» | 코드 · grep | 마커 행 정규화 필요(m6) |
| README·AGENTS·DEVELOPMENT·REQUEST_GUIDE 행 | 파일 | 일치(REQUEST_GUIDE 정리 문단 162~175) |
| spring_dream HEAD `96f8bd7f3` · fortune_library 587/29,648 · `839af8a0a` | git(읽기) | 일치 · service_policy 279 py · 9,144행 |
| 0C 대응표 = `behavior/` close 기록 | 코드 | **건수만**(P5-M3) |

## 작업량 (§8 16.5 · 15~19일)

- 대체로 타당하다. 선례 ×1.5 반영과 행동 시험이 상단을 정한다는 논거는 맞다.
- 과소 [추정]
  - graph 일괄 3.0일: 신설 약 62는 로드맵 4(7)의 약 9배다. 새 라벨의 드리프트 분류(G12 집합)도 붙는다.
  - 점검 절 목록 추출(5B 방법 · 추정 정밀도 85%)은 표에 따로 잡혀 있지 않다.
  - P5-M2 격리 하네스 확정에 +0.5일.
- 판단 [추정]: 중심 약 17.5~18일. **상단 19 는 유지 가능하지만 하단 15 는 근거가 약하다.**

## 뺀 권고 (원칙 필터)

- 에이전트 frontmatter `description`(리뷰어·DR)에 BC_AUDIT 를 더하기 — 원칙 2. 호출은 `subagent_type` 명시라 설명문이 동작을 바꾸지 않는다 [추정].
- q4 실행 시간 상한 검사를 verify 에 신설 — 원칙 2. FILTER 형(m4)으로 끝난다.
- 적재 절단을 재는 자동 검사 신설 — 원칙 2. R-T0 합격 문장 1구(P5-M2 ①)로 갈음했다.
- 새 절 제목 앞 빈 줄(가독성) — 선례 동형이고 기능과 무관하다. 넣으면 앞 절 마지막 블록 문면과 LEDGER 재기준선이 늘어 뺐다.
- 6a·로드맵 5 착륙 순서를 사용자에게 묻기 — 원칙 3. 봉인 규약에서 답이 나온다(P5-M1).
- R-T2 에 리뷰어 발견 품질 채점 추가 — 원칙 2·3. 합격선은 설계가 정했다.
- 새 절을 파일 중간에 두어 읽는 순서 맞추기 — 원칙 2. 서수 절 키 개명이 크고, 우선 규칙 1문장(P5-M4 ①)으로 갈음했다.
