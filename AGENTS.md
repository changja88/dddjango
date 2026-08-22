# dddjango 프로젝트 지침

## 프로젝트 목적

이 저장소는 `dddjango` 플러그인을 개발하는 워크스페이스다. 플러그인은
`/dddjango` 커맨드(Coordinator)가 기존 Django 프로젝트의 한 기능을 DDD 방식으로
요구→설계→구현(TDD)까지 단계별 게이트로 빌드하도록 오케스트레이션한다.
**Claude Code(`dddjango/`)와 Codex(`codex-dddjango/`) 양 런타임을 지원**하며, 둘 다
같은 GitHub 레포에서 마켓으로 배포한다(Claude `dddjango@changja88-dddjango` · Codex `dddjango@changja88-dddjango`).
플러그인 정본은 `dddjango/`다. `references/final.md`는 `corpus_mirror_sync`가 Codex에
byte-exact로 미러하고, checker script는 별도 byte mirror로 검증한다. 역할·Coordinator·
`SKILL.md` 본문은 각 플랫폼 형식을 유지하는 의미 미러다.

**개발 절차 정본은 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)다** — 이 저장소에서
무엇이 정본/투영물/소성물인지, 규범을 어떻게 수정·검증·릴리즈하는지는 그 가이드를 따른다.
아래 «규범 수정» 절은 그중 위반하기 쉬운 핵심만 요약한 것이다.

## 저장소 구조

- `dddjango/` — 실제 플러그인. `.claude-plugin/plugin.json`(매니페스트) +
  `commands/dddjango.md`(Coordinator) + `agents/*.md`(7개 subagent) +
  `skills/*/SKILL.md`(11개 스킬) + `scripts/check-*.py`(결정적 백스톱 27종).
- `ontology/` — 규범 **정본**(그래프): `rules/*.ttl`(30 문서 키) · `vocab/` · `shapes/` ·
  `wiring/` · `ISSUED`(채번 대장) · `LEDGER.tsv`(산문 절 기준선 원장).
- `workspace/reference/**` — 배포 reference의 출처·P1 메타데이터를 보존하는 소스 미러.
  배포 본문 정본은 `dddjango/skills/*/references/final.md`이며,
  `corpus_mirror_sync.py --write`가 workspace 소스 본문과 Codex reference를 갱신한다.
- `workspace/design/`, `workspace/plan/` — 빌드 설계 메모와 계획서.
  파이프라인의 권위 있는 명세는 `workspace/design/2026-05-26-dddjango-plugin-pipeline-design.md`.

## 작업 위치 원칙

- 플러그인 산출물(커맨드·subagent·스킬·매니페스트)은 `dddjango/` 아래에 둔다.
- 빌드 과정의 설계·계획·레퍼런스 등 개발 산출물은 `workspace/` 아래에 둔다.
- 플랫폼·도구 규격상 루트에 있어야 동작하는 파일만 예외적으로 루트에 두고,
  이유를 변경 내용에 남긴다.

## 플러그인 작성 원칙

- 커맨드·subagent 파일 본문은 곧 런타임 시스템 프롬프트다. 설계 근거 같은
  메타코멘트로 본문을 오염시키지 않는다.
- 한 주제는 한 소유자가 — 역할 경계를 넘기지 않는다(설계 명세=architect,
  인수 테스트=acceptance-tester, 코드=coder).
- 스킬 reference의 **산문 절에 한해** `dddjango/skills/*/references/final.md`를 먼저 편집한 뒤
  `corpus_mirror_sync.py --write`로 workspace/Codex 미러를 갱신한다(graph-owned 절은
  아래 «규범 수정» 절). 플러그인 이름은 `dddjango`로 일관되게 쓴다.
- 플러그인 매니페스트나 구조를 바꾸면 `claude plugin validate dddjango --strict`로 검증한다.

## 규범 수정 — 온톨로지 이후 (정본: `docs/DEVELOPMENT.md`)

릴리즈 2.17.0부터 커맨드·에이전트·스킬 md의 참조성 절은 온톨로지 그래프가 정본이다.

- md 안의 `<!-- graph-owned: … -->` 마커 절은 **직접 수정 금지** — `ontology/rules/<doc_key>.ttl`
  에서 고치고 `ontology_render.py --apply <doc_key>`로 재투영한다(새 규범은 `ISSUED` 채번).
  위반은 pre-commit 훅과 `ontology_render_sync`가 red로 차단한다.
- 산문(NAR) 절은 md가 정본 — 직접 수정하되 `ontology/LEDGER.tsv`에 재기준선 행
  (새 SHA-256 + 사유)을 append한다.
- 그래프가 바뀌면 `make rulepack`으로 소성물(`dddjango/scripts/rulepack.json`)을 재생성해
  함께 커밋한다.
- 검사기 `dddjango/scripts/check-*.py`는 `codex-dddjango/skills/dddjango/scripts/`와
  **byte 동일 미러** — 항상 양쪽을 함께 갱신한다.
- 커밋 전 `make verify` green을 확인한다. 릴리즈는 `make release`만 사용한다.

## 변경 방식

- 기존 파일과 사용자 변경을 보존한다.
- 불필요한 추상화나 미리 만든 확장 지점을 추가하지 않는다.
- 구조 변경·대규모 재작성은 작은 단위로 나누고, 논의 후 진행한다.
