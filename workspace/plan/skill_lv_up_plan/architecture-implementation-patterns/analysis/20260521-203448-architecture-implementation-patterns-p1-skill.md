수정 대상: skill
원인 분류: skill-source drift

# architecture-implementation-patterns P1 skill 반영 분석

## 평가 요약

Dedicated source reference인 `workspace/reference/architecture-implementation-patterns/reference/final.md`를 생성한 뒤 source skill을 재평가했다. 현재 `dddjango/skills/architecture-implementation-patterns/**`는 여전히 provisional/fallback source 상태를 선언하고 있어 source reference와 충돌한다. Bundled reference는 패턴 선택 기준의 골격은 있으나 clean architecture, service layer, event sourcing/saga 회피 기준, handoff 범위가 source reference만큼 명확하지 않다.

## 근거

- `SKILL.md` frontmatter와 본문이 `Provisional`, `fallback sources`, `dedicated source does not exist yet`라고 선언한다.
- `agents/openai.yaml`의 `short_description`과 `default_prompt`도 provisional/fallback 사용을 안내한다.
- `references/*.md` 네 파일이 모두 provisional/fallback 문구를 포함한다.
- `pattern-selection.md`는 패턴 trigger 표가 있으나 source reference의 적용 순서, clean/hexagonal 선택/회피, service layer 기준, risky write handoff를 충분히 연결하지 않는다.
- `ports-adapters.md`, `repository-uow.md`, `outbox-acl.md`는 source reference의 핵심과 대체로 일치하지만 dedicated source 이후 runtime-facing 경계와 handoff 설명을 보강해야 한다.

## 수정 필요 항목

| 항목 | 판정 | 필요한 수정 |
|---|---|---|
| frontmatter description | Major | fallback/provisional 제거, dedicated source 기준 trigger로 갱신 |
| SKILL.md 본문 | Major | source policy 문구 제거, routing/reference loading/runtime rules 갱신 |
| pattern-selection.md | Major | source reference의 적용 순서, 패턴별 선택/회피, service layer 포함 |
| ports-adapters.md | Minor | 의존성 방향, port ownership, adapter 책임, ACL handoff를 한글 runtime reference로 정리 |
| repository-uow.md | Minor | Django-native 기본 경로, service/selector, custom UoW 조건 보강 |
| outbox-acl.md | Major | event sourcing, saga, outbox, ACL, risky write handoff를 source 기준으로 명확화 |
| agents/openai.yaml | Major | fallback/provisional 안내 제거 |

## 수정하지 않을 항목

- eval case/answer/evaluator는 P1 skill 반영 수정 범위가 아니다.
- source reference를 skill에 맞추기 위해 다시 바꾸지 않는다.
- DB locking/isolation, REST idempotency, Django 구현, pytest 구현 상세는 owning skill로 유지한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

Subagent 리뷰/순차 fallback: 수정 전 분석은 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md` 기준으로 순차 fallback을 수행했다. 수정 후 real-subagent 리뷰를 별도로 수행해 이 문서의 리뷰 결과를 갱신한다.

skill-creator 리뷰: trigger description에 사용 조건과 제외 조건은 있으나 provisional/fallback 문구가 stale 상태다. SKILL.md는 500줄 미만이고 bundled references는 1단계로 직접 연결되어 progressive disclosure 구조는 적절하다. 다만 reference 문서의 첫 문단이 모두 stale 상태라 validation integrity를 해친다.

리뷰 결과: Blocker 0, Major 4, 열린 Minor 2

## 완료 판정

Source skill과 bundled reference를 dedicated source 기준으로 갱신한 뒤 runtime cache sync를 별도 평가한다.
