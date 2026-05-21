수정 대상: skill

# implementation-cleancode P1 skill 반영 분석

## 평가 기준

- 대상 skill: `dddjango/skills/implementation-cleancode/`
- source reference: `workspace/reference/implementation-cleancode/reference/final.md`
- 확인 대상:
  - `SKILL.md`
  - `references/responsibility.md`
  - `references/naming-functions.md`
  - `references/encapsulation-abstraction.md`
  - `references/legacy-review.md`
  - `agents/openai.yaml`

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| trigger description | 충분 | `SKILL.md` frontmatter가 responsibility, naming, function shape, encapsulation, abstraction, SOLID, duplication, error handling, legacy, fat models/views/routers를 포함한다. |
| routing boundary | 대체로 충분 | `SKILL.md`가 DDD/API/DB/Django/Ninja/Python/Test/workflow skill로 라우팅할 조건을 명시한다. |
| progressive disclosure | 충분 | `SKILL.md`는 짧고, 세부 기준은 4개 bundled reference로 나뉘어 있다. |
| naming/function 기준 반영 | 충분 | `references/naming-functions.md`가 이름, 함수 형태, 인수, 부수 효과, 명령/조회 분리를 다룬다. |
| encapsulation/abstraction/SOLID/DRY/error 기준 반영 | 충분 | `references/encapsulation-abstraction.md`가 정보 은닉, 깊은 모듈, SOLID, DRY, 오류 처리 기준을 다룬다. |
| legacy review 기준 반영 | 충분 | `references/legacy-review.md`가 code smell, characterization test, seam, sprout/wrap method를 다룬다. |
| Fat Model/View/Router 반영 | 부족 | source reference에 Django/dddjango 경계 기준을 보강했지만 bundled reference에는 "views, routers, schemas, templates에 비즈니스 규칙을 묻지 말라"는 단일 문장만 있다. Fat Model, Fat Schema/Serializer, service dumping ground, 전문 skill 라우팅 경계가 런타임에서 충분히 보이지 않는다. |
| `agents/openai.yaml` | 일부 부족 | default prompt가 responsibility, naming, encapsulation, duplication, legacy만 예시로 들며 Fat Model/View/Router 리뷰 표면을 드러내지 않는다. |

## 원인

- source reference는 Django/dddjango 특화 유지보수성 기준을 갖게 되었지만, runtime bundled reference가 아직 그 기준을 압축 반영하지 않았다.
- `agents/openai.yaml`은 UI metadata이므로 완전한 기준을 담을 필요는 없지만, 이 skill의 주요 trigger 표면인 Fat View/Router 유지보수성 리뷰를 예시에서 드러내는 편이 목적과 더 잘 맞다.

## 수정 필요 범위

- `dddjango/skills/implementation-cleancode/references/responsibility.md`
  - Django/dddjango framework boundary smell 기준 추가
  - service/selector로 옮기는 것이 항상 책임 분리가 아니라는 주의 추가
  - DB/API/DDD 결정이 필요한 경우 관련 skill로 라우팅하는 경계 추가
- `dddjango/skills/implementation-cleancode/SKILL.md`
  - Reference Loading 설명에서 responsibility reference가 Django boundary smell도 포함함을 명시
  - Runtime Rules에 Fat Model/View/Router 판단 기준을 간결히 추가
- `dddjango/skills/implementation-cleancode/agents/openai.yaml`
  - UI short/default prompt를 skill 목적과 source reference 보강 범위에 맞춰 갱신

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 2개를 실행했다. 하나는 skill-creator 관점, 하나는 독립 P1 감사 관점이다.
- skill-creator 리뷰: `agents/openai.yaml` short description이 skill 범위보다 좁다는 Minor를 제기했고, metadata를 `Review clean-code and Fat boundary risks.`로 보완했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 초기 Major 1: Fat Model/View/Router 및 Django framework boundary smell에 대한 source reference 보강분이 runtime bundled reference와 UI metadata에 충분히 반영되지 않았다.
- 재평가: `SKILL.md`, `references/responsibility.md`, `agents/openai.yaml` 보강 후 두 subagent 모두 Blocker 0, Major 0으로 판정했다. metadata Minor는 수정으로 닫았다.

## 결론

skill 구조는 유지하고, `responsibility.md`, `SKILL.md`, `agents/openai.yaml`만 좁게 수정한다. naming/function, encapsulation/abstraction, legacy reference는 이미 해당 source 기준을 충분히 반영하므로 이번 수정 범위에서 제외한다.
