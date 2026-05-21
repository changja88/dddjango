수정 대상: skill
원인 분류: P1 skill reflection gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
초기 발견 수: Blocker 0, Major 1, 열린 Minor 4

## 평가 기준

- source reference: `workspace/reference/implementation-django/reference/final.md`
- source skill: `dddjango/skills/implementation-django/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/`

## 현재 평가

source reference 보강 후 `SKILL.md`와 bundled references는 모델, ORM, QuerySet/Manager, service/selector, migration, transaction, caching, security, performance, Django test acceptance 기준을 대체로 반영한다. 그러나 skill-facing metadata와 DRF boundary 표현에 보완이 필요하다.

## Blocker

없음.

## Major

1. 기존 DRF 유지보수 exception의 progressive disclosure 부족
   - source reference는 기존 DRF 유지보수, legacy migration review, 이미 DRF를 표준으로 채택한 프로젝트의 exception을 명시한다.
   - 기존 `SKILL.md`는 greenfield DRF 금지만 말하고, bundled references는 기존 DRF adapter 유지보수 기준을 제공하지 않는다.
   - 허용 claim: 신규 API 표준으로 DRF를 권장하지 않는다.
   - 금지 claim: 기존 DRF 유지보수 작업이 항상 `implementation-django` 범위 밖이라고 말할 수 없다.

## Minor

1. `agents/openai.yaml` scope 축약
   - 현재 `short_description`과 `default_prompt`는 models/ORM/services/migrations/transactions만 언급한다.
   - source와 `SKILL.md` description은 settings, caching, security, performance, Django integration test acceptance까지 포함한다.
   - UI metadata가 skill 목적을 좁게 보이게 하므로 P1 metadata alignment 관점에서 보완한다.

2. 기존 DRF 유지보수 boundary의 runtime rule 부재
   - `SKILL.md`는 greenfield DRF를 표준으로 권장하지 말라는 금지는 있다.
   - source reference는 기존 DRF 코드 유지보수에서는 DRF adapter를 다룰 수 있되 durable business rules를 model/service/DB boundary에 두라고 정리했다.
   - runtime rule에 이 경계가 없으면 기존 DRF 작업에서 "무조건 out-of-scope"로 오해할 수 있다.

3. Django-specific coding style under-claim
   - source reference는 Django coding style, import grouping, string formatting, model member order, template/view style을 포함한다.
   - skill trigger와 bundled references에는 이 Django-specific coding style을 로드할 경로가 없다.

4. bundled reference provenance 약화
   - source reference는 `[DDoc]`, `[DCS]`, `[TSD]`, `[HS]`, `[CP]`, `[OWASP]` 등 provenance 약어를 둔다.
   - bundled references는 결론만 요약하고 source basis를 거의 표시하지 않아 후속 conflict audit에서 source 추적 비용이 커진다.

## Note

- bundled references는 progressive disclosure 구조를 유지한다.
- `transactions-performance-security.md`는 source 보강 후 transaction/risky write guidance와 정합성이 있다.
- source skill과 runtime cache는 수정 전 `diff -qr` 기준 차이가 없었다.

## Subagent 리뷰/순차 fallback

- 리뷰 방식: real-subagent
- 리뷰 상태: real-subagent 2건 완료. 메인 판단과 충돌 없음.
- skill-creator 리뷰: 기존 DRF 유지보수 progressive disclosure 부족을 Major로 지적했고, coding style/reference metadata gap을 Minor로 지적했다.
- 독립 P1 리뷰: source coverage 충분, metadata under-claim Minor, provenance label 약화 Minor를 지적했다.

## 재평가

- 기존 DRF 유지보수 exception은 `coding-style-drf-maintenance.md`와 `SKILL.md` reference loading/runtime rule로 닫혔다.
- `agents/openai.yaml` under-claim은 settings, caching, security, performance, acceptance criteria를 포함하도록 보정해 닫혔다.
- Django-specific coding style under-claim은 `coding-style-drf-maintenance.md`로 닫혔다.
- bundled reference provenance 약화는 각 bundled reference의 source basis 표시로 닫혔다.
- 리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
