# 작업 지시서 — dddjango 새 결함 3건 수리 (2026-10-01)

너는 dddjango 플러그인 저장소의 수리 작업자다. 이 워크트리(`/Users/hyun/.herdr/worktrees/dddjango/fix-new-defects-3`, 브랜치 `fix/new-defects-3`, 기준 main `2fffcb22`)에서만 일한다. 결과는 운영자(Claude)가 리뷰하고 `make verify` 를 다시 돌린 뒤 사용자 승인을 받아 main 에 올린다. 한국어로 기록·보고한다.

## 먼저 읽을 것
- `AGENTS.md`(저장소 지침) · `docs/DEVELOPMENT.md`(정본·투영물·검증 절차)
- 핵심 규칙
  - md 의 `<!-- graph-owned: … -->` 절과 에이전트 frontmatter 는 **직접 고치지 않는다** — `ontology/rules/<doc_key>.ttl` 을 고치고 `python3 workspace/tools/ontology_render.py --apply <doc_key>` 로 재투영한다. 그래프가 바뀌면 `make rulepack` 으로 `dddjango/scripts/rulepack.json` 을 다시 만든다. 산문(NAR) 절을 고치면 `ontology/LEDGER.tsv` 에 재기준선 행을 append 한다.
  - 검사기·스크립트 `dddjango/scripts/*` 는 `codex-dddjango/skills/dddjango/scripts/` 와 **byte 동일 미러** — 항상 양쪽을 같이 고친다(`cmp` 로 확인).
  - Codex 역할·Coordinator `SKILL.md` 는 의미 미러다(뜻을 맞춘다).

## 결함 1 — 중복 요청(idempotency) 검사기가 registry_gate·pre-gate 안에서 발화하지 않는다
- 증상: `dddjango/scripts/registry_gate.py` 의 `_snapshot_current`(:170)가 `_IGNORE_COPY`(:105)로 `.*` 를 빼고 현재 트리를 복사한다. 그래서 현재 스냅숏에 `.dddjango/*/scope.md` 가 없고, `check-idempotency-scope-creep.py` 는 늘 exit 0 이 된다. 앵커 스냅숏(`git archive`)에는 추적된 `.dddjango/` 가 있어 앵커 쪽만 발화할 수 있다 → 집합 차분에서 «해소»로 보인다.
- 재현(앞선 리뷰가 실측): 요청에 없는 scope + 미추적 `idempotency_record.py` → 검사기 직접 실행 exit 2 · 같은 트리에서 registry_gate 표는 `0 | 0`.
- 지금은 G2 의 검사기 직접 실행(Coordinator `dddjango/commands/dddjango.md` 의 G2 단계)이 막아 주지만 늦게 잡힌다.
- 할 일: 원인을 코드로 확인하고, 이 검사기가 읽는 입력(`.dddjango/<폴더>/scope.md` · `design-spec.md` 등 — 검사기 `:178-200` 근처)이 현재 스냅숏에도 들어가게 고친다. 다른 검사기의 판정이 바뀌면 안 된다(다른 숨김 경로는 계속 빼야 한다). `design_pregate.py` 가 같은 문제를 갖는지도 확인한다.
- 시험: 위 재현을 픽스처로 고정한다(수정 전 red · 수정 뒤 green). 기존 스모크 `workspace/tools/registry_gate_smoke.py` · `workspace/tools/git_touched_smoke.py` 가 계속 green 이어야 한다.

## 결함 2 — 읽기 전용 역할에 Serena 편집 도구가 열려 있다
- 증상: `dddjango/agents/design-review-api.md` · `design-review-db.md` · `design-review-ddd.md` · `discipline-reviewer.md` 의 frontmatter `tools:` 가 `mcp__serena__*`(와일드카드)다. 이 와일드카드에는 `replace_symbol_body` · `insert_before_symbol` · `insert_after_symbol` · `replace_in_files`·이름 바꾸기 같은 **편집 도구**가 들어 있다. 현장 8-C-0 리뷰어 세션 56개 모두에 정의가 실렸다(실제 사용은 읽기뿐이었다).
- 같은 종류: `design-architect.md` 도 «코드는 쓰지 않는다»(명세 전속 작성자)인데 같은 와일드카드다. 이것도 같이 고칠지 판단하고 이유를 보고한다(권장: 같이 고친다).
- 할 일: 와일드카드를 **읽기 전용 Serena 도구의 명시 목록**으로 바꾼다. 목록은 실제 Serena 도구 정의에서 고른다(예: `find_symbol` · `get_symbols_overview` · `find_referencing_symbols` · `find_declaration` · `find_implementations` · `get_diagnostics_for_file` 등 — 실재하는 이름만, 쓰기·메모리 쓰기·셸 실행 도구는 빼고). 근거로 쓴 도구 정의 출처를 보고한다. frontmatter 는 graph-owned 다(예: `ontology/rules/agent-design-review-api.ttl` 의 `djr:text "tools: …"`) — ttl → render → rulepack 순서로 한다. Codex 쪽은 frontmatter 가 없으니 해당 역할 SKILL 문면에 같은 뜻(편집 도구 금지)이 이미 있는지 보고, 없으면 의미 미러로 한 줄 맞춘다.
- `acceptance-tester` · `coder` 는 편집이 일이므로 건드리지 않는다.
- 이 작업은 **dddjango(core)만**이다. `dddjango-web/` 은 지금 다른 작업이 고치고 있으니 손대지 않는다(같은 결함이 web 리뷰어에도 있으면 보고만 한다).

