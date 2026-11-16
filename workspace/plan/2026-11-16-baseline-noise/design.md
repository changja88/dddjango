> 설계 정리본 — 3판(dddjango 2.40.0) 설계 초안 셋(단위 c 글 v3 · b 검사기 v3 · a 게이트 v5 — 모두 독립 검토 · 좁은 재확인에서 닫힘)을 묶고, 현장 코드 이름을 걷은 판. 구현 중 바뀐 것(넷째 확인 W1 · W2 · 계획 검토 M4 · 구현 독립 검토 처분 — 하위 폴더 프로젝트 · #257 컨테이너 바꿈 · 글 사소)은 `plan-2.40.0.md` · `plan.md` 가 정본이다. 본문의 `pan3-1116/…` · `a/` · `b/` · `c/` · `review-*` 같은 경로는 작업 폴더(배포 뒤 지움)다.

# dddjango 2.40.0 — 설계 정리본 (2026-11-16)

# 3판 단위 c 초안 v2 — F4-29 · F4-45(규칙 글 · 에이전트 글)

- 재현자 C · v1 2026-11-16 03시대 · v2 2026-11-16 09시대 · **v3 2026-11-16 09시대**(KST · `date` 실측). v3 은 좁은 재확인 1(`review-c/RECHECK-1.md` · 새 지적 N1 · N2 · N3 · 걱정 하나)과 처분(`op-rev/DISPOSITION.md` «좁은 재확인 1»)을 받아 고쳤다 — 끝 절 «v2 → v3 바뀐 것». v2 는 설계 독립 검토(`pan3-1116/review-c/REVIEW.md` · 중요 5 · 사소 9)와 운영자 처분(`op-rev/DISPOSITION.md` «review-c»)을 모두 받아 고쳤다. 바뀐 것은 끝 절 «v1 → v2 바뀐 것».
- 대조: 배포판 2.39.0(`dddjango--v2.39.0` = f36fa9f9) 사본 `pan3-1116/rel/`. 2.39.0 → main b29635ca 사이 `dddjango/` · `codex-dddjango/` · `ontology/` 변경 0행.
- 두 항목 모두 글 항목이다. 검사기 판정이 바뀌지 않아 현장 사본(리허설 클론) 대조는 해당 없음.
- 돌린 것(모두 `pan3-1116/c/` 안 · 홀로 선 장난감 또는 읽기만):
  - v1: `toy45.sh` · `toy45-pathspec.sh` → `*.out`(git 읽기 길 · 글롭이 먹는 명령).
  - v3: `v3_inflow.sh` → `v3_inflow.out` — v3 R-3607 글(오래된 머지부터 · 뒤 머지가 이김 · 목록 SHA 를 `rev-parse` 로 풂)을 그대로 옮겨 검토자 장난감 `review-c/toyR-r1` · `r2` 에 40자 · 9자 목록 둘로 돌리고 배포판 사본 pre-gate `approved_inflow`(`review-c/inflow_driver.py`)와 견줌.
  - v2: `v2_inflow.sh` → `v2_inflow.out` — v2 유입 판 식을 글 그대로 옮겨 검토자 장난감 `review-c/toyR-r1 ~ r4` 에 읽기만으로 돌림 · `v2_globs.sh` → `v2_globs.out` — 글롭마다 `:(glob)` · pytest 설정 파일 · 뿌리 파일 · `v2_labels.py` → `v2_labels.out` — 새 라벨 G12 적중.
- 두 항목 모두 플러그인 정의 · 이미 정한 구조에서 답이 나온다 — **질문 생략 · 설계 처리 · 이의 시 뒤집음**.

---

## F4-29 — architect 자기모순 스캔이 명세 안 수 표기를 대조하지 않는다

### 재현(글 대조) — 지금도 그대로

| 자리 | 문장(요지) | 정본 |
|---|---|---|
| `rel/dddjango/agents/design-architect.md:104-105` | 절 `## 리뷰 반영·충돌 중재` — graph-owned | `agent-design-architect.ttl` s006 |
| `rel/dddjango/agents/design-architect.md:114` | «초안·수정을 완료로 넘기기 전, 절 간 **자기모순을 1회 스캔**한다 — 같은 개념의 소유권 · 명명 · 시그니처 · 불변식이 절마다 일치하는지 …» — 대조 거리는 이 넷뿐 · 수 표기 없음 | **R-1754**(Obligation «완료 인계 전 절 간 자기모순 1회 스캔» · `R-1754@2026-08-22` rev 1) · R-1755(해소) · R-1756(리뷰어 대체 금지) — 블록 `s006/b5`(`rel/ontology/rules/agent-design-architect.ttl:1757` · `:2850-2855`) |
| `rel/codex-dddjango/skills/dddjango-design-architect/SKILL.md:107` | 같은 문장(손 미러) | — |
| `rel/dddjango/commands/dddjango.md` | 조정자는 이 스캔을 부르거나 대조하지 않는다(찾음 0) | — |
| `rel/dddjango/scripts/design_pregate.py:12` · `:488` · `design-architect.md:92` | pre-gate 는 기계 블록만 전사 — «산문 추론 재료는 0» | (pre-gate 성문 묶음) |
| `rel/dddjango/scripts/*.py` | 한글 수 낱말 · 목록 길이를 보는 도구 0 | — |

- 문장은 fac248bb(2026-05-27)부터 안 바뀌었다(2.18.4 `:105` = 2.39.0 `:114`). 보고 때 «§15» 는 dddjango 규칙 번호가 아니라 현장 명세 안에 architect 가 스스로 만든 «자기모순 스캔» 절 번호다.
- 현장 꼴: 슬라이스 절이 «docstring 셋» 이라 적고, 도메인 절은 고칠 docstring 을 메서드별 불릿 안에 흩어 둘만 적음 → coder 는 둘만 씀 → Phase 2 S2 경량 감사가 nit 로 잡음. 현장 architect 는 다른 자리에서는 셈 대조를 했지만 규칙이 요구하지 않아 고르게 하지 않았다.

### 원인
R-1754 의 대조 거리 목록이 «같은 개념의 소유권 · 명명 · 시그니처 · 불변식» 넷으로 닫혀 있고, 수를 세는 말(«셋» · «N 개»)과 그 수가 가리키는 것의 실제 개수는 들지 않는다.

### 같은 꼴의 다른 자리
- 리뷰어 확인 모드: «diff 가 바꾼 이름·값·결정·표 행이 명세의 다른 자리와 맞는지»(`discipline-reviewer.md:40` · `design-review-ddd.md:17` · `-api.md:36` · `-db.md:18`) — 반영 diff 가 수를 바꾼 때만 닿는다. 처음부터 어긋난 수는 몫 밖.
- `NIT_DIFF_CHECK` 는 «한글 수 낱말» 고침을 내용 바뀜으로 친다(`discipline-reviewer.md:34`) — 플러그인이 이미 수 낱말을 뜻 있는 글로 본다.
- 자매 플러그인 `dddjango-web/agents/design-architect-web.md:100` 의 같은 스캔은 명세 목록 ↔ 바깥 재료(추출 토큰 · 시안 아이콘 · asset-manifest)의 회계를 대조한다 — 명세 안 «수 낱말 ↔ 목록» 축은 없다. 이번 고침은 architect 자기점검 거리 하나를 더할 뿐 게이트 · 리뷰어 흐름 · 막힘을 더하지 않으므로 web 보다 엄격한 기준을 거는 것이 아니다. web 은 보고가 없어 그대로 둔다.

### 고칠 방향
1. **R-1754 개정(글만) — 추천.** 대조 거리에 «수를 세는 말 ↔ 그 수가 가리키는 것을 명세가 낱낱이 적은 개수(목록 · 표 행 · file-plan 행 · 여러 절에 흩어진 언급)» 를 더하고, 명세 어디에도 낱낱이 적지 않은 수(플러그인 상수 · 코드에서 세기만 하고 명세에 적지 않은 수)는 대조 밖이라고 본문에 적는다.
   - 비용: architect 가 막 쓴 명세(현장 571 ~ 860여 행)를 맥락에 둔 채 하는 판단이라 도구 호출 · 출력이 거의 늘지 않는다(모델 시간 대부분은 출력 — 11-03 실측). 개정마다 돈다는 점만 비용.
   - 거짓 지적 위험: 자기점검이라 남에게 가는 지적이 없다. 위험은 명세가 낱낱이 적지 않은 수를 억지로 맞추는 것 — «대조 밖» 본문 문장으로 막는다.
   - 효과 한계: LLM 자기 스캔은 놓칠 수 있다(현장도 스캔을 하고 놓쳤다). 거리 목록에 이름을 붙여 두는 값만 있다.
2. 리뷰어(discipline-reviewer Phase 1 lightweight) 항목 — 독립 눈이 생기지만 모든 다발에 nit 흐름이 늘고 거짓 nit(`G1 전 닫기` 왕복)가 커진다. 지금은 Phase 2 슬라이스 경량 감사가 잡아 냈다. 1 로 다시 나면 그때 연다.
3. 기계 장치(pre-gate · 명세 검사 도구) — 하지 않는다. pre-gate 는 «산문 추론 재료 0» 이 원칙이고(`design_pregate.py:12` · `design-architect.md:92`), 한글 수 낱말은 순서 · 횟수(«셋째» · «두 번»)와 섞이며 «무엇을 세는가» 는 뜻으로만 가려진다 — 거짓 지적이 크고 새 도구 · 픽스처 · EXPECTED 비용이 든다.

### R-1754 새 문장 초안(블록 `s006/b5` 첫 문장을 바꾼다 — R-1755 · R-1756 문장은 그대로)
> 초안·수정을 완료로 넘기기 전, 절 간 **자기모순을 1회 스캔**한다 — 같은 개념의 소유권(어느 계층·모델이 규칙을 갖는지)·명명·시그니처·불변식이 절마다 일치하는지(예: 한 절은 "Product가 차감을 소유"인데 다른 절이 인프라에 차감 로직을 두면 모순), 그리고 수를 세는 말(«셋» · «다섯 곳» · «N 개»)이 그 수가 가리키는 것을 명세가 낱낱이 적은 개수(목록 · 표 행 · file-plan 행 · 여러 절에 흩어진 언급)와 같은지 본다(예: 슬라이스 절은 "docstring 셋"인데 도메인 절들이 고칠 docstring 을 둘만 적으면 모순). 명세 어디에도 낱낱이 적지 않은 수(플러그인 상수 · 코드에서 세기만 하고 명세에 적지 않은 수)는 이 대조 밖이다.

- 개정 꼴: 새 Expression `R-1754@<날짜>` rev 2 · `revisionKind` amendment(대조 거리를 더함) · prefLabel 후보 «완료 인계 전 절 간 자기모순 1회 스캔(수를 세는 말 ↔ 명세가 낱낱이 적은 개수 포함 · 낱낱이 적지 않은 수는 밖)». R-1755 는 고치지 않는다.
- Codex 의미 미러: `codex-dddjango/skills/dddjango-design-architect/SKILL.md:107` 을 같은 뜻으로 손 고침.
- 구현 때: DEVELOPMENT §3 체크리스트 1(ttl 편집 · canon) → 2(gate · `ontology_render.py --apply agent-design-architect`) → 3(LEDGER 재기준선 — design-architect.md s006) → 4(target-counts ExpressionShape +1 · q4 골든 · `make rulepack`) → 6(Codex 미러). 5 · 7 · 8 해당 없음. `dddjango/agents/*.md` · `codex-dddjango/skills/**/*.md` · `ontology/**` 는 봉인 대상 → 커밋 직전 봉인 · 배포 뒤 chore 봉인.
- G12: 지금 라벨 · 후보 라벨 모두 DRIFT_RE 적중 0(`v2_labels.out`) → `DRIFT_REVIEWED` · `scope-limit-norms.md` 손댈 것 없음.
- 2.39.0 대비: 새로 막는 것 0(자기점검 거리 하나) · 푸는 것 0. 요청 가이드: 바뀔 것 없음.

---

## F4-45 — arrange 점검 모드의 닫힌 읽기 목록(git 0) ↔ 조정자의 `git show` 지정

### 재현(글 대조) — 지금도 어긋난다

| 자리 | 문장(요지) | 정본 |
|---|---|---|
| `rel/dddjango/agents/acceptance-tester.md:64` | 이 모드는 «G1 전(**또는 Phase 2 재진입 전**)» 에도 부른다 | **R-3612** · `agent-acceptance-tester.ttl:759` · 블록 `s006/b1` |
| `…/acceptance-tester.md:66` | 입력 = 명세 경로 · sha256 · 인수 행 · 슬라이스 표기 · test anchor · 기록 경로 — **어느 판을 기준선으로 읽을지 칸이 없다** | **R-3613** · `:767` · `s006/b2` |
| `…/acceptance-tester.md:68` | 읽기 범위(닫힘) = 명세 · 시험 쪽 파일 · 제품 경로 실존 — 판 언급 없음(곧 작업 트리) · 시험 쪽 정의에 pytest 설정 절 없음 | **R-3614** · `:775`(rev 2 · 2026-10-21) · `s006/b3` |
| `…/acceptance-tester.md:70` | «읽기는 Read·Grep·Glob 가 있으면 그것으로 하고, 없으면 Bash 의 읽기 명령만 쓴다 — 허용 목록은 닫혀 있다: …» · «그 밖의 명령(`python`·`python3` · **`git`** · 해시 명령 · 시험 실행 · 설치 · 리다이렉트 쓰기 포함)은 쓰지 않는다» | **R-3615** · `:789`(rev 2 · 2026-11-09 · 2.33.0 F4-148 이 셸 꼴을 넓힐 때도 git 은 막힘) · `s006/b4` |
| `…/acceptance-tester.md:72` | 출처 `기준선` = «시험 쪽 파일이 그 꼴로 이미 쓰고 있거나 명세가 기준선의 꼴을 적었을 때» | **R-3616** · `:803` · `s006/b5` |
| `rel/dddjango/commands/dddjango.md:155` | 조정자 arrange 점검 — ⓘⓘⓘ «매 G1′ 재리뷰 다발에 합류» · 재사용 ㉢ «코드 기준선 SHA(pregate-report 의 `pre-gate 기준선` 행 …)» · ㉣ 시험 쪽 파일 해시 · ㉤ `approved-merges.txt` 해시 — 판정은 pre-gate 기준선에 묶이는데 역할에게 그 판을 읽을 길이 없다 | **R-3607**(`command-dddjango.ttl:4606`) · **R-3608**(`:4620`) · R-3609 · R-3723 — 블록 `s006/b12`(`:5745`) |
| `…/dddjango.md:149` | pre-gate 재발화 `--base <pre-gate 기준선 행 값>` + `--approved-merge-file` — Phase 2 뒤 «기준선» = pre-gate 기준선 ⊕ 승인 유입 | (pre-gate 판형 규범) |
| `…/dddjango.md:162` | 슬라이스 0 의 0T «테스트 쪽» 정의 — 경로 조각 · 파일 이름 · `test_*.py` 를 품은 `test`/`tests` 디렉터리 아래 파일 · **pytest 설정 절** | (Phase 2 3번 규범) |
| `rel/codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md:58` · `:60` · `:62` · `:64` · `:66` | 같은 뜻(`:64` «읽기는 셸의 읽기 명령만» · git 금지 같음) | — |
| `rel/codex-dddjango/skills/dddjango/SKILL.md:175` | 조정자 arrange 점검 같은 뜻 | — |

- git 금지는 모드가 생긴 e6aa40e9(2026-10-01 · C7)부터이고 2.19.1 · 2.39.0 모두 같다. 고쳐진 판 없음.
- 현장 꼴: Phase 2 설계 반송 뒤 G1′ 다발의 arrange 점검. 작업 트리에 이 실행의 S1 ~ S3 산출이 미커밋으로 섞여 있어, 조정자가 «승인 머지 판을 `git show <머지>:<경로>` 로 읽으라» 고 지정했고 역할은 «목록이 git 을 뺀다» 는 알림을 남긴 채 그 길로 판정했다(검색 후보는 작업 트리 `grep -l` · 인용은 머지 판 · 같은 기록에 pytest 설정 절도 머지 판에서 읽음 — 시험 쪽 정의 밖).

### 장난감
- v1 `toy-45`(`toy45.out`): 작업 트리는 이 실행 산출이 섞임 · 이 실행이 커밋한 뒤 승인 머지가 오면 머지 판(현장 조정자 꼴)에도 이 실행 산출이 섞임(`cash_payment` 1 · 기준선 판 0) · 읽기 셋은 `.git/index` · `.git` 최상위 목록을 바꾸지 않음(검토자가 `GIT_OPTIONAL_LOCKS` 없이 · 색인 stat 을 낡게 해 다시 잼 — 같음) · `git ls-tree` 는 글롭 불가 · `git archive` 는 안 맞는 글롭 하나로 통째 실패.
- 검토자 `review-c/toyR.sh` · `toyR5.sh`: R1(머지 둘 · 뒤 머지 충돌 해소) · R2(유입이 시험 파일을 지움) · R3(이 실행 커밋 + 유입이 함수를 지움) · R4(양쪽 고친 자동 머지) · R6(제품 경로 실존) · R7(`:(glob)` 첫 글롭에만).
- v2 `v2_inflow.sh`(v2 R-3607 식을 글 그대로 · 읽기만) on `review-c/toyR-r1 ~ r4` → `v2_inflow.out` — 넷 모두 pre-gate `approved_inflow`(검토자 `inflow_driver.py` 출력 `toyR.out`)와 같다:
  - r1: helpers 를 바꾼 마지막 참여 머지 = M2 · M2^2→M2 에도 있음 → 싣지 않음 → 역할은 `기준선 판` 에서 읽어 `"v0"`(pre-gate «충돌 해소 제외(기준선판 유지)» 와 같음 · v1 식은 `"main1"`).
  - r2: `유입 판 M: orders/tests/old_factories.py (지움)`(pre-gate «지움» 과 같음).
  - r3: `유입 판 M: orders/tests/helpers.py` · 그 판에 `make_legacy_order` 없음(pre-gate blob 과 같음).
  - r4: conftest 싣지 않음(pre-gate «충돌 해소 제외» 와 같음 — 아래 «남은 걱정» 한계 줄).
- v3 `v3_inflow.sh` → `v3_inflow.out`(v3 R-3607 글 그대로 · 읽기만): 검토자 좁은 재확인 R1 · R2 를 40자 목록과 9자 줄임 목록(9자 목록에는 `//` 주석 줄 · 메모 · 빈 줄도 섞음) 둘로 돌림 — 넷 모두 pre-gate 와 같다.
  - R1: 참여 머지 M1 · M2(오래된 것부터 · 9자 목록도 `rev-parse` 로 풀어 같은 둘) · helpers 를 바꾼 머지는 M1 · M2 이고 뒤 머지 M2 가 이김 · M2^2→M2 에도 있음 → 싣지 않음 → 역할은 기준선 판에서 `"v0"`(pre-gate «충돌 해소 제외(기준선판 유지)» 와 같음). 차례를 `--reverse` 없이 읽으면 M1 이 이겨 `"main1"` 이 된다(검토 N1 재현).
  - R2: 참여 머지 M(9자 목록도 같음) · `유입 판 M: orders/tests/old_factories.py (지움)` → 역할은 «기준선에 없음»(pre-gate «지움» 과 같음). 9자 줄을 글자 그대로 맞추면 참여 0 이 되어 역할이 기준선 판에서 지운 파일을 보게 된다(검토 N2 재현).
- v2 `v2_globs.sh` → `v2_globs.out`: 글롭마다 `:(glob)` 이면 `git diff --name-status` · `git grep` 이 뿌리 `conftest.py` · 뿌리 `test_*.py` · `pkg/*_test.py` · `fixtures/` · 뿌리 `pyproject.toml` 까지 잡고 제품(`OrderModel` · `Payment`)은 거른다 · 첫 글롭에만 붙이면 뿌리 `conftest.py` · `test_root.py` 를 조용히 놓친다(검토 R7 과 같음).

### 원인
R-3612 가 Phase 2 재진입 · G1′ 다발에도 이 모드를 부르게 했고(R-3607 ⓘⓘⓘ), 그때 판정의 «기준선» 은 조정자 규칙상 pre-gate 기준선 ⊕ 승인 유입(R-3608 ㉢ · ㉤ · pre-gate 재발화 `--base`)인데, 역할의 입력(R-3613) · 읽기 범위(R-3614)에는 판 칸이 없고 도구(R-3615)는 git 을 막는다. 작업 트리에는 이 실행의 슬라이스 산출이 섞여 있어 그대로 읽으면 이 실행이 만든 시험 재료를 `기준선` 으로 잘못 인용할 수 있다(거짓 «가능»). 그래서 현장 조정자가 즉석 길을 냈고 글과 어긋났다.

### 같은 꼴의 다른 자리(다른 읽기 전용 역할)
- Claude 판 리뷰어 넷(`design-review-api|db|ddd.md:5` · `discipline-reviewer.md:5`)은 도구가 `Read, Grep, Glob, Write` — Bash 가 없어 git 을 못 돈다. 글은 «git 쓰기 명령은 0»(`discipline-reviewer.md:45` · `design-review-api.md:41` · `-db.md:23` · `-ddd.md:22`)뿐이고, 조정자는 그들에게 git 읽기를 지정하지 않는다 — 판이 필요한 자료는 조정자가 재서 넘긴다(`NIT_DIFF_CHECK` 반영 diff · 이름 표시의 `git grep` 결과 — `dddjango.md:141` · 확인 모드 반영 diff). 어긋남 없음.
- Codex 판 리뷰어(`codex-…/dddjango-design-review-*/SKILL.md` · `dddjango-discipline-reviewer/SKILL.md:42`)는 «셸로는 그 밖의 쓰기·git 쓰기를 하지 않는다» — git 읽기가 막히지 않는다. 어긋남 없음.
- architect(Bash 없음) · coder(`coder.md:47` 이 `git show <기준선>:<경로>` 를 명시 허용) · acceptance-tester 기본 모드(Bash · 닫힌 목록 없음) — 어긋남 없음.
- 곧 «닫힌 읽기 목록 + git 0 + 판이 다른 기준선» 을 함께 가진 것은 arrange 모드 하나다.
- 곁 관찰(고치지 않음): G1′ 다발의 설계 리뷰어도 작업 트리(이 실행 산출 섞임)를 읽지만 그들의 판정은 `기준선` 이름표를 달지 않아 글 모순은 아니다.

### 고칠 방향
1. **작업 트리로 충분하다고 적는다** — 글 한 줄 · 비용 최소. 그러나 Phase 2 재진입 · G1′ 에서 틀린 `기준선` 인용(거짓 «가능»)을 허락하고 조정자의 재사용 ㉢ 과도 어긋난다. 현장 역할 · 조정자도 이 길을 버렸다. 버린다.
2. **git 읽기 세 꼴을 받은 판에만 허용하고, 조정자가 `기준선 판` · `유입 판` 을 싣는다 — 추천.**
   - 조정자(R-3607): Phase 2 진입 뒤 부르는 arrange 점검 입력에 `기준선 판 <pre-gate 기준선 행 SHA>` 와 `유입 판` 줄을 싣는다. 유입 판 식은 pre-gate `approved_inflow`(`rel/dddjango/scripts/design_pregate.py:1780-1808`)를 글로 옮긴 것 — 목록 SHA 를 `rev-parse` 로 푼 참여 머지를 오래된 것부터(`rev-list --reverse`) 보며 경로마다 그 경로를 바꾼(`M^1→M`) 머지 M 을 고르되 뒤 머지가 이기고, 그 경로가 `M^2→M` 에도 있으면(충돌 해소) 싣지 않고 기준선 판 그대로 · 아니면 `유입 판 <M>: <경로>` · 지움이면 `(지움)`. 그 밖의 판 · git 읽기를 역할에게 지정하지 않는다.
   - 역할(R-3613 · R-3614 · R-3615): 판이 오면 `기준선` 은 그 판(유입 경로는 유입 판 · `(지움)` · 그 판에 없는 경로는 기준선에 없음)에서만 본다 · 작업 트리 시험 쪽 파일은 후보 고르기에만 · 제품 경로 실존은 작업 트리에서 하되 `기준선` 근거가 아님 · 읽기는 Read·Grep·Glob 유무와 상관없이 Bash 의 git 세 꼴(따로 선 문장). 판이 없으면(Phase 1) 지금 그대로 작업 트리.
   - 시험 쪽 정의: 역할 R-3614 정의에 pytest 설정 절을 더해 조정자 0T 정의(`dddjango.md:162`)와 맞춘다 — 집합은 **글롭 = R-3614 ⊇ 0T** 다. 0T 는 경로 조각 아래 파일도 «`.py`» 로 한정해 `fixtures/` · `factories/` · `fake(s)/` 아래 `.py` 아닌 파일(JSON fixture 등)은 0T 밖이지만, R-3614 와 글롭은 파일 종류를 가리지 않는다(arrange 에는 넓은 쪽이 안전하다 — 유입 JSON fixture 를 놓치지 않는다). 0T 의 «`test_*.py` 를 품은 `test`/`tests` 디렉터리 아래 파일» 은 경로 조각 갈래에 이미 든다. git 글롭 목록은 역할 · 조정자 각자 자기 정의를 가리킨다(역할은 «위 읽기 범위의 시험 쪽», 조정자는 «0T 의 테스트 쪽 경로를 파일 종류와 상관없이»). pytest 설정 파일은 닫힌 목록이 아니라 «등» 이 붙은 예로 적고, 범위는 «pytest 가 설정을 읽는 절» 이라는 뜻으로 정한다.
   - 비용: 글 다섯(+ Codex 둘) · 도구 0 · 조정자 git 명령 머지당 둘(대개 0 ~ 1 머지).
   - 위험: `git show <판>:<제품 경로>` 로 블랙박스를 넘을 수 있다 — 지금 허용된 `cat` · Read 도 제품 파일을 글로만 막고 플러그인에 읽기 훅이 없어 집행 수준은 같다. 커밋 보기 꼴(`git show <SHA>` · `git diff` · `git log`)은 이름을 들어 막는다. `git grep` 은 시험 쪽 글롭으로 제품을 기계로 거른다.
   - 2.39.0 대비: 새로 푸는 것 = 받은 판의 시험 쪽 git 읽기 세 꼴 · 판을 실은 점검끼리의 재사용에서 ㉣ 생략. 새로 막는 것 = Phase 2 뒤 판이 왔을 때 작업 트리 시험 파일 · 제품 경로 실존을 `기준선` 근거로 쓰는 것(지금도 뜻으로는 틀린 일).
3. **조정자가 기준선 시험 쪽 사본(내용)을 만들어 넘긴다** — 역할 목록은 그대로(git 0)이고 사본에 제품 파일이 없어 블랙박스가 몸으로 지켜진다. 그러나 ⓐ 사본 자리: 산출물 폴더 안이면 실행 기록 커밋에 시험 트리 사본이 딸려 가기 쉽고 개정마다 쌓인다 · 작업 트리 밖이면 서브에이전트 Read 가 프로젝트 밖 경로 권한을 물을 수 있다 ⓑ `git archive` 는 안 맞는 글롭이 섞이면 통째로 실패한다 ⓒ 유입 겹치기 · 지우기를 손으로 하거나 pre-gate 에 «사본만 내기» 플래그를 새로 내야 한다(도구 변경 → 체크리스트 8 · EXPECTED · 픽스처). 다시 나면 연다.

### 새 문장 초안(추천 2) — graph-owned 절이라 ttl 의 블록 글을 고친다

- **R-3613**(`s006/b2` 끝에 덧붙임):
  > Phase 2 진입 뒤에 부르면 `기준선 판 <SHA>` 와 `유입 판 <머지 SHA>: <경로>` 줄(지운 경로는 끝에 `(지움)` · 유입 판 줄은 없을 수 있다)이 함께 온다.
- **R-3614**(`s006/b3` — 시험 쪽 정의에 한 갈래를 더하고 끝에 덧붙임):
  > **읽기 범위(닫힘)**: 명세 · 시험 쪽 파일(경로 조각 `test`·`tests`·`factories`·`fake`·`fakes`·`fixtures` 아래이거나 이름이 `test_*.py`·`*_test.py`·`conftest.py` 인 파일 · pytest 설정 절 — pytest 가 설정을 읽는 절(`pyproject.toml` 의 `[tool.pytest.ini_options]` · `pytest.ini` · `setup.cfg` 의 `[tool:pytest]` 등)만) · 제품 경로의 **실존만**이다. (… 지금 문장 그대로 …) 입력에 `기준선 판` 이 있으면 출처 `기준선` 은 그 판의 시험 쪽 파일로만 판단한다 — `유입 판` 에 적힌 경로는 그 머지 판의 파일로 보고(새로 들어온 파일 포함), `(지움)` 이 붙었거나 그 판에 없는 경로는 기준선에 없다. 작업 트리의 시험 쪽 파일은 찾을 후보를 고르는 데만 쓰고, 제품 경로 실존 확인은 판이 와도 작업 트리에서 하되 둘 다 `기준선` 근거로 쓰지 않는다. `기준선 판` 이 없으면 작업 트리가 기준선이다.
- **R-3615**(`s006/b4` — git 세 꼴을 «없으면» 목록 밖 따로 선 문장으로 넣고 금지 열거를 고침):
  > … 부속 기록이 있는 `<산출물 폴더>` 로만 가는 `cd`(제품 폴더로 들어가 상대 경로로 읽거나 검색하지 않는다). 입력에 `기준선 판` 이 있으면 Read·Grep·Glob 유무와 상관없이 그 판과 `유입 판` 의 시험 쪽 파일은 Bash 의 다음 세 꼴로만 읽는다 — `git show <SHA>:<시험 쪽 파일>` · `git ls-tree -r --name-only <SHA> -- <시험 쪽 폴더>`(폴더 글자 그대로) · `git grep -n -e <글자> <SHA> -- <시험 쪽 글롭>`(세 꼴 모두 위 읽기 전용 필터를 파이프로 걸 수 있다). `<SHA>` 에는 입력의 `기준선 판` · `유입 판` 값만, 경로 자리에는 시험 쪽만 넣는다. 시험 쪽 글롭은 위 읽기 범위의 시험 쪽을 글롭마다 `:(glob)` 을 붙여 적은 것이다 — `':(glob)**/test/**'` · `':(glob)**/tests/**'` · `':(glob)**/factories/**'` · `':(glob)**/fake/**'` · `':(glob)**/fakes/**'` · `':(glob)**/fixtures/**'` · `':(glob)**/test_*.py'` · `':(glob)**/*_test.py'` · `':(glob)**/conftest.py'` 와, pytest 설정 절이 든 파일의 글롭(`':(glob)pyproject.toml'` · `':(glob)pytest.ini'` · `':(glob)setup.cfg'` 등 — 그 파일은 그 절만 본다). 그 밖의 명령(`python`·`python3` · 위 세 꼴 밖의 `git`(`git show <SHA>` 커밋 보기 · `git diff` · `git log` 포함) · 해시 명령 · 시험 실행 · 설치 · 리다이렉트 쓰기 포함)은 쓰지 않는다. …
- **R-3607**(`command-dddjango.ttl` `s006/b12` — 입력 문장 뒤에 덧붙임):
  > Phase 2 진입 뒤(이번 실행 `pre-gate 기준선` 행을 쓴 뒤 — G1′ 재리뷰 다발 · Phase 2 재진입 앞)에 부르면 입력에 `기준선 판 <그 행의 SHA>` 와 `유입 판` 줄을 싣는다. 참여 머지는 `approved-merges.txt` 줄(빈 줄 · `//` 줄 빼고)의 첫 낱말을 `git rev-parse --verify "<SHA>^{commit}"` 로 푼 값 가운데 `git rev-list --reverse --first-parent "<기준선 판>..HEAD"` 에 있는 것이다(그 명령이 찍는 차례 — 오래된 것부터 · pre-gate «승인 유입» 행의 «머지» 칸과 같은 집합). 참여 머지를 그 차례로 보며 시험 쪽 경로마다 그 경로를 바꾼(`git diff --name-status --no-renames "<M>^1" "<M>" -- <시험 쪽 글롭>` 에 나온) 머지 M 을 고른다 — 한 경로를 여러 머지가 바꿨으면 뒤 머지가 이긴다. 그 경로가 `git diff --name-only --no-renames "<M>^2" "<M>" -- <시험 쪽 글롭>` 에도 나오면 싣지 않는다(기준선 판 그대로). 아니면 `유입 판 <M>: <경로>` 로 싣고, 그 머지에서 상태가 `D` 면 끝에 `(지움)` 을 붙인다. 시험 쪽 글롭은 Phase 2 3번 0T 의 테스트 쪽 경로를 파일 종류와 상관없이 글롭마다 `:(glob)` 을 붙여 적은 것이다 — `':(glob)**/test/**'` · `':(glob)**/tests/**'` · `':(glob)**/factories/**'` · `':(glob)**/fake/**'` · `':(glob)**/fakes/**'` · `':(glob)**/fixtures/**'` · `':(glob)**/test_*.py'` · `':(glob)**/*_test.py'` · `':(glob)**/conftest.py'` 와, pytest 설정 절이 든 파일의 글롭(`':(glob)pyproject.toml'` · `':(glob)pytest.ini'` · `':(glob)setup.cfg'` 등). 역할에게 그 밖의 판 · git 읽기를 지정하지 않는다.
- **R-3608**(같은 블록 · 재사용 ㉣ 에 괄호 하나):
  > ㉣ 그 기록이 출처 `기준선` 으로 인용한 시험 쪽 파일(기존 시험·fixture·conftest·도움 모듈) 전부의 해시(직전 점검과 이번 점검이 모두 `기준선 판` 을 실었으면 보지 않는다)

- 개정 꼴: 다섯 Norm 모두 새 Expression(rev n+1) · `revisionKind` amendment. prefLabel 후보(전문은 `c/v2_labels.py`):
  - R-3613 «… · 기존 test anchor · Phase 2 진입 뒤면 기준선 판·유입 판 · 부속 기록 경로·기록 토큰»
  - R-3614 «arrange 점검 읽기 범위 닫힘 — 명세·시험 쪽 파일(pytest 설정 절 포함)·제품 경로 실존만 · … · 기준선 판이 오면 기준선 출처는 그 판(유입 경로는 유입 판 · (지움)·그 판에 없음은 기준선에 없음)만 · 작업 트리 시험 파일·제품 경로 실존은 기준선 근거 아님 · …»
  - R-3615 «arrange 점검 도구 — Read·Grep·Glob 없으면 Bash 읽기 명령 닫힌 목록만(…) · 기준선 판이 오면 도구 유무와 상관없이 그 판·유입 판의 시험 쪽 파일은 git show·ls-tree·grep 세 꼴로만(받은 SHA · 시험 쪽 경로 · 글롭마다 :(glob)) · 쓰기는 기록 한 파일(Write·Edit) · python·python3·세 꼴 밖 git(커밋 보기·log 포함)·해시·시험·설치·리다이렉트 쓰기 0 · 계산 0(…)»
  - R-3607 «… · 배너 1행 · Phase 2 진입 뒤 부르면 입력에 기준선 판(pre-gate 기준선 행)·유입 판(경로마다 그 경로를 바꾼 마지막 참여 머지 · ^2 쪽과 다른 경로는 뺌 · 지운 경로는 (지움)) · 그 밖의 판·git 읽기 지정 0»
  - R-3608 «… · 기록이 기준선으로 인용한 시험 쪽 파일 해시(직전·이번 모두 기준선 판을 실었으면 보지 않음) · …»
- Codex 의미 미러(같은 뜻으로 손 고침):
  - `codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md:60`(입력) · `:62`(읽기 범위 — 위 R-3614 와 같은 글 · «코디네이터») · `:64`(도구 — Codex 는 «셸의 읽기 명령만» 이라 git 세 꼴을 닫힌 목록 안의 한 갈래 «입력이 준 `기준선 판` · `유입 판` 의 시험 쪽 파일에 `git show …` · `git ls-tree …` · `git grep …`(같은 제한 · 같은 글롭)» 으로 넣고, «입력에 `기준선 판` 이 있으면 그 판과 `유입 판` 의 시험 쪽 파일은 이 세 꼴로만 읽는다» 를 덧붙이며 금지 열거는 Claude 판과 같게).
  - `codex-dddjango/skills/dddjango/SKILL.md:175`(조정자 — R-3607 · R-3608 과 같은 글 · v3 의 목록 SHA 풀기 · `--reverse` 차례 · «뒤 머지가 이긴다» · «파일 종류와 상관없이» · pytest 설정 파일 «등» 예를 그대로). acceptance-tester `:62` · `:64` 도 pytest 설정 절 «등» 꼴을 Claude 판과 같게.
- 구현 때: 체크리스트 1(ttl 두 파일) → 2(`ontology_render.py --apply agent-acceptance-tester` · `command-dddjango`) → 3(LEDGER 재기준선 — acceptance-tester.md s006 · dddjango.md s006) → 4(ExpressionShape +5 · q4 골든 · `make rulepack`) → 6(Codex 둘). 5 · 7 · 8 해당 없음(arrange 기록을 읽는 도구 · 이 Norm 을 보는 픽스처 0 — 검토자 확인). 봉인 대상(agents · commands · Codex skills · ontology) → 봉인 두 번.
- G12(`v2_labels.out`): R-3607 · R-3608 · R-3614 · R-3615 후보 라벨 적중 0 · R-3613 은 «기존» 적중이나 이미 `DRIFT_REVIEWED` 등재(R-ID 같음) → 다섯 모두 통과 · `DRIFT_REVIEWED` · `scope-limit-norms.md` 손댈 것 없음. «git diff» 는 «diff» 가 적중하므로 라벨에 쓰지 않고 본문에만 둔다(R-3615 라벨은 «세 꼴 밖 git(커밋 보기·log 포함)»).
- 요청 가이드: 바뀔 것 없음(조정자 · 역할 사이 입력 · 도구 글만 바뀜).
- 판 합산: ExpressionShape 는 F4-29 +1 · F4-45 +5 = +6.

---

## 남은 걱정 · 한계
- F4-29 고침은 효과를 재기 어렵다(LLM 자기 스캔). 같은 꼴이 다시 나면 선택지 2(리뷰어 항목)로 간다.
- F4-45 줄인 안(«이 실행 커밋이 없을 때만 머지 판 하나 · 그 밖은 기준선 판만»)은 쓰지 않는다. 검토 R3 에서 이 실행 커밋 뒤 승인 머지가 시험 쪽 함수를 지운 꼴이면 줄인 안은 기준선 판에서 그 함수를 `기준선` 으로 인용해 거짓 «가능» 을 낸다(추천안 · 실제 HEAD 트리는 적중 0). «커밋하는 실행» 은 조정자 글의 정상 길(슬라이스 0 커밋 분리 · nit 길 «커밋하는 실행은 여기서 커밋»)이라 드문 꼴도 아니다 — 추천안 2(유입 판 목록)를 그대로 둔다.
- 한계(pre-gate 와 같은 사각 · 이번 판의 새 구멍 아님): 이 실행과 main 이 같은 시험 쪽 파일을 고쳐 자동 머지되면(충돌 없음) 그 경로는 `M^2→M` 에도 나와 «기준선 판 그대로» 다. main 이 그 파일에서 fixture 를 지웠어도 역할은 기준선 판에서 그 fixture 를 보고 `기준선` 으로 인용할 수 있다(검토 R4 · `v2_inflow.out` r4). 다시 나면 «양쪽 판 모두에 있는 재료만 `기준선`» 을 열 거리다.
- 현장 사본 대조(리허설 클론)는 두 항목 모두 검사기 판정이 바뀌지 않아 하지 않았다.

---

## v1 → v2 바뀐 것(검토 지적 번호별)
- **중1** R-3615: git 세 꼴을 «Read·Grep·Glob 없으면 … 허용 목록» 안에서 빼어 «입력에 `기준선 판` 이 있으면 Read·Grep·Glob 유무와 상관없이 … 세 꼴로만 읽는다» 따로 선 문장으로 옮김. 괄호의 설계 근거(«받은 판은 Read·Grep·Glob 로 읽을 수 없으니»)는 지움. 라벨도 같은 뜻으로 고치고 G12 다시 잼(적중 0). Codex 판은 닫힌 목록 안 한 갈래 + 같은 «세 꼴로만» 문장.
- **중2** R-3607 유입 판 식: v1 «머지마다 `M^1→M ∖ M^2→M` · 뒤 머지» → v2 pre-gate `approved_inflow` 와 같은 «경로마다 그 경로를 바꾼(`M^1→M`) 마지막 참여 머지 · 그 경로가 `M^2→M` 에도 있으면 싣지 않음(기준선 판 그대로)». 참여 머지 = `approved-merges.txt` ∩ `<기준선 판>..HEAD` 첫 부모 사슬(pre-gate «승인 유입» 행 «머지» 칸과 같은 집합). 검토 R1 꼴을 글로 따라감 — helpers 를 바꾼 마지막 머지 M2 · M2^2→M2 에 있음 → 싣지 않음 → 역할은 기준선 판에서 `"v0"` 을 읽는다(`v2_inflow.out` r1 · pre-gate 와 같음). v1 의 «장난감에서 확인» 주장은 지움.
- **중3** 유입이 지운 경로: R-3607 에 `(지움)`(`--name-status` 의 `D`) · R-3613 입력 꼴에 `(지움)` · R-3614 에 «`(지움)` 이 붙었거나 그 판에 없는 경로는 기준선에 없다» (`v2_inflow.out` r2).
- **중4** 글롭: R-3607 · R-3615 의 시험 쪽 글롭을 글롭마다 `:(glob)` 을 붙여 적음 · 역할 `git grep` 도 같은 글롭 · 조정자 명령은 `"<M>^1"` · `"<M>^2"` · `"<기준선 판>..HEAD"` 로 따옴표(`v2_globs.out`).
- **중5** R-3607 끝 «판이 더 필요하면 이 입력을 고친다» 를 지우고 «역할에게 그 밖의 판 · git 읽기를 지정하지 않는다» 로 끝냄.
- **사6** 남은 걱정의 «줄이면 안전 쪽» 문장을 검토 R3 결과(줄인 안 = 거짓 «가능» · 커밋하는 실행은 정상 길)로 고치고 추천안 2 유지.
- **사7** 제품 경로 실존: R-3614 에 «제품 경로 실존 확인은 판이 와도 작업 트리에서 하되 `기준선` 근거로 쓰지 않는다».
- **사8** pytest 설정 절: R-3614 시험 쪽 정의에 pytest 설정 절(파일 다섯 · 그 절만)을 더해 조정자 0T 정의와 맞춤 · 글롭 목록에도 설정 파일 다섯.
- **사9** R-3615 금지 열거: «위 셋 밖의 `git`» → «위 세 꼴 밖의 `git`(`git show <SHA>` 커밋 보기 · `git diff` · `git log` 포함)».
- **사10** R-3608 ㉣: v1 «범위 밖» → v2 짧은 괄호 «직전 점검과 이번 점검이 모두 `기준선 판` 을 실었으면 보지 않는다»(조정자가 무엇을 잴지 헷갈리지 않게 · Norm 하나 더 → ExpressionShape F4-45 +5).
- **사11** 시험 쪽 정의 출처: 역할 글롭은 «위 읽기 범위의 시험 쪽을 글롭마다 `:(glob)` 을 붙여 적은 것», 조정자 글롭은 «Phase 2 3번 0T 의 테스트 쪽 정의를 … 적은 것» 으로 각자 자기 정의 하나를 가리킴. 세 집합(R-3614 v2 · 0T · 글롭)이 같은지 맞춤 — 0T 의 «`test_*.py` 를 품은 `test`/`tests` 디렉터리 아래 파일» 은 경로 조각 갈래에 들고, 다른 것은 pytest 설정 절 하나라 사8 로 메움.
- **사12** R-1754: «대조 밖» 마디를 예 괄호 밖 본문 문장으로 올림 · 대상을 «명세가 낱낱이 적은 개수(목록 · 표 행 · file-plan 행 · 여러 절에 흩어진 언급)», 밖을 «명세 어디에도 낱낱이 적지 않은 수(플러그인 상수 · 코드에서 세기만 하고 명세에 적지 않은 수)» 로.
- **사13** R-1754 예에서 «맞는 쪽을 정해 두 자리를 함께 고친다» 를 뺌(해소는 R-1755 몫 · R-1755 는 고치지 않음).
- **사14** web 견주기 근거를 «web 은 바깥 재료 회계라 축이 다르다 · 이번 고침은 자기점검 거리 하나일 뿐 게이트 · 리뷰어 흐름 · 막힘을 더하지 않아 web 보다 엄격한 기준이 아니다 · web 은 보고가 없어 그대로» 로 고침.
- 그 밖: 런타임 글 초안에서 설계 근거 괄호를 걷음(R-3614 «이번 실행의 슬라이스 산출이 섞여 있어» · R-3615 «받은 판은 … 읽을 수 없으니»). 판 합산 ExpressionShape 를 +6 으로 고침.

---

## v2 → v3 바뀐 것(좁은 재확인 1 지적 번호별)
- **N1**(중요) R-3607 머지 차례: v2 «`git rev-list --first-parent "<기준선 판>..HEAD"` · 사슬 차례로 보며 … 마지막 머지» 는 그 명령이 최신 머지부터 찍어 «마지막» 을 덮으면 가장 오래된 머지가 이겼다(검토 R1 → `"main1"`). v3 은 명령을 `git rev-list --reverse --first-parent "<기준선 판>..HEAD"` 로 적고 «그 명령이 찍는 차례 — 오래된 것부터» · «한 경로를 여러 머지가 바꿨으면 뒤 머지가 이긴다» 를 붙였다. `v3_inflow.out` R1 — 역할은 기준선 판에서 `"v0"`(pre-gate 와 같음). 고칠 방향 2 요약 줄도 같은 뜻으로 고침.
- **N2**(중요) 목록 줄의 SHA: v3 R-3607 에 «`approved-merges.txt` 줄(빈 줄 · `//` 줄 빼고)의 첫 낱말을 `git rev-parse --verify "<SHA>^{commit}"` 로 푼 값» 을 더해 7 ~ 40자 줄임 SHA 를 받는 pre-gate 로더(`anchor_diff.load_approved_merges`)와 같게 했다. `v3_inflow.out` R1 · R2 — 9자 목록(주석 줄 · 메모 · 빈 줄 섞음)도 40자 목록과 같은 참여 머지 · 같은 유입 판 · pre-gate 와 같음.
- **N3**(사소) 시험 쪽 글롭: R-3607 «0T 의 테스트 쪽 정의를 … 적은 것» → «0T 의 테스트 쪽 경로를 파일 종류와 상관없이 글롭마다 `:(glob)` 을 붙여 적은 것». 고칠 방향 2 의 시험 쪽 정의 노트 «같은 집합» → «글롭 = R-3614 ⊇ 0T»(0T 는 경로 조각 아래도 `.py` 로 한정 · 넓은 쪽이 arrange 에 안전).
- **걱정**(pytest 설정 파일 다섯): R-3614 는 범위를 «pytest 가 설정을 읽는 절» 로 정하고 파일은 «`pyproject.toml` 의 `[tool.pytest.ini_options]` · `pytest.ini` · `setup.cfg` 의 `[tool:pytest]` 등» 의 예로 적음. R-3615 · R-3607 의 글롭 목록도 시험 쪽 글롭 아홉 «와, pytest 설정 절이 든 파일의 글롭(`':(glob)pyproject.toml'` · `':(glob)pytest.ini'` · `':(glob)setup.cfg'` 등)» 으로 닫힌 목록을 걷음.
- **Codex**: 조정자 `SKILL.md:175` 에 N1 · N2 · N3 · 걱정 고침을 같은 뜻으로 넣고, acceptance-tester `:62` · `:64` 도 pytest 설정 절 «등» 꼴을 Claude 판과 같게 한다고 미러 줄에 적음.
- 바뀌지 않은 것: G12 — v3 고침은 본문만이라 후보 라벨이 그대로고 다섯 모두 적중 0 · R-3613 은 등재(`v2_labels.out` 그대로). ExpressionShape +6(F4-29 +1 · F4-45 +5) 그대로. 덤: v2 확인 스크립트 `v2_globs.sh` 는 글롭 13개(`.pytest.ini` 빠짐)로 쟀다 — 검토자가 14개로 다시 재 결론이 같았고, v3 은 설정 파일을 «등» 예로 바꿔 개수에 기대지 않는다.


---

# 3판 단위 b v3 — 검사기 ⓓ 후보 소음 셋(F4-26 · F4-32 · F4-95): 재현 · 원인 · 고칠 방향 초안

- 바탕: 배포판 dddjango 2.39.0(태그 `dddjango--v2.39.0` = f36fa9f9) 사본 `pan3-1116/rel/` 의 검사기로 잼. main = b29635ca(배포 뒤 문서만).
- 장부: 발췌 `pan3-1116/LEDGER-EXCERPT.md`(읽은 때 11-16 · 마지막 F4-180). v1 잰 때 11-16 03시대 · v2 잰 때 11-16 13시대 · v3 잰 때 11-16 14시대(`date`).
- 입력: 설계 독립 검토 `pan3-1116/review-b/REVIEW.md`(차단 1 · 중요 2 · 사소 5) · 좁은 재확인 1 `review-b/RECHECK-1.md`(차단 0 · 중요 2 · 사소 6) ·
  처분 `pan3-1116/op-rev/DISPOSITION.md` «review-b» · «F4-95 사용자 결정» · «review-b 좁은 재확인 1» 절. v3 잰 때 11-16 14시대.
- 작업 폴더 `pan3-1116/b/`
  - 장난감(홀로 선 git 저장소) `toys/t257` · `toys/t191` · `toys/t485`. 검토자 장난감 `review-b/toys2/r257` · `r257b` · `r191` · `r485` · `r485c` · `r485e` · `r485f` 도
    절대 경로로 돌렸다.
  - 시제품 v3 `proto/`(바뀐 검사기 세 파일만 · diff `proto-257.diff` · `proto-485.diff` · `proto-191.diff`) · v2 는 `proto-v2/` · v1 은 `proto-v1/`.
  - 더할 시험 초안 `proposed_smoke.py`(v3) · 출력 `out3/`(v3) · `out2/`(v2) · `out/`(v1) · 매트릭스 결과 `run/`(`*-v3.txt`).
- 셋 다 ⓓ(exit 불산입) 후보다. 소음의 비용은 G2 «ⓓ 신규(N′∖L′)» 를 받는 규율 감사(discipline-reviewer)의 기각 수고다. 리팩토링 모드 BC 점검은 대상 BC 의 기존 코드
  전체를 보므로 전부가 감사 입력이 된다. 고침의 위험은 «진짜 물음을 후보에서 빼는 것(새 놓침)» 이다.

## v1 → v2 바뀐 것
| 자리 | v1 | v2 | 까닭 |
|---|---|---|---|
| F4-95 판정 | 원시 값 반환 + `INTENT_DENY` 머리 아님 → 묻지 않음 | 원시 값 **또는 저장소 안 Enum**(과 그 묶음 · 선택) 반환 + 첫 낱말이 `INTENT_DENY` 도 **모호 동사 머리**(invoke · apply · call · perform · trigger · dispatch · request · exec · operate · manage)도 아님 → 묻지 않음 | 사용자 결정 11-16 13:30 «확정» · 검토 차1 |
| F4-95 애너테이션 읽기 | 옛 `_ann_names`(모듈 이름과 끝 이름을 함께 모음) · `PLAIN_RETURN_NAMES` 에 `datetime` · `timedelta` | 반환 전용 `_return_names`(점 붙은 이름은 끝 이름 · 문자열 애너테이션 · `X \| None` · `Optional` · `Literal` 일관) · 원시 값 = 사용자 목록 그대로(timedelta 뺌) · Iterator 는 묶음이 아님 | 검토 중3 · 사용자 목록 |
| F4-95 규칙 글 | 글은 고치지 않음(E 안은 권하지 않음) | 규칙 1 ~ 4 를 그래프 규범에 넣음 — houserules §3 새 칸 · 감수 물음 R-1123 개정 · cleancode §2.6 다시 말함 · 후보 물음 글 맞춤(아래 §3.5) | 사용자 결정 «규칙 1 ~ 4 는 그래프 규범에» |
| F4-26 return 건너뛰기 | 앞 문장이 확인 호출(부분 글)이면 끝 | 앞 문장이 `_` 낱말로 확인 호출 + **self 에 쓴 뒤 확인 없이 빠져나가는 다른 return 없음**(길 읽기) + return 식에 **self 속성을 그대로 묶은 지역 이름**도 없음 | 검토 중2 · 사4 · 검토자 장난감 H4 |
| F4-32 | 머리 넷 · «#485 와 같은 넷» 주석 | 머리 넷 그대로 · 주석 «동사로만 읽히는 묻는 머리 넷(독립 상수)» · 한계 글에 «바꾸는 동사 머리 + 명사 접미» · 장부 처분 초안 | 검토 사5 · 사6 |
| 시험 초안 | 7 시험 · 변이 7 · 놓침을 «passes_accepted_limit» 로 못 박음 | 8 시험 · 변이 16 · 놓침 시험은 «사용자 결정이 받아들인 놓침» 으로 이름 · docstring 에 결정 날짜 | 검토 사8 |
| 현장 #485 | 69 → 38 | 69 → 37(Enum 묶음을 돌려주는 동사 머리 이름 하나 더 빠짐 · 되살아난 줄 0) | Enum 신호 |

## v2 → v3 바뀐 것(좁은 재확인 1 · 처분 «review-b 좁은 재확인 1»)
| 자리 | v2 | v3 | 까닭 |
|---|---|---|---|
| F4-95 Enum 기저 | 기저 끝 이름이 `Enum` · `Flag` · `Choices` … 이면 Enum | 그 이름(또는 모듈 이름)을 `enum` · `django` 에서 들여왔을 때만 Enum 기저 · 아니면 저장소 안 풀이(네 겹)로 | N2 — 업무 dataclass `Flag` · `Choices` 기저 반환이 다시 묻는다(r485e 3 → 6) |
| F4-95 감싸개 | list · tuple · set · frozenset · dict · Sequence · Collection · Iterable · Mapping · Optional · Union | list · tuple · set · frozenset · Sequence · Collection · `List` · `Tuple` · `Set` · `FrozenSet` · Optional · Union · `Annotated` 첫 인자 · dict · Mapping · Iterable 는 묻는다 | N5 운영자 해석 «그 목록 · Optional» |
| F4-95 후보 물음 글 | 권함(넣지 않음) | 시제품에 넣음 — «이 이름이 의도를 말하나 — 조회면 명사구도 되고, 그 밖은 명령이라 동사구다» | 볼 것 6 · N7(지문 방향 바로잡음) |
| F4-95 규칙 글 | cleancode b2 = restates + statesNorm R-N1 · houserules «명사구도 된다» · 계수표에 Block 없음 | b2 = kind-norm + restates 만 · «명사구 · 묻는 꼴도 된다» · BlockShape 3018 → 3020 | N1 · N8 · N3 |
| 한계 글 | 묶은 이름 · 대소문자 글이 실제와 다름 | #257 묶은 이름 한계(첨자 · `or` · 두 번 건넌 별칭 · 원소) · 대소문자 갈림은 `is_file()` · 돌 수 없는 import 뿐 | N4 · N6 |
| 시험 초안 | 8 시험 · 변이 16 | 8 시험(`List` · `Annotated` 안 물음 · `dict` · `Iterable` · `Flag` 기저 물음 · 새 `Q485`) · 변이 21(들여온 곳 확인 뺌 · Iterator · dict 묶음 · typing 대문자 · Annotated · 물음 글) | N2 · N5 · 볼 것 6 |
| 현장 #485 | 69 → 37 | 69 → 38(`Mapping[str, <Enum>]` 반환 목록 밖 동사 하나가 다시 묻는다 · 새로 묻는 이름 0) | N5 |
| EXPECTED | 바뀔 것 없음 | findings_count port-adapter 지문 1 · smoke 물음 상수 1(물음 글) | 볼 것 6 |
| 검사기 #257 · #191 | — | v2 와 byte 같음 | — |

## 요약

| 항목 | 2.39.0 재현 | 원인(배포판 사본 줄) | 추천(v3) | 규칙 목적 | 현장 사본 ⓓ |
|---|---|---|---|---|---|
| F4-26 #257 | 재현됨(그대로) | `check-domain-model.py:497-507` — 끝 문장 = `m.body[-1]` 하나 · `return` 은 확인이 아님 · `self._version += 1`(AugAssign)은 상태 변경 셈 밖 | 끝이 «확인 호출 + 값만 돌려주는 return» 이고 확인 없이 빠져나가는 다른 길이 없으면 확인으로 끝난 것 | 닿지 않음(질문 생략) | 120 → 74 |
| F4-32 #485 현장 `draw_…` 이름 | 이미 고쳐짐 — 2.27.3(ffbacbd5 · 10-26 · F4-114 동사 목록 넓힘) | — | — | — | — |
| F4-32 #191 `get_<x>_detail` | 재현됨(그대로) | `check-usecase-dto-placement.py:508-509` — 명사 접미를 머리와 무관하게 물음 | 묻는 동사 머리 넷(get · find · list · count)으로 시작하면 명사 접미를 묻지 않음 | 닿지 않음(질문 생략) | 4 → 0 |
| F4-95 #485 `replace` · 현장 이름 둘 | 이미 고쳐짐 — 2.27.3(같은 커밋) | — | — | — | — |
| F4-95 #485 `url` | 재현됨(그대로) | `check-port-adapter-pairing.py:297-301` — «묻는 꼴» 을 접두로만 가늠 | 사용자 결정대로 — 원시 값 · Enum(`enum` · `django` 기저)과 그 목록 · 선택 반환 + 모호 동사 머리 아님이면 묻지 않음 · 규칙 1 ~ 4 를 그래프에 · 물음 글 맞춤 | **사용자 결정(11-16 13:30 «확정»)** | 69 → 38 |

시제품 v3 셋 모두 대조군 그대로 · 매트릭스 차이는 물음 글이 낳는 둘뿐(아래 §5).

---

## 1. F4-26 — ⓓ#257 «끝에 불변식 확인이 없다» 가 확인 뒤 `return True` 에 뜬다

### 재현(장난감 `b/toys/t257` · 루트 `Order`)
- 배포판 `check-domain-model.py toys/t257` → exit 0 · ⓓ#257 8 줄(`out2/t257-rel.txt`).
- 신고 꼴 `cancel_order`(앞 조건 블록 `if ends_note: self._note = None` · 끝 `self._version += 1` · `self._assert_invariants()` · `return True`) → 후보 뜸.
- 같은 몸에서 조건 블록만 뺀 `cancel_order_plain` → 조용함. 신고가 본 «블록을 더하자 새로 뜸» 의 실제 뜻은 아래 원인 ②다.
- 같은 결의 소음: 확인 뒤 `return self._version`(`mark_closed`) · 확인 뒤 결과 값 객체 `return FinishResult(closed=True, version=1)`(`finish`).
- 대조(남아야 하는 물음): 확인 없이 `return True`(`drop_note`) · 확인 뒤 다시 대입(`reopen`) · 확인 뒤 `return self._fold_lines()`(`close_and_fold`) ·
  끝 `if` 가 필드를 바꾸고 return(`clear_note`) · 확인 뒤 결과 값에 `self` 를 넘김(`finish_with_self`).
- 검토자 장난감 `review-b/toys2/r257`(배포판 6 줄): 앞 갈래가 바꾸고 확인 없이 빠져나감(`close_or_park`) · 확인 낱말이 부분 글로만 든 바꾸는 호출(`close_and_invalidate` ·
  `close_with_checkpoint`) · self 속성을 묶은 이름을 이름 호출로 비움(`close_and_drain`) · 대조 `close_count`(`len(self._lines)`) · `close_result`(값에 self 필드).

### 원인
- `rel/dddjango/scripts/check-domain-model.py:488-507` `_check_root_class` 의 #257 후보.
  - ① 끝 문장 판정이 `last = m.body[-1]` 하나다(498행). 끝이 `return` 이면 그 앞이 확인 호출이어도 «확인 없음».
  - ② «상태를 바꾸는 메서드» 는 `self.<x> = …` 대입(Assign · AnnAssign)이 있을 때만이다(493-496행). `self._version += 1`(AugAssign)이나 도움 메서드로 바꾸는
    몸은 셈 밖이다. 그래서 if 안 `self._note = None` 이 생기자 비로소 «상태 변경» 으로 세어져 ① 에 걸렸다. «끝 위치를 잘못 잡는다» 는 현장 추정은 반만 맞다.
  - (사각) ③ 끝이 `if` 면 무엇을 하든 확인으로 친다(499행) · ④ 확인 낱말은 부분 글로 맞춘다(500-503행 — `_invalidate_cache` 의 valid).
- 처음 꼴 그대로다(`git log -S ends_with_check` = 7f695bbc 트리 재건 하나).

### 같은 꼴의 다른 자리
- 같은 «끝에 불변식 확인» 판정은 이 한 곳뿐이다. 다른 `body[-1]` 쓰임(`check-api-error-controller-contract.py:3502` · `:4217` · `check-domain-model.py:1347` ·
  `:1594` · `:1611` · `:1621`)은 목적이 다른 구조 판정이라 영향 없다.
- Codex 미러 `codex-dddjango/skills/dddjango/scripts/check-domain-model.py` byte 같음(같이 고친다). dddjango-web 에는 같은 규칙이 없다.
- 규칙 글: 트리 개정 명세 #257 행 · predicates 144행 · 감사 물음 R-1102 — 글은 고칠 것 없음(predicates 144행만 코드에 맞춤 · §6).
- 영향 실행: 기능 · 수정 · 리팩토링 모두(G2 registry_gate ⓓ 신규 → 규율 감사 · 리팩토링 BC 점검은 전체).

### 고칠 방향(v2 · v3 같음)
끝 판정은 옛 그대로 두고(끝이 확인 호출 · `raise` · `if` 면 확인), **끝이 return 일 때만** 다음 셋을 모두 만족하면 확인으로 끝난 것으로 본다.
1. return 이 값만 돌려준다 — 값 없음 · 호출 없는 식(상수 · 이름 · 속성 읽기 · 그 묶음) · 맨 이름 호출만 있고 식에 `self` 도 self 속성을 그대로 묶은 지역 이름
   (`lines = self._lines` · `for line in self._lines`)도 없음(`Result(...)`). self 메서드를 부른 결과(`snapshot = self._snapshot()`)는 새 값이라 묶은 이름으로 치지 않는다.
2. 바로 앞 문장이 확인 호출이다 — 메서드 이름을 `_` 로 가른 낱말에 assert · check · ensure · valid · validate · verify 가 있다(`_invalidate_cache` · `_checkpoint` 는 아님).
   건너뛴 return 앞의 `if` 는 확인으로 치지 않는다.
3. 길 읽기 — 끝 return 말고, self 에 쓴(대입 · 주석 대입 · 더하기 대입) 뒤 확인 호출 없이 닿는 return 이 없다. `if` · `match` · 고리 · `with` · `try` 갈래를 문장 차례대로
   따라간다(검토자 변형 proto2 와 같은 뜻 · `match` · `TryStar` 를 더함).

| 안 | 2.39.0 대비 푸는 것 | 새 놓침 | 비용 |
|---|---|---|---|
| **v2 · v3(추천)** | 확인 호출 + 값만 return 이고 다른 길도 확인을 거친 꼴만 | 0 — 장난감 t257 · r257 대조 열하나 모두 그대로 · 현장 사라진 46 줄 모두 `_assert_invariants()` 바로 뒤 return | 검사기 +132 줄(빈 줄 · docstring 포함 · 길 읽기 ~50 · 묶은 이름 ~30) |
| v1 | 위 + 앞 갈래 빠져나감 · 부분 글 확인 · self 묶은 이름 비움 | r257 넷(`close_or_park` · `close_and_invalidate` · `close_with_checkpoint` · `close_and_drain`) | ~20줄 |
| 2(옛 `if` 인정 유지) | v1 + 끝 `if` 뒤 return | 현장 4 줄(끝 `if` 가 필드를 바꾸고 `return True`) | 작음 |
| 3(글만) | 0 | 0 | 소음 그대로 |

- 규칙 목적 판정: **질문 생략 · 설계 처리** — #257 규범이 «끝에서 확인» 을 요구하고, 값만 돌려주는 return 은 상태를 바꾸지 않으므로 확인이 끝에 있는 것이다(이의 시 뒤집음).
- 받아들인 한계:
  - 도움 메서드 안의 바뀜(`self._fold()` · `self._checkpoint()` 처럼 부르기만 하는 줄)은 길 읽기에서 «self 에 씀» 으로 세지 않는다(옛 «상태 변경» 정의와 같은 한계).
  - 묶은 이름은 self 속성을 **그대로** 묶은 꼴(`x = self._a` · `x = self._a.b` · `for x in self._a`)만 본다(N4). 첨자(`x = self._data["k"]`) · `or`(`x = self._a or []`) ·
    두 번 건넌 별칭(`a = self._a; x = a`) · 원소(`x = self._a[0]`) · self 메서드가 돌려준 내부 객체는 못 본다 — 그런 이름을 이름 호출로 비우는 꼴은 묻지 않는다
    (검토자 장난감 r257b 넷 · 배포판은 물음 · 현장 0).
  - 반대로 바꿀 수 없는 값을 그대로 묶은 이름(`old = self._note` 뒤 `return Cleared(old)`)도 묻는다(배포판도 묻던 소음 · 새 소음 아님).
- 덤(신고 밖 · 새로 묻기 · 작업 리스트로): ② AugAssign 을 상태 변경으로 셈(현장 +1) · ③ 끝 `if` 는 안에 `raise` 가 있을 때만 확인(현장 +3) · ④ 끝 판정의 확인 낱말도 `_` 낱말 경계로.

### 시제품 v3(= v2) · 현장 사본
- `b/proto/check-domain-model.py` — `_CHECK_TOKENS` · `_called_method` · `_is_check_word_call` · `_self_store` · `_writes_self` · `_unchecked_exit` · `_self_attr_chain` ·
  `_self_bound_names` · `_returns_value_only` + 끝 판정 4줄 · 머리 docstring 한 줄.
- 장난감 t257: 8 → 5(v1 과 같음 · `cancel_order` · `mark_closed` · `finish` 녹색 · 대조 다섯 그대로 · exit 0 = 0).
- 검토자 장난감 r257: 배포판 6 · v1 2 · proto2 3 · **v3 6**(H 넷 모두 다시 물음 · 대조 둘 그대로). r257b: 배포판 7 · **v3 3** — 바로 묶은 `close_and_drain` 은 묻고, 첨자 · `or` ·
  두 번 건넌 · 원소 별칭 넷은 묻지 않음(한계 · 위), 바꿀 수 없는 값을 묶은 소음 둘(`clear_note` · `close_count`)은 묻는다(배포판도 물음).
- 현장 사본(v3 · 14시대 다시 잼): #257 120 → 74 · 더해진 줄 0 · #257 밖 줄 byte 같음 · exit 2 = 2.
- 현장 사본: #257 120 → 74(-46 · 더해진 줄 0 · #257 밖 줄 byte 같음 · exit 2 = 2). 사라진 46 = 한 루트 파일의 `_assert_invariants()` 바로 뒤 return(값 43 · 결과 값 객체 3).
  묶은 이름 규칙을 «self 가 든 식이면 모두» 로 두니 self 메서드 호출 결과를 돌려주는 2 줄이 되살아나(76) «self 속성을 그대로 묶은 이름» 으로 좁혔다.

---

## 2. F4-32 — #485 현장 `draw_…` 이름(고쳐짐) · ⓓ#191 `get_<x>_detail`(그대로)

### #485 `draw` — 이미 고쳐짐
- 2.27.3 커밋 ffbacbd5(10-26 · «ⓓ#485 아는 동사 목록 넓힘 — F4-113 · F4-114» · 태그 `dddjango--v2.27.3` 부터)가 `draw` 를 포함한 39 낱말을 `VERB_HINTS` 에 더했다.
- 확인: 같은 장난감을 2.27.2 검사기(`git archive dddjango--v2.27.2`)로 돌리면 현장 `draw_…` 이름 가 후보 · 2.39.0 에서는 없음.

### #191 재현 · 원인
- 장난감 `b/toys/t191` → 배포판 exit 0 · ⓓ#191 15 줄. `get_book_detail` · `list_book_status` · `find_loan_info` · `count_loan_list` 가 «명사 접미로 끝난다 — 동사로 짓는다» 후보.
- `rel/dddjango/scripts/check-usecase-dto-placement.py:503-509` — 명사 접미(`_list` · `_info` · `_detail` · `_status`) 후보가 첫 낱말을 보지 않는다. #191 규범
  («`<use_case>/` 폴더 이름은 동사로 짓는다») 에서 `get_book_detail` 은 동사구다. 처음 꼴 그대로(7f695bbc).
- 글 어긋남: predicates 129행은 «자동 통과: 루트 공개 메서드 첫 토큰» 을 적는데 검사기는 하지 않는다(503-504행 주석 «수집 비용 대비 이득이 낮아»).
- 같은 꼴: #485 `ASKING_PREFIX`(`check-port-adapter-pairing.py:102` — 아홉) 는 목적이 달라 공유하지 않는다. Codex 미러 byte 같음. web 없음. 감사 물음 R-1096 고칠 것 없음.

### 고칠 방향
| 안 | 무엇 | 새 놓침 | 비용 |
|---|---|---|---|
| **1(추천)** | 첫 낱말이 **동사로만 읽히는 묻는 머리 넷**(get · find · list · count — 독립 상수 `QUERY_VERB_HEADS`)이면 명사 접미를 묻지 않음 | 사실상 0(`list_status` 처럼 `list` 가 명사 머리인 이름만) | 3줄 + 주석 |
| 2 | 넓은 동사 사전(93 낱말) | 동사 겸용 명사 머리의 명사구 여섯(`record_detail` · `refund_status` · `review_list` · `schedule_info` · `load_status` · `read_status`) | 사전 공유 |
| 3 | 루트 공개 메서드 첫 토큰 자동 통과 구현 | 0 | `get` 은 루트 메서드가 아니라 신고를 못 고침 |

- **받아들인 한계(사5)**: 동사 머리라도 넷 밖이면 명사 접미를 계속 묻는다 — 바꾸는 동사 머리(`update_book_status` · `change_loan_status` · `set_book_info` · `edit_book_detail` ·
  `cancel_loan_list`) · 그 밖 동사 머리(`search_book_list` · `fetch_loan_status` · `show_book_detail`) · 명사로도 읽히는 머리(`read_status` · `load_status`). 신고 꼴(`get_` · `list_`)만
  고치고 같은 결은 남긴다(현장 0). 넓히려면 명사 겸용이 드문 동사만 장난감으로 재서 더한다.
- 규칙 목적 판정: **질문 생략 · 설계 처리**(규범이 «동사로 짓는다» 이고 동사 머리 이름은 규범을 지킨다 · 이의 시 뒤집음).
- 시제품: `b/proto/check-usecase-dto-placement.py` — 상수 + 509행 조건 하나 · 상수 주석 «동사로만 읽히는 묻는 머리 넷 · 바꾸는 동사 머리와 명사로도 읽히는 머리는 그대로 묻는다» ·
  머리 docstring #191 줄 · 503행 주석.
- 장난감 t191 15 → 11(대조 열하나 그대로) · 검토자 r191 9 → 7(`get_status` · `list_status` 빠짐 · 바꾸는 동사 머리 다섯 · `search_book_list` · `current_book_status` 그대로) ·
  현장 4 → 0(ⓓ 머리 줄 수만 178 → 174).

---

## 3. F4-95 — #485 `url`(그대로) · 사용자 결정으로 정한 규칙과 검사기

### 재현 · 원인
- 2.27.2: `replace` · 현장 이름 셋 · `url` 모두 후보. 2.39.0: 앞의 넷은 지나가고(2.27.3 ffbacbd5) `url` 만 남는다.
- `rel/dddjango/scripts/check-port-adapter-pairing.py:297-301` — 첫 토큰이 아는 동사 목록(`VERB_HINTS` 71)에 없고 묻는 꼴 접두(`ASKING_PREFIX` 102행)도 아니면 후보.
  «묻는 꼴» 을 접두로만 가늠하므로 명사 · 파생 질의 이름(`url`)은 늘 후보다.
- 런타임 글에 «조회는 명사 가능» 이 없다: D39 ③(08-08 · «물으면 묻는 꼴 `current_status()`») 과 트리 개정 명세 #485 행에만 있고, 감사 물음 R-1123 은 «무엇을 시키는지»
  만 묻고 cleancode §2.6(R-1380)은 «메서드: 동사» 만 적는다.

### 사용자 결정(11-16 13:30 «확정» · 처분 «F4-95 사용자 결정» 절)
- 규칙(사람 판정 · 설계자 · 감수자): ① 조회(부른 뒤 아무것도 바뀌지 않고 값만 돌려줌)는 명사구도 된다. ② 조회가 아니면 모두 명령이고 동사구로 짓는다 — 조회인지 확신이 없으면
  명령 · 값을 돌려줘도 바뀜이 있으면 명령. ③ 로그 · 캐시처럼 결과에 영향 없는 것은 바뀜이 아니다. ④ notify · handle · execute · invoke 처럼 무엇을 시키는지 안 말하는 이름은 위반.
  판단은 이름 짓는 사람이 의도로 한다(구현 추적 없음).
- 검사기(ⓓ#485 물음 · exit 그대로): 아는 동사 · 묻는 꼴이면 묻지 않음 · 반환이 원시 값 또는 Enum 이고 첫 낱말이 모호 동사가 아니면 묻지 않음 · 그 밖은 묻는다.
  받아들인 놓침 = 원시 값 · Enum 을 돌려주는 명사 이름 명령(감수 몫).

### 3.1 검사기 v3(`b/proto/check-port-adapter-pairing.py` · +156 줄 · 대부분 반환 애너테이션 읽기와 Enum 풀이)
- 후보 조건: 확정(이름이 `INTENT_DENY` 여섯이거나 `_command` · `_query` 접미)이 아니고, 묻는 꼴 접두가 아니고, 첫 토큰이 `VERB_HINTS` 밖이며, 아래 «묻지 않음» 이 아니면 후보.
- 묻지 않음 = 첫 토큰이 있고(`_` 로 시작하지 않음) · `INTENT_DENY` 도 `VAGUE_HEADS`(invoke · apply · call · perform · trigger · dispatch · request · exec · operate · manage)도 아니고 ·
  반환 애너테이션이 «원시 값 · Enum 과 그 목록 · 선택만» 이다.
- 반환 애너테이션 읽기(`_return_names` — 옛 `_ann_names` 는 375 · 416행 다른 판정이 쓰므로 건드리지 않는다):
  - 점 붙은 이름은 끝 이름(`datetime.date` = `date` · `uuid.UUID` = `UUID` · `typing.Optional` = `Optional`) · 문자열 애너테이션은 풀어 읽음 · `None` · `...` 은 뺌 ·
    `X | Y` · 첨자를 따라감 · `Literal[...]` 은 글 · 수 값 · `Annotated[X, …]` 은 X 로 읽음.
  - 값 이름 = 원시 값(`str` · `int` · `float` · `bool` · `bytes` · `date` · `datetime` · `time` · `Decimal` · `UUID` — 사용자 목록) 또는 Enum.
  - 감싸개(«그 목록 · Optional» — 운영자 해석 · 처분 N5) = `list` · `tuple` · `set` · `frozenset` · `Sequence` · `Collection` · typing 대문자 `List` · `Tuple` · `Set` · `FrozenSet` ·
    `Optional` · `Union`(과 `X | None`). 값 이름이 하나도 없으면(`-> list` · `-> None` · `tuple[()]`) 묻는다.
  - 그 밖 이름이 하나라도 있으면 묻는다 — 사전 · 흐름(`dict` · `Dict` · `Mapping` · `Iterable` · `Iterator` · `Generator`) · `Any` · `object` · `type` · `NoReturn` · `Path` · `timedelta` ·
    객체 · 못 푼 이름. 읽을 수 없는 꼴(호출 · 애너테이션 없음)도 묻는다.
- Enum 판정(`_enum_class` · 정적으로만 · 못 풀면 묻는 쪽):
  - 반환 이름을 저장소 안 클래스로 푼다 — 같은 파일의 클래스 · `from <저장소 모듈> import X [as Y]`(절대 · 상대 · 꾸러미 `__init__.py` 다시 내보내기) ·
    `from <꾸러미> import <모듈>` 뒤 `<모듈>.X` · `import <모듈> [as m]` 뒤 `m.X`. `TYPE_CHECKING` 안 import 도 본다.
  - **그 클래스의 기저가 Enum 기저인가(N2)**: 기저 끝 이름이 `Enum` · `StrEnum` · `IntEnum` · `Flag` · `IntFlag` · `ReprEnum` · `TextChoices` · `IntegerChoices` · `Choices` 이고
    그 이름(또는 `models.TextChoices` 의 `models` 같은 모듈 이름)을 **`enum` 이나 `django` 에서 들여왔을 때만** Enum 기저다(`_imported_from`). 아니면 기저를 다시 저장소 안 클래스로
    풀어 Enum 기저까지 닿는지 본다(네 겹까지). 그래서 저장소의 업무 클래스 `Flag` · `Choices` 를 기저로 둔 dataclass 는 Enum 이 아니다.
  - 못 푸는 것(묻는다): 저장소 밖 모듈(가상환경 · 서드파티) · 다섯 겹 이상 · 여러 겹 점 경로(`import a.b.c` 뒤 `a.b.c.X`) · 함수 안 import · 별칭 대입(`Status = OrderStatus`) · `import *` ·
    `enum` · `django` 밖 Enum 꾸러미(예: 따로 설치한 choices 꾸러미)를 기저로 둔 클래스.
  - 받아들인 한계:
    - 값 이름(`UUID` · `Decimal` · `date` …)은 끝 이름만 본다 — 저장소에 같은 이름의 다른 클래스가 있으면 속는다(드묾).
    - 대소문자(N6): 갈림은 모듈 파일을 찾는 `is_file()` 하나다. import 글자 크기가 파일과 다르면(`…value_object.Order_Status` ↔ `order_status.py`) 대소문자를 가리지 않는
      macOS 는 Enum 으로 풀어 묻지 않고, Linux 는 못 풀어 묻는다(검토자 장난감 r485f · macOS 0 줄). 그런 import 는 파이썬이 실행하지 못하므로(`ModuleNotFoundError`) 돌 수 있는 코드에서는
      갈림이 없다.
- 장난감 결과(배포판 → v2 → v3):
  - t485(포트 다섯) 33 → 16 → **16** · exit 2 = 2 · 확정 `notify` 그대로. 묻지 않음 = `url -> str` · `signed_url` · `size_bytes` · `stored_keys -> tuple[str, ...]` · `created_at` · `holds_coupon` ·
    `timeout_seconds` · `created_on -> "datetime.date"` · `amount -> "decimal.Decimal"` · Enum `status` · `statuses` · `maybe_status` · `module_status` · `tier`(꾸러미 다시 내보내기 · `enum.IntEnum`) ·
    `visibility`(`models.TextChoices`) · `kind`(저장소 Enum 을 기저로 둔 Enum) · 받아들인 놓침 `payment -> str`. 묻는다 = 객체 · `None` · `run_` · `process_` · 모호 동사 셋 · `invoke_lookup -> OrderStatus` ·
    dataclass · 저장소 밖 · `Iterator` · `timedelta` · 맨 `list` · `_` 이름 · `transmit_payload -> None` · `run_searches`.
  - 검토자 r485 27 → 14 → **16** — v3 에서 `label_iterable -> Iterable[str]` · `meta_str -> dict[str, str]` 이 다시 묻는다. 모호 동사 여덟 · `invoke_later` · `Iterator` · `dict[str, Any]` · `Path` ·
    애너테이션 없음 · `"None"` 그대로 묻음.
  - 검토자 r485c(꼴 51) 51 → 16 → **16** — v3 에서 묻게 된 넷 `dict[str, int]` · `Mapping[str, int]` · `Iterable[str]` · `list[dict[str, str]]`, 묻지 않게 된 넷 `List[str]` · `typing.List[str]` ·
    `Tuple[str, int]` · `Annotated[str, "key"]`. 묻는 16 = `Any` · 맨 `dict` · 맨 `list` · `Dict[str, str]` · `dict[str, int]` · `Generator` · `Iterable` · `Iterator` · `list[dict]` · `Mapping` ·
    `NoReturn` · `object` · `Optional[list]` · `timedelta` · `tuple[()]` · `type[str]`.
  - 검토자 r485e(Enum 풀이) 13 → 3 → **6** — 업무 dataclass `Flag` · `Choices` 기저의 `feature_state` · `quiz_answer` · `enrollment` 가 다시 묻는다. 그대로 묻는 셋 = 다섯 · 여섯 겹 · 별칭 대입.
    같은 파일 · 절대 · 상대 · 다시 내보내기 · 모듈 속성 · `import as` · 네 겹은 풀린다.
  - 검토자 r485f(import 글자 크기) 2 → 0 → **0**(macOS — 위 N6 한계).
- 현장 사본: #485 69 → **38**(v2 37). 사라진 31 = 명사 · 파생 질의 28 + 원시 값을 돌려주는 목록 밖 동사 3. v2 에서 빠졌던 `Mapping[str, <Enum>]` 반환 목록 밖 동사 하나가 다시 묻는다.
  이름으로 배포판 ⊇ v3(새로 묻는 이름 0) · #485 밖 줄 byte 같음 · exit 무변. #485 줄 글자는 물음 글이 바뀌어 남은 38 줄 모두 바뀐다(아래 §3.5). 남은 38 = 목록 밖 동사 25 · 모호 동사 머리 1
  (`request_` · 원시 값 반환 아님) · `run_` 2 · 객체를 돌려주는 명사 질의 10.

### 3.2 규칙 글 — 어느 Norm 에 넣나(`rel/ontology/rules/*.ttl` 에서 확정)
| 자리 | Norm · Block | 지금 | 할 일 |
|---|---|---|---|
| houserules §3 «명명»(graph-owned · 포트 자료의 방향 칸 옆) | 새 Block `…/discipline-houserules/references/final.md/s011-3/b4` · 새 Norm 둘(R-N1 Obligation · R-N2 Prohibition) | 포트 메서드 이름 규칙이 런타임 글에 없다(D39 · 트리 명세에만) | **신설**(사용자 결정의 범위가 포트 메서드) |
| 감수 물음(agent-discipline-reviewer · s007 «포트·어댑터» 줄) | Block `…/agents/discipline-reviewer.md/s007/b52` 글 · Norm R-1123(라벨 «ⓓ#485 이름이 무엇을 시키는지 말하나») | 시키는 갈래만 묻는다 | **개정**(새 Expression `R-1123@2026-11-16` · revision 2 · `prov:wasRevisionOf R-1123@2026-08-22` · revisionKind amendment · 라벨 교체) |
| cleancode §2.6 «클래스 이름은 명사, 메서드 이름은 동사» | 새 Block `…/discipline-cleancode/references/final.md/s018-2.6/b2` | «메서드: 동사» 만 | **다시 말하는 칸 하나** — kind-norm + `djr:restates` houserules s011-3/b4 **만**(statesNorm 없음 · N1). R-1380 은 그대로 |

- N1: 한 Work 를 블록 둘 이상이 말하면 `make rulepack` 이 붉다(`workspace/tools/ontology_rulepack.py:126-128`). 다시 말하는 블록은 Norm 을 말하지 않고 `restates` 만 둔다(배포판에 같은 꼴 19).
- cleancode §2.6 을 «모든 메서드» 로 넓히는 길(규칙 1 ~ 3 을 R-1380 개정으로)은 사용자 결정(포트 메서드)보다 넓다 — 원하면 사용자에게 범위 하나를 묻는다. 추천은 위 표.

### 3.3 새 문장 초안(런타임 글 — 메타 코멘트 없음)
- houserules §3 새 칸(b4 · order 4):
  > - **포트 메서드 이름**(2026-11-16): `port/<capability>/` 계약 메서드의 이름은 의도를 말한다. 조회(부른 뒤 아무것도 바뀌지 않고 값만 돌려준다)는 명사구 · 묻는 꼴도 된다
  > (`url()` · `current_status()` · `created_at()` · `has_shipped()`). 조회가 아니면 모두 명령이고 동사구로 짓는다(`save_photo()` · `charge_order()` · `revoke_for_child()`) —
  > 값을 돌려줘도 무엇이 바뀌면 명령이고, 조회인지 확신이 없으면 명령으로 본다. 로그 · 캐시처럼 결과에 영향이 없는 것은 바뀜이 아니다. `notify()` · `handle()` · `execute()` ·
  > `invoke()` 처럼 무엇을 시키는지 말하지 않는 이름은 위반이다. 판단은 이름을 짓는 쪽이 그 메서드의 의도로 한다(구현을 따라가 저장 · 파일 쓰기를 찾지 않는다).
  > 기계 판정은 #485 다 — 이름이 `notify` · `handle` · `execute` · `process` · `run` · `do` 이거나 `_command` · `_query` 로 끝나면 확정이다. 첫 낱말이 아는 동사도 묻는 꼴도 아닌
  > 이름은 discipline-reviewer 물음 후보다. 단 원시 값(글 · 수 · 참거짓 · 바이트 · 날짜 · 시각 · Decimal · UUID)이나 Enum(과 그 목록 · 선택)을 돌려준다고 선언했고 첫 낱말이
  > 모호 동사(`invoke` · `apply` · `call` · `perform` · `trigger` · `dispatch` · `request` …)가 아니면 묻지 않는다 — 그런 명사 이름 명령은 설계 경량 점검과 구현 감사가 이 규칙으로 본다.
  - R-N1(Obligation) 라벨: «포트 메서드 이름은 의도를 말한다 — 조회(부른 뒤 바뀜 없이 값만)는 명사구 · 묻는 꼴도 · 그 밖은 명령이라 동사구 · 확신이 없으면 명령 · 로그·캐시는 바뀜 아님 · 판단은 이름 짓는 쪽의 의도로»
  - R-N2(Prohibition) 라벨: «무엇을 시키는지 말하지 않는 포트 메서드 이름 금지(notify · handle · execute · invoke 류)»
  - wiring(`wiring/discipline-houserules-final.ttl`): R-N1 · R-N2 `djr:delegatedTo agent-discipline-reviewer` · `djr:enforcedBy check-port-adapter-pairing.py`(앞 칸 R-3500 · R-3501 선례).
  - 번호 R-N1 · R-N2 는 구현 때 `ontology/ISSUED` 끝(2.39.0 = R-3764)에서 다른 단위와 겹치지 않게 채번한다.
- 감수 물음 b52 의 #485 토막(나머지 글 그대로):
  > · #485 이 이름이 의도를 말하나 — 부른 뒤 아무것도 바뀌지 않고 값만 돌려주는 조회면 명사구 · 묻는 꼴도 되고, 그 밖은 명령이라 동사구다(조회인지 확신이 없으면 명령 · 로그 · 캐시는
  > 바뀜이 아니다 · `notify` · `handle` · `execute` · `invoke` 처럼 무엇을 시키는지 말하지 않으면 반송 · 원시 값 · Enum 을 돌려주는 명사 이름도 이 물음으로 본다 — houserules §3 «포트 메서드 이름»)
  - R-1123 새 라벨: «ⓓ#485 이름이 의도를 말하나 — 조회는 명사구도 · 그 밖은 명령이라 동사구»
- cleancode §2.6 새 칸(b2 · order 2 · kind-norm · `djr:restates` houserules s011-3/b4 · statesNorm 없음):
  > 포트 계약 메서드는 조회(부른 뒤 아무것도 바뀌지 않고 값만 돌려준다)면 명사구 · 묻는 꼴도 된다 — 조회가 아니면 동사구다(`discipline-houserules` §3 «포트 메서드 이름»).

### 3.4 그래프 개정 체크리스트(DEVELOPMENT §3 · 1 ~ 6 · G12)
1. 편집 — rdflib 구조 편집 뒤 `canon_turtle` 재직렬화(먼저 현행 ttl 왕복 byte 동일 확인).
   - `rules/discipline-houserules-final.ttl` — Block s011-3/b4(statesNorm R-N1 · R-N2) · Norm 둘 · Expression 둘(`@2026-11-16` · revision 1).
   - `ontology/ISSUED` 두 줄 · `wiring/discipline-houserules-final.ttl` 두 줄.
   - `rules/agent-discipline-reviewer.ttl` — R-1123 새 Expression · currentExpression · prefLabel 교체 · b52 글.
   - `rules/discipline-cleancode-final.ttl` — Block s018-2.6/b2(kind-norm · restates 만).
2. `ontology_gate.py` green → `ontology_render.py --apply` 세 문서(houserules final · cleancode final · discipline-reviewer agent).
3. LEDGER 재기준선 — 다시 투영된 절 셋(houserules §3 · cleancode §2.6 · discipline-reviewer s007)마다 `rebaseline:2026-11-16 F4-95 포트 메서드 이름` 행.
4. 계수표 `workspace/eval/fixtures/ontology_gate/target-counts.json`(2.39.0 값 → 이 단위만의 새 값):
   - NormShape 3773 → 3775 · WorkShape 3773 → 3775(신설 2).
   - ExpressionShape 4366 → 4369(신설 2 + 리비전 1).
   - **BlockShape 3018 → 3020**(houserules b4 · cleancode b2 · N3). SectionShape · AliasEntryShape 무변(#485 alias 없음).
   - 같은 판 다른 단위(a · c)의 그래프 변경과 합칠 때는 더한 값을 쓴다.
   - q4 골든 `query_golden_check.py --emit` · `make rulepack`(소성물 함께 커밋).
5. final.md 소스 미러 — `workspace/reference/discipline-houserules/reference/final.md` §3 · `workspace/reference/discipline-cleancode/reference/final.md` §2.6 을 손으로 맞춘 뒤
   `corpus_mirror_sync --write` → `--check`(Codex final.md 미러도 여기서).
6. Codex 의미 미러 — `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` 의 #485 토막을 같은 뜻으로 손으로.
- 7(새 검사기 규칙 번호) — 없음.
- G12 — 새 · 바뀐 라벨 셋에 식 낱말(신규 · touched · 레거시 · 기존 · diff · 확립 · 보존 …)이 없어 무관(`rulepack_smoke` G12 green 이 확인).

### 3.5 검사기 글 맞춤(사7 · 볼 것 6)
- 머리 docstring #485 줄: «후보: 아는 동사 · 묻는 꼴 밖이고 원시 값 · Enum 반환 선언이 아니거나 모호 동사 머리».
- `VERB_HINTS` 주석: «같은 꼴 `timeout_seconds` 는 원시 값 · Enum 반환을 선언하지 않으면 묻는다(받아들인 한계) · INTENT_DENY · VAGUE_HEADS 의 모호 동사는 넣지 않는다».
- smoke `CandidateWordRegression` docstring: «#485: 포트 메서드 첫 토큰이 아는 동사 목록에 있으면 묻지 않는다 — 목록 밖 낱말은 원시 값 · Enum 반환을 선언하지 않았으면 그대로 묻는다».
- **후보 물음 글을 시제품 v3 에 넣었다**: «이 이름이 무엇을 시키는지 말하나» → «이 이름이 의도를 말하나 — 조회면 명사구도 되고, 그 밖은 명령이라 동사구다».
  파급(v3 사본으로 잼 · N7 방향 바로잡음):
  - `findings_count_matrix` EXPECTED port-adapter 지문(6번째 열) `b0c0ad90cfce6b9e` → `423cf2d5c9625d1d`(1 레인 · 다른 열 무변).
  - 기존 smoke `CandidateWordRegression.test_485_unlisted_first_tokens_stay_questions` 의 물음 상수(1 시험).
  - 새 시험 초안의 `Q485` 상수(넣음).
  - checker_cross_matrix 349 행 차이 0 · fixture_matrix 171/171 · baseline 73/73.
  - registry_gate ⓓ 신규는 앵커 · 현재 두 벌을 같은 검사기로 돌리므로(`registry_gate.py:1528-1534`) 글이 바뀌어도 «신규» 가 생기지 않는다.

### 3.6 규칙 목적
- 사용자 결정으로 닫힘(review-b 차1). 시제품은 결정 문장 그대로다.
- 결정의 «그 목록 · Optional» 을 운영자가 해석한 것(처분 N5): 감싸개는 목록 · 집합 · 튜플 꼴(`list` · `tuple` · `set` · `frozenset` · `Sequence` · `Collection` · typing 대문자)과
  `Optional` · `Union` · `X | None` · `Annotated` 첫 인자까지다. 사전(`dict` · `Mapping`)과 흐름(`Iterable` · `Iterator` · `Generator`)은 «목록» 이 아니라 «확신 없으면 묻는다» 쪽이다.
  `timedelta` 는 사용자 목록(날짜 · 시각)에 없어 묻는다 · `Literal` 은 글 · 수 값. Enum 은 `enum` · `django` 기저만(N2). 이의가 있으면 상수 한 줄로 뒤집힌다.

---

## 4. 시험 도구에 더할 사례(파일은 고치지 않음 · 초안 `b/proposed_smoke.py` v3)

`field_report_checker_smoke.py` — 새 클래스 셋 · 시험 여덟(줄 글자 정확 일치).
- 2.39.0: 붉음 여섯 · 녹색 둘(물음 글이 바뀌어 #485 «유지» 시험도 글자로 붉다). v2: 붉음 둘(`dict` · `Iterable` · `Flag` 기저 · `List` · `Annotated` · 물음 글). v3: 여덟 녹색.
- `InvariantTailRegression`(F4-26 · #257) — v2 와 같음.
  - `test_check_then_value_only_return_ends_with_check` — `cancel_order` · `mark_closed` · `finish` · `park_or_close`(앞 갈래가 바꾸고 확인한 뒤 return) → 0 줄.
  - `test_no_check_at_the_end_stays_a_question` — `drop_note` · `reopen` · `close_and_fold` · `clear_note` · `finish_with_self` · `close_or_park`(길 읽기) · `close_and_invalidate` ·
    `close_with_checkpoint`(낱말 경계) · `close_and_drain`(self 속성을 묶은 이름) → 아홉 줄.
- `UseCaseQueryHeadRegression`(F4-32 · #191) — v2 와 같음.
  - `test_query_verb_heads_pass` — `get_book_detail` · `list_book_status` · `find_loan_info` · `count_loan_list` → 0 줄.
  - `test_noun_phrases_and_other_heads_stay_questions` — 명사구 · 동사 겸용 명사 머리 · `fetch_` · `show_` · 바꾸는 동사 머리 셋 · 애그리거트 이름 `book` → 열둘 줄.
- `PortQueryReturnRegression`(F4-95 · #485 · docstring 에 사용자 결정 11-16)
  - `test_plain_value_answers_read_as_asking` — `str` · `int` · `"str | None"` · `"tuple[str, ...]"` · `bool` · `datetime.date` · `uuid.UUID` · `decimal.Decimal` · `typing.Optional[str]` ·
    **`List[str]` · `typing.Tuple[str, int]` · `Annotated[str, "label"]`** → 0 줄.
  - `test_enum_answers_read_as_asking` — `OrderStatus`(StrEnum) · `list[OrderStatus]` · `"OrderStatus | None"` · `Tier`(다시 내보내기 · `enum.IntEnum`) · `Visibility`(`models.TextChoices`) → 0 줄.
  - `test_object_none_vague_and_unknown_returns_stay_questions` — 객체 · `None` · `run_` · `process_` · `_` 이름 · `invoke -> dict[str, str]` · `perform -> bool` · `apply_change -> int` ·
    `invoke_lookup -> OrderStatus` · dataclass · 저장소 밖 이름 · `Iterator[str]` · `timedelta` · 맨 `list` · **`dict[str, str]` · `Iterable[str]` · 업무 dataclass `Flag` 를 기저로 둔 `FeatureState`** → 열일곱 줄.
  - `test_accepted_miss_noun_named_command_with_plain_or_enum_return` — `payment -> str` · `reservation -> OrderStatus` → 0 줄(사용자 결정이 받아들인 놓침 · 붉어지면 결정 기록을 먼저 고친다).
- `_MUTATIONS` 에 더할 변이 스물하나 — 초안으로 모두 죽음을 봤다.
  - #257: self 조건 뺌 · self 속성을 묶은 이름 뺌 · 건너뛴 뒤 `if` 도 확인 · 호출 return 도 건너뜀 · 길 읽기 뺌 · 낱말 경계 뺌.
  - #485: first 조건 뺌 · INTENT_DENY 조건 뺌 · 모호 동사 머리 뺌 · 객체 반환도 질의 · Enum 판정 뺌 · **들여온 곳 확인 뺌** · **Iterator · Iterable 도 묶음** · **dict 도 묶음** ·
    **typing 대문자 뺌** · **Annotated 첫 인자 뺌** · timedelta 도 원시 · 점 이름 앞 이름으로 · **물음 글 옛 글로**.
  - #191: 머리 넓힘 · 머리 뺌.
- 새 클래스는 반환 애너테이션을 받는 도움을 둔다(기존 `CandidateWordRegression.port()` 는 `-> None` 만 쓴다 — 물음 상수만 바꾸면 녹색).
- `fixture_matrix.py`(선택): `domain_model/good` 루트에 «확인 호출 + `return True`» 메서드를 더하면 0 줄 레인이 #257 을 지킨다 — 픽스처를 고치면 지문 · 봉인이 함께 움직여 smoke 로 충분하면 넣지 않는다.

## 5. 검사 · 구현 때(DEVELOPMENT §3 체크리스트 8)
- 시제품 v3 세 파일을 넣은 검사기 사본(`run/scripts-v3`)으로 잰 값(OS 임시 폴더 그대로):
  - fixture_matrix 171/171 · checker_baseline_matrix 73/73 · checker_cross_matrix 349 행 차이 0.
  - findings_count_matrix 72/73 — 불일치 1 = port-adapter 지문 `b0c0ad90cfce6b9e` → `423cf2d5c9625d1d`(물음 글 · §3.5 · EXPECTED 갱신 대상).
  - field_report_checker_smoke 171/172 — 실패 1 = `test_485_unlisted_first_tokens_stay_questions` 물음 상수(§3.5 · 시험 글 갱신 대상).
  - `construct_drift_report` 는 구현 때 돌려 확인.
- Codex byte 미러 세 파일 · `gen_pregate_symbol_kinds` 재소성(`source_sha` 세 칸 · 두 미러) · 봉인(§4 · §6) → `make verify` 전체 + `make verify-mutation`.
- 그래프 개정이 따르므로 §3.4 의 1 ~ 6 과 rulepack · LEDGER · 계수표를 함께 커밋한다.
- 실행 시간: port-adapter 현장 사본 배포판 25.6 · 24.7 s ↔ v2 24.7 · 25.8 s(번갈아 두 번씩 · 차이 없음 · v3 의 더함은 들여온 곳 확인 한 번뿐). domain-model 은 다른 단위 검사와 겹쳐
  벽시계가 흔들렸다 — 새 판정만 따로 재니 현장 domain_layer 메서드 2682 개에 CPU 0.080 s 로 무시할 크기다.
- 요청 가이드: 사용자가 요청에 쓰는 칸 · 플러그인이 묻는 일이 바뀌지 않음 → «바뀔 것 없음»(포트 메서드 이름 규칙은 설계 · 감수 쪽 글).

## 6. 글 맞춤(graph-owned 아님 · 손으로)
- predicates(`workspace/design/2026-08-11-predicates.md`):
  - 129(#191): «후보: 이름 전체가 애그리거트 이름이거나, 묻는 동사 머리(`get` · `find` · `list` · `count`)로 시작하지 않으면서 `_list` · `_info` · `_detail` · `_status` 로 끝나는 것
    (루트 공개 메서드 첫 토큰 자동 통과는 두지 않는다 — 수집 비용) / 물음: Q1».
  - 144(#257): «… / 후보: 루트 공개 메서드 중 자기 속성에 대입하면서 마지막 문장이 검증 호출 · `raise` · `if` 가 아닌 것 — 마지막이 값만 돌려주는 return 이고 그 앞이 `_` 낱말로
    확인 호출(assert · check · ensure · valid · validate · verify)이며 self 에 쓴 뒤 확인 없이 빠져나가는 다른 return 이 없으면 확인으로 끝난 것 / 물음: Q4».
  - 197(#485 · 사6): «확정: (그대로) / 후보: deny-list 밖인데 첫 `_`-토큰이 아는 동사 목록(데이터 — 닫지 않는다 · 모호 동사는 넣지 않는다)에 없고 묻는 꼴 접두(`has_` · `is_` · `can_` ·
    `current_` · `get_` · `find_` · `list_` · `count_` · `exists_`)도 아니며, 원시 값(글 · 수 · 참거짓 · 바이트 · 날짜 · 시각 · Decimal · UUID) · Enum(`enum` · `django` 기저를 둔 저장소
    클래스)과 그 목록 · 선택을 돌려준다고 선언하지 않았거나 첫 토큰이 모호 동사(`invoke` · `apply` · `call` · `perform` · `trigger` · `dispatch` · `request` · `exec` · `operate` · `manage`)인 메서드 /
    물음: 「이 이름이 의도를 말하나 — 조회면 명사구도 되고, 그 밖은 명령이라 동사구다」».
- 세 검사기 머리 docstring(시제품에 넣음).

## 7. 장부 처분 문장 초안(배포 뒤 운영자가 덧붙임 · 판 · 시각 · 태그는 그때)
- F4-26: «처분 갱신(<시각> · 운영자): 수리됨 = dddjango <판>(<배포 시각> · 태그) — ⓓ#257 은 끝이 «확인 호출 + 값만 돌려주는 return» 이고 상태를 바꾼 뒤 확인 없이 빠져나가는
  다른 return 이 없으면 확인으로 끝난 것으로 본다. 같은 결 남음: 덧셈 대입만 하는 메서드는 «상태 변경» 으로 세지 않음 · 끝 `if` 를 확인으로 침(작업 리스트).»
- F4-32: «처분 갱신(<시각> · 운영자): 수리됨 = dddjango <판>(…) — `draw` 는 dddjango 2.27.3(ffbacbd5)에서 고쳐짐 · ⓓ#191 은 묻는 동사 머리(get · find · list · count)로
  시작하는 유스케이스 이름을 명사 접미 후보에서 뺀다. 신고 꼴 수리 · 같은 결 남음: 바꾸는 동사 머리(update · change · set · edit · cancel) · 그 밖 동사 머리(search · fetch · show)와
  명사로도 읽히는 머리(read · load) + 명사 접미는 계속 묻는다(현장 0 · 넓히려면 장난감으로 재서).»
- F4-95: «처분 갱신(<시각> · 운영자): 수리됨 = dddjango <판>(…) — `replace` · `link` 는 dddjango 2.27.3(ffbacbd5)에서 고쳐짐 · 사용자 결정(11-16 «확정»)대로 포트 메서드는 조회면
  명사구 · 묻는 꼴도 되고 그 밖은 동사구(규칙을 houserules §3 · 감수 물음에 넣음) · ⓓ#485 는 원시 값 · Enum 과 그 목록 · 선택 반환을 선언하고 모호 동사 머리가 아니면 묻지 않는다.
  받아들인 놓침: 원시 값 · Enum 을 돌려주는 명사 이름 명령(감수 몫). 같은 결 남음: 목록 밖 동사 머리(현장 25 줄 · 작업 리스트).»

## 8. 남은 걱정
- F4-26 길 읽기 · 묶은 이름은 도움 메서드 안의 바뀜 · 첨자 · `or` · 두 번 건넌 별칭 · 원소 별칭을 보지 않는다(현장 0).
- F4-95 Enum 판정은 `enum` · `django` 밖 Enum 꾸러미를 기저로 둔 클래스를 묻는 쪽으로 보낸다(소음 쪽) · 값 이름은 끝 이름만 본다 · 다섯 겹 이상 · 별칭 대입은 못 푼다(묻는 쪽).
- cleancode §2.6 을 모든 메서드로 넓힐지는 사용자 범위 질문으로 남긴다(추천은 넓히지 않음).
- R-N1 · R-N2 채번과 계수표 합산은 같은 판의 다른 단위(a · c)와 겹치지 않게 구현 때 한다.
- #485 의 남은 소음 대부분(현장 25/38)은 목록 밖 동사다 — 신고 밖 · 작업 리스트.
- 현장 사본은 리허설 클론 하나다.


---

# 3판 재현 · 원인 · 고칠 방향 초안 — 단위 a(기준선 · 기록 파일) · v5

- 맡은 항목: F4-27 · F4-136(위반 기록 파일이 작업 트리에 남음) · F4-28(앵커 사본에서만 `check-app-container` 2 → 거짓 «해소 1») · F4-46(ⓓ#644 행수가 바뀌면 legacy 가 «신규» 로 다시 뜸) · v2 에서 더한 **N1** 계약 문법 합성 줄의 가림 · **N2** 첫 `migrations/` 폴더를 못 봄 · **N3** 문서 입력 비대칭(사용자 11-16 «가»).
- v3 = 설계 독립 검토(`pan3-1116/review-a/REVIEW.md` · 차단 1 · 중요 8 · 사소 5) 처분(`op-rev/DISPOSITION.md` «review-a») 반영.
- v4 = 좁은 재확인 1(`review-a/RECHECK-1.md` · 차단 R1 · 중요 R2 · 사소 R3 ~ R7) 처분(`op-rev/DISPOSITION.md` «좁은 재확인 1(a v3 · 둘째 확인)») 반영. 고침마다 반대 꼴(대조) 장난감을 함께 적었다. 바뀐 것은 끝 «v3 → v4 바뀐 것».
- v5 = 셋째 확인(`review-a/RECHECK-2.md` · 차단 R1′ · 사소 S1 ~ S3) · 사용자 «가.»(11-16 16:07 — 고치고 넷째 확인) · 처분(`op-rev/DISPOSITION.md` 끝 두 절) 반영. R1′ 은 검토자 둘째 길(ⓐ — 출처 판정에서 앱 폴더 줄의 «건드림» 을 만든 경로만 파일 단위로)로 고쳤다(§2 «R1′»). 바뀐 것은 끝 «v4 → v5 바뀐 것».
- (v4 때) **처분 글과 다른 자리에서 고친 것 둘**(장난감 판정은 처분 요구와 같음 · 운영자 확인 필요): R1 은 «지금 사본 건드림에서 경로 빼기» 대신 출처 재실행에 끝 커밋을 넘겨 L 을 세움(§2 — 유입 기록 · merge-idem 판정 유지) · R2 는 «안전한 셋 · 같은 기호» 갈래 없이 «흔들리는 칸만 다른 글» 짝 하나로(§4 — 일곱 검사기 글 꼴에서 그 갈래가 새로 짝 짓는 줄이 없음 · 처분보다 좁음 · 그 판 v4a 를 `a/proto-v4a/` 에 남김).
- 기준: 배포판 2.39.0(태그 `dddjango--v2.39.0` = f36fa9f9) 사본 `pan3-1116/rel/` · main b29635ca. v1 실행 11-16 03:03 ~ 03:49 · v2 08:50 ~ 10:08 · v3 10:45 ~ · v4 12:10 ~ · v5 16:10 ~.
- 시제품: `pan3-1116/a/proto/scripts/` = v5(v4 는 `a/proto-v4/` 로 남김 · rel 의 scripts 를 복사한 위에 여섯 파일만 고침 — `findings.py` · `anchor_diff.py` · `registry_gate.py` · `check-app-container.py` · `check-idempotency-scope-creep.py` · `checker_target.py` · 링크 없음). 옛 판 `a/proto-v1/` ~ `a/proto-v4/` · `a/proto-v4a/` 를 남겨 나란히 돌렸다.
- 장난감: v1 · v2 의 `a/toys/`(지은 이름 `orders` · `catalog` · `payments` · `OrderRepository` · `IdempotencyRecordStore`)와 검토자 장난감 `review-a/toys/`(읽기만 · 커밋 판은 이름 끝 `c`). v4 에서 대조 장난감 셋 갈래를 `a/toys/` 에 더함(`merge-migx(c)` · `rs-*` · `skel-cas(c)` — 만든 스크립트 `a/mk_rs.sh` · `a/mk_skel_cas.sh` · merge-migx 는 검토자 merge-mig 의 복제 위에 레인 마이그레이션 하나). v4 하네스 `a/run4.sh` · `a/run4_all.sh` · `a/run4_skel.sh` · 출력 `a/out/v4/`(v3 출력 `a/out/v3/` 은 그대로). v5 에서 검토자 R1′ 장난감 일곱을 `review-a/bin/mk6.sh` 를 내 폴더로 복사해 A 경로만 바꾼 `a/mk6.sh` 로 `a/toys/mm-*` 에 지었다(검토자 폴더의 하네스 · 출력은 쓰지 않음) · v5 하네스 `a/run5_r1.sh` · `a/run5_reg.sh`(`a/run4.sh` 의 판 v5) · 출력 `a/out/v5/`.
- 기존 시험: 저장소 main 의 `--shared` 복제 모래상자 `a/repo-v2/`(시제품 여섯 파일을 플러그인 · Codex 미러 두 곳에 넣음 · `CLAUDE.md` 는 운영자가 지움)에서 돌렸다(§7).
- 규칙 목적에 닿는 질문: **0개**(일곱 갈래 모두 «질문 생략 · 설계 처리» — 까닭은 각 절). 2.39.0 대비 새로 막는 것 · 푸는 것은 §8(알림 필요). 그래프 글 하나(R-3617)가 바뀐다(§4 · §10 — 구현 때 그래프 담당). 운영자 판단으로 남긴 것 하나: merge-idem +승인을 2.39.0 처럼 귀속으로 둘지(v5) 검사기 정의대로 0 으로 풀지(§2 «R1′»).

---

## 1. F4-27 · F4-136 — 위반 기록 파일이 작업 트리에 남는다

### 재현(2.39.0 · 장난감 `toys/sink` — 설치 표식 `.dddjango/<시각>-orders/scope.md` 가 있는 git 저장소 · `run_sink.sh rel`)

| 갈래 | 명령 | exit | 작업 트리 `.dddjango/violations/*.jsonl` | 호출자 폴더 |
|---|---|---|---|---|
| 1 | 검사기 직접 실행 · 변수 없음 | 2 | **1(`??` 미추적)** | — |
| 2 | 직접 실행 · `DJR_VIOLATIONS_DIR=<폴더>` | 2 | 0 | 1 |
| 3 | 직접 실행 · `DJR_FINDINGS_JSON=<파일>` | 2 | 0 | 10줄 |
| 4 | 직접 실행 · `DJR_EXPERIMENT_RUN_ID=t2ab-R01`(A/B 실런) | 2 | 1 | — |
| 5 | `registry_gate --anchor` · `DJR_VIOLATIONS_DIR=<폴더>` | 2 | 0 | **0** |
| 6 | `registry_gate --anchor` · 변수 없음 | 2 | 0 | — |
| 7 | scope 렌더 직접 실행 `--anchor`(`check-context-isolation --scope-bc orders`) · `DJR_VIOLATIONS_DIR` · 앵커 · 지금 모두에 같은 legacy 위반 1(`toys/ghost`) | 0 | — | **2 파일**(지금 실행 1 + 앵커 재실행 1) |

- F4-136(검사기 직접 실행이 미추적 파일을 남김) — **재현됨**(갈래 1).
- F4-27 의 «`registry_gate` 가 `DJR_VIOLATIONS_DIR` 를 지워 작업 트리에 쌓인다» — **게이트 몫은 재현 안 됨**(갈래 5 · 6). 게이트는 2.18.4 판(보고 판)부터 지금까지 작업 트리의 사본에서 검사기를 돌리고 검사기마다 임시 sink 를 준다 — 쌓인 파일은 같은 레인의 직접 실행분이다(보고의 귀속 추정이 어긋남). 호출자의 `DJR_VIOLATIONS_DIR` 에 기록이 오지 않는 것(갈래 5)은 맞다 — 아래 «게이트는 고치지 않는다».
- 새로 본 것(갈래 7): scope 렌더 직접 실행의 앵커 재실행이 `DJR_FINDINGS_JSON` 만 걷고 `DJR_VIOLATIONS_DIR` 는 그대로 물려줘, 호출자 폴더에 stdout 에 없는 앵커 몫 레코드가 따로 쌓인다(T2-1 이 파일 sink 에서 고친 «유령 레코드» 와 같은 꼴).
- 현장 사본(리허설 클론 · 읽기만 · `git ls-files`): `.dddjango/violations/*.jsonl` **추적 286개**(커밋 25개 · 08-29 ~ 10-28 — 레인이 `.dddjango/` 를 커밋하며 함께 쓸어 담음 · 저장소가 `.dddjango/` 를 무시하지 않음) · **미추적 48개**(11-14 운영자 조사 실행 · 판 B 설계 기록에 적힌 것).

### «일부 고쳐짐» 확정
- 2.19.0(a9ced34e · 10-01): 쓰기 울타리 창 안의 코디네이터 직접 실행은 `DJR_FINDINGS_JSON=<울타리 폴더>/findings.jsonl`(`commands/dddjango.md:63`).
- 2.38.0(19df25ee · 11-14): `refactor_audit.py run-state` 가 `.dddjango/violations` 를 «실행 폴더 아님 — 건너뜀» 으로 G0 폴더 목록에서 뺌.
- 안 고쳐진 것: 울타리 창 밖의 직접 실행 — G0 리팩터링 스캔(27종 직접) · Phase 2 6번 백스톱 직접 실행 · coder · 시험 역할의 자체 확인 · 운영자 조사. 갈래 1 · 현장 미추적 48 이 지금도 생긴다.

### 원인
- `rel/dddjango/scripts/findings.py:125-140` `_default_dir` · `_sink_mode` — 표식 `.dddjango/` 가 있으면 `<TARGET>/.dddjango/violations/` 를 기본 sink 로 켠다(T2-2 · 526772c5 · 08-20). 표식은 파이프라인 산출물 폴더라 **모든 레인에 있다**. 대상 등록은 `checker_target.py:134`(27종 공통 한 곳).
- 기본 자리가 작업 트리 안인 까닭: T2 온톨로지 A/B 실런의 관측 채널 — 실런 레인에서 검사기가 도는 자리에 남기고 저장소 쪽 `collect_violations.py --from <타깃>/.dddjango/violations --run t2ab-R<NN>`(`workspace/eval/ab/orders/README.md:80`)가 거둔다. 실런 레인은 `DJR_EXPERIMENT_RUN_ID` 를 세션 환경으로 띄우고(`workspace/eval/ab/BK2-RUNSTATE.md:90`) 수집기는 `--run` 이면 그 실런 레코드만 거둔다(`collect_violations.py:81-90` — 나머지는 «다른 실런 — 미수집»). 실런 밖 수집은 쓰인 적이 없다(`workspace/eval/violations/raw/` 없음).
- `registry_gate.py:428-440` 이 검사기 환경에서 `DJR_FINDINGS_JSON` · `DJR_VIOLATIONS_DIR` 를 걷고 검사기마다 `<임시>/records-*.jsonl.NN.part` 를 준다. 까닭(`:404-409` · 적대 리뷰 AM#3 · AN#3): 앵커 실행분과 현재 실행분이 한 sink 에 섞이면 소비자가 legacy · 신규를 못 가른다 — `commands/dddjango.md:220` «검사기의 레코드 파일을 직접 읽지 않는다 — 앵커 실행분이 섞여 legacy 잔존까지 고치게 된다» 의 전제.
- `anchor_diff.py:1257-1264` `_run_lines` 가 `DJR_FINDINGS_JSON` 만 걷는다(갈래 7).

### 같은 꼴의 다른 자리
- `design_pregate.py:4782-4785` 는 파일 sink 를 스크래치로 두고 디렉터리 sink 를 걷는다(이미 막힘).
- Codex 미러 `codex-dddjango/skills/dddjango/scripts/` 의 같은 파일(byte 동일 — rel 에서 `cmp` 확인).
- dddjango-web: web 검사기는 이 기록 채널을 쓰지 않는다(이번 일 밖 · 확인만).

### 고칠 방향
1. **(추천) 기본 자리는 실런일 때만 켠다** — `findings.py` `_default_dir` 에 «`DJR_EXPERIMENT_RUN_ID` 가 없으면 None» 한 조건 + 머리 글 ③. 함께 `anchor_diff._run_lines` 가 `DJR_VIOLATIONS_DIR` 도 걷는다(1줄). 비용 S(findings +8 −5 · anchor_diff +1).
   - A/B 실런: 레인 세션에 변수가 있어 지금처럼 쌓이고 수집기가 거둔다(바뀌는 것 없음 — 수집기는 원래 실런 레코드만 거둔다).
   - 실런 밖 직접 실행: 아무것도 남기지 않는다. 명시 변수(`DJR_FINDINGS_JSON` · `DJR_VIOLATIONS_DIR`)는 지금 그대로.
   - 새로 막는 것 0 · 푸는 것 0(판정 · exit · stdout 무변 — 기록 자리만).
   - 위험: 실런 밖에서 기본 자리 기록에 기대던 소비자 — 저장소 안 0(시험 · 도구 grep: 기본 자리에 기대는 시험 없음 · `pregate_transcription_smoke` 의 «설치 표식 저장소» 사례는 «남기지 않음» 을 단언하므로 그대로 녹색).
2. 기본 자리를 아예 없앤다(명시 변수만) — A/B 절차 글(README:80) · 하네스를 함께 바꿔야 하고 온톨로지 실험 설계 방향에 닿는다(사용자 결정) · 비용 M · 이득은 1 과 같음.
3. `.dddjango/violations/.gitignore`(`*`)를 만든다 — git 에는 안 보이나 파일은 계속 쌓인다(F4-136 «남는 파일을 만들지 않는다» 미충족) · 이미 추적된 파일과 섞임.
4. 역할 · 조정자 글에 «직접 실행마다 `DJR_FINDINGS_JSON`» 을 늘린다 — 울타리 규칙이 이미 그랬는데도 창 밖에서 샌다 · 글 여러 곳 · 지키기 어려움.
- **게이트는 고치지 않는다**: 두 채널을 걷는 것은 앵커 · 현재 · 출처 재실행 레코드를 섞지 않는 장치다. 걷지 않으면 호출자 폴더에 세 벌이 섞여 위 계약이 깨진다. F4-27 의 다른 «기대»(«게이트 전용 임시 폴더를 쓰고 끝에 알린다»)는 이미 임시 sink + `--introduced-json` 으로 서 있다.
- 규칙 목적: 판정과 무관한 기록 자리 · A/B 수집이 실런 레코드만 거두는 정의에서 답이 나온다 → **질문 생략 · 설계 처리**. 이미 추적된 현장 jsonl 286 은 현장 저장소 주인 몫(지우기 · 그대로 — 알림만).

### 시제품 결과(`run_sink.sh proto` · `toys/ghost`)
- 갈래 1: 작업 트리 jsonl **1 → 0**(붉음 → 녹색) · exit 2 그대로.
- 갈래 4(실런): 1 → 1(대조 — A/B 기록 그대로).
- 갈래 2 · 3 · 5 · 6: 그대로(대조).
- 갈래 7: 호출자 폴더 **2 → 1 파일**(지금 실행분만) · stdout 은 앵커 sha 빼고 byte 같음.
- 현장 복제(`--shared` · 설치 표식 있음): `check-layer-skeleton` 직접 실행(변수 없음) — 배포판 jsonl 1 → 시제품 0 · exit 2 · stdout byte 같음. 판정이 바뀌는 고침이 아니라 검사기 줄 차이 0.

### 구현 때(DEVELOPMENT §3 체크리스트 8)
- Codex byte 미러 `findings.py` · `anchor_diff.py`.
- EXPECTED: 바뀔 것 없음 예상(`findings_count_matrix` · `checker_baseline_matrix` · `checker_cross_matrix` · `construct_drift_report` 는 명시 sink · 검사기 출력 무변) — `make verify` 로 확인.
- pregate kinds: 무관(`pregate_symbol_kinds.json` 의 `source_sha` 는 검사기 27 + `checker_target.py` — `findings.py` · `anchor_diff.py` 밖).
- 봉인: `findings.py` · `anchor_diff.py` 는 봉인 대상(`manifest_seal.py:57 · :61`).
- 글: `commands/dddjango.md:63` «이 변수가 있으면 `.dddjango/violations/` 게시가 없다» 는 그대로 참 — 고칠 글 없음.

### 시험 사례(더할 것 — 파일은 고치지 않음)
- `anchor_diff_smoke.py`: (a) 표식 있는 장난감에서 검사기 직접 실행(변수 없음) → `.dddjango/violations` 없음 · (b) 같은 실행에 `DJR_EXPERIMENT_RUN_ID` → 파일 1 · (c) scope 렌더 `--anchor` + `DJR_VIOLATIONS_DIR` + 앵커 · 지금 모두에 같은 legacy 1 → 폴더의 레코드 run_id 가 하나뿐(앵커 재실행분 없음).
- `registry_gate_smoke.py`: 표식 있는 TARGET + `DJR_VIOLATIONS_DIR` → TARGET 작업 트리 · 호출자 폴더 모두 jsonl 0(지금도 녹색 — 두 채널 pop 을 걷는 변이를 죽이는 보호 장치).

---

## 2. F4-28 — 앵커 사본에서만 `check-app-container` 2 → 거짓 «legacy 해소 1»

### 재현(2.39.0 · 장난감 — 앵커에 `application/` 밖 legacy 평면 앱 `catalog/` · `a/out/v3/table.txt`)

| 갈래 | 레인 변경 | 작업 트리 직접 실행 | 게이트 표 `anchor \| current` | app-container 귀속 | 판정 |
|---|---|---|---|---|---|
| a · ac(커밋) | 무관 파일 하나 | 0 | **2 \| 0** · 해소 **1** | 0 | 거짓 해소(보고 꼴) |
| b · bc | `catalog/migrations/0002_more.py` 더함(건드린 legacy 평면 앱) | b 2 · bc 0 | b 2 \| 2 · bc 2 \| 0 | 0 | **놓친 막힘**(게이트 exit 0) |
| c · cc | 새 평면 앱 `payments/` | c 2 · cc 0 | 2 \| 2 · 2 \| 0 | 0 | 가려짐(게이트 붉음은 #336 몫) |
| f · fc | 새 평면 앱 `payments/`(`models/` 꾸러미만) | f 2 · fc 0 | 2 \| 2 · 2 \| 0 | 0 | **놓친 막힘**(게이트 exit 0) |
| d(대조) | 무관 · 앵커에 모델 있는 `cross_context/backoffice` | 2 | 2 \| 2 | 0 | legacy 잔존 1 |

- 보고 꼴 **재현됨**(a · ac) — 그리고 보고보다 큰 결함: legacy 평면 앱이 하나라도 있는 저장소에서는 게이트가 이 검사기의 새 위반을 늘 가린다.

### 원인
- `check-app-container.py` 는 계약 문법 줄(`- {where}: {msg}`)을 낸다 → `registry_gate.py:138` `_FINDING_RE`(`[#N]` 만)에 안 잡혀 `:484` 합성 줄 하나 — 이 검사기의 차분은 exit 값 차분이다(N1 이 고침 · §4).
- 앵커 사본 실행(`:1530`)에는 원본 git 루트가 없다(`:411-416` BK1 주석). `check-app-container.py:157-170` 이 fail-closed(전 후보) → 합성 줄이 L 에 늘 있다.
- «건드림» 의 기준도 어긋나 있다(검토 차1 · 중2): 지금 사본은 원본 루트의 porcelain(HEAD 대비)을 묻는데 게이트의 «이번 런» 은 앵커부터다. 레인이 변경을 **커밋**한 뒤 G2 를 돌면(슬라이스 · 창 close 앞 커밋 — `commands/dddjango.md` Phase 2 3번 · R-3700) porcelain 이 깨끗해 «건드림 없음» 이 된다(bc · cc · fc 의 직접 실행 0).

### 같은 꼴의 다른 자리
- 원본 git 루트를 읽는 검사기는 app-container 하나(2.39.0). v3 에서는 idempotency 도 같은 문맥을 쓴다(§6).
- git touched 를 묻는 다른 검사기(choices-literal · db-table · mechanism-ownership · synthetic-infra-exc · transient-overmapping · composition-root · openapi · api-error-controller · error-centralization · business-vocabulary #604)는 두 사본 모두 비-git 이라 대칭(둘 다 fail-closed) — 거짓 해소는 없다. fail-closed 검사기에서 «직접 실행 0 · 게이트만 새 붉음» 이 나는 꼴은 §8(검토 중7).
- 코드로만 본 대상 집합 차이(장난감 안 지음): `_IGNORE_COPY`(build · dist · staticfiles · site-packages · node_modules · venv · `registry_gate.py:141-147`)는 지금 사본만 뺌 · `git archive` 는 `export-ignore` 속성 파일을 뺌 · 지금 사본 `copytree` 는 링크를 따라 복사. gitignore 된 파일과 미추적 파일이 지금에만 있는 것은 의도(«.gitignore 은닉» 막기 · 레인 작업).

### 고칠 방향(v3 · v4)
1. **(추천) 게이트가 두 사본에 git 문맥을 준다** — 앵커 사본에는 «커밋 트리» 표지, 지금 사본에는 원본 루트 + 앵커 커밋.
   - 앵커 사본: `DJR_COMMITTED_SNAPSHOT=<앵커 사본 절대 경로>`(시제품 `registry_gate.py:582`). 검사기는 표지 값이 자기 뿌리(resolve)와 같을 때만 믿는다 — 게이트 밖에서 `=1` 처럼 켜져도 fail-open 이 되지 않는다(검토 사10 · 비-git 장난감 `nongit-c` · `nongit-idem`: v2 값 1 → 0 이던 것이 v3 은 2 그대로 · 값 = 자기 경로일 때만 0).
   - 지금 사본: `DJR_SOURCE_GIT_ROOT`(지금처럼) + **`DJR_SOURCE_GIT_BASE=<앵커 SHA>`**(차1 · 시제품 `:1678` · `:1692`). 검사기는 «건드림» 을 앵커 대비로 센다 — `git diff --name-status -z <앵커>` 의 지우지 않은 경로 ∪ `status --porcelain -z --untracked-files=all` 의 미추적(새 경로 = 앵커 트리 `ls-tree` 에 없는 경로). dddjango-web 백스톱 `--diff-base`(`dddjango-web/scripts/src/common.py:829-890`)와 같은 꼴이다. 커밋 · 미커밋이 같은 판정이 된다.
   - 판정 한 곳: `checker_target.py` 에 `gate_git_root` · `committed_snapshot` · `gate_base` · `anchor_changes`(+112 · 프로세스 안 캐시 — 검사기마다 git 셋 한 번). app-container · idempotency 둘이 이것만 부른다(v2 의 두 벌 복제를 모음).
   - app-container(시제품 `:160-169`): 앵커 트리에 그 앱 폴더 파일이 없으면 새 앱 · 앵커 대비 새 경로 가운데 `<앱>/migrations/*.py`(`__init__.py` 밖) · `<앱>/apps.py` · `<앱>/models.py` 가 있으면 건드림.
   - **변수가 없을 때(사용자 · 역할의 직접 실행)는 지금 그대로**(HEAD 대비 porcelain + N2 고침) — 장난감 bc · cc · fc 직접 실행 0 은 세 판 모두 같다.
   - 크기(대략 · 머리 글 빼고): registry_gate +11 · checker_target +112 · app-container +24 −14 · findings +4.
2. 지금 사본만 앵커 대비로 바꾸지 않고 «커밋 안 한 채 G2» 를 받아들인 한계로 적는다 — 파이프라인의 정식 길(커밋하는 실행)에서 F4-28 · N3 의 새 막힘 대부분이 서지 않고, N3 은 2.39.0 이 막던 꼴(idem-newc)을 연다(검토 차1) → 기각.
3. v1 의 다른 기각 셋(앵커 L 비우기 · 앵커를 worktree 로 · 해소 셈만 빼기)은 그대로 기각.
- **승인 머지 출처 재실행(R1 · v4)**: 출처 판정(W · F1 · F2 · L)의 사본 재실행(M^1 · M^2 커밋 트리)에도 원본 루트 · 앵커와 **그 커밋**을 넘긴다 — 새 변수 `DJR_SOURCE_GIT_TIP=<M^k>`(상수 `findings.ENV_GIT_TIP` · `checker_target.gate_tip`). 검사기의 «건드림» 은 그 사본에서 `앵커..M^k` 커밋 차이다(`git diff --name-status <앵커> <M^k>` · 미추적 없음 — 커밋 트리 사본이라). 그러면 L(ℓ ∈ R(M^2)∖R(M^1))이 지금 사본과 같은 뜻으로 선다: 레인이 건드리지 않은 legacy 앱은 M^1 에서 줄이 없고, main 이 그 앱에 마이그레이션을 더한 M^2 에서 줄이 있다 → **승인 유입**(exit 제외 · 기록). v3 은 두 사본 모두 fail-closed 라 L 이 서지 않아 «유입 증명 실패(이중 원인)» 로 귀속했다(검토 R1 차단).
  - 검토 권고(«지금 사본 건드림에서 승인 머지가 그대로 들인 경로를 뺀다»)와 다른 자리에서 고친 까닭: ① 경로를 «건드림» 에서 빼면 그 줄이 아예 사라져 2.39.0 의 «승인 유입» 기록(exit 제외 · 기록 의무)이 남지 않는다 ② 레인이 scope 를 «미요청» 으로 두고 main 이 멱등 파일을 들인 이중 원인(merge-idem)이 귀속 0 이 된다 — 2.39.0 은 귀속 · 처분이 요구한 «merge-idem 은 2.39.0 과 같은 판정» 과 어긋난다 ③ F1 같은 파일 판정을 검사기 쪽에 한 벌 더 두게 된다. 출처 판정을 그대로 쓰면 F1 · L 이 게이트 provenance 한 출처에 남는다.
  - 크기: registry_gate +4(인자 · 환경 · 출처 재실행 호출) · checker_target +10(`gate_tip` · `anchor_changes` 의 끝 커밋 길) · findings +3.

#### R1 장난감(`a/run4.sh` · 출력 `a/out/v4/<장난감>[+승인]-<판>.txt` · 처분 요구와 대조)

| 장난감 | 꼴 | 2.39.0 | v3 | v4 |
|---|---|---|---|---|
| **merge-mig +승인** | 레인은 legacy 평면 앱 `catalog` 를 안 건드림 · main 이 `catalog/migrations/0002` · 승인 머지로 받음 | 귀속 0(앵커 합성 줄이 가림 · 거짓 해소) | **귀속 1**(유입 증명 실패 · 이중 원인) | **귀속 0 · 승인 유입 1**(L 증명 · 폴더 verbatim) |
| merge-newapp +승인 | main 이 새 평면 앱 `payments` | 0(가려짐) | 유입 1 | 유입 1 |
| merge-idem +승인 | 레인 scope «미요청» + main 이 멱등 파일 | 귀속 1(레코드 없음) | 귀속 1(이중 원인) | **귀속 1(이중 원인) — 2.39.0 과 같은 판정** |
| merge-m +승인 | 승인 머지가 계약 위반을 그대로 들임(N1) | 귀속 1 · exit 2 | 유입 · exit 0 | 같음 |
| 대조 merge-m2 · m3 +승인 | 레인이 그 주어를 작업 트리에서 고침 | 귀속 | 귀속(worktree 수정 중) | 같음 |
| **대조 merge-migx · merge-migxc +승인**(내 장난감) | merge-mig 위에 레인이 `catalog/migrations/0003` 을 더함(미커밋 · 커밋) | 귀속 0(가려짐) | 귀속 1 | **귀속 1**(«worktree 수정 중» · «레인 커밋 수정 …(승인 머지 이후)») |
| **대조 merge-mig · merge-newapp 승인 목록 없음** | 같은 머지 · `--approved-merge-file` 없음 | 0(가려짐) | 귀속 1 | **귀속 1**(§8 «새로 막음») |
| 대조 merge-idem 승인 목록 없음 | | 귀속 1 | 귀속 1 | 귀속 1 |
| 대조 커밋 판 bc · cc · ec · fc · gc · jc · kc · newparentc · idem-newc · renc | 레인 자기 커밋 | 0(가려짐 · idem-newc 만 1) | 귀속 1 | **귀속 1 그대로**(`a/out/v4/all.txt` — 검토자 장난감 38줄 v3 = v4 같음) |
#### R1′(v5 · 셋째 확인 차단 · 사용자 «가.») — 앱 폴더 줄의 출처는 «건드림» 을 만든 경로만 파일 단위로
- 결함: v4 출처 판정은 앱 폴더 주어를 폴더 tree 째(F1′) 견줘, main 이 legacy 평면 앱에 들인 마이그레이션이 그대로여도 레인이 같은 폴더의 **다른 파일**(`models.py` 메서드 · 앵커 전 README)을 고쳤으면 «worktree 수정 중» · «충돌 해소분» · «레인 커밋 수정» 으로 귀속했다(2.39.0 은 줄 자체가 가려져 통과 · 직접 실행 0). 검사기 정의(새 마이그레이션 · `apps.py` · `models.py` 를 더함)로는 레인 몫이 아니다.
- **고른 길 ⓐ(검토자 둘째 길)**: 출처 재실행 · L 증명은 v4 그대로 두고, app-container 줄의 주어 판정만 폴더 tree 대신 **그 줄을 «건드림» 으로 만든 경로마다 파일 단위 W · F1** 로 본다(`_provenance_split` 의 `touch_paths` · `classify_touch`).
  - «건드림을 만든 경로» = `checker_target.app_touch_paths(changes, 앱)` 한 곳 — 앵커에 없던 앱이면 그 아래 바뀐 경로 모두, 있던 앱이면 앵커 대비 새 `migrations/*.py`(`__init__.py` 밖) · `apps.py` · `models.py`. 검사기 `_touched_with_new_domain` 도 이 함수가 비었는지로 판정한다(건드림 정의 한 벌). 게이트는 지금 작업 트리의 앵커 대비 변경(`checker_target.anchor_changes(root, base=앵커)`)으로 그 경로를 구한다.
  - 같은 파일 판정은 `anchor_diff.PathFacts.classify` 그대로(W 는 `facts.dirty` 로 먼저 — 미추적 경로도 «worktree 수정 중»). 경로 하나라도 승인 머지의 verbatim 파일이 아니면 그 사유와 경로로 귀속 유지(«비머지 커밋 경유 … — catalog/migrations/0002_lane.py»). 경로가 비면(새 앱 폴더 자신뿐 등) v4 처럼 폴더 tree 로 가른다.
  - 고른 까닭: ① 승인 유입이 기록으로 남는다(mm-* · merge-mig 유입 1 — 처분 «유입 기록이면 더 좋음») ② 건드림 정의(`checker_target`)와 같은 파일 판정(`PathFacts.classify`)이 각각 한 출처로 남는다 ③ «줄이 머지로 들어왔다» 는 L 증명을 그대로 쓴다.
  - 버린 길 ⓑ(지금 사본 «건드림» 에서 그대로 들어온 경로를 뺌)의 비용: 게이트가 지금 사본을 돌리기 **전에** 승인 머지 · 사슬 · `PathFacts` 를 세워 «그대로 들어온 경로» 목록을 만들고, 사본 검사기에 새 변수로 넘겨야 한다(새 신뢰 표면 하나 — 사10 · S2 같은 사본 묶음이 또 필요). 그 줄이 아예 사라져 승인 유입 기록이 없다. merge-idem 은 0 이 된다(검토자 판단대로지만 2.39.0 판정을 바꿈 — 아래).
  - 크기(v4 → v5 · S2 포함): registry_gate +31 −2(두 내부 함수 · 호출 · 상수 · 머리 글) · checker_target +27 −7(`app_touch_paths` · `gate_tip(root)` · `anchor_changes` 인자) · app-container +2 −6 · idempotency +1 −1 · findings +1(주석).
- **merge-idem +승인 = 귀속 1(유입 증명 실패 · 이중 원인) — 2.39.0 과 같은 판정**: idempotency 줄은 주어가 곧 그 멱등 파일이라 v4 부터 파일 단위였다(v5 무변). L 이 서지 않는 까닭은 M^2(main)에 레인의 scope «미요청» 문서가 없어 R(M^2) 에 줄이 없기 때문이다 — 이 줄은 레인의 scope 판단과 main 이 들인 멱등 코드가 함께 만든다. 검토자는 검사기 정의(«이번 변경이 더한 멱등 산출물»)로 0 이 맞다고 본다. 0 으로 하려면 ⓑ 꼴(건드림에서 그대로 들어온 경로 빼기)이 필요하다. 이번 판은 2.39.0 판정을 지킨다(G2 에서 멈춰 사람이 scope 와 들어온 멱등 코드를 맞추는 보수 쪽). 바꾸면 §8 «푸는 것» 한 줄이다(운영자 판단).
- **S2(v5)**: `DJR_SOURCE_GIT_TIP` 은 대상이 git 이 아닐 때(게이트 사본)만 믿는다 — `checker_target.gate_tip(root)` 가 대상 `.git` 이 있으면 빈 글자(`gate_git_root` 와 같은 «대상이 git» 판정). 검사기는 `anchor_changes(qroot, root)` 로 넘긴다.

#### R1′ 장난감(`a/run5_r1.sh` · `a/run5_reg.sh` · 출력 `a/out/v5/` · 앵커 = base · legacy 평면 앱 `catalog` · main 이 `catalog/migrations/0002_upstream.py` · 승인 머지)

| 장난감 | 레인이 한 일 | 2.39.0 | v4 | **v5** | 직접 실행 |
|---|---|---|---|---|---|
| mm-wt(미커밋) | 머지 뒤 `catalog/models.py` 에 메서드 | 귀속 0 · exit 0 | 귀속 1(worktree 수정 중) · exit 2 | **귀속 0 · 유입 1 · exit 0** | 0 |
| mm-pre(커밋) | 머지 앞에 같은 고침 | 귀속 0 | 귀속 1(충돌 해소분) | **귀속 0 · 유입 1** | 0 |
| mm-post(커밋) | 머지 뒤에 같은 고침 | 귀속 0 | 귀속 1(레인 커밋 수정) | **귀속 0 · 유입 1** | 0 |
| mm-conf(커밋) | `models.py` 충돌을 두 쪽 살려 해소 | 귀속 0 | 귀속 1(충돌 해소분) | **귀속 0 · 유입 1** | 0 |
| mm-preanchor(커밋) | 앵커 전 커밋에서만 `catalog/README` | 귀속 0 | 귀속 1(충돌 해소분) | **귀속 0 · 유입 1** | 0 |
| mm-two | 승인 머지 둘(0002 · 0003) | 귀속 0 | 유입 1 | 유입 1 | 0 |
| 대조 mm-lanemig-pre(커밋) | 머지 앞에 레인 자기 마이그레이션 0002_lane | 귀속 0(놓침) | 귀속 1 | **귀속 1**(«비머지 커밋 경유 … — 0002_lane.py») | 0 |
| 대조 merge-migx(미커밋) · merge-migxc(커밋) | 승인 머지 뒤 레인이 0003_lane | 귀속 0(놓침) | 귀속 1 | **귀속 1**(«worktree 수정 중 — 0003_lane.py» · «비머지 커밋 경유 … — 0003_lane.py») | 2 · 0 |
| 대조 merge-mig +승인 | 레인이 catalog 를 안 건드림 | 귀속 0 | 유입 1 | 유입 1 | 0 |
| 대조 merge-mig · merge-newapp · mm-wt 승인 목록 없음 | | 0 | 귀속 1 | 귀속 1 | 0 |
| merge-newapp +승인 · merge-m +승인 | 새 평면 앱 · backoffice 모델을 그대로 들임 | 0 · 귀속 1 | 유입 1 | 유입 1(«파일 verbatim») | 0 · 2 |
| merge-m2 · merge-m3 +승인 | 레인이 그 주어(모델 · 마이그레이션 파일)를 작업 트리에서 고침 | 귀속 | 귀속(worktree 수정 중) | 귀속(«worktree 수정 중 — …/models.py» · «— payments/migrations/0001_initial.py») | 2 |
| merge-idem +승인 | 레인 scope «미요청» + main 멱등 파일 | 귀속 1 | 귀속 1(이중 원인) | 귀속 1(이중 원인) | 0 |
| 지난 판정 — app-* 열일곱 · idem 아홉(커밋 · 미커밋) | | | | v4 와 같음(26줄 · `a/out/v5/reg.txt`) | |

- 변이: `touch_paths` 를 빈 집합으로(폴더 단위로 되돌림) → mm-wt · mm-post 귀속 1 · 출처 재실행 `git_tip` 걷기 → mm-wt 귀속 1(이중 원인) · `gate_tip` 의 사본 묶음 걷기 → app-b · idem-new 직접 실행 `BASE=TIP=HEAD` 2 → 0(대조: v5 2 · `BASE` 만 2).
- 시험 사례(더할 것): `registry_gate_smoke.py` 에 mm-wt · mm-pre · mm-post · mm-conf · mm-preanchor(유입) · mm-lanemig-pre · merge-migx(c)(귀속) · `git_touched_smoke.py` 에 S2 대조(app-b · idem-new `BASE=TIP=HEAD` → 2).

- 규칙 목적: houserules §0-1 · 검사기 정의(«이번 작업이 건드린 기존 앱도 이주») · 게이트의 «이번 런 = 앵커부터» 그대로 → **질문 생략 · 설계 처리**.

### 시제품 결과(v3 · `a/run3_all.sh` · 2.39.0 → v3)
- a · ac: 해소 **1 → 0** · 표 `2|0` → `0|0`.
- b · **bc**: 귀속 0 → **1**(bc 는 v2 에서도 0 이던 커밋 판 — 차1 로 닫힘).
- c · **cc** · f · **fc**: 귀속 0 → **1**.
- d(대조): 그대로(`2|2` · 잔존 1).
- v4: 위 판정 모두 같음(`a/out/v4/all.txt` — R1 · R2 고침이 이 갈래를 바꾸지 않음).

### 시험 사례(더할 것)
- `registry_gate_smoke.py`: 앵커에 legacy 평면 앱 → a(무관 · 커밋 · 미커밋 둘 다 `0|0` · 해소 0) · b · f(커밋 · 미커밋 둘 다 귀속 1) · d(잔존 1). 표지 값 사례 — 비-git 대상 직접 실행에 `DJR_COMMITTED_SNAPSHOT=1` → fail-closed 그대로 · 값 = 대상 경로 → 0.
- 변이: 앵커 실행 `committed=True` 걷기 → a · b 붉음 · 지금 실행 `git_base` 걷기 → bc · fc 붉음 · `committed_snapshot` 의 경로 대조를 «값이 있으면 참» 으로 → 표지 값 사례 붉음.
- R1(v4): merge-mig +승인(귀속 0 · 유입 1) · merge-newapp +승인(유입 1) · merge-idem +승인(귀속 1 · 이중 원인) · 대조 merge-migx · merge-migxc(귀속 1) · 승인 목록 없는 merge-mig · merge-newapp(귀속 1). 변이: 출처 재실행의 `git_tip=sha`(그리고 `git_root` · `git_base`) 걷기 → merge-mig +승인 붉음(귀속 1).

---

## 3. F4-46 — ⓓ#644 진단 글의 행수가 바뀌면 legacy 가 «신규» 로 다시 뜬다

### 재현(2.39.0 · `a/out/v3/skel-table.txt`)

| 갈래 | 레인 변경 | 2.39.0 ⓓ 신규 | v2 | v3 |
|---|---|---|---|---|
| s1 | 저장소 칸(트리 93행) 230 → 223행(지움만) | **1** | 0(짝) | 0(짝) |
| m3 | 230 → 222행(지움만 · 검토자 장난감) | **1** | 0 | 0 |
| s3 | 엔티티 4 → 3(지움만) | **1** | 0 | 0 |
| m1 | 옛 메서드 30행 지우고 새 이름 메서드 22행 더함(223행) | 1 | **0(새 내용이 감수자에게서 사라짐 — 검토 중9)** | **1** |
| m2 | 엔티티 둘 지우고 새 엔티티 하나(4 → 3) | 1 | **0** | **1** |
| s2 · s4 · s5(대조) | 늘림 · 새 큰 파일 · 엔티티 늘림 | 1 | 1 | 1 |

- **재현됨**(s1). 2.39.0 의 F4-166 짝은 목록 칸(`['a', 'b']`)만 칸으로 세어(`registry_gate.py:261-286`) 이 꼴을 덮지 않는다.

### 원인
- 진단 글 안 수: `check-layer-skeleton.py:179 · 188 · 631 · 793`(#644 `{n}행`) · `check-domain-model.py:1841`(#547 ⑶ `엔티티 {len(ents)}개`). 게이트 정규화(`:253-255`)는 경로 echo 와 `:줄번호` 만 바꾼다.

### 같은 꼴의 다른 자리(정적 스캔 `a/scan_cand_msgs.py` · `out/cand-msgs.tsv` — ⓓ 방출 65곳)
- 진단 글에 수 칸이 있는 ⓓ: **#644(방출 4곳) · #547 ⑶(1곳)** — 파일 단위 주어. #153(`유스케이스 실행 {n}회`)은 줄 단위 주어라 F4-166 짝 범위와 같이 밖.
- 위반 줄(`[#N]`)에 수 칸이 있는 규칙 약 20(«한 파일 하나» 류 · `out/viol-msgs.tsv`): F4-99 · 판 B #668 결정(«고친 파일에서 일부만 걷으면 새 줄»)대로 그대로 둔다.
- 현장 사본: #644 줄 **109개** — 레인이 이 가운데 하나를 줄이기만 해도 ⓓ 신규 1.

### 고칠 방향(v3 · v4)
1. **(추천) F4-166 ⓓ 짝을 수 칸까지 넓히되 «지움만» 일 때로 좁힌다**(검토 중9).
   - `_list_shrunk(…, counts=True, narrowed=…)` 를 ⓓ 짝에서만 부른다. 주어 뒤 진단 글의 정수(낱말 · 코드 이름 안 숫자 밖 — `(?<![A-Za-z0-9_`.])\d+(?![A-Za-z0-9_.])`)를 칸으로 보고 «목록 칸 부분집합 · 수 칸 칸마다 지금 ≤ 앵커 · 나머지 글자 같음».
   - **수 칸이 다른 짝은 `_deletions_only` 가 참일 때만**: 주어 파일이 앵커 사본 대비 줄 차분에서 지움뿐(`difflib` opcodes 에 insert · replace 없음)이다. **폴더 조건(그 파일이 든 폴더 아래에 앵커에 없던 파일이 없음)은 수 칸이 폴더 구성원 수인 #547 ⑶ 에만**(`_FOLDER_COUNT_RULES = ("[ⓓ#547]",)` · `folder=` 인자 · R4) — #547 ⑶ 은 주어(루트 파일)가 그대로여도 엔티티 폴더에 새 파일이 생기면 짝이 서지 않는다(m2). #644 의 행수는 그 파일만 세므로 파일 줄 차분만 본다(같은 승격 폴더에 부품 파일을 새로 만드는 캐스케이드 고침도 짝 — skel-cas).
   - 수 칸이 같은(목록만 다른) 짝은 F4-166 그대로 — 가드 없음.
   - 위반 줄 짝(`shrunk`)은 `counts=False` 로 지금 그대로(판 B #668 · F4-99 결정과 안 부딪침).
   - 크기: registry_gate 약 +60 −15(이 항목 몫 · 대략).
2. 대조 열쇠에서 수를 뺀다 — 키운 파일도 legacy 로 숨는다.
3. 검사기 진단 글에서 행수를 뺀다 — 출력 계약 · 골든이 바뀌고 감수자가 행수를 잃는다.
- 받아들인 한계: #547 ⑶ 에서 엔티티 폴더에 새 파일이 생긴 실행은 엔티티 수를 줄였어도 2.39.0 처럼 ⓓ 신규로 남는다(보수 쪽 · 감수자 소음). #644 는 v4 에서 이 한계를 걷었다(R4).
- 규칙 목적: ⓓ 는 exit 밖 감수자 입력 · F4-166 의 «좁아진 신호는 legacy» 와 같은 결 · 새 내용이 섞인 순감은 좁아진 것이 아니다 → **질문 생략 · 설계 처리**. exit · 귀속 무변.

### 시제품 결과(v3)
- s1 · s3 · m3: ⓓ 신규 1 → **0**(«목록만 줄어 legacy 로 센 ⓓ 줄 … · 수 칸은 앵커 이하» 에 앵커 줄과 짝).
- m1 · m2: **1 그대로**(v2 의 0 을 되돌림).
- s2 · s4 · s5: 1 그대로. 모든 갈래 게이트 exit 같음.
- **v4(R4 · `a/run4_skel.sh` · 출력 `a/out/v4/skel-*`)**: 내 장난감 **skel-cas · skel-casc**(skel-s1 의 앵커 복제 · 저장소 파일 230 → 223행 지움만 + 같은 폴더에 작은 부품 파일 `order_query.py` 새로 · 미커밋 · 커밋) — 2.39.0 신규 1 · v3 신규 1(폴더 조건) → **v4 짝 · 신규 0**. **대조 m2**(#547 엔티티 둘 지우고 새 엔티티 하나) — v4 신규 **1 그대로**. s1 ~ s5 · m1 ~ m3 는 v3 = v4.

### 시험 사례 · 변이
- `registry_gate_smoke.py` `ListShrinkRegression`: s1 · m3(짝) · m1(새 내용 섞임 → 신규) · s3(짝) · m2(새 엔티티 → 신규) · s2(늘림 → 신규) · 위반 줄 수 칸 대조(고친 파일에서 하나 걷음 → 귀속 그대로).
- v4 더함: skel-cas(짝 · #644 폴더 새 파일은 막지 않음) · m2 그대로(#547 폴더 새 파일은 막음).
- 변이: `counts=True` 걷기 → s1 · s3 붉음 · `narrowed` 걷기 → m1 · m2 붉음 · `folder=any(…)` → `folder=False` → m2 붉음 · → `folder=True` → skel-cas 붉음(R4) · 위반 짝에 `counts=True` → 대조 붉음.
- 기존 변이 표 고침(검토 중4): `registry_gate_smoke.py:2496` `_BASELINE_MUTATIONS` «F4-166 ⓓ 후보 짝에 파일 무변 조건 되살림» 의 옛 글 `cand_shrunk = _list_shrunk(sorted(n_cands - l_cands), sorted(l_cands - n_cands))` 를 새 줄 `… sorted(l_cands - n_cands), counts=True,` 꼴로 맞춘다(모래상자에서 고친 표로 `--mutation-test` — §7).

---

## 4. N1 — 계약 문법 합성 줄의 가림

### 재현(2.39.0 → v3 · `a/out/v3/table.txt`)

| 갈래 | 꼴 | 2.39.0 | v2 | v3 |
|---|---|---|---|---|
| g · gc | 앵커에 모델 있는 backoffice(legacy 계약 위반) · 레인이 새 평면 앱 | 잔존(가려짐) | g 귀속 · **gc 잔존** | 귀속 1(둘 다) |
| j · jc | 앵커에도 `scope.md` · legacy 멱등 파일 · 레인이 새 멱등 파일 | 잔존(가려짐) | j 귀속 · **jc 0** | 귀속 1(둘 다) |
| merge-m | 승인 머지가 계약 위반을 그대로 들임 | 합성 줄 «레코드 없음» 귀속 유지 · exit 2(멈춤) | 승인 유입 · exit 0 | 같음(v2) |
| merge-m2 · m3(대조) | 레인이 그 주어를 작업 트리에서 고침 | exit 2 | exit 2 «worktree 수정 중» | 같음 |
| to-dup | 앵커 `api/handlers.py` 과잉매핑 핸들러 하나 · 레인이 같은 파일에 둘째(직접 실행 2줄) | 잔존 | **잔존(같은 열쇠로 뭉침 — 검토 중8)** | 귀속 1(`(같은 열쇠 2번째)`) |
| to-sep(대조) | 둘째를 다른 파일에 | 잔존 | 귀속 1 | 귀속 1 |
| cc-ign | 앵커 버킷 `application/common/` a · b · 무시 파일 generated.py 가 작업 트리에만 · 레인은 무관 변경 | 잔존 | **귀속 1(거짓 — 검토 중6)** | 잔존(같은 자리 짝 1) |
| cc-part | 레인이 버킷의 b.py 를 `framework/` 로 옮김(부분 정리) | 잔존 | 귀속 1(검토 중5) | 잔존(같은 자리 짝 1) |
| d(대조) | backoffice legacy 만 | 잔존 1 | 잔존 1 | 잔존 1 |

v4(R2 · R3 · 검토자 장난감 ch-* · cc-* 와 내 장난감 rs-* · `a/mk_rs.sh` · 출력 `a/out/v4/`):

| 갈래 | 꼴 | 2.39.0 | v3 | v4 |
|---|---|---|---|---|
| **ch-swap · ch-swapc** | choices-literal — 앵커 `shop/views.py` 의 `Order` 리터럴 legacy 를 레인이 고치고 같은 파일에 `Invoice` 리터럴을 새로 씀 | 잔존(가려짐) | **잔존**(같은 자리 짝 — R2) | **귀속 1**(글이 다름 — `Order…status` ≠ `Invoice…kind` → 짝 없음) |
| 대조 ch-add · ch-addc | 고치지 않고 더함 | 잔존(가려짐) | 귀속 1 | 귀속 1 |
| **rs-swap · rs-swapc** | response-schema-bypass — legacy `get_order` 를 고치고 같은 파일에 `cancel_order` 원시 응답을 새로 씀 | 잔존(가려짐) | 잔존 | **귀속 1** |
| **rs-move · rs-movec** | 위에 주석 넷을 넣어 `get_order@11` → `@16` 으로 밀리고 `cancel_order` 를 새로 씀 | 잔존(가려짐) | 귀속 1 · **귀속 줄이 `get_order@16`(legacy 를 가리킴 — R3)** · 짝이 `cancel_order` ↔ `get_order@11` | 귀속 1 · **귀속 줄 `cancel_order@21`** · 짝 `get_order@16` ↔ `get_order@11` |
| 대조 rs-moveonly | 줄만 밀림 | 잔존 · exit 0 | 잔존 · exit 0 | 잔존(`@<줄>` 만 다름 → 짝) · exit 0 |
| 대조 cc-part · cc-ign | 버킷 일부 정리 · 무시 파일 | 잔존 | 잔존 | **잔존 그대로**(내용 칸만 다름 → 짝) |
| 대조 cc-add · cc-addc | legacy 버킷에 새 파일 더함 | 잔존 | 잔존 | 잔존(받아들인 대로 · 2.39.0 과 같음 · 직접 실행 2) |

- 원인: 계약 문법 검사기는 `[#N]` 줄을 내지 않아 `registry_gate.py:484` 가 합성 줄 하나로 바꾼다 → 검사기 하나에 줄 하나 · exit 값 차분 · 레코드 없음. legacy 가 하나라도 있으면 새 위반이 L 의 합성 줄과 같은 글자라 늘 잔존이고, 출처 판정도 «레코드 없음».
- 같은 꼴(계약 문법으로만 줄을 내는 검사기 7): app-container · idempotency-scope-creep · choices-literal-consumption · transient-overmapping · common-container · ninja-boundary-middleware · response-schema-bypass(`check-response-schema-bypass.py:1010`). 계약 꼬리를 쓰는 셋(api-error-controller · composition-root · error-centralization)은 `[#N]` 줄이 없을 때만 같은 길.
- 덤(조정자 글과의 사이): 2.39.0 조정자 글(`commands/dddjango.md:216`)은 «잔존 절의 [진단 미파싱] fail-closed 귀속은 legacy 로 읽지 않고 측정 실패로 반송» 하라 하지만 게이트 잔존 절은 검사기별 수만 찍어(`registry_gate.py` 잔존 인쇄) 그 줄이 보이지 않는다 — 실제로는 지나간다. N1 뒤에는 레코드가 성한 계약 검사기에서 잔존 합성 줄 자체가 생기지 않는다(글은 그대로 참 — 진짜 측정 실패 몫).

### 정할 것과 답(v3 · v4)
1. **열쇠** — 줄 글자 `<검사기> :: - <where>: <msg>`(사본 경로 echo · `:줄` 정규화 = `_contract_key` · `registry_gate.py:817`)로 줄을 만들되, **비교는 줄 글자의 다중 집합으로 하고 흔들리는 칸만 다른 줄은 짝 짓는다**:
   - 같은 글자의 둘째 레코드부터 ` (같은 열쇠 N번째)` 를 붙여 집합 차분이 다중 집합 차분이 되게 한다(검토 중8 — to-dup).
   - 집합 차분 뒤 남은 귀속(N∖L) · 해소(L∖N) 계약 줄을 **같은 위반의 글자만 흔들린 것끼리** 1:1 로 짝 지어 잔존으로 센다(`_contract_pairs` · v4 R2 · R3). 대조는 **흔들리는 칸을 걷은 글이 같은가** 하나다(`_contract_stable` — 순번 꼬리 · 연산 이름의 `@<줄>` → `@N` · 횡단 버킷 `(내용: …)`). 줄 이동한 연산(rs-move `get_order@16` ↔ `@11`)과 버킷 내용 칸(cc-ign 무시 파일 · cc-part 부분 정리 · cc-add 더함)이 짝이고, 같은 글끼리라 남는 귀속 줄이 새 위반을 가리킨다(R3).
   - **글이 다르면 같은 주어 칸이어도 짝 없음** — 한 주어에 위반이 여럿 나는 검사기에서 «하나 고치고 다른 하나 더함»(ch-swap · rs-swap)은 귀속이다(R2). 짝은 legacy 절에 «같은 위반의 계약 줄이라 잔존으로 센 줄 N건» 과 앵커 줄로 찍는다.
   - **처분의 «안전한 셋은 글을 건너 짝 · 그 밖은 같은 기호일 때만» 을 넣지 않은 까닭**(처분보다 좁은 쪽): 일곱 검사기의 진단 글 꼴(아래 표)에서 흔들리는 칸을 걷으면 주어 · 위반마다 글이 하나라, 그 두 갈래가 이 대조 밖에서 새로 짝 짓는 줄이 **하나도 없다** — 안전한 셋은 주어마다 글이 하나(앱 폴더 · 멱등 파일 · 버킷 — 버킷은 내용 칸만 흔들림)이고, 기호 넷은 기호가 글 안에 그대로 있다(choices `모델.필드` · response 연산 이름 · ninja 미들웨어 이름) · transient 는 글이 늘 같아 기호가 달라도 줄이 같은 글자다(2.39.0 · v2 와 같은 «같은 열쇠» — 남는 걱정). 죽일 장난감 · 변이가 없는 갈래라 두지 않았다(시제품 v4a `a/proto-v4a/` 에 그 판을 남김 · 장난감 판정은 v4 와 같음 · `a/out/v4a/`). 뒤에 검사기가 진단 글에 다른 흔들리는 칸을 더하면 짝이 서지 않아 귀속(fail-closed)으로 드러난다.

     | 검사기 | 주어 칸 | 진단 글의 바뀌는 칸 |
     |---|---|---|
     | app-container | 앱 폴더 | 없음(평면 앱 · backoffice 글은 주어가 다름) |
     | idempotency-scope-creep | 멱등 파일 | 없음 |
     | common-container | 버킷 폴더 | `(내용: …)` |
     | choices-literal-consumption | 파일:줄 | `모델.필드`(= 기호) |
     | response-schema-bypass | 파일:줄 | 연산 이름 `이름@줄`(= 기호 · `@줄` 은 흔들림) |
     | ninja-boundary-middleware | settings 파일 | 미들웨어 이름(= 기호) |
     | transient-overmapping | 파일:줄 | 없음(기호 `이름()` 은 글에 없음) |
   - 받아들인 것(«새로 막지 않는 것»): legacy 버킷에 새 파일을 더한 꼴(cc-add · 같은 자리 · 버킷 하나에 줄 하나라 수 그대로)은 잔존 — 직접 실행은 막는데 게이트는 통과(2.39.0 과 같음). choices-literal 에서 같은 파일 · 같은 `모델.필드` 리터럴 하나를 고치고 다른 줄에 하나 더한 꼴 · transient-overmapping 에서 같은 파일 핸들러 하나를 고치고 하나 더한 꼴은 줄 글자가 같아(`:N` 정규화) 처음부터 L∩N 이다 — `[#N]` 줄과 같은 결 · 2.39.0 과 같음(위반 수 그대로).
2. **앵커 쪽 레코드가 없을 때** — 그 검사기는 두 벌 모두 합성 줄(`_harmonize_contract` · 2.39.0 exit 차분).
3. **레코드 없는 옛 꼴과의 호환** — 계약 줄은 «exit 2 · `[#N]` 0 줄 · 그 검사기의 `rule=null` 레코드가 모두 `contract_ref` · 센티널 없음 · 레코드마다 `line_of_record` 가 원 출력에 그대로» 일 때만(`_contract_lines`). 하나라도 어긋나면 합성 줄. **레코드 채널이 끊긴 실행도 합성 줄**(v4 R6 — 원 출력에 `구조화 레코드 채널 비활성` · `[분석]` 이 있거나 게이트가 그 검사기를 `unclassifiable` 로 셈) — 쓰기 실패로 레코드가 일부만 남으면 «레코드 ⊆ 출력» 은 서도 레코드 없는 출력 줄이 차분에서 사라지기 때문이다. 다른 쪽은 `_harmonize_contract` 가 합성 줄로 맞춘다.
4. **출처 재실행** — 승인 머지 사본 재실행에 sink(계약 줄을 잴 수 있게)와 원본 루트 · 앵커 · 그 커밋(v4 R1 · §2)을 준다. 순번 줄(`2번째`)은 대응 레코드 글자와 달라 출처 · 자매 판정에서 «대응 레코드 없음» 으로 귀속 유지(fail-closed · 드묾).
5. **sidecar** — 계약 줄 레코드가 `introduced.json` `records` 에 실린다(재생성 루프는 `rule=null` 을 버려 주입 무변 · `contract.json` 무변 · pre-gate 안정 ID 는 `[#N]` 없는 줄 대체로 섬). 순번 줄은 `unmatched_lines`.

### 그래프 글 — R-3617 새 Expression(검토 중3)
- 자리: `ontology/rules/command-dddjango.ttl` 블록 `s007/b60`(R-3617 · `commands/dddjango.md:176` · Codex `codex-dddjango/skills/dddjango/SKILL.md:195`). 지금 글 «`registry_gate`의 판정 차분 집합은 숫자 규칙 줄과 pre-scan만이다. 정상 측정된 신규 `rule=null` 계약 레코드는 별도로 `- <경로>: …`의 주어 칸을 읽어 자매 보고 절에 싣고 `contract.json`에서 제외하며, 서버 계약과 legacy 계약은 보존한다.» 는 N1 뒤 틀린다.
- 새 문장 초안(그 두 문장 자리):
  > `registry_gate`의 판정 차분 집합은 숫자 규칙 줄 · pre-scan · 계약 줄이다. 계약 줄은 `[#N]` 줄 없이 exit 2 인 검사기의 `rule=null` 계약 레코드(센티널 없음 · 원 출력과 같은 줄 · 레코드 채널이 성함)마다 `- <경로>: …` 한 줄이다. 앵커에 없던 계약 줄은 연산 이름의 줄 번호 · 버킷 내용 칸만 다른 앵커 줄과 1:1 로 짝 지은 몫을 빼고 귀속이며, 글이 다르면 같은 주어 칸이어도 귀속이다. 한쪽이 `[진단 미파싱 …]` 합성 줄이면(exit ≠ 0 인데 계약 레코드가 성하지 않으면) 그 검사기는 두 쪽 모두 합성 줄로 잰다. 정상 측정된 신규 계약 줄은 `- <경로>: …`의 주어 칸을 읽어 자매 보고 절에 싣고 `contract.json`에서 제외하며, 서버 계약과 legacy 계약은 보존한다.
- 뒤 문장(«… `[진단 미파싱 …]`·`(target)` 주어(#74)·경로 없는 합성 줄은 남긴다.»)은 그대로. prefLabel(«정상 측정된 dddjango-web 소유 주어는 …»)은 그대로 — G12 라벨 드리프트 무변(확인은 §10).
- revisionKind = amendment(판정 차분 집합이 넓어짐) · 새 Expression `<djr#R-3617@2026-11-16>`(revision 4 · `prov:wasRevisionOf <…R-3617@2026-10-13>`).

### 선택지
1. **(추천) 위 1 ~ 5 + R-3617 개정** — 비용 M(registry_gate N1 몫 약 +130 −4 · 그래프 글 한 블록).
2. 계약 문법 검사기를 `[#N]` 줄로 바꾼다 — 검사기 일곱의 출력 계약 · 골든 · 규칙 소유 지도가 바뀐다 · 크다.
3. 그대로 두고 한계로 적는다 — F4-28 의 b · f 가 backoffice legacy 저장소에서 다시 가려진다(g).
- 규칙 목적: 게이트의 귀속 정의(«이번 런이 위반을 늘렸나») 그대로를 계약 검사기에도 · 열쇠는 이미 있는 `_contract_key` · 수로 견줌 → **질문 생략 · 설계 처리**(그래프 글은 이 결정을 옮겨 적는 개정).

### 단위 대조(`a/n1_unit.py` 18/18)
- v2 의 8(레코드 없음 · 센티널 · 출력에 없음 · 남의 레코드 → 합성 · 한쪽 합성 → 둘 다 합성 · 둘 다 계약 → 새 줄만) + v3 넷: 같은 열쇠 둘 → 순번 줄 · 같은 자리 글자만 바뀜 → 짝(다른 자리 새 줄은 귀속) · 같은 자리 수가 늘면 귀속 · `_deletions_only`.
- v4 여섯(고침마다 대조 함께): `_deletions_only` 폴더 새 파일 — `folder=True`(#547 꼴) 거짓 / **대조** 기본(#644 꼴) 참(R4) · choices 같은 주어 칸 다른 위반 → 짝 없음 / **대조** 버킷 내용 칸만 다름 → 짝(R2) · response 줄 이동 + 새 연산(새 연산이 정렬 앞) → 같은 연산끼리 짝 · 새 연산 귀속(R3) · response 고치고 더함 → 짝 없음 · 채널 끊김(레코드 하나만 · 경고 · `_run_checker` 대역) → 합성 줄 / **대조** 채널 성함 → 계약 줄 둘(R6).

### 시험 사례 · 변이
- `registry_gate_smoke.py`: g · gc · j · jc · merge-m · m2 · d · to-dup · to-sep · cc-ign · cc-part 와 대역 사례 «앵커 합성 · 지금 계약 → 잔존» · «자매 경로 계약 줄 → 자매 절». v4 더함: ch-swap · ch-add · rs-swap · rs-move(귀속 줄 글이 `cancel_order` 인지 단언) · rs-moveonly · cc-add(잔존) · 채널 끊김 대역(합성 줄).
- 변이: `_contract_lines` 늘 None → g · j · merge-m 붉음 · `_harmonize_contract` 걷기 → 대역 사례 붉음 · 순번 걷기 → to-dup 붉음 · `_contract_pairs` 걷기 → cc-ign · cc-part 붉음 · 출처 재실행 sink 걷기 → merge-m 붉음 · v4: 짝 대조를 «같은 주어 칸» 으로 넓힘(v3 꼴) → ch-swap · rs-swap 붉음 · 내용 칸 정규화 걷기 → cc-ign · cc-part · cc-add 붉음 · `@<줄>` 정규화 걷기 → rs-move · rs-moveonly 붉음 · `and not broken` 걷기 → 채널 끊김 대역 붉음.
- `registry_gate_smoke` R1 · R2(옛 직렬 게이트 `86fc3c24` byte 대조)는 N1 의 설계된 출력 변화로 어긋난다 — §7 · §10 의 덧대기(조건 둘).

---

## 5. N2 — 첫 `migrations/` 폴더를 «건드림» 으로 못 봄

### 재현 · 원인
- 장난감 e(앵커의 legacy 평면 앱 `catalog/` 에 `migrations/` 없음 · 레인이 `migrations/0001_initial.py` 를 처음 더함): 작업 트리 직접 실행 **exit 0**(2.39.0 · v1).
- `check-app-container.py:143-153` `_porcelain` 이 `--untracked-files=all` 없이 불러 미추적 폴더가 `?? catalog/migrations/` 한 줄로 접히고 `:183-185` «새 마이그레이션 파일» 판정에 안 걸린다.

### 선택지
1. **(추천) 두 길로 나눈다**:
   - 게이트 지금 사본(v3 의 앵커 대비 길): `anchor_changes` 가 `status --untracked-files=all` 로 미추적을 파일마다 펴고 «앱 폴더가 앵커 트리에 없음» 으로 새 앱을 따로 가르므로 접힘 문제가 없다(§2).
   - 직접 실행(변수 없음 · HEAD 대비 porcelain): 접힌 `?? <앱>/migrations/` 줄이면 그 폴더에서 `__init__.py` 밖 `.py` 를 디스크로 센다(+5).
2. 직접 실행 쪽 `_porcelain` 에 `--untracked-files=all`(지시의 방향) — 접힌 `?? payments/` 가 파일 줄로 풀려 «앱 폴더 전체가 새것» 판정이 서지 않아, `models/` 꾸러미만 있는 새 앱(f)을 놓친다(변형 `a/alt-uall/` 직접 실행 e 0 → 2 · **f 2 → 0** · 검토 다시 돎).
3. 그대로 — 다른 검사기(#336)가 잡는 경우가 많으나 app-container 정의와 어긋난 채 남는다.
- 규칙 목적: 검사기 머리 G2 «`D/migrations/` 아래 신규 마이그레이션 파일» 그대로 → **질문 생략 · 설계 처리**.

### F4-28 과 함께 놓았을 때(v3)
- e · **ec**: 직접 실행 e 0 → **2** · ec 0(커밋 판 직접 실행은 HEAD 대비라 그대로) · 게이트 `2|0`(거짓 해소) → `0|2` · 귀속 1(둘 다).
- f · fc: 게이트 귀속(둘 다). 새 상위 폴더 안 새 앱(`newparent` · `newparentc` — porcelain 이 `?? services/payments/` 로 접음): 귀속(둘 다).

### 시험 사례 · 변이
- `git_touched_smoke.py`(직접 실행): e(첫 `migrations/` → 2) · f(새 앱 `models/` 만 → 2 — `-uall` 변이를 죽임) · 대조(첫 `migrations/` 에 `__init__.py` 만 → 0).
- `registry_gate_smoke.py`: e · ec · newparentc 를 게이트로(귀속 1).
- 변이: 접힌 폴더 판정 걷기 → e 붉음 · `-uall` 로 바꾸기 → f 붉음.

---

## 6. N3 — 문서 입력 비대칭(앵커에 없는 실행 문서 · 지금 사본만 작업 트리 문서)

### 같은 꼴을 쓰는 검사기 세기
- 실행 문서(`.dddjango/<폴더>/scope.md` · `design-spec.md`)를 읽는 검사기는 27 가운데 **`check-idempotency-scope-creep` 하나**(`:180-210`). 다른 검사기는 `.dddjango` 를 건너뛰거나 숨김 경로라 두 사본 모두에서 빠진다. `folder_group` 의 `refactor-scope.md` 는 `--run <원본 폴더>` 로 받아 대칭.

### 재현 · 원인
- i · ic(앵커에 `scope.md` 없음 · 지금 작업 트리에 «멱등성 미요청» · legacy 멱등 그대로): 직접 실행 0 · 게이트 합성 줄 **거짓 귀속 1**.
- k(앵커에도 scope · 레인이 legacy 멱등 파일을 고침): 직접 실행 2 · 게이트 잔존 — **놓친 막힘**(게이트 exit 0). kc(커밋 판): 직접 0 · 게이트 0.
- idem-new · idem-newc(앵커: scope 미요청 · 멱등 산출물 없음 → 레인이 새 멱등 파일): 2.39.0 은 둘 다 합성 줄 귀속(막음).
- 원인: 두 사본 모두 비-git 이라 `:136-154` `_is_new_or_modified` 가 «모든 파일 건드림» → 멱등 판정이 문서 유무로만 갈린다(i) · 문서가 둘 다에 있으면 legacy 가 두 쪽 다 잡혀 건드린 것이 가려진다(k).
- v2 의 구멍(검토 차1): v2 는 지금 사본 «건드림» 을 원본 루트의 HEAD 대비(`ls-files` · `diff HEAD`)로 물어, 커밋하는 실행에서 새 멱등 파일을 놓쳤다(idem-newc v2 귀속 0 · 2.39.0 은 막음).

### 선택지(v3)
1. **(추천) app-container 와 같은 게이트 git 문맥 · 앵커 대비** — 앵커 사본은 커밋 트리 표지면 «건드린 것 없음», 지금 사본은 `anchor_changes().touched`(앵커 대비 바뀐 경로 ∪ 미추적 · 커밋 · 미커밋 같음). 변수가 없으면 지금 그대로(HEAD 대비). 크기 +15 −5(판정은 `checker_target` 한 곳).
2. 문서 입력 대칭(앵커 사본에 작업 트리 문서를 넣음) + 두 쪽 fail-closed 유지 — 2.39.0 이 막던 것을 잃지 않지만 k 는 2.39.0 처럼 놓침 · 앵커 사본의 뜻을 바꿈 → 차선.
- 규칙 목적: 검사기 정의(«이번 변경에서 touched 된 멱등성 산출물») · 게이트 = 직접 실행(앵커부터) → **질문 생략 · 설계 처리**.

### 2.39.0 대비 · 시제품 결과(v3)
- i · ic: 거짓 귀속 1 → **0**(표 `0|0`) — 풂.
- k · **kc**: 놓침 → **귀속 1**(둘 다) — 새로 막음(직접 실행 k 2 와 같음 · kc 는 직접 실행 0 이지만 앵커 대비로는 레인이 고친 파일).
- idem-new · **idem-newc**: 귀속 1(둘 다 · 계약 줄) — 2.39.0 과 같은 판정(v2 의 idem-newc 구멍 닫힘).
- j · jc: 귀속 1(§4). l(대조): `0|0`.
- v4: 위 판정 모두 같음(`a/out/v4/all.txt` · `pair.txt` — 짝 단순화 뒤 다시 돎).

### 시험 사례 · 변이
- `registry_gate_smoke.py`: i · ic · k · kc · l · idem-new · idem-newc. 변이: `gate_base` 길 걷기(HEAD 대비로 되돌림) → kc · idem-newc 붉음 · 커밋 트리 표지 걷기 → l 붉음.

---

## 7. 기존 시험(모래상자 `a/repo-v2` · v5 여섯 파일 · 기본 TMPDIR · `a/run_suite.sh` · `a/run_post4.sh` · 출력 `a/out/v5/suite-repo-v2-*.txt` · 기록 `a/out/v5/suite-v5.log` · `post.log` · 11-16 16:16 ~ 16:54)

| 도구 | v5 결과(마지막 실행) |
|---|---|
| `fixture_matrix` · `checker_baseline_matrix` · `findings_count_matrix` | exit 0 |
| `checker_cross_matrix` | exit 0 · census 349 · EXPECTED 차이 0 |
| `findings_smoke` · `construct_drift_report` · `git_touched_smoke` | exit 0(15/15 · 8/8 · 90/90) |
| `anchor_diff_smoke` | exit 0 · 142 OK · 표 14/14(대역 `fake` 서명에 `committed` · `git_base` · `git_tip` 더한 모래상자 사본) |
| `registry_gate_smoke` | unittest **66 OK**(대역 `run` 서명 고친 사본) · 표 **45 가운데 불일치 5**(R1 넷 · R2 — N1 몫 · v3 · v4 와 같음) |
| `registry_gate_smoke --mutation-test` | exit 0 — 게이트 채널 변이(`_MUTATIONS`) 11 · 이름 붙은 기준선 · 귀속 변이(`_BASELINE_MUTATIONS`) 16 모두 붉음(변이 표 «F4-166 ⓓ 후보 짝» 옛 글을 새 호출 꼴로 고친 사본 · 검토 중4) |
| `field_report_checker_smoke` · `pregate_transcription_smoke` · `pregate_field_report_smoke` | 172 OK · 69 OK · 89 OK |
| `pregate_fixture_run` | PASS |
| `gen_pregate_symbol_kinds --check` | red — `pregate_symbol_kinds.json` 재생성 필요(설계대로 · 세 검사기 · `checker_target` sha) |

- 대역 서명: F4-28(`committed`) · 차1(`git_base`) · R1(`git_tip`) 세 인자 — `registry_gate_smoke.py` `SisterGateRegression.measure` 의 `run(...)` · `anchor_diff_smoke.py:3106` `fake(...)`. 고치지 않으면 TypeError(v2 에서 22 · 1 오류로 확인).
- R1 · R2 불일치 5 는 N1 의 설계된 출력 변화다(`a/r1_diff.py` · 기본 TMPDIR · `a/out/v5/r1-diff.txt`): choices-literal 합성 줄 1 → 계약 줄 3 · response-schema-bypass 합성 줄 1 → 계약 줄 `get_order@11` 1(귀속) · 귀속 493 → 495 · introduced 레코드 493 → 497 · 대응 없는 귀속 줄 2 → 0. 처리는 §10(직렬 사본 덧대기 · 조건 둘).
- 바로잡음(S1): v4 초안의 수치(492 → 494 · 496 · 1 → 0)와 «response-schema-bypass 는 두 판 모두 잔존» 은 내 하네스가 TMPDIR 를 dddjango 작업 트리 안(`a/tmp`)에 두어 생긴 값이었다 — 사본이 git 작업 트리 안에 생기면 사본 안 git 질의가 바깥 저장소에 닿아 response-schema-bypass 앵커 쪽 판정이 바뀐다. 하네스에서 그 TMPDIR 를 걷고 기본 자리로 다시 돌았다(위 값 = 검토자 기본 TMPDIR 값과 같음). 변이 · kinds 결과는 두 자리에서 같다.
- 모래상자 `a/repo-v2` 는 v5 여섯 파일 · 고친 시험 사본(대역 둘 · 변이 표 한 줄)을 담은 채 남겼다(구현자가 다시 돌릴 수 있게).

---

## 8. 새로 막는 것 · 푸는 것(2.39.0 대비 · v5 · 장난감 게이트 판정 · 커밋 · 미커밋 두 판)

- v3 행은 v4 · v5 에서 같다(검토자 장난감 38줄 `a/out/v4/all.txt` v3 = v4 · 건드림 판정을 쓰는 app-* 열일곱 · idem 아홉 `a/out/v5/reg.txt` v4 = v5). v4 에서 바뀌거나 더한 행은 표 끝 넷, v5 에서 더한 행은 끝 둘.

| 장난감 | 꼴 | 2.39.0 게이트 | v5 게이트 | 직접 실행(v5 · 변수 없음) | 몫 |
|---|---|---|---|---|---|
| b · bc | legacy 평면 앱에 새 마이그레이션 | **exit 0**(놓침) | 귀속 · exit 2 | b 2 · bc 0 | F4-28 · 차1 |
| f · fc | 새 평면 앱(`models/` 꾸러미만) | **exit 0**(놓침) | 귀속 · exit 2 | f 2 · fc 0 | F4-28 · 차1 |
| k · kc | 앵커에도 scope · legacy 멱등 파일을 고침 | **exit 0**(놓침) | 귀속 · exit 2 | k 2 · kc 0 | N3 · 차1 |
| c · cc · e · ec · g · gc · j · jc · newparent · newparentc | 새 평면 앱 · 첫 `migrations/` · backoffice legacy + 새 앱 · 새 멱등 파일 · 새 상위 폴더 안 새 앱 | exit 2(다른 검사기 몫으로만 붉음 · 해당 검사기 줄은 가려짐) | 해당 검사기 줄도 귀속 | v3 직접 실행: 미커밋 2 · 커밋 0(gc 는 backoffice 줄로 늘 2) | F4-28 · N1 · N2 · 차1 |
| to-dup | 같은 파일에 둘째 과잉매핑 핸들러 | 잔존(가려짐 · 게이트 붉음은 다른 몫) | 귀속(순번 줄) | 2 | N1(중8) |
| **ch-reg** | 앵커에 choices 리터럴 legacy · 레인이 `kind` 에 choices 만 더함 → 건드리지 않은 `report.py` 의 `filter(kind="x")` 가 새 위반 | 잔존 · **exit 0** | **귀속 · exit 2** | **0** | N1(중7) |
| ch-nolegacy(대조) | 같은 꼴 · 앵커에 legacy 없음(`--anchor HEAD`) | 합성 줄 귀속 · exit 2 | 계약 줄 귀속 · exit 2 | 0 | — |
| i · ic | 앵커에 scope 없음 · legacy 멱등 그대로 | 합성 줄 거짓 귀속 | 0 | 0 | N3(풂) |
| merge-m | 승인 머지가 계약 위반을 그대로 들임 | 귀속 유지 · exit 2(멈춤) | 승인 유입 · exit 0 | 2 | N1(풂) |
| cc-ign · cc-part | 무시 파일이 버킷 내용 칸을 바꿈 · 버킷 일부 정리 | 잔존 | 잔존(내용 칸만 다른 짝) | 2 | N1(v2 의 거짓 귀속 · 새 막힘 거둠) |
| a · ac · l | 무관 변경 | 거짓 해소 1 · legacy 잔존 | 0 | 0 | F4-28 · N3(보고만) |
| **merge-mig · merge-newapp(승인 목록 없음)** | main 머지가 legacy 평면 앱에 마이그레이션 · 새 평면 앱을 들임 · `--approved-merge-file` 없음 | 0(가려짐) | **귀속 · exit 2** | 0 | F4-28 · 차1(R1 — 게이트의 «미승인 머지 = 레인 편집» 정책) |
| merge-mig +승인 | 같은 머지를 승인 목록으로 | 0(가려짐 · 거짓 해소) | 승인 유입 1(기록 · exit 제외) | 0 | R1 |
| merge-migx · merge-migxc +승인 | 승인 머지 뒤 레인이 그 legacy 앱에 마이그레이션을 더함 | 0(가려짐) | **귀속 · exit 2** | migx 2 · migxc 0 | F4-28 · 차1 · R1 대조 |
| ch-swap · ch-swapc · rs-swap · rs-swapc · rs-move(c) | 한 주어에 위반이 여럿 나는 계약 검사기에서 legacy 하나를 고치고(또는 밀고) 새 위반을 더함 | 잔존(가려짐) | **귀속 · exit 2** | 미커밋 2 · 커밋 0 | N1 · R2 · R3 |
| mm-wt · mm-pre · mm-post · mm-conf · mm-preanchor +승인(v5) | 승인 머지가 legacy 평면 앱에 마이그레이션을 그대로 들였고 레인은 같은 폴더의 다른 파일만 고침(미커밋 · 커밋) | 귀속 0(가려짐 · mm-wt exit 0) | **귀속 0 · 승인 유입 1**(mm-wt exit 0) | 0 | R1′(v4 의 거짓 귀속을 거둠 · 2.39.0 과 같은 판정 + 유입 기록) |
| mm-lanemig-pre(v5) | 승인 머지 앞에 레인이 그 앱에 자기 마이그레이션을 커밋 | 귀속 0(놓침) | **귀속 · exit 2** | 0 | F4-28 · 차1 · R1′ 대조 |

- **의도한 새 붉음**:
  - b · bc · f · fc · k · kc — 게이트가 «앵커부터의 변경» 으로 직접 실행 정의를 따른다(커밋 판 직접 실행 0 은 사용자 직접 실행의 HEAD 기준이 그대로라서다).
  - **ch-reg(직접 실행 0 · 게이트만 붉음 — 검토 중7)**: 게이트 안 fail-closed 검사기(choices-literal · transient-overmapping)는 두 사본 모두 «전 파일 건드림» 이라, 레인 변경(choices 를 더함)이 만든 다른 파일의 새 줄이 귀속된다. 같은 검사기에 legacy 가 없는 저장소에서는 2.39.0 도 같은 줄을 귀속한다(ch-nolegacy) — 게이트 뜻(«위반을 늘렸나»)과 맞고 2.39.0 의 legacy 없는 판정과 같다. **의도로 둔다**(계획 «새로 막는 것» 에 적음).
  - **승인 목록 없이 main 머지가 들인 평면 앱 · 마이그레이션 · 멱등 파일(merge-newapp · merge-mig · merge-idem 승인 없음)** — 게이트의 «미승인 머지 = 레인 편집» 정책대로 귀속이다(R1 처분 · 계획 «새로 막는 것» 에 적음). merge-idem 은 2.39.0 도 귀속. 승인 목록이 있으면 merge-mig · merge-newapp 은 «승인 유입» 기록이고 merge-idem 은 이중 원인이라 귀속(2.39.0 과 같은 판정).
- **새로 막지 않는 것(받아들임)**: legacy 계약 버킷에 새 파일을 더함(cc-add — **직접 실행은 막는데 게이트는 통과** · 2.39.0 과 같음) · choices-literal 같은 파일 같은 `모델.필드` 리터럴 · transient-overmapping 같은 파일 핸들러의 «하나 고치고 하나 더함»(줄 글자가 같아 L∩N — `[#N]` 줄의 `:N` 정규화와 같은 결 · 2.39.0 과 같음) · #547 ⑶ 엔티티 폴더에 새 파일이 생긴 실행의 줄이기(§3 한계).
- **v5 R1′ — 막지 않는 것(2.39.0 과 같게 되돌림)**: 승인 머지가 legacy 평면 앱에 그대로 들인 마이그레이션은, 레인이 같은 폴더의 다른 파일을 고쳤어도(mm-wt · mm-pre · mm-post · mm-conf · mm-preanchor · 커밋 · 미커밋) 승인 유입이다 — v4 가 새로 막던 것을 거둔다(2.39.0 도 통과 · v5 는 유입 기록이 더 있음). 레인이 그 앱에 자기 마이그레이션 · `apps.py` · `models.py` 를 더했으면(mm-lanemig-pre · merge-migx · merge-migxc) 귀속 — 2.39.0 이 놓치던 것을 막는다(F4-28 몫 · «새로 막는 것»).
- **merge-idem +승인**: v5 도 귀속(이중 원인) — 2.39.0 과 같아 «푸는 것» 아님(까닭 §2 «R1′»).
- 현장 영향은 §9.

---

## 9. 현장 사본 차이(리허설 클론 · 읽기만 · 절대 경로로 넘김)

- **v5**: 현장은 다시 돌지 않았다 — v5 의 바뀜은 승인 머지 목록이 있는 실행의 앱 폴더 줄 출처 판정과 게이트 밖 TIP 묶음뿐이다. v4 현장 실행 셋(HEAD · HEAD~10 · 승인 머지 복제 fieldclone4)에서 app-container 줄이 출처 판정까지 간 일이 없어(귀속 0 · 승인 유입 줄은 #493 둘) 판정이 바뀔 자리가 없고, 기계 부하가 커서(한 실행 20 ~ 30분) 생략했다. app-* · idem 장난감 26줄 v4 = v5 로 건드림 판정 무변을 대신 보였다.

- **v4(11-16 12:43 ~ 15:00 · `a/run_field_v4.sh` · 출력 `a/out/v4/field*` · 기계 부하가 높아 한 실행 20 ~ 30분)**:
  - 원본 클론 `--anchor HEAD`: v4 출력 = v3 출력(다른 줄은 툴체인 줄 하나) — 배포판(v1 때 같은 앵커 실행 `a/out/field-gate-rel.txt`) `check-app-container.py | 2 | 0` · 해소 1 → `0 | 0` · 해소 0 · 귀속 0 · 잔존 2207 · ⓓ 신규 0.
  - 원본 클론 `--anchor HEAD~10`: v4 = v3(툴체인 줄 · 끊은 실행의 임시 사본을 다음 게이트가 지운 «정리» 한 줄만 다름).
  - **내 복제 `fieldclone4`(승인 머지 꼴 · R1 현장 확인)**: `--shared` 복제에서 앵커 = HEAD~30(그 사이 103 파일 바뀜) 에 레인 커밋 하나(트리 93행 legacy 파일의 빈 줄 둘 지움) + main(HEAD)을 `--no-ff` 머지 · 그 머지를 승인 목록으로. 배포판 · v3 · v4 모두 귀속 0 · **승인 유입 2**(main 이 들인 #493 줄 둘 · L 증명 · 파일 verbatim) · 잔존 2205 · ⓓ 신규 8 · green. 차이는 배포판 표 `2 | 0` · 해소 4 → v3 · v4 `0 | 0` · 해소 3(F4-28 거짓 해소 하나). v3 ↔ v4 출력 차이 0(툴체인 줄만) — 이 구간의 main 변경은 legacy 평면 앱 · 멱등 파일을 건드리지 않아 R1 꼴은 현장 수치로 보이지 않는다(장난감 merge-mig 로만). 복제는 다 쓴 뒤 지움.

- **원본 클론 `--anchor HEAD`**(작업 트리 변경은 숨김 경로뿐 → 앵커 · 지금 내용 같음 · 차이는 측정 방식 몫): 배포판 exit 0 · 표 `check-app-container.py | 2 | 0` · 잔존 2207 · **해소 1** · ⓓ 신규 0 · legacy 3346 → v1 · v2 · v3 모두 `0 | 0` · **해소 0**(차이 줄은 이 둘). v3 출력은 v2 출력과 같다(sidecar 줄만 다름 · `a/out/v3/field-head-v3.txt`).
- **원본 클론 `--anchor HEAD~10`**(앵커가 HEAD 보다 앞 · 실제 커밋 이력 · 그 사이 바뀐 파일 1): 배포판 exit 0 · 표 `check-app-container.py | 2 | 0` · 해소 **1** · 잔존 2207 · ⓓ 신규 0 → v3 exit 0 · `0 | 0` · 해소 **0** — 차이 줄은 이 둘(`a/out/v3/field-h10-{rel,v3}.txt`).
- **내 복제 `fieldclone3`**(`--shared` · 다 쓴 뒤 지움 · 트리 93행 legacy 파일 266 → 264행 + 현장 legacy 평면 앱 둘에 첫 `migrations/0001_initial.py` — **모두 커밋** · 앵커 = 원본 HEAD · 작업 트리 깨끗): 배포판 exit 2(#336 · #414 새 줄로 이미 붉음) · 귀속 2 · 자매 1 · 표 `2 | 0` · 해소 1(거짓) · **ⓓ 신규 2**(264행 줄 포함) · legacy 3345 → v3 exit 2 · **귀속 3**(+ 서버 쪽 평면 앱 계약 줄 — 커밋했어도 앵커 대비로 건드림 · 차1) · **자매 2**(+ web 쪽 평면 앱 계약 줄) · 표 `0 | 2` · 해소 0 · **ⓓ 신규 1**(264행은 앵커 266행과 짝 — 커밋한 지움만) · legacy 3346. 판정은 두 판 모두 붉음(무변 · `a/out/v3/fieldclone3-{rel,v3}.txt`).
- v1 · v2 복제(`fieldclone` · `fieldclone2` · 모두 지움)의 미커밋 꼴 수치: v1 — F4-46 ⓓ 신규 1 → 0 · 해소 1 → 0 · v2 — 첫 `migrations/` 둘에서 서버 앱 계약 줄 귀속 1 · web 앱 계약 줄 자매 1 · 판정 무변(#336 · #414 로 이미 붉음).
- fail-closed 에서 잡히는 현장 legacy 평면 앱 2 · #644 줄 109 · 추적 jsonl 286 · 미추적 48(이름 · 경로는 `a/field-notes.md` 와 `a/out/field*` 원 출력에만).

---

## 10. 구현 때 — 합본(DEVELOPMENT §3 체크리스트)

### 검사기 · 도구(체크리스트 8)
- 바뀌는 파일(+ Codex byte 미러 여섯): `findings.py`(F4-27 · 상수 넷 — `ENV_COMMITTED_SNAPSHOT` · `ENV_GIT_BASE` · `ENV_GIT_TIP` 과 F4-27 몫) · `anchor_diff.py`(F4-27) · `registry_gate.py`(F4-28 · F4-46 · N1 · 차1 · R1 ~ R6 · R1′) · `check-app-container.py`(F4-28 · N2 · 차1) · `check-idempotency-scope-creep.py`(N3 · 차1) · `checker_target.py`(게이트 git 문맥 한 곳 · R1 끝 커밋 · R7 머리 글 · R1′ 건드림 경로 `app_touch_paths` · S2 끝 커밋 사본 묶음). rel → v5: registry_gate +244 −25 · checker_target +142 · app-container +20 −14 · idempotency +15 −5 · findings +17 −5 · anchor_diff +1(v4 → v5: registry_gate +31 −2 · checker_target +27 −7 · app-container +2 −6 · idempotency +1 −1 · findings +1).
- 시험 고침:
  - 대역 서명 둘에 `committed=False, git_base=None, git_tip=None`(v5 무변)(`registry_gate_smoke.py` `SisterGateRegression.measure` 의 `run(...)` · `anchor_diff_smoke.py:3106` `fake(...)` — v4 에서 `git_tip` 더함).
  - `_BASELINE_MUTATIONS` «F4-166 ⓓ 후보 짝에 파일 무변 조건 되살림» 의 옛 글을 새 호출 꼴로(검토 중4 · §3).
  - R1 · R2 직렬 대조 — 직렬 사본(`86fc3c24` 게이트)에 같은 변경을 시험 시점에 덧댄다. 덧대는 자리 셋: 옛 `:297` 합성 줄 자리 → 계약 줄(같은 열쇠 순번 포함) · 앵커 · 지금 두 벌 뒤(`:806` · `:810` 다음) `_harmonize_contract` · `:813-815` 집합 차분 뒤 `_contract_pairs`. 조건 둘(검토 사11): ① 직렬 사본은 병렬 쪽 검사기별 `.part` 가 아니라 **직렬 sink 를 검사기 이름(`rec["checker"]`)으로 걸러** 레코드를 얻는다(두 쪽이 같은 조각 코드를 쓰면 조각 대응 결함이 숨는다) ② 덧댄 자리마다 옛 글이 **정확히 한 번** 바뀌었는지 단언한다(못 바뀌면 시험 오류). 이 길이 크면 시험 머리 유지 규칙대로 «R 을 워커 1 대조로 낮춤» 을 커밋 메시지에 적는다(사용자 결정 아님).
  - 새 사례 · 변이: §2 ~ §6 «시험 사례». 장난감을 시험 픽스처로 옮길 때 지은 이름 그대로(`catalog` · `payments` · `shop` · `orders` · `get_order` · `cancel_order`).
  - **변이 표 초안(새 판정마다 죽일 변이 하나 이상 · `registry_gate_smoke.py` 의 `_MUTATIONS`(게이트 채널 변이) 또는 이름 붙은 기준선 · 귀속 변이 `_BASELINE_MUTATIONS` 에 더함 · 처분 «새 판정을 죽이는 변이» · S3)**:

    | 이름(초안) | 파일 · 바꿀 글 | 죽이는 사례 | 시제품에서 돌려 봄(v4 열한 · v5 셋 — `a/mk_mut4.py` · `a/run_mut4.sh` · `a/out/v4/mut.txt` · `a/out/v5/mut-*`) |
    |---|---|---|---|
    | N1 계약 줄 순번 걷기 | registry_gate `_contract_lines` 의 `out.add(key if seen[key] == 1 else f"{key}{_CONTRACT_NTH…}")` → `out.add(key)` | to-dup | 귀속 1 → **0** · 단위 BAD 1 |
    | R2 짝을 같은 주어 칸으로 넓힘(v3 꼴) | `_contract_stable` 의 반환을 주어 칸(`… .split(": ", 1)[0]`)으로 | ch-swap · rs-swap · rs-move | ch-swap 귀속 1 → **0** · rs-move 귀속 줄 `cancel_order` → **`get_order@16`** · 단위 BAD 3 |
    | N1 버킷 내용 칸 정규화 걷기 | `_contract_stable` 의 `_CONTENT_RE.sub("(내용: …)", …)` 걷기 | cc-ign · cc-part · cc-add | cc-ign 잔존 → **귀속 1** · 단위 BAD 2 |
    | R3 `@<줄>` 정규화 걷기 | `_contract_stable` 의 `_AT_LINE_RE.sub("@N", …)` 걷기 | rs-moveonly · rs-move | rs-moveonly 잔존 · exit 0 → **귀속 1 · exit 2** · 단위 BAD 1 |
    | R6 채널 끊김 합성 줄 걷기 | `if proc.returncode == 2 and not broken` → `if proc.returncode == 2` | 채널 끊김 대역 | 단위 BAD 1(계약 줄 하나만 남음) |
    | R4 폴더 조건 늘 켬 | `folder=any(rule in line for rule in _FOLDER_COUNT_RULES)` → `folder=True` | skel-cas | ⓓ 신규 0 → **1** |
    | R4 폴더 조건 늘 끔 | 같은 자리 → `folder=False` | m2 | ⓓ 신규 1 → **0** |
    | R1 출처 재실행 끝 커밋 걷기 | 출처 재실행의 `git_tip=sha` 걷기(루트 · 앵커는 둠) — 또는 셋 다 걷기(v3 꼴) | merge-mig +승인 | 둘 다 귀속 0 · 유입 1 → **귀속 1(이중 원인)** |
    | **R1′ 파일 단위 → 폴더 단위로 되돌림(v5)** | registry_gate `_provenance_split` 의 `touch: "frozenset[str]" = touch_paths(checker, p)` → `frozenset()` | mm-wt · mm-post | 유입 1 → **귀속 1**(«worktree 수정 중» · «레인 커밋 수정 …(승인 머지 이후)») |
    | R1 출처 재실행 끝 커밋 걷기(v5 에서 다시) | 출처 재실행의 `git_tip=sha` 걷기 | mm-wt | 유입 1 → **귀속 1(이중 원인)** |
    | **S2 TIP 사본 묶음 걷기(v5)** | checker_target `gate_tip` 의 `if (Path(root) / ".git").exists(): return ""` 걷기 | app-b · idem-new 직접 실행에 `BASE=TIP=HEAD`(`git_touched_smoke` 사례로) | 2 → **0** |
    | 차1 앵커 대비 건드림 걷기 | 지금 실행(병렬 길)의 `git_base=anchor_sha` 걷기 | bc · kc · idem-newc | app-bc 귀속 1 → **0**(게이트 exit 0) · idem-newc 귀속 1 → **0** |
    | F4-28 앵커 커밋 트리 표지 걷기 | 앵커 실행의 `committed=True` 걷기 | a · b | app-a 표 `0\|0` → **`2\|0` · 해소 1** |
    | F4-46 수 칸 짝 · 지움만 걷기 | ⓓ 짝 호출의 `counts=True,` · `narrowed=…` 걷기 | s1 · s3 / m1 · m2 | (v3 판에서 정함 · v4 에서 다시 안 돎) |
    | 사10 표지 경로 대조 걷기 | checker_target `committed_snapshot` 의 경로 대조 → «값이 있으면 참» | 비-git 표지 값 사례 | (v3 장난감 nongit-c · nongit-idem 로 정함 · 다시 안 돎) |
    | N2 접힌 폴더 판정 걷기 | app-container 직접 실행 길의 접힌 `?? <앱>/migrations/` 판정 걷기 | e(직접 실행) | (v3 · 다시 안 돎) |

    - 변이 표 «옛 글» 은 구현본 글자와 정확히 한 번 맞아야 한다(맞지 않으면 시험 오류 — 기존 규칙). 위 글은 시제품 글자다.
- EXPECTED: `fixture_matrix` · `checker_baseline_matrix` · `findings_count_matrix` · `checker_cross_matrix` · `construct_drift_report` 무변(모래상자 녹색). **pregate kinds 재생성**(`check-app-container.py` · `check-idempotency-scope-creep.py` · `checker_target.py` sha — `gen_pregate_symbol_kinds --check` red 확인).
- 봉인(§4 · 검토 사12): 여섯 스크립트(`manifest_seal.py:56-61 · :83`) + **`pregate_symbol_kinds.json`(`:121`)** + **`rulepack.json`**(그래프 개정으로 재소성).
- 게이트 머리 글(시제품에 고침): 합성 귀속 줄에 N1 한 단락 · 이관 빚 «번호 없는 줄 `= …` 은 scope 렌더 전용 — 이 게이트엔 맞을 줄이 없다» → «scope 렌더 다섯의 계약 줄 — 이 게이트에서는 `[#N]` 없이 계약 줄만 낸 실행에서만 맞는다» · F4-166 줄에 F4-46 수 칸(지움만) · BK1 주석(앵커 = 커밋 트리 표지 · 지금 = 앵커 대비).
- 검사기 머리 글: app-container G2(«게이트 지금 사본은 앵커 대비 · 앵커 사본은 건드린 것 없음») · idempotency (2).

### 그래프 글(체크리스트 1 ~ 6 · 검토 중3 — 구현 때 그래프 담당)
1. **편집** — `ontology/rules/command-dddjango.ttl`: 새 Expression `<djr#R-3617@2026-11-16>`(`prov:specializationOf djr:R-3617` · `prov:wasRevisionOf <djr#R-3617@2026-10-13>` · `djr:revision 4` · `djr:revisionKind djr:revision-amendment`) + R-3617 `currentExpression` 교체 · 블록 `s007/b60` `djr:text` 의 두 문장을 §4 초안으로. prefLabel 그대로. rdflib 편집 뒤 `canon_turtle` 재직렬화(현행 ttl 왕복 byte 동일 먼저 확인).
2. `ontology_gate.py` green → `ontology_render.py --apply command-dddjango`.
3. **LEDGER 재기준선** — `command-dddjango` `s007` 행 덧붙임(`sha256(strip_marker(span))` · 사유 `rebaseline:<날짜> 3판 N1 — R-3617 리비전(개정) — 계약 줄 차분` · migrated 칸은 최근 행 값).
4. **계수표** `workspace/eval/fixtures/ontology_gate/target-counts.json` ExpressionShape **+1**(4366 → 4367 · 다른 판의 개정과 함께면 합) · **q4 골든** `query_golden_check.py --emit` · `make rulepack`(→ `rulepack.json` 함께 커밋 · 봉인).
5. final.md 소스 미러 — 해당 없음(조정자 글 · 스킬 final.md 아님).
6. **Codex 의미 미러** — `codex-dddjango/skills/dddjango/SKILL.md:195` 같은 두 문장을 같은 뜻으로 손으로.
- G12(`rulepack_smoke` 라벨 드리프트 `DRIFT_RE`): R-3617 prefLabel 을 바꾸지 않으므로 적중 무변 — `make verify` 의 rulepack_smoke 로 확인 한 줄.
- 조정자 글 `commands/dddjango.md:216`(잔존 합성 줄은 측정 실패로 반송)은 그대로 참(진짜 측정 실패 몫) — 고칠 글 없음.

### 문서 확인(§6 · 검토 사12)
- 사용자에게 보이는 G2 막힘이 바뀐다(§8) → README · `docs/master/master.html` 싣는 문서에 «게이트는 앵커부터의 변경을 본다(커밋한 실행도) · 계약 검사기도 줄마다 가른다» 가 필요한지 본다. 요청 가이드(`dddjango/REQUEST_GUIDE.md`): 사용자가 요청에 쓰는 칸 · 플러그인이 스스로 하거나 묻는 일은 바뀌지 않음 → «바뀔 것 없음» 예상(구현 때 확인).

## 남는 걱정
- `[#N]` 줄이 있는 검사기의 계약 꼬리(api-error-controller · composition-root · error-centralization)는 차분 밖이다 — 번호 줄과 함께 나면 꼬리의 새 위반은 안 보인다. 반대 방향(검토 사13): 앵커가 `[#N]` + 꼬리 C 이고 레인이 `[#N]` 만 고치면 지금 쪽 `parsed == 0` 이라 C 가 계약 줄로 «귀속» 된다 — 2.39.0 도 합성 줄로 귀속하던 같은 판정(회귀 아님) · 한계 줄로 남긴다.
- 진행 중 레인: N1 로 pre-gate 안정 ID 가 «합성 줄 하나» 에서 «계약 줄마다» 로 바뀌어 지난 처분 행과 이어지지 않는다 — 툴체인 digest 가 바뀌어 재예보는 어차피 필요하다(배포 알림 한 줄).
- N1 은 계약 검사기 legacy 를 줄마다 세므로 G2 배너의 «legacy 잔존 N건» 이 커질 수 있다(판정 무변).
- `DJR_COMMITTED_SNAPSHOT` 을 대상 경로 그대로 손으로 주면 비-git 대상의 fail-closed 가 꺼진다(받아들임 — 게이트는 지금 쪽에서 늘 걷음).
- 이미 추적된 현장 jsonl(286)은 그대로 남는다 — 플러그인이 지우지 않는다.
- (R7) 게이트 지금 사본의 «건드림» 은 `status` 미추적이라 **무시(gitignore)된 새 멱등 파일**은 들지 않는다 — 직접 실행(`ls-files` 실패 → 건드림)은 잡고 게이트는 놓친다(무르는 쪽 · 드묾). `checker_target.gate_base` 머리 글에 한계 줄로 적었다. 같은 머리 글에 «게이트 밖에서 `DJR_SOURCE_GIT_BASE` 를 주면 대상이 git 이어도 그 커밋 대비로 잰다(잘못된 커밋이면 fail-closed)» 한 줄(`findings.ENV_GIT_BASE` 주석에도).
- (R1) 승인 머지가 legacy 평면 앱 · 마이그레이션을 들인 레인은 v4 에서 그 줄이 «승인 유입» 절에 기록으로 뜬다(2.39.0 은 앵커 합성 줄에 가려 안 보였다) — 판정 무변 · G2 보고가 길어질 수 있다.
- (R1) 출처 재실행의 «건드림» 은 `앵커..M^k` 다. 앵커가 main(M^2)의 조상이 아니면(레인 첫 커밋 뒤를 앵커로 잡은 실행) `앵커..M^2` 에 레인 변경을 되돌리는 경로가 끼어 R(M^2) 가 커질 수 있다 — 그 경로는 작업 트리 글이 M^2 와 달라 W · F1 에서 먼저 귀속 유지라 무르는 쪽은 아니다(장난감 없음 · 코드 읽기).
- (R1′) 앱 폴더 줄의 «건드림을 만든 경로» 는 평면 앱 줄과 backoffice 줄에 같이 쓴다 — backoffice 줄(모델 있는 backoffice)은 검사기에서 건드림에 기대지 않지만, 승인 머지가 그 모델 · 마이그레이션 파일을 그대로 들였는지를 파일 단위로 보는 것이 폴더 tree 보다 좁지 않다(merge-m 유입 · merge-m2 «worktree 수정 중 — …/models.py» 귀속). 그 경로가 비면(예: `models/` 꾸러미만 더함) 폴더 tree 판정으로 돌아간다(v4 그대로 · 막는 쪽).
- (R1′) merge-idem +승인은 귀속 그대로다(이중 원인 — §2). 검토자는 검사기 정의로 0 이 맞다고 보았다 — 0 으로 바꾸려면 «건드림» 에서 그대로 들어온 경로를 빼는 길(ⓑ)이 필요하다. 바꾸면 «푸는 것» 이다.
- (R2) 진단 글에 새 흔들리는 칸(수 · 목록)을 더하는 검사기 변경은 계약 줄 짝을 깨 legacy 를 귀속으로 띄운다(fail-closed · 드러나는 쪽) — 계약 검사기 진단 글을 고칠 때 `_contract_stable` 을 함께 본다(체크리스트 8 한 줄).

## v4 → v5 바뀐 것
- **R1′(차단 · 사용자 «가.»)**: 앱 폴더 계약 줄(check-app-container)의 승인 머지 출처 판정을 폴더 tree(F1′) 대신 **그 줄을 «건드림» 으로 만든 경로마다 파일 단위 W · F1** 로(§2 «R1′»). «건드림을 만든 경로» 는 `checker_target.app_touch_paths` 한 곳(검사기도 같은 함수의 «비었나» 로 판정) · 같은 파일 판정은 `PathFacts.classify` 그대로 · 출처 재실행 · L 은 v4 그대로. mm-wt · mm-pre · mm-post · mm-conf · mm-preanchor 귀속 1 → **0 · 승인 유입 1** · mm-two 유입 · 대조 mm-lanemig-pre · merge-migx · merge-migxc 귀속 1 · merge-mig +승인 유입 · 승인 목록 없는 merge-mig · merge-newapp 귀속 · merge-idem +승인 귀속 1(이중 원인 · 2.39.0 과 같음 — 까닭 §2).
- **S1**: §7 R1 직렬 대조 수치를 기본 TMPDIR 마지막 실행 값으로 · response-schema-bypass 설명 바로잡음 · 하네스 `a/run_post4.sh` 에서 작업 트리 안 TMPDIR 걷음 · 기존 시험을 기본 TMPDIR 로 다시.
- **S2**: `DJR_SOURCE_GIT_TIP` 은 대상이 git 이 아닐 때(게이트 사본)만 믿는다(`checker_target.gate_tip(root)` · `anchor_changes(qroot, target)`) — git 작업 트리 직접 실행에 `BASE=TIP=HEAD`: app-b · idem-new v4 0 → v5 **2**(대조 `BASE` 만 2 그대로 · app-bc `BASE=TIP=앵커` v4 0 → v5 2).
- **S3**: §10 변이 표 이름 `_MUTATIONS` · `_BASELINE_MUTATIONS`.
- 변이 셋 더함(R1′ 폴더 단위 되돌림 · 끝 커밋 걷기 다시 · S2 묶음 걷기) — 모두 판정 바뀜 확인.
- 시제품 `a/proto/scripts/` = v5 · v4 는 `a/proto-v4/` · 모래상자 `a/repo-v2` 에 v5 여섯 파일(플러그인 · Codex 미러 byte 같음).

## v3 → v4 바뀐 것
- **R1(차단)**: 승인 머지 출처 재실행(M^1 · M^2 커밋 트리)에도 원본 루트 · 앵커와 그 커밋(`DJR_SOURCE_GIT_TIP` · `checker_target.gate_tip`)을 넘겨 «건드림» 을 `앵커..M^k` 로 잰다 → L 이 서서 merge-mig +승인 귀속 1 → **0(승인 유입 1)** · merge-newapp +승인 유입 · merge-idem +승인 귀속(이중 원인 · 2.39.0 과 같음). 대조: merge-migx · merge-migxc(레인이 그 앱에 마이그레이션) 귀속 1 · 승인 목록 없는 merge-mig · merge-newapp 귀속 1(§8 «새로 막음») · 커밋 판 *c 귀속 1 그대로. 검토 권고(지금 사본 «건드림» 에서 경로 빼기)와 자리가 다른 까닭은 §2(유입 기록 유지 · merge-idem 판정 유지 · F1 한 출처).
- **R2(중요) · R3**: 계약 줄 짝을 «흔들리는 칸(`@<줄>` · `(내용: …)` · 순번 꼬리)을 걷은 글이 같은 줄» 로만 — 같은 주어 칸의 글 다른 짝을 없앰. ch-swap(c) · rs-swap(c) 잔존 → **귀속** · rs-move 귀속 줄이 legacy(`get_order`) → **새 연산(`cancel_order`)** · 대조 cc-part · cc-ign · cc-add · rs-moveonly 잔존 그대로 · ch-add 귀속 그대로. 처분의 «안전한 셋 · 같은 기호» 갈래는 일곱 검사기 진단 글 꼴에서 새로 짝 짓는 줄이 없어(§4 표) 넣지 않았다 — 그 판(v4a)은 `a/proto-v4a/` 에 남김 · 장난감 판정 같음.
- **R4**: F4-46 «지움만» 의 폴더 새 파일 조건을 #547 ⑶ 에만(`_FOLDER_COUNT_RULES`) — 내 장난감 skel-cas(c)(#644 줄이기 + 같은 폴더 부품 파일) 신규 1 → **짝** · 대조 m2(#547 새 엔티티) 신규 1 그대로.
- **R5**: R-3617 새 문장 — «한쪽이 `[진단 미파싱 …]` 합성 줄이면(exit ≠ 0 인데 계약 레코드가 성하지 않으면)» · 짝 문장을 R2 꼴로(§4).
- **R6**: 레코드 채널이 끊긴 실행(경고 글 · `[분석]` · `unclassifiable`)은 계약 줄 대신 합성 줄 — 단위 대역(레코드 하나만 남음 → 합성 / 대조 성함 → 계약 줄 둘).
- **R7**: `gate_base` 머리 글 · `ENV_GIT_BASE` 주석 한 줄 · 무시된 멱등 파일 한계 줄(남는 걱정).
- 변이 표 초안(§10 — 새 판정마다 죽이는 사례 · 그 가운데 열한 변이를 시제품 사본 `a/mut/<이름>/` 으로 돌려 모두 판정이 바뀜을 확인) · 대역 서명 `git_tip=None` · 단위 18/18 · 시제품 `a/proto/scripts/` = v4 · `a/proto-v3/` · `a/proto-v4a/` 남김.
- 기존 시험 · 현장 다시 돎(§7 · §9): 묶음 녹색(설계된 R1 · R2 불일치 5 · pregate kinds 재생성 필요는 v3 와 같음) · 현장 v4 = v3 · 승인 머지 꼴 현장 복제(fieldclone4)에서 세 판 모두 green · 유입 2.
- 실수 한 건(되돌림): 재확인 중 검토자 하네스 `review-a/bin/run3.sh v3` 를 돌려 `review-a/out/r3-merge-{mig,idem,newapp,m,m2,m3}+승인-v3.txt`(와 `.direct`) 여섯 쌍을 v4 출력으로 덮었다 — v3 시제품(`a/proto-v3/`)으로 다시 만들어 되돌렸다(툴체인 경로 줄만 다름). 이후 내 하네스 `a/run4.sh`(출력 `a/out/v4/`)만 썼다.

## v2 → v3 바뀐 것
- **차1 · 중2**: «건드림» 을 앵커 대비로 — 게이트가 지금 사본에 `DJR_SOURCE_GIT_BASE=<앵커>` 를 넘기고 `checker_target.anchor_changes`(dddjango-web `--diff-base` 꼴) 한 곳으로 app-container · idempotency 가 센다. 커밋 판 장난감 bc · cc · ec · fc · gc · jc · kc · newparentc · idem-newc 모두 귀속(v2 는 0 · gc 잔존). 직접 실행(변수 없음)은 그대로.
- **사10**: 커밋 트리 표지 값 = 앵커 사본 경로 · 검사기 뿌리와 같을 때만 믿음(비-git 장난감 값 1 → fail-closed 그대로).
- **중3**: N1 이 R-3617(s007/b60)과 어긋남 — 새 Expression 문장 초안 · 체크리스트 1 ~ 6(§4 · §10). v2 의 «graph-owned 절 무변» 은 틀렸다.
- **중5 · 중6 · 중8**: 계약 줄은 같은 열쇠 순번(다중 집합) + 같은 자리(검사기 · 주어 칸) 1:1 짝 — cc-ign 거짓 귀속 0 · cc-part 줄이기 잔존 · to-dup 둘째 위반 귀속. 버킷에 새 파일 더함은 «새로 막지 않음» 으로 적음.
- **중9**: F4-46 수 칸 짝을 «지움만»(그 파일 더한 줄 0 · 그 폴더 새 파일 0)으로 좁힘 — m1 · m2 신규 · m3 · s1 · s3 짝.
- **중7**: ch-reg(직접 실행 0 · 게이트만 붉음)를 의도한 새 붉음으로 §8 에.
- **중4 · 사11 · 사12 · 사13**: 변이 표 고침 · R1 · R2 덧대기 조건 둘 · 게이트 머리 글 · 봉인 목록(pregate kinds · rulepack) · 문서 확인 · 한계 줄(§10 · 남는 걱정).
- 시제품: `a/proto/scripts/` = v3(`checker_target.py` 더함) · `a/proto-v2/` 남김.


---

