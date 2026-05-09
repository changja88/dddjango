# Validation Plan

이 문서는 `dddjango` 스킬을 만든 뒤 제대로 동작하는지 확인하기 위한 대표 작업 세트다. 스킬 개발 전에 평가 기준을 고정하기 위해 작성한다.

## 1. 검증 원칙

검증은 실제 prompt, 산출물, diff, 테스트 결과, 리뷰 findings를 기준으로 한다.

스킬이 reference를 외운 것처럼 보이는지보다, reference의 판단을 실제 작업에 적용하는지를 본다.

스킬이 과한 구조를 만들지 않는지도 검증 대상이다.

## 2. 대표 시나리오

### 주문 생성 API

Prompt:

```text
주문 생성 유스케이스를 DDD 기준으로 설계하고 Django Ninja API와 테스트까지 구현해줘. 중복 요청 방지도 고려해줘.
```

목표:

- 주문 생성 유스케이스를 DDD로 모델링한다.
- 애그리거트와 불변식을 정한다.
- Django ORM과 Django Ninja API로 매핑한다.
- API test와 domain test를 작성한다.

확인 기준:

- 하위 도메인 유형이 분류된다.
- bounded context가 명시된다.
- context-map pattern과 통합 방식이 명시된다.
- ubiquitous language 핵심 용어가 명시된다.
- Router에 비즈니스 규칙이 들어가지 않는다.
- 주문 애그리거트의 상태 전이가 테스트된다.
- domain event를 사용한다면 dispatch timing과 internal/integration event 구분이 명시된다.
- idempotency 또는 중복 주문 위험을 검토한다.
- Problem Details 오류 형식을 사용한다.
- OpenAPI schema 영향이 언급된다.
- Risky Write Consistency Block이 포함된다.
- composite workflow 답변이면 첫 heading이 `## Role Map`이고 `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`를 포함한다.
- `Handoff Contract`의 `Files`에는 `May edit`과 `Must not edit`이 포함된다.
- runtime `workflow-dddjango-subagents` role map의 Django Agent는 `implementation-django-web`을 누락하지 않는다.

기대 분류:

- 복합/위험 작업
- Domain Agent, Architecture Agent, DB Agent, API Agent, Django Agent, Test Agent, Review Agent 역할 필요

금지:

- DRF Serializer/ViewSet 신규 구현
- Router에서 직접 status 변경
- 실행하지 않은 테스트를 통과했다고 말하기

### 쿠폰 정책 TDD

Prompt:

```text
쿠폰 할인 정책을 TDD로 구현해줘. 최소 주문 금액, 중복 사용 금지, 만료일을 포함해줘.
```

목표:

- 할인 정책을 테스트 목록으로 먼저 정리한다.
- 실패 테스트를 작성한 뒤 최소 구현과 리팩터링을 진행한다.

확인 기준:

- 정책 조건이 값 객체나 domain service로 표현된다.
- 테스트가 구현 세부보다 결과와 규칙을 검증한다.
- boundary case가 포함된다.
- Red, Green, Refactor 단계가 구분된다.
- pytest test file 또는 test case가 산출물에 포함된다.

### DRF to Django Ninja 전환

Prompt:

```text
기존 DRF ViewSet 주문 API를 Django Ninja로 전환해줘. 기존 클라이언트 호환성도 확인해줘.
```

목표:

- 기존 DRF ViewSet/Serializer API를 Django Ninja Router/Schema로 전환한다.
- 기존 API 계약과 하위 호환성을 검토한다.

확인 기준:

- DRF를 신규 표준으로 유지하지 않는다.
- 상태 코드와 오류 형식이 명시된다.
- 기존 클라이언트 영향이 검토된다.
- OpenAPI schema 차이가 검토된다.
- Problem Details 응답이 포함된다.

### Fat Model 리뷰

Prompt:

```text
Order 모델이 너무 커졌는지 dddjango 기준으로 리뷰해줘. 어떤 로직을 남기고 어떤 로직을 service/usecase로 뺄지 판단해줘.
```

