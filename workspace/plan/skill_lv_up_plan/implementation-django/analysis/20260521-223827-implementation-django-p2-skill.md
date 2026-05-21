수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
초기 발견 수: Blocker 0, Major 2, 열린 Minor 1

## 평가 기준

- `dddjango/skills/implementation-django/SKILL.md` 목적, trigger, 제외 조건이 source reference와 일치해야 한다.
- frontmatter `description`에 사용 조건, trigger, 제외 조건이 충분히 들어 있고 본문에만 숨은 trigger가 없어야 한다.
- `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 일치해야 한다.
- `agents/openai.yaml`은 `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`의 필드 제약을 따라야 하며, 명시 요청 없는 optional interface field를 추가하지 않아야 한다.
- source skill과 runtime cache는 같은 내용을 가져야 한다.

## 현재 평가

`SKILL.md`는 Django 5.x/LTS 구현 범위, 모델/ORM/서비스/마이그레이션/트랜잭션/settings/caching/security/performance, Django integration acceptance criteria, 기존 DRF 유지보수 예외, Django Ninja/API/Web/Test/Workflow/DDD/DB 라우팅 제외 조건을 드러낸다. bundled references도 task별로 progressive disclosure가 가능하게 분리되어 있다.

metadata에는 optional interface field가 추가되어 있지 않고 `default_prompt`도 `$implementation-django`를 명시한다. 다만 `interface.short_description`이 25-64자 quick-scan blurb 제약을 초과한다.

real-subagent 독립 리뷰에서 body-only workflow trigger도 발견했다. 본문은 `subagents`, `역할 분해`, `병렬 검토`, `책임 분배` 요청을 `workflow-dddjango-subagents`로 보낸다고 명시하지만, frontmatter는 composite/risky work만 언급해 explicit role-decomposition trigger를 충분히 노출하지 못했다.

## Blocker

없음.

## Major

1. `agents/openai.yaml` short_description 길이 제약 위반
   - `openai_yaml.md`는 `interface.short_description`을 25-64 chars로 설명한다.
   - 현재 값은 skill 범위를 설명하되 너무 길어 UI quick scan 제약과 맞지 않는다.
   - 의미를 보존하면서 더 짧은 human-facing 문구로 줄인다.

2. body-only workflow trigger
   - 본문 routing에 있는 subagent/역할 분해/병렬 검토/책임 분배 trigger가 frontmatter에 충분히 노출되지 않았다.
   - Codex skill routing은 frontmatter description을 먼저 보므로, 본문 routing과 같은 제외 조건을 frontmatter에도 반영한다.

## Minor

1. `agents/openai.yaml` short_description의 scope under-claim
   - 길이 수정 후에도 short description이 models/ORM/services/migrations에 치우치면 transactions/settings/caching/security/performance 범위가 좁아 보일 수 있다.
   - 64자 안에서 transactions와 operational Django concerns를 함께 암시하도록 보정한다.

## Note

- `SKILL.md` frontmatter와 본문 routing은 수정 후 충돌하지 않는다.
- 본문에만 존재하던 workflow trigger는 frontmatter에 반영했다. frontmatter는 Django model/ORM/service/migration/transaction/settings/caching/security/performance와 주요 제외 라우팅을 포함한다.
- source reference 자체의 P2 추가 gap은 발견하지 못했다.
- source skill과 runtime cache는 수정 전 `diff -qr` 기준 차이가 없었다.

## Subagent 리뷰/순차 fallback

- skill-creator real-subagent 리뷰: Blocker 0, Major 0, Minor 0. 목적/trigger coverage, progressive disclosure, OpenAI YAML alignment, source/runtime sync가 P2-clean이라고 판단했다.
- 독립 real-subagent 리뷰: Blocker 0, Major 1, Minor 1. body-only workflow/Korean trigger terms를 Major로, short_description scope under-claim을 Minor로 지적했다.
- 메인 통합 판단: 독립 리뷰의 Major/Minor는 P2 기준상 타당하므로 `SKILL.md` frontmatter와 `agents/openai.yaml`을 추가 보완했다.

## 재평가

- `SKILL.md` frontmatter에 subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배 trigger를 추가해 본문 routing과 맞췄다.
- hidden trigger 재점검에서 TemplateView/HTMX/CSRF web routing과 mock/factory/concurrency/coverage test routing도 frontmatter에 명시했다.
- `agents/openai.yaml` short_description을 25-64자 안에서 transactions와 operational Django concerns를 암시하도록 보정했다.
- optional interface field는 추가하지 않았다.
- source reference 추가 gap은 발견하지 못했다.
- runtime cache는 별도 runtime-sync analysis/plan에 따라 동기화한다.
- 리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
