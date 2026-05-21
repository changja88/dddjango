수정 대상: skill
원인 분류: skill reflection gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# architecture-ddd skill 반영도 분석

## 평가 대상

- source skill: `dddjango/skills/architecture-ddd/`
- source reference: `workspace/reference/architecture-ddd/reference/final.md`
- runtime metadata: `dddjango/skills/architecture-ddd/agents/openai.yaml`

## 초기 평가

source reference는 충분하지만, source skill이 일부 reference 결정을 약하게 반영한다.

## 초기 Findings

### 초기 Major 1, 해결됨

- `SKILL.md`와 `references/tactical-patterns.md`가 Django 모델을 단순 도메인 객체로 사용할 수 있다고 말한다.
- scoped source reference는 계층+DIP와 pure domain dependency rule을 기본으로 두고, ORM은 도메인 모델을 import해야 한다고 정리한다.
- source reference의 Django 관련 완화는 간소화된 폴더 구조 허용에 가깝고, Active Record 모델을 domain object로 기본 허용한다는 결정은 아니다.

### 초기 Minor 3, 해결됨

- `SKILL.md` frontmatter에 `도메인 정책/정책` 중복 표현이 있다.
- `agents/openai.yaml`의 `short_description`과 `default_prompt`가 context map, entity, value object, domain service, consistency boundary 범위를 충분히 드러내지 않는다.
- `references/tactical-patterns.md`의 entity guidance가 "clear independent consistency boundary"라는 표현으로 source reference의 "entity는 aggregate 일부로만 사용" 결정을 약하게 만든다.

## Subagent 리뷰/순차 fallback

- skill-creator 리뷰: real-subagent로 실행했다.
- 독립 P1 충분성 리뷰: real-subagent로 실행했다.
- 두 리뷰 모두 Blocker는 없었다. 한 리뷰는 source/reference drift를 Major로, 다른 리뷰는 metadata/entity wording을 Minor로 분류했다.

## 수정 방향

- reference는 수정하지 않는다.
- `SKILL.md`와 bundled reference의 Django mapping rule을 source reference의 계층+DIP/pure domain 기본 결정에 맞춘다.
- entity wording을 aggregate boundary 중심으로 명확히 한다.
- UI metadata를 skill scope에 맞게 보강한다.
- runtime cache sync는 별도 `runtime-sync` 분석/계획에서 다룬다.

## 재평가 결과

- `SKILL.md` frontmatter 중복 표현을 제거했다.
- Django mapping rule을 domain/application model과 infrastructure separation 기본 결정에 맞췄다.
- entity guidance를 aggregate boundary와 aggregate root 중심으로 명확히 했다.
- `agents/openai.yaml` default prompt가 context map, entity, value object, domain service, consistency boundary를 포함하도록 보강됐다.
- post-fix real-subagent 리뷰 2건 모두 Blocker 0, Major 0, 열린 Minor 0으로 판정했다.