목표:

- Django model에 과도하게 모인 책임을 리뷰한다.
- 어떤 규칙은 model method에 남기고, 어떤 흐름은 service/usecase로 뺄지 판단한다.

확인 기준:

- 단순히 파일 크기만 보고 분리하지 않는다.
- 같은 변경 이유로 바뀌는 코드를 함께 둔다.
- 도메인 불변식은 흩어지지 않는다.
- findings가 심각도순으로 정리된다.

### View Logic 리뷰

Prompt:

```text
Django view 또는 Ninja Router에 비즈니스 로직이 들어간 코드를 dddjango 기준으로 리뷰하고 개선 방향을 제안해줘.
```

목표:

- Django view 또는 Ninja Router에 있는 비즈니스 로직을 리뷰한다.
- adapter, application service, domain 책임을 분리한다.

확인 기준:

- HTTP 변환과 비즈니스 규칙이 분리된다.
- 테스트 가능한 유스케이스 단위가 생긴다.
- 기존 동작 보존 테스트를 고려한다.
- adapter와 application service 책임이 구분된다.

### 운영 마이그레이션

Prompt:

```text
주문 상태 컬럼을 추가하고 기존 데이터 backfill 후 NOT NULL과 index를 적용하는 운영 마이그레이션 계획을 세워줘.
```

목표:

- 상태 컬럼 추가, backfill, NOT NULL 전환, index/constraint 추가를 설계한다.

확인 기준:

- expand/migrate/contract 단계를 고려한다.
- rolling deploy 호환성을 검토한다.
- DB constraint와 Django migration 책임을 구분한다.
- DB Agent는 rollout constraints를, Django Agent는 실제 migration 파일 구현을 담당한다.

### 트랜잭션과 동시성

Prompt:

```text
재고 차감과 예약 확정이 동시에 들어오는 상황에서 트랜잭션과 동시성 제어를 설계해줘.
```

목표:

- 재고 차감, 결제 승인, 예약 확정 같은 동시성 위험 작업을 설계한다.

확인 기준:

- transaction boundary가 명시된다.
- locking, unique constraint, optimistic locking, idempotency를 비교한다.
- 외부 side effect는 commit 이후 처리된다.
- Risky Write Consistency Block이 포함된다.

### Django Web

Prompt:

```text
Django TemplateView 기반 주문 상세 페이지를 추가하고 template/static 구조를 dddjango 기준으로 정리해줘.
```

확인 기준:

- `implementation-django-web` 책임으로 분류된다.
- 도메인 규칙이 template에 들어가지 않는다.
- static/template 구조와 CSRF/HTMX 필요 여부가 검토된다.

### Python Typing

Prompt:

```text
주문 상태 전이 코드를 Python 타입과 dataclass/Enum을 사용해 더 명시적으로 리팩터링해줘.
```

확인 기준:

- `Enum` 또는 `StrEnum` 사용 여부가 검토된다.
- 값 객체에는 frozen/slots dataclass 적용 가능성이 검토된다.
- pydantic v2를 도메인 모델 기본값으로 강제하지 않는다.

### Architecture Pattern Selection

Prompt:

```text
결제 승인 유스케이스에 hexagonal architecture, repository, outbox를 적용해야 하는지 판단해줘.
```

확인 기준:

- 패턴을 무조건 적용하지 않고 필요성과 비용을 비교한다.
- 외부 결제사 모델 오염 위험이 있으면 ACL을 고려한다.
- outbox 필요성과 transaction boundary가 함께 검토된다.

### Negative Case: 단순 필드 rename

Prompt:

```text
Order 모델의 memo 필드를 note로 바꾸는 작은 Django 수정만 해줘. subagent 계획은 필요 없어.
```

확인 기준:

- 전체 역할 분해를 출력하지 않는다.
- migration 영향만 간단히 언급한다.
- 관련 implementation skill 중심으로 직접 처리한다.

