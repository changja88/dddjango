# dddjango 프로젝트 지침

## 프로젝트 목적

이 저장소는 `dddjango` 플러그인을 개발하는 워크스페이스다. 플러그인은
`/dddjango` 커맨드(Coordinator)가 기존 Django 프로젝트의 한 기능을 DDD 방식으로
요구→설계→구현(TDD)까지 단계별 게이트로 빌드하도록 오케스트레이션한다.
**Claude Code(`dddjango/`)와 Codex(`codex-dddjango/`) 양 런타임을 지원**하며, 둘 다
같은 GitHub 레포에서 마켓으로 배포한다(Claude `dddjango@changja88-dddjango` · Codex `dddjango@changja88-dddjango`).
정본은 `dddjango/`이고 `codex-dddjango/`는 플랫폼 표기만 달리한 의미 동등 미러다. 11개
source reference/SKILL 정규화 parity는 `corpus_mirror_sync`로, 결정적 스크립트 19종은
별도 byte 비교로 검증한다. coordinator·역할 prompt는 도구 차이 때문에 byte-identical 대상이 아니다.

## 저장소 구조

- `dddjango/` — 실제 플러그인. `.claude-plugin/plugin.json`(매니페스트) +
  `commands/dddjango.md`(Coordinator) + `agents/*.md`(7개 subagent) +
  `skills/*/SKILL.md`(11개 스킬) + `scripts/check-*.py`(결정적 백스톱 19종).
- `workspace/reference/**` — 소스 코퍼스(아키텍처·구현 레퍼런스의 `final.md`).
  스킬 재생성의 1차 근거.
- `workspace/design/`, `workspace/plan/` — 빌드 설계 메모와 계획서.
  제품·파이프라인의 권위 있는 현재 명세는 `workspace/reference/spec.md`이며,
  결정 변경 이력은 `workspace/DEVLOG.md`에 남긴다.

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
- 스킬은 소스 코퍼스(`workspace/reference/**`)를 근거로 작성하며, 플러그인
  이름은 `dddjango`로 일관되게 쓴다.
- 플러그인 매니페스트나 구조를 바꾸면 `claude plugin validate dddjango --strict`로 검증한다.

## 변경 방식

- 기존 파일과 사용자 변경을 보존한다.
- 불필요한 추상화나 미리 만든 확장 지점을 추가하지 않는다.
- 구조 변경·대규모 재작성은 작은 단위로 나누고, 논의 후 진행한다.