## 결함 3 — pre-gate 격리 사본이 남고, 백그라운드 git 정리 작업이 생긴다(의심 · 진단부터)
- 관찰: `dddjango/scripts/design_pregate.py` 는 `tempfile.mkdtemp(prefix="design-pregate-")`(:3503 근처)에 기준선 사본을 만들고, 그 안에서 `git init` · `git add -A` · `git commit`(:3555 근처)을 한 뒤 `finally` 에서 `shutil.rmtree(scratch, ignore_errors=True)`(:3644)로 지운다. 그런데 `$TMPDIR` 에 `design-pregate-*` 폴더가 지워지지 않고 남는다(지금 13:13 · 13:32 것이 남아 있다). 실행 중에는 사본이 수 GB(관찰 약 3.2GB)이고, 같은 때 분리된 `git maintenance`/repack 프로세스가 보였다.
- 가설(검증할 것): 큰 `git add -A` + `commit` 이 `gc --auto`/`maintenance --auto` 를 분리 실행으로 띄우고, 그것이 사본 `.git` 에 쓰는 동안 `rmtree` 가 경합해 일부가 남는다 · 분리 실행이 사본이 지워진 뒤에도 기계 부하를 만든다.
- 할 일: 재현으로 원인을 확정한 뒤 고친다(예: 사본 저장소에서 자동 gc/maintenance 를 끈다 · 지우기 실패를 조용히 넘기지 않는다). `registry_gate.py` 의 사본도 같은 모양인지 본다. 가설이 틀리면 실제 원인을 적고, 결함이 아니면 그렇게 보고한다.
- 시험: 수정 뒤 pre-gate 를 여러 번 돌려 `design-pregate-*` 잔여 0 · 분리 git 프로세스 0 을 보인다(재현 스크립트·결과를 보고에 남긴다).

## 금지(보안·운영 — 반드시 지킨다)
- **다른 프로세스를 죽이거나 건드리지 않는다**(다른 세션·레인의 git·python 포함). 결함 3 재현에서 생긴 프로세스라도 네가 띄운 것인지 확실할 때만 정리한다.
- 남아 있는 옛 `design-pregate-*` 폴더는 지우지 않는다(지금 다른 레인이 pre-gate 를 돌리고 있을 수 있다 — 증거로 둔다).
- 읽기만: `/Users/hyun/Desktop/spring_dream_server` · `/Users/hyun/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude`(쓰기·`git status` 금지). 필요하면 `git clone --shared` 로 `$TMPDIR` 에 사본을 만든다.
- `dddjango-web/` · `codex-dddjango-web/` 수정 금지.
- push 금지 · main 브랜치 수정 금지 · 이 워크트리 브랜치에만 커밋한다.
- `.venv`(심볼릭 링크)와 이 지시서·보고서 파일은 커밋하지 않는다. `git add -A` 대신 경로를 지정해 add 한다.
- 봉인(`workspace/tools/manifest_seal.py --write`) chore 커밋은 만들지 않는다(운영자가 착지 때 한다). 검증 중 봉인 드리프트만 red 면 그 사실을 보고한다.
- Serena · Graphify 를 쓰지 않는다(이 저장소는 opt-in 이 없다).

## 커밋 · 검증
- 결함마다 커밋을 나눈다(3개). 메시지는 한국어, 형식은 최근 로그(`git log --oneline -15`)를 따른다. 끝에 빈 줄 뒤 `Co-Authored-By: GPT-6 Astra (Codex) <noreply@openai.com>` 를 붙인다.
- 커밋마다 `make verify` 를 돌린다(봉인 드리프트 외 green). 결함 2 는 `python3 workspace/tools/ontology_render.py --check` 류 · `make rulepack` 차이 0 · `claude plugin validate dddjango --strict` 도 확인한다(명령이 없으면 보고).

## 보고 — `workspace/plan/2026-10-01-new-defects/report.md` 에 쓴다(커밋하지 않음)
1. 결함마다: 확정한 원인(파일:줄) · 고친 내용 · 시험(수정 전 red → 수정 뒤 green 증거) · 커밋 해시
2. 결함 2: 고른 Serena 도구 목록과 근거 출처 · architect 처리 판단 · Codex 쪽 처리
3. 결함 3: 재현 방법 · 수정 전후 잔여 폴더·프로세스 수
4. `make verify` 결과(커밋별) · 미러 `cmp` 결과
5. 설계·지시와 다르게 한 것 · 새로 본 결함(고치지 말고 적기) · 남은 일
다 끝나면 마지막 줄에 `REPORT-DONE` 을 쓴다.