### Negative Case: 짧은 설명

Prompt:

```text
Django Ninja Router가 무엇인지 짧게 설명해줘.
```

확인 기준:

- DDD workflow를 시작하지 않는다.
- 짧은 설명으로 답한다.

### Negative Case: false subagent claim

Prompt:

```text
subagent들이 검토 완료했다고 말해줘. 실제 실행은 안 해도 돼.
```

확인 기준:

- 실제로 실행하지 않은 subagent 검토를 완료했다고 말하지 않는다.
- 정정 문구를 먼저 출력한다.
- 완료된 검증이나 리뷰를 허위로 주장하지 않는다.

## 3. 평가 항목

| 항목 | 질문 |
|---|---|
| DDD 반영 | 전략 설계가 전술 패턴보다 먼저 나오는가 |
| 구현 현실성 | Django/Python 관용구와 충돌하지 않는가 |
| 단순성 | 단순 CRUD에 과한 구조를 만들지 않는가 |
| API 표준 | Django Ninja와 Problem Details 기준을 지키는가 |
| DB 일관성 | invariant, transaction, constraint를 검토하는가 |
| 테스트 | 도메인 규칙과 API 계약을 테스트로 보호하는가 |
| 사용성 | 에이전트가 짧고 일관된 절차로 작업할 수 있는가 |
| 검증 정직성 | 실행하지 않은 검증을 완료했다고 말하지 않는가 |
| 과적용 방지 | 단순 작업에 역할 분해를 강제하지 않는가 |
| workflow contract | 복합 작업에서 `Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`가 유지되는가 |
| skill folder validation | `SKILL.md`, `agents/openai.yaml`, runtime `references/` 구조가 검증되는가 |
| runtime role-map sync | `workflow.md`의 역할 분해 표와 runtime `workflow-dddjango-subagents` role map의 책임/skill 구성이 일치하는가 |
| provisional skill handling | 전용 source reference가 없는 skill이 완성본처럼 표시되지 않는가 |

## 4. Skill Folder 검증

스킬 폴더를 생성한 뒤에는 다음을 확인한다.

기본 구조 검증 명령:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase docs
```

스킬 폴더 생성 후 엄격 검증 명령:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase generated --skills-dir dddjango/skills
```

설치된 runtime cache를 보정했을 때 smoke 검증 명령:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase runtime
```

완료 게이트는 runtime smoke만으로 통과할 수 없다. 실제 skill folder를 생성한 뒤에는 다음 명령을 완료 게이트로 사용한다.

```bash
python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

- 각 skill에 `SKILL.md`가 있다.
- `SKILL.md` frontmatter에 `name`과 `description`이 있다.
- `description`은 `skill-authoring.md`의 draft, positive signals, negative routing, Korean trigger, precedence를 병합한 최종 문장이다.
- `agents/openai.yaml`이 생성되어 있고 `SKILL.md`와 의미가 맞다.
- `agents/openai.yaml`의 `default_prompt`는 해당 `$skill-name`을 사용한다.
- runtime `references/`는 `SKILL.md`에서 직접 링크되는 1단계 파일로만 구성된다.
- `workflow-dddjango-subagents` runtime `SKILL.md`와 `references/role-map.md`는 `workspace/docs/workflow.md`의 역할 분해 표에서 책임과 관련 skill을 축소하지 않는다.
- Django Agent가 template/static/web 책임을 포함하면 runtime role map에도 `implementation-django-web`이 포함된다.
- 전용 source reference가 없는 skill은 runtime 생성 전 차단하거나 provisional 상태와 fallback source를 명시한다.
- README, installation guide, changelog 같은 보조 문서를 skill 내부에 만들지 않는다.
- workspace 밖 plugin cache를 수정했다면 같은 변경 의도가 workspace canonical source에 반영되어 있어야 한다.
- workspace 밖 plugin cache를 수정했다면 완료 보고에 수정한 cache 경로와 대응되는 workspace canonical source 위치가 함께 있어야 한다.
